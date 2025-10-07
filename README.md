# AOI-Based IC Marking Verification System

An automated optical inspection system that captures IC part markings, verifies them against OEM datasheets, and identifies fake components using AI and web scraping.

## Features

- **Automated IC Detection**: Detects and locates IC marking areas from captured images
- **OCR Extraction**: Extracts text, numbers, and logos from IC surfaces
- **Web Scraping**: Automatically retrieves OEM marking reference data from datasheets
- **Intelligent Verification**: Compares captured markings with OEM specifications
- **AI Agent Orchestration**: Uses LangChain agents for autonomous operation
- **Result Reporting**: Generates inspection reports with highlighted differences
- **Database Storage**: Stores inspection data for future reference and learning

## Installation

1. Install Python 3.9 or higher
2. Install Tesseract OCR:
   - Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki
   - Add Tesseract to PATH

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env and add your OpenAI API key
```

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment
```bash
# Copy example env file
copy .env.example .env

# Edit .env and add your OpenAI API key
OPENAI_API_KEY=your_key_here
```

### 3. Test System
```bash
python test_system.py
```

### 4. Run Web Interface
```bash
python app.py
```
Access at http://localhost:8000

## Usage

### Web Interface (Recommended)
1. Upload IC image
2. Enter part number (e.g., "LM358")
3. Enter OEM name (e.g., "Texas Instruments")
4. Click "Verify IC"
5. View results with confidence score

### Python API
```python
from main import ICInspectionSystem

system = ICInspectionSystem()

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
├── agents/              # AI agent modules
├── ocr/                 # OCR and image processing
├── scraper/             # Web scraping modules
├── verification/        # Marking verification logic
├── database/            # Database models and storage
├── utils/               # Utility functions
├── main.py              # Main system orchestrator
├── app.py               # Web application
└── requirements.txt     # Dependencies
```

## License

MIT License
