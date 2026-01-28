# -*- coding: utf-8 -*-
"""
Main Application Entry Point
Complete Lab Report Analytics Pipeline
"""
import os
# Set PaddlePaddle environment variables BEFORE any imports (for OCR)
os.environ['FLAGS_use_mkldnn'] = '0'
os.environ['FLAGS_allocator_strategy'] = 'naive_best_fit'
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'

import sys
import json
import argparse
from pathlib import Path
from datetime import datetime

# Add project root to path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

from modules.ocr_module import process_image_file
from modules.normalization_engine import NormalizationEngine
from modules.query_engine import QueryEngine
from modules.response_generator import ResponseGenerator


def process_single_image(image_path: str, use_ai: bool = False, verbose: bool = True) -> dict:
    """
    Process a single lab report image through the full pipeline
    
    Steps:
    1. OCR extraction (raw)
    2. Normalization (canonical)
    """
    if verbose:
        print(f"\n{'='*60}")
        print(f"Processing: {os.path.basename(image_path)}")
        print('='*60)
    
    # Step 1: OCR Extraction
    if verbose:
        print("\n[1/2] Extracting text via OCR...")
    
    raw_ocr = process_image_file(image_path)
    
    if not raw_ocr.get("success"):
        if verbose:
            print(f"  ❌ OCR failed: {raw_ocr.get('error', 'Unknown error')}")
        return {"success": False, "error": raw_ocr.get("error")}
    
    if verbose:
        print(f"  ✓ Extracted {raw_ocr.get('text_segments_count', 0)} text segments")
        print(f"  ✓ Found {raw_ocr.get('tests_extracted_count', 0)} potential test entries")
    
    # Step 2: Normalization
    if verbose:
        print("\n[2/2] Normalizing to canonical format...")
    
    normalizer = NormalizationEngine(use_ai_fallback=use_ai)
    normalized = normalizer.normalize(raw_ocr)
    
    if verbose:
        print(f"  ✓ Normalized {normalized.get('total_tests', 0)} tests")
        print(f"  ✓ Report types: {', '.join(normalized.get('report_types', []))}")
        
        if normalized.get("unmapped_tests", 0) > 0:
            print(f"  ⚠ {normalized['unmapped_tests']} tests could not be mapped to canonical names")
    
    return {
        "success": True,
        "raw_ocr": raw_ocr,
        "normalized": normalized
    }


def process_folder(folder_path: str, use_ai: bool = False, output_file: str = None) -> dict:
    """
    Process all images in a folder
    """
    if not os.path.exists(folder_path):
        print(f"Error: Folder not found: {folder_path}")
        return {"success": False, "error": "Folder not found"}
    
    results = []
    image_extensions = ('.png', '.jpg', '.jpeg', '.bmp', '.tiff')
    
    print(f"\nScanning folder: {folder_path}")
    
    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.lower().endswith(image_extensions):
                image_path = os.path.join(root, file)
                result = process_single_image(image_path, use_ai=use_ai)
                results.append({
                    "file": file,
                    "path": image_path,
                    **result
                })
    
    # Summary
    success_count = sum(1 for r in results if r.get("success"))
    total_tests = sum(r.get("normalized", {}).get("total_tests", 0) for r in results if r.get("success"))
    
    print(f"\n{'='*60}")
    print("PROCESSING SUMMARY")
    print('='*60)
    print(f"Total files processed: {len(results)}")
    print(f"Successful: {success_count}")
    print(f"Failed: {len(results) - success_count}")
    print(f"Total tests extracted: {total_tests}")
    
    # Save to file if specified
    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, default=str)
        print(f"\nResults saved to: {output_file}")
    
    return {
        "success": True,
        "total_files": len(results),
        "successful": success_count,
        "total_tests": total_tests,
        "results": results
    }


def interactive_query_mode(use_ai: bool = False):
    """
    Interactive query mode for testing NLP queries
    """
    print("\n" + "="*60)
    print("INTERACTIVE QUERY MODE")
    print("="*60)
    print("Enter natural language queries to test the query engine.")
    print("Type 'exit' or 'quit' to exit.\n")
    
    query_engine = QueryEngine()
    response_generator = ResponseGenerator(use_ai=use_ai)
    
    while True:
        try:
            query = input("\n🔍 Query: ").strip()
            
            if query.lower() in ['exit', 'quit', 'q']:
                print("Goodbye!")
                break
            
            if not query:
                continue
            
            # Process query
            result = query_engine.process_query(query)
            
            print(f"\n📊 Parsed Intent: {result.get('parsed_query', {}).get('intent')}")
            print(f"📋 Test Detected: {result.get('parsed_query', {}).get('test_name', 'None')}")
            print(f"🗄️ MongoDB Query: {json.dumps(result.get('mongo_query', {}).get('filter', {}), default=str)}")
            
            if result.get("validation", {}).get("warnings"):
                print(f"⚠️ Warnings: {', '.join(result['validation']['warnings'])}")
            
            # Generate response (with mock data for demo)
            if not result.get("results"):
                result["results"] = []  # Empty results for demo
            
            response = response_generator.generate(result)
            print(f"\n💬 Response: {response['natural_response']}")
            
        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Lab Report Analytics - OCR extraction and NLP querying"
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Process single image
    process_parser = subparsers.add_parser('process', help='Process a single image')
    process_parser.add_argument('image_path', help='Path to the image file')
    process_parser.add_argument('--ai', action='store_true', help='Use AI for unknown test mapping')
    process_parser.add_argument('--output', '-o', help='Output file for results (JSON)')
    
    # Process folder
    folder_parser = subparsers.add_parser('folder', help='Process all images in a folder')
    folder_parser.add_argument('folder_path', help='Path to the folder')
    folder_parser.add_argument('--ai', action='store_true', help='Use AI for unknown test mapping')
    folder_parser.add_argument('--output', '-o', help='Output file for results (JSON)')
    
    # Interactive query mode
    query_parser = subparsers.add_parser('query', help='Interactive query mode')
    query_parser.add_argument('--ai', action='store_true', help='Use AI for response generation')
    
    # API server
    api_parser = subparsers.add_parser('api', help='Start the API server')
    api_parser.add_argument('--host', default='0.0.0.0', help='Host address')
    api_parser.add_argument('--port', type=int, default=8000, help='Port number')
    
    args = parser.parse_args()
    
    if args.command == 'process':
        result = process_single_image(args.image_path, use_ai=args.ai)
        
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, default=str)
            print(f"\nResults saved to: {args.output}")
        else:
            print("\n" + "="*60)
            print("NORMALIZED RESULTS")
            print("="*60)
            normalized = result.get("normalized", {})
            for test in normalized.get("normalized_tests", []):
                status = "❌" if test.get("is_abnormal") else "✓"
                print(f"  {status} {test.get('canonical_test')}: {test.get('value')} {test.get('unit', '')}")
    
    elif args.command == 'folder':
        process_folder(args.folder_path, use_ai=args.ai, output_file=args.output)
    
    elif args.command == 'query':
        interactive_query_mode(use_ai=args.ai)
    
    elif args.command == 'api':
        import uvicorn
        uvicorn.run("api:app", host=args.host, port=args.port, reload=True)
    
    else:
        # Default: show help or run demo
        print("\n" + "="*60)
        print("LAB REPORT ANALYTICS SYSTEM")
        print("="*60)
        print("\nUsage:")
        print("  python main.py process <image_path>  - Process a single image")
        print("  python main.py folder <folder_path>  - Process all images in folder")
        print("  python main.py query                 - Interactive query mode")
        print("  python main.py api                   - Start API server")
        print("\nExamples:")
        print("  python main.py process images/cbc/report1.png")
        print("  python main.py folder images/cbc --output results.json")
        print("  python main.py api --port 8080")
        
        # Demo with images folder if exists
        images_folder = os.path.join(PROJECT_ROOT, "images")
        if os.path.exists(images_folder):
            print(f"\n💡 Tip: Found images folder at {images_folder}")
            print(f"   Try: python main.py folder {images_folder}")


if __name__ == "__main__":
    main()
