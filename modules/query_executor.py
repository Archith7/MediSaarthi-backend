# -*- coding: utf-8 -*-
"""
Query Executor
Executes built MongoDB queries against the database
"""

from typing import Dict, Any, List
from db.models import mongo_manager


class QueryExecutor:
    """
    Executes MongoDB queries built by QueryBuilder
    """
    
    async def execute(self, mongo_query: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a MongoDB query
        
        Args:
            mongo_query: Dict with 'type', 'filter'/'pipeline', etc.
            
        Returns:
            Dict with 'success', 'data', 'count', or 'error'
        """
        query_type = mongo_query.get("type")
        
        if query_type == "find":
            return await self._execute_find(mongo_query)
        elif query_type == "aggregate":
            return await self._execute_aggregate(mongo_query)
        else:
            return {"success": False, "error": f"Unknown query type: {query_type}"}
    
    async def _execute_find(self, query: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a find query"""
        try:
            collection = await mongo_manager.get_collection()
            
            filter_query = query.get("filter", {})
            projection = query.get("projection")
            sort = query.get("sort")
            limit = query.get("limit")
            
            # Build cursor
            cursor = collection.find(filter_query, projection)
            
            if sort:
                cursor = cursor.sort(list(sort.items()))
            
            if limit:
                cursor = cursor.limit(limit)
            
            # Execute
            results = await cursor.to_list(length=None)
            
            # Convert ObjectId to string for JSON serialization
            for doc in results:
                if '_id' in doc:
                    doc['_id'] = str(doc['_id'])
                if 'created_at' in doc:
                    doc['created_at'] = doc['created_at'].isoformat()
                if 'report_date' in doc and doc['report_date']:
                    doc['report_date'] = doc['report_date'].isoformat()
            
            return {
                "success": True,
                "data": results,
                "count": len(results)
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _execute_aggregate(self, query: Dict[str, Any]) -> Dict[str, Any]:
        """Execute an aggregation pipeline"""
        try:
            collection = await mongo_manager.get_collection()
            
            pipeline = query.get("pipeline", [])
            
            cursor = collection.aggregate(pipeline)
            results = await cursor.to_list(length=None)
            
            return {
                "success": True,
                "data": results,
                "count": len(results)
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}


# Global executor instance
query_executor = QueryExecutor()
