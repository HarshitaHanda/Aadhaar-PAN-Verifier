import cv2
import numpy as np

def calculate_ela(image, quality=90):
    """Calculate Error Level Analysis for tamper detection"""
    temp_path = "temp_ela.jpg"
    cv2.imwrite(temp_path, image, [cv2.IMWRITE_JPEG_QUALITY, quality])
    temp_image = cv2.imread(temp_path)
    os.remove(temp_path)
    
    if temp_image is None:
        return 0
    
    # Resize if needed
    if image.shape != temp_image.shape:
        temp_image = cv2.resize(temp_image, (image.shape[1], image.shape[0]))
    
    # Calculate difference
    diff = cv2.absdiff(image, temp_image)
    diff_mean = np.mean(diff)
    return min(100, diff_mean * 0.5)  # Scale to percentage

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
