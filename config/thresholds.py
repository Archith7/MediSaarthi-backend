# -*- coding: utf-8 -*-
"""
Medical Thresholds Configuration
PREDEFINED thresholds - NOT AI-guessed
Used for deficiency detection and abnormal flagging
"""

# Deficiency Thresholds
# Format: "Test Name": {gender: {low: x, high: y, critical_low: z, critical_high: w}}
DEFICIENCY_THRESHOLDS = {
    # ============== CBC ==============
    "Hemoglobin": {
        "male": {"low": 13.0, "high": 17.5, "critical_low": 7.0, "critical_high": 20.0},
        "female": {"low": 12.0, "high": 16.0, "critical_low": 7.0, "critical_high": 20.0},
        "default": {"low": 12.0, "high": 17.0, "critical_low": 7.0, "critical_high": 20.0}
    },
    "RBC Count": {
        "male": {"low": 4.5, "high": 5.5, "critical_low": 3.0},
        "female": {"low": 4.0, "high": 5.0, "critical_low": 3.0},
        "default": {"low": 4.0, "high": 5.5, "critical_low": 3.0}
    },
    "WBC Count": {
        "default": {"low": 4000, "high": 11000, "critical_low": 2000, "critical_high": 30000}
    },
    "Platelet Count": {
        "default": {"low": 150000, "high": 450000, "critical_low": 50000, "critical_high": 1000000}
    },
    "Hematocrit": {
        "male": {"low": 38.3, "high": 48.6},
        "female": {"low": 35.5, "high": 44.9},
        "default": {"low": 36, "high": 50}
    },
    "MCV": {"default": {"low": 80, "high": 100}},
    "MCH": {"default": {"low": 27, "high": 32}},
    "MCHC": {"default": {"low": 32, "high": 36}},
    "RDW": {"default": {"low": 11.5, "high": 16.0}},
    "Neutrophils": {"default": {"low": 40, "high": 75}},
    "Lymphocytes": {"default": {"low": 20, "high": 45}},
    "Monocytes": {"default": {"low": 2, "high": 10}},
    "Eosinophils": {"default": {"low": 1, "high": 6}},
    "Basophils": {"default": {"low": 0, "high": 2}},
    "ESR": {
        "male": {"high": 15},
        "female": {"high": 20},
        "default": {"high": 20}
    },
    
    # ============== LIVER ==============
    "ALT": {"default": {"high": 56}},
    "AST": {"default": {"high": 40}},
    "ALP": {"default": {"low": 44, "high": 147}},
    "GGT": {"default": {"high": 48}},
    "Bilirubin Total": {"default": {"high": 1.2}},
    "Bilirubin Direct": {"default": {"high": 0.3}},
    "Albumin": {"default": {"low": 3.5, "high": 5.5}},
    "Total Protein": {"default": {"low": 6.0, "high": 8.3}},
    
    # ============== KIDNEY ==============
    "Creatinine": {
        "male": {"high": 1.3},
        "female": {"high": 1.1},
        "default": {"high": 1.2}
    },
    "BUN": {"default": {"low": 7, "high": 20}},
    "Urea": {"default": {"low": 15, "high": 45}},
    "eGFR": {"default": {"low": 90}},
    "Uric Acid": {
        "male": {"high": 7.0},
        "female": {"high": 6.0},
        "default": {"high": 7.0}
    },
    "Sodium": {"default": {"low": 136, "high": 145}},
    "Potassium": {"default": {"low": 3.5, "high": 5.0}},
    "Chloride": {"default": {"low": 98, "high": 106}},
    
    # ============== THYROID ==============
    "TSH": {"default": {"low": 0.4, "high": 4.5}},
    "T3 Total": {"default": {"low": 60, "high": 181}},
    "T4 Total": {"default": {"low": 4.5, "high": 12.0}},
    "Free T3": {"default": {"low": 2.3, "high": 4.2}},
    "Free T4": {"default": {"low": 0.8, "high": 1.8}},
    
    # ============== LIPID ==============
    "Total Cholesterol": {"default": {"high": 200}},
    "LDL Cholesterol": {"default": {"high": 100}},
    "HDL Cholesterol": {"default": {"low": 40}},
    "Triglycerides": {"default": {"high": 150}},
    
    # ============== DIABETES ==============
    "Glucose Fasting": {"default": {"low": 70, "high": 100}},
    "Glucose Random": {"default": {"high": 140}},
    "HbA1c": {"default": {"high": 5.7}},
    "Average Blood Glucose": {"default": {"high": 120}},
}

# Medical Condition Mappings
# Maps condition keywords to test + condition type
CONDITION_MAPPINGS = {
    "anemic": {"test": "Hemoglobin", "condition": "low"},
    "anemia": {"test": "Hemoglobin", "condition": "low"},
    "low hemoglobin": {"test": "Hemoglobin", "condition": "low"},
    "low hb": {"test": "Hemoglobin", "condition": "low"},
    "low rbc": {"test": "RBC Count", "condition": "low"},
    "low wbc": {"test": "WBC Count", "condition": "low"},
    "high wbc": {"test": "WBC Count", "condition": "high"},
    "leukopenia": {"test": "WBC Count", "condition": "low"},
    "leukocytosis": {"test": "WBC Count", "condition": "high"},
    "thrombocytopenia": {"test": "Platelet Count", "condition": "low"},
    "low platelets": {"test": "Platelet Count", "condition": "low"},
    "high cholesterol": {"test": "Total Cholesterol", "condition": "high"},
    "diabetic": {"test": "HbA1c", "condition": "high"},
    "high sugar": {"test": "Glucose Fasting", "condition": "high"},
    "high creatinine": {"test": "Creatinine", "condition": "high"},
    "thyroid issue": {"test": "TSH", "condition": "abnormal"},
    "hypothyroid": {"test": "TSH", "condition": "high"},
    "hyperthyroid": {"test": "TSH", "condition": "low"},
}


def get_threshold(test_name: str, gender: str = None) -> dict:
    """
    Get threshold for a test, considering gender if applicable
    Returns dict with low/high thresholds or empty dict if not found
    """
    if test_name not in DEFICIENCY_THRESHOLDS:
        return {}
    
    thresholds = DEFICIENCY_THRESHOLDS[test_name]
    
    # Normalize gender
    if gender:
        gender_lower = gender.lower().strip()
        if gender_lower in ["m", "male"]:
            gender_key = "male"
        elif gender_lower in ["f", "female"]:
            gender_key = "female"
        else:
            gender_key = "default"
    else:
        gender_key = "default"
    
    # Try gender-specific, fallback to default
    if gender_key in thresholds:
        return thresholds[gender_key]
    return thresholds.get("default", {})


def check_abnormal(test_name: str, value: float, gender: str = None) -> tuple:
    """
    Check if a value is abnormal based on configured thresholds
    Returns: (is_abnormal: bool, direction: str or None)
    Direction can be "HIGH", "LOW", "CRITICAL_HIGH", "CRITICAL_LOW", or None
    """
    if value is None:
        return (False, None)
    
    threshold = get_threshold(test_name, gender)
    if not threshold:
        # No threshold defined - can't determine abnormality
        return (False, None)
    
    # Check critical levels first
    if "critical_low" in threshold and value < threshold["critical_low"]:
        return (True, "CRITICAL_LOW")
    if "critical_high" in threshold and value > threshold["critical_high"]:
        return (True, "CRITICAL_HIGH")
    
    # Check normal low/high
    if "low" in threshold and value < threshold["low"]:
        return (True, "LOW")
    if "high" in threshold and value > threshold["high"]:
        return (True, "HIGH")
    
    return (False, None)


def get_condition_filter(condition: str) -> dict:
    """Get test and condition type for a medical condition keyword"""
    condition_lower = condition.lower().strip()
    return CONDITION_MAPPINGS.get(condition_lower)
