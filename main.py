from config import Config
from database import DatabaseManager
from ocr import OCREngine
from scraper import DatasheetScraper
from verification import MarkingVerifier
from agents import ICInspectionAgent
from utils import setup_logger

logger = setup_logger(__name__)

class ICInspectionSystem:
    """Main orchestrator for IC inspection system"""
    
    def __init__(self):
        logger.info("Initializing IC Inspection System...")
        
        # Create necessary directories
        Config.create_directories()
        
        # Initialize components
        self.db_manager = DatabaseManager()
        self.ocr_engine = OCREngine()
        self.scraper = DatasheetScraper()
        self.verifier = MarkingVerifier()
        
        # Initialize AI agent
        self.agent = ICInspectionAgent(
            self.ocr_engine,
            self.scraper,
            self.verifier,
            self.db_manager
        )
        
        logger.info("IC Inspection System initialized successfully")
    
    def inspect_ic(self, image_path: str, ic_part_number: str, oem_name: str):
        """
        Inspect an IC image and verify its authenticity
        
        Args:
            image_path: Path to IC image
            ic_part_number: Expected IC part number
            oem_name: OEM manufacturer name
        
        Returns:
            Inspection result dictionary
        """
        logger.info(f"Starting inspection for {ic_part_number} from {oem_name}")
        
        try:
            result = self.agent.inspect(image_path, ic_part_number, oem_name)
            logger.info(f"Inspection complete: {result['status']}")
            return result
        except Exception as e:
            logger.error(f"Inspection failed: {e}")
            raise

if __name__ == "__main__":
    # Example usage
    system = ICInspectionSystem()
    
    # Test inspection
    result = system.inspect_ic(
        image_path="test_images/ic_sample.jpg",
        ic_part_number="LM358",
        oem_name="Texas Instruments"
    )
    
    print(f"\nInspection Result:")
    print(f"Status: {result['status']}")
    print(f"Confidence: {result['confidence']:.2%}")
    print(f"Extracted Text: {result['extracted_text']}")
