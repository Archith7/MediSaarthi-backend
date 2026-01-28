# -*- coding: utf-8 -*-
"""
Query Builder
Converts StructuredQuery → MongoDB Query
Deterministic, NO AI involved
"""

from typing import Dict, Any, List, Optional
from modules.query_schema import StructuredQuery, QueryIntent, Operator


class QueryBuilder:
    """
    Deterministic converter from StructuredQuery to MongoDB queries
    """
    
    def build(self, query: StructuredQuery) -> Dict[str, Any]:
        """
        Build MongoDB query from StructuredQuery
        Returns dict with 'filter', 'pipeline', or error
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
    
    def _build_patient_lookup(self, query: StructuredQuery) -> Dict[str, Any]:
        """
        Build query for PATIENT_LOOKUP
        Get all tests for a specific patient
        """
        filter_query = {}
        
        if query.patient_id:
            filter_query["patient_id"] = query.patient_id
        elif query.patient_name:
            # Case-insensitive regex search
            filter_query["patient_name"] = {
                "$regex": query.patient_name,
                "$options": "i"
            }
        
        # Optional filters
        if query.report_type:
            filter_query["report_type"] = query.report_type
        
        if query.canonical_test:
            filter_query["canonical_test"] = query.canonical_test
        
        return {
            "type": "find",
            "filter": filter_query,
            "sort": {"canonical_test": 1}
        }
    
    def _build_filter(self, query: StructuredQuery) -> Dict[str, Any]:
        """
        Build query for FILTER
        Filter tests by criteria (test type, value range, etc.)
        """
        filter_query = {}
        
        # Required: canonical_test
        filter_query["canonical_test"] = query.canonical_test
        
        # Value filtering
        if query.value is not None and query.operator:
            filter_query["value"] = self._build_value_condition(
                query.operator, query.value, query.value_max
            )
        
        # Optional filters
        if query.gender:
            filter_query["gender"] = query.gender
        
        if query.report_type:
            filter_query["report_type"] = query.report_type
        
        result = {
            "type": "find",
            "filter": filter_query,
            "sort": {"value": -1}
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
        Build query for DEFICIENCY
        Find abnormal/deficient test results
        """
        filter_query = {"is_abnormal": True}
        
        # Optional: specific test
        if query.canonical_test:
            filter_query["canonical_test"] = query.canonical_test
        
        # Optional: abnormal direction (HIGH/LOW)
        if query.value is not None:  # Using value field to indicate direction preference
            pass  # Could extend to filter by direction
        
        # Optional filters
        if query.gender:
            filter_query["gender"] = query.gender
        
        if query.report_type:
            filter_query["report_type"] = query.report_type
        
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
        Build aggregation pipeline
        count, avg, min, max operations
        """
        pipeline = []
        
        # Match stage
        match_stage = {}
        
        if query.canonical_test:
            match_stage["canonical_test"] = query.canonical_test
        
        if query.gender:
            match_stage["gender"] = query.gender
        
        if query.report_type:
            match_stage["report_type"] = query.report_type
        
        # Filter to only numeric values
        if query.aggregation_type in ['avg', 'min', 'max', 'sum']:
            match_stage["value"] = {"$ne": None}
        
        if match_stage:
            pipeline.append({"$match": match_stage})
        
        # Group stage
        group_id = None
        if query.group_by:
            group_id = f"${query.group_by}"
        
        group_stage = {"_id": group_id}
        
        agg_type = query.aggregation_type
        if agg_type == "count":
            group_stage["result"] = {"$sum": 1}
        elif agg_type == "avg":
            group_stage["result"] = {"$avg": "$value"}
        elif agg_type == "min":
            group_stage["result"] = {"$min": "$value"}
        elif agg_type == "max":
            group_stage["result"] = {"$max": "$value"}
        elif agg_type == "sum":
            group_stage["result"] = {"$sum": "$value"}
        
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
        """
        Build query for TREND
        Track a patient's test values over time
        """
        filter_query = {
            "canonical_test": query.canonical_test
        }
        
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
                "unit": 1,
                "report_date": 1,
                "is_abnormal": 1
            }
        }
    
    def _build_comparison(self, query: StructuredQuery) -> Dict[str, Any]:
        """
        Build aggregation for COMPARISON
        Compare values across patients or groups
        """
        pipeline = []
        
        # Match stage
        match_stage = {"canonical_test": query.canonical_test}
        
        if query.gender:
            match_stage["gender"] = query.gender
        
        match_stage["value"] = {"$ne": None}
        
        pipeline.append({"$match": match_stage})
        
        # Group by patient
        group_by = query.group_by or "patient_name"
        
        pipeline.append({
            "$group": {
                "_id": f"${group_by}",
                "avg_value": {"$avg": "$value"},
                "min_value": {"$min": "$value"},
                "max_value": {"$max": "$value"},
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
        """
        Build aggregation for SUMMARY
        Overall statistics across the database
        """
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


# Global builder instance
query_builder = QueryBuilder()
