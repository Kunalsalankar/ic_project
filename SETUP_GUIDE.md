# IC Marking Verification System - Setup Guide

## Prerequisites

1. **Python 3.9 or higher**
2. **Tesseract OCR**
   - Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki
   - Install and add to PATH
   - Default location: `C:\Program Files\Tesseract-OCR\tesseract.exe`

## Installation Steps

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Create a `.env` file from the example:

```bash
copy .env.example .env
```

Edit `.env` and add your Google Gemini API key:

```
GEMINI_API_KEY=AIzaSyC8vyWG5CMDpmzc2NhgjzJLD3f3bHgVNcM
DATABASE_URL=sqlite:///./ic_inspection.db
LOG_LEVEL=INFO
```

### 3. Verify Tesseract Installation

Open PowerShell and run:

```powershell
tesseract --version
```

If not found, update the path in `config.py`:

```python
TESSERACT_CMD = r"C:\Path\To\Your\tesseract.exe"
```

## Running the System

### Option 1: Web Interface (Recommended)

Start the web application:

```bash
python app.py
```

Access the interface at: http://localhost:8000

### Option 2: Python API

```python
from main import ICInspectionSystem

# Initialize system
system = ICInspectionSystem()

# Inspect an IC
result = system.inspect_ic(
    image_path="path/to/ic_image.jpg",
    ic_part_number="LM358",
    oem_name="Texas Instruments"
)

print(f"Status: {result['status']}")
print(f"Confidence: {result['confidence']:.2%}")
```

## Project Structure

```
ai_agent/
├── agents/              # AI agent with LangChain
│   ├── __init__.py
│   └── ic_agent.py
├── database/            # Database models and storage
│   ├── __init__.py
│   ├── models.py
│   └── storage.py
├── ocr/                 # OCR and image processing
│   ├── __init__.py
│   ├── image_processor.py
│   └── ocr_engine.py
├── scraper/             # Web scraping for datasheets
│   ├── __init__.py
│   └── datasheet_scraper.py
├── verification/        # Marking verification logic
│   ├── __init__.py
│   └── verifier.py
├── utils/               # Utility functions
│   ├── __init__.py
│   └── logger.py
├── main.py              # Main system orchestrator
├── app.py               # FastAPI web application
├── config.py            # Configuration settings
└── requirements.txt     # Python dependencies
```

## Features

### 1. **Image Processing**
- Automatic IC region detection
- Multiple preprocessing techniques
- Contrast enhancement and denoising

### 2. **OCR Extraction**
- Tesseract OCR integration
- Confidence-based filtering
- Multiple image version processing

### 3. **Web Scraping**
- Automatic datasheet search
- Marking pattern extraction
- Caching for performance

### 4. **Verification**
- Fuzzy string matching
- Pattern recognition
- Confidence scoring

### 5. **AI Agent**
- LangChain-based orchestration
- Google Gemini Pro integration
- Autonomous decision making

### 6. **Database Storage**
- SQLite database
- Inspection history
- Datasheet caching

## Usage Examples

### Web Interface

1. Upload IC image
2. Enter part number (e.g., "LM358")
3. Enter OEM name (e.g., "Texas Instruments")
4. Click "Verify IC"
5. View results with confidence score

### API Endpoints

- `GET /` - Web interface
- `POST /inspect` - Submit inspection
- `GET /history` - View inspection history

## Troubleshooting

### Tesseract Not Found

```
Error: Tesseract not found
```

**Solution:** Update `TESSERACT_CMD` in `config.py` with correct path

### Gemini API Error

```
Error: Invalid API key
```

**Solution:** Check `.env` file has valid `GEMINI_API_KEY`

### Image Processing Error

```
Error: Failed to load image
```

**Solution:** Ensure image format is supported (JPG, PNG, BMP)

## Performance Tips

1. **Image Quality**: Use high-resolution images (1920x1080 or higher)
2. **Lighting**: Ensure good lighting on IC markings
3. **Focus**: IC markings should be in focus
4. **Angle**: Capture image perpendicular to IC surface

## Next Steps

1. Test with sample IC images
2. Review inspection logs in `ic_inspection.log`
3. Check database records in `ic_inspection.db`
4. Customize thresholds in `config.py` as needed

## Support

For issues or questions, check the logs:
- Application logs: `ic_inspection.log`
- Database: `ic_inspection.db`
