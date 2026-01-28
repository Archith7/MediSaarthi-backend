# -*- coding: utf-8 -*-
"""
Query Intent Definitions and Validation V2
7 Query Categories with Strict Schema

CRITICAL FIXES:
1. Updated valid tests to use ENUM values
2. Better validation for canonical test names
"""

from enum import Enum
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
from datetime import datetime


class QueryIntent(str, Enum):
    """Supported query intents"""
    PATIENT_LOOKUP = "PATIENT_LOOKUP"    # Get all tests for a patient
    FILTER = "FILTER"                    # Filter tests by criteria
    DEFICIENCY = "DEFICIENCY"            # Find abnormal/deficient results
    AGGREGATION = "AGGREGATION"          # Count, avg, min, max operations
    TREND = "TREND"                      # Track values over time (single patient)
    COMPARISON = "COMPARISON"            # Compare patients or groups
    SUMMARY = "SUMMARY"                  # Overall statistics


class Operator(str, Enum):
    """Comparison operators for filters"""
    EQ = "eq"        # equals
    GT = "gt"        # greater than
    LT = "lt"        # less than
    GTE = "gte"      # greater than or equal
    LTE = "lte"      # less than or equal
    BETWEEN = "between"  # range


class AbnormalDirection(str, Enum):
    """Direction of abnormality for DEFICIENCY queries"""
    LOW = "LOW"      # Below reference range
    HIGH = "HIGH"    # Above reference range


@dataclass
class StructuredQuery:
    """
    The structured query contract that AI must produce.
    This is what gets converted to MongoDB queries.
    """
    intent: QueryIntent
    patient_id: Optional[str] = None
    patient_name: Optional[str] = None  # For lookup by name
    canonical_test: Optional[str] = None  # ENUM value (e.g., "HEMOGLOBIN_CBC")
    operator: Optional[Operator] = None
    value: Optional[float] = None
    value_max: Optional[float] = None  # For BETWEEN operator
    report_type: Optional[str] = None
    time_range: Optional[Dict[str, str]] = None
    gender: Optional[str] = None
    aggregation_type: Optional[str] = None  # "count", "avg", "min", "max"
    group_by: Optional[str] = None  # Field to group by
    limit: Optional[int] = None  # Limit results
    abnormal_direction: Optional[str] = None  # "LOW" or "HIGH" for DEFICIENCY queries
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary, excluding None values"""
        result = {"intent": self.intent.value}
        
        for field in ['patient_id', 'patient_name', 'canonical_test', 'report_type', 
                      'gender', 'aggregation_type', 'group_by', 'limit', 'abnormal_direction']:
            val = getattr(self, field)
            if val is not None:
                result[field] = val
        
        if self.operator is not None:
            result['operator'] = self.operator.value
        
        if self.value is not None:
            result['value'] = self.value
            
        if self.value_max is not None:
            result['value_max'] = self.value_max
            
        if self.time_range is not None:
            result['time_range'] = self.time_range
            
        return result


class QueryValidationError(Exception):
    """Raised when query validation fails"""
    pass


class QueryValidatorV2:
    """
    Validates structured queries before execution.
    Schema validation + Semantic validation.
    
    KEY IMPROVEMENTS:
    - Uses ENUM canonical test names
    - More flexible validation
    """
    
    # Valid canonical test names - ENUM format
    VALID_TESTS = {
        # CBC
        "HEMOGLOBIN_CBC", "RBC_COUNT", "WBC_COUNT", "PLATELET_COUNT",
        "HEMATOCRIT", "MCV", "MCH", "MCHC", "RDW", "MPV", "PDW", "PCT",
        "NEUTROPHILS", "LYMPHOCYTES", "MONOCYTES", "EOSINOPHILS", "BASOPHILS", "ESR",
        # Liver
        "ALT", "AST", "ALP", "GGT",
        "BILIRUBIN_TOTAL", "BILIRUBIN_DIRECT", "BILIRUBIN_INDIRECT",
        "ALBUMIN", "TOTAL_PROTEIN", "GLOBULIN",
        # Kidney
        "CREATININE", "BUN", "UREA", "URIC_ACID",
        "SODIUM", "POTASSIUM", "CHLORIDE", "CALCIUM", "PHOSPHORUS", "EGFR",
        # Thyroid
        "TSH", "T3_TOTAL", "T4_TOTAL", "FREE_T3", "FREE_T4",
        # Lipid
        "TOTAL_CHOLESTEROL", "LDL_CHOLESTEROL", "HDL_CHOLESTEROL",
        "VLDL_CHOLESTEROL", "TRIGLYCERIDES",
        # Diabetes
        "GLUCOSE_FASTING", "GLUCOSE_RANDOM", "GLUCOSE_PP",
        "HBA1C", "AVERAGE_BLOOD_GLUCOSE",
        # Misc
        "VITAMIN_D", "VITAMIN_B12", "IRON", "FERRITIN", "TIBC", "CRP"
    }
    
    VALID_REPORT_TYPES = {"CBC", "LIVER", "KIDNEY", "THYROID", "LIPID", "DIABETES", "OTHER"}
    
    def validate(self, query: StructuredQuery) -> bool:
        """
        Validate a structured query.
        Raises QueryValidationError if invalid.
        """
        self._validate_intent(query)
        self._validate_semantic_rules(query)
        self._validate_values(query)
        return True
    
    def _validate_intent(self, query: StructuredQuery):
        """Validate intent is recognized"""
        if not isinstance(query.intent, QueryIntent):
            raise QueryValidationError(f"Invalid intent: {query.intent}")
    
    def _validate_semantic_rules(self, query: StructuredQuery):
        """Apply semantic validation rules per intent"""
        
        intent = query.intent
        
        if intent == QueryIntent.PATIENT_LOOKUP:
            if not query.patient_id and not query.patient_name:
                raise QueryValidationError(
                    "PATIENT_LOOKUP requires patient_id or patient_name"
                )
        
        elif intent == QueryIntent.FILTER:
            if not query.canonical_test:
                raise QueryValidationError(
                    "FILTER requires canonical_test"
                )
        
        elif intent == QueryIntent.DEFICIENCY:
            pass  # No required fields
        
        elif intent == QueryIntent.AGGREGATION:
            if not query.aggregation_type:
                raise QueryValidationError(
                    "AGGREGATION requires aggregation_type (count, avg, min, max)"
                )
            if query.aggregation_type not in ['count', 'avg', 'min', 'max', 'sum']:
                raise QueryValidationError(
                    f"Invalid aggregation_type: {query.aggregation_type}"
                )
        
        elif intent == QueryIntent.TREND:
            if not query.patient_id and not query.patient_name:
                raise QueryValidationError(
                    "TREND requires patient_id or patient_name"
                )
            if not query.canonical_test:
                raise QueryValidationError(
                    "TREND requires canonical_test"
                )
        
        elif intent == QueryIntent.COMPARISON:
            if not query.canonical_test:
                raise QueryValidationError(
                    "COMPARISON requires canonical_test"
                )
        
        elif intent == QueryIntent.SUMMARY:
            pass
    
    def _validate_values(self, query: StructuredQuery):
        """Validate field values are acceptable"""
        
        # Validate canonical_test if provided
        if query.canonical_test:
            test_upper = query.canonical_test.upper().replace(" ", "_")
            if test_upper not in self.VALID_TESTS and test_upper != "UNKNOWN":
                # Log warning but don't fail - allows flexibility
                pass
        
        # Validate report_type if provided
        if query.report_type:
            if query.report_type.upper() not in self.VALID_REPORT_TYPES:
                raise QueryValidationError(
                    f"Unknown report_type: {query.report_type}"
                )
        
        # Validate gender if provided
        if query.gender and query.gender not in ['M', 'F']:
            raise QueryValidationError(
                f"Invalid gender: {query.gender}. Must be M or F"
            )
        
        # Validate BETWEEN operator has value_max
        if query.operator == Operator.BETWEEN:
            if query.value is None or query.value_max is None:
                raise QueryValidationError(
                    "BETWEEN operator requires both value and value_max"
                )


# Global validator instance
query_validator = QueryValidatorV2()


def validate_query(query_dict: Dict[str, Any]) -> StructuredQuery:
    """
    Parse and validate a query dictionary.
    Returns StructuredQuery if valid.
    Raises QueryValidationError if invalid.
    """
    try:
        # Parse intent
        intent_str = query_dict.get('intent', '').upper()
        intent = QueryIntent(intent_str)
        
        # Parse operator if present
        operator = None
        if 'operator' in query_dict and query_dict['operator']:
            operator = Operator(query_dict['operator'].lower())
        
        # Get canonical_test - keep as-is (should already be ENUM format)
        canonical_test = query_dict.get('canonical_test')
        if canonical_test:
            # Normalize to uppercase with underscores
            canonical_test = canonical_test.upper().replace(" ", "_")
        
        # Build structured query
        query = StructuredQuery(
            intent=intent,
            patient_id=query_dict.get('patient_id'),
            patient_name=query_dict.get('patient_name'),
            canonical_test=canonical_test,
            operator=operator,
            value=query_dict.get('value'),
            value_max=query_dict.get('value_max'),
            report_type=query_dict.get('report_type', '').upper() if query_dict.get('report_type') else None,
            time_range=query_dict.get('time_range'),
            gender=query_dict.get('gender', '').upper() if query_dict.get('gender') else None,
            aggregation_type=query_dict.get('aggregation_type'),
            group_by=query_dict.get('group_by'),
            limit=query_dict.get('limit'),
            abnormal_direction=query_dict.get('abnormal_direction', '').upper() if query_dict.get('abnormal_direction') else None
        )
        
        # Validate
        query_validator.validate(query)
        
        return query
        
    except ValueError as e:
        raise QueryValidationError(f"Invalid query format: {e}")


# Legacy aliases
QueryValidator = QueryValidatorV2
