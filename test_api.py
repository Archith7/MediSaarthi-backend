# -*- coding: utf-8 -*-
"""
API Test Script
Tests all endpoints of the Lab Analytics API
"""

import httpx
import asyncio
import json


BASE_URL = "http://localhost:8000"


async def test_api():
    """Test all API endpoints"""
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        
        print("="*60)
        print("🧪 TESTING LAB ANALYTICS API")
        print("="*60)
        
        # 1. Health Check
        print("\n1️⃣ Testing Health Check...")
        r = await client.get(f"{BASE_URL}/")
        print(f"   Status: {r.status_code}")
        print(f"   Response: {r.json()}")
        
        # 2. Ingest Data
        print("\n2️⃣ Testing Data Ingestion...")
        r = await client.post(f"{BASE_URL}/api/ingest", json={})
        print(f"   Status: {r.status_code}")
        if r.status_code == 200:
            data = r.json()
            print(f"   Inserted: {data.get('stats', {}).get('tests_extracted', 0)} tests")
            print(f"   Patients: {data.get('stats', {}).get('patients_processed', 0)}")
        else:
            print(f"   Error: {r.text}")
        
        # 3. Get Stats
        print("\n3️⃣ Testing Stats Endpoint...")
        r = await client.get(f"{BASE_URL}/api/stats")
        print(f"   Status: {r.status_code}")
        if r.status_code == 200:
            data = r.json()
            print(f"   Total Tests: {data.get('total_tests')}")
            print(f"   Unique Patients: {data.get('unique_patients')}")
            print(f"   Abnormal Tests: {data.get('abnormal_tests')}")
        
        # 4. Get Summary
        print("\n4️⃣ Testing Summary Endpoint...")
        r = await client.get(f"{BASE_URL}/api/summary")
        print(f"   Status: {r.status_code}")
        if r.status_code == 200:
            summary = r.json().get("summary", {})
            print(f"   Total Tests: {summary.get('total_tests')}")
            print(f"   Patients: {summary.get('unique_patients')}")
            print(f"   By Report Type: {summary.get('by_report_type')[:3]}")
        
        # 5. Get Abnormal Tests
        print("\n5️⃣ Testing Abnormal Endpoint...")
        r = await client.get(f"{BASE_URL}/api/abnormal?limit=5")
        print(f"   Status: {r.status_code}")
        if r.status_code == 200:
            data = r.json()
            print(f"   Total Abnormal: {data.get('result_count')}")
            for test in data.get('abnormal_tests', [])[:3]:
                print(f"   - {test['patient_name']}: {test['canonical_test']} = {test['value']} ({test['abnormal_direction']})")
        
        # 6. Patient Lookup
        print("\n6️⃣ Testing Patient Lookup...")
        r = await client.get(f"{BASE_URL}/api/patient/NIKETA")
        print(f"   Status: {r.status_code}")
        if r.status_code == 200:
            data = r.json()
            print(f"   Tests found: {data.get('result_count')}")
            for test in data.get('tests', [])[:3]:
                print(f"   - {test['canonical_test']}: {test['value']} {test['unit']}")
        
        # 7. Structured Query
        print("\n7️⃣ Testing Structured Query...")
        query = {
            "intent": "FILTER",
            "canonical_test": "HEMOGLOBIN",
            "operator": "lt",
            "value": 12.0,
            "limit": 5
        }
        r = await client.post(f"{BASE_URL}/api/query/structured", json=query)
        print(f"   Status: {r.status_code}")
        if r.status_code == 200:
            data = r.json()
            print(f"   Results: {data.get('result_count')}")
            for d in data.get('data', [])[:3]:
                print(f"   - {d['patient_name']}: HB = {d['value']} g/dL")
        else:
            print(f"   Error: {r.text}")
        
        # 8. Natural Language Query (Mock)
        print("\n8️⃣ Testing Natural Language Query (Mock)...")
        r = await client.post(f"{BASE_URL}/api/query", json={
            "query": "Show me a summary of all tests",
            "use_mock": True
        })
        print(f"   Status: {r.status_code}")
        if r.status_code == 200:
            data = r.json()
            print(f"   Parsed Intent: {data.get('parsed_query', {}).get('intent')}")
            print(f"   Results: {data.get('result_count')}")
        
        # 9. Available Tests
        print("\n9️⃣ Testing Available Tests...")
        r = await client.get(f"{BASE_URL}/api/tests")
        print(f"   Status: {r.status_code}")
        if r.status_code == 200:
            tests = r.json().get("tests", {})
            print(f"   Total test types: {len(tests)}")
            print(f"   Sample: {list(tests.keys())[:5]}")
        
        print("\n" + "="*60)
        print("✅ API TESTS COMPLETE")
        print("="*60)


if __name__ == "__main__":
    asyncio.run(test_api())
