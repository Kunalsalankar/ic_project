"""
Test script for IC Inspection System
Run this to verify the system is working correctly
"""

import os
from main import ICInspectionSystem
from config import Config
from utils import setup_logger

logger = setup_logger(__name__)

def test_system_initialization():
    """Test system initialization"""
    print("=" * 60)
    print("Testing System Initialization...")
    print("=" * 60)
    
    try:
        system = ICInspectionSystem()
        print("✓ System initialized successfully")
        return system
    except Exception as e:
        print(f"✗ Initialization failed: {e}")
        return None

def test_database():
    """Test database operations"""
    print("\n" + "=" * 60)
    print("Testing Database...")
    print("=" * 60)
    
    try:
        from database import DatabaseManager
        db = DatabaseManager()
        
        # Test saving inspection
        test_data = {
            'image_path': 'test.jpg',
            'part_number': 'TEST123',
            'oem_name': 'Test OEM',
            'extracted_text': 'TEST TEXT',
            'ocr_confidence': 85.5,
            'status': 'GENUINE',
            'confidence': 0.95,
            'differences': [],
            'reference_markings': {},
            'datasheet_url': 'http://test.com'
        }
        
        record = db.save_inspection(test_data)
        print(f"✓ Database save successful (ID: {record.id})")
        
        # Test retrieval
        retrieved = db.get_inspection(record.id)
        if retrieved:
            print(f"✓ Database retrieval successful")
        
        return True
    except Exception as e:
        print(f"✗ Database test failed: {e}")
        return False

def test_ocr():
    """Test OCR engine"""
    print("\n" + "=" * 60)
    print("Testing OCR Engine...")
    print("=" * 60)
    
    try:
        from ocr import OCREngine
        import numpy as np
        
        ocr = OCREngine()
        
        # Create a simple test image with text
        test_image = np.ones((100, 300), dtype=np.uint8) * 255
        
        result = ocr.extract_text(test_image)
        print(f"✓ OCR engine working (confidence: {result['confidence']:.2f}%)")
        
        return True
    except Exception as e:
        print(f"✗ OCR test failed: {e}")
        print("  Make sure Tesseract is installed and path is correct in config.py")
        return False

def test_scraper():
    """Test web scraper"""
    print("\n" + "=" * 60)
    print("Testing Web Scraper...")
    print("=" * 60)
    
    try:
        from scraper import DatasheetScraper
        
        scraper = DatasheetScraper()
        result = scraper.extract_marking_info("LM358", "Texas Instruments")
        
        print(f"✓ Scraper working")
        print(f"  Part: {result['part_number']}")
        print(f"  OEM: {result['oem_name']}")
        
        return True
    except Exception as e:
        print(f"✗ Scraper test failed: {e}")
        return False

def test_verifier():
    """Test marking verifier"""
    print("\n" + "=" * 60)
    print("Testing Marking Verifier...")
    print("=" * 60)
    
    try:
        from verification import MarkingVerifier
        
        verifier = MarkingVerifier()
        
        # Test with matching text
        result = verifier.verify_marking(
            "LM358 TI 2023",
            {
                'part_number': 'LM358',
                'oem_name': 'Texas Instruments',
                'marking_patterns': ['LM358', 'TI']
            }
        )
        
        print(f"✓ Verifier working")
        print(f"  Status: {result['status']}")
        print(f"  Confidence: {result['confidence']:.2%}")
        
        return True
    except Exception as e:
        print(f"✗ Verifier test failed: {e}")
        return False

def test_config():
    """Test configuration"""
    print("\n" + "=" * 60)
    print("Testing Configuration...")
    print("=" * 60)
    
    checks = []
    
    # Check Gemini API key
    if Config.GEMINI_API_KEY and Config.GEMINI_API_KEY != "":
        print("✓ Gemini API key configured")
        checks.append(True)
    else:
        print("✗ Gemini API key not set in .env file")
        checks.append(False)
    
    # Check Tesseract path
    if os.path.exists(Config.TESSERACT_CMD):
        print(f"✓ Tesseract found at: {Config.TESSERACT_CMD}")
        checks.append(True)
    else:
        print(f"✗ Tesseract not found at: {Config.TESSERACT_CMD}")
        print("  Update TESSERACT_CMD in config.py")
        checks.append(False)
    
    # Check directories
    Config.create_directories()
    for folder in [Config.UPLOAD_FOLDER, Config.RESULTS_FOLDER, Config.DATASHEET_CACHE]:
        if os.path.exists(folder):
            print(f"✓ Directory exists: {folder}")
            checks.append(True)
        else:
            print(f"✗ Directory missing: {folder}")
            checks.append(False)
    
    return all(checks)

def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("IC INSPECTION SYSTEM - TEST SUITE")
    print("=" * 60)
    
    results = {
        'Configuration': test_config(),
        'System Initialization': test_system_initialization() is not None,
        'Database': test_database(),
        'OCR Engine': test_ocr(),
        'Web Scraper': test_scraper(),
        'Verifier': test_verifier()
    }
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    for test_name, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{test_name:.<40} {status}")
    
    total = len(results)
    passed = sum(results.values())
    
    print("\n" + "=" * 60)
    print(f"Results: {passed}/{total} tests passed")
    print("=" * 60)
    
    if passed == total:
        print("\n🎉 All tests passed! System is ready to use.")
        print("Run 'python app.py' to start the web interface.")
    else:
        print("\n⚠️  Some tests failed. Please fix the issues above.")

if __name__ == "__main__":
    main()
