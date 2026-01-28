# -*- coding: utf-8 -*-
"""
Re-Ingestion Script V2
Run this to populate MongoDB with corrected data

Features Applied:
1. Programmatic abnormality detection (ignores OCR flags)
2. Unit normalization (value_standard, unit_standard)
3. Global reference range fallback
4. ENUM canonical test names (HEMOGLOBIN_CBC vs HBA1C)
"""

import asyncio
import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent))

from modules.ingestion_v2 import ingest_json_to_mongodb_v2
from db.models import mongo_manager


async def main():
    """Run re-ingestion with V2 ingester"""
    print("=" * 60)
    print("LAB ANALYTICS V2 - RE-INGESTION")
    print("=" * 60)
    
    # Default JSON path
    json_path = Path(__file__).parent / "all_results_new.json"
    
    if not json_path.exists():
        print(f"❌ JSON file not found: {json_path}")
        return
    
    print(f"📄 Source: {json_path}")
    print()
    
    # Connect to MongoDB
    print("🔌 Connecting to MongoDB...")
    await mongo_manager.connect()
    
    # Get current count
    current_count = await mongo_manager.count()
    print(f"📊 Current records in database: {current_count}")
    print()
    
    # Run ingestion
    print("🔄 Running V2 ingestion...")
    print("   - Programmatic abnormality detection")
    print("   - Unit normalization")
    print("   - Global reference range fallback")
    print("   - ENUM canonical test names")
    print()
    
    result = await ingest_json_to_mongodb_v2(str(json_path))
    
    if result["success"]:
        print("✅ INGESTION COMPLETE")
        print()
        print("📈 Statistics:")
        stats = result.get("stats", {})
        print(f"   Total records inserted: {result['inserted']}")
        print(f"   Reports processed: {stats.get('reports', 0)}")
        
        # Get breakdown
        collection = await mongo_manager.get_collection()
        
        # By report type
        pipeline = [
            {"$group": {"_id": "$report_type", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        by_type = await collection.aggregate(pipeline).to_list(length=10)
        
        print()
        print("📋 By Report Type:")
        for item in by_type:
            print(f"   {item['_id']}: {item['count']}")
        
        # Abnormal count
        abnormal = await mongo_manager.count({"is_abnormal": True})
        print()
        print(f"🔴 Abnormal tests: {abnormal}")
        
        # Used global reference
        global_ref = await mongo_manager.count({"used_global_reference": True})
        print(f"📐 Used global reference: {global_ref}")
        
        # Sample a record
        print()
        print("📝 Sample record:")
        sample = await collection.find_one({"canonical_test": "HEMOGLOBIN_CBC"})
        if sample:
            print(f"   Test: {sample.get('canonical_test')}")
            print(f"   Value: {sample.get('value')} {sample.get('unit')}")
            print(f"   Standard: {sample.get('value_standard')} {sample.get('unit_standard')}")
            print(f"   Abnormal: {sample.get('is_abnormal')}")
            print(f"   Abnormality: {sample.get('abnormality_type')}")
        
    else:
        print(f"❌ INGESTION FAILED: {result.get('error')}")
    
    # Cleanup
    await mongo_manager.close()
    print()
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
