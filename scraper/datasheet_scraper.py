import requests
from bs4 import BeautifulSoup
from typing import Dict, Optional
from config import Config
from utils import setup_logger

logger = setup_logger(__name__)

class DatasheetScraper:
    def __init__(self):
        self.timeout = Config.SCRAPER_TIMEOUT
        self.headers = {'User-Agent': Config.USER_AGENT}
    
    def search_datasheet(self, part_number: str, oem_name: str) -> Optional[str]:
        """Search for datasheet URL"""
        try:
            query = f"{part_number} {oem_name} datasheet"
            search_url = f"https://www.google.com/search?q={query}"
            response = requests.get(search_url, headers=self.headers, timeout=self.timeout)
            
            soup = BeautifulSoup(response.text, 'html.parser')
            links = soup.find_all('a', href=True)
            
            for link in links:
                href = link['href']
                if 'pdf' in href.lower() or 'datasheet' in href.lower():
                    logger.info(f"Found datasheet: {href}")
                    return href
            
            return None
        except Exception as e:
            logger.error(f"Datasheet search failed: {e}")
            return None
    
    def extract_marking_info(self, part_number: str, oem_name: str) -> Dict:
        """Extract marking information from web sources"""
        datasheet_url = self.search_datasheet(part_number, oem_name)
        
        return {
            'part_number': part_number,
            'oem_name': oem_name,
            'datasheet_url': datasheet_url,
            'marking_patterns': [part_number, oem_name[:3].upper()],
            'date_code_format': 'YYWW'
        }
