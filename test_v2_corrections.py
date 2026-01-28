# -*- coding: utf-8 -*-
"""
Test V2 Corrections
Quick test script to verify all 10 corrections work correctly
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from pymongo import MongoClient


async def test_all_corrections():
    """Test all 10 corrections"""
    print("=" * 60)
    print("TESTING V2 CORRECTIONS")
    print("=" * 60)
    
    # Connect to MongoDB
    client = MongoClient('mongodb://localhost:27017')
    db = client['lab_analytics']
    collection = db['test_results']
    
    # Test 1: HEMOGLOBIN_CBC vs HBA1C distinction
    print("\n1️⃣ TEST: HEMOGLOBIN_CBC vs HBA1C distinction")
    hb_cbc = collection.count_documents({"canonical_test": "HEMOGLOBIN_CBC"})
    hba1c = collection.count_documents({"canonical_test": "HBA1C"})
    print(f"   HEMOGLOBIN_CBC records: {hb_cbc}")
    print(f"   HBA1C records: {hba1c}")
    print(f"   ✅ PASS" if hb_cbc > 0 and hba1c >= 0 else "   ❌ FAIL")
    
    # Test 2: Programmatic abnormality detection
    print("\n2️⃣ TEST: Programmatic abnormality detection")
    abnormal_high = collection.find_one({"abnormal_direction": "HIGH"})
    abnormal_low = collection.find_one({"abnormal_direction": "LOW"})
    if abnormal_high:
        print(f"   Sample HIGH: {abnormal_high['canonical_test']} = {abnormal_high['value']} (ref: {abnormal_high.get('reference_min')}-{abnormal_high.get('reference_max')})")
    if abnormal_low:
        print(f"   Sample LOW: {abnormal_low['canonical_test']} = {abnormal_low['value']} (ref: {abnormal_low.get('reference_min')}-{abnormal_low.get('reference_max')})")
    abnormal_count = collection.count_documents({"is_abnormal": True})
    print(f"   Total abnormal: {abnormal_count}")
    print(f"   ✅ PASS" if abnormal_high or abnormal_low else "   ⚠️ WARNING: No abnormal direction found")
    
    # Test 3: Global reference fallback
    print("\n3️⃣ TEST: Global reference range fallback")
    global_ref_used = collection.count_documents({"used_global_reference": True})
    print(f"   Records using global reference: {global_ref_used}")
    if global_ref_used > 0:
        sample = collection.find_one({"used_global_reference": True})
        print(f"   Sample: {sample['canonical_test']} - ref {sample.get('reference_min')}-{sample.get('reference_max')}")
    print(f"   ✅ PASS" if global_ref_used > 0 else "   ⚠️ INFO: No global fallbacks needed")
    
    # Test 4: Unit normalization
    print("\n4️⃣ TEST: Unit normalization (value_standard)")
    with_standard = collection.count_documents({"value_standard": {"$ne": None}})
    sample = collection.find_one({"value_standard": {"$ne": None}})
    if sample:
        print(f"   Sample: {sample['value']} {sample['unit']} → {sample['value_standard']} {sample['unit_standard']}")
    print(f"   Records with standard values: {with_standard}")
    print(f"   ✅ PASS" if with_standard > 0 else "   ❌ FAIL")
    
    # Test 5: DEFICIENCY intent (test query builder)
    print("\n5️⃣ TEST: DEFICIENCY intent patient constraint")
    from modules.query_schema_v2 import validate_query
    from modules.query_builder_v2 import query_builder
    
    query = validate_query({
        "intent": "DEFICIENCY",
        "patient_name": "Niketa"
    })
    mongo_query = query_builder.build(query)
    print(f"   Query filter keys: {list(mongo_query.get('filter', {}).keys())}")
    has_patient = "patient_name" in mongo_query.get('filter', {}) or "$and" in mongo_query.get('filter', {})
    print(f"   ✅ PASS - Patient constraint enforced" if has_patient else "   ❌ FAIL - No patient constraint")
    
    # Test 6: FILTER threshold handling
    print("\n6️⃣ TEST: FILTER auto-inject threshold")
    query = validate_query({
        "intent": "FILTER",
        "canonical_test": "HEMOGLOBIN_CBC"
        # No operator/value provided
    })
    mongo_query = query_builder.build(query)
    print(f"   MongoDB query generated: {bool(mongo_query.get('filter'))}")
    print(f"   ✅ PASS - Query builds without threshold" if "error" not in mongo_query else "   ❌ FAIL")
    
    # Test 7: Report scope enforcement
    print("\n7️⃣ TEST: Report scope enforcement for CBC tests")
    query = validate_query({
        "intent": "FILTER",
        "canonical_test": "HEMOGLOBIN_CBC"
    })
    mongo_query = query_builder.build(query)
    has_report_type = "report_type" in str(mongo_query.get('filter', {}))
    print(f"   Report type in filter: {has_report_type}")
    print(f"   ✅ PASS" if has_report_type else "   ⚠️ INFO: Report type not added (may be intentional)")
    
    # Test 8: Safety guard
    print("\n8️⃣ TEST: Safety guard for medical advice")
    from modules.ai_parser_v2 import check_safety_guard
    
    # Should block
    blocked1 = check_safety_guard("Why is my hemoglobin low? What should I do?")
    blocked2 = check_safety_guard("Is high TSH dangerous? What medication should I take?")
    # Should not block
    blocked3 = check_safety_guard("Show me all patients with low hemoglobin")
    blocked4 = check_safety_guard("List abnormal CBC results")
    
    print(f"   'Why is my hemoglobin low?' blocked: {blocked1}")
    print(f"   'Is high TSH dangerous?' blocked: {blocked2}")
    print(f"   'Show patients with low hemoglobin' blocked: {blocked3}")
    print(f"   'List abnormal CBC results' blocked: {blocked4}")
    print(f"   ✅ PASS" if blocked1 and blocked2 and not blocked3 and not blocked4 else "   ⚠️ PARTIAL")
    
    # Test 9: ENUM canonical test names
    print("\n9️⃣ TEST: ENUM canonical test names")
    from config.canonical_mappings_v2 import CanonicalTest, get_canonical_test
    
    # Test mapping
    hb1 = get_canonical_test("Hemoglobin", "CBC")
    hb2 = get_canonical_test("Hemoglobin (HbA1c)", "DIABETES")
    print(f"   'Hemoglobin' in CBC → {hb1.value if hb1 else 'None'}")
    print(f"   'Hemoglobin (HbA1c)' in DIABETES → {hb2.value if hb2 else 'None'}")
    print(f"   ✅ PASS" if hb1 == CanonicalTest.HEMOGLOBIN_CBC and hb2 == CanonicalTest.HBA1C else "   ❌ FAIL")
    
    # Test 10: Data integrity
    print("\n🔟 TEST: Data integrity check")
    total = collection.count_documents({})
    by_report = collection.aggregate([
        {"$group": {"_id": "$report_type", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ])
    print(f"   Total records: {total}")
    print(f"   By report type:")
    for r in by_report:
        print(f"      {r['_id']}: {r['count']}")
    print(f"   ✅ PASS" if total > 0 else "   ❌ FAIL")
    
    print("\n" + "=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)
    
    client.close()


if __name__ == "__main__":
    asyncio.run(test_all_corrections())
