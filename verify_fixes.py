# Verify fixes
from pymongo import MongoClient

c = MongoClient('mongodb://localhost:27017')
db = c['lab_analytics']

print("=== FIX 1: ARCHANA NEUTROPHILS (comma parsing) ===")
doc = db.test_results.find_one({
    'patient_name': {'$regex': 'ARCHANA', '$options': 'i'}, 
    'raw_test_name': 'ABSOLUTE NEUTROPHIL COUNT'
})
if doc:
    print(f"Value: {doc.get('value')} | Text: {doc.get('value_text')}")
    print(f"Ref: {doc.get('reference_min')} - {doc.get('reference_max')}")
    print(f"Abnormal: {doc.get('is_abnormal')} ({doc.get('abnormal_direction')})")
    expected_normal = 1600 <= doc.get('value', 0) <= 8000
    print(f"Should be normal (1600-8000): {expected_normal}")
else:
    print("Not found")

print()
print("=== FIX 2: JOHNATAN DOE PLATELET COUNT (unit mismatch) ===")
docs = list(db.test_results.find({
    'patient_name': 'Johnatan Doe', 
    'canonical_test': 'PLATELET_COUNT'
}))
print(f"Record count: {len(docs)} (should be 1 after dedup)")
for d in docs:
    print(f"  Value: {d.get('value')} | Ref: {d.get('reference_min')}-{d.get('reference_max')}")
    print(f"  Abnormal: {d.get('is_abnormal')} ({d.get('abnormal_direction')})")
    expected_normal = 150 <= d.get('value', 0) <= 450
    print(f"  Should be normal (150-450): {expected_normal}")

print()
print("=== FIX 3: DUPLICATE CHECK ===")
total = db.test_results.count_documents({})
print(f"Total records: {total}")

c.close()
