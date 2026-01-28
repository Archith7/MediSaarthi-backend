# -*- coding: utf-8 -*-
"""
MongoDB Models and Database Layer
Stores normalized lab data in analytics-ready schema
"""
from datetime import datetime
from typing import List, Dict, Optional, Any
import logging

logger = logging.getLogger(__name__)

# Try to import Motor for async MongoDB, fallback to PyMongo for sync
try:
    from motor.motor_asyncio import AsyncIOMotorClient
    ASYNC_AVAILABLE = True
except ImportError:
    ASYNC_AVAILABLE = False

try:
    from pymongo import MongoClient, ASCENDING, DESCENDING
    from pymongo.errors import DuplicateKeyError
    PYMONGO_AVAILABLE = True
except ImportError:
    PYMONGO_AVAILABLE = False
    MongoClient = None


# Collection Schema Definition
LAB_RESULT_SCHEMA = {
    "patient_id": str,          # Unique patient identifier
    "patient_name": str,        # Patient full name
    "age": int,                 # Patient age
    "gender": str,              # Male/Female
    "canonical_test": str,      # Normalized test name
    "value": float,             # Test result value
    "value_modifier": str,      # None, "less_than", "greater_than"
    "unit": str,                # Standardized unit
    "reference_min": float,     # Reference range minimum
    "reference_max": float,     # Reference range maximum
    "is_abnormal": bool,        # True if outside reference range
    "report_type": str,         # CBC, Liver Function, etc.
    "report_date": datetime,    # Date of the report
    "source_image": str,        # Original source file
    "created_at": datetime,     # Record creation timestamp
    "raw_data": dict            # Original raw OCR data for audit
}

# Indexes for efficient querying
INDEXES = [
    ("patient_id", ASCENDING) if PYMONGO_AVAILABLE else "patient_id",
    ("canonical_test", ASCENDING) if PYMONGO_AVAILABLE else "canonical_test",
    ("report_type", ASCENDING) if PYMONGO_AVAILABLE else "report_type",
    ("report_date", DESCENDING) if PYMONGO_AVAILABLE else "report_date",
    ("is_abnormal", ASCENDING) if PYMONGO_AVAILABLE else "is_abnormal"
]


class DatabaseManager:
    """
    Synchronous MongoDB manager for lab results storage
    """
    
    def __init__(self, mongodb_uri: str, database_name: str = "lab_analytics"):
        if not PYMONGO_AVAILABLE:
            raise ImportError("pymongo is required. Install with: pip install pymongo")
        
        self.client = MongoClient(mongodb_uri)
        self.db = self.client[database_name]
        self.lab_results = self.db["lab_results"]
        self.patients = self.db["patients"]
        self.raw_ocr = self.db["raw_ocr_data"]
        
        # Create indexes
        self._create_indexes()
    
    def _create_indexes(self):
        """Create indexes for efficient querying"""
        try:
            # Lab results indexes
            self.lab_results.create_index([("patient_id", ASCENDING)])
            self.lab_results.create_index([("canonical_test", ASCENDING)])
            self.lab_results.create_index([("report_type", ASCENDING)])
            self.lab_results.create_index([("report_date", DESCENDING)])
            self.lab_results.create_index([("is_abnormal", ASCENDING)])
            self.lab_results.create_index([
                ("patient_id", ASCENDING),
                ("canonical_test", ASCENDING),
                ("report_date", DESCENDING)
            ])
            
            # Compound index for common queries
            self.lab_results.create_index([
                ("canonical_test", ASCENDING),
                ("value", ASCENDING)
            ])
            
            logger.info("Database indexes created successfully")
        except Exception as e:
            logger.error(f"Error creating indexes: {e}")
    
    def store_normalized_result(self, normalized_data: Dict) -> Dict:
        """
        Store normalized lab results in MongoDB
        
        Input: Normalized OCR output from NormalizationEngine
        Output: Storage result with inserted IDs
        """
        if not normalized_data.get("success"):
            return {
                "success": False,
                "error": "Cannot store failed normalization"
            }
        
        inserted_ids = []
        patient_id = self._get_or_create_patient(normalized_data)
        
        # Store each test as a separate document
        for test in normalized_data.get("normalized_tests", []):
            doc = {
                "patient_id": patient_id,
                "patient_name": normalized_data.get("patient_name"),
                "age": normalized_data.get("age"),
                "gender": normalized_data.get("gender"),
                "canonical_test": test.get("canonical_test"),
                "value": test.get("value"),
                "value_modifier": test.get("value_modifier"),
                "unit": test.get("unit"),
                "reference_min": test.get("reference_min"),
                "reference_max": test.get("reference_max"),
                "is_abnormal": test.get("is_abnormal"),
                "report_type": test.get("report_type"),
                "report_date": self._parse_date(normalized_data.get("report_date")),
                "source_image": normalized_data.get("source_image"),
                "created_at": datetime.utcnow(),
                "raw_data": {
                    "test_name_raw": test.get("test_name_raw")
                }
            }
            
            result = self.lab_results.insert_one(doc)
            inserted_ids.append(str(result.inserted_id))
        
        # Store raw OCR data for audit
        self.raw_ocr.insert_one({
            "patient_id": patient_id,
            "source_image": normalized_data.get("source_image"),
            "normalized_data": normalized_data,
            "created_at": datetime.utcnow()
        })
        
        return {
            "success": True,
            "patient_id": patient_id,
            "inserted_count": len(inserted_ids),
            "inserted_ids": inserted_ids
        }
    
    def _get_or_create_patient(self, normalized_data: Dict) -> str:
        """Get existing patient ID or create new patient"""
        patient_name = normalized_data.get("patient_name", "").strip().upper()
        age = normalized_data.get("age")
        gender = normalized_data.get("gender")
        
        # Try to find existing patient
        existing = self.patients.find_one({
            "name_upper": patient_name,
            "age": age,
            "gender": gender
        })
        
        if existing:
            return str(existing["_id"])
        
        # Create new patient
        result = self.patients.insert_one({
            "name": normalized_data.get("patient_name"),
            "name_upper": patient_name,
            "age": age,
            "gender": gender,
            "created_at": datetime.utcnow()
        })
        
        return str(result.inserted_id)
    
    def _parse_date(self, date_str: str) -> Optional[datetime]:
        """Parse date string to datetime"""
        if not date_str:
            return datetime.utcnow()
        
        if isinstance(date_str, datetime):
            return date_str
        
        try:
            return datetime.fromisoformat(date_str)
        except:
            return datetime.utcnow()
    
    def query(self, mongo_query: Dict, projection: Dict = None, 
              sort: List = None, limit: int = 100) -> List[Dict]:
        """
        Execute MongoDB query
        
        Input: MongoDB query dict
        Output: List of matching documents
        """
        cursor = self.lab_results.find(mongo_query, projection)
        
        if sort:
            cursor = cursor.sort(sort)
        
        if limit:
            cursor = cursor.limit(limit)
        
        results = []
        for doc in cursor:
            doc["_id"] = str(doc["_id"])
            results.append(doc)
        
        return results
    
    def aggregate(self, pipeline: List[Dict]) -> List[Dict]:
        """
        Execute MongoDB aggregation pipeline
        
        Input: Aggregation pipeline
        Output: Aggregation results
        """
        results = list(self.lab_results.aggregate(pipeline))
        for doc in results:
            if "_id" in doc and doc["_id"]:
                doc["_id"] = str(doc["_id"])
        return results
    
    def get_patient_history(self, patient_id: str, test_name: str = None) -> List[Dict]:
        """Get all results for a patient, optionally filtered by test"""
        query = {"patient_id": patient_id}
        if test_name:
            query["canonical_test"] = test_name
        
        return self.query(
            query,
            sort=[("report_date", DESCENDING)],
            limit=1000
        )
    
    def get_abnormal_results(self, patient_id: str = None) -> List[Dict]:
        """Get all abnormal results, optionally for a specific patient"""
        query = {"is_abnormal": True}
        if patient_id:
            query["patient_id"] = patient_id
        
        return self.query(
            query,
            sort=[("report_date", DESCENDING)],
            limit=500
        )
    
    def get_test_statistics(self, canonical_test: str) -> Dict:
        """Get statistics for a specific test across all patients"""
        pipeline = [
            {"$match": {"canonical_test": canonical_test}},
            {"$group": {
                "_id": "$canonical_test",
                "count": {"$sum": 1},
                "avg_value": {"$avg": "$value"},
                "min_value": {"$min": "$value"},
                "max_value": {"$max": "$value"},
                "abnormal_count": {
                    "$sum": {"$cond": ["$is_abnormal", 1, 0]}
                }
            }}
        ]
        
        results = self.aggregate(pipeline)
        return results[0] if results else {}
    
    def close(self):
        """Close database connection"""
        if self.client:
            self.client.close()


# Singleton instance for easy access
_db_manager: Optional[DatabaseManager] = None


def get_db_manager(mongodb_uri: str = None, database_name: str = "lab_analytics") -> DatabaseManager:
    """Get or create database manager singleton"""
    global _db_manager
    
    if _db_manager is None:
        if mongodb_uri is None:
            from config.settings import MONGODB_URI, MONGODB_DATABASE
            mongodb_uri = MONGODB_URI
            database_name = MONGODB_DATABASE
        
        _db_manager = DatabaseManager(mongodb_uri, database_name)
    
    return _db_manager


# For standalone testing
if __name__ == "__main__":
    # Test database connection
    try:
        db = get_db_manager("mongodb://localhost:27017/", "lab_analytics_test")
        print("Database connected successfully!")
        
        # Test storing sample data
        sample_normalized = {
            "success": True,
            "patient_name": "John Doe",
            "age": 35,
            "gender": "Male",
            "report_date": "2024-01-15",
            "report_types": ["CBC"],
            "normalized_tests": [
                {
                    "test_name_raw": "Hemoglobin",
                    "canonical_test": "Hemoglobin",
                    "value": 14.5,
                    "value_modifier": None,
                    "unit": "g/dL",
                    "reference_min": 13.0,
                    "reference_max": 17.0,
                    "is_abnormal": False,
                    "report_type": "CBC"
                }
            ],
            "source_image": "test.png"
        }
        
        result = db.store_normalized_result(sample_normalized)
        print(f"Storage result: {result}")
        
        # Test query
        results = db.query({"canonical_test": "Hemoglobin"})
        print(f"Query results: {len(results)} documents found")
        
        db.close()
        
    except Exception as e:
        print(f"Database test failed: {e}")
