import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Configuration settings for the IC inspection system"""
    
    # API Keys
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    
    # Database
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./ic_inspection.db")
    
    # Tesseract OCR
    TESSERACT_CMD = os.getenv("TESSERACT_CMD", r"C:\Program Files\Tesseract-OCR\tesseract.exe")
    
    # Image Processing
    IMAGE_MAX_WIDTH = 1920
    IMAGE_MAX_HEIGHT = 1080
    OCR_CONFIDENCE_THRESHOLD = 60.0
    
    # Web Scraping
    SCRAPER_TIMEOUT = 30
    MAX_RETRIES = 3
    USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    
    # Verification
    SIMILARITY_THRESHOLD = 0.85
    FUZZY_MATCH_THRESHOLD = 80
    
    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE = "ic_inspection.log"
    
    # Storage
    UPLOAD_FOLDER = "uploads"
    RESULTS_FOLDER = "results"
    DATASHEET_CACHE = "datasheet_cache"
    
    # AI Agent
    LLM_MODEL = "gemini-pro"
    LLM_TEMPERATURE = 0.1
    MAX_TOKENS = 2000
    
    @classmethod
    def create_directories(cls):
        """Create necessary directories if they don't exist"""
        for folder in [cls.UPLOAD_FOLDER, cls.RESULTS_FOLDER, cls.DATASHEET_CACHE]:
            os.makedirs(folder, exist_ok=True)
