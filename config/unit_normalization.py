# -*- coding: utf-8 -*-
"""
Unit Normalization V2
Converts all values to standard base units
Stores both raw and standardized values
"""

import re
from typing import Tuple, Optional
from config.canonical_mappings_v2 import CanonicalTest


# Standard units for each test category
STANDARD_UNITS = {
    # Cell counts - standardize to cells/µL
    "cell_count": "cells/µL",
    # Percentages
    "percentage": "%",
    # Concentration
    "g_per_dL": "g/dL",
    "mg_per_dL": "mg/dL",
    "ng_per_mL": "ng/mL",
    "pg_per_mL": "pg/mL",
    "mIU_per_L": "mIU/L",
    "U_per_L": "U/L",
    "mEq_per_L": "mEq/L",
    # Volume
    "fL": "fL",
    "pg": "pg",
    # Rate
    "mm_per_hr": "mm/hr",
}


# Unit conversion factors to standard units
# Format: (pattern, target_unit, multiplier)
UNIT_CONVERSIONS = {
    # ============== CELL COUNTS ==============
    # WBC/Platelet units to cells/µL
    "10^3/uL": ("cells/µL", 1000),
    "10³/µL": ("cells/µL", 1000),
    "10^3/µL": ("cells/µL", 1000),
    "x10³/µL": ("cells/µL", 1000),
    "x10^3/µL": ("cells/µL", 1000),
    "thousand/µL": ("cells/µL", 1000),
    "K/µL": ("cells/µL", 1000),
    "K/uL": ("cells/µL", 1000),
    
    "10^9/L": ("cells/µL", 1000),  # 10^9/L = 10^3/µL = 1000 cells/µL
    "×10⁹/L": ("cells/µL", 1000),
    "x10^9/L": ("cells/µL", 1000),
    
    "lakhs/cumm": ("cells/µL", 100000),  # 1 lakh = 100,000
    "lakh/cumm": ("cells/µL", 100000),
    "lac/cumm": ("cells/µL", 100000),
    "lacs/cumm": ("cells/µL", 100000),
    
    # Already in cells/µL
    "cells/µL": ("cells/µL", 1),
    "cells/uL": ("cells/µL", 1),
    "/µL": ("cells/µL", 1),
    "/uL": ("cells/µL", 1),
    "/cumm": ("cells/µL", 1),
    "/cu mm": ("cells/µL", 1),
    "per cumm": ("cells/µL", 1),
    
    # RBC units - to million/µL
    "million/µL": ("million/µL", 1),
    "million/uL": ("million/µL", 1),
    "mill/µL": ("million/µL", 1),
    "mill/cumm": ("million/µL", 1),
    "10^6/µL": ("million/µL", 1),
    "x10^6/µL": ("million/µL", 1),
    "10^12/L": ("million/µL", 1),  # 10^12/L = 10^6/µL
    "×10¹²/L": ("million/µL", 1),
    
    # ============== HEMOGLOBIN ==============
    "g/dL": ("g/dL", 1),
    "gm/dL": ("g/dL", 1),
    "g/dl": ("g/dL", 1),
    "gm/dl": ("g/dL", 1),
    "gms/dL": ("g/dL", 1),
    "gm%": ("g/dL", 1),  # gm% = g/dL (old notation)
    "g%": ("g/dL", 1),
    
    "g/L": ("g/dL", 0.1),  # g/L to g/dL: divide by 10
    "gm/L": ("g/dL", 0.1),
    
    # ============== PERCENTAGES ==============
    "%": ("%", 1),
    "percent": ("%", 1),
    
    # ============== ENZYME UNITS ==============
    "U/L": ("U/L", 1),
    "IU/L": ("U/L", 1),  # IU/L ≈ U/L for most enzymes
    "u/L": ("U/L", 1),
    
    # ============== ELECTROLYTES ==============
    "mEq/L": ("mEq/L", 1),
    "meq/L": ("mEq/L", 1),
    "mmol/L": ("mEq/L", 1),  # For monovalent ions, mmol/L = mEq/L
    
    # ============== GENERAL CONCENTRATIONS ==============
    "mg/dL": ("mg/dL", 1),
    "mg/dl": ("mg/dL", 1),
    "mg%": ("mg/dL", 1),
    
    "mg/L": ("mg/dL", 0.1),  # mg/L to mg/dL: divide by 10
    
    "ng/mL": ("ng/mL", 1),
    "ng/ml": ("ng/mL", 1),
    
    "pg/mL": ("pg/mL", 1),
    "pg/ml": ("pg/mL", 1),
    
    "µg/dL": ("µg/dL", 1),
    "ug/dL": ("µg/dL", 1),
    "mcg/dL": ("µg/dL", 1),
    
    # ============== THYROID ==============
    "mIU/L": ("mIU/L", 1),
    "µIU/mL": ("mIU/L", 1),
    "uIU/mL": ("mIU/L", 1),
    "mU/L": ("mIU/L", 1),
    
    "ng/dL": ("ng/dL", 1),
    "ng/dl": ("ng/dL", 1),
    
    # ============== CELL INDICES ==============
    "fL": ("fL", 1),
    "fl": ("fL", 1),
    "femtoliters": ("fL", 1),
    "femtolitre": ("fL", 1),
    
    "pg": ("pg", 1),
    "picograms": ("pg", 1),
    
    # ============== ESR ==============
    "mm/hr": ("mm/hr", 1),
    "mm/hour": ("mm/hr", 1),
    "mm/1hr": ("mm/hr", 1),
    "mm 1st hr": ("mm/hr", 1),
    "mm in 1 hr": ("mm/hr", 1),
    "mm at 1 hour": ("mm/hr", 1),
}


def normalize_unit(raw_unit: str) -> str:
    """
    Legacy function - just clean the unit string
    Use normalize_value_and_unit for full normalization
    """
    if not raw_unit:
        return ""
    
    # Basic cleaning
    cleaned = raw_unit.strip()
    cleaned = re.sub(r'\s+', ' ', cleaned)
    
    return cleaned


def normalize_value_and_unit(
    value: Optional[float],
    raw_unit: str,
    canonical_test: CanonicalTest
) -> Tuple[Optional[float], str, Optional[float], str]:
    """
    Normalize value and unit to standard form.
    
    Args:
        value: The raw numeric value
        raw_unit: The raw unit string from OCR
        canonical_test: The canonical test for context
        
    Returns:
        Tuple of (value_raw, unit_raw, value_standard, unit_standard)
    """
    if value is None:
        return None, raw_unit or "", None, ""
    
    # Clean raw unit
    cleaned_unit = raw_unit.strip().lower() if raw_unit else ""
    
    # Try to find a matching conversion
    for pattern, (target_unit, multiplier) in UNIT_CONVERSIONS.items():
        pattern_lower = pattern.lower()
        if pattern_lower in cleaned_unit or cleaned_unit == pattern_lower:
            value_standard = value * multiplier
            return value, raw_unit or "", value_standard, target_unit
    
    # No conversion found - try to infer from test type
    inferred = _infer_standard_unit(canonical_test)
    if inferred:
        # Assume raw value is in standard unit
        return value, raw_unit or "", value, inferred
    
    # Return as-is
    return value, raw_unit or "", value, raw_unit or ""


def _infer_standard_unit(canonical_test: CanonicalTest) -> Optional[str]:
    """Infer standard unit from test type"""
    
    # Cell counts
    if canonical_test in [CanonicalTest.WBC_COUNT, CanonicalTest.PLATELET_COUNT]:
        return "cells/µL"
    
    if canonical_test == CanonicalTest.RBC_COUNT:
        return "million/µL"
    
    # Percentages
    if canonical_test in [
        CanonicalTest.HEMATOCRIT, CanonicalTest.NEUTROPHILS, CanonicalTest.LYMPHOCYTES,
        CanonicalTest.MONOCYTES, CanonicalTest.EOSINOPHILS, CanonicalTest.BASOPHILS,
        CanonicalTest.RDW, CanonicalTest.HBA1C
    ]:
        return "%"
    
    # Hemoglobin
    if canonical_test == CanonicalTest.HEMOGLOBIN_CBC:
        return "g/dL"
    
    # Cell indices
    if canonical_test in [CanonicalTest.MCV, CanonicalTest.MPV, CanonicalTest.PDW]:
        return "fL"
    
    if canonical_test == CanonicalTest.MCH:
        return "pg"
    
    if canonical_test == CanonicalTest.MCHC:
        return "g/dL"
    
    # ESR
    if canonical_test == CanonicalTest.ESR:
        return "mm/hr"
    
    # Liver enzymes
    if canonical_test in [CanonicalTest.ALT, CanonicalTest.AST, CanonicalTest.ALP, CanonicalTest.GGT]:
        return "U/L"
    
    # Proteins
    if canonical_test in [CanonicalTest.ALBUMIN, CanonicalTest.TOTAL_PROTEIN, CanonicalTest.GLOBULIN]:
        return "g/dL"
    
    # Bilirubin
    if canonical_test in [CanonicalTest.BILIRUBIN_TOTAL, CanonicalTest.BILIRUBIN_DIRECT, CanonicalTest.BILIRUBIN_INDIRECT]:
        return "mg/dL"
    
    # Kidney function
    if canonical_test in [CanonicalTest.CREATININE, CanonicalTest.BUN, CanonicalTest.UREA, CanonicalTest.URIC_ACID]:
        return "mg/dL"
    
    # Electrolytes
    if canonical_test in [CanonicalTest.SODIUM, CanonicalTest.POTASSIUM, CanonicalTest.CHLORIDE]:
        return "mEq/L"
    
    if canonical_test in [CanonicalTest.CALCIUM, CanonicalTest.PHOSPHORUS]:
        return "mg/dL"
    
    # Thyroid
    if canonical_test == CanonicalTest.TSH:
        return "mIU/L"
    
    if canonical_test in [CanonicalTest.T3_TOTAL, CanonicalTest.T4_TOTAL]:
        return "µg/dL"
    
    if canonical_test in [CanonicalTest.FREE_T3, CanonicalTest.FREE_T4]:
        return "ng/dL"
    
    # Lipids
    if canonical_test in [
        CanonicalTest.TOTAL_CHOLESTEROL, CanonicalTest.LDL_CHOLESTEROL,
        CanonicalTest.HDL_CHOLESTEROL, CanonicalTest.VLDL_CHOLESTEROL,
        CanonicalTest.TRIGLYCERIDES
    ]:
        return "mg/dL"
    
    # Glucose
    if canonical_test in [CanonicalTest.GLUCOSE_FASTING, CanonicalTest.GLUCOSE_RANDOM, 
                          CanonicalTest.GLUCOSE_PP, CanonicalTest.AVERAGE_BLOOD_GLUCOSE]:
        return "mg/dL"
    
    # Vitamins
    if canonical_test == CanonicalTest.VITAMIN_D:
        return "ng/mL"
    
    if canonical_test == CanonicalTest.VITAMIN_B12:
        return "pg/mL"
    
    # Iron studies
    if canonical_test in [CanonicalTest.IRON, CanonicalTest.TIBC]:
        return "µg/dL"
    
    if canonical_test == CanonicalTest.FERRITIN:
        return "ng/mL"
    
    # CRP
    if canonical_test == CanonicalTest.CRP:
        return "mg/L"
    
    return None
