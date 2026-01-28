# -*- coding: utf-8 -*-
"""
Query Engine - NLP to MongoDB Query Conversion
Converts natural language queries to validated MongoDB queries
"""
import re
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import logging

from config.canonical_tests import (
    CANONICAL_TEST_DICTIONARY,
    CBC_TESTS,
    LIVER_TESTS,
    KIDNEY_TESTS,
    THYROID_TESTS,
    LIPID_TESTS,
    SUPPORTED_INTENTS
)

logger = logging.getLogger(__name__)


# Test name aliases for query understanding
TEST_ALIASES = {
    # Hemoglobin
    "hemoglobin": "Hemoglobin",
    "hgb": "Hemoglobin",
    "hb": "Hemoglobin",
    
    # RBC
    "rbc": "RBC Count",
    "red blood cell": "RBC Count",
    "red blood cells": "RBC Count",
    "red cells": "RBC Count",
    
    # WBC
    "wbc": "WBC Count",
    "white blood cell": "WBC Count",
    "white blood cells": "WBC Count",
    "white cells": "WBC Count",
    "leukocytes": "WBC Count",
    
    # Platelets
    "platelet": "Platelet Count",
    "platelets": "Platelet Count",
    "plt": "Platelet Count",
    "plts": "Platelet Count",
    
    # Hematocrit
    "hematocrit": "Hematocrit",
    "hct": "Hematocrit",
    "pcv": "Hematocrit",
    
    # Liver tests
    "alt": "ALT",
    "sgpt": "ALT",
    "ast": "AST",
    "sgot": "AST",
    "alp": "ALP",
    "alkaline phosphatase": "ALP",
    "bilirubin": "Bilirubin Total",
    
    # Kidney tests
    "creatinine": "Creatinine",
    "bun": "BUN",
    "urea": "BUN",
    "egfr": "eGFR",
    "gfr": "eGFR",
    
    # Thyroid
    "tsh": "TSH",
    "t3": "T3 Total",
    "t4": "T4 Total",
    "thyroid": "TSH",
    
    # Lipids
    "cholesterol": "Total Cholesterol",
    "ldl": "LDL Cholesterol",
    "hdl": "HDL Cholesterol",
    "triglycerides": "Triglycerides",
    "triglyceride": "Triglycerides",
    
    # Blood sugar
    "glucose": "Glucose Fasting",
    "sugar": "Glucose Fasting",
    "blood sugar": "Glucose Fasting",
    "fasting glucose": "Glucose Fasting",
    "hba1c": "HbA1c",
    "a1c": "HbA1c"
}

# Report type aliases
REPORT_TYPE_ALIASES = {
    "cbc": "CBC",
    "complete blood count": "CBC",
    "blood count": "CBC",
    "hemogram": "CBC",
    "liver": "Liver Function",
    "liver function": "Liver Function",
    "lft": "Liver Function",
    "kidney": "Kidney Function",
    "kidney function": "Kidney Function",
    "renal": "Kidney Function",
    "kft": "Kidney Function",
    "rft": "Kidney Function",
    "thyroid": "Thyroid",
    "thyroid profile": "Thyroid",
    "lipid": "Lipid Profile",
    "lipid profile": "Lipid Profile",
    "lipids": "Lipid Profile",
    "cholesterol profile": "Lipid Profile"
}


class QueryParser:
    """
    Parses natural language queries into structured query objects
    """
    
    def __init__(self):
        self.test_aliases = TEST_ALIASES
        self.report_aliases = REPORT_TYPE_ALIASES
        self.supported_intents = SUPPORTED_INTENTS
    
    def parse(self, natural_query: str) -> Dict:
        """
        Parse natural language query into structured format
        
        Input: "Show me all hemoglobin results below 12"
        Output: {
            "intent": "filter_by_value",
            "test_name": "Hemoglobin",
            "operator": "lt",
            "value": 12,
            "time_range": None,
            "patient_name": None
        }
        """
        query_lower = natural_query.lower().strip()
        
        parsed = {
            "original_query": natural_query,
            "intent": None,
            "test_name": None,
            "report_type": None,
            "operator": None,
            "value": None,
            "time_range": None,
            "patient_name": None,
            "limit": 100,
            "sort_order": "desc"
        }
        
        # Detect intent
        parsed["intent"] = self._detect_intent(query_lower)
        
        # Extract test name
        parsed["test_name"] = self._extract_test_name(query_lower)
        
        # Extract report type
        parsed["report_type"] = self._extract_report_type(query_lower)
        
        # Extract comparison operator and value
        parsed["operator"], parsed["value"] = self._extract_comparison(query_lower)
        
        # Extract time range
        parsed["time_range"] = self._extract_time_range(query_lower)
        
        # Extract patient name
        parsed["patient_name"] = self._extract_patient_name(natural_query)
        
        # Extract limit
        parsed["limit"] = self._extract_limit(query_lower)
        
        return parsed
    
    def _detect_intent(self, query: str) -> str:
        """Detect the intent of the query"""
        # Abnormal results
        if any(word in query for word in ["abnormal", "out of range", "outside range", "flagged", "critical"]):
            return "get_abnormal"
        
        # Trend analysis
        if any(word in query for word in ["trend", "over time", "history", "progression", "change"]):
            return "get_trend"
        
        # Comparison
        if any(word in query for word in ["compare", "comparison", "vs", "versus", "difference"]):
            return "compare"
        
        # Statistics
        if any(word in query for word in ["average", "mean", "statistics", "stats", "summary"]):
            return "get_statistics"
        
        # Count
        if any(word in query for word in ["count", "how many", "number of"]):
            return "count"
        
        # Filter by value
        if any(word in query for word in ["below", "above", "less than", "greater than", "more than", 
                                           "under", "over", "between", "equal", "="]):
            return "filter_by_value"
        
        # Latest results
        if any(word in query for word in ["latest", "recent", "last", "newest", "current"]):
            return "get_latest"
        
        # Default to list all
        return "list_all"
    
    def _extract_test_name(self, query: str) -> Optional[str]:
        """Extract canonical test name from query"""
        # Check for direct test name mentions
        for alias, canonical in self.test_aliases.items():
            # Word boundary check
            if re.search(rf'\b{re.escape(alias)}\b', query):
                return canonical
        
        # Check for full canonical names (case insensitive)
        all_canonical = set(self.test_aliases.values())
        for canonical in all_canonical:
            if canonical.lower() in query:
                return canonical
        
        return None
    
    def _extract_report_type(self, query: str) -> Optional[str]:
        """Extract report type from query"""
        for alias, report_type in self.report_aliases.items():
            if alias in query:
                return report_type
        return None
    
    def _extract_comparison(self, query: str) -> Tuple[Optional[str], Optional[float]]:
        """Extract comparison operator and value"""
        patterns = [
            # Below/under/less than
            (r'(?:below|under|less than|<)\s*(\d+\.?\d*)', 'lt'),
            # Above/over/greater than/more than
            (r'(?:above|over|greater than|more than|>)\s*(\d+\.?\d*)', 'gt'),
            # Equal to
            (r'(?:equal to|equals|=)\s*(\d+\.?\d*)', 'eq'),
            # Between X and Y
            (r'between\s*(\d+\.?\d*)\s*(?:and|to|-)\s*(\d+\.?\d*)', 'between'),
            # At least / minimum
            (r'(?:at least|minimum|min)\s*(\d+\.?\d*)', 'gte'),
            # At most / maximum
            (r'(?:at most|maximum|max)\s*(\d+\.?\d*)', 'lte'),
        ]
        
        for pattern, operator in patterns:
            match = re.search(pattern, query)
            if match:
                if operator == 'between':
                    return operator, (float(match.group(1)), float(match.group(2)))
                return operator, float(match.group(1))
        
        return None, None
    
    def _extract_time_range(self, query: str) -> Optional[Dict]:
        """Extract time range from query"""
        now = datetime.utcnow()
        
        # Last N days
        match = re.search(r'last\s*(\d+)\s*days?', query)
        if match:
            days = int(match.group(1))
            return {
                "start": now - timedelta(days=days),
                "end": now
            }
        
        # Last N weeks
        match = re.search(r'last\s*(\d+)\s*weeks?', query)
        if match:
            weeks = int(match.group(1))
            return {
                "start": now - timedelta(weeks=weeks),
                "end": now
            }
        
        # Last N months
        match = re.search(r'last\s*(\d+)\s*months?', query)
        if match:
            months = int(match.group(1))
            return {
                "start": now - timedelta(days=months * 30),
                "end": now
            }
        
        # This week
        if "this week" in query:
            start = now - timedelta(days=now.weekday())
            return {"start": start, "end": now}
        
        # This month
        if "this month" in query:
            start = now.replace(day=1)
            return {"start": start, "end": now}
        
        return None
    
    def _extract_patient_name(self, query: str) -> Optional[str]:
        """Extract patient name from query"""
        patterns = [
            r"(?:for|patient)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)",
            r"([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)'s\s+(?:results?|reports?|tests?)",
        ]
        
        for pattern in patterns:
            match = re.search(pattern, query)
            if match:
                return match.group(1).strip()
        
        return None
    
    def _extract_limit(self, query: str) -> int:
        """Extract result limit from query"""
        match = re.search(r'(?:top|first|limit)\s*(\d+)', query)
        if match:
            return min(int(match.group(1)), 1000)
        
        if "all" in query:
            return 1000
        
        return 100


class QueryValidator:
    """
    Validates parsed queries against allowed schema and operations
    """
    
    def __init__(self):
        self.allowed_tests = set(TEST_ALIASES.values())
        self.allowed_report_types = set(REPORT_TYPE_ALIASES.values())
        self.allowed_fields = {
            "patient_id", "patient_name", "canonical_test", "value",
            "unit", "reference_min", "reference_max", "is_abnormal",
            "report_type", "report_date", "created_at"
        }
    
    def validate(self, parsed_query: Dict) -> Dict:
        """
        Validate parsed query
        
        Returns: {
            "valid": True/False,
            "errors": [...],
            "warnings": [...]
        }
        """
        errors = []
        warnings = []
        
        # Check if we have something to query
        if not parsed_query.get("test_name") and not parsed_query.get("report_type"):
            if parsed_query.get("intent") not in ["list_all", "get_abnormal", "count"]:
                warnings.append("No specific test or report type identified. Query may return broad results.")
        
        # Validate test name
        test_name = parsed_query.get("test_name")
        if test_name and test_name not in self.allowed_tests:
            warnings.append(f"Test '{test_name}' may not be in our database.")
        
        # Validate report type
        report_type = parsed_query.get("report_type")
        if report_type and report_type not in self.allowed_report_types:
            errors.append(f"Unknown report type: {report_type}")
        
        # Validate comparison
        operator = parsed_query.get("operator")
        value = parsed_query.get("value")
        
        if operator and value is None:
            errors.append("Comparison operator found but no value specified.")
        
        if value is not None:
            if isinstance(value, tuple):
                if value[0] >= value[1]:
                    errors.append("Invalid range: start value must be less than end value.")
            elif isinstance(value, (int, float)) and value < 0:
                warnings.append("Negative value specified. Lab values are typically positive.")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "parsed_query": parsed_query
        }


class QueryBuilder:
    """
    Builds MongoDB queries from validated parsed queries
    """
    
    def build(self, parsed_query: Dict) -> Dict:
        """
        Build MongoDB query from parsed query
        
        Returns: {
            "filter": {...},      # MongoDB filter
            "projection": {...},  # Fields to return
            "sort": [...],        # Sort specification
            "limit": int,         # Result limit
            "aggregation": [...]  # Aggregation pipeline (if needed)
        }
        """
        mongo_filter = {}
        projection = None
        sort = [("report_date", -1)]  # Default sort by date
        aggregation = None
        
        intent = parsed_query.get("intent")
        
        # Build filter based on test name
        if parsed_query.get("test_name"):
            mongo_filter["canonical_test"] = parsed_query["test_name"]
        
        # Build filter based on report type
        if parsed_query.get("report_type"):
            mongo_filter["report_type"] = parsed_query["report_type"]
        
        # Build filter based on comparison
        operator = parsed_query.get("operator")
        value = parsed_query.get("value")
        
        if operator and value is not None:
            if operator == "lt":
                mongo_filter["value"] = {"$lt": value}
            elif operator == "lte":
                mongo_filter["value"] = {"$lte": value}
            elif operator == "gt":
                mongo_filter["value"] = {"$gt": value}
            elif operator == "gte":
                mongo_filter["value"] = {"$gte": value}
            elif operator == "eq":
                mongo_filter["value"] = value
            elif operator == "between" and isinstance(value, tuple):
                mongo_filter["value"] = {"$gte": value[0], "$lte": value[1]}
        
        # Build filter based on time range
        time_range = parsed_query.get("time_range")
        if time_range:
            mongo_filter["report_date"] = {
                "$gte": time_range["start"],
                "$lte": time_range["end"]
            }
        
        # Build filter based on patient name
        if parsed_query.get("patient_name"):
            mongo_filter["patient_name"] = {
                "$regex": parsed_query["patient_name"],
                "$options": "i"
            }
        
        # Handle specific intents
        if intent == "get_abnormal":
            mongo_filter["is_abnormal"] = True
        
        elif intent == "get_latest":
            sort = [("report_date", -1)]
            parsed_query["limit"] = min(parsed_query.get("limit", 10), 10)
        
        elif intent == "get_statistics":
            # Build aggregation pipeline
            match_stage = {"$match": mongo_filter} if mongo_filter else {"$match": {}}
            
            aggregation = [
                match_stage,
                {"$group": {
                    "_id": "$canonical_test",
                    "count": {"$sum": 1},
                    "avg_value": {"$avg": "$value"},
                    "min_value": {"$min": "$value"},
                    "max_value": {"$max": "$value"},
                    "abnormal_count": {"$sum": {"$cond": ["$is_abnormal", 1, 0]}}
                }},
                {"$sort": {"count": -1}}
            ]
        
        elif intent == "get_trend":
            # For trend, we need to sort by date and include date in results
            sort = [("report_date", 1)]  # Ascending for trends
            projection = {
                "canonical_test": 1,
                "value": 1,
                "unit": 1,
                "report_date": 1,
                "is_abnormal": 1
            }
        
        elif intent == "count":
            aggregation = [
                {"$match": mongo_filter} if mongo_filter else {"$match": {}},
                {"$count": "total"}
            ]
        
        return {
            "filter": mongo_filter,
            "projection": projection,
            "sort": sort,
            "limit": parsed_query.get("limit", 100),
            "aggregation": aggregation
        }


class QueryEngine:
    """
    Main query engine combining parser, validator, and builder
    """
    
    def __init__(self, db_manager=None):
        self.parser = QueryParser()
        self.validator = QueryValidator()
        self.builder = QueryBuilder()
        self.db = db_manager
    
    def process_query(self, natural_query: str) -> Dict:
        """
        Process natural language query end-to-end
        
        Input: Natural language query string
        Output: {
            "success": bool,
            "parsed_query": {...},
            "mongo_query": {...},
            "validation": {...},
            "results": [...],  # If DB connected
            "error": str       # If any
        }
        """
        try:
            # Step 1: Parse natural language
            parsed = self.parser.parse(natural_query)
            
            # Step 2: Validate parsed query
            validation = self.validator.validate(parsed)
            
            if not validation["valid"]:
                return {
                    "success": False,
                    "error": "Validation failed: " + "; ".join(validation["errors"]),
                    "parsed_query": parsed,
                    "validation": validation
                }
            
            # Step 3: Build MongoDB query
            mongo_query = self.builder.build(parsed)
            
            result = {
                "success": True,
                "parsed_query": parsed,
                "mongo_query": mongo_query,
                "validation": validation,
                "results": None
            }
            
            # Step 4: Execute query if DB connected
            if self.db:
                if mongo_query.get("aggregation"):
                    result["results"] = self.db.aggregate(mongo_query["aggregation"])
                else:
                    result["results"] = self.db.query(
                        mongo_query["filter"],
                        mongo_query["projection"],
                        mongo_query["sort"],
                        mongo_query["limit"]
                    )
            
            return result
            
        except Exception as e:
            logger.error(f"Query processing error: {e}")
            return {
                "success": False,
                "error": str(e)
            }


# Convenience function
def process_natural_query(query: str, db_manager=None) -> Dict:
    """Process natural language query"""
    engine = QueryEngine(db_manager)
    return engine.process_query(query)


# For standalone testing
if __name__ == "__main__":
    import json
    
    # Test queries
    test_queries = [
        "Show me all hemoglobin results below 12",
        "What are the abnormal CBC results?",
        "Get John Doe's latest liver function tests",
        "Average platelet count in the last 30 days",
        "How many patients have low RBC?",
        "Show hemoglobin trend over time",
        "All results where WBC is above 11000",
        "Thyroid test results between 0.5 and 4.5"
    ]
    
    engine = QueryEngine()
    
    for query in test_queries:
        print(f"\n{'='*60}")
        print(f"Query: {query}")
        print("="*60)
        
        result = engine.process_query(query)
        print(f"Intent: {result['parsed_query']['intent']}")
        print(f"Test: {result['parsed_query']['test_name']}")
        print(f"MongoDB Filter: {json.dumps(result['mongo_query']['filter'], default=str)}")
        print(f"Valid: {result['validation']['valid']}")
        if result['validation']['warnings']:
            print(f"Warnings: {result['validation']['warnings']}")
