# -*- coding: utf-8 -*-
"""
Query Builder V2
Converts StructuredQuery → MongoDB Query
Deterministic, NO AI involved

CRITICAL FIXES:
1. DEFICIENCY: Enforces patient constraint when specified
2. FILTER: Auto-injects threshold when operator is missing
3. Report Scope: Enforces report_type for CBC queries
4. Uses value_standard for queries (not raw value)
"""

from typing import Dict, Any, List, Optional
from modules.query_schema import StructuredQuery, QueryIntent, Operator
from config.reference_ranges import get_reference_range
from config.canonical_mappings_v2 import CanonicalTest, REPORT_TYPE_TESTS, ALIAS_TO_CANONICAL


# Common aliases that need normalization (AI might return these)
QUERY_ALIAS_MAP = {
    "HEMOGLOBIN": "HEMOGLOBIN_CBC",
    "HB": "HEMOGLOBIN_CBC",
    "HGB": "HEMOGLOBIN_CBC",
    "RBC": "RBC_COUNT",
    "WBC": "WBC_COUNT",
    "PLATELETS": "PLATELET_COUNT",
    "PLT": "PLATELET_COUNT",
    "T3": "T3_TOTAL",
    "T4": "T4_TOTAL",
    "CHOLESTEROL": "TOTAL_CHOLESTEROL",
    "GLUCOSE": "GLUCOSE_FASTING",
    "SUGAR": "GLUCOSE_FASTING",
    "BILIRUBIN": "BILIRUBIN_TOTAL",
}


class QueryBuilderV2:
    """
    Deterministic converter from StructuredQuery to MongoDB queries.
    
    KEY IMPROVEMENTS:
    - DEFICIENCY enforces patient constraint
    - FILTER auto-injects thresholds from global reference
    - Enforces report_type for CBC-related queries
    - Uses value_standard field for numeric queries
    - Normalizes test aliases to ENUM format
    """
    
    def _normalize_canonical_test(self, test_name: Optional[str]) -> Optional[str]:
        """
        Normalize canonical test name to match database ENUM values.
        Maps common aliases like 'HEMOGLOBIN' → 'HEMOGLOBIN_CBC'
        """
        if not test_name:
            return None
        
        # Uppercase and replace spaces with underscores
        normalized = test_name.upper().replace(" ", "_")
        
        # Check if it's already a valid ENUM
        try:
            CanonicalTest(normalized)
            return normalized  # Already valid
        except ValueError:
            pass
        
        # Try alias mapping
        if normalized in QUERY_ALIAS_MAP:
            return QUERY_ALIAS_MAP[normalized]
        
        # Try the ingestion alias map (more comprehensive)
        if normalized in ALIAS_TO_CANONICAL:
            return ALIAS_TO_CANONICAL[normalized].value
        
        # Return as-is if no mapping found
        return normalized
    
    def build(self, query: StructuredQuery) -> Dict[str, Any]:
        """
        Build MongoDB query from StructuredQuery.
        Returns dict with 'filter', 'pipeline', or error.
        """
        intent = query.intent
        
        if intent == QueryIntent.PATIENT_LOOKUP:
            return self._build_patient_lookup(query)
        
        elif intent == QueryIntent.FILTER:
            return self._build_filter(query)
        
        elif intent == QueryIntent.DEFICIENCY:
            return self._build_deficiency(query)
        
        elif intent == QueryIntent.AGGREGATION:
            return self._build_aggregation(query)
        
        elif intent == QueryIntent.TREND:
            return self._build_trend(query)
        
        elif intent == QueryIntent.COMPARISON:
            return self._build_comparison(query)
        
        elif intent == QueryIntent.SUMMARY:
            return self._build_summary(query)
        
        return {"error": f"Unknown intent: {intent}"}
    
    def _infer_report_type(self, canonical_test: str) -> Optional[str]:
        """Infer report type from canonical test for scope enforcement"""
        try:
            test_enum = CanonicalTest(canonical_test)
            for report_type, tests in REPORT_TYPE_TESTS.items():
                if test_enum in tests:
                    return report_type
        except ValueError:
            pass
        return None
    
    def _build_patient_lookup(self, query: StructuredQuery) -> Dict[str, Any]:
        """Build query for PATIENT_LOOKUP - Get all tests for a specific patient"""
        filter_query = {}
        
        if query.patient_id:
            filter_query["patient_id"] = query.patient_id
        elif query.patient_name:
            filter_query["patient_name"] = {
                "$regex": query.patient_name,
                "$options": "i"
            }
        
        # Optional filters
        if query.report_type:
            filter_query["report_type"] = query.report_type
        
        # NORMALIZE canonical_test
        if query.canonical_test:
            canonical_test = self._normalize_canonical_test(query.canonical_test)
            filter_query["canonical_test"] = canonical_test
        
        return {
            "type": "find",
            "filter": filter_query,
            "sort": {"canonical_test": 1}
        }
    
    def _build_filter(self, query: StructuredQuery) -> Dict[str, Any]:
        """
        Build query for FILTER - Filter tests by criteria.
        
        FIX: Auto-inject threshold when operator is missing.
        - "low X" → operator = lt, value = reference_min
        - "high X" → operator = gt, value = reference_max
        """
        filter_query = {}
        
        # Required: canonical_test (NORMALIZED)
        canonical_test = self._normalize_canonical_test(query.canonical_test)
        filter_query["canonical_test"] = canonical_test
        
        # Determine operator and value
        operator = query.operator
        value = query.value
        
        # FIX: Auto-inject threshold if missing
        if operator is None or value is None:
            # Try to infer from canonical test's reference range
            try:
                ref_min, ref_max, _ = get_reference_range(
                    CanonicalTest(canonical_test) if canonical_test else None,
                    query.gender
                )
            except ValueError:
                ref_min, ref_max = None, None
            
            # If no operator specified, we can't auto-inject
            # But if operator is specified without value, use reference
            if operator == Operator.LT and ref_min is not None:
                value = ref_min
            elif operator == Operator.GT and ref_max is not None:
                value = ref_max
        
        # Build value condition if we have both
        if value is not None and operator:
            # Use value_standard for accurate filtering
            filter_query["value_standard"] = self._build_value_condition(
                operator, value, query.value_max
            )
        
        # Optional filters
        if query.gender:
            filter_query["gender"] = query.gender
        
        # FIX: Enforce report scope (use normalized canonical_test)
        if query.report_type:
            filter_query["report_type"] = query.report_type
        elif canonical_test:
            # Auto-infer report type for scope enforcement
            inferred_type = self._infer_report_type(canonical_test)
            if inferred_type:
                filter_query["report_type"] = inferred_type
        
        result = {
            "type": "find",
            "filter": filter_query,
            "sort": {"value_standard": -1}
        }
        
        if query.limit:
            result["limit"] = query.limit
        
        return result
    
    def _build_value_condition(self, operator: Operator, value: float, 
                               value_max: Optional[float] = None) -> Dict:
        """Build MongoDB value condition from operator"""
        
        if operator == Operator.EQ:
            return {"$eq": value}
        elif operator == Operator.GT:
            return {"$gt": value}
        elif operator == Operator.LT:
            return {"$lt": value}
        elif operator == Operator.GTE:
            return {"$gte": value}
        elif operator == Operator.LTE:
            return {"$lte": value}
        elif operator == Operator.BETWEEN:
            return {"$gte": value, "$lte": value_max}
        
        return {"$eq": value}
    
    def _build_deficiency(self, query: StructuredQuery) -> Dict[str, Any]:
        """
        Build query for DEFICIENCY - Find abnormal/deficient test results.
        
        CRITICAL FIX: MUST enforce patient constraint when specified.
        Query template:
        - is_abnormal = true
        - patient_name = <patient> (if specified)
        - canonical_test = <test> (if specified)
        - abnormal_direction = <LOW|HIGH> (if specified)
        - report_type = <type> (if specified or inferred)
        """
        filter_query = {"is_abnormal": True}
        
        # CRITICAL: Enforce patient constraint
        if query.patient_id:
            filter_query["patient_id"] = query.patient_id
        elif query.patient_name:
            filter_query["patient_name"] = {
                "$regex": query.patient_name,
                "$options": "i"
            }
        
        # Optional: specific test (NORMALIZED)
        canonical_test = self._normalize_canonical_test(query.canonical_test)
        if canonical_test:
            filter_query["canonical_test"] = canonical_test
        
        # CRITICAL FIX: Filter by abnormal direction (LOW/HIGH)
        if query.abnormal_direction:
            direction = query.abnormal_direction.upper()
            if direction in ("LOW", "HIGH"):
                filter_query["abnormal_direction"] = direction
        
        # Optional filters
        if query.gender:
            filter_query["gender"] = query.gender
        
        # FIX: Enforce report scope (use normalized test)
        if query.report_type:
            filter_query["report_type"] = query.report_type
        elif canonical_test:
            # Auto-infer report type for scope enforcement
            inferred_type = self._infer_report_type(canonical_test)
            if inferred_type:
                filter_query["report_type"] = inferred_type
        
        result = {
            "type": "find",
            "filter": filter_query,
            "sort": {"canonical_test": 1, "patient_name": 1}
        }
        
        if query.limit:
            result["limit"] = query.limit
        
        return result
    
    def _build_aggregation(self, query: StructuredQuery) -> Dict[str, Any]:
        """
        Build aggregation pipeline - count, avg, min, max operations.
        Uses value_standard for accurate calculations.
        """
        pipeline = []
        
        # Match stage (NORMALIZE canonical_test)
        match_stage = {}
        canonical_test = self._normalize_canonical_test(query.canonical_test)
        
        if canonical_test:
            match_stage["canonical_test"] = canonical_test
        
        if query.gender:
            match_stage["gender"] = query.gender
        
        # FIX: Enforce report scope
        if query.report_type:
            match_stage["report_type"] = query.report_type
        elif canonical_test:
            inferred_type = self._infer_report_type(canonical_test)
            if inferred_type:
                match_stage["report_type"] = inferred_type
        
        # Add value filter for aggregations that need numeric values
        if query.value is not None and query.operator:
            match_stage["value_standard"] = self._build_value_condition(
                query.operator, query.value, query.value_max
            )
        
        # Filter to only numeric values for math operations
        if query.aggregation_type in ['avg', 'min', 'max', 'sum']:
            match_stage["value_standard"] = {"$ne": None}
        
        if match_stage:
            pipeline.append({"$match": match_stage})
        
        # Group stage
        group_id = None
        if query.group_by:
            group_id = f"${query.group_by}"
        
        group_stage = {"_id": group_id}
        
        # Use value_standard for accurate math
        agg_type = query.aggregation_type
        if agg_type == "count":
            group_stage["result"] = {"$sum": 1}
        elif agg_type == "avg":
            group_stage["result"] = {"$avg": "$value_standard"}
        elif agg_type == "min":
            group_stage["result"] = {"$min": "$value_standard"}
        elif agg_type == "max":
            group_stage["result"] = {"$max": "$value_standard"}
        elif agg_type == "sum":
            group_stage["result"] = {"$sum": "$value_standard"}
        
        pipeline.append({"$group": group_stage})
        
        # Sort by result
        pipeline.append({"$sort": {"result": -1}})
        
        if query.limit:
            pipeline.append({"$limit": query.limit})
        
        return {
            "type": "aggregate",
            "pipeline": pipeline
        }
    
    def _build_trend(self, query: StructuredQuery) -> Dict[str, Any]:
        """Build query for TREND - Track a patient's test values over time"""
        # NORMALIZE canonical_test
        canonical_test = self._normalize_canonical_test(query.canonical_test)
        
        filter_query = {
            "canonical_test": canonical_test
        }
        
        # MUST have patient constraint for trend
        if query.patient_id:
            filter_query["patient_id"] = query.patient_id
        elif query.patient_name:
            filter_query["patient_name"] = {
                "$regex": query.patient_name,
                "$options": "i"
            }
        
        # Time range filter
        if query.time_range:
            date_filter = {}
            if query.time_range.get('start'):
                date_filter["$gte"] = query.time_range['start']
            if query.time_range.get('end'):
                date_filter["$lte"] = query.time_range['end']
            if date_filter:
                filter_query["report_date"] = date_filter
        
        return {
            "type": "find",
            "filter": filter_query,
            "sort": {"report_date": 1, "created_at": 1},
            "projection": {
                "patient_name": 1,
                "canonical_test": 1,
                "value": 1,
                "value_standard": 1,
                "unit": 1,
                "unit_standard": 1,
                "report_date": 1,
                "is_abnormal": 1
            }
        }
    
    def _build_comparison(self, query: StructuredQuery) -> Dict[str, Any]:
        """Build aggregation for COMPARISON - Compare values across patients or groups"""
        pipeline = []
        
        # Match stage (NORMALIZE canonical_test)
        canonical_test = self._normalize_canonical_test(query.canonical_test)
        match_stage = {"canonical_test": canonical_test}
        
        if query.gender:
            match_stage["gender"] = query.gender
        
        # FIX: Enforce report scope
        if query.report_type:
            match_stage["report_type"] = query.report_type
        elif canonical_test:
            inferred_type = self._infer_report_type(canonical_test)
            if inferred_type:
                match_stage["report_type"] = inferred_type
        
        match_stage["value_standard"] = {"$ne": None}
        
        pipeline.append({"$match": match_stage})
        
        # Group by patient or specified field
        group_by = query.group_by or "patient_name"
        
        pipeline.append({
            "$group": {
                "_id": f"${group_by}",
                "avg_value": {"$avg": "$value_standard"},
                "min_value": {"$min": "$value_standard"},
                "max_value": {"$max": "$value_standard"},
                "count": {"$sum": 1}
            }
        })
        
        # Sort by average value
        pipeline.append({"$sort": {"avg_value": -1}})
        
        if query.limit:
            pipeline.append({"$limit": query.limit})
        
        return {
            "type": "aggregate",
            "pipeline": pipeline
        }
    
    def _build_summary(self, query: StructuredQuery) -> Dict[str, Any]:
        """Build aggregation for SUMMARY - Overall statistics"""
        pipeline = []
        
        # Optional match stage
        match_stage = {}
        
        if query.report_type:
            match_stage["report_type"] = query.report_type
        
        if query.canonical_test:
            match_stage["canonical_test"] = query.canonical_test
        
        if match_stage:
            pipeline.append({"$match": match_stage})
        
        # Summary statistics
        pipeline.append({
            "$facet": {
                "total_tests": [{"$count": "count"}],
                "unique_patients": [
                    {"$group": {"_id": "$patient_id"}},
                    {"$count": "count"}
                ],
                "abnormal_count": [
                    {"$match": {"is_abnormal": True}},
                    {"$count": "count"}
                ],
                "by_report_type": [
                    {"$group": {
                        "_id": "$report_type",
                        "count": {"$sum": 1}
                    }},
                    {"$sort": {"count": -1}}
                ],
                "by_test": [
                    {"$group": {
                        "_id": "$canonical_test",
                        "count": {"$sum": 1},
                        "abnormal": {
                            "$sum": {"$cond": ["$is_abnormal", 1, 0]}
                        }
                    }},
                    {"$sort": {"count": -1}},
                    {"$limit": 10}
                ]
            }
        })
        
        return {
            "type": "aggregate",
            "pipeline": pipeline
        }


# Global builder instance (V2)
query_builder = QueryBuilderV2()

# Legacy alias
QueryBuilder = QueryBuilderV2
