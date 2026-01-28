# -*- coding: utf-8 -*-
"""Test the full query pipeline"""

import asyncio
from modules.ai_parser import GroqAIParser
from modules.query_builder import QueryBuilder
from modules.query_executor import QueryExecutor
from modules.query_schema import StructuredQuery
from db.models import mongo_manager

async def main():
    # Initialize MongoDB connection
    await mongo_manager.connect()
    
    # Test natural language queries
    test_queries = [
        "Show me patients with low hemoglobin",
        "Find all test results for patient John",
        "How many patients have vitamin D deficiency?",
    ]
    
    parser = GroqAIParser()
    builder = QueryBuilder()
    executor = QueryExecutor()
    
    for query in test_queries:
        print(f"\n{'='*50}")
        print(f"Query: {query}")
        print('='*50)
        
        # Parse
        parsed = await parser.parse_query(query)
        print(f"Parsed: {parsed}")
        
        if parsed.get('success'):
            # Convert dict to StructuredQuery
            query_dict = parsed['query']
            structured_query = StructuredQuery(**query_dict)
            print(f"Structured Query: {structured_query}")
            
            # Build MongoDB query
            mongo_query = builder.build(structured_query)
            print(f"MongoDB Query: {mongo_query}")
            
            # Execute
            results = await executor.execute(mongo_query)
            print(f"Results count: {len(results.get('data', []))}")
            
            for r in results.get('data', [])[:3]:
                name = r.get('patient_name', 'Unknown')
                test = r.get('test_name', 'Unknown')
                value = r.get('value', 'N/A')
                print(f"  - {name}: {test} = {value}")

if __name__ == "__main__":
    asyncio.run(main())
