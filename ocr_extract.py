# -*- coding: utf-8 -*-
import os
import logging
import warnings
import cv2
import numpy as np
from PIL import Image
from paddleocr import PaddleOCR

# Suppress unwanted logs and warnings
warnings.filterwarnings("ignore")
logging.getLogger("ppocr").setLevel(logging.ERROR)
logging.getLogger("paddle").setLevel(logging.ERROR)
logging.getLogger().setLevel(logging.ERROR)
os.environ["FLAGS_allocator_strategy"] = 'naive_best_fit'
os.environ['CUDA_VISIBLE_DEVICES'] = ''  # Force CPU to avoid CUDA warnings
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'  # Fix OpenMP issue
os.environ['FLAGS_use_mkldnn'] = '0'  # Disable OneDNN to fix PIR attribute error
os.environ['PADDLE_DISABLE_PIR'] = '1'  # Disable PIR to avoid attribute conversion issues

# Lazy initialization of PaddleOCR
_ocr = None

def get_ocr():
    """Lazy-load PaddleOCR instance"""
    global _ocr
    if _ocr is None:
        _ocr = PaddleOCR(use_angle_cls=True, lang='en')
    return _ocr

def deskew_image(image):
    """Detect and correct image skew/rotation"""
    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Apply binary threshold
    thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
    
    # Find contours
    coords = np.column_stack(np.where(thresh > 0))
    
    if len(coords) < 5:
        return image, 0
    
    # Calculate minimum area rectangle
    angle = cv2.minAreaRect(coords)[-1]
    
    # Adjust angle
    if angle < -45:
        angle = 90 + angle
    elif angle > 45:
        angle = angle - 90
    
    # Only rotate if angle is significant (more than 0.5 degrees)
    if abs(angle) > 0.5:
        (h, w) = image.shape[:2]
        center = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        rotated = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
        return rotated, angle
    
    return image, 0

def preprocess_image(image_path):
    """
    Comprehensive image preprocessing for better OCR accuracy:
    - Orientation correction
    - Noise removal
    - Contrast enhancement
    - Sharpening
    """
    # Read image
    img = cv2.imread(image_path)
    
    if img is None:
        return image_path, {}
    
    preprocessing_info = {}
    
    # 1. Deskew/correct rotation
    img, rotation_angle = deskew_image(img)
    if abs(rotation_angle) > 0.5:
        preprocessing_info['rotation_corrected'] = f"{rotation_angle:.2f}°"
    
    # 2. Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # 3. Noise removal
    denoised = cv2.fastNlMeansDenoising(gray, None, 10, 7, 21)
    preprocessing_info['noise_removal'] = 'Applied'
    
    # 4. Contrast enhancement using CLAHE (Contrast Limited Adaptive Histogram Equalization)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(denoised)
    preprocessing_info['contrast_enhanced'] = 'CLAHE'
    
    # 5. Sharpening
    kernel = np.array([[-1,-1,-1],
                       [-1, 9,-1],
                       [-1,-1,-1]])
    sharpened = cv2.filter2D(enhanced, -1, kernel)
    preprocessing_info['sharpening'] = 'Applied'
    
    # 6. Binarization (Otsu's method)
    _, binary = cv2.threshold(sharpened, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    preprocessing_info['binarization'] = 'Otsu'
    
    # Save preprocessed image temporarily
    temp_path = image_path.replace('.', '_preprocessed.')
    cv2.imwrite(temp_path, binary)
    
    return temp_path, preprocessing_info

def extract_text_from_image(image_path):
    """Extract text from image using OCR with preprocessing"""
    print(f"\n{'='*60}")
    print(f"Processing: {os.path.basename(image_path)}")
    print(f"{'='*60}")
    
    # Preprocess image
    preprocessed_path, preprocessing_info = preprocess_image(image_path)
    
    # Show preprocessing applied
    if preprocessing_info:
        print("[Preprocessing Applied]")
        for key, value in preprocessing_info.items():
            print(f"  - {key.replace('_', ' ').title()}: {value}")
    
    # Perform OCR on preprocessed image
    ocr = get_ocr()
    result = ocr.ocr(preprocessed_path)
    text_list = []
    
    if result and result[0]:
        for line in result[0]:
            if line[1]:
                text = line[1][0]
                text_list.append(text)
    
    # Clean up temporary preprocessed file
    if preprocessed_path != image_path and os.path.exists(preprocessed_path):
        try:
            os.remove(preprocessed_path)
        except:
            pass
    
    # Combine all extracted text
    extracted_text = " ".join(text_list)
    
    # Print extraction info
    print(f"Extracted {len(text_list)} text segments")
    print(f"Total text length: {len(extracted_text)} characters")
    print(f"\n{'='*60}")
    print("EXTRACTED TEXT:")
    print(f"{'='*60}")
    print(extracted_text)
    print(f"{'='*60}\n")
    
    return extracted_text

def process_images_folder(images_folder="images"):
    """Process all images in the images folder"""
    # Get the absolute path
    script_dir = os.path.dirname(os.path.abspath(__file__))
    images_path = os.path.join(script_dir, images_folder)
    
    if not os.path.exists(images_path):
        print(f"[ERROR] Images folder not found: {images_path}")
        return
    
    print(f"[INFO] Scanning folder: {images_path}")
    
    # Supported image formats
    supported_formats = ('.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.pdf')
    
    # Find all image files recursively
    image_files = []
    for root, dirs, files in os.walk(images_path):
        for file in files:
            if file.lower().endswith(supported_formats):
                image_files.append(os.path.join(root, file))
    
    if not image_files:
        print(f"[WARNING] No images found in {images_path}")
        return
    
    print(f"[INFO] Found {len(image_files)} image(s)")
    print()
    
    # Process each image
    for image_file in image_files:
        try:
            extract_text_from_image(image_file)
        except Exception as e:
            print(f"[ERROR] Failed to process {image_file}: {str(e)}")
            print()

if __name__ == "__main__":
    print("[INFO] Starting OCR Text Extraction...")
    print("[INFO] Using images from /images folder")
    print()
    
    process_images_folder("images")
    
    print("[INFO] OCR extraction completed!")
