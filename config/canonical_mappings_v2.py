# -*- coding: utf-8 -*-
"""
Canonical Test Mappings V2 - CORRECTED
Maps raw OCR test names to ENUM canonical identifiers
Key corrections:
1. HEMOGLOBIN_CBC vs HBA1C distinction
2. Strict enum-style naming (UPPER_SNAKE_CASE)
3. Report type awareness for disambiguation
"""

from enum import Enum
from typing import Optional, Tuple


class CanonicalTest(str, Enum):
    """
    Canonical Test Identifiers - ENUM only
    Format: CATEGORY_SPECIFIC_NAME
    """
    # ============== CBC TESTS ==============
    HEMOGLOBIN_CBC = "HEMOGLOBIN_CBC"
    RBC_COUNT = "RBC_COUNT"
    WBC_COUNT = "WBC_COUNT"
    PLATELET_COUNT = "PLATELET_COUNT"
    HEMATOCRIT = "HEMATOCRIT"
    MCV = "MCV"
    MCH = "MCH"
    MCHC = "MCHC"
    RDW = "RDW"
    MPV = "MPV"
    PDW = "PDW"
    PCT = "PCT"
    NEUTROPHILS = "NEUTROPHILS"
    LYMPHOCYTES = "LYMPHOCYTES"
    MONOCYTES = "MONOCYTES"
    EOSINOPHILS = "EOSINOPHILS"
    BASOPHILS = "BASOPHILS"
    ESR = "ESR"
    
    # ============== LIVER TESTS ==============
    ALT = "ALT"
    AST = "AST"
    ALP = "ALP"
    GGT = "GGT"
    BILIRUBIN_TOTAL = "BILIRUBIN_TOTAL"
    BILIRUBIN_DIRECT = "BILIRUBIN_DIRECT"
    BILIRUBIN_INDIRECT = "BILIRUBIN_INDIRECT"
    ALBUMIN = "ALBUMIN"
    TOTAL_PROTEIN = "TOTAL_PROTEIN"
    GLOBULIN = "GLOBULIN"
    
    # ============== KIDNEY TESTS ==============
    CREATININE = "CREATININE"
    BUN = "BUN"
    UREA = "UREA"
    EGFR = "EGFR"
    URIC_ACID = "URIC_ACID"
    SODIUM = "SODIUM"
    POTASSIUM = "POTASSIUM"
    CHLORIDE = "CHLORIDE"
    CALCIUM = "CALCIUM"
    PHOSPHORUS = "PHOSPHORUS"
    
    # ============== THYROID TESTS ==============
    TSH = "TSH"
    T3_TOTAL = "T3_TOTAL"
    T4_TOTAL = "T4_TOTAL"
    FREE_T3 = "FREE_T3"
    FREE_T4 = "FREE_T4"
    
    # ============== LIPID TESTS ==============
    TOTAL_CHOLESTEROL = "TOTAL_CHOLESTEROL"
    LDL_CHOLESTEROL = "LDL_CHOLESTEROL"
    HDL_CHOLESTEROL = "HDL_CHOLESTEROL"
    VLDL_CHOLESTEROL = "VLDL_CHOLESTEROL"
    TRIGLYCERIDES = "TRIGLYCERIDES"
    
    # ============== DIABETES TESTS ==============
    GLUCOSE_FASTING = "GLUCOSE_FASTING"
    GLUCOSE_RANDOM = "GLUCOSE_RANDOM"
    GLUCOSE_PP = "GLUCOSE_PP"
    HBA1C = "HBA1C"
    AVERAGE_BLOOD_GLUCOSE = "AVERAGE_BLOOD_GLUCOSE"
    
    # ============== MISCELLANEOUS ==============
    VITAMIN_D = "VITAMIN_D"
    VITAMIN_B12 = "VITAMIN_B12"
    IRON = "IRON"
    FERRITIN = "FERRITIN"
    TIBC = "TIBC"
    CRP = "CRP"
    
    UNKNOWN = "UNKNOWN"


# Report Type to Tests Mapping
REPORT_TYPE_TESTS = {
    "CBC": {
        CanonicalTest.HEMOGLOBIN_CBC, CanonicalTest.RBC_COUNT, CanonicalTest.WBC_COUNT,
        CanonicalTest.PLATELET_COUNT, CanonicalTest.HEMATOCRIT, CanonicalTest.MCV,
        CanonicalTest.MCH, CanonicalTest.MCHC, CanonicalTest.RDW, CanonicalTest.MPV,
        CanonicalTest.PDW, CanonicalTest.PCT, CanonicalTest.NEUTROPHILS,
        CanonicalTest.LYMPHOCYTES, CanonicalTest.MONOCYTES, CanonicalTest.EOSINOPHILS,
        CanonicalTest.BASOPHILS, CanonicalTest.ESR
    },
    "LIVER": {
        CanonicalTest.ALT, CanonicalTest.AST, CanonicalTest.ALP, CanonicalTest.GGT,
        CanonicalTest.BILIRUBIN_TOTAL, CanonicalTest.BILIRUBIN_DIRECT,
        CanonicalTest.BILIRUBIN_INDIRECT, CanonicalTest.ALBUMIN,
        CanonicalTest.TOTAL_PROTEIN, CanonicalTest.GLOBULIN
    },
    "KIDNEY": {
        CanonicalTest.CREATININE, CanonicalTest.BUN, CanonicalTest.UREA,
        CanonicalTest.EGFR, CanonicalTest.URIC_ACID, CanonicalTest.SODIUM,
        CanonicalTest.POTASSIUM, CanonicalTest.CHLORIDE, CanonicalTest.CALCIUM,
        CanonicalTest.PHOSPHORUS
    },
    "THYROID": {
        CanonicalTest.TSH, CanonicalTest.T3_TOTAL, CanonicalTest.T4_TOTAL,
        CanonicalTest.FREE_T3, CanonicalTest.FREE_T4
    },
    "LIPID": {
        CanonicalTest.TOTAL_CHOLESTEROL, CanonicalTest.LDL_CHOLESTEROL,
        CanonicalTest.HDL_CHOLESTEROL, CanonicalTest.VLDL_CHOLESTEROL,
        CanonicalTest.TRIGLYCERIDES
    },
    "DIABETES": {
        CanonicalTest.GLUCOSE_FASTING, CanonicalTest.GLUCOSE_RANDOM,
        CanonicalTest.GLUCOSE_PP, CanonicalTest.HBA1C, CanonicalTest.AVERAGE_BLOOD_GLUCOSE
    }
}


# Alias Mappings - Map OCR text to canonical enum
# Format: "ALIAS_UPPERCASE": CanonicalTest.ENUM_VALUE
ALIAS_TO_CANONICAL = {
    # ============== HEMOGLOBIN (CBC) - CRITICAL: Separate from HbA1c ==============
    "HEMOGLOBIN": CanonicalTest.HEMOGLOBIN_CBC,
    "HB": CanonicalTest.HEMOGLOBIN_CBC,
    "HGB": CanonicalTest.HEMOGLOBIN_CBC,
    "HAEMOGLOBIN": CanonicalTest.HEMOGLOBIN_CBC,
    "HB%": CanonicalTest.HEMOGLOBIN_CBC,
    "HAEMOGLOBIN HB": CanonicalTest.HEMOGLOBIN_CBC,
    "HEMOGLOBIN (HB)": CanonicalTest.HEMOGLOBIN_CBC,
    "HB (HEMOGLOBIN)": CanonicalTest.HEMOGLOBIN_CBC,
    
    # ============== HBA1C (DIABETES) - Distinct from Hemoglobin ==============
    "HBA1C": CanonicalTest.HBA1C,
    "A1C": CanonicalTest.HBA1C,
    "GLYCATED HEMOGLOBIN": CanonicalTest.HBA1C,
    "GLYCOSYLATED HEMOGLOBIN": CanonicalTest.HBA1C,
    "HEMOGLOBIN A1C": CanonicalTest.HBA1C,
    "HB A1C": CanonicalTest.HBA1C,
    "GLYCATED HAEMOGLOBIN": CanonicalTest.HBA1C,
    "GLYCOSYLATED HAEMOGLOBIN": CanonicalTest.HBA1C,
    "GLYCOHEMOGLOBIN": CanonicalTest.HBA1C,
    "HBA1C (GLYCATED HEMOGLOBIN)": CanonicalTest.HBA1C,
    
    # ============== RBC ==============
    "RBC": CanonicalTest.RBC_COUNT,
    "R.B.C": CanonicalTest.RBC_COUNT,
    "RBC COUNT": CanonicalTest.RBC_COUNT,
    "RED BLOOD CELL": CanonicalTest.RBC_COUNT,
    "RED BLOOD CELLS": CanonicalTest.RBC_COUNT,
    "ERYTHROCYTES": CanonicalTest.RBC_COUNT,
    "TOTAL RBC COUNT": CanonicalTest.RBC_COUNT,
    "RED CELL COUNT": CanonicalTest.RBC_COUNT,
    "ERYTHROCYTE COUNT": CanonicalTest.RBC_COUNT,
    "RED BLOOD CELL COUNT": CanonicalTest.RBC_COUNT,
    
    # ============== WBC ==============
    "WBC": CanonicalTest.WBC_COUNT,
    "W.B.C": CanonicalTest.WBC_COUNT,
    "WBC COUNT": CanonicalTest.WBC_COUNT,
    "TLC": CanonicalTest.WBC_COUNT,
    "TOTAL LEUCOCYTE COUNT": CanonicalTest.WBC_COUNT,
    "TOTAL LEUKOCYTE COUNT": CanonicalTest.WBC_COUNT,
    "WHITE BLOOD CELL": CanonicalTest.WBC_COUNT,
    "WHITE BLOOD CELLS": CanonicalTest.WBC_COUNT,
    "LEUKOCYTES": CanonicalTest.WBC_COUNT,
    "LEUCOCYTES": CanonicalTest.WBC_COUNT,
    "WHITE CELL COUNT": CanonicalTest.WBC_COUNT,
    "TOTAL WBC": CanonicalTest.WBC_COUNT,
    "TC": CanonicalTest.WBC_COUNT,
    "TOTAL LEUKOCYTE COUNT (TC)": CanonicalTest.WBC_COUNT,
    "WHITE BLOOD CELL COUNT": CanonicalTest.WBC_COUNT,
    
    # ============== PLATELET ==============
    "PLATELET": CanonicalTest.PLATELET_COUNT,
    "PLATELET COUNT": CanonicalTest.PLATELET_COUNT,
    "PLATELETS": CanonicalTest.PLATELET_COUNT,
    "PLT": CanonicalTest.PLATELET_COUNT,
    "PLTS": CanonicalTest.PLATELET_COUNT,
    "THROMBOCYTE": CanonicalTest.PLATELET_COUNT,
    "THROMBOCYTES": CanonicalTest.PLATELET_COUNT,
    "PLATELET COUNT PLT": CanonicalTest.PLATELET_COUNT,
    
    # ============== HEMATOCRIT ==============
    "HCT": CanonicalTest.HEMATOCRIT,
    "HEMATOCRIT": CanonicalTest.HEMATOCRIT,
    "HAEMATOCRIT": CanonicalTest.HEMATOCRIT,
    "PCV": CanonicalTest.HEMATOCRIT,
    "PACKED CELL VOLUME": CanonicalTest.HEMATOCRIT,
    "HEMATOCRIT VALUE": CanonicalTest.HEMATOCRIT,
    "HCT VALUE": CanonicalTest.HEMATOCRIT,
    "PCV HCT": CanonicalTest.HEMATOCRIT,
    "PACKED CELL VOLUME(PCV)/HAEMATOCRIT": CanonicalTest.HEMATOCRIT,
    "PACKED CELL VOLUME (PCV)": CanonicalTest.HEMATOCRIT,
    
    # ============== CBC INDICES ==============
    "MCV": CanonicalTest.MCV,
    "MEAN CORPUSCULAR VOLUME": CanonicalTest.MCV,
    "MEAN CELL VOLUME": CanonicalTest.MCV,
    "MEAN CORPUSCULAR VOLUME(MCV)": CanonicalTest.MCV,
    "MEAN CORPUSCULAR VOLUME (MCV)": CanonicalTest.MCV,
    
    "MCH": CanonicalTest.MCH,
    "MEAN CORPUSCULAR HEMOGLOBIN": CanonicalTest.MCH,
    "MEAN CORPUSCULAR HAEMOGLOBIN": CanonicalTest.MCH,
    "MEAN CELL HEMOGLOBIN": CanonicalTest.MCH,
    "MEAN CELL HAEMOGLOBIN": CanonicalTest.MCH,
    "MEAN CORPUSCULAR HAEMOGLOBIN(MCH)": CanonicalTest.MCH,
    "MEAN CORPUSCULAR HEMOGLOBIN(MCH)": CanonicalTest.MCH,
    "MCH (MEAN CORPUSCULAR HB)": CanonicalTest.MCH,
    
    "MCHC": CanonicalTest.MCHC,
    "MEAN CORPUSCULAR HB CONC": CanonicalTest.MCHC,
    "MEAN CORPUSCULAR HEMOGLOBIN CONCENTRATION": CanonicalTest.MCHC,
    "MEAN CORPUSCULAR HAEMOGLOBIN CONCENTRATION": CanonicalTest.MCHC,
    "MEAN CELL HB CONC": CanonicalTest.MCHC,
    "MEAN CELL HAEMOGLOBIN CON": CanonicalTest.MCHC,
    "MEAN CORPUSCULAR HAEMOGLOBINCONCENTRATION(MCHC)": CanonicalTest.MCHC,
    
    "RDW": CanonicalTest.RDW,
    "RDW CV": CanonicalTest.RDW,
    "RDW-CV": CanonicalTest.RDW,
    "RED CELL DISTRIBUTION WIDTH": CanonicalTest.RDW,
    "RED CELL DISTRIBUTION WIDTH CV": CanonicalTest.RDW,
    "RDW SD": CanonicalTest.RDW,
    "RDW-SD": CanonicalTest.RDW,
    
    "MPV": CanonicalTest.MPV,
    "MEAN PLATELET VOLUME": CanonicalTest.MPV,
    
    "PDW": CanonicalTest.PDW,
    "PLATELET DISTRIBUTION WIDTH": CanonicalTest.PDW,
    
    "PCT": CanonicalTest.PCT,
    "PLATELETCRIT": CanonicalTest.PCT,
    
    # ============== DIFFERENTIAL COUNT ==============
    "NEUTROPHIL": CanonicalTest.NEUTROPHILS,
    "NEUTROPHILS": CanonicalTest.NEUTROPHILS,
    "NEUT": CanonicalTest.NEUTROPHILS,
    "SEGMENTED NEUTROPHILS": CanonicalTest.NEUTROPHILS,
    "POLYMORPHS": CanonicalTest.NEUTROPHILS,
    "ABSOLUTE NEUTROPHILS": CanonicalTest.NEUTROPHILS,
    "ABSOLUTE NEUTROPHIL COUNT": CanonicalTest.NEUTROPHILS,
    
    "LYMPHOCYTE": CanonicalTest.LYMPHOCYTES,
    "LYMPHOCYTES": CanonicalTest.LYMPHOCYTES,
    "LYMPH": CanonicalTest.LYMPHOCYTES,
    "ABSOLUTE LYMPHOCYTES": CanonicalTest.LYMPHOCYTES,
    "ABSOLUTE LYMPHOCYTE COUNT": CanonicalTest.LYMPHOCYTES,
    
    "MONOCYTE": CanonicalTest.MONOCYTES,
    "MONOCYTES": CanonicalTest.MONOCYTES,
    "MONO": CanonicalTest.MONOCYTES,
    "ABSOLUTE MONOCYTES": CanonicalTest.MONOCYTES,
    "ABSOLUTE MONOCYTE COUNT": CanonicalTest.MONOCYTES,
    
    "EOSINOPHIL": CanonicalTest.EOSINOPHILS,
    "EOSINOPHILS": CanonicalTest.EOSINOPHILS,
    "EOS": CanonicalTest.EOSINOPHILS,
    "ABSOLUTE EOSINOPHILS": CanonicalTest.EOSINOPHILS,
    "ABSOLUTE EOSINOPHIL COUNT": CanonicalTest.EOSINOPHILS,
    
    "BASOPHIL": CanonicalTest.BASOPHILS,
    "BASOPHILS": CanonicalTest.BASOPHILS,
    "BASO": CanonicalTest.BASOPHILS,
    "ABSOLUTE BASOPHILS": CanonicalTest.BASOPHILS,
    "ABSOLUTE BASOPHIL COUNT": CanonicalTest.BASOPHILS,
    
    "ESR": CanonicalTest.ESR,
    "ERYTHROCYTE SEDIMENTATION RATE": CanonicalTest.ESR,
    "ESR WESTERGREN": CanonicalTest.ESR,
    "ESR WESTERGREN METHOD": CanonicalTest.ESR,
    "SEDIMENTATION RATE": CanonicalTest.ESR,
    "ESR AUTOMATED": CanonicalTest.ESR,
    
    # ============== LIVER ==============
    "ALT": CanonicalTest.ALT,
    "SGPT": CanonicalTest.ALT,
    "ALANINE AMINOTRANSFERASE": CanonicalTest.ALT,
    "ALANINE TRANSAMINASE": CanonicalTest.ALT,
    "ALT (SGPT)": CanonicalTest.ALT,
    "SGPT (ALT)": CanonicalTest.ALT,
    "ALANINE AMINOTRANSFERASE (ALT)": CanonicalTest.ALT,
    
    "AST": CanonicalTest.AST,
    "SGOT": CanonicalTest.AST,
    "ASPARTATE AMINOTRANSFERASE": CanonicalTest.AST,
    "ASPARTATE TRANSAMINASE": CanonicalTest.AST,
    "AST (SGOT)": CanonicalTest.AST,
    "SGOT (AST)": CanonicalTest.AST,
    "ASPARTATE AMINOTRANSFERASE (AST)": CanonicalTest.AST,
    
    "ALP": CanonicalTest.ALP,
    "ALKALINE PHOSPHATASE": CanonicalTest.ALP,
    "ALK PHOS": CanonicalTest.ALP,
    "ALKALINE PHOSPHATASE (ALP)": CanonicalTest.ALP,
    
    "GGT": CanonicalTest.GGT,
    "GAMMA GT": CanonicalTest.GGT,
    "GAMMA GLUTAMYL TRANSFERASE": CanonicalTest.GGT,
    
    "BILIRUBIN TOTAL": CanonicalTest.BILIRUBIN_TOTAL,
    "TOTAL BILIRUBIN": CanonicalTest.BILIRUBIN_TOTAL,
    "BILIRUBIN": CanonicalTest.BILIRUBIN_TOTAL,
    "T. BILIRUBIN": CanonicalTest.BILIRUBIN_TOTAL,
    "BILIRUBIN (TOTAL)": CanonicalTest.BILIRUBIN_TOTAL,
    
    "BILIRUBIN DIRECT": CanonicalTest.BILIRUBIN_DIRECT,
    "DIRECT BILIRUBIN": CanonicalTest.BILIRUBIN_DIRECT,
    "D. BILIRUBIN": CanonicalTest.BILIRUBIN_DIRECT,
    "CONJUGATED BILIRUBIN": CanonicalTest.BILIRUBIN_DIRECT,
    
    "BILIRUBIN INDIRECT": CanonicalTest.BILIRUBIN_INDIRECT,
    "INDIRECT BILIRUBIN": CanonicalTest.BILIRUBIN_INDIRECT,
    "UNCONJUGATED BILIRUBIN": CanonicalTest.BILIRUBIN_INDIRECT,
    
    "ALBUMIN": CanonicalTest.ALBUMIN,
    "SERUM ALBUMIN": CanonicalTest.ALBUMIN,
    "ALB": CanonicalTest.ALBUMIN,
    
    "TOTAL PROTEIN": CanonicalTest.TOTAL_PROTEIN,
    "PROTEIN TOTAL": CanonicalTest.TOTAL_PROTEIN,
    "SERUM PROTEIN": CanonicalTest.TOTAL_PROTEIN,
    
    "GLOBULIN": CanonicalTest.GLOBULIN,
    "SERUM GLOBULIN": CanonicalTest.GLOBULIN,
    
    # ============== KIDNEY ==============
    "CREATININE": CanonicalTest.CREATININE,
    "SERUM CREATININE": CanonicalTest.CREATININE,
    "CREAT": CanonicalTest.CREATININE,
    "CREATININE,SERUM": CanonicalTest.CREATININE,
    "CREATININE SERUM": CanonicalTest.CREATININE,
    
    "BUN": CanonicalTest.BUN,
    "BLOOD UREA NITROGEN": CanonicalTest.BUN,
    
    "UREA": CanonicalTest.UREA,
    "BLOOD UREA": CanonicalTest.UREA,
    "UREA,SERUM": CanonicalTest.UREA,
    "UREA SERUM": CanonicalTest.UREA,
    
    "EGFR": CanonicalTest.EGFR,
    "GFR": CanonicalTest.EGFR,
    "ESTIMATED GFR": CanonicalTest.EGFR,
    "ESTIMATED GLOMERULAR FILTRATION RATE": CanonicalTest.EGFR,
    
    "URIC ACID": CanonicalTest.URIC_ACID,
    "SERUM URIC ACID": CanonicalTest.URIC_ACID,
    
    "SODIUM": CanonicalTest.SODIUM,
    "NA": CanonicalTest.SODIUM,
    "SERUM SODIUM": CanonicalTest.SODIUM,
    "NA+": CanonicalTest.SODIUM,
    
    "POTASSIUM": CanonicalTest.POTASSIUM,
    "K": CanonicalTest.POTASSIUM,
    "SERUM POTASSIUM": CanonicalTest.POTASSIUM,
    "K+": CanonicalTest.POTASSIUM,
    
    "CHLORIDE": CanonicalTest.CHLORIDE,
    "CL": CanonicalTest.CHLORIDE,
    "SERUM CHLORIDE": CanonicalTest.CHLORIDE,
    "CL-": CanonicalTest.CHLORIDE,
    
    "CALCIUM": CanonicalTest.CALCIUM,
    "CA": CanonicalTest.CALCIUM,
    "SERUM CALCIUM": CanonicalTest.CALCIUM,
    "CA++": CanonicalTest.CALCIUM,
    
    "PHOSPHORUS": CanonicalTest.PHOSPHORUS,
    "PHOSPHATE": CanonicalTest.PHOSPHORUS,
    "SERUM PHOSPHORUS": CanonicalTest.PHOSPHORUS,
    
    # ============== THYROID ==============
    "TSH": CanonicalTest.TSH,
    "THYROID STIMULATING HORMONE": CanonicalTest.TSH,
    "TSH 3RD GENERATION": CanonicalTest.TSH,
    "TSH ULTRASENSITIVE": CanonicalTest.TSH,
    "TSH (3RD GENERATION)": CanonicalTest.TSH,
    
    "T3": CanonicalTest.T3_TOTAL,
    "T3 TOTAL": CanonicalTest.T3_TOTAL,
    "TOTAL T3": CanonicalTest.T3_TOTAL,
    "TRIIODOTHYRONINE": CanonicalTest.T3_TOTAL,
    "T3 (TRIIODOTHYRONINE)": CanonicalTest.T3_TOTAL,
    
    "T4": CanonicalTest.T4_TOTAL,
    "T4 TOTAL": CanonicalTest.T4_TOTAL,
    "TOTAL T4": CanonicalTest.T4_TOTAL,
    "THYROXINE": CanonicalTest.T4_TOTAL,
    "T4 (THYROXINE)": CanonicalTest.T4_TOTAL,
    
    "FREE T3": CanonicalTest.FREE_T3,
    "FT3": CanonicalTest.FREE_T3,
    "F.T3": CanonicalTest.FREE_T3,
    
    "FREE T4": CanonicalTest.FREE_T4,
    "FT4": CanonicalTest.FREE_T4,
    "F.T4": CanonicalTest.FREE_T4,
    "FREE THYROXINE": CanonicalTest.FREE_T4,
    "FREE THYROXINE (FT4)": CanonicalTest.FREE_T4,
    
    # ============== LIPID ==============
    "CHOLESTEROL": CanonicalTest.TOTAL_CHOLESTEROL,
    "TOTAL CHOLESTEROL": CanonicalTest.TOTAL_CHOLESTEROL,
    "SERUM CHOLESTEROL": CanonicalTest.TOTAL_CHOLESTEROL,
    "CHOLESTEROL TOTAL": CanonicalTest.TOTAL_CHOLESTEROL,
    
    "LDL": CanonicalTest.LDL_CHOLESTEROL,
    "LDL CHOLESTEROL": CanonicalTest.LDL_CHOLESTEROL,
    "LDL-C": CanonicalTest.LDL_CHOLESTEROL,
    "LOW DENSITY LIPOPROTEIN": CanonicalTest.LDL_CHOLESTEROL,
    
    "HDL": CanonicalTest.HDL_CHOLESTEROL,
    "HDL CHOLESTEROL": CanonicalTest.HDL_CHOLESTEROL,
    "HDL-C": CanonicalTest.HDL_CHOLESTEROL,
    "HIGH DENSITY LIPOPROTEIN": CanonicalTest.HDL_CHOLESTEROL,
    
    "TRIGLYCERIDES": CanonicalTest.TRIGLYCERIDES,
    "TRIGLYCERIDE": CanonicalTest.TRIGLYCERIDES,
    "TG": CanonicalTest.TRIGLYCERIDES,
    "SERUM TRIGLYCERIDES": CanonicalTest.TRIGLYCERIDES,
    
    "VLDL": CanonicalTest.VLDL_CHOLESTEROL,
    "VLDL CHOLESTEROL": CanonicalTest.VLDL_CHOLESTEROL,
    "VLDL-C": CanonicalTest.VLDL_CHOLESTEROL,
    
    # ============== DIABETES ==============
    "GLUCOSE FASTING": CanonicalTest.GLUCOSE_FASTING,
    "FASTING GLUCOSE": CanonicalTest.GLUCOSE_FASTING,
    "FBS": CanonicalTest.GLUCOSE_FASTING,
    "FASTING BLOOD SUGAR": CanonicalTest.GLUCOSE_FASTING,
    "BLOOD SUGAR FASTING": CanonicalTest.GLUCOSE_FASTING,
    "FPG": CanonicalTest.GLUCOSE_FASTING,
    "FASTING PLASMA GLUCOSE": CanonicalTest.GLUCOSE_FASTING,
    
    "GLUCOSE RANDOM": CanonicalTest.GLUCOSE_RANDOM,
    "RANDOM GLUCOSE": CanonicalTest.GLUCOSE_RANDOM,
    "RBS": CanonicalTest.GLUCOSE_RANDOM,
    "RANDOM BLOOD SUGAR": CanonicalTest.GLUCOSE_RANDOM,
    "GLUCOSE,RANDOM": CanonicalTest.GLUCOSE_RANDOM,
    "GLUCOSE": CanonicalTest.GLUCOSE_RANDOM,  # Default for unspecified glucose
    
    "GLUCOSE PP": CanonicalTest.GLUCOSE_PP,
    "PPBS": CanonicalTest.GLUCOSE_PP,
    "POST PRANDIAL BLOOD SUGAR": CanonicalTest.GLUCOSE_PP,
    "POST PRANDIAL GLUCOSE": CanonicalTest.GLUCOSE_PP,
    "PP GLUCOSE": CanonicalTest.GLUCOSE_PP,
    
    "AVERAGE BLOOD GLUCOSE": CanonicalTest.AVERAGE_BLOOD_GLUCOSE,
    "ABG": CanonicalTest.AVERAGE_BLOOD_GLUCOSE,
    "AVERAGE BLOOD GLUCOSE (ABG)": CanonicalTest.AVERAGE_BLOOD_GLUCOSE,
    "ESTIMATED AVERAGE GLUCOSE": CanonicalTest.AVERAGE_BLOOD_GLUCOSE,
    "EAG": CanonicalTest.AVERAGE_BLOOD_GLUCOSE,
    
    # ============== MISC ==============
    "VITAMIN D": CanonicalTest.VITAMIN_D,
    "VIT D": CanonicalTest.VITAMIN_D,
    "25-HYDROXY VITAMIN D": CanonicalTest.VITAMIN_D,
    "25 OH VITAMIN D": CanonicalTest.VITAMIN_D,
    
    "VITAMIN B12": CanonicalTest.VITAMIN_B12,
    "VIT B12": CanonicalTest.VITAMIN_B12,
    "CYANOCOBALAMIN": CanonicalTest.VITAMIN_B12,
    
    "IRON": CanonicalTest.IRON,
    "SERUM IRON": CanonicalTest.IRON,
    
    "FERRITIN": CanonicalTest.FERRITIN,
    "SERUM FERRITIN": CanonicalTest.FERRITIN,
    
    "TIBC": CanonicalTest.TIBC,
    "TOTAL IRON BINDING CAPACITY": CanonicalTest.TIBC,
    
    "CRP": CanonicalTest.CRP,
    "C-REACTIVE PROTEIN": CanonicalTest.CRP,
    "HS-CRP": CanonicalTest.CRP,
    "HIGH SENSITIVITY CRP": CanonicalTest.CRP,
}


# Keywords that indicate HbA1c (for disambiguation)
HBA1C_KEYWORDS = {"HBA1C", "A1C", "GLYCATED", "GLYCOSYLATED", "GLYCOHEMOGLOBIN"}


def get_canonical_test(raw_test_name: str, report_type: Optional[str] = None) -> CanonicalTest:
    """
    Map raw test name to canonical enum.
    Uses report_type for disambiguation when needed.
    
    Args:
        raw_test_name: Original test name from OCR
        report_type: Report category (CBC, LIVER, etc.) for disambiguation
        
    Returns:
        CanonicalTest enum value
    """
    if not raw_test_name:
        return CanonicalTest.UNKNOWN
    
    # Clean and uppercase
    cleaned = raw_test_name.upper().strip()
    
    # CRITICAL: Check for HbA1c keywords FIRST (before generic hemoglobin match)
    if any(kw in cleaned for kw in HBA1C_KEYWORDS):
        return CanonicalTest.HBA1C
    
    # Direct lookup
    if cleaned in ALIAS_TO_CANONICAL:
        return ALIAS_TO_CANONICAL[cleaned]
    
    # Try cleaning variants
    variants = [
        cleaned,
        cleaned.replace(".", ""),
        cleaned.replace(",", " ").strip(),
        cleaned.replace("(", "").replace(")", ""),
        cleaned.replace("-", " ").strip(),
    ]
    
    for variant in variants:
        if variant in ALIAS_TO_CANONICAL:
            return ALIAS_TO_CANONICAL[variant]
    
    # Partial match - look for longer aliases first
    sorted_aliases = sorted(ALIAS_TO_CANONICAL.keys(), key=len, reverse=True)
    for alias in sorted_aliases:
        if len(alias) > 3 and alias in cleaned:
            return ALIAS_TO_CANONICAL[alias]
    
    return CanonicalTest.UNKNOWN


def get_report_type(canonical_test: CanonicalTest) -> str:
    """
    Get report type from canonical test.
    
    Args:
        canonical_test: The canonical test enum
        
    Returns:
        Report type string (CBC, LIVER, KIDNEY, etc.)
    """
    for report_type, tests in REPORT_TYPE_TESTS.items():
        if canonical_test in tests:
            return report_type
    return "OTHER"


def is_cbc_test(canonical_test: CanonicalTest) -> bool:
    """Check if test belongs to CBC report type"""
    return canonical_test in REPORT_TYPE_TESTS.get("CBC", set())


# Export test lists for validation
CBC_TESTS = list(REPORT_TYPE_TESTS["CBC"])
LIVER_TESTS = list(REPORT_TYPE_TESTS["LIVER"])
KIDNEY_TESTS = list(REPORT_TYPE_TESTS["KIDNEY"])
THYROID_TESTS = list(REPORT_TYPE_TESTS["THYROID"])
LIPID_TESTS = list(REPORT_TYPE_TESTS["LIPID"])
DIABETES_TESTS = list(REPORT_TYPE_TESTS["DIABETES"])

# All valid test names for validation
ALL_CANONICAL_TESTS = {t for t in CanonicalTest if t != CanonicalTest.UNKNOWN}
