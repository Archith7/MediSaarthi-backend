# -*- coding: utf-8 -*-
"""
Canonical Test Mappings - FIXED DICTIONARY
Maps raw OCR test names to canonical standardized names
NO AI GUESSING - Pure dictionary lookup
"""

# Canonical Test Name Mappings
# Format: "CANONICAL_NAME": ["alias1", "alias2", ...]
CANONICAL_TEST_DICTIONARY = {
    # ============== CBC TESTS ==============
    "Hemoglobin": [
        "HEMOGLOBIN", "HB", "HGB", "HAEMOGLOBIN", "HB%", "HAEMOGLOBIN HB",
        "HEMOGLOBIN (HB)", "HB (HEMOGLOBIN)"
    ],
    
    "RBC Count": [
        "RBC", "R.B.C", "RBC COUNT", "RED BLOOD CELL", "RED BLOOD CELLS",
        "ERYTHROCYTES", "TOTAL RBC COUNT", "RED CELL COUNT", "ERYTHROCYTE COUNT",
        "RBC COUNT", "RED BLOOD CELL COUNT"
    ],
    
    "WBC Count": [
        "WBC", "W.B.C", "WBC COUNT", "TLC", "TOTAL LEUCOCYTE COUNT",
        "TOTAL LEUKOCYTE COUNT", "WHITE BLOOD CELL", "WHITE BLOOD CELLS",
        "LEUKOCYTES", "LEUCOCYTES", "WHITE CELL COUNT", "TOTAL WBC", "TC",
        "TOTAL LEUKOCYTE COUNT (TC)", "WHITE BLOOD CELL COUNT"
    ],
    
    "Platelet Count": [
        "PLATELET", "PLATELET COUNT", "PLATELETS", "PLT", "PLTS",
        "THROMBOCYTE", "THROMBOCYTES", "PLATELET COUNT PLT"
    ],
    
    "Hematocrit": [
        "HCT", "HEMATOCRIT", "HAEMATOCRIT", "PCV", "PACKED CELL VOLUME",
        "HEMATOCRIT VALUE", "HCT VALUE", "PCV HCT",
        "PACKED CELL VOLUME(PCV)/HAEMATOCRIT", "PACKED CELL VOLUME (PCV)"
    ],
    
    "MCV": [
        "MCV", "MEAN CORPUSCULAR VOLUME", "MEAN CELL VOLUME",
        "MEAN CORPUSCULAR VOLUME(MCV)", "MEAN CORPUSCULAR VOLUME (MCV)"
    ],
    
    "MCH": [
        "MCH", "MEAN CORPUSCULAR HEMOGLOBIN", "MEAN CORPUSCULAR HAEMOGLOBIN",
        "MEAN CELL HEMOGLOBIN", "MEAN CELL HAEMOGLOBIN",
        "MEAN CORPUSCULAR HAEMOGLOBIN(MCH)", "MEAN CORPUSCULAR HEMOGLOBIN(MCH)"
    ],
    
    "MCHC": [
        "MCHC", "MEAN CORPUSCULAR HB CONC", "MEAN CORPUSCULAR HEMOGLOBIN CONCENTRATION",
        "MEAN CORPUSCULAR HAEMOGLOBIN CONCENTRATION", "MEAN CELL HB CONC",
        "MEAN CELL HAEMOGLOBIN CON", "MEAN CORPUSCULAR HAEMOGLOBINCONCENTRATION(MCHC)"
    ],
    
    "RDW": [
        "RDW", "RDW CV", "RDW-CV", "RED CELL DISTRIBUTION WIDTH",
        "RED CELL DISTRIBUTION WIDTH CV", "RDW SD", "RDW-SD"
    ],
    
    "MPV": ["MPV", "MEAN PLATELET VOLUME"],
    
    "PDW": ["PDW", "PLATELET DISTRIBUTION WIDTH"],
    
    "PCT": ["PCT", "PLATELETCRIT"],
    
    # Differential Count
    "Neutrophils": [
        "NEUTROPHIL", "NEUTROPHILS", "NEUT", "SEGMENTED NEUTROPHILS",
        "POLYMORPHS", "ABSOLUTE NEUTROPHILS", "ABSOLUTE NEUTROPHIL COUNT"
    ],
    
    "Lymphocytes": [
        "LYMPHOCYTE", "LYMPHOCYTES", "LYMPH", "ABSOLUTE LYMPHOCYTES",
        "ABSOLUTE LYMPHOCYTE COUNT"
    ],
    
    "Monocytes": [
        "MONOCYTE", "MONOCYTES", "MONO", "ABSOLUTE MONOCYTES",
        "ABSOLUTE MONOCYTE COUNT"
    ],
    
    "Eosinophils": [
        "EOSINOPHIL", "EOSINOPHILS", "EOS", "ABSOLUTE EOSINOPHILS",
        "ABSOLUTE EOSINOPHIL COUNT"
    ],
    
    "Basophils": [
        "BASOPHIL", "BASOPHILS", "BASO", "ABSOLUTE BASOPHILS",
        "ABSOLUTE BASOPHIL COUNT"
    ],
    
    "ESR": [
        "ESR", "ERYTHROCYTE SEDIMENTATION RATE", "ESR WESTERGREN",
        "ESR WESTERGREN METHOD", "SEDIMENTATION RATE", "ESR AUTOMATED"
    ],
    
    "MCH": [
        "MCH", "MEAN CORPUSCULAR HEMOGLOBIN", "MEAN CORPUSCULAR HAEMOGLOBIN",
        "MEAN CELL HEMOGLOBIN", "MEAN CELL HAEMOGLOBIN",
        "MEAN CORPUSCULAR HAEMOGLOBIN(MCH)", "MEAN CORPUSCULAR HEMOGLOBIN(MCH)",
        "MCH (MEAN CORPUSCULAR HB)"
    ],
    
    # ============== LIVER FUNCTION ==============
    "ALT": [
        "ALT", "SGPT", "ALANINE AMINOTRANSFERASE", "ALANINE TRANSAMINASE",
        "ALT (SGPT)", "SGPT (ALT)"
    ],
    
    "AST": [
        "AST", "SGOT", "ASPARTATE AMINOTRANSFERASE", "ASPARTATE TRANSAMINASE",
        "AST (SGOT)", "SGOT (AST)"
    ],
    
    "ALP": ["ALP", "ALKALINE PHOSPHATASE", "ALK PHOS"],
    
    "GGT": ["GGT", "GAMMA GT", "GAMMA GLUTAMYL TRANSFERASE"],
    
    "Bilirubin Total": [
        "BILIRUBIN TOTAL", "TOTAL BILIRUBIN", "BILIRUBIN", "T. BILIRUBIN",
        "BILIRUBIN (TOTAL)"
    ],
    
    "Bilirubin Direct": [
        "BILIRUBIN DIRECT", "DIRECT BILIRUBIN", "D. BILIRUBIN",
        "CONJUGATED BILIRUBIN"
    ],
    
    "Bilirubin Indirect": [
        "BILIRUBIN INDIRECT", "INDIRECT BILIRUBIN", "UNCONJUGATED BILIRUBIN"
    ],
    
    "Albumin": ["ALBUMIN", "SERUM ALBUMIN", "ALB"],
    
    "Total Protein": ["TOTAL PROTEIN", "PROTEIN TOTAL", "SERUM PROTEIN"],
    
    "Globulin": ["GLOBULIN", "SERUM GLOBULIN"],
    
    # ============== KIDNEY FUNCTION ==============
    "Creatinine": [
        "CREATININE", "SERUM CREATININE", "CREAT", "CREATININE,SERUM",
        "REATININE,SERUM", "CREATININE SERUM"
    ],
    
    "BUN": ["BUN", "BLOOD UREA NITROGEN"],
    
    "Urea": ["UREA", "BLOOD UREA", "UREA,SERUM", "UREA SERUM"],
    
    "eGFR": ["EGFR", "GFR", "ESTIMATED GFR", "ESTIMATED GLOMERULAR FILTRATION RATE"],
    
    "Uric Acid": ["URIC ACID", "SERUM URIC ACID"],
    
    "Sodium": ["SODIUM", "NA", "SERUM SODIUM", "NA+"],
    
    "Potassium": ["POTASSIUM", "K", "SERUM POTASSIUM", "K+"],
    
    "Chloride": ["CHLORIDE", "CL", "SERUM CHLORIDE", "CL-"],
    
    "Calcium": ["CALCIUM", "CA", "SERUM CALCIUM", "CA++"],
    
    "Phosphorus": ["PHOSPHORUS", "PHOSPHATE", "SERUM PHOSPHORUS"],
    
    # ============== THYROID ==============
    "TSH": [
        "TSH", "THYROID STIMULATING HORMONE", "TSH 3RD GENERATION",
        "TSH ULTRASENSITIVE", "TSH (3RD GENERATION)"
    ],
    
    "T3 Total": [
        "T3", "T3 TOTAL", "TOTAL T3", "TRIIODOTHYRONINE",
        "T3 (TRIIODOTHYRONINE)"
    ],
    
    "T4 Total": [
        "T4", "T4 TOTAL", "TOTAL T4", "THYROXINE",
        "T4 (THYROXINE)"
    ],
    
    "Free T3": ["FREE T3", "FT3", "F.T3"],
    
    "Free T4": ["FREE T4", "FT4", "F.T4"],
    
    # ============== LIPID PROFILE ==============
    "Total Cholesterol": [
        "CHOLESTEROL", "TOTAL CHOLESTEROL", "SERUM CHOLESTEROL",
        "CHOLESTEROL TOTAL"
    ],
    
    "LDL Cholesterol": [
        "LDL", "LDL CHOLESTEROL", "LDL-C", "LOW DENSITY LIPOPROTEIN"
    ],
    
    "HDL Cholesterol": [
        "HDL", "HDL CHOLESTEROL", "HDL-C", "HIGH DENSITY LIPOPROTEIN"
    ],
    
    "Triglycerides": [
        "TRIGLYCERIDES", "TRIGLYCERIDE", "TG", "SERUM TRIGLYCERIDES"
    ],
    
    "VLDL Cholesterol": ["VLDL", "VLDL CHOLESTEROL", "VLDL-C"],
    
    # ============== DIABETES ==============
    "Glucose Fasting": [
        "GLUCOSE FASTING", "FASTING GLUCOSE", "FBS", "FASTING BLOOD SUGAR",
        "BLOOD SUGAR FASTING", "FPG", "FASTING PLASMA GLUCOSE"
    ],
    
    "Glucose Random": [
        "GLUCOSE RANDOM", "RANDOM GLUCOSE", "RBS", "RANDOM BLOOD SUGAR",
        "GLUCOSE,RANDOMSODIUM FLUORIDE", "GLUCOSE,RANDOM"
    ],
    
    "Glucose PP": [
        "GLUCOSE PP", "PPBS", "POST PRANDIAL BLOOD SUGAR",
        "POST PRANDIAL GLUCOSE", "PP GLUCOSE"
    ],
    
    "HbA1c": [
        "HBA1C", "A1C", "GLYCATED HEMOGLOBIN", "GLYCOSYLATED HEMOGLOBIN",
        "HEMOGLOBIN A1C", "HB A1C"
    ],
    
    "Average Blood Glucose": [
        "AVERAGE BLOOD GLUCOSE", "ABG", "AVERAGE BLOOD GLUCOSE (ABG)",
        "ESTIMATED AVERAGE GLUCOSE", "EAG"
    ],
    
    # ============== URINE ANALYSIS ==============
    "Urine Glucose": [
        "URINARY GLUCOSE", "URINE GLUCOSE", "GLUCOSE URINE", "URINE SUGAR"
    ],
    
    "Urine Protein": [
        "PROTEINS", "URINE PROTEIN", "URINARY PROTEIN", "PROTEIN URINE"
    ],
    
    "Urine Blood": [
        "URINE BLOOD", "BLOOD URINE", "URINARY BLOOD", "OCCULT BLOOD"
    ],
    
    "Urine Appearance": [
        "PHYSICAL EXAMINATION", "APPEARANCE", "URINE APPEARANCE"
    ],
    
    "Urine Turbidity": ["TURBIDITY", "URINE TURBIDITY"],
    
    "Epithelial Cells": [
        "EPITHELIAL CELLS", "EPITHELIAL", "EPITHELIAL CELL COUNT"
    ],
    
    "Glucose": ["GLUCOSE"],
    
    # ============== MISCELLANEOUS ==============
    "Mixed Cell Count": [
        "ABS.COUNT OF BA,EO,MO MIXED", "ABSOLUTE COUNT MIXED", "BA EO MO MIXED"
    ],
}

# Build reverse lookup dictionary
# Maps any alias (uppercase) to canonical name
ALIAS_TO_CANONICAL = {}
for canonical, aliases in CANONICAL_TEST_DICTIONARY.items():
    for alias in aliases:
        ALIAS_TO_CANONICAL[alias.upper()] = canonical
    # Also add the canonical name itself
    ALIAS_TO_CANONICAL[canonical.upper()] = canonical


def get_canonical_name(raw_test_name: str) -> str:
    """
    Map raw test name to canonical name
    Returns 'UNKNOWN' if not found
    """
    if not raw_test_name:
        return "UNKNOWN"
    
    # Clean the input
    cleaned = raw_test_name.upper().strip()
    
    # Direct lookup
    if cleaned in ALIAS_TO_CANONICAL:
        return ALIAS_TO_CANONICAL[cleaned]
    
    # Remove common prefixes/suffixes and try again
    cleaned_variants = [
        cleaned,
        cleaned.replace(".", ""),
        cleaned.replace(",", " ").strip(),
        cleaned.replace("(", "").replace(")", ""),
        cleaned.replace("-", " ").strip(),
    ]
    
    for variant in cleaned_variants:
        if variant in ALIAS_TO_CANONICAL:
            return ALIAS_TO_CANONICAL[variant]
    
    # Partial match - check if any alias is contained in the raw name
    for alias, canonical in ALIAS_TO_CANONICAL.items():
        if alias in cleaned and len(alias) > 3:
            return canonical
    
    return "UNKNOWN"


# CBC Tests List
CBC_TESTS = [
    "Hemoglobin", "RBC Count", "WBC Count", "Platelet Count", "Hematocrit",
    "MCV", "MCH", "MCHC", "RDW", "MPV", "PDW", "PCT",
    "Neutrophils", "Lymphocytes", "Monocytes", "Eosinophils", "Basophils", "ESR"
]

# Other Report Type Lists
LIVER_TESTS = ["ALT", "AST", "ALP", "GGT", "Bilirubin Total", "Bilirubin Direct", "Albumin", "Total Protein"]
KIDNEY_TESTS = ["Creatinine", "BUN", "Urea", "eGFR", "Uric Acid", "Sodium", "Potassium", "Chloride"]
THYROID_TESTS = ["TSH", "T3 Total", "T4 Total", "Free T3", "Free T4"]
LIPID_TESTS = ["Total Cholesterol", "LDL Cholesterol", "HDL Cholesterol", "Triglycerides"]
DIABETES_TESTS = ["Glucose Fasting", "Glucose Random", "Glucose PP", "HbA1c", "Average Blood Glucose"]


def get_report_type(canonical_test: str) -> str:
    """Determine report type based on canonical test name"""
    if canonical_test in CBC_TESTS:
        return "CBC"
    elif canonical_test in LIVER_TESTS:
        return "LIVER"
    elif canonical_test in KIDNEY_TESTS:
        return "KIDNEY"
    elif canonical_test in THYROID_TESTS:
        return "THYROID"
    elif canonical_test in LIPID_TESTS:
        return "LIPID"
    elif canonical_test in DIABETES_TESTS:
        return "DIABETES"
    else:
        return "OTHER"
