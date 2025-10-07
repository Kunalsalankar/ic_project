import cv2
import numpy as np
from PIL import Image
from typing import Tuple, List, Optional
import os

from config import Config
from utils import setup_logger

logger = setup_logger(__name__)


class ImageProcessor:
    """Handles image preprocessing for OCR"""
    
    def __init__(self):
        self.max_width = Config.IMAGE_MAX_WIDTH
        self.max_height = Config.IMAGE_MAX_HEIGHT
    
    def load_image(self, image_path: str) -> np.ndarray:
        """Load image from file path"""
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image not found: {image_path}")
        
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Failed to load image: {image_path}")
        
        logger.info(f"Loaded image: {image_path}, shape: {image.shape}")
        return image
    
    def resize_image(self, image: np.ndarray) -> np.ndarray:
        """Resize image if it exceeds maximum dimensions"""
        height, width = image.shape[:2]
        
        if width <= self.max_width and height <= self.max_height:
            return image
        
        # Calculate scaling factor
        scale = min(self.max_width / width, self.max_height / height)
        new_width = int(width * scale)
        new_height = int(height * scale)
        
        resized = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_AREA)
        logger.info(f"Resized image from {width}x{height} to {new_width}x{new_height}")
        return resized
    
    def convert_to_grayscale(self, image: np.ndarray) -> np.ndarray:
        """Convert image to grayscale"""
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            logger.debug("Converted image to grayscale")
            return gray
        return image
    
    def enhance_contrast(self, image: np.ndarray) -> np.ndarray:
        """Enhance image contrast using CLAHE"""
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(image)
        logger.debug("Enhanced image contrast")
        return enhanced
    
    def denoise_image(self, image: np.ndarray) -> np.ndarray:
        """Apply denoising to image"""
        denoised = cv2.fastNlMeansDenoising(image, None, h=10, templateWindowSize=7, searchWindowSize=21)
        logger.debug("Applied denoising")
        return denoised
    
    def apply_threshold(self, image: np.ndarray, method: str = 'adaptive') -> np.ndarray:
        """Apply thresholding to binarize image"""
        if method == 'adaptive':
            threshold = cv2.adaptiveThreshold(
                image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                cv2.THRESH_BINARY, 11, 2
            )
        elif method == 'otsu':
            _, threshold = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        else:
            _, threshold = cv2.threshold(image, 127, 255, cv2.THRESH_BINARY)
        
        logger.debug(f"Applied {method} thresholding")
        return threshold
    
    def detect_ic_region(self, image: np.ndarray) -> Optional[Tuple[int, int, int, int]]:
        """Detect the IC chip region in the image using contour detection"""
        # Convert to grayscale if needed
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()
        
        # Apply edge detection
        edges = cv2.Canny(gray, 50, 150)
        
        # Find contours
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if not contours:
            logger.warning("No contours detected in image")
            return None
        
        # Find the largest rectangular contour (likely the IC chip)
        largest_contour = max(contours, key=cv2.contourArea)
        x, y, w, h = cv2.boundingRect(largest_contour)
        
        # Filter out very small or very large regions
        image_area = image.shape[0] * image.shape[1]
        contour_area = w * h
        
        if contour_area < image_area * 0.05 or contour_area > image_area * 0.95:
            logger.warning("Detected region size is out of expected range")
            return None
        
        logger.info(f"Detected IC region: x={x}, y={y}, w={w}, h={h}")
        return (x, y, w, h)
    
    def crop_to_region(self, image: np.ndarray, region: Tuple[int, int, int, int]) -> np.ndarray:
        """Crop image to specified region"""
        x, y, w, h = region
        cropped = image[y:y+h, x:x+w]
        logger.debug(f"Cropped image to region: {region}")
        return cropped
    
    def preprocess_for_ocr(self, image_path: str, auto_detect_ic: bool = True) -> List[np.ndarray]:
        """
        Complete preprocessing pipeline for OCR
        Returns multiple processed versions for better OCR results
        """
        # Load and resize
        image = self.load_image(image_path)
        image = self.resize_image(image)
        
        # Detect IC region if requested
        if auto_detect_ic:
            region = self.detect_ic_region(image)
            if region:
                image = self.crop_to_region(image, region)
        
        # Convert to grayscale
        gray = self.convert_to_grayscale(image)
        
        # Create multiple processed versions
        processed_images = []
        
        # Version 1: Enhanced contrast
        enhanced = self.enhance_contrast(gray)
        processed_images.append(enhanced)
        
        # Version 2: Denoised
        denoised = self.denoise_image(gray)
        processed_images.append(denoised)
        
        # Version 3: Adaptive threshold
        adaptive_thresh = self.apply_threshold(gray, 'adaptive')
        processed_images.append(adaptive_thresh)
        
        # Version 4: Otsu threshold
        otsu_thresh = self.apply_threshold(gray, 'otsu')
        processed_images.append(otsu_thresh)
        
        # Version 5: Enhanced + denoised
        enhanced_denoised = self.denoise_image(enhanced)
        processed_images.append(enhanced_denoised)
        
        logger.info(f"Generated {len(processed_images)} processed image versions")
        return processed_images
    
    def save_image(self, image: np.ndarray, output_path: str):
        """Save processed image to file"""
        cv2.imwrite(output_path, image)
        logger.info(f"Saved image to: {output_path}")
