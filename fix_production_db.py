#!/usr/bin/env python3
"""
Quick Production Database Fix
Add sample data directly to the production database that Render is using
"""

import asyncio
import os
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorClient
import uuid

# Hardcode the correct Atlas connection - same as local
MONGO_URI = "mongodb+srv://archithsabbani14:archith0914@cluster0.7ow8zo6.mongodb.net/medisaarthi?retryWrites=true&w=majority&appName=Cluster0"
DATABASE_NAME = "medisaarthi"
COLLECTION_NAME = "test_results"

async def fix_production_data():
    """Fix production database by ensuring sample data exists"""
    
    try:
        print("🔗 Connecting to MongoDB Atlas (Production Database)...")
        client = AsyncIOMotorClient(MONGO_URI)
        db = client[DATABASE_NAME]
        collection = db[COLLECTION_NAME]
        
        # Test connection
        await client.admin.command('ismaster')
        print(f"✅ Connected to MongoDB Atlas: {DATABASE_NAME}")
        
        # Check current data
        current_count = await collection.count_documents({})
        print(f"📊 Current test records in database: {current_count}")
        
        if current_count == 0:
            print("📝 No data found - adding sample patients...")
            
            # Create one quick patient for testing
            patient_id = str(uuid.uuid4())
            sample_test = {
                "patient_id": patient_id,
                "patient_name": "Renuka Sharma",
                "age": 28,
                "gender": "F",
                "canonical_test": "HEMOGLOBIN_CBC",
                "raw_test_name": "Hemoglobin",
                "value": 11.2,
                "value_text": "11.2",
                "unit": "g/dL",
                "value_standard": 11.2,
                "unit_standard": "g/dL",
                "reference_min": 12.0,
                "reference_max": 15.5,
                "reference_raw": "12.0-15.5",
                "used_global_reference": False,
                "is_abnormal": True,
                "abnormal_direction": "LOW",
                "report_type": "CBC",
                "report_date": datetime.now() - timedelta(days=1),
                "source_image": "renuka_cbc_report.jpg",
                "created_at": datetime.now()
            }
            
            result = await collection.insert_one(sample_test)
            print(f"✅ Inserted test record: {result.inserted_id}")
            
        else:
            print("✅ Data already exists in production database!")
        
        # Final count
        final_count = await collection.count_documents({})
        print(f"📈 Total test records in database: {final_count}")
        
        print("\n🎉 Production database ready!")
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
    finally:
        if 'client' in locals():
            client.close()

if __name__ == "__main__":
    asyncio.run(fix_production_data())