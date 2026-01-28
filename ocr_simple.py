# -*- coding: utf-8 -*-
import os
import warnings
import logging
from paddleocr import PaddleOCR

# Suppress warnings
warnings.filterwarnings("ignore")
logging.getLogger("ppocr").setLevel(logging.ERROR)
logging.getLogger("paddle").setLevel(logging.ERROR)
os.environ["FLAGS_allocator_strategy"] = 'naive_best_fit'
os.environ['FLAGS_use_mkldnn'] = '0'  # Disable OneDNN to fix PIR attribute error
os.environ['PADDLE_DISABLE_PIR'] = '1'  # Disable PIR to avoid attribute conversion issues
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'

# Lazy initialization of PaddleOCR
_ocr = None

def get_ocr():
    """Lazy-load PaddleOCR instance"""
    global _ocr
    if _ocr is None:
        print("[INFO] Initializing PaddleOCR...")
        _ocr = PaddleOCR(use_angle_cls=True, lang='en')
        print("[INFO] PaddleOCR initialized successfully!\n")
    return _ocr

def extract_text_from_image(image_path):
    """Extract and print text from an image"""
    print(f"{'='*60}")
    print(f"Processing: {os.path.basename(image_path)}")
    print(f"{'='*60}")
    
    try:
        ocr = get_ocr()
        result = ocr.ocr(image_path)
        
        if result and result[0]:
            print(f"\n[EXTRACTED TEXT]:\n")
            for line in result[0]:
                if line[1]:
                    text = line[1][0]
                    print(f"{text}")
            print(f"\n[INFO] Extracted {len(result[0])} text lines\n")
        else:
            print("[WARNING] No text extracted from this image\n")
    except Exception as e:
        print(f"[ERROR] Failed to process image: {e}\n")

def process_images_folder(folder_path="images"):
    """Process all images in the images folder"""
    if not os.path.exists(folder_path):
        print(f"[ERROR] Folder '{folder_path}' not found!")
        return
    
    # Supported formats
    supported_formats = ('.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.pdf')
    
    # Get all image files
    image_files = []
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.lower().endswith(supported_formats):
                image_files.append(os.path.join(root, file))
    
    if not image_files:
        print(f"[INFO] No images found in '{folder_path}' folder")
        return
    
    print(f"[INFO] Found {len(image_files)} image(s) in '{folder_path}' folder\n")
    
    # Process each image
    for image_path in image_files:
        extract_text_from_image(image_path)
    
    print(f"{'='*60}")
    print(f"[COMPLETE] Processed {len(image_files)} image(s)")
    print(f"{'='*60}")

if __name__ == "__main__":
    process_images_folder("images")
