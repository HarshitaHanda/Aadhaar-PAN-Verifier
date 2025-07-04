import cv2
import numpy as np
import pytesseract
import re
from .helpers import calculate_ela, extract_region, preprocess_for_ocr

# Aadhaar card regions (relative coordinates)
AADHAAR_REGIONS = {
    'name': (0.35, 0.25, 0.85, 0.32),
    'aadhaar_no': (0.35, 0.32, 0.85, 0.38),
    'dob': (0.35, 0.38, 0.85, 0.44),
    'gender': (0.35, 0.44, 0.85, 0.50),
    'photo': (0.10, 0.25, 0.30, 0.50)
}

def verify(image):
    """Verify Aadhaar card"""
    height, width = image.shape[:2]
    results = {
        'structure_valid': width > height,  # Aadhaar should be landscape
        'photo_tamper_score': 0,
        'text_valid': False,
        'extracted_text': {}
    }
    
    # Convert relative coordinates to absolute
    abs_regions = {}
    for key, (x1, y1, x2, y2) in AADHAAR_REGIONS.items():
        abs_regions[key] = (
            int(width * x1), int(height * y1),
            int(width * x2), int(height * y2)
        )
    
    # Photo tamper detection
    if 'photo' in abs_regions:
        photo_region = extract_region(image, abs_regions['photo'])
        if photo_region.size > 0:
            results['photo_tamper_score'] = calculate_ela(photo_region)
    
    # Text extraction and validation
    text_fields = ['name', 'aadhaar_no', 'dob', 'gender']
    valid_text_count = 0
    
    for field in text_fields:
        region = extract_region(image, abs_regions[field])
        if region.size > 0:
            processed = preprocess_for_ocr(region)
            text = pytesseract.image_to_string(processed, lang='eng')
            text = re.sub(r'\W+', ' ', text).strip()
            results['extracted_text'][field] = text
            
            # Simple validation
            if text and len(text) > 2:
                valid_text_count += 1
    
    # Validate Aadhaar number format (XXXX XXXX XXXX)
    aadhaar_text = results['extracted_text'].get('aadhaar_no', '')
    results['text_valid'] = re.match(r'^\d{4}\s?\d{4}\s?\d{4}$', aadhaar_text) is not None
    
    return results
