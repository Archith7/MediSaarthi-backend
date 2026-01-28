# -*- coding: utf-8 -*-
"""
MongoDB Models and Connection Manager
Schema: ONE test = ONE document
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, asdict
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
import os


# MongoDB Configuration
# Set MONGO_URI environment variable for MongoDB Atlas, or use local by default
# For Atlas: mongodb+srv://<username>:<password>@<cluster>.mongodb.net/<dbname>?retryWrites=true&w=majority
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("MONGO_DB", "lab_analytics")
COLLECTION_NAME = "test_results"


@dataclass
class TestDocument:
    """
    Single test result document - V2
    ONE test = ONE document in MongoDB
    
    CRITICAL FIELDS:
    - canonical_test: ENUM value only (e.g., "HEMOGLOBIN_CBC", not "Hemoglobin")
    - value_standard: Normalized to base units for queries
    - is_abnormal/abnormal_direction: Computed programmatically, not from OCR
    """
    patient_id: str              # UUID generated per patient
    patient_name: str            # Original name from report
    age: Optional[int]           # Age in years (None if not parseable)
    gender: Optional[str]        # M/F/None
    
    # Test identification
    canonical_test: str          # ENUM value: HEMOGLOBIN_CBC, RBC_COUNT, etc.
    raw_test_name: str           # Original test name from OCR (traceability)
    
    # Value fields - DUAL storage
    value: Optional[float]       # Raw numeric value from OCR
    value_text: Optional[str]    # Original text (e.g., "Positive", "1.5 (High)")
    unit: str                    # Raw unit from OCR
    value_standard: Optional[float]  # Normalized to base units (e.g., cells/µL)
    unit_standard: str           # Standard unit (e.g., "cells/µL", "g/dL")
    
    # Reference range - validated
    reference_min: Optional[float]  # Validated lower bound (or global fallback)
    reference_max: Optional[float]  # Validated upper bound (or global fallback)
    reference_raw: Optional[str]    # Original reference string from OCR
    used_global_reference: bool     # True if OCR reference was invalid
    
    # Abnormality - COMPUTED (not from OCR)
    is_abnormal: bool            # Computed from value vs reference
    abnormal_direction: Optional[str]  # "HIGH", "LOW", or None
    
    # Report metadata
    report_type: str             # CBC, LIVER, THYROID, etc.
    report_date: Optional[datetime]  # If available
    source_image: Optional[str]  # Original image filename
    created_at: datetime         # Ingestion timestamp
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to MongoDB-compatible dictionary"""
        d = asdict(self)
        return d


class MongoManager:
    """
    Async MongoDB Connection Manager
    """
    _instance = None
    _client: Optional[AsyncIOMotorClient] = None
    _db: Optional[AsyncIOMotorDatabase] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    @property
    def db(self) -> AsyncIOMotorDatabase:
        """Get database instance (must call connect() first)"""
        if self._db is None:
            raise RuntimeError("Database not connected. Call await connect() first.")
        return self._db
    
    async def connect(self) -> AsyncIOMotorDatabase:
        """Connect to MongoDB and return database instance"""
        if self._client is None:
            self._client = AsyncIOMotorClient(MONGO_URI)
            self._db = self._client[DATABASE_NAME]
            
            # Create indexes for efficient querying
            await self._create_indexes()
            
        return self._db
    
    async def _create_indexes(self):
        """Create necessary indexes for query performance"""
        collection = self._db[COLLECTION_NAME]
        
        # Single field indexes
        await collection.create_index("patient_id")
        await collection.create_index("canonical_test")
        await collection.create_index("value")
        await collection.create_index("report_type")
        await collection.create_index("report_date")
        await collection.create_index("is_abnormal")
        await collection.create_index("gender")
        
        # Compound indexes for common queries
        await collection.create_index([("patient_id", 1), ("canonical_test", 1)])
        await collection.create_index([("canonical_test", 1), ("value", 1)])
        await collection.create_index([("report_type", 1), ("is_abnormal", 1)])
        await collection.create_index([("canonical_test", 1), ("is_abnormal", 1)])
        
        print(f"[+] MongoDB indexes created on '{COLLECTION_NAME}'")
    
    async def get_collection(self):
        """Get the test results collection"""
        if self._db is None:
            await self.connect()
        return self._db[COLLECTION_NAME]
    
    async def insert_many(self, documents: List[TestDocument]) -> int:
        """Insert multiple test documents, return count inserted"""
        collection = await self.get_collection()
        docs = [d.to_dict() for d in documents]
        result = await collection.insert_many(docs)
        return len(result.inserted_ids)
    
    async def find(self, query: Dict[str, Any], projection: Dict[str, Any] = None) -> List[Dict]:
        """Execute a find query"""
        collection = await self.get_collection()
        cursor = collection.find(query, projection)
        return await cursor.to_list(length=None)
    
    async def aggregate(self, pipeline: List[Dict]) -> List[Dict]:
        """Execute an aggregation pipeline"""
        collection = await self.get_collection()
        cursor = collection.aggregate(pipeline)
        return await cursor.to_list(length=None)
    
    async def count(self, query: Dict[str, Any] = None) -> int:
        """Count documents matching query"""
        collection = await self.get_collection()
        if query:
            return await collection.count_documents(query)
        return await collection.estimated_document_count()
    
    async def close(self):
        """Close MongoDB connection"""
        if self._client:
            self._client.close()
            self._client = None
            self._db = None


# Singleton instance
mongo_manager = MongoManager()
