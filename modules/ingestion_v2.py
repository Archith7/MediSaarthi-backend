# -*- coding: utf-8 -*-
"""
JSON Ingestion Module V2
Processes all_results_new.json → Normalized TestDocuments

CRITICAL FIXES:
1. Uses CanonicalTest ENUM (HEMOGLOBIN_CBC vs HBA1C distinction)
2. Computes abnormality programmatically (ignores OCR flags)
3. Validates reference ranges (uses global fallback if invalid)
4. Normalizes units to standard base units
"""

import json
import re
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path

# Import config modules
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.canonical_mappings_v2 import (
    CanonicalTest, get_canonical_test, get_report_type
)
from config.reference_ranges import (
    validate_reference_range, get_reference_range
)
from config.unit_normalization import normalize_value_and_unit
from db.models import TestDocument


class JSONIngesterV2:
    """
    Ingests patient lab reports from JSON and produces normalized TestDocuments.
    
    KEY IMPROVEMENTS:
    - Canonical test mapping with HEMOGLOBIN_CBC vs HBA1C distinction
    - Programmatic abnormality detection (ignores OCR)
    - Reference range validation with global fallback
    - Unit normalization to standard base units
    """
    
    def __init__(self, json_path: str):
        self.json_path = json_path
        self.raw_data: List[Dict] = []
        self.documents: List[TestDocument] = []
        self.stats = {
            "patients_processed": 0,
            "tests_extracted": 0,
            "tests_with_values": 0,
            "tests_abnormal": 0,
            "tests_unknown": 0,
            "reference_fallbacks": 0,
            "unmapped_tests": [],
        }
    
    def load_json(self) -> bool:
        """Load JSON file"""
        try:
            with open(self.json_path, 'r', encoding='utf-8') as f:
                self.raw_data = json.load(f)
            print(f"✅ Loaded {len(self.raw_data)} patient records from JSON")
            return True
        except Exception as e:
            print(f"❌ Failed to load JSON: {e}")
            return False
    
    def parse_age(self, age_str: Any) -> Optional[int]:
        """Parse age from various formats"""
        if age_str is None:
            return None
        
        if isinstance(age_str, (int, float)):
            return int(age_str)
        
        if isinstance(age_str, str):
            match = re.search(r'(\d+)', str(age_str))
            if match:
                return int(match.group(1))
        
        return None
    
    def parse_gender(self, gender_str: Any) -> Optional[str]:
        """Normalize gender to M/F/None"""
        if not gender_str:
            return None
        
        g = str(gender_str).strip().upper()
        
        if g in ['M', 'MALE']:
            return 'M'
        elif g in ['F', 'FEMALE']:
            return 'F'
        
        return None
    
    def parse_value(self, result_str: Any) -> Tuple[Optional[float], Optional[str]]:
        """
        Parse test result value.
        Returns: (numeric_value, original_text)
        
        CRITICAL FIX: Handle comma-separated numbers like "4,455" → 4455
        """
        if result_str is None:
            return None, None
        
        text = str(result_str).strip()
        
        if not text:
            return None, None
        
        # CRITICAL: Remove commas from numbers BEFORE parsing
        # "4,455" should become "4455", "1,50,000" → "150000"
        text_clean = text.replace(',', '')
        
        # Try to extract numeric value
        match = re.search(r'[<>]?\s*(\d+\.?\d*)', text_clean)
        
        if match:
            try:
                numeric = float(match.group(1))
                return numeric, text  # Return original text for display
            except ValueError:
                pass
        
        # Non-numeric result
        return None, text
    
    def parse_reference_range(self, ref_str: Any) -> Tuple[Optional[float], Optional[float], Optional[str]]:
        """
        Parse reference range string.
        Returns: (min_value, max_value, original_string)
        """
        if not ref_str:
            return None, None, None
        
        text = str(ref_str).strip()
        
        if not text or text.lower() in ['negative', 'positive', 'nil', 'absent', '-']:
            return None, None, text
        
        # Pattern: "12.0 - 16.0" or "12.0-16.0"
        range_match = re.search(r'(\d+\.?\d*)\s*[-–—to]\s*(\d+\.?\d*)', text)
        if range_match:
            try:
                min_val = float(range_match.group(1))
                max_val = float(range_match.group(2))
                return min_val, max_val, text
            except ValueError:
                pass
        
        # Pattern: "< 200" or "<200"
        less_match = re.search(r'<\s*(\d+\.?\d*)', text)
        if less_match:
            try:
                max_val = float(less_match.group(1))
                return None, max_val, text
            except ValueError:
                pass
        
        # Pattern: "> 60"
        greater_match = re.search(r'>\s*(\d+\.?\d*)', text)
        if greater_match:
            try:
                min_val = float(greater_match.group(1))
                return min_val, None, text
            except ValueError:
                pass
        
        return None, None, text
    
    def compute_abnormality(
        self,
        value: Optional[float],
        reference_min: Optional[float],
        reference_max: Optional[float]
    ) -> Tuple[bool, Optional[str]]:
        """
        CRITICAL: Compute abnormality programmatically.
        DO NOT trust OCR-labeled abnormal flags.
        
        Algorithm:
        - IF reference_min exists AND value < reference_min → LOW
        - IF reference_max exists AND value > reference_max → HIGH
        - ELSE → normal
        """
        if value is None:
            return False, None
        
        # Check LOW
        if reference_min is not None and value < reference_min:
            return True, "LOW"
        
        # Check HIGH
        if reference_max is not None and value > reference_max:
            return True, "HIGH"
        
        # Normal
        return False, None
    
    def is_urine_report(self, tests: List[Dict]) -> bool:
        """
        Detect if this is a urine analysis report.
        Urine reports have characteristic tests that don't appear in blood tests.
        Must have multiple STRONG urine indicators, not just one.
        """
        # STRONG urine indicators (very specific to urine tests)
        strong_urine_indicators = {
            "specific gravity", "turbidity", "pus cells", "epithelial cells",
            "casts", "urobilinogen", "deposit", "organisms", "amorphous", 
            "completeurinogram", "urinary", "urinogram"
        }
        
        test_names = [t.get("Test Name", "").lower() for t in tests]
        
        # Count how many STRONG urine indicators are present
        strong_count = sum(1 for name in test_names 
                         if any(ind in name for ind in strong_urine_indicators))
        
        # If 3+ strong indicators, it's definitely a urine report
        return strong_count >= 3
    
    def should_skip_urine_test(self, test_name: str, is_urine: bool) -> bool:
        """
        Check if a test should be skipped because it's a urine test
        that would incorrectly map to a blood test.
        """
        if not is_urine:
            return False
        
        # Tests that have same name in urine and blood, but different meaning
        # These should only be skipped if we're CERTAIN it's a urine report
        ambiguous_tests = {
            "red blood cells", "rbc", "glucose", "protein", "proteins",
            "bilirubin", "ketones", "sugar"
        }
        
        test_lower = test_name.lower().strip()
        return test_lower in ambiguous_tests or \
               any(test_lower.startswith(amb) or test_lower.endswith(amb) 
                   for amb in ["red blood", "rbc"])
    
    def process_patient(self, patient_data: Dict) -> List[TestDocument]:
        """
        Process a single patient's data into TestDocuments.
        ONE test = ONE document.
        """
        documents = []
        
        # Generate UUID for this patient
        patient_id = str(uuid.uuid4())
        
        # Extract patient info
        patient_name = patient_data.get("Patient Name", "Unknown")
        age = self.parse_age(patient_data.get("Age"))
        gender = self.parse_gender(patient_data.get("Gender"))
        source_image = patient_data.get("Image Filename")
        report_date_str = patient_data.get("Report Date")
        
        # Parse report date if available
        report_date = None
        if report_date_str:
            try:
                report_date = datetime.strptime(report_date_str, "%Y-%m-%d")
            except:
                pass  # Keep as None if parsing fails
        
        # Get tests array
        tests = patient_data.get("Tests", [])
        
        # CRITICAL FIX: Detect if this is a urine report
        is_urine = self.is_urine_report(tests)
        
        for test in tests:
            raw_test_name = test.get("Test Name", "")
            
            if not raw_test_name:
                continue
            
            # CRITICAL FIX: Skip urine tests that would map incorrectly to blood tests
            if self.should_skip_urine_test(raw_test_name, is_urine):
                self.stats["tests_unknown"] += 1
                self.stats["unmapped_tests"].append(f"URINE:{raw_test_name}")
                continue
            
            # Step 1: Map to canonical test ENUM
            canonical_test = get_canonical_test(raw_test_name)
            
            if canonical_test == CanonicalTest.UNKNOWN:
                self.stats["tests_unknown"] += 1
                self.stats["unmapped_tests"].append(raw_test_name)
                continue  # Skip unknown tests
            
            # Step 2: Parse raw value
            value, value_text = self.parse_value(test.get("Result"))
            
            # Step 3: Get raw unit and normalize
            raw_unit = test.get("Unit", "")
            _, _, value_standard, unit_standard = normalize_value_and_unit(
                value, raw_unit, canonical_test
            )
            
            # Step 4: Parse OCR reference range
            ocr_ref_min, ocr_ref_max, ref_raw = self.parse_reference_range(
                test.get("Reference Range")
            )
            
            # Step 5: Validate reference range (use global fallback if invalid)
            ref_min, ref_max, used_fallback = validate_reference_range(
                ocr_ref_min, ocr_ref_max, canonical_test, gender
            )
            
            if used_fallback:
                self.stats["reference_fallbacks"] += 1
            
            # Step 6: Determine report type
            report_type = get_report_type(canonical_test)
            
            # Step 7: COMPUTE abnormality using RAW value against RAW reference
            # CRITICAL FIX: Do NOT use value_standard here!
            # value_standard may have unit conversion (e.g., 250 x10^9/L → 250000 cells/µL)
            # but reference_min/max are from OCR (still in original units)
            # So we MUST compare raw value against raw reference
            is_abnormal, abnormal_direction = self.compute_abnormality(
                value,  # Use RAW value, not value_standard
                ref_min,
                ref_max
            )
            
            # Create document
            doc = TestDocument(
                patient_id=patient_id,
                patient_name=patient_name,
                age=age,
                gender=gender,
                canonical_test=canonical_test.value,  # Store ENUM value string
                raw_test_name=raw_test_name,
                value=value,
                value_text=value_text,
                unit=raw_unit,
                value_standard=value_standard,
                unit_standard=unit_standard,
                reference_min=ref_min,
                reference_max=ref_max,
                reference_raw=ref_raw,
                used_global_reference=used_fallback,
                is_abnormal=is_abnormal,
                abnormal_direction=abnormal_direction,
                report_type=report_type,
                report_date=report_date,  # Now captured from JSON
                source_image=source_image,
                created_at=datetime.utcnow()
            )
            
            documents.append(doc)
            
            # Update stats
            if value is not None:
                self.stats["tests_with_values"] += 1
            if is_abnormal:
                self.stats["tests_abnormal"] += 1
        
        return documents
    
    def _create_dedup_key(self, doc: TestDocument) -> str:
        """Create a unique key for deduplication based on patient + test + value"""
        return f"{doc.patient_name}|{doc.canonical_test}|{doc.value}|{doc.unit}"
    
    def ingest(self) -> List[TestDocument]:
        """
        Main ingestion process.
        Returns list of normalized TestDocuments.
        
        INCLUDES DEDUPLICATION: Removes exact duplicate entries
        """
        if not self.raw_data:
            if not self.load_json():
                return []
        
        self.documents = []
        seen_keys = set()
        duplicates_removed = 0
        
        for patient_data in self.raw_data:
            patient_docs = self.process_patient(patient_data)
            
            # Deduplicate as we go
            for doc in patient_docs:
                key = self._create_dedup_key(doc)
                if key not in seen_keys:
                    seen_keys.add(key)
                    self.documents.append(doc)
                else:
                    duplicates_removed += 1
            
            self.stats["patients_processed"] += 1
        
        self.stats["tests_extracted"] = len(self.documents)
        self.stats["duplicates_removed"] = duplicates_removed
        
        # Deduplicate unmapped tests
        self.stats["unmapped_tests"] = list(set(self.stats["unmapped_tests"]))
        
        return self.documents
    
    def print_stats(self):
        """Print ingestion statistics"""
        print("\n" + "="*50)
        print("📊 INGESTION STATISTICS (V2)")
        print("="*50)
        print(f"Patients processed:      {self.stats['patients_processed']}")
        print(f"Tests extracted:         {self.stats['tests_extracted']}")
        print(f"Tests with values:       {self.stats['tests_with_values']}")
        print(f"Tests abnormal:          {self.stats['tests_abnormal']}")
        print(f"Tests unknown/skipped:   {self.stats['tests_unknown']}")
        print(f"Reference fallbacks:     {self.stats['reference_fallbacks']}")
        print(f"Duplicates removed:      {self.stats.get('duplicates_removed', 0)}")
        
        if self.stats["unmapped_tests"]:
            print(f"\n⚠️ Unmapped tests ({len(self.stats['unmapped_tests'])}):")
            for test in sorted(self.stats["unmapped_tests"])[:10]:
                print(f"   - {test}")
            if len(self.stats["unmapped_tests"]) > 10:
                print(f"   ... and {len(self.stats['unmapped_tests']) - 10} more")


# Legacy alias for compatibility
JSONIngester = JSONIngesterV2


async def ingest_json_to_mongodb_v2(json_path: str) -> Dict[str, Any]:
    """
    Full pipeline: JSON → Parse → Normalize → Insert to MongoDB
    
    Returns:
        Dict with success status, inserted count, and stats
    """
    from db.models import mongo_manager
    
    try:
        # Step 1: Load and process JSON
        ingester = JSONIngesterV2(json_path)
        documents = ingester.ingest()  # Correct method name
        
        if not documents:
            return {
                "success": False,
                "error": "No documents extracted from JSON",
                "inserted": 0,
                "stats": ingester.stats
            }
        
        # Print stats
        ingester.print_stats()
        
        # Step 2: Clear existing data
        collection = await mongo_manager.get_collection()
        delete_result = await collection.delete_many({})
        print(f"\n🗑️ Cleared {delete_result.deleted_count} existing records")
        
        # Step 3: Insert new documents
        docs_to_insert = [doc.to_dict() for doc in documents]
        result = await collection.insert_many(docs_to_insert)
        
        inserted_count = len(result.inserted_ids)
        print(f"✅ Inserted {inserted_count} new records")
        
        return {
            "success": True,
            "inserted": inserted_count,
            "stats": {
                "reports": ingester.stats["patients_processed"],
                "tests_extracted": ingester.stats["tests_extracted"],
                "tests_abnormal": ingester.stats["tests_abnormal"],
                "reference_fallbacks": ingester.stats["reference_fallbacks"]
            }
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "inserted": 0,
            "stats": {}
        }
