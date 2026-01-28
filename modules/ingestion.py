# -*- coding: utf-8 -*-
"""
JSON Ingestion Module
Processes all_results_new.json → Normalized TestDocuments
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

from config.canonical_mappings import get_canonical_name, get_report_type
from config.unit_mappings import normalize_unit
from config.thresholds import check_abnormal
from db.models import TestDocument


class JSONIngester:
    """
    Ingests patient lab reports from JSON and produces normalized TestDocuments
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
        """
        Parse age from various formats:
        - "45 Yrs" → 45
        - "45" → 45
        - 45 → 45
        - "45 years" → 45
        """
        if age_str is None:
            return None
        
        if isinstance(age_str, (int, float)):
            return int(age_str)
        
        if isinstance(age_str, str):
            # Extract numeric part
            match = re.search(r'(\d+)', str(age_str))
            if match:
                return int(match.group(1))
        
        return None
    
    def parse_gender(self, gender_str: Any) -> Optional[str]:
        """
        Normalize gender to M/F/None
        """
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
        Parse test result value
        Returns: (numeric_value, original_text)
        
        Handles:
        - "5.2" → (5.2, "5.2")
        - "Positive" → (None, "Positive")
        - "< 10" → (10.0, "< 10")  # Use the number
        - "5.2 (High)" → (5.2, "5.2 (High)")
        """
        if result_str is None:
            return None, None
        
        text = str(result_str).strip()
        
        if not text:
            return None, None
        
        # Try to extract numeric value
        # Handle formats like "< 10", "> 5", "5.2 (High)"
        match = re.search(r'[<>]?\s*(\d+\.?\d*)', text)
        
        if match:
            try:
                numeric = float(match.group(1))
                return numeric, text
            except ValueError:
                pass
        
        # Non-numeric result (Positive, Negative, etc.)
        return None, text
    
    def parse_reference_range(self, ref_str: Any) -> Tuple[Optional[float], Optional[float], Optional[str]]:
        """
        Parse reference range string
        Returns: (min_value, max_value, original_string)
        
        Handles:
        - "12.0 - 16.0" → (12.0, 16.0)
        - "< 200" → (None, 200.0)
        - "> 60" → (60.0, None)
        - "4.5-5.5" → (4.5, 5.5)
        - "Negative" → (None, None)
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
    
    def process_patient(self, patient_data: Dict) -> List[TestDocument]:
        """
        Process a single patient's data into TestDocuments
        ONE test = ONE document
        """
        documents = []
        
        # Generate UUID for this patient
        patient_id = str(uuid.uuid4())
        
        # Extract patient info
        patient_name = patient_data.get("Patient Name", "Unknown")
        age = self.parse_age(patient_data.get("Age"))
        gender = self.parse_gender(patient_data.get("Gender"))
        source_image = patient_data.get("Image Filename")
        
        # Get tests array
        tests = patient_data.get("Tests", [])
        
        for test in tests:
            raw_test_name = test.get("Test Name", "")
            
            if not raw_test_name:
                continue
            
            # Step 2.2: Map to canonical name
            canonical_test = get_canonical_name(raw_test_name)
            
            if canonical_test == "UNKNOWN":
                self.stats["unmapped_tests"].append(raw_test_name)
            
            # Step 2.4: Parse value
            value, value_text = self.parse_value(test.get("Result"))
            
            # Step 2.3: Normalize unit
            raw_unit = test.get("Unit", "")
            unit = normalize_unit(raw_unit) if raw_unit else ""
            
            # Step 2.5: Parse reference range
            ref_min, ref_max, ref_raw = self.parse_reference_range(test.get("Reference Range"))
            
            # Step 2.6: Determine report type
            report_type = get_report_type(canonical_test)
            
            # Check abnormal status
            is_abnormal, direction = check_abnormal(canonical_test, value, gender)
            
            # Create document
            doc = TestDocument(
                patient_id=patient_id,
                patient_name=patient_name,
                age=age,
                gender=gender,
                canonical_test=canonical_test,
                raw_test_name=raw_test_name,
                value=value,
                value_text=value_text,
                unit=unit,
                reference_min=ref_min,
                reference_max=ref_max,
                reference_raw=ref_raw,
                is_abnormal=is_abnormal,
                abnormal_direction=direction,
                report_type=report_type,
                report_date=None,  # Not available in current JSON
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
    
    def ingest(self) -> List[TestDocument]:
        """
        Main ingestion process
        Returns list of normalized TestDocuments
        """
        if not self.raw_data:
            if not self.load_json():
                return []
        
        self.documents = []
        
        for patient_data in self.raw_data:
            patient_docs = self.process_patient(patient_data)
            self.documents.extend(patient_docs)
            self.stats["patients_processed"] += 1
        
        self.stats["tests_extracted"] = len(self.documents)
        
        # Deduplicate unmapped tests for reporting
        self.stats["unmapped_tests"] = list(set(self.stats["unmapped_tests"]))
        
        return self.documents
    
    def print_stats(self):
        """Print ingestion statistics"""
        print("\n" + "="*50)
        print("📊 INGESTION STATISTICS")
        print("="*50)
        print(f"Patients processed:    {self.stats['patients_processed']}")
        print(f"Tests extracted:       {self.stats['tests_extracted']}")
        print(f"Tests with values:     {self.stats['tests_with_values']}")
        print(f"Abnormal tests:        {self.stats['tests_abnormal']}")
        print(f"Unmapped test names:   {len(self.stats['unmapped_tests'])}")
        
        if self.stats['unmapped_tests']:
            print("\n⚠️  Unmapped tests (first 10):")
            for test in self.stats['unmapped_tests'][:10]:
                print(f"   - {test}")
        print("="*50 + "\n")


async def ingest_json_to_mongodb(json_path: str) -> Dict[str, Any]:
    """
    Full pipeline: JSON → Normalize → MongoDB
    """
    from db.models import mongo_manager
    
    # Step 1: Load and normalize
    ingester = JSONIngester(json_path)
    documents = ingester.ingest()
    
    if not documents:
        return {"success": False, "error": "No documents generated"}
    
    ingester.print_stats()
    
    # Step 2: Insert into MongoDB
    try:
        inserted_count = await mongo_manager.insert_many(documents)
        print(f"✅ Inserted {inserted_count} documents into MongoDB")
        
        return {
            "success": True,
            "inserted": inserted_count,
            "stats": ingester.stats
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


# For direct testing
if __name__ == "__main__":
    import asyncio
    
    json_path = Path(__file__).parent.parent / "all_results_new.json"
    
    # Test without MongoDB (just normalization)
    ingester = JSONIngester(str(json_path))
    docs = ingester.ingest()
    ingester.print_stats()
    
    # Print sample documents
    print("\n📄 SAMPLE DOCUMENTS (first 3):")
    for i, doc in enumerate(docs[:3]):
        print(f"\n--- Document {i+1} ---")
        print(f"  Patient: {doc.patient_name} ({doc.gender}, {doc.age}y)")
        print(f"  Test: {doc.canonical_test} (raw: {doc.raw_test_name})")
        print(f"  Value: {doc.value} {doc.unit}")
        print(f"  Reference: {doc.reference_min} - {doc.reference_max}")
        print(f"  Abnormal: {doc.is_abnormal} ({doc.abnormal_direction})")
        print(f"  Report Type: {doc.report_type}")
