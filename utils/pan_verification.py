import cv2
import numpy as np
import pytesseract
import re
from .helpers import calculate_ela, extract_region, preprocess_for_ocr

# PAN card regions (relative coordinates)
PAN_REGIONS = {
    'name': (0.20, 0.20, 0.80, 0.28),
    'pan_no': (0.20, 0.28, 0.80, 0.36),
    'father_name': (0.20, 0.36, 0.80, 0.44),
    'dob': (0.20, 0.44, 0.80, 0.52),
    'hologram': (0.65, 0.10, 0.90, 0.25)
}

def verify(image):
    """Verify PAN card"""
    height, width = image.shape[:2]
    results = {
        'tamper_score': calculate_ela(image),
        'hologram_detected': False,
        'pan_valid': False,
        'extracted_text': {}
    }
    
    # Convert relative coordinates to absolute
    abs_regions = {}
    for key, (x1, y1, x2, y2) in PAN_REGIONS.items():
        abs_regions[key] = (
            int(width * x1), int(height * y1),
            int(width * x2), int(height * y2)
        )
    
    # Hologram detection (simulated)
    if 'hologram' in abs_regions:
        hologram_region = extract_region(image, abs_regions['hologram'])
        if hologram_region.size > 0:
            hsv = cv2.cvtColor(hologram_region, cv2.COLOR_BGR2HSV)
            results['hologram_detected'] = np.mean(hsv[:,:,1]) > 80
    
    # Text extraction
    text_fields = ['name', 'pan_no', 'father_name', 'dob']
    
    for field in text_fields:
        region = extract_region(image, abs_regions[field])
        if region.size > 0:
            processed = preprocess_for_ocr(region)
            text = pytesseract.image_to_string(processed, lang='eng')
            text = re.sub(r'\W+', ' ', text).strip()
            results['extracted_text'][field] = text
    
    # Validate PAN number format (AAAAA0000A)
    pan_text = results['extracted_text'].get('pan_no', '')
    results['pan_valid'] = re.match(r'^[A-Z]{5}\d{4}[A-Z]{1}$', pan_text) is not None
    
    return results
