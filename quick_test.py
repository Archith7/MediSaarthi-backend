# Quick test script
from pymongo import MongoClient

c = MongoClient('mongodb://localhost:27017')
db = c['lab_analytics']

print("HEMOGLOBIN_CBC values in database:")
results = list(db.test_results.find({'canonical_test': 'HEMOGLOBIN_CBC'}).limit(10))
for r in results:
    print(f"  value={r.get('value')}, value_standard={r.get('value_standard')}, unit={r.get('unit')}")

print(f"\nTotal HEMOGLOBIN_CBC records: {db.test_results.count_documents({'canonical_test': 'HEMOGLOBIN_CBC'})}")
print(f"Records with value_standard < 12: {db.test_results.count_documents({'canonical_test': 'HEMOGLOBIN_CBC', 'value_standard': {'$lt': 12}})}")
print(f"Records with value < 12: {db.test_results.count_documents({'canonical_test': 'HEMOGLOBIN_CBC', 'value': {'$lt': 12}})}")

c.close()
