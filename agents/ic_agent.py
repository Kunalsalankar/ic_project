from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.tools import Tool
from langchain.prompts import ChatPromptTemplate
from typing import Dict
from config import Config
from utils import setup_logger

logger = setup_logger(__name__)

class ICInspectionAgent:
    def __init__(self, ocr_engine, scraper, verifier, db_manager):
        self.ocr_engine = ocr_engine
        self.scraper = scraper
        self.verifier = verifier
        self.db_manager = db_manager
        
        self.llm = ChatGoogleGenerativeAI(
            model=Config.LLM_MODEL,
            temperature=Config.LLM_TEMPERATURE,
            google_api_key=Config.GEMINI_API_KEY
        )
        
        self.agent = self._create_agent()
        logger.info("IC Inspection Agent initialized")
    
    def _create_tools(self):
        """Create tools for the agent"""
        return [
            Tool(
                name="extract_text_from_image",
                func=lambda path: self.ocr_engine.extract_from_image_path(path),
                description="Extract text from IC image using OCR"
            ),
            Tool(
                name="search_datasheet",
                func=lambda args: self.scraper.extract_marking_info(args['part'], args['oem']),
                description="Search for datasheet and marking information"
            ),
            Tool(
                name="verify_marking",
                func=lambda args: self.verifier.verify_marking(args['text'], args['ref']),
                description="Verify extracted marking against reference data"
            )
        ]
    
    def _create_agent(self):
        """Create the LangChain agent (simplified for Gemini)"""
        # Gemini doesn't support function calling agents yet
        # Using direct workflow instead
        return None
    
    def inspect(self, image_path: str, part_number: str, oem_name: str) -> Dict:
        """Run complete inspection workflow"""
        logger.info(f"Starting inspection: {part_number} from {oem_name}")
        
        # Extract text
        ocr_result = self.ocr_engine.extract_from_image_path(image_path)
        
        # Get reference data
        reference = self.scraper.extract_marking_info(part_number, oem_name)
        
        # Verify
        verification = self.verifier.verify_marking(ocr_result['text'], reference)
        
        # Save to database
        inspection_data = {
            'image_path': image_path,
            'part_number': part_number,
            'oem_name': oem_name,
            'extracted_text': ocr_result['text'],
            'ocr_confidence': ocr_result['confidence'],
            'status': verification['status'],
            'confidence': verification['confidence'],
            'differences': verification['differences'],
            'reference_markings': reference,
            'datasheet_url': reference.get('datasheet_url')
        }
        
        self.db_manager.save_inspection(inspection_data)
        
        return inspection_data
