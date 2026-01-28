# -*- coding: utf-8 -*-
"""
Test Script - Verify Ingestion Pipeline
Run this to test the JSON → Normalized Documents flow
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from modules.ingestion import JSONIngester


def test_ingestion():
    """Test the JSON ingestion without MongoDB"""
    
    json_path = Path(__file__).parent / "all_results_new.json"
    
    if not json_path.exists():
        print(f"❌ JSON file not found: {json_path}")
        return
    
    print("="*60)
    print("🧪 TESTING INGESTION PIPELINE")
    print("="*60)
    
    # Create ingester
    ingester = JSONIngester(str(json_path))
    
    # Run ingestion
    documents = ingester.ingest()
    
    # Print statistics
    ingester.print_stats()
    
    if not documents:
        print("❌ No documents generated!")
        return
    
    # Print sample documents
    print("\n" + "="*60)
    print("📄 SAMPLE DOCUMENTS")
    print("="*60)
    
    for i, doc in enumerate(documents[:5]):
        print(f"\n--- Document {i+1} ---")
        print(f"  🧑 Patient: {doc.patient_name}")
        print(f"     Gender: {doc.gender}, Age: {doc.age}")
        print(f"     Patient ID: {doc.patient_id[:8]}...")
        print(f"  🔬 Test: {doc.canonical_test}")
        print(f"     Raw Name: {doc.raw_test_name}")
        print(f"  📊 Value: {doc.value} {doc.unit}")
        print(f"     Original: {doc.value_text}")
        print(f"  📏 Reference: {doc.reference_min} - {doc.reference_max}")
        print(f"     Raw: {doc.reference_raw}")
        print(f"  ⚠️  Abnormal: {doc.is_abnormal} ({doc.abnormal_direction or 'N/A'})")
        print(f"  📁 Report Type: {doc.report_type}")
        print(f"  🖼️  Source: {doc.source_image}")
    
    # Test specific lookups
    print("\n" + "="*60)
    print("🔍 TESTING DATA LOOKUP")
    print("="*60)
    
    # Count by report type
    report_types = {}
    for doc in documents:
        rt = doc.report_type
        report_types[rt] = report_types.get(rt, 0) + 1
    
    print("\n📊 Tests by Report Type:")
    for rt, count in sorted(report_types.items(), key=lambda x: -x[1]):
        print(f"   {rt}: {count}")
    
    # Count abnormal by test
    abnormal_tests = {}
    for doc in documents:
        if doc.is_abnormal:
            test = doc.canonical_test
            abnormal_tests[test] = abnormal_tests.get(test, 0) + 1
    
    print("\n⚠️  Top Abnormal Tests:")
    for test, count in sorted(abnormal_tests.items(), key=lambda x: -x[1])[:10]:
        print(f"   {test}: {count} abnormal")
    
    # Unique patients
    unique_patients = set(doc.patient_id for doc in documents)
    print(f"\n👥 Unique Patients: {len(unique_patients)}")
    
    print("\n" + "="*60)
    print("✅ INGESTION TEST COMPLETE")
    print("="*60)


if __name__ == "__main__":
    test_ingestion()
