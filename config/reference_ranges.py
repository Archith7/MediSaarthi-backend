# -*- coding: utf-8 -*-
"""
Global Reference Ranges
Medical reference ranges for all canonical tests
Used as fallback when OCR reference is missing/invalid
"""

from typing import Dict, Optional, Tuple
from config.canonical_mappings_v2 import CanonicalTest


# Global Reference Ranges
# Format: CanonicalTest: {"min": value, "max": value, "unit": "standard_unit"}
# Gender-specific: {"male": {...}, "female": {...}, "default": {...}}

GLOBAL_REFERENCE_RANGES: Dict[CanonicalTest, Dict] = {
    # ============== CBC TESTS ==============
    CanonicalTest.HEMOGLOBIN_CBC: {
        "male": {"min": 13.0, "max": 17.5, "unit": "g/dL"},
        "female": {"min": 12.0, "max": 16.0, "unit": "g/dL"},
        "default": {"min": 12.0, "max": 17.0, "unit": "g/dL"}
    },
    CanonicalTest.RBC_COUNT: {
        "male": {"min": 4.5, "max": 5.9, "unit": "million/µL"},
        "female": {"min": 4.0, "max": 5.2, "unit": "million/µL"},
        "default": {"min": 4.0, "max": 5.9, "unit": "million/µL"}
    },
    CanonicalTest.WBC_COUNT: {
        "default": {"min": 4000, "max": 11000, "unit": "cells/µL"}
    },
    CanonicalTest.PLATELET_COUNT: {
        "default": {"min": 150000, "max": 450000, "unit": "cells/µL"}
    },
    CanonicalTest.HEMATOCRIT: {
        "male": {"min": 38.3, "max": 48.6, "unit": "%"},
        "female": {"min": 35.5, "max": 44.9, "unit": "%"},
        "default": {"min": 36, "max": 50, "unit": "%"}
    },
    CanonicalTest.MCV: {
        "default": {"min": 80, "max": 100, "unit": "fL"}
    },
    CanonicalTest.MCH: {
        "default": {"min": 27, "max": 32, "unit": "pg"}
    },
    CanonicalTest.MCHC: {
        "default": {"min": 32, "max": 36, "unit": "g/dL"}
    },
    CanonicalTest.RDW: {
        "default": {"min": 11.5, "max": 16.0, "unit": "%"}
    },
    CanonicalTest.MPV: {
        "default": {"min": 7.5, "max": 11.5, "unit": "fL"}
    },
    CanonicalTest.PDW: {
        "default": {"min": 9.0, "max": 17.0, "unit": "fL"}
    },
    CanonicalTest.PCT: {
        "default": {"min": 0.1, "max": 0.5, "unit": "%"}
    },
    CanonicalTest.NEUTROPHILS: {
        "default": {"min": 40, "max": 75, "unit": "%"}
    },
    CanonicalTest.LYMPHOCYTES: {
        "default": {"min": 20, "max": 45, "unit": "%"}
    },
    CanonicalTest.MONOCYTES: {
        "default": {"min": 2, "max": 10, "unit": "%"}
    },
    CanonicalTest.EOSINOPHILS: {
        "default": {"min": 1, "max": 6, "unit": "%"}
    },
    CanonicalTest.BASOPHILS: {
        "default": {"min": 0, "max": 2, "unit": "%"}
    },
    CanonicalTest.ESR: {
        "male": {"min": 0, "max": 15, "unit": "mm/hr"},
        "female": {"min": 0, "max": 20, "unit": "mm/hr"},
        "default": {"min": 0, "max": 20, "unit": "mm/hr"}
    },
    
    # ============== LIVER TESTS ==============
    CanonicalTest.ALT: {
        "default": {"min": 7, "max": 56, "unit": "U/L"}
    },
    CanonicalTest.AST: {
        "default": {"min": 8, "max": 48, "unit": "U/L"}
    },
    CanonicalTest.ALP: {
        "default": {"min": 44, "max": 147, "unit": "U/L"}
    },
    CanonicalTest.GGT: {
        "male": {"min": 0, "max": 65, "unit": "U/L"},
        "female": {"min": 0, "max": 45, "unit": "U/L"},
        "default": {"min": 0, "max": 55, "unit": "U/L"}
    },
    CanonicalTest.BILIRUBIN_TOTAL: {
        "default": {"min": 0.1, "max": 1.2, "unit": "mg/dL"}
    },
    CanonicalTest.BILIRUBIN_DIRECT: {
        "default": {"min": 0, "max": 0.3, "unit": "mg/dL"}
    },
    CanonicalTest.BILIRUBIN_INDIRECT: {
        "default": {"min": 0.1, "max": 0.9, "unit": "mg/dL"}
    },
    CanonicalTest.ALBUMIN: {
        "default": {"min": 3.5, "max": 5.5, "unit": "g/dL"}
    },
    CanonicalTest.TOTAL_PROTEIN: {
        "default": {"min": 6.0, "max": 8.3, "unit": "g/dL"}
    },
    CanonicalTest.GLOBULIN: {
        "default": {"min": 2.0, "max": 3.5, "unit": "g/dL"}
    },
    
    # ============== KIDNEY TESTS ==============
    CanonicalTest.CREATININE: {
        "male": {"min": 0.7, "max": 1.3, "unit": "mg/dL"},
        "female": {"min": 0.6, "max": 1.1, "unit": "mg/dL"},
        "default": {"min": 0.6, "max": 1.2, "unit": "mg/dL"}
    },
    CanonicalTest.BUN: {
        "default": {"min": 7, "max": 20, "unit": "mg/dL"}
    },
    CanonicalTest.UREA: {
        "default": {"min": 15, "max": 45, "unit": "mg/dL"}
    },
    CanonicalTest.EGFR: {
        "default": {"min": 90, "max": None, "unit": "mL/min/1.73m²"}
    },
    CanonicalTest.URIC_ACID: {
        "male": {"min": 3.5, "max": 7.2, "unit": "mg/dL"},
        "female": {"min": 2.5, "max": 6.2, "unit": "mg/dL"},
        "default": {"min": 2.5, "max": 7.0, "unit": "mg/dL"}
    },
    CanonicalTest.SODIUM: {
        "default": {"min": 136, "max": 145, "unit": "mEq/L"}
    },
    CanonicalTest.POTASSIUM: {
        "default": {"min": 3.5, "max": 5.0, "unit": "mEq/L"}
    },
    CanonicalTest.CHLORIDE: {
        "default": {"min": 98, "max": 106, "unit": "mEq/L"}
    },
    CanonicalTest.CALCIUM: {
        "default": {"min": 8.5, "max": 10.5, "unit": "mg/dL"}
    },
    CanonicalTest.PHOSPHORUS: {
        "default": {"min": 2.5, "max": 4.5, "unit": "mg/dL"}
    },
    
    # ============== THYROID TESTS ==============
    CanonicalTest.TSH: {
        "default": {"min": 0.4, "max": 4.5, "unit": "mIU/L"}
    },
    CanonicalTest.T3_TOTAL: {
        "default": {"min": 60, "max": 181, "unit": "ng/dL"}
    },
    CanonicalTest.T4_TOTAL: {
        "default": {"min": 4.5, "max": 12.0, "unit": "µg/dL"}
    },
    CanonicalTest.FREE_T3: {
        "default": {"min": 2.3, "max": 4.2, "unit": "pg/mL"}
    },
    CanonicalTest.FREE_T4: {
        "default": {"min": 0.8, "max": 1.8, "unit": "ng/dL"}
    },
    
    # ============== LIPID TESTS ==============
    CanonicalTest.TOTAL_CHOLESTEROL: {
        "default": {"min": None, "max": 200, "unit": "mg/dL"}
    },
    CanonicalTest.LDL_CHOLESTEROL: {
        "default": {"min": None, "max": 100, "unit": "mg/dL"}
    },
    CanonicalTest.HDL_CHOLESTEROL: {
        "male": {"min": 40, "max": None, "unit": "mg/dL"},
        "female": {"min": 50, "max": None, "unit": "mg/dL"},
        "default": {"min": 40, "max": None, "unit": "mg/dL"}
    },
    CanonicalTest.VLDL_CHOLESTEROL: {
        "default": {"min": None, "max": 30, "unit": "mg/dL"}
    },
    CanonicalTest.TRIGLYCERIDES: {
        "default": {"min": None, "max": 150, "unit": "mg/dL"}
    },
    
    # ============== DIABETES TESTS ==============
    CanonicalTest.GLUCOSE_FASTING: {
        "default": {"min": 70, "max": 100, "unit": "mg/dL"}
    },
    CanonicalTest.GLUCOSE_RANDOM: {
        "default": {"min": None, "max": 140, "unit": "mg/dL"}
    },
    CanonicalTest.GLUCOSE_PP: {
        "default": {"min": None, "max": 140, "unit": "mg/dL"}
    },
    CanonicalTest.HBA1C: {
        "default": {"min": None, "max": 5.7, "unit": "%"}
    },
    CanonicalTest.AVERAGE_BLOOD_GLUCOSE: {
        "default": {"min": None, "max": 120, "unit": "mg/dL"}
    },
    
    # ============== MISCELLANEOUS ==============
    CanonicalTest.VITAMIN_D: {
        "default": {"min": 30, "max": 100, "unit": "ng/mL"}
    },
    CanonicalTest.VITAMIN_B12: {
        "default": {"min": 200, "max": 900, "unit": "pg/mL"}
    },
    CanonicalTest.IRON: {
        "male": {"min": 65, "max": 175, "unit": "µg/dL"},
        "female": {"min": 50, "max": 170, "unit": "µg/dL"},
        "default": {"min": 50, "max": 175, "unit": "µg/dL"}
    },
    CanonicalTest.FERRITIN: {
        "male": {"min": 20, "max": 300, "unit": "ng/mL"},
        "female": {"min": 10, "max": 150, "unit": "ng/mL"},
        "default": {"min": 10, "max": 300, "unit": "ng/mL"}
    },
    CanonicalTest.TIBC: {
        "default": {"min": 250, "max": 400, "unit": "µg/dL"}
    },
    CanonicalTest.CRP: {
        "default": {"min": None, "max": 3, "unit": "mg/L"}
    },
}


def get_reference_range(
    canonical_test: CanonicalTest,
    gender: Optional[str] = None
) -> Tuple[Optional[float], Optional[float], str]:
    """
    Get reference range for a test.
    
    Args:
        canonical_test: The canonical test enum
        gender: 'M', 'F', or None
        
    Returns:
        Tuple of (min_value, max_value, unit)
    """
    if canonical_test not in GLOBAL_REFERENCE_RANGES:
        return None, None, ""
    
    ranges = GLOBAL_REFERENCE_RANGES[canonical_test]
    
    # Determine which gender key to use
    gender_key = "default"
    if gender:
        g = gender.upper().strip()
        if g in ["M", "MALE"]:
            gender_key = "male"
        elif g in ["F", "FEMALE"]:
            gender_key = "female"
    
    # Get gender-specific or default
    ref = ranges.get(gender_key, ranges.get("default", {}))
    
    return ref.get("min"), ref.get("max"), ref.get("unit", "")


def validate_reference_range(
    ocr_min: Optional[float],
    ocr_max: Optional[float],
    canonical_test: CanonicalTest,
    gender: Optional[str] = None
) -> Tuple[Optional[float], Optional[float], bool]:
    """
    Validate OCR reference range and return valid values.
    Falls back to global reference if OCR is invalid.
    
    Args:
        ocr_min: OCR-extracted minimum
        ocr_max: OCR-extracted maximum
        canonical_test: The canonical test
        gender: Patient gender
        
    Returns:
        Tuple of (validated_min, validated_max, used_fallback)
    """
    # Get global reference as fallback
    global_min, global_max, _ = get_reference_range(canonical_test, gender)
    
    # Check if OCR values are valid
    ocr_valid = True
    
    # Rule 1: If both exist, min must be less than max
    if ocr_min is not None and ocr_max is not None:
        if ocr_min > ocr_max:
            ocr_valid = False
    
    # Rule 2: Values should be positive (most lab values)
    if ocr_min is not None and ocr_min < 0:
        ocr_valid = False
    if ocr_max is not None and ocr_max < 0:
        ocr_valid = False
    
    if ocr_valid and (ocr_min is not None or ocr_max is not None):
        # Use OCR values (may be partial)
        final_min = ocr_min if ocr_min is not None else global_min
        final_max = ocr_max if ocr_max is not None else global_max
        return final_min, final_max, False
    else:
        # Use global fallback
        return global_min, global_max, True


def get_standard_unit(canonical_test: CanonicalTest) -> str:
    """Get the standard unit for a test"""
    if canonical_test in GLOBAL_REFERENCE_RANGES:
        ref = GLOBAL_REFERENCE_RANGES[canonical_test]
        default_ref = ref.get("default", ref.get("male", ref.get("female", {})))
        return default_ref.get("unit", "")
    return ""
