# -*- coding: utf-8 -*-
"""
Canonical Test Dictionary - Static Configuration
Maps raw OCR test names to canonical standardized names
"""

# Canonical Test Name Mappings
# Format: raw_ocr_text (lowercase) -> canonical_name
CANONICAL_TEST_DICTIONARY = {
    # Complete Blood Count (CBC) Tests
    # RBC
    "rbc": "RBC Count",
    "r.b.c": "RBC Count",
    "r b c": "RBC Count",
    "red blood cell": "RBC Count",
    "red blood cells": "RBC Count",
    "erythrocytes": "RBC Count",
    "total rbc count": "RBC Count",
    "rbc count": "RBC Count",
    "red cell count": "RBC Count",
    "erythrocyte count": "RBC Count",
    
    # WBC
    "wbc": "WBC Count",
    "w.b.c": "WBC Count",
    "w b c": "WBC Count",
    "tlc": "WBC Count",
    "total leucocyte count": "WBC Count",
    "total leukocyte count": "WBC Count",
    "white blood cell": "WBC Count",
    "white blood cells": "WBC Count",
    "leukocytes": "WBC Count",
    "leucocytes": "WBC Count",
    "wbc count": "WBC Count",
    "white cell count": "WBC Count",
    "total wbc": "WBC Count",
    "tc": "WBC Count",
    
    # Hemoglobin
    "hb": "Hemoglobin",
    "hgb": "Hemoglobin",
    "haemoglobin": "Hemoglobin",
    "hemoglobin": "Hemoglobin",
    "hb%": "Hemoglobin",
    "haemoglobin hb": "Hemoglobin",
    
    # Platelet
    "platelet": "Platelet Count",
    "platelet count": "Platelet Count",
    "platelets": "Platelet Count",
    "plt": "Platelet Count",
    "plts": "Platelet Count",
    "thrombocyte": "Platelet Count",
    "thrombocytes": "Platelet Count",
    "platelet count plt": "Platelet Count",
    
    # Hematocrit
    "hct": "Hematocrit",
    "hematocrit": "Hematocrit",
    "haematocrit": "Hematocrit",
    "pcv": "Hematocrit",
    "packed cell volume": "Hematocrit",
    "hematocrit value": "Hematocrit",
    "hct value": "Hematocrit",
    "pcv hct": "Hematocrit",
    
    # MCV
    "mcv": "MCV",
    "mean corpuscular volume": "MCV",
    "mean cell volume": "MCV",
    
    # MCH
    "mch": "MCH",
    "mean corpuscular hemoglobin": "MCH",
    "mean corpuscular haemoglobin": "MCH",
    "mean cell hemoglobin": "MCH",
    "mean cell haemoglobin": "MCH",
    
    # MCHC
    "mchc": "MCHC",
    "mean corpuscular hb conc": "MCHC",
    "mean corpuscular hemoglobin concentration": "MCHC",
    "mean corpuscular haemoglobin concentration": "MCHC",
    "mean cell hb conc": "MCHC",
    "mean cell haemoglobin con": "MCHC",
    
    # RDW
    "rdw": "RDW",
    "rdw cv": "RDW",
    "rdw-cv": "RDW",
    "red cell distribution width": "RDW",
    "red cell distribution width cv": "RDW",
    "rdw sd": "RDW",
    "rdw-sd": "RDW",
    
    # MPV
    "mpv": "MPV",
    "mean platelet volume": "MPV",
    
    # PDW
    "pdw": "PDW",
    "platelet distribution width": "PDW",
    
    # PCT
    "pct": "PCT",
    "plateletcrit": "PCT",
    "procalcitonin": "Procalcitonin",
    
    # Differential Leucocyte Count (DLC)
    "neutrophil": "Neutrophils",
    "neutrophils": "Neutrophils",
    "neut": "Neutrophils",
    "segmented neutrophils": "Neutrophils",
    "polymorphs": "Neutrophils",
    "absolute neutrophils": "Neutrophils",
    "absolute neutrophil count": "Neutrophils",
    
    "lymphocyte": "Lymphocytes",
    "lymphocytes": "Lymphocytes",
    "lymph": "Lymphocytes",
    "absolute lymphocytes": "Lymphocytes",
    "absolute lymphocyte count": "Lymphocytes",
    
    "monocyte": "Monocytes",
    "monocytes": "Monocytes",
    "mono": "Monocytes",
    "absolute monocytes": "Monocytes",
    "absolute monocyte count": "Monocytes",
    
    "eosinophil": "Eosinophils",
    "eosinophils": "Eosinophils",
    "eos": "Eosinophils",
    "absolute eosinophils": "Eosinophils",
    "absolute eosinophil count": "Eosinophils",
    
    "basophil": "Basophils",
    "basophils": "Basophils",
    "baso": "Basophils",
    "absolute basophils": "Basophils",
    "absolute basophil count": "Basophils",
    
    # ESR
    "esr": "ESR",
    "erythrocyte sedimentation rate": "ESR",
    "esr westergren": "ESR",
    "esr westergren method": "ESR",
    "sedimentation rate": "ESR",
    
    # Reticulocyte
    "reticulocyte": "Reticulocyte Count",
    "reticulocytes": "Reticulocyte Count",
    "retic": "Reticulocyte Count",
    "reticulocyte count": "Reticulocyte Count",
    "reticulocyte absolute": "Reticulocyte Count",
    
    # Liver Function Tests
    "alt": "ALT",
    "sgpt": "ALT",
    "alanine aminotransferase": "ALT",
    "alanine transaminase": "ALT",
    
    "ast": "AST",
    "sgot": "AST",
    "aspartate aminotransferase": "AST",
    "aspartate transaminase": "AST",
    
    "alp": "ALP",
    "alkaline phosphatase": "ALP",
    
    "ggt": "GGT",
    "gamma gt": "GGT",
    "gamma glutamyl transferase": "GGT",
    
    "bilirubin total": "Bilirubin Total",
    "total bilirubin": "Bilirubin Total",
    "bilirubin": "Bilirubin Total",
    "bilirubin direct": "Bilirubin Direct",
    "direct bilirubin": "Bilirubin Direct",
    "bilirubin indirect": "Bilirubin Indirect",
    "indirect bilirubin": "Bilirubin Indirect",
    
    "albumin": "Albumin",
    "serum albumin": "Albumin",
    "total protein": "Total Protein",
    "protein total": "Total Protein",
    "globulin": "Globulin",
    
    # Kidney Function Tests
    "creatinine": "Creatinine",
    "serum creatinine": "Creatinine",
    "bun": "BUN",
    "blood urea nitrogen": "BUN",
    "urea": "Urea",
    "blood urea": "Urea",
    "egfr": "eGFR",
    "gfr": "eGFR",
    "estimated gfr": "eGFR",
    "uric acid": "Uric Acid",
    "serum uric acid": "Uric Acid",
    
    "sodium": "Sodium",
    "na": "Sodium",
    "serum sodium": "Sodium",
    "potassium": "Potassium",
    "k": "Potassium",
    "serum potassium": "Potassium",
    "chloride": "Chloride",
    "cl": "Chloride",
    "serum chloride": "Chloride",
    "calcium": "Calcium",
    "ca": "Calcium",
    "serum calcium": "Calcium",
    "phosphorus": "Phosphorus",
    "phosphate": "Phosphorus",
    
    # Thyroid Tests
    "tsh": "TSH",
    "thyroid stimulating hormone": "TSH",
    "t3": "T3 Total",
    "t3 total": "T3 Total",
    "total t3": "T3 Total",
    "triiodothyronine": "T3 Total",
    "t4": "T4 Total",
    "t4 total": "T4 Total",
    "total t4": "T4 Total",
    "thyroxine": "T4 Total",
    "free t3": "Free T3",
    "ft3": "Free T3",
    "free t4": "Free T4",
    "ft4": "Free T4",
    
    # Lipid Profile
    "cholesterol": "Total Cholesterol",
    "total cholesterol": "Total Cholesterol",
    "serum cholesterol": "Total Cholesterol",
    "ldl": "LDL Cholesterol",
    "ldl cholesterol": "LDL Cholesterol",
    "ldl-c": "LDL Cholesterol",
    "hdl": "HDL Cholesterol",
    "hdl cholesterol": "HDL Cholesterol",
    "hdl-c": "HDL Cholesterol",
    "triglycerides": "Triglycerides",
    "triglyceride": "Triglycerides",
    "tg": "Triglycerides",
    "vldl": "VLDL Cholesterol",
    "vldl cholesterol": "VLDL Cholesterol",
    
    # Blood Sugar
    "glucose": "Glucose Fasting",
    "fasting glucose": "Glucose Fasting",
    "fbs": "Glucose Fasting",
    "fasting blood sugar": "Glucose Fasting",
    "blood sugar fasting": "Glucose Fasting",
    "glucose random": "Glucose Random",
    "rbs": "Glucose Random",
    "random blood sugar": "Glucose Random",
    "ppbs": "Glucose PP",
    "post prandial blood sugar": "Glucose PP",
    "glucose pp": "Glucose PP",
    "hba1c": "HbA1c",
    "a1c": "HbA1c",
    "glycated hemoglobin": "HbA1c",
    "glycosylated hemoglobin": "HbA1c",
}

# CBC Test List (for report type classification)
CBC_TESTS = [
    "RBC", "WBC", "Hemoglobin", "RBC Count", "WBC Count", "Platelet Count",
    "Hematocrit", "MCV", "MCH", "MCHC", "RDW", "MPV", "PDW", "PCT",
    "Neutrophils", "Lymphocytes", "Monocytes", "Eosinophils", "Basophils",
    "ESR", "Reticulocyte Count", "HEMOGLOBIN", "PLATELET", "NEUTROPHIL",
    "LYMPHOCYTE", "MONOCYTE", "EOSINOPHIL", "BASOPHIL", "RETICULOCYTE"
]

# Liver Function Tests
LIVER_TESTS = [
    "ALT", "AST", "ALP", "GGT", "Bilirubin Total", "Bilirubin Direct",
    "Bilirubin Indirect", "Albumin", "Total Protein", "Globulin",
    "SGPT", "SGOT", "Alkaline Phosphatase"
]

# Kidney Function Tests
KIDNEY_TESTS = [
    "Creatinine", "BUN", "eGFR", "Uric Acid", "Sodium", "Potassium",
    "Chloride", "Calcium", "Phosphorus", "Urea"
]

# Thyroid Tests
THYROID_TESTS = [
    "TSH", "T3 Total", "T4 Total", "Free T3", "Free T4", "T3", "T4"
]

# Lipid Profile Tests
LIPID_TESTS = [
    "Total Cholesterol", "LDL Cholesterol", "HDL Cholesterol", 
    "Triglycerides", "VLDL Cholesterol", "Cholesterol"
]

# Unit Mappings - simple string to string mapping
UNIT_MAPPINGS = {
    "g/dl": "g/dL",
    "gm/dl": "g/dL",
    "gms/dl": "g/dL",
    "g%": "g/dL",
    "gm%": "g/dL",
    "million/ul": "×10⁶/µL",
    "million/cmm": "×10⁶/µL",
    "10^6/ul": "×10⁶/µL",
    "10^12/l": "×10¹²/L",
    "/ul": "cells/µL",
    "/cmm": "cells/µL",
    "/cumm": "cells/µL",
    "cells/ul": "cells/µL",
    "cells/cmm": "cells/µL",
    "10^9/l": "×10⁹/L",
    "10^3/ul": "×10³/µL",
    "k/ul": "×10³/µL",
    "thousand/ul": "×10³/µL",
    "fl": "fL",
    "pg": "pg",
    "%": "%",
    "percent": "%",
    "mm/hr": "mm/hr",
    "mm/1st hr": "mm/hr",
    "mg/dl": "mg/dL",
    "mmol/l": "mmol/L",
    "umol/l": "µmol/L",
    "meq/l": "mEq/L",
    "iu/l": "IU/L",
    "u/l": "U/L",
    "ng/ml": "ng/mL",
    "pg/ml": "pg/mL",
    "miu/l": "mIU/L",
    "miu/ml": "mIU/mL",
    "uiu/ml": "µIU/mL",
}

# Reference Ranges (default values for flagging abnormal results)
DEFAULT_REFERENCE_RANGES = {
    # CBC
    "RBC Count": {"min": 4.0, "max": 5.5, "unit": "×10⁶/µL"},
    "WBC Count": {"min": 4000, "max": 11000, "unit": "cells/µL"},
    "Hemoglobin": {"min": 12.0, "max": 17.0, "unit": "g/dL"},
    "Platelet Count": {"min": 150000, "max": 450000, "unit": "cells/µL"},
    "Hematocrit": {"min": 36, "max": 50, "unit": "%"},
    "MCV": {"min": 80, "max": 100, "unit": "fL"},
    "MCH": {"min": 27, "max": 32, "unit": "pg"},
    "MCHC": {"min": 31, "max": 37, "unit": "g/dL"},
    "RDW": {"min": 11.5, "max": 14.5, "unit": "%"},
    "MPV": {"min": 7.5, "max": 11.5, "unit": "fL"},
    "Neutrophils": {"min": 40, "max": 75, "unit": "%"},
    "Lymphocytes": {"min": 20, "max": 45, "unit": "%"},
    "Monocytes": {"min": 2, "max": 10, "unit": "%"},
    "Eosinophils": {"min": 1, "max": 6, "unit": "%"},
    "Basophils": {"min": 0, "max": 2, "unit": "%"},
    "ESR": {"min": 0, "max": 20, "unit": "mm/hr"},
    
    # Liver Function
    "ALT": {"min": 7, "max": 56, "unit": "U/L"},
    "AST": {"min": 10, "max": 40, "unit": "U/L"},
    "ALP": {"min": 44, "max": 147, "unit": "U/L"},
    "GGT": {"min": 9, "max": 48, "unit": "U/L"},
    "Bilirubin Total": {"min": 0.1, "max": 1.2, "unit": "mg/dL"},
    "Bilirubin Direct": {"min": 0.0, "max": 0.3, "unit": "mg/dL"},
    "Albumin": {"min": 3.5, "max": 5.5, "unit": "g/dL"},
    "Total Protein": {"min": 6.0, "max": 8.3, "unit": "g/dL"},
    
    # Kidney Function
    "Creatinine": {"min": 0.7, "max": 1.3, "unit": "mg/dL"},
    "BUN": {"min": 7, "max": 20, "unit": "mg/dL"},
    "Urea": {"min": 15, "max": 45, "unit": "mg/dL"},
    "eGFR": {"min": 90, "max": 120, "unit": "mL/min/1.73m²"},
    "Uric Acid": {"min": 3.5, "max": 7.2, "unit": "mg/dL"},
    "Sodium": {"min": 136, "max": 145, "unit": "mEq/L"},
    "Potassium": {"min": 3.5, "max": 5.0, "unit": "mEq/L"},
    "Chloride": {"min": 98, "max": 106, "unit": "mEq/L"},
    
    # Thyroid
    "TSH": {"min": 0.4, "max": 4.0, "unit": "µIU/mL"},
    "T3 Total": {"min": 80, "max": 200, "unit": "ng/dL"},
    "T4 Total": {"min": 5.0, "max": 12.0, "unit": "µg/dL"},
    "Free T3": {"min": 2.3, "max": 4.2, "unit": "pg/mL"},
    "Free T4": {"min": 0.8, "max": 1.8, "unit": "ng/dL"},
    
    # Lipid Profile
    "Total Cholesterol": {"min": 0, "max": 200, "unit": "mg/dL"},
    "LDL Cholesterol": {"min": 0, "max": 100, "unit": "mg/dL"},
    "HDL Cholesterol": {"min": 40, "max": 60, "unit": "mg/dL"},
    "Triglycerides": {"min": 0, "max": 150, "unit": "mg/dL"},
    
    # Blood Sugar
    "Glucose Fasting": {"min": 70, "max": 100, "unit": "mg/dL"},
    "Glucose Random": {"min": 70, "max": 140, "unit": "mg/dL"},
    "HbA1c": {"min": 4.0, "max": 5.6, "unit": "%"},
}

# Query intents supported by the system
SUPPORTED_INTENTS = ["FILTER", "AGGREGATION", "TREND", "PATIENT_LOOKUP"]

# Supported operators for filtering
SUPPORTED_OPERATORS = ["lt", "gt", "eq", "lte", "gte", "ne"]

# Time ranges supported
SUPPORTED_TIME_RANGES = ["1_month", "3_months", "6_months", "1_year", "all"]

# Report types
REPORT_TYPES = ["CBC", "OTHER_LAB"]
