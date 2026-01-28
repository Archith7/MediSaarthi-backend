# -*- coding: utf-8 -*-
"""
OCR Module - Extracts raw text from lab report images/PDFs
Output is RAW and UNTRUSTED - no normalization happens here
"""
import os
import re
import warnings
import logging
import cv2
import numpy as np
from datetime import datetime
import uuid

# Suppress warnings
warnings.filterwarnings("ignore")
logging.getLogger("ppocr").setLevel(logging.ERROR)
logging.getLogger("paddle").setLevel(logging.ERROR)
os.environ["FLAGS_allocator_strategy"] = 'naive_best_fit'
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'
os.environ['FLAGS_use_mkldnn'] = '0'

# Lazy initialization of PaddleOCR
_ocr = None
_ocr_available = None

def is_ocr_available():
    """Check if PaddleOCR is available"""
    global _ocr_available
    if _ocr_available is None:
        try:
            from paddleocr import PaddleOCR
            _ocr_available = True
        except ImportError:
            _ocr_available = False
            print("[OCR] PaddleOCR not available - OCR features will be disabled")
    return _ocr_available

def get_ocr():
    """Lazy-load PaddleOCR instance"""
    global _ocr
    if not is_ocr_available():
        raise ImportError("PaddleOCR is not installed. OCR features are disabled in this deployment.")
    if _ocr is None:
        from paddleocr import PaddleOCR
        _ocr = PaddleOCR(use_angle_cls=True, lang='en')
    return _ocr


def deskew_image(image):
    """Detect and correct image skew/rotation"""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
    coords = np.column_stack(np.where(thresh > 0))
    
    if len(coords) < 5:
        return image, 0
    
    angle = cv2.minAreaRect(coords)[-1]
    
    if angle < -45:
        angle = 90 + angle
    elif angle > 45:
        angle = angle - 90
    
    if abs(angle) > 0.5:
        (h, w) = image.shape[:2]
        center = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        rotated = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
        return rotated, angle
    
    return image, 0


def preprocess_image(image_path):
    """Comprehensive image preprocessing for better OCR accuracy"""
    img = cv2.imread(image_path)
    
    if img is None:
        return image_path, {}
    
    preprocessing_info = {}
    
    # Deskew
    img, rotation_angle = deskew_image(img)
    if abs(rotation_angle) > 0.5:
        preprocessing_info['rotation_corrected'] = f"{rotation_angle:.2f}°"
    
    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Noise removal
    denoised = cv2.fastNlMeansDenoising(gray, None, 10, 7, 21)
    
    # Contrast enhancement (CLAHE)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(denoised)
    
    # Sharpening
    kernel = np.array([[-1,-1,-1], [-1, 9,-1], [-1,-1,-1]])
    sharpened = cv2.filter2D(enhanced, -1, kernel)
    
    # Binarization
    _, binary = cv2.threshold(sharpened, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    
    # Save preprocessed image temporarily
    temp_path = image_path.replace('.', '_preprocessed.')
    cv2.imwrite(temp_path, binary)
    
    return temp_path, preprocessing_info


def extract_raw_text(image_path):
    """
    Extract raw text from image using PaddleOCR
    Returns list of text lines with positions
    """
    # Preprocess image
    preprocessed_path, _ = preprocess_image(image_path)
    
    # Perform OCR
    ocr = get_ocr()
    result = ocr.ocr(preprocessed_path)
    
    # Clean up temp file
    if preprocessed_path != image_path and os.path.exists(preprocessed_path):
        try:
            os.remove(preprocessed_path)
        except:
            pass
    
    text_lines = []
    if result and result[0]:
        for line in result[0]:
            if line[1]:
                text = line[1][0]
                confidence = line[1][1]
                position = line[0]
                text_lines.append({
                    "text": text,
                    "confidence": confidence,
                    "position": position
                })
    
    return text_lines


def parse_patient_info(text_lines):
    """
    Extract patient information from OCR text
    Returns RAW, UNTRUSTED data
    """
    full_text = " ".join([line["text"] for line in text_lines]).upper()
    
    patient_info = {
        "patient_name": None,
        "age": None,
        "gender": None,
        "patient_id": None,
        "report_date": None
    }
    
    # Extract patient name (common patterns)
    name_patterns = [
        r"(?:PATIENT\s*NAME|NAME)\s*[:\-]?\s*([A-Z][A-Z\s\.]+)",
        r"(?:MR\.|MRS\.|MS\.|MASTER)\s*([A-Z][A-Z\s\.]+)",
    ]
    for pattern in name_patterns:
        match = re.search(pattern, full_text)
        if match:
            patient_info["patient_name"] = match.group(1).strip()
            break
    
    # Extract age
    age_patterns = [
        r"AGE\s*[:\-]?\s*(\d+)\s*(?:YRS?|YEARS?)?",
        r"(\d+)\s*(?:YRS?|YEARS?)\s*(?:OLD)?",
        r"AGE\s*/\s*(?:SEX|GENDER)\s*[:\-]?\s*(\d+)"
    ]
    for pattern in age_patterns:
        match = re.search(pattern, full_text)
        if match:
            try:
                patient_info["age"] = int(match.group(1))
                break
            except:
                pass
    
    # Extract gender
    gender_patterns = [
        r"(?:SEX|GENDER)\s*[:\-]?\s*(MALE|FEMALE|M|F)",
        r"AGE\s*/\s*(?:SEX|GENDER)\s*[:\-]?\s*\d+\s*/?\s*(MALE|FEMALE|M|F)",
    ]
    for pattern in gender_patterns:
        match = re.search(pattern, full_text)
        if match:
            gender = match.group(1).strip()
            if gender in ["M", "MALE"]:
                patient_info["gender"] = "Male"
            elif gender in ["F", "FEMALE"]:
                patient_info["gender"] = "Female"
            break
    
    # Extract date
    date_patterns = [
        r"(?:DATE|REPORT\s*DATE|COLLECTED)\s*[:\-]?\s*(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})",
        r"(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{4})"
    ]
    for pattern in date_patterns:
        match = re.search(pattern, full_text)
        if match:
            patient_info["report_date"] = match.group(1)
            break
    
    return patient_info


def parse_test_results(text_lines):
    """
    Extract test results from OCR text
    Returns RAW, UNTRUSTED test data
    """
    tests = []
    full_text = " ".join([line["text"] for line in text_lines])
    
    # Common test result patterns
    # Pattern: TEST_NAME VALUE UNIT REFERENCE
    test_patterns = [
        # Pattern: Test name, value, unit, reference range
        r"([A-Z][A-Z\s\.\(\)]+?)\s+(\d+[\.,]?\d*)\s*([\w\/\%]+)?\s*(\d+[\.,]?\d*\s*[\-–]\s*\d+[\.,]?\d*)?",
    ]
    
    # Process each line individually for better accuracy
    for line_info in text_lines:
        line = line_info["text"].strip()
        
        # Skip very short lines or headers
        if len(line) < 3:
            continue
        
        # Try to extract test data from line
        test_entry = extract_test_from_line(line)
        if test_entry:
            tests.append(test_entry)
    
    return tests


def extract_test_from_line(line):
    """
    Extract a single test result from a line
    Returns RAW data without normalization
    """
    # Clean the line
    line = line.strip()
    
    # Skip header-like lines
    skip_keywords = ["PARAMETER", "TEST NAME", "RESULT", "UNIT", "REFERENCE", 
                     "NORMAL", "RANGE", "VALUE", "REPORT", "LAB", "HOSPITAL"]
    if any(keyword in line.upper() for keyword in skip_keywords) and len(line) < 30:
        return None
    
    # Pattern to extract: test_name, value, unit, reference
    # Flexible pattern to handle various formats
    patterns = [
        # Pattern: Name Value Unit Min-Max
        r"^([A-Za-z][A-Za-z\s\.\(\)\-]+?)\s+(\d+[\.,]?\d*)\s*([\w\/\%\^]+)?\s*([\d\.\,]+\s*[\-–]\s*[\d\.\,]+)?",
        # Pattern: Name: Value
        r"^([A-Za-z][A-Za-z\s\.\(\)\-]+?)\s*[:\-]\s*(\d+[\.,]?\d*)\s*([\w\/\%\^]+)?",
    ]
    
    for pattern in patterns:
        match = re.match(pattern, line)
        if match:
            groups = match.groups()
            test_name = groups[0].strip() if groups[0] else None
            result = groups[1].strip() if len(groups) > 1 and groups[1] else None
            unit = groups[2].strip() if len(groups) > 2 and groups[2] else None
            reference = groups[3].strip() if len(groups) > 3 and groups[3] else None
            
            # Validate that we have at least a test name and result
            if test_name and result and len(test_name) > 1:
                return {
                    "test_name_raw": test_name,
                    "result_raw": result,
                    "unit_raw": unit,
                    "reference_raw": reference
                }
    
    return None


def extract_ocr_data(image_path):
    """
    Main OCR extraction function
    
    Input: Image/PDF path
    Output: Raw OCR JSON (UNTRUSTED, not normalized)
    """
    # Extract raw text
    text_lines = extract_raw_text(image_path)
    
    if not text_lines:
        return {
            "success": False,
            "error": "No text extracted from image",
            "raw_text": [],
            "patient_info": {},
            "tests": [],
            "source_image": os.path.basename(image_path)
        }
    
    # Parse patient info
    patient_info = parse_patient_info(text_lines)
    
    # Parse test results
    tests = parse_test_results(text_lines)
    
    # Build raw OCR output (UNTRUSTED)
    raw_ocr_output = {
        "success": True,
        "extraction_timestamp": datetime.utcnow().isoformat(),
        "patient_name": patient_info.get("patient_name"),
        "age": patient_info.get("age"),
        "gender": patient_info.get("gender"),
        "report_date_raw": patient_info.get("report_date"),
        "tests": tests,
        "raw_text": [line["text"] for line in text_lines],
        "source_image": os.path.basename(image_path),
        "text_segments_count": len(text_lines),
        "tests_extracted_count": len(tests)
    }
    
    return raw_ocr_output


def process_image_file(image_path):
    """
    Process a single image file and return raw OCR data
    """
    if not os.path.exists(image_path):
        return {
            "success": False,
            "error": f"File not found: {image_path}"
        }
    
    print(f"[OCR] Processing: {os.path.basename(image_path)}")
    
    try:
        result = extract_ocr_data(image_path)
        print(f"[OCR] Extracted {result.get('tests_extracted_count', 0)} test entries")
        return result
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "source_image": os.path.basename(image_path)
        }


# For standalone testing
if __name__ == "__main__":
    import json
    
    # Test with images in the images folder
    images_folder = "images"
    
    if os.path.exists(images_folder):
        for root, dirs, files in os.walk(images_folder):
            for file in files:
                if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                    image_path = os.path.join(root, file)
                    result = process_image_file(image_path)
                    print(f"\n{'='*60}")
                    print(f"File: {file}")
                    print(f"{'='*60}")
                    print(json.dumps(result, indent=2, default=str))
                    print()
                    break  # Just test first image
