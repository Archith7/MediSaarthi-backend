# -*- coding: utf-8 -*-
"""
Groq AI Integration
Natural Language → Structured Query
Uses llama-3.3-70b-versatile via Groq API
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
GROQ_MODEL = "llama-3.3-70b-versatile"


# System prompt for the AI
SYSTEM_PROMPT = """You are a medical lab report query parser. Your ONLY job is to convert natural language questions about lab reports into a structured JSON query format.

## AVAILABLE QUERY INTENTS:
1. PATIENT_LOOKUP - Get all tests for a specific patient
2. FILTER - Filter tests by criteria (test type, value range)
3. DEFICIENCY - Find abnormal/deficient test results
4. AGGREGATION - Count, average, min, max operations
5. TREND - Track a patient's test values over time
6. COMPARISON - Compare values across patients or groups
7. SUMMARY - Overall statistics

## CANONICAL TEST NAMES (use EXACTLY these):
CBC: HEMOGLOBIN, RBC_COUNT, WBC_COUNT, PLATELET_COUNT, PCV, MCV, MCH, MCHC, RDW, NEUTROPHILS, LYMPHOCYTES, MONOCYTES, EOSINOPHILS, BASOPHILS, ESR
LIVER: BILIRUBIN_TOTAL, BILIRUBIN_DIRECT, SGOT, SGPT, ALP, GGT, ALBUMIN, TOTAL_PROTEIN
KIDNEY: UREA, CREATININE, BUN, URIC_ACID, SODIUM, POTASSIUM, CHLORIDE, CALCIUM, EGFR
THYROID: TSH, T3, T4, FT3, FT4
LIPID: TOTAL_CHOLESTEROL, HDL_CHOLESTEROL, LDL_CHOLESTEROL, TRIGLYCERIDES
DIABETES: FASTING_GLUCOSE, PP_GLUCOSE, HBA1C
OTHER: VITAMIN_D, VITAMIN_B12, IRON, FERRITIN, CRP

## OPERATORS:
- eq: equals
- gt: greater than
- lt: less than
- gte: greater than or equal
- lte: less than or equal
- between: range (requires value and value_max)

## OUTPUT FORMAT (JSON ONLY):
{
  "intent": "INTENT_TYPE",
  "patient_id": "uuid-if-known",
  "patient_name": "name for lookup",
  "canonical_test": "TEST_NAME",
  "operator": "gt|lt|eq|gte|lte|between",
  "value": 10.0,
  "value_max": 20.0,
  "report_type": "CBC|LIVER|KIDNEY|THYROID|LIPID|DIABETES",
  "gender": "M|F",
  "aggregation_type": "count|avg|min|max",
  "group_by": "field_name",
  "limit": 10
}

## RULES:
1. ONLY output valid JSON, no explanations
2. Include only relevant fields (omit null/unused fields)
3. Use EXACT canonical test names from the list above
4. Map common terms: "anemic" → HEMOGLOBIN, "diabetic" → HBA1C, "cholesterol" → TOTAL_CHOLESTEROL
5. "low hemoglobin" → DEFICIENCY intent with canonical_test=HEMOGLOBIN
6. "patients with high sugar" → FILTER intent with FASTING_GLUCOSE or HBA1C
7. For counts, use AGGREGATION with aggregation_type="count"

## EXAMPLES:

User: "Show me all tests for patient John"
{"intent": "PATIENT_LOOKUP", "patient_name": "John"}

User: "Find all anemic patients"
{"intent": "DEFICIENCY", "canonical_test": "HEMOGLOBIN"}

User: "How many patients have hemoglobin below 12?"
{"intent": "AGGREGATION", "canonical_test": "HEMOGLOBIN", "operator": "lt", "value": 12.0, "aggregation_type": "count"}

User: "What's the average cholesterol level?"
{"intent": "AGGREGATION", "canonical_test": "TOTAL_CHOLESTEROL", "aggregation_type": "avg"}

User: "Show all abnormal test results"
{"intent": "DEFICIENCY"}

User: "Compare hemoglobin levels between males and females"
{"intent": "COMPARISON", "canonical_test": "HEMOGLOBIN", "group_by": "gender"}

User: "Give me a summary of all tests"
{"intent": "SUMMARY"}

User: "Find patients with creatinine above 1.5"
{"intent": "FILTER", "canonical_test": "CREATININE", "operator": "gt", "value": 1.5}

User: "Track hemoglobin trend for patient Niketa"
{"intent": "TREND", "patient_name": "Niketa", "canonical_test": "HEMOGLOBIN"}

IMPORTANT: Output ONLY the JSON object, nothing else."""


class GroqAIParser:
    """
    Parses natural language queries to structured format using Groq API
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or GROQ_API_KEY
        print(f"🔑 Groq API Key loaded: {self.api_key[:20]}..." if self.api_key else "❌ No API key!")
        if not self.api_key:
            raise ValueError("GROQ_API_KEY not set. Set it as environment variable or pass to constructor.")
    
    async def parse_query(self, natural_language: str) -> Dict[str, Any]:
        """
        Convert natural language to structured query
        
        Args:
            natural_language: User's question in plain English
            
        Returns:
            Dict with parsed query or error
        """
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
                        "temperature": 0.1,  # Low temperature for consistent output
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
                # Handle potential markdown code blocks
                if content.startswith("```"):
                    content = content.split("```")[1]
                    if content.startswith("json"):
                        content = content[4:]
                    content = content.strip()
                
                parsed_query = json.loads(content)
                
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

    async def parse_lab_report(self, raw_text: str) -> Dict[str, Any]:
        """
        Parse raw OCR text from a lab report into structured data
        
        Args:
            raw_text: Raw OCR extracted text from lab report
            
        Returns:
            Dict with parsed patient info, tests, values
        """
        lab_report_prompt = """You are a medical lab report parser. Extract structured data from the following raw OCR text.

Extract:
1. Patient information (name, age, gender, patient_id if available)
2. Report date
3. Test results in format: test_name, value, unit, reference_range

Return JSON format:
{
    "patient_name": "name or null",
    "age": number or null,
    "gender": "Male/Female or null",
    "report_date": "date string or null",
    "tests": [
        {
            "test_name": "name",
            "value": "numeric value as string",
            "unit": "unit or null",
            "reference_range": "min-max or null"
        }
    ]
}

Only return valid JSON. Do not include markdown code blocks.

RAW OCR TEXT:
"""
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    GROQ_API_URL,
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": GROQ_MODEL,
                        "messages": [
                            {"role": "system", "content": lab_report_prompt},
                            {"role": "user", "content": raw_text[:4000]}  # Limit text length
                        ],
                        "temperature": 0.1,
                        "max_tokens": 2000
                    }
                )
                
                if response.status_code != 200:
                    return {
                        "error": f"Groq API error: {response.status_code}"
                    }
                
                data = response.json()
                content = data["choices"][0]["message"]["content"].strip()
                
                # Handle potential markdown code blocks
                if "```" in content:
                    content = content.split("```")[1]
                    if content.startswith("json"):
                        content = content[4:]
                    content = content.strip()
                
                parsed_data = json.loads(content)
                return parsed_data
                
        except json.JSONDecodeError as e:
            return {"error": f"Failed to parse AI response: {e}"}
        except Exception as e:
            return {"error": f"AI parsing error: {str(e)}"}


# Factory function for creating parser
def get_ai_parser(api_key: Optional[str] = None) -> GroqAIParser:
    """Get an instance of the AI parser"""
    return GroqAIParser(api_key)


# For testing without API
class MockAIParser:
    """Mock parser for testing without API calls"""
    
    async def parse_query(self, natural_language: str) -> Dict[str, Any]:
        """
        Simple keyword-based parser for testing
        """
        nl_lower = natural_language.lower()
        
        # Simple keyword matching
        if "summary" in nl_lower or "overview" in nl_lower:
            return {"success": True, "query": {"intent": "SUMMARY"}}
        
        if "abnormal" in nl_lower or "deficien" in nl_lower:
            query = {"intent": "DEFICIENCY"}
            if "hemoglobin" in nl_lower or "anemi" in nl_lower:
                query["canonical_test"] = "HEMOGLOBIN"
            return {"success": True, "query": query}
        
        if "count" in nl_lower or "how many" in nl_lower:
            query = {"intent": "AGGREGATION", "aggregation_type": "count"}
            if "hemoglobin" in nl_lower:
                query["canonical_test"] = "HEMOGLOBIN"
            return {"success": True, "query": query}
        
        if "average" in nl_lower or "avg" in nl_lower:
            query = {"intent": "AGGREGATION", "aggregation_type": "avg"}
            if "cholesterol" in nl_lower:
                query["canonical_test"] = "TOTAL_CHOLESTEROL"
            return {"success": True, "query": query}
        
        if "patient" in nl_lower:
            # Extract potential name (very basic)
            words = natural_language.split()
            for i, word in enumerate(words):
                if word.lower() == "patient" and i + 1 < len(words):
                    return {"success": True, "query": {
                        "intent": "PATIENT_LOOKUP",
                        "patient_name": words[i + 1]
                    }}
        
        # Default to summary
        return {"success": True, "query": {"intent": "SUMMARY"}}
