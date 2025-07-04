import cv2
import numpy as np

def calculate_ela(image):
    """Simplified tamper detection without file I/O"""
    compressed = cv2.resize(image, None, fx=0.95, fy=0.95)
    restored = cv2.resize(compressed, (image.shape[1], image.shape[0]))
    diff = cv2.absdiff(image, restored)
    return min(100, np.mean(diff) * 0.3)  # Scale to percentage

def extract_region(image, coordinates):
    """Extract region of interest from image"""
    x1, y1, x2, y2 = coordinates
    if y2 > image.shape[0] or x2 > image.shape[1]:
        return np.array([])
    return image[y1:y2, x1:x2]

def preprocess_for_ocr(image):
    """Enhance image for better OCR results"""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)
    _, thresh = cv2.threshold(enhanced, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return thresh
