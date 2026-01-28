# -*- coding: utf-8 -*-
"""
FastAPI Application
Lab Analytics API Endpoints

UPDATED: Now uses V2 query builder with canonical test normalization
"""

import os
# Set PaddlePaddle environment variables BEFORE any imports (for OCR)
os.environ['FLAGS_use_mkldnn'] = '0'
os.environ['FLAGS_allocator_strategy'] = 'naive_best_fit'
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'

from pathlib import Path
from typing import Dict, Any, Optional
from contextlib import asynccontextmanager
from datetime import datetime

from dotenv import load_dotenv
load_dotenv()  # Load .env file

from fastapi import FastAPI, HTTPException, Query, Body, UploadFile, File, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Import modules - USE V2 QUERY BUILDER for proper test name normalization
from modules.ingestion import JSONIngester, ingest_json_to_mongodb
from modules.query_schema import validate_query, QueryValidationError, StructuredQuery
from modules.query_builder_v2 import query_builder  # V2 with normalization!
from modules.query_executor import query_executor
from modules.ai_parser import get_ai_parser, MockAIParser
from modules.response_generator import generate_response
from db.models import mongo_manager


# Pydantic models for API
class NaturalLanguageQuery(BaseModel):
    """Natural language query input"""
    query: str = Field(..., description="Natural language question about lab reports")
    use_mock: bool = Field(False, description="Use mock parser instead of Groq API")


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
    # Startup
    print("[*] Starting Lab Analytics API...")
    await mongo_manager.connect()
    print("[+] MongoDB connected")
    yield
    # Shutdown
    print("[*] Shutting down...")
    await mongo_manager.close()


# Create FastAPI app
app = FastAPI(
    title="MediSaarthi API",
    description="AI-powered lab report analysis and natural language querying system",
    version="2.0.0",
    lifespan=lifespan
)

# CORS Configuration for production
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://medi-saarthi-frontend.vercel.app",  # Production frontend
        "https://medisaarthi.vercel.app",            # Alternative production domain
        "https://*.vercel.app",                      # Vercel preview deployments
        "http://localhost:3000",                     # Local development
        "http://localhost:5173",                     # Vite dev server
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==================== ENDPOINTS ====================

# ==================== AUTHENTICATION ====================

from modules.auth import (
    UserCreate, UserLogin, UserResponse, Token,
    get_password_hash, verify_password, create_access_token,
    get_current_user, get_optional_user
)
import uuid


@app.post("/api/auth/register", response_model=Token)
async def register(user_data: UserCreate):
    """Register a new user"""
    try:
        # Check if user already exists
        existing_user = await mongo_manager.db.users.find_one({"email": user_data.email})
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Create user document
        user_id = str(uuid.uuid4())
        user_doc = {
            "_id": user_id,
            "email": user_data.email,
            "full_name": user_data.full_name,
            "organization": user_data.organization,
            "hashed_password": get_password_hash(user_data.password),
            "created_at": datetime.now(),
            "is_active": True
        }
        
        await mongo_manager.db.users.insert_one(user_doc)
        
        # Create access token
        access_token = create_access_token(
            data={"sub": user_id, "email": user_data.email}
        )
        
        return Token(
            access_token=access_token,
            user=UserResponse(
                id=user_id,
                email=user_data.email,
                full_name=user_data.full_name,
                organization=user_data.organization,
                created_at=user_doc["created_at"]
            )
        )
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        print(f"[Auth] Registration error: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")


@app.post("/api/auth/login", response_model=Token)
async def login(credentials: UserLogin):
    """Login and get access token"""
    try:
        # Find user
        user = await mongo_manager.db.users.find_one({"email": credentials.email})
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Verify password
        if not verify_password(credentials.password, user["hashed_password"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Check if active
        if not user.get("is_active", True):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is disabled"
            )
        
        # Create access token
        access_token = create_access_token(
            data={"sub": user["_id"], "email": user["email"]}
        )
        
        return Token(
            access_token=access_token,
            user=UserResponse(
                id=user["_id"],
                email=user["email"],
                full_name=user["full_name"],
                organization=user.get("organization"),
                created_at=user["created_at"]
            )
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f"[Auth] Login error: {e}")
        raise HTTPException(status_code=500, detail="Login failed")


@app.get("/api/auth/me", response_model=UserResponse)
async def get_me(current_user: dict = Depends(get_current_user)):
    """Get current user profile"""
    return UserResponse(
        id=current_user["_id"],
        email=current_user["email"],
        full_name=current_user["full_name"],
        organization=current_user.get("organization"),
        created_at=current_user["created_at"],
        is_active=current_user.get("is_active", True)
    )


@app.put("/api/auth/profile")
async def update_profile(
    full_name: Optional[str] = Body(None),
    organization: Optional[str] = Body(None),
    current_user: dict = Depends(get_current_user)
):
    """Update user profile"""
    update_data = {}
    if full_name is not None:
        update_data["full_name"] = full_name
    if organization is not None:
        update_data["organization"] = organization
    
    if update_data:
        await mongo_manager.db.users.update_one(
            {"_id": current_user["_id"]},
            {"$set": update_data}
        )
    
    return {"success": True, "message": "Profile updated"}


# ==================== PUBLIC ENDPOINTS ====================

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "status": "healthy",
        "service": "Lab Analytics API",
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    print("[API] Health check called")
    return {
        "status": "healthy",
        "service": "Lab Analytics API",
        "mongodb": "connected" if mongo_manager.db is not None else "disconnected"
    }


@app.get("/debug")
async def debug_info():
    """Debug endpoint to check database configuration"""
    import os
    from db.models import MONGO_URI, DATABASE_NAME, COLLECTION_NAME
    
    try:
        collection = await mongo_manager.get_collection()
        test_count = await collection.count_documents({})
        db_name = mongo_manager.db.name if mongo_manager.db else "None"
        
        return {
            "environment": os.getenv("ENVIRONMENT", "not_set"),
            "database_name": db_name,
            "collection_name": COLLECTION_NAME,
            "mongo_uri_prefix": MONGO_URI[:50] + "..." if MONGO_URI else "not_set",
            "test_count": test_count,
            "mongo_db_env": os.getenv("MONGO_DB", "not_set")
        }
    except Exception as e:
        return {
            "error": str(e),
            "mongo_uri_prefix": MONGO_URI[:50] + "..." if MONGO_URI else "not_set",
            "database_name": DATABASE_NAME,
            "environment": os.getenv("ENVIRONMENT", "not_set")
        }


@app.get("/api/stats")
async def get_stats():
    """Get comprehensive database statistics"""
    print("[API] Stats endpoint called")
    try:
        collection = await mongo_manager.get_collection()
        
        # Basic counts
        total_tests = await collection.count_documents({})
        abnormal_count = await collection.count_documents({"is_abnormal": True})
        
        # Unique patients
        patient_names = await collection.distinct("patient_name")
        total_patients = len(patient_names)
        
        # Unique test types
        test_types = await collection.distinct("canonical_test")
        unique_tests = len(test_types)
        
        # Test distribution (top 10)
        pipeline_test_dist = [
            {"$group": {"_id": "$canonical_test", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": 10}
        ]
        test_dist_cursor = collection.aggregate(pipeline_test_dist)
        test_distribution = {doc["_id"]: doc["count"] async for doc in test_dist_cursor}
        
        # Abnormal by test type (top 10)
        pipeline_abnormal = [
            {"$match": {"is_abnormal": True}},
            {"$group": {"_id": "$canonical_test", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": 10}
        ]
        abnormal_cursor = collection.aggregate(pipeline_abnormal)
        abnormal_by_test = {doc["_id"]: doc["count"] async for doc in abnormal_cursor}
        
        # Gender distribution
        pipeline_gender = [
            {"$group": {"_id": "$gender", "count": {"$sum": 1}}}
        ]
        gender_cursor = collection.aggregate(pipeline_gender)
        gender_distribution = {doc["_id"] or "Unknown": doc["count"] async for doc in gender_cursor}
        
        # Abnormality rate
        abnormal_rate = round((abnormal_count / total_tests * 100), 1) if total_tests > 0 else 0
        
        return {
            "total_tests": total_tests,
            "total_patients": total_patients,
            "unique_tests": unique_tests,
            "abnormal_count": abnormal_count,
            "normal_count": total_tests - abnormal_count,
            "abnormal_rate": abnormal_rate,
            "test_distribution": test_distribution,
            "abnormal_by_test": abnormal_by_test,
            "gender_distribution": gender_distribution
        }
    except Exception as e:
        print(f"[API] Stats error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/ingest")
async def ingest_data(request: IngestRequest = Body(default=IngestRequest())):
    """
    Ingest JSON data into MongoDB
    Uses default path if not specified
    """
    # Default JSON path
    default_path = Path(__file__).parent / "all_results_new.json"
    json_path = request.json_path or str(default_path)
    
    if not Path(json_path).exists():
        raise HTTPException(status_code=404, detail=f"JSON file not found: {json_path}")
    
    try:
        result = await ingest_json_to_mongodb(json_path)
        
        if result["success"]:
            return {
                "success": True,
                "message": f"Successfully ingested {result['inserted']} test records",
                "stats": result["stats"]
            }
        else:
            raise HTTPException(status_code=500, detail=result["error"])
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/query")
async def execute_natural_language_query(request: NaturalLanguageQuery):
    """
    Execute a natural language query
    Pipeline: NL → AI Parser → Structured Query → Validation → MongoDB Query → Execute
    """
    print(f"\n[API] Received query: {request.query}")
    try:
        # Step 1: Parse natural language with AI
        if request.use_mock:
            parser = MockAIParser()
        else:
            try:
                parser = get_ai_parser()
            except ValueError:
                # Fall back to mock if no API key
                parser = MockAIParser()
        
        parse_result = await parser.parse_query(request.query)
        
        if not parse_result["success"]:
            raise HTTPException(status_code=400, detail=f"Failed to parse query: {parse_result['error']}")
        
        parsed_query = parse_result["query"]
        
        # Step 2: Validate structured query
        try:
            validated_query = validate_query(parsed_query)
        except QueryValidationError as e:
            raise HTTPException(status_code=400, detail=f"Query validation failed: {str(e)}")
        
        # Step 3: Build MongoDB query
        mongo_query = query_builder.build(validated_query)
        
        if "error" in mongo_query:
            raise HTTPException(status_code=400, detail=mongo_query["error"])
        
        # Step 4: Execute query
        result = await query_executor.execute(mongo_query)
        
        if not result["success"]:
            raise HTTPException(status_code=500, detail=result["error"])
        
        # Step 5: Generate AI-powered natural language response
        print(f"[API] Generating response for {result['count']} results...")
        message = await generate_response(
            natural_query=request.query,
            parsed_query=parsed_query,
            data=result["data"],
            result_count=result["count"],
            error=None
        )
        print(f"[API] Generated message: {message[:100]}...")
        
        response_data = {
            "success": True,
            "message": message,
            "natural_query": request.query,
            "parsed_query": parsed_query,
            "result_count": result["count"],
            "data": result["data"]
        }
        print(f"[API] Sending response - Success: {response_data['success']}, Count: {result['count']}")
        return response_data
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/query/structured")
async def execute_structured_query(request: StructuredQueryInput):
    """
    Execute a pre-built structured query directly (bypass AI)
    Useful for testing or programmatic access
    """
    try:
        # Convert to dict
        query_dict = request.model_dump(exclude_none=True)
        
        # Validate
        try:
            validated_query = validate_query(query_dict)
        except QueryValidationError as e:
            raise HTTPException(status_code=400, detail=f"Query validation failed: {str(e)}")
        
        # Build MongoDB query
        mongo_query = query_builder.build(validated_query)
        
        if "error" in mongo_query:
            raise HTTPException(status_code=400, detail=mongo_query["error"])
        
        # Execute
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
    """
    Get all tests for a specific patient by name
    """
    try:
        query_dict = {
            "intent": "PATIENT_LOOKUP",
            "patient_name": patient_name
        }
        
        if report_type:
            query_dict["report_type"] = report_type
        
        validated_query = validate_query(query_dict)
        mongo_query = query_builder.build(validated_query)
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
    report_type: Optional[str] = None,
    gender: Optional[str] = None,
    limit: Optional[int] = 100
):
    """
    Get all abnormal test results
    """
    try:
        query_dict = {"intent": "DEFICIENCY"}
        
        if canonical_test:
            query_dict["canonical_test"] = canonical_test
        if report_type:
            query_dict["report_type"] = report_type
        if gender:
            query_dict["gender"] = gender
        if limit:
            query_dict["limit"] = limit
        
        validated_query = validate_query(query_dict)
        mongo_query = query_builder.build(validated_query)
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


@app.get("/api/summary")
async def get_summary(report_type: Optional[str] = None):
    """
    Get overall summary statistics
    """
    try:
        query_dict = {"intent": "SUMMARY"}
        
        if report_type:
            query_dict["report_type"] = report_type
        
        validated_query = validate_query(query_dict)
        mongo_query = query_builder.build(validated_query)
        result = await query_executor.execute(mongo_query)
        
        if not result["success"]:
            raise HTTPException(status_code=500, detail=result["error"])
        
        # Parse faceted results
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
    List all canonical test names and their categories
    """
    from config.canonical_mappings import CANONICAL_TEST_DICTIONARY
    
    return {
        "success": True,
        "tests": CANONICAL_TEST_DICTIONARY
    }


@app.get("/api/patients")
async def get_all_patients():
    """
    Get list of all patients with summary statistics
    """
    try:
        collection = await mongo_manager.get_collection()
        
        # Aggregate to get patient summaries
        pipeline = [
            {
                "$group": {
                    "_id": "$patient_name",
                    "age": {"$first": "$age"},
                    "gender": {"$first": "$gender"},
                    "test_count": {"$sum": 1},
                    "tests": {
                        "$push": {
                            "test_name": "$test_name",
                            "value": "$value",
                            "reference_range": "$reference_range",
                            "is_abnormal": "$is_abnormal",
                            "report_date": "$report_date",
                            "report_type": "$report_type"
                        }
                    }
                }
            },
            {
                "$project": {
                    "name": "$_id",
                    "age": 1,
                    "gender": 1,
                    "test_count": 1,
                    "has_abnormal": {
                        "$anyElementTrue": ["$tests.is_abnormal"]
                    },
                    "latest_date": {"$max": "$tests.report_date"}
                }
            },
            {
                "$sort": {"name": 1}
            }
        ]
        
        patients = await collection.aggregate(pipeline).to_list(None)
        
        return {
            "success": True,
            "count": len(patients),
            "patients": patients
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/patient/{patient_name}/history")
async def get_patient_history(patient_name: str):
    """
    Get complete test history for a patient with all details
    """
    try:
        collection = await mongo_manager.get_collection()
        
        # Get all tests for patient, grouped by date
        pipeline = [
            {
                "$match": {"patient_name": patient_name}
            },
            {
                "$sort": {"report_date": -1}
            },
            {
                "$group": {
                    "_id": {
                        "date": "$report_date",
                        "report_type": "$report_type"
                    },
                    "patient_name": {"$first": "$patient_name"},
                    "age": {"$first": "$age"},
                    "gender": {"$first": "$gender"},
                    "report_date": {"$first": "$report_date"},
                    "report_type": {"$first": "$report_type"},
                    "tests": {
                        "$push": {
                            "test_name": "$raw_test_name",
                            "canonical_test": "$canonical_test",
                            "value": "$value",
                            "unit": "$unit",
                            "reference_range": "$reference_raw",
                            "is_abnormal": "$is_abnormal"
                        }
                    }
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "patient_name": 1,
                    "age": 1,
                    "gender": 1,
                    "report_date": 1,
                    "report_type": 1,
                    "tests": 1,
                    "abnormal_count": {
                        "$size": {
                            "$filter": {
                                "input": "$tests",
                                "as": "test",
                                "cond": {"$eq": ["$$test.is_abnormal", True]}
                            }
                        }
                    },
                    "total_tests": {"$size": "$tests"}
                }
            },
            {
                "$sort": {"report_date": -1}
            }
        ]
        
        history = await collection.aggregate(pipeline).to_list(None)
        
        if not history:
            raise HTTPException(status_code=404, detail=f"No records found for patient: {patient_name}")
        
        # Get summary
        total_tests = sum(h["total_tests"] for h in history)
        total_abnormal = sum(h["abnormal_count"] for h in history)
        
        return {
            "success": True,
            "patient_name": patient_name,
            "age": history[0]["age"],
            "gender": history[0]["gender"],
            "total_reports": len(history),
            "total_tests": total_tests,
            "total_abnormal": total_abnormal,
            "reports": history
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/ocr/upload")
async def upload_and_extract(file: UploadFile = File(...)):
    """
    Upload lab report image and extract structured data
    Returns structured data for user verification before saving to DB
    """
    import tempfile
    import shutil
    from pathlib import Path
    
    try:
        # Validate file type
        allowed_extensions = {'.png', '.jpg', '.jpeg', '.pdf', '.tiff', '.bmp'}
        file_ext = Path(file.filename).suffix.lower()
        
        if file_ext not in allowed_extensions:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid file type. Allowed: {', '.join(allowed_extensions)}"
            )
        
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as tmp_file:
            shutil.copyfileobj(file.file, tmp_file)
            tmp_path = tmp_file.name
        
        try:
            # Import OCR and parsing modules
            from modules.ocr_module import extract_ocr_data
            from modules.ai_parser import get_ai_parser
            from modules.normalization_engine import NormalizationEngine
            
            # Step 1: Extract raw OCR data
            print(f"[OCR] Processing file: {file.filename}")
            ocr_result = extract_ocr_data(tmp_path)
            
            if not ocr_result or not ocr_result.get("success"):
                raise HTTPException(status_code=500, detail="OCR extraction failed")
            
            # Get raw text (it's a list in the new format)
            raw_text_list = ocr_result.get("raw_text", [])
            raw_text = "\n".join(raw_text_list) if isinstance(raw_text_list, list) else str(raw_text_list)
            
            # Step 2: Parse with AI
            print("[OCR] Parsing with AI...")
            ai_parser = get_ai_parser()
            parsed_data = await ai_parser.parse_lab_report(raw_text)
            
            if not parsed_data or "error" in parsed_data:
                raise HTTPException(status_code=500, detail=f"AI parsing failed: {parsed_data.get('error', 'Unknown')}")
            
            # Step 3: Normalize the data
            print("[OCR] Normalizing data...")
            normalizer = NormalizationEngine()
            normalized_tests = []
            
            for test in parsed_data.get("tests", []):
                # Convert AI parser output to normalization engine input format
                raw_test = {
                    "test_name_raw": test.get("test_name", ""),
                    "result_raw": str(test.get("value", "")),
                    "unit_raw": test.get("unit", "") or "",
                    "reference_raw": test.get("reference_range", "") or ""
                }
                normalized = normalizer.normalize_single_test(raw_test)
                if normalized:
                    normalized_tests.append(normalized)
                else:
                    # Keep original if normalization fails
                    normalized_tests.append({
                        "test_name": test.get("test_name", ""),
                        "canonical_name": None,
                        "value": test.get("value"),
                        "unit": test.get("unit"),
                        "reference_range": test.get("reference_range"),
                        "normalization_status": "UNMAPPED"
                    })
            
            # Step 4: Structure for verification
            structured_data = {
                "success": True,
                "filename": file.filename,
                "patient_info": {
                    "patient_name": parsed_data.get("patient_name", ""),
                    "age": parsed_data.get("age"),
                    "gender": parsed_data.get("gender", ""),
                    "report_date": parsed_data.get("report_date")
                },
                "report_type": parsed_data.get("report_type", "UNKNOWN"),
                "tests": normalized_tests,
                "raw_text": raw_text[:500] + "..." if len(raw_text) > 500 else raw_text
            }
            
            return structured_data
            
        finally:
            # Clean up temp file
            Path(tmp_path).unlink(missing_ok=True)
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"[OCR] Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")


@app.post("/api/ocr/save")
async def save_verified_data(data: dict = Body(...)):
    """
    Save verified lab report data to database
    Expects structured data after user verification
    """
    try:
        from db.models import TestDocument
        from datetime import datetime
        import uuid
        
        patient_info = data.get("patient_info", {})
        tests = data.get("tests", [])
        report_type = data.get("report_type", "UNKNOWN")
        
        if not patient_info.get("patient_name"):
            raise HTTPException(status_code=400, detail="Patient name is required")
        
        if not tests:
            raise HTTPException(status_code=400, detail="At least one test is required")
        
        # Generate patient ID
        patient_id = str(uuid.uuid4())
        
        # Parse report date
        report_date = None
        if patient_info.get("report_date"):
            try:
                report_date = datetime.fromisoformat(patient_info["report_date"].replace('Z', '+00:00'))
            except:
                report_date = datetime.now()
        else:
            report_date = datetime.now()
        
        # Create test documents
        documents = []
        for test in tests:
            doc = TestDocument(
                patient_id=patient_id,
                patient_name=patient_info["patient_name"],
                age=patient_info.get("age"),
                gender=patient_info.get("gender"),
                canonical_test=test.get("canonical_test", "UNKNOWN"),
                raw_test_name=test.get("raw_test_name", test.get("test_name", "Unknown")),
                value=test.get("value"),
                value_text=test.get("value_text"),
                unit=test.get("unit", ""),
                value_standard=test.get("value_standard"),
                unit_standard=test.get("unit_standard", ""),
                reference_min=test.get("reference_min"),
                reference_max=test.get("reference_max"),
                reference_raw=test.get("reference_raw"),
                used_global_reference=test.get("used_global_reference", False),
                is_abnormal=test.get("is_abnormal", False),
                abnormal_direction=test.get("abnormal_direction"),
                report_type=report_type,
                report_date=report_date,
                source_image=data.get("filename"),
                created_at=datetime.now()
            )
            documents.append(doc)
        
        # Save to database
        count = await mongo_manager.insert_many(documents)
        
        return {
            "success": True,
            "message": f"Successfully saved {count} test results",
            "patient_name": patient_info["patient_name"],
            "tests_saved": count
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"[OCR Save] Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Save error: {str(e)}")


@app.get("/api/tests/types")
async def get_test_types():
    """
    Get all unique test types (canonical tests) in the database
    """
    try:
        collection = await mongo_manager.get_collection()
        
        # Get all unique canonical tests with counts
        pipeline = [
            {
                "$group": {
                    "_id": "$canonical_test",
                    "count": {"$sum": 1},
                    "example_name": {"$first": "$raw_test_name"}
                }
            },
            {
                "$sort": {"count": -1}
            }
        ]
        
        tests = await collection.aggregate(pipeline).to_list(None)
        
        return {
            "success": True,
            "total_types": len(tests),
            "tests": [
                {
                    "canonical_name": t["_id"],
                    "example_name": t["example_name"],
                    "count": t["count"]
                }
                for t in tests
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/patients/list")
async def list_all_patients(
    gender: Optional[str] = Query(None, description="Filter by gender: M, F, Male, Female"),
    has_abnormal: Optional[bool] = Query(None, description="Filter by abnormal test results"),
    test_type: Optional[str] = Query(None, description="Filter by test type (canonical name)"),
    report_type: Optional[str] = Query(None, description="Filter by report type: CBC, LIVER, THYROID, etc.")
):
    """
    List all patients with optional filters:
    - gender: Filter by M/F
    - has_abnormal: true/false for abnormal results
    - test_type: Filter patients who have this test (e.g., HEMOGLOBIN_CBC)
    - report_type: Filter by report type (e.g., THYROID, CBC)
    """
    try:
        collection = await mongo_manager.get_collection()
        
        # Build match query
        match_query = {}
        
        if gender:
            # Normalize gender input
            gender_upper = gender.upper()
            if gender_upper in ['M', 'MALE']:
                match_query["gender"] = "M"
            elif gender_upper in ['F', 'FEMALE']:
                match_query["gender"] = "F"
        
        if test_type:
            match_query["canonical_test"] = test_type
        
        if report_type:
            match_query["report_type"] = report_type.upper()
        
        if has_abnormal is not None:
            match_query["is_abnormal"] = has_abnormal
        
        # Aggregate to get unique patients with their stats
        pipeline = [
            {"$match": match_query} if match_query else {"$match": {}},
            {
                "$group": {
                    "_id": "$patient_name",
                    "age": {"$first": "$age"},
                    "gender": {"$first": "$gender"},
                    "test_count": {"$sum": 1},
                    "abnormal_count": {
                        "$sum": {"$cond": [{"$eq": ["$is_abnormal", True]}, 1, 0]}
                    },
                    "report_types": {"$addToSet": "$report_type"}
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "name": "$_id",
                    "age": 1,
                    "gender": 1,
                    "test_count": 1,
                    "abnormal_count": 1,
                    "has_abnormal": {"$gt": ["$abnormal_count", 0]},
                    "report_types": 1
                }
            },
            {"$sort": {"name": 1}}
        ]
        
        patients = await collection.aggregate(pipeline).to_list(None)
        
        # Build filter description
        filters_applied = []
        if gender:
            filters_applied.append(f"Gender: {gender.upper()}")
        if has_abnormal is not None:
            filters_applied.append(f"Has abnormal: {has_abnormal}")
        if test_type:
            filters_applied.append(f"Test type: {test_type}")
        if report_type:
            filters_applied.append(f"Report type: {report_type}")
        
        return {
            "success": True,
            "count": len(patients),
            "filters": filters_applied if filters_applied else ["None - showing all patients"],
            "patients": patients
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/reports/types")
async def get_report_types():
    """
    Get all unique report types in the database
    """
    try:
        collection = await mongo_manager.get_collection()
        
        # Get unique report types with counts
        pipeline = [
            {
                "$group": {
                    "_id": "$report_type",
                    "count": {"$sum": 1},
                    "patients": {"$addToSet": "$patient_name"}
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "report_type": "$_id",
                    "test_count": "$count",
                    "patient_count": {"$size": "$patients"}
                }
            },
            {"$sort": {"test_count": -1}}
        ]
        
        reports = await collection.aggregate(pipeline).to_list(None)
        
        return {
            "success": True,
            "total_types": len(reports),
            "report_types": reports
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Run with: uvicorn api:app --reload
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
