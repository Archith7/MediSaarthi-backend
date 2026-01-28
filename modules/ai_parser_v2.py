# -*- coding: utf-8 -*-
"""
Groq AI Integration V2
Natural Language → Structured Query
Uses llama3-groq-70b-8192-tool-use-preview via Groq API

CRITICAL FIXES:
1. Safety guard for medical advice questions
2. Updated canonical test names (HEMOGLOBIN_CBC, HBA1C)
3. Better prompt for query parsing
"""

import os
import json
import httpx
from typing import Dict, Any, Optional
from pathlib import Path
from dotenv import load_dotenv

# Load .env file from project root (override=True to ensure fresh values)
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path, override=True)

# Groq API Configuration
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "llama-3.1-8b-instant"


# SAFETY GUARD: Blocked intent keywords
# These indicate medical advice questions that should NOT be answered
BLOCKED_KEYWORDS = [
    "why", "cause", "causes", "diagnosis", "diagnose", "predict",
    "prediction", "treatment", "treat", "cure", "medicine", "medication",
    "drug", "prescription", "should i", "recommend", "what to do",
    "is it dangerous", "is it serious", "what does it mean"
]

MEDICAL_ADVICE_RESPONSE = {
    "success": False,
    "blocked": True,
    "error": "This system provides data analysis only, not medical advice. Please consult a healthcare professional for medical questions."
}


# System prompt for the AI - Updated with correct canonical names
SYSTEM_PROMPT = """You are a medical lab report query parser. Your ONLY job is to convert natural language questions about lab reports into a structured JSON query format.

## AVAILABLE QUERY INTENTS:
1. PATIENT_LOOKUP - Get all tests for a specific patient
2. FILTER - Filter tests by criteria (test type, value range)
3. DEFICIENCY - Find abnormal/deficient test results
4. AGGREGATION - Count, average, min, max operations
5. TREND - Track a patient's test values over time
6. COMPARISON - Compare values across patients or groups
7. SUMMARY - Overall statistics

## CANONICAL TEST NAMES (use EXACTLY these ENUM values):
CBC Tests:
- HEMOGLOBIN_CBC (regular hemoglobin from CBC, NOT HbA1c)
- RBC_COUNT
- WBC_COUNT
- PLATELET_COUNT
- HEMATOCRIT
- MCV, MCH, MCHC, RDW
- NEUTROPHILS, LYMPHOCYTES, MONOCYTES, EOSINOPHILS, BASOPHILS
- ESR

Liver Tests:
- ALT, AST, ALP, GGT
- BILIRUBIN_TOTAL, BILIRUBIN_DIRECT
- ALBUMIN, TOTAL_PROTEIN

Kidney Tests:
- CREATININE, BUN, UREA, URIC_ACID
- SODIUM, POTASSIUM, CHLORIDE, CALCIUM
- EGFR

Thyroid Tests:
- TSH, T3_TOTAL, T4_TOTAL, FREE_T3, FREE_T4

Lipid Tests:
- TOTAL_CHOLESTEROL, LDL_CHOLESTEROL, HDL_CHOLESTEROL, TRIGLYCERIDES

Diabetes Tests:
- GLUCOSE_FASTING, GLUCOSE_RANDOM, GLUCOSE_PP
- HBA1C (glycated hemoglobin, HbA1c - DIFFERENT from HEMOGLOBIN_CBC)

Other:
- VITAMIN_D, VITAMIN_B12, IRON, FERRITIN, CRP

## CRITICAL DISAMBIGUATION:
- "hemoglobin" in CBC context → HEMOGLOBIN_CBC
- "HbA1c", "glycated hemoglobin", "A1C" → HBA1C
- "anemic", "low hemoglobin" → HEMOGLOBIN_CBC with DEFICIENCY intent
- "diabetic", "high sugar" → HBA1C or GLUCOSE_FASTING

## OPERATORS:
- eq: equals
- gt: greater than
- lt: less than
- gte: greater than or equal
- lte: less than or equal
- between: range (requires value and value_max)

## ABNORMAL DIRECTION (for DEFICIENCY queries):
- LOW: Below reference range (deficient, low, decreased, below normal)
- HIGH: Above reference range (elevated, high, increased, above normal)
Use abnormal_direction when user specifies "low" or "high" for a test.

## OUTPUT FORMAT (JSON ONLY):
{
  "intent": "INTENT_TYPE",
  "patient_id": "uuid-if-known",
  "patient_name": "name for lookup",
  "canonical_test": "TEST_ENUM_NAME",
  "operator": "gt|lt|eq|gte|lte|between",
  "value": 10.0,
  "value_max": 20.0,
  "report_type": "CBC|LIVER|KIDNEY|THYROID|LIPID|DIABETES",
  "gender": "M|F",
  "aggregation_type": "count|avg|min|max",
  "group_by": "field_name",
  "limit": 10,
  "abnormal_direction": "LOW|HIGH"
}

## RULES:
1. ONLY output valid JSON, no explanations
2. Include only relevant fields (omit null/unused fields)
3. Use EXACT canonical test ENUM names from the list above
4. For DEFICIENCY queries with a patient name, MUST include patient_name
5. For CBC-related queries, infer report_type="CBC"
6. For "low X" queries, use DEFICIENCY intent with abnormal_direction="LOW"
7. For "high X" queries, use DEFICIENCY intent with abnormal_direction="HIGH"

## EXAMPLES:

User: "Show me all tests for patient John"
{"intent": "PATIENT_LOOKUP", "patient_name": "John"}

User: "Find all anemic patients"
{"intent": "DEFICIENCY", "canonical_test": "HEMOGLOBIN_CBC", "abnormal_direction": "LOW", "report_type": "CBC"}

User: "Who has low RBC values"
{"intent": "DEFICIENCY", "canonical_test": "RBC_COUNT", "abnormal_direction": "LOW", "report_type": "CBC"}

User: "Show deficiencies for patient Niketa"
{"intent": "DEFICIENCY", "patient_name": "Niketa"}

User: "How many patients have HbA1c above 6.5?"
{"intent": "AGGREGATION", "canonical_test": "HBA1C", "operator": "gt", "value": 6.5, "aggregation_type": "count", "report_type": "DIABETES"}

User: "Show me all abnormal test results"
{"intent": "DEFICIENCY"}

User: "Find patients with low hemoglobin in CBC"
{"intent": "DEFICIENCY", "canonical_test": "HEMOGLOBIN_CBC", "abnormal_direction": "LOW", "report_type": "CBC"}

User: "Who has high WBC count"
{"intent": "DEFICIENCY", "canonical_test": "WBC_COUNT", "abnormal_direction": "HIGH", "report_type": "CBC"}

User: "Track hemoglobin trend for patient Niketa"
{"intent": "TREND", "patient_name": "Niketa", "canonical_test": "HEMOGLOBIN_CBC"}

IMPORTANT: Output ONLY the JSON object, nothing else."""


def check_safety_guard(query: str) -> bool:
    """
    Check if query contains blocked keywords indicating medical advice request.
    
    Returns:
        True if query should be blocked, False if safe to process
    """
    query_lower = query.lower()
    
    for keyword in BLOCKED_KEYWORDS:
        if keyword in query_lower:
            # Additional check: make sure it's not a data query
            data_indicators = [
                "show", "list", "find", "get", "count", "how many",
                "average", "total", "all", "patient", "results"
            ]
            
            # If it has data indicators, it might be a legitimate query
            has_data_indicator = any(ind in query_lower for ind in data_indicators)
            
            # If it's clearly asking for medical interpretation, block it
            medical_phrases = [
                "why is", "what causes", "is it dangerous", "should i",
                "what does it mean", "what to do about", "how to treat",
                "is this serious", "what medication", "what medicine"
            ]
            
            for phrase in medical_phrases:
                if phrase in query_lower:
                    return True
            
            # If no data indicator and has blocked keyword, likely medical advice
            if not has_data_indicator:
                return True
    
    return False


class GroqAIParserV2:
    """
    Parses natural language queries to structured format using Groq API.
    
    KEY IMPROVEMENTS:
    - Safety guard for medical advice questions
    - Updated canonical test names
    - Better error handling
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or GROQ_API_KEY
        print(f"🔑 Groq API Key loaded: {self.api_key[:20]}..." if self.api_key else "❌ No API key!")
        if not self.api_key:
            raise ValueError("GROQ_API_KEY not set. Set it as environment variable or pass to constructor.")
    
    async def parse_query(self, natural_language: str) -> Dict[str, Any]:
        """
        Convert natural language to structured query.
        
        Args:
            natural_language: User's question in plain English
            
        Returns:
            Dict with parsed query or error
        """
        # SAFETY GUARD: Check for medical advice questions
        if check_safety_guard(natural_language):
            return MEDICAL_ADVICE_RESPONSE
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    GROQ_API_URL,
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": GROQ_MODEL,
                        "messages": [
                            {"role": "system", "content": SYSTEM_PROMPT},
                            {"role": "user", "content": natural_language}
                        ],
                        "temperature": 0.1,
                        "max_tokens": 500
                    }
                )
                
                if response.status_code != 200:
                    return {
                        "success": False,
                        "error": f"Groq API error: {response.status_code} - {response.text}"
                    }
                
                data = response.json()
                content = data["choices"][0]["message"]["content"].strip()
                
                # Parse JSON from response
                if content.startswith("```"):
                    content = content.split("```")[1]
                    if content.startswith("json"):
                        content = content[4:]
                    content = content.strip()
                
                parsed_query = json.loads(content)
                
                # Post-process: normalize canonical test names
                if "canonical_test" in parsed_query:
                    parsed_query["canonical_test"] = self._normalize_canonical_test(
                        parsed_query["canonical_test"]
                    )
                
                return {
                    "success": True,
                    "query": parsed_query,
                    "raw_response": content
                }
                
        except json.JSONDecodeError as e:
            return {
                "success": False,
                "error": f"Failed to parse AI response as JSON: {e}",
                "raw_response": content if 'content' in dir() else None
            }
        except httpx.TimeoutException:
            return {
                "success": False,
                "error": "Request to Groq API timed out"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Error calling Groq API: {str(e)}"
            }
    
    def _normalize_canonical_test(self, test_name: str) -> str:
        """Normalize canonical test name to correct ENUM format"""
        if not test_name:
            return test_name
        
        # Map old names to new ENUM names
        name_mapping = {
            "HEMOGLOBIN": "HEMOGLOBIN_CBC",
            "Hemoglobin": "HEMOGLOBIN_CBC",
            "hemoglobin": "HEMOGLOBIN_CBC",
            "RBC Count": "RBC_COUNT",
            "WBC Count": "WBC_COUNT",
            "Platelet Count": "PLATELET_COUNT",
            "Hematocrit": "HEMATOCRIT",
            "Total Cholesterol": "TOTAL_CHOLESTEROL",
            "LDL Cholesterol": "LDL_CHOLESTEROL",
            "HDL Cholesterol": "HDL_CHOLESTEROL",
            "Triglycerides": "TRIGLYCERIDES",
            "Glucose Fasting": "GLUCOSE_FASTING",
            "Glucose Random": "GLUCOSE_RANDOM",
            "Glucose PP": "GLUCOSE_PP",
            "HbA1c": "HBA1C",
            "T3 Total": "T3_TOTAL",
            "T4 Total": "T4_TOTAL",
            "Free T3": "FREE_T3",
            "Free T4": "FREE_T4",
            "Bilirubin Total": "BILIRUBIN_TOTAL",
            "Bilirubin Direct": "BILIRUBIN_DIRECT",
            "Total Protein": "TOTAL_PROTEIN",
            "Uric Acid": "URIC_ACID",
            "Vitamin D": "VITAMIN_D",
            "Vitamin B12": "VITAMIN_B12",
        }
        
        return name_mapping.get(test_name, test_name.upper().replace(" ", "_"))


# Factory function for creating parser
def get_ai_parser(api_key: Optional[str] = None) -> GroqAIParserV2:
    """Get an instance of the AI parser"""
    return GroqAIParserV2(api_key)


# Legacy aliases
GroqAIParser = GroqAIParserV2


# For testing without API
class MockAIParserV2:
    """Mock parser for testing without API calls"""
    
    async def parse_query(self, natural_language: str) -> Dict[str, Any]:
        """Simple keyword-based parser for testing"""
        
        # Safety guard check
        if check_safety_guard(natural_language):
            return MEDICAL_ADVICE_RESPONSE
        
        nl_lower = natural_language.lower()
        
        # Simple keyword matching
        if "summary" in nl_lower or "overview" in nl_lower:
            return {"success": True, "query": {"intent": "SUMMARY"}}
        
        if "abnormal" in nl_lower or "deficien" in nl_lower:
            query = {"intent": "DEFICIENCY"}
            if "hemoglobin" in nl_lower or "anemi" in nl_lower:
                query["canonical_test"] = "HEMOGLOBIN_CBC"
                query["report_type"] = "CBC"
            
            # Check for patient name
            if "patient" in nl_lower:
                words = natural_language.split()
                for i, word in enumerate(words):
                    if word.lower() == "patient" and i + 1 < len(words):
                        query["patient_name"] = words[i + 1].rstrip("'s")
                        break
            
            return {"success": True, "query": query}
        
        if "count" in nl_lower or "how many" in nl_lower:
            query = {"intent": "AGGREGATION", "aggregation_type": "count"}
            if "hemoglobin" in nl_lower:
                query["canonical_test"] = "HEMOGLOBIN_CBC"
            elif "hba1c" in nl_lower or "a1c" in nl_lower:
                query["canonical_test"] = "HBA1C"
            return {"success": True, "query": query}
        
        if "average" in nl_lower or "avg" in nl_lower:
            query = {"intent": "AGGREGATION", "aggregation_type": "avg"}
            if "cholesterol" in nl_lower:
                query["canonical_test"] = "TOTAL_CHOLESTEROL"
            return {"success": True, "query": query}
        
        if "patient" in nl_lower:
            words = natural_language.split()
            for i, word in enumerate(words):
                if word.lower() == "patient" and i + 1 < len(words):
                    return {"success": True, "query": {
                        "intent": "PATIENT_LOOKUP",
                        "patient_name": words[i + 1]
                    }}
        
        return {"success": True, "query": {"intent": "SUMMARY"}}


MockAIParser = MockAIParserV2
