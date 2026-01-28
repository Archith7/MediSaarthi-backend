# -*- coding: utf-8 -*-
"""
FastAPI Application V2
Lab Analytics API Endpoints with All Corrections Applied

KEY FIXES:
1. Uses V2 modules (ai_parser_v2, query_builder_v2, query_schema_v2, ingestion_v2)
2. Safety guard integrated for medical advice queries
3. Proper canonical test name handling (ENUM format)
4. Programmatic abnormality detection
"""

import os
# Set PaddlePaddle environment variables BEFORE any imports (for OCR)
os.environ['FLAGS_use_mkldnn'] = '0'
os.environ['FLAGS_allocator_strategy'] = 'naive_best_fit'
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'

from pathlib import Path
from typing import Dict, Any, Optional
from contextlib import asynccontextmanager

from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, HTTPException, Query, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Import V2 modules
from modules.ingestion_v2 import JSONIngesterV2, ingest_json_to_mongodb_v2
from modules.query_schema_v2 import validate_query, QueryValidationError, StructuredQuery
from modules.query_builder_v2 import query_builder as query_builder_v2
from modules.query_executor import query_executor
from modules.ai_parser_v2 import get_ai_parser, check_safety_guard
from modules.response_generator import get_response_generator
from db.models import mongo_manager
from config.canonical_mappings_v2 import CanonicalTest, get_report_type as get_test_report_type


# Pydantic models for API
class NaturalLanguageQuery(BaseModel):
    """Natural language query input"""
    query: str = Field(..., description="Natural language question about lab reports")


class StructuredQueryInput(BaseModel):
    """Direct structured query input"""
    intent: str
    patient_id: Optional[str] = None
    patient_name: Optional[str] = None
    canonical_test: Optional[str] = None
    operator: Optional[str] = None
    value: Optional[float] = None
    value_max: Optional[float] = None
    report_type: Optional[str] = None
    gender: Optional[str] = None
    aggregation_type: Optional[str] = None
    group_by: Optional[str] = None
    limit: Optional[int] = None


class IngestRequest(BaseModel):
    """JSON ingestion request"""
    json_path: Optional[str] = Field(None, description="Path to JSON file (uses default if not provided)")


# Lifespan context manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    print("🚀 Starting Lab Analytics API V2...")
    await mongo_manager.connect()
    print("✅ MongoDB connected")
    yield
    print("👋 Shutting down...")
    await mongo_manager.close()


# Create FastAPI app
app = FastAPI(
    title="Lab Analytics API V2",
    description="API for querying and analyzing lab test results (with corrections)",
    version="2.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==================== ENDPOINTS ====================

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Lab Analytics API V2",
        "version": "2.0.0",
        "features": [
            "Programmatic abnormality detection",
            "HEMOGLOBIN_CBC vs HBA1C distinction",
            "Safety guard for medical advice",
            "Unit normalization (value_standard)",
            "Global reference range fallback"
        ]
    }


@app.get("/api/stats")
async def get_stats():
    """Get database statistics"""
    try:
        total_count = await mongo_manager.count()
        abnormal_count = await mongo_manager.count({"is_abnormal": True})
        
        collection = await mongo_manager.get_collection()
        patient_ids = await collection.distinct("patient_id")
        
        # Count by report type
        pipeline = [
            {"$group": {"_id": "$report_type", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        by_report_type = await collection.aggregate(pipeline).to_list(length=100)
        
        return {
            "total_tests": total_count,
            "unique_patients": len(patient_ids),
            "abnormal_tests": abnormal_count,
            "by_report_type": {item["_id"]: item["count"] for item in by_report_type}
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/ingest")
async def ingest_data(request: IngestRequest = Body(default=IngestRequest())):
    """
    Ingest JSON data into MongoDB using V2 ingester
    Features: Programmatic abnormality detection, unit normalization
    """
    default_path = Path(__file__).parent / "all_results_new.json"
    json_path = request.json_path or str(default_path)
    
    if not Path(json_path).exists():
        raise HTTPException(status_code=404, detail=f"JSON file not found: {json_path}")
    
    try:
        result = await ingest_json_to_mongodb_v2(json_path)
        
        if result["success"]:
            return {
                "success": True,
                "message": f"Successfully ingested {result['inserted']} test records",
                "stats": result["stats"],
                "features_applied": [
                    "Programmatic abnormality detection",
                    "Unit normalization to standard units",
                    "Global reference range fallback",
                    "ENUM canonical test names"
                ]
            }
        else:
            raise HTTPException(status_code=500, detail=result["error"])
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/query")
async def execute_natural_language_query(request: NaturalLanguageQuery):
    """
    Execute a natural language query with safety guard and AI response
    Pipeline: Safety Check → AI Parser → Validation → MongoDB Query → Execute → AI Response
    """
    try:
        response_gen = get_response_generator()
        
        # Step 0: Safety guard check
        is_blocked = check_safety_guard(request.query)
        if is_blocked:
            # Generate helpful response for blocked queries
            ai_response = await response_gen.generate(
                natural_query=request.query,
                parsed_query={"intent": "BLOCKED"},
                data=[],
                result_count=0,
                error="Medical advice query blocked"
            )
            return {
                "success": False,
                "blocked": True,
                "message": ai_response,
                "natural_query": request.query
            }
        
        # Step 1: Parse natural language with AI
        parser = get_ai_parser()
        parse_result = await parser.parse_query(request.query)
        
        if not parse_result["success"]:
            # Generate helpful response for parse failures
            ai_response = await response_gen.generate(
                natural_query=request.query,
                parsed_query={"intent": "PARSE_ERROR"},
                data=[],
                result_count=0,
                error=parse_result.get('error', 'Could not understand query')
            )
            return {
                "success": False,
                "message": ai_response,
                "natural_query": request.query
            }
        
        parsed_query = parse_result["query"]
        
        # Step 2: Validate structured query
        try:
            validated_query = validate_query(parsed_query)
        except QueryValidationError as e:
            ai_response = await response_gen.generate(
                natural_query=request.query,
                parsed_query=parsed_query,
                data=[],
                result_count=0,
                error=str(e)
            )
            return {
                "success": False,
                "message": ai_response,
                "natural_query": request.query
            }
        
        # Step 3: Build MongoDB query using V2 builder
        mongo_query = query_builder_v2.build(validated_query)
        
        if "error" in mongo_query:
            ai_response = await response_gen.generate(
                natural_query=request.query,
                parsed_query=parsed_query,
                data=[],
                result_count=0,
                error=mongo_query["error"]
            )
            return {
                "success": False,
                "message": ai_response,
                "natural_query": request.query
            }
        
        # Step 4: Execute query
        result = await query_executor.execute(mongo_query)
        
        if not result["success"]:
            ai_response = await response_gen.generate(
                natural_query=request.query,
                parsed_query=parsed_query,
                data=[],
                result_count=0,
                error=result.get("error", "Query execution failed")
            )
            return {
                "success": False,
                "message": ai_response,
                "natural_query": request.query
            }
        
        # Step 5: Generate AI-polished response
        ai_response = await response_gen.generate(
            natural_query=request.query,
            parsed_query=parsed_query,
            data=result["data"],
            result_count=result["count"]
        )
        
        return {
            "success": True,
            "natural_query": request.query,
            "message": ai_response,
            "parsed_query": parsed_query,
            "result_count": result["count"],
            "data": result["data"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        # Even errors get a friendly response
        try:
            response_gen = get_response_generator()
            ai_response = await response_gen.generate(
                natural_query=request.query,
                parsed_query={},
                data=[],
                result_count=0,
                error=str(e)
            )
            return {
                "success": False,
                "message": ai_response,
                "natural_query": request.query
            }
        except:
            raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/query/structured")
async def execute_structured_query(request: StructuredQueryInput):
    """
    Execute a pre-built structured query directly (bypass AI)
    """
    try:
        query_dict = request.model_dump(exclude_none=True)
        
        try:
            validated_query = validate_query(query_dict)
        except QueryValidationError as e:
            raise HTTPException(status_code=400, detail=f"Query validation failed: {str(e)}")
        
        mongo_query = query_builder_v2.build(validated_query)
        
        if "error" in mongo_query:
            raise HTTPException(status_code=400, detail=mongo_query["error"])
        
        result = await query_executor.execute(mongo_query)
        
        if not result["success"]:
            raise HTTPException(status_code=500, detail=result["error"])
        
        return {
            "success": True,
            "query": query_dict,
            "result_count": result["count"],
            "data": result["data"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/patient/{patient_name}")
async def get_patient_tests(patient_name: str, report_type: Optional[str] = None):
    """Get all tests for a specific patient by name"""
    try:
        query_dict = {
            "intent": "PATIENT_LOOKUP",
            "patient_name": patient_name
        }
        
        if report_type:
            query_dict["report_type"] = report_type
        
        validated_query = validate_query(query_dict)
        mongo_query = query_builder_v2.build(validated_query)
        result = await query_executor.execute(mongo_query)
        
        if not result["success"]:
            raise HTTPException(status_code=500, detail=result["error"])
        
        return {
            "success": True,
            "patient_name": patient_name,
            "result_count": result["count"],
            "tests": result["data"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/abnormal")
async def get_abnormal_tests(
    canonical_test: Optional[str] = None,
    patient_name: Optional[str] = None,
    report_type: Optional[str] = None,
    gender: Optional[str] = None,
    limit: Optional[int] = 100
):
    """
    Get all abnormal test results
    FIXED: Now properly enforces patient constraint when patient_name provided
    """
    try:
        query_dict = {"intent": "DEFICIENCY"}
        
        if canonical_test:
            # Normalize to ENUM format
            query_dict["canonical_test"] = canonical_test.upper().replace(" ", "_")
        if patient_name:
            query_dict["patient_name"] = patient_name
        if report_type:
            query_dict["report_type"] = report_type
        if gender:
            query_dict["gender"] = gender
        if limit:
            query_dict["limit"] = limit
        
        validated_query = validate_query(query_dict)
        mongo_query = query_builder_v2.build(validated_query)
        result = await query_executor.execute(mongo_query)
        
        if not result["success"]:
            raise HTTPException(status_code=500, detail=result["error"])
        
        return {
            "success": True,
            "result_count": result["count"],
            "abnormal_tests": result["data"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/filter")
async def filter_tests(
    canonical_test: str,
    operator: Optional[str] = None,
    value: Optional[float] = None,
    report_type: Optional[str] = None,
    gender: Optional[str] = None,
    limit: Optional[int] = 100
):
    """
    Filter tests by criteria
    FIXED: Auto-injects threshold when operator not provided
    """
    try:
        # Normalize canonical test to ENUM format
        canonical_test_enum = canonical_test.upper().replace(" ", "_")
        
        query_dict = {
            "intent": "FILTER",
            "canonical_test": canonical_test_enum
        }
        
        if operator:
            query_dict["operator"] = operator
        if value is not None:
            query_dict["value"] = value
        if report_type:
            query_dict["report_type"] = report_type
        if gender:
            query_dict["gender"] = gender
        if limit:
            query_dict["limit"] = limit
        
        validated_query = validate_query(query_dict)
        mongo_query = query_builder_v2.build(validated_query)
        result = await query_executor.execute(mongo_query)
        
        if not result["success"]:
            raise HTTPException(status_code=500, detail=result["error"])
        
        return {
            "success": True,
            "result_count": result["count"],
            "tests": result["data"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/summary")
async def get_summary(report_type: Optional[str] = None):
    """Get overall summary statistics"""
    try:
        query_dict = {"intent": "SUMMARY"}
        
        if report_type:
            query_dict["report_type"] = report_type
        
        validated_query = validate_query(query_dict)
        mongo_query = query_builder_v2.build(validated_query)
        result = await query_executor.execute(mongo_query)
        
        if not result["success"]:
            raise HTTPException(status_code=500, detail=result["error"])
        
        data = result["data"][0] if result["data"] else {}
        
        summary = {
            "total_tests": data.get("total_tests", [{}])[0].get("count", 0),
            "unique_patients": data.get("unique_patients", [{}])[0].get("count", 0),
            "abnormal_count": data.get("abnormal_count", [{}])[0].get("count", 0),
            "by_report_type": data.get("by_report_type", []),
            "top_tests": data.get("by_test", [])
        }
        
        return {
            "success": True,
            "summary": summary
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/tests")
async def list_available_tests():
    """
    List all canonical test names (ENUM format)
    """
    # Group by report type
    tests_by_category = {}
    
    for test in CanonicalTest:
        if test == CanonicalTest.UNKNOWN:
            continue
        report_type = get_test_report_type(test)
        if report_type not in tests_by_category:
            tests_by_category[report_type] = []
        tests_by_category[report_type].append(test.value)
    
    return {
        "success": True,
        "tests_by_category": tests_by_category,
        "total_test_types": sum(len(v) for v in tests_by_category.values())
    }


@app.get("/api/reference-ranges")
async def get_reference_ranges(
    canonical_test: Optional[str] = None,
    gender: Optional[str] = None
):
    """
    Get global reference ranges for tests
    """
    from config.reference_ranges import GLOBAL_REFERENCE_RANGES, get_reference_range
    
    if canonical_test:
        # Get specific test
        test_upper = canonical_test.upper().replace(" ", "_")
        ref_range = get_reference_range(test_upper, gender)
        
        return {
            "success": True,
            "test": test_upper,
            "gender": gender,
            "reference_range": ref_range
        }
    else:
        # Return all
        return {
            "success": True,
            "reference_ranges": GLOBAL_REFERENCE_RANGES
        }


@app.get("/health")
async def health_check():
    """Simple health check for UI"""
    return {"status": "healthy"}


@app.get("/api/recent-abnormal")
async def get_recent_abnormal(limit: int = 10):
    """Get recent abnormal test results"""
    try:
        collection = await mongo_manager.get_collection()
        results = await collection.find(
            {"is_abnormal": True},
            {"_id": 0}
        ).sort("created_at", -1).limit(limit).to_list(length=limit)
        
        return {
            "success": True,
            "count": len(results),
            "results": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/patients")
async def get_patients():
    """Get list of all patients with summary info"""
    try:
        collection = await mongo_manager.get_collection()
        
        # Aggregate patient data
        pipeline = [
            {
                "$group": {
                    "_id": "$patient_name",
                    "age": {"$first": "$age"},
                    "gender": {"$first": "$gender"},
                    "test_count": {"$sum": 1},
                    "has_abnormal": {"$max": "$is_abnormal"},
                    "latest_date": {"$max": "$report_date"}
                }
            },
            {
                "$project": {
                    "name": "$_id",
                    "age": 1,
                    "gender": 1,
                    "test_count": 1,
                    "has_abnormal": 1,
                    "latest_test": {
                        "$dateToString": {
                            "format": "%Y-%m-%d",
                            "date": "$latest_date",
                            "onNull": "N/A"
                        }
                    }
                }
            },
            {"$sort": {"name": 1}}
        ]
        
        patients = await collection.aggregate(pipeline).to_list(length=None)
        
        return {
            "success": True,
            "count": len(patients),
            "patients": patients
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/ocr/upload")
async def upload_image(file: Any):
    """
    Placeholder for image upload OCR endpoint
    TODO: Integrate OCR module
    """
    return {
        "success": False,
        "message": "OCR functionality not yet implemented in V2"
    }


# Static files for UI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# Serve static files
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/ui")
async def serve_ui():
    """Serve the UI"""
    return FileResponse("static/index.html")


# Run with: uvicorn api_v2:app --reload --port 8001
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
