from typing import Dict, List
from difflib import SequenceMatcher
from fuzzywuzzy import fuzz
from config import Config
from utils import setup_logger

logger = setup_logger(__name__)

class MarkingVerifier:
    def __init__(self):
        self.similarity_threshold = Config.SIMILARITY_THRESHOLD
        self.fuzzy_threshold = Config.FUZZY_MATCH_THRESHOLD
    
    def calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two strings"""
        return SequenceMatcher(None, text1.upper(), text2.upper()).ratio()
    
    def fuzzy_match(self, text1: str, text2: str) -> int:
        """Calculate fuzzy match score"""
        return fuzz.ratio(text1.upper(), text2.upper())
    
    def verify_marking(self, extracted_text: str, reference_data: Dict) -> Dict:
        """Verify extracted marking against reference data"""
        part_number = reference_data.get('part_number', '')
        oem_name = reference_data.get('oem_name', '')
        marking_patterns = reference_data.get('marking_patterns', [])
        
        # Check for part number match
        part_similarity = self.fuzzy_match(extracted_text, part_number)
        
        # Check for OEM name match
        oem_similarity = self.fuzzy_match(extracted_text, oem_name)
        
        # Check for marking patterns
        pattern_matches = []
        for pattern in marking_patterns:
            if pattern.upper() in extracted_text.upper():
                pattern_matches.append(pattern)
        
        # Calculate overall confidence
        confidence = max(part_similarity, oem_similarity) / 100.0
        
        # Determine status
        if confidence >= self.similarity_threshold:
            status = "GENUINE"
        elif confidence >= 0.6:
            status = "UNCERTAIN"
        else:
            status = "FAKE"
        
        differences = []
        if part_similarity < 90:
            differences.append(f"Part number mismatch (similarity: {part_similarity}%)")
        if not pattern_matches:
            differences.append("Expected marking patterns not found")
        
        logger.info(f"Verification complete: {status} (confidence: {confidence:.2f})")
        
        return {
            'status': status,
            'confidence': confidence,
            'part_similarity': part_similarity,
            'oem_similarity': oem_similarity,
            'pattern_matches': pattern_matches,
            'differences': differences
        }
