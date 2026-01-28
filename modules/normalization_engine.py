# -*- coding: utf-8 -*-
"""
Normalization Engine - CORE LOGIC
Transforms raw OCR output into canonical, analytics-ready format
"""
import re
from typing import Optional, Dict, List, Any
from datetime import datetime
import logging

# Import canonical test dictionary
from config.canonical_tests import (
    CANONICAL_TEST_DICTIONARY,
    UNIT_MAPPINGS,
    DEFAULT_REFERENCE_RANGES,
    CBC_TESTS,
    LIVER_TESTS,
    KIDNEY_TESTS,
    THYROID_TESTS,
    LIPID_TESTS
)

logger = logging.getLogger(__name__)


class NormalizationEngine:
    """
    7-Step Normalization Algorithm:
    1. Clean raw text (strip, lowercase, remove artifacts)
    2. Map to canonical test name (dictionary lookup)
    3. AI fallback for unknown tests (optional)
    4. Normalize result (float conversion, handle <, >, etc.)
    5. Normalize unit (map to standard units)
    6. Parse reference range (extract min/max)
    7. Assign report type (CBC, Liver, Kidney, etc.)
    """
    
    def __init__(self, use_ai_fallback: bool = False, openai_api_key: str = None):
        self.use_ai_fallback = use_ai_fallback
        self.openai_api_key = openai_api_key
        self.canonical_dict = CANONICAL_TEST_DICTIONARY
        self.unit_mappings = UNIT_MAPPINGS
        self.reference_ranges = DEFAULT_REFERENCE_RANGES
        self.unmapped_tests = []
    
    def normalize(self, raw_ocr_output: Dict) -> Dict:
        """
        Main normalization entry point
        
        Input: Raw OCR JSON
        Output: Normalized, analytics-ready JSON
        """
        if not raw_ocr_output.get("success"):
            return {
                "success": False,
                "error": raw_ocr_output.get("error", "Unknown OCR error"),
                "normalized_tests": []
            }
        
        normalized_tests = []
        unmapped_count = 0
        
        for raw_test in raw_ocr_output.get("tests", []):
            normalized = self.normalize_single_test(raw_test)
            
            if normalized:
                normalized_tests.append(normalized)
            else:
                unmapped_count += 1
        
        # Determine report types present
        report_types = self._detect_report_types(normalized_tests)
        
        return {
            "success": True,
            "normalization_timestamp": datetime.utcnow().isoformat(),
            "patient_name": raw_ocr_output.get("patient_name"),
            "age": raw_ocr_output.get("age"),
            "gender": raw_ocr_output.get("gender"),
            "report_date": self._parse_date(raw_ocr_output.get("report_date_raw")),
            "report_types": report_types,
            "normalized_tests": normalized_tests,
            "total_tests": len(normalized_tests),
            "unmapped_tests": unmapped_count,
            "source_image": raw_ocr_output.get("source_image")
        }
    
    def normalize_single_test(self, raw_test: Dict) -> Optional[Dict]:
        """
        Normalize a single test entry through the 7-step algorithm
        """
        try:
            # Step 1: Clean raw text
            raw_name = self._clean_text(raw_test.get("test_name_raw", ""))
            raw_result = raw_test.get("result_raw", "")
            raw_unit = raw_test.get("unit_raw", "")
            raw_reference = raw_test.get("reference_raw", "")
            
            if not raw_name or not raw_result:
                return None
            
            # Step 2: Map to canonical test name
            canonical_name = self._map_to_canonical(raw_name)
            
            # Step 3: AI fallback (if enabled and not mapped)
            if canonical_name is None and self.use_ai_fallback:
                canonical_name = self._ai_fallback_mapping(raw_name)
            
            if canonical_name is None:
                # Store unmapped for review
                self.unmapped_tests.append(raw_name)
                canonical_name = raw_name.upper()  # Use cleaned raw as fallback
            
            # Step 4: Normalize result value
            normalized_value, value_modifier = self._normalize_result(raw_result)
            
            if normalized_value is None:
                return None
            
            # Step 5: Normalize unit
            normalized_unit = self._normalize_unit(raw_unit, canonical_name)
            
            # Step 6: Parse reference range
            ref_min, ref_max = self._parse_reference_range(raw_reference, canonical_name)
            
            # Step 7: Assign report type
            report_type = self._assign_report_type(canonical_name)
            
            # Determine if abnormal
            is_abnormal = self._check_abnormal(normalized_value, ref_min, ref_max)
            
            return {
                "test_name_raw": raw_test.get("test_name_raw"),
                "canonical_test": canonical_name,
                "value": normalized_value,
                "value_modifier": value_modifier,  # None, "less_than", "greater_than"
                "unit": normalized_unit,
                "reference_min": ref_min,
                "reference_max": ref_max,
                "is_abnormal": is_abnormal,
                "report_type": report_type
            }
        
        except Exception as e:
            logger.error(f"Error normalizing test: {raw_test}, Error: {e}")
            return None
    
    def _clean_text(self, text: str) -> str:
        """Step 1: Clean and standardize text"""
        if not text:
            return ""
        
        # Strip whitespace
        text = text.strip()
        
        # Remove common OCR artifacts
        text = re.sub(r'[|\[\]{}]', '', text)
        
        # Normalize spaces
        text = re.sub(r'\s+', ' ', text)
        
        # Remove leading/trailing special characters
        text = re.sub(r'^[\-\.\:\s]+|[\-\.\:\s]+$', '', text)
        
        return text
    
    def _map_to_canonical(self, raw_name: str) -> Optional[str]:
        """Step 2: Map raw test name to canonical name using dictionary"""
        if not raw_name:
            return None
        
        # Convert to lowercase for matching
        raw_lower = raw_name.lower().strip()
        
        # Direct lookup
        if raw_lower in self.canonical_dict:
            return self.canonical_dict[raw_lower]
        
        # Try with variations
        variations = [
            raw_lower,
            raw_lower.replace(" ", ""),
            raw_lower.replace(".", ""),
            raw_lower.replace("-", " "),
            re.sub(r'\s+', ' ', raw_lower)
        ]
        
        for variant in variations:
            if variant in self.canonical_dict:
                return self.canonical_dict[variant]
        
        # Partial matching - check if any key is contained in the raw name
        for key, canonical in self.canonical_dict.items():
            if key in raw_lower or raw_lower in key:
                return canonical
        
        return None
    
    def _ai_fallback_mapping(self, raw_name: str) -> Optional[str]:
        """Step 3: Use AI (LLM) to map unknown test names"""
        if not self.openai_api_key:
            return None
        
        try:
            from openai import OpenAI
            client = OpenAI(api_key=self.openai_api_key)
            
            prompt = f"""You are a medical laboratory expert. Map the following raw OCR test name 
to its correct canonical test name. Only return the canonical name, nothing else.

Raw test name: "{raw_name}"

Common canonical names include: Hemoglobin, RBC Count, WBC Count, Platelet Count, 
Hematocrit, MCV, MCH, MCHC, RDW, Neutrophils, Lymphocytes, Monocytes, Eosinophils, 
Basophils, ALT, AST, ALP, GGT, Bilirubin Total, Albumin, Creatinine, BUN, eGFR, 
Sodium, Potassium, Chloride, Glucose Fasting, HbA1c, TSH, T3, T4, etc.

If you cannot determine the correct mapping, return "UNKNOWN"."""

            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=50,
                temperature=0
            )
            
            result = response.choices[0].message.content.strip()
            if result and result != "UNKNOWN":
                return result
            
        except Exception as e:
            logger.error(f"AI fallback error: {e}")
        
        return None
    
    def _normalize_result(self, raw_result: str) -> tuple:
        """Step 4: Normalize result value to float"""
        if not raw_result:
            return None, None
        
        raw_result = str(raw_result).strip()
        modifier = None
        
        # Handle less than / greater than
        if raw_result.startswith("<") or raw_result.lower().startswith("less"):
            modifier = "less_than"
            raw_result = re.sub(r'^[<\s]+|less\s*than\s*', '', raw_result, flags=re.I)
        elif raw_result.startswith(">") or raw_result.lower().startswith("greater"):
            modifier = "greater_than"
            raw_result = re.sub(r'^[>\s]+|greater\s*than\s*', '', raw_result, flags=re.I)
        
        # Extract numeric value
        # Handle comma as decimal separator
        raw_result = raw_result.replace(",", ".")
        
        # Extract first number
        match = re.search(r'(\d+\.?\d*)', raw_result)
        if match:
            try:
                value = float(match.group(1))
                return value, modifier
            except ValueError:
                return None, None
        
        return None, None
    
    def _normalize_unit(self, raw_unit: str, canonical_name: str) -> str:
        """Step 5: Normalize unit to standard format"""
        if not raw_unit:
            # Use default unit from reference ranges
            if canonical_name in self.reference_ranges:
                return self.reference_ranges[canonical_name].get("unit", "")
            return ""
        
        raw_unit = raw_unit.strip().lower()
        
        # Check unit mappings
        if raw_unit in self.unit_mappings:
            return self.unit_mappings[raw_unit]
        
        # Common normalizations
        unit_map = {
            "g/dl": "g/dL",
            "g/l": "g/L",
            "mg/dl": "mg/dL",
            "umol/l": "µmol/L",
            "mmol/l": "mmol/L",
            "iu/l": "IU/L",
            "u/l": "U/L",
            "ng/ml": "ng/mL",
            "pg/ml": "pg/mL",
            "miu/l": "mIU/L",
            "miu/ml": "mIU/mL",
            "cells/ul": "cells/µL",
            "10^3/ul": "×10³/µL",
            "10^6/ul": "×10⁶/µL",
            "10^12/l": "×10¹²/L",
            "10^9/l": "×10⁹/L",
            "%": "%",
            "fl": "fL",
            "pg": "pg",
            "g%": "g/dL"
        }
        
        return unit_map.get(raw_unit, raw_unit.upper())
    
    def _parse_reference_range(self, raw_reference: str, canonical_name: str) -> tuple:
        """Step 6: Parse reference range into min/max"""
        ref_min = None
        ref_max = None
        
        if raw_reference:
            raw_reference = str(raw_reference).replace(",", ".")
            
            # Pattern: MIN - MAX
            match = re.search(r'(\d+\.?\d*)\s*[\-–]\s*(\d+\.?\d*)', raw_reference)
            if match:
                try:
                    ref_min = float(match.group(1))
                    ref_max = float(match.group(2))
                except ValueError:
                    pass
        
        # Use defaults if not extracted
        if ref_min is None or ref_max is None:
            if canonical_name in self.reference_ranges:
                ref_data = self.reference_ranges[canonical_name]
                ref_min = ref_min or ref_data.get("min")
                ref_max = ref_max or ref_data.get("max")
        
        return ref_min, ref_max
    
    def _assign_report_type(self, canonical_name: str) -> str:
        """Step 7: Assign report type based on test name"""
        if canonical_name in CBC_TESTS:
            return "CBC"
        elif canonical_name in LIVER_TESTS:
            return "Liver Function"
        elif canonical_name in KIDNEY_TESTS:
            return "Kidney Function"
        elif canonical_name in THYROID_TESTS:
            return "Thyroid"
        elif canonical_name in LIPID_TESTS:
            return "Lipid Profile"
        else:
            return "Other"
    
    def _detect_report_types(self, normalized_tests: List[Dict]) -> List[str]:
        """Detect all report types present in the results"""
        report_types = set()
        for test in normalized_tests:
            if test.get("report_type"):
                report_types.add(test["report_type"])
        return list(report_types)
    
    def _check_abnormal(self, value: float, ref_min: float, ref_max: float) -> Optional[bool]:
        """Check if value is outside reference range"""
        if value is None:
            return None
        
        if ref_min is not None and value < ref_min:
            return True
        if ref_max is not None and value > ref_max:
            return True
        if ref_min is not None and ref_max is not None:
            return False
        
        return None  # Cannot determine
    
    def _parse_date(self, raw_date: str) -> Optional[str]:
        """Parse raw date string to ISO format"""
        if not raw_date:
            return None
        
        # Common date formats
        formats = [
            "%d/%m/%Y",
            "%d-%m-%Y",
            "%m/%d/%Y",
            "%Y-%m-%d",
            "%d/%m/%y",
            "%d-%m-%y"
        ]
        
        for fmt in formats:
            try:
                parsed = datetime.strptime(raw_date, fmt)
                return parsed.date().isoformat()
            except ValueError:
                continue
        
        return raw_date  # Return raw if cannot parse
    
    def get_unmapped_tests(self) -> List[str]:
        """Return list of tests that couldn't be mapped"""
        return list(set(self.unmapped_tests))


def normalize_ocr_output(raw_ocr_output: Dict, use_ai: bool = False, api_key: str = None) -> Dict:
    """
    Convenience function to normalize OCR output
    """
    engine = NormalizationEngine(use_ai_fallback=use_ai, openai_api_key=api_key)
    return engine.normalize(raw_ocr_output)


# For standalone testing
if __name__ == "__main__":
    # Test with sample raw OCR data
    sample_raw_ocr = {
        "success": True,
        "patient_name": "JOHN DOE",
        "age": 35,
        "gender": "Male",
        "report_date_raw": "15/01/2024",
        "tests": [
            {"test_name_raw": "Hemoglobin", "result_raw": "14.5", "unit_raw": "g/dl", "reference_raw": "13.0-17.0"},
            {"test_name_raw": "RBC", "result_raw": "4.8", "unit_raw": "10^6/ul", "reference_raw": "4.5-5.5"},
            {"test_name_raw": "wbc count", "result_raw": "7500", "unit_raw": "cells/ul", "reference_raw": "4000-11000"},
            {"test_name_raw": "plts", "result_raw": "250", "unit_raw": "10^3/ul", "reference_raw": "150-400"},
        ],
        "source_image": "test_report.png"
    }
    
    import json
    engine = NormalizationEngine()
    result = engine.normalize(sample_raw_ocr)
    print(json.dumps(result, indent=2, default=str))
