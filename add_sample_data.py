#!/usr/bin/env python3
"""
Add Sample Patient Data to MongoDB Atlas
Includes 5 patients with Renuka as one of them
"""

import asyncio
import os
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorClient
import uuid
from typing import List, Dict, Any

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# MongoDB configuration
MONGO_URI = os.getenv("MONGO_URI")
DATABASE_NAME = os.getenv("MONGO_DB", "medisaarthi")
COLLECTION_NAME = "test_results"


def create_sample_patients() -> List[Dict[str, Any]]:
    """Create sample patient test data"""
    
    # Base date for reports
    base_date = datetime.now() - timedelta(days=30)
    
    patients_data = []
    
    # Patient 1: Renuka (as requested)
    renuka_id = str(uuid.uuid4())
    renuka_tests = [
        {
            "patient_id": renuka_id,
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
            "report_date": base_date + timedelta(days=1),
            "source_image": "renuka_cbc_report.jpg",
            "created_at": datetime.now()
        },
        {
            "patient_id": renuka_id,
            "patient_name": "Renuka Sharma",
            "age": 28,
            "gender": "F",
            "canonical_test": "RBC_COUNT_CBC",
            "raw_test_name": "RBC Count",
            "value": 4.1,
            "value_text": "4.1",
            "unit": "million/µL",
            "value_standard": 4.1,
            "unit_standard": "million/µL",
            "reference_min": 4.2,
            "reference_max": 5.4,
            "reference_raw": "4.2-5.4",
            "used_global_reference": False,
            "is_abnormal": True,
            "abnormal_direction": "LOW",
            "report_type": "CBC",
            "report_date": base_date + timedelta(days=1),
            "source_image": "renuka_cbc_report.jpg",
            "created_at": datetime.now()
        },
        {
            "patient_id": renuka_id,
            "patient_name": "Renuka Sharma",
            "age": 28,
            "gender": "F",
            "canonical_test": "WBC_COUNT_CBC",
            "raw_test_name": "WBC Count",
            "value": 7200,
            "value_text": "7200",
            "unit": "cells/µL",
            "value_standard": 7200,
            "unit_standard": "cells/µL",
            "reference_min": 4000,
            "reference_max": 11000,
            "reference_raw": "4000-11000",
            "used_global_reference": False,
            "is_abnormal": False,
            "abnormal_direction": None,
            "report_type": "CBC",
            "report_date": base_date + timedelta(days=1),
            "source_image": "renuka_cbc_report.jpg",
            "created_at": datetime.now()
        }
    ]
    patients_data.extend(renuka_tests)
    
    # Patient 2: Rajesh Kumar
    rajesh_id = str(uuid.uuid4())
    rajesh_tests = [
        {
            "patient_id": rajesh_id,
            "patient_name": "Rajesh Kumar",
            "age": 45,
            "gender": "M",
            "canonical_test": "GLUCOSE_FASTING",
            "raw_test_name": "Fasting Glucose",
            "value": 125,
            "value_text": "125",
            "unit": "mg/dL",
            "value_standard": 125,
            "unit_standard": "mg/dL",
            "reference_min": 70,
            "reference_max": 100,
            "reference_raw": "70-100",
            "used_global_reference": False,
            "is_abnormal": True,
            "abnormal_direction": "HIGH",
            "report_type": "DIABETES",
            "report_date": base_date + timedelta(days=5),
            "source_image": "rajesh_diabetes_report.jpg",
            "created_at": datetime.now()
        },
        {
            "patient_id": rajesh_id,
            "patient_name": "Rajesh Kumar",
            "age": 45,
            "gender": "M",
            "canonical_test": "HBA1C",
            "raw_test_name": "HbA1c",
            "value": 7.2,
            "value_text": "7.2%",
            "unit": "%",
            "value_standard": 7.2,
            "unit_standard": "%",
            "reference_min": 4.0,
            "reference_max": 5.7,
            "reference_raw": "4.0-5.7",
            "used_global_reference": False,
            "is_abnormal": True,
            "abnormal_direction": "HIGH",
            "report_type": "DIABETES",
            "report_date": base_date + timedelta(days=5),
            "source_image": "rajesh_diabetes_report.jpg",
            "created_at": datetime.now()
        }
    ]
    patients_data.extend(rajesh_tests)
    
    # Patient 3: Priya Singh
    priya_id = str(uuid.uuid4())
    priya_tests = [
        {
            "patient_id": priya_id,
            "patient_name": "Priya Singh",
            "age": 35,
            "gender": "F",
            "canonical_test": "TSH",
            "raw_test_name": "TSH",
            "value": 8.5,
            "value_text": "8.5",
            "unit": "µIU/mL",
            "value_standard": 8.5,
            "unit_standard": "µIU/mL",
            "reference_min": 0.27,
            "reference_max": 4.2,
            "reference_raw": "0.27-4.2",
            "used_global_reference": False,
            "is_abnormal": True,
            "abnormal_direction": "HIGH",
            "report_type": "THYROID",
            "report_date": base_date + timedelta(days=10),
            "source_image": "priya_thyroid_report.jpg",
            "created_at": datetime.now()
        },
        {
            "patient_id": priya_id,
            "patient_name": "Priya Singh",
            "age": 35,
            "gender": "F",
            "canonical_test": "T4_FREE",
            "raw_test_name": "Free T4",
            "value": 0.8,
            "value_text": "0.8",
            "unit": "ng/dL",
            "value_standard": 0.8,
            "unit_standard": "ng/dL",
            "reference_min": 0.93,
            "reference_max": 1.7,
            "reference_raw": "0.93-1.7",
            "used_global_reference": False,
            "is_abnormal": True,
            "abnormal_direction": "LOW",
            "report_type": "THYROID",
            "report_date": base_date + timedelta(days=10),
            "source_image": "priya_thyroid_report.jpg",
            "created_at": datetime.now()
        }
    ]
    patients_data.extend(priya_tests)
    
    # Patient 4: Amit Patel
    amit_id = str(uuid.uuid4())
    amit_tests = [
        {
            "patient_id": amit_id,
            "patient_name": "Amit Patel",
            "age": 52,
            "gender": "M",
            "canonical_test": "TOTAL_CHOLESTEROL",
            "raw_test_name": "Total Cholesterol",
            "value": 245,
            "value_text": "245",
            "unit": "mg/dL",
            "value_standard": 245,
            "unit_standard": "mg/dL",
            "reference_min": 0,
            "reference_max": 200,
            "reference_raw": "<200",
            "used_global_reference": False,
            "is_abnormal": True,
            "abnormal_direction": "HIGH",
            "report_type": "LIPID",
            "report_date": base_date + timedelta(days=15),
            "source_image": "amit_lipid_report.jpg",
            "created_at": datetime.now()
        },
        {
            "patient_id": amit_id,
            "patient_name": "Amit Patel",
            "age": 52,
            "gender": "M",
            "canonical_test": "HDL_CHOLESTEROL",
            "raw_test_name": "HDL Cholesterol",
            "value": 38,
            "value_text": "38",
            "unit": "mg/dL",
            "value_standard": 38,
            "unit_standard": "mg/dL",
            "reference_min": 40,
            "reference_max": 100,
            "reference_raw": ">40",
            "used_global_reference": False,
            "is_abnormal": True,
            "abnormal_direction": "LOW",
            "report_type": "LIPID",
            "report_date": base_date + timedelta(days=15),
            "source_image": "amit_lipid_report.jpg",
            "created_at": datetime.now()
        }
    ]
    patients_data.extend(amit_tests)
    
    # Patient 5: Sunita Reddy
    sunita_id = str(uuid.uuid4())
    sunita_tests = [
        {
            "patient_id": sunita_id,
            "patient_name": "Sunita Reddy",
            "age": 42,
            "gender": "F",
            "canonical_test": "SGPT_ALT",
            "raw_test_name": "SGPT (ALT)",
            "value": 65,
            "value_text": "65",
            "unit": "U/L",
            "value_standard": 65,
            "unit_standard": "U/L",
            "reference_min": 7,
            "reference_max": 40,
            "reference_raw": "7-40",
            "used_global_reference": False,
            "is_abnormal": True,
            "abnormal_direction": "HIGH",
            "report_type": "LIVER",
            "report_date": base_date + timedelta(days=20),
            "source_image": "sunita_liver_report.jpg",
            "created_at": datetime.now()
        },
        {
            "patient_id": sunita_id,
            "patient_name": "Sunita Reddy",
            "age": 42,
            "gender": "F",
            "canonical_test": "SGOT_AST",
            "raw_test_name": "SGOT (AST)",
            "value": 58,
            "value_text": "58",
            "unit": "U/L",
            "value_standard": 58,
            "unit_standard": "U/L",
            "reference_min": 10,
            "reference_max": 40,
            "reference_raw": "10-40",
            "used_global_reference": False,
            "is_abnormal": True,
            "abnormal_direction": "HIGH",
            "report_type": "LIVER",
            "report_date": base_date + timedelta(days=20),
            "source_image": "sunita_liver_report.jpg",
            "created_at": datetime.now()
        },
        {
            "patient_id": sunita_id,
            "patient_name": "Sunita Reddy",
            "age": 42,
            "gender": "F",
            "canonical_test": "BILIRUBIN_TOTAL",
            "raw_test_name": "Total Bilirubin",
            "value": 1.8,
            "value_text": "1.8",
            "unit": "mg/dL",
            "value_standard": 1.8,
            "unit_standard": "mg/dL",
            "reference_min": 0.2,
            "reference_max": 1.2,
            "reference_raw": "0.2-1.2",
            "used_global_reference": False,
            "is_abnormal": True,
            "abnormal_direction": "HIGH",
            "report_type": "LIVER",
            "report_date": base_date + timedelta(days=20),
            "source_image": "sunita_liver_report.jpg",
            "created_at": datetime.now()
        }
    ]
    patients_data.extend(sunita_tests)
    
    return patients_data


async def add_sample_data():
    """Add sample data to MongoDB Atlas"""
    
    if not MONGO_URI:
        print("❌ ERROR: MONGO_URI not found in environment variables")
        print("Make sure your .env file has the correct MongoDB Atlas connection string")
        return
    
    try:
        # Connect to MongoDB Atlas
        print("🔗 Connecting to MongoDB Atlas...")
        client = AsyncIOMotorClient(MONGO_URI)
        db = client[DATABASE_NAME]
        collection = db[COLLECTION_NAME]
        
        # Test connection
        await client.admin.command('ismaster')
        print(f"✅ Connected to MongoDB Atlas database: {DATABASE_NAME}")
        
        # Create sample data
        print("📝 Creating sample patient data...")
        sample_data = create_sample_patients()
        
        # Clear existing test data (optional - comment out if you want to keep existing data)
        # await collection.delete_many({})
        # print("🗑️  Cleared existing test data")
        
        # Insert sample data
        print(f"📥 Inserting {len(sample_data)} test records...")
        result = await collection.insert_many(sample_data)
        
        print(f"✅ Successfully inserted {len(result.inserted_ids)} test records!")
        
        # Verify data by counting documents per patient
        pipeline = [
            {
                "$group": {
                    "_id": {
                        "patient_id": "$patient_id",
                        "patient_name": "$patient_name"
                    },
                    "test_count": {"$sum": 1}
                }
            },
            {
                "$sort": {"_id.patient_name": 1}
            }
        ]
        
        print("\n📊 Patient Summary:")
        async for doc in collection.aggregate(pipeline):
            patient = doc["_id"]
            count = doc["test_count"]
            print(f"   • {patient['patient_name']}: {count} tests")
        
        # Show total count
        total_tests = await collection.count_documents({})
        print(f"\n📈 Total test records in database: {total_tests}")
        
        print("\n🎉 Sample data successfully added to MongoDB Atlas!")
        print("   Your MediSaarthi application now has realistic patient data for testing.")
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
    finally:
        if 'client' in locals():
            client.close()


if __name__ == "__main__":
    asyncio.run(add_sample_data())