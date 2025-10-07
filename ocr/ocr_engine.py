import pytesseract
import numpy as np
from typing import Dict, List
import re
from config import Config
from utils import setup_logger

logger = setup_logger(__name__)

class OCREngine:
    def __init__(self):
        pytesseract.pytesseract.tesseract_cmd = Config.TESSERACT_CMD
        self.confidence_threshold = Config.OCR_CONFIDENCE_THRESHOLD
    
    def extract_text(self, image: np.ndarray) -> Dict:
        try:
            data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
            filtered_text = []
            confidences = []
            
            for i, conf in enumerate(data['conf']):
                if conf > self.confidence_threshold:
                    text = data['text'][i].strip()
                    if text:
                        filtered_text.append(text)
                        confidences.append(conf)
            
            full_text = ' '.join(filtered_text)
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0
            
            return {'text': full_text, 'confidence': avg_confidence}
        except Exception as e:
            logger.error(f"OCR failed: {e}")
            return {'text': '', 'confidence': 0}
    
    def extract_from_image_path(self, image_path: str) -> Dict:
        from .image_processor import ImageProcessor
        processor = ImageProcessor()
        images = processor.preprocess_for_ocr(image_path)
        
        results = [self.extract_text(img) for img in images]
        best = max(results, key=lambda x: x['confidence'])
        logger.info(f"OCR complete: {best['confidence']:.2f}% confidence")
        return best
