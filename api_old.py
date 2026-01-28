# -*- coding: utf-8 -*-
"""
Lab Report Analytics API
FastAPI endpoints for the complete data flow
"""
import os
import sys
import json
import shutil
import logging
from datetime import datetime
from typing import List, Optional
from pathlib import Path

from fastapi import FastAPI, File, UploadFile, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from modules.ocr_module import process_image_file
from modules.normalization_engine import NormalizationEngine
from modules.query_engine import QueryEngine
from modules.response_generator import ResponseGenerator
from config.settings import (
    UPLOAD_FOLDER,
    ALLOWED_EXTENSIONS,
    MONGODB_URI,
    MONGODB_DATABASE,
    OPENAI_API_KEY
)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI(
    title="Lab Report Analytics API",
    description="OCR-powered lab report extraction and natural language querying",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialize components
normalizer = NormalizationEngine(use_ai_fallback=bool(OPENAI_API_KEY), openai_api_key=OPENAI_API_KEY)
query_engine = QueryEngine()
response_generator = ResponseGenerator(openai_api_key=OPENAI_API_KEY, use_ai=bool(OPENAI_API_KEY))

# Database manager (lazy initialization)
db_manager = None


def get_db():
    """Get or create database manager"""
    global db_manager
    if db_manager is None:
        try:
            from modules.database import get_db_manager
            db_manager = get_db_manager(MONGODB_URI, MONGODB_DATABASE)
            query_engine.db = db_manager
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            return None
    return db_manager


# Request/Response Models
class QueryRequest(BaseModel):
    query: str
    use_ai_response: bool = True


class QueryResponse(BaseModel):
    success: bool
    natural_response: str
    data: List[dict]
    summary: dict
    query_info: dict


class ProcessingResult(BaseModel):
    success: bool
    message: str
    raw_ocr: dict
    normalized: dict
    stored: dict = None


# Health check
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    db_status = "connected" if get_db() else "disconnected"
    return {
        "status": "healthy",
        "database": db_status,
        "timestamp": datetime.utcnow().isoformat()
    }


# Upload and process lab report
@app.post("/api/upload", response_model=ProcessingResult)
async def upload_lab_report(
    file: UploadFile = File(...),
    store_in_db: bool = Query(True, description="Store results in database")
):
    """
    Upload a lab report image/PDF and process it through the full pipeline:
    1. OCR extraction (raw)
    2. Normalization (canonical)
    3. Storage (MongoDB)
    """
    # Validate file type
    file_ext = file.filename.split('.')[-1].lower() if '.' in file.filename else ''
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"File type not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    # Save uploaded file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_filename = f"{timestamp}_{file.filename}"
    file_path = os.path.join(UPLOAD_FOLDER, safe_filename)
    
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")
    
    try:
        # Step 1: OCR Extraction
        logger.info(f"Processing file: {file.filename}")
        raw_ocr = process_image_file(file_path)
        
        if not raw_ocr.get("success"):
            return ProcessingResult(
                success=False,
                message=f"OCR extraction failed: {raw_ocr.get('error', 'Unknown error')}",
                raw_ocr=raw_ocr,
                normalized={},
                stored={}
            )
        
        # Step 2: Normalization
        normalized = normalizer.normalize(raw_ocr)
        
        # Step 3: Storage (optional)
        stored = {}
        if store_in_db:
            db = get_db()
            if db:
                stored = db.store_normalized_result(normalized)
            else:
                stored = {"success": False, "error": "Database not available"}
        
        return ProcessingResult(
            success=True,
            message=f"Successfully processed {file.filename}",
            raw_ocr=raw_ocr,
            normalized=normalized,
            stored=stored
        )
        
    except Exception as e:
        logger.error(f"Processing error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        # Clean up uploaded file (optional - keep for debugging)
        # os.remove(file_path)
        pass


# Process existing image
@app.post("/api/process")
async def process_existing_image(image_path: str):
    """
    Process an existing image file on the server
    """
    if not os.path.exists(image_path):
        raise HTTPException(status_code=404, detail=f"File not found: {image_path}")
    
    try:
        # Step 1: OCR
        raw_ocr = process_image_file(image_path)
        
        # Step 2: Normalize
        normalized = normalizer.normalize(raw_ocr)
        
        return {
            "success": True,
            "raw_ocr": raw_ocr,
            "normalized": normalized
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Natural language query
@app.post("/api/query", response_model=QueryResponse)
async def natural_language_query(request: QueryRequest):
    """
    Process a natural language query about lab results
    
    Examples:
    - "Show me all hemoglobin results below 12"
    - "What are John's abnormal CBC results?"
    - "Average platelet count in the last 30 days"
    """
    try:
        # Process query through query engine
        query_result = query_engine.process_query(request.query)
        
        # Generate polished response
        response = response_generator.generate(query_result)
        
        return QueryResponse(
            success=response["success"],
            natural_response=response["natural_response"],
            data=response["data"],
            summary=response["summary"],
            query_info={
                "original_query": request.query,
                "parsed_intent": query_result.get("parsed_query", {}).get("intent"),
                "test_detected": query_result.get("parsed_query", {}).get("test_name"),
                "mongo_query": query_result.get("mongo_query", {}).get("filter", {})
            }
        )
        
    except Exception as e:
        logger.error(f"Query error: {str(e)}")
        return QueryResponse(
            success=False,
            natural_response=f"Error processing query: {str(e)}",
            data=[],
            summary={},
            query_info={"error": str(e)}
        )


# Get all patients
@app.get("/api/patients")
async def get_patients(limit: int = 100):
    """Get list of all patients"""
    db = get_db()
    if not db:
        raise HTTPException(status_code=503, detail="Database not available")
    
    patients = list(db.patients.find({}, {"_id": 1, "name": 1, "age": 1, "gender": 1}).limit(limit))
    for p in patients:
        p["_id"] = str(p["_id"])
    
    return {"patients": patients, "count": len(patients)}


# Get patient history
@app.get("/api/patients/{patient_id}/history")
async def get_patient_history(patient_id: str, test_name: str = None):
    """Get all lab results for a specific patient"""
    db = get_db()
    if not db:
        raise HTTPException(status_code=503, detail="Database not available")
    
    results = db.get_patient_history(patient_id, test_name)
    return {"patient_id": patient_id, "results": results, "count": len(results)}


# Get abnormal results
@app.get("/api/abnormal")
async def get_abnormal_results(patient_id: str = None, limit: int = 100):
    """Get all abnormal results, optionally filtered by patient"""
    db = get_db()
    if not db:
        raise HTTPException(status_code=503, detail="Database not available")
    
    results = db.get_abnormal_results(patient_id)[:limit]
    return {"results": results, "count": len(results)}


# Get test statistics
@app.get("/api/statistics/{test_name}")
async def get_test_statistics(test_name: str):
    """Get statistics for a specific test"""
    db = get_db()
    if not db:
        raise HTTPException(status_code=503, detail="Database not available")
    
    stats = db.get_test_statistics(test_name)
    return stats


# Batch process images in a folder
@app.post("/api/batch-process")
async def batch_process_folder(folder_path: str, store_in_db: bool = True):
    """
    Process all images in a folder
    """
    if not os.path.exists(folder_path):
        raise HTTPException(status_code=404, detail=f"Folder not found: {folder_path}")
    
    results = []
    image_extensions = ('.png', '.jpg', '.jpeg', '.bmp', '.tiff')
    
    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.lower().endswith(image_extensions):
                image_path = os.path.join(root, file)
                
                try:
                    # Process image
                    raw_ocr = process_image_file(image_path)
                    normalized = normalizer.normalize(raw_ocr)
                    
                    stored = {}
                    if store_in_db:
                        db = get_db()
                        if db:
                            stored = db.store_normalized_result(normalized)
                    
                    results.append({
                        "file": file,
                        "success": True,
                        "tests_extracted": normalized.get("total_tests", 0),
                        "stored": stored.get("success", False)
                    })
                    
                except Exception as e:
                    results.append({
                        "file": file,
                        "success": False,
                        "error": str(e)
                    })
    
    success_count = sum(1 for r in results if r["success"])
    
    return {
        "total_files": len(results),
        "successful": success_count,
        "failed": len(results) - success_count,
        "results": results
    }


# Error handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc), "type": type(exc).__name__}
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
