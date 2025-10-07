from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import os
import shutil
from datetime import datetime
from main import ICInspectionSystem
from config import Config
from utils import setup_logger

logger = setup_logger(__name__)

app = FastAPI(title="IC Marking Verification System")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize system
system = ICInspectionSystem()

@app.get("/", response_class=HTMLResponse)
async def home():
    """Serve the main web interface"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>IC Marking Verification</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 800px;
                margin: 50px auto;
                padding: 20px;
                background: #f5f5f5;
            }
            .container {
                background: white;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            h1 {
                color: #333;
                text-align: center;
            }
            .form-group {
                margin: 20px 0;
            }
            label {
                display: block;
                margin-bottom: 5px;
                font-weight: bold;
            }
            input[type="text"], input[type="file"] {
                width: 100%;
                padding: 10px;
                border: 1px solid #ddd;
                border-radius: 5px;
            }
            button {
                background: #007bff;
                color: white;
                padding: 12px 30px;
                border: none;
                border-radius: 5px;
                cursor: pointer;
                font-size: 16px;
                width: 100%;
            }
            button:hover {
                background: #0056b3;
            }
            #result {
                margin-top: 20px;
                padding: 20px;
                border-radius: 5px;
                display: none;
            }
            .genuine {
                background: #d4edda;
                border: 1px solid #c3e6cb;
            }
            .fake {
                background: #f8d7da;
                border: 1px solid #f5c6cb;
            }
            .uncertain {
                background: #fff3cd;
                border: 1px solid #ffeeba;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🔍 IC Marking Verification System</h1>
            <form id="inspectionForm" enctype="multipart/form-data">
                <div class="form-group">
                    <label>IC Image:</label>
                    <input type="file" name="image" accept="image/*" required>
                </div>
                <div class="form-group">
                    <label>Part Number:</label>
                    <input type="text" name="part_number" placeholder="e.g., LM358" required>
                </div>
                <div class="form-group">
                    <label>OEM Name:</label>
                    <input type="text" name="oem_name" placeholder="e.g., Texas Instruments" required>
                </div>
                <button type="submit">Verify IC</button>
            </form>
            <div id="result"></div>
        </div>
        
        <script>
            document.getElementById('inspectionForm').onsubmit = async (e) => {
                e.preventDefault();
                const formData = new FormData(e.target);
                const button = e.target.querySelector('button');
                button.textContent = 'Processing...';
                button.disabled = true;
                
                try {
                    const response = await fetch('/inspect', {
                        method: 'POST',
                        body: formData
                    });
                    const data = await response.json();
                    
                    const resultDiv = document.getElementById('result');
                    resultDiv.className = data.status.toLowerCase();
                    resultDiv.style.display = 'block';
                    resultDiv.innerHTML = `
                        <h2>Verification Result</h2>
                        <p><strong>Status:</strong> ${data.status}</p>
                        <p><strong>Confidence:</strong> ${(data.confidence * 100).toFixed(2)}%</p>
                        <p><strong>Extracted Text:</strong> ${data.extracted_text}</p>
                        <p><strong>OCR Confidence:</strong> ${data.ocr_confidence.toFixed(2)}%</p>
                        ${data.differences.length > 0 ? `
                            <p><strong>Issues Found:</strong></p>
                            <ul>${data.differences.map(d => `<li>${d}</li>`).join('')}</ul>
                        ` : ''}
                    `;
                } catch (error) {
                    alert('Error: ' + error.message);
                }
                
                button.textContent = 'Verify IC';
                button.disabled = false;
            };
        </script>
    </body>
    </html>
    """

@app.post("/inspect")
async def inspect_ic(
    image: UploadFile = File(...),
    part_number: str = Form(...),
    oem_name: str = Form(...)
):
    """Handle IC inspection request"""
    try:
        # Save uploaded image
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{image.filename}"
        filepath = os.path.join(Config.UPLOAD_FOLDER, filename)
        
        with open(filepath, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)
        
        logger.info(f"Processing inspection: {part_number} from {oem_name}")
        
        # Run inspection
        result = system.inspect_ic(filepath, part_number, oem_name)
        
        return JSONResponse(content=result)
    
    except Exception as e:
        logger.error(f"Inspection error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/history")
async def get_history():
    """Get recent inspection history"""
    try:
        records = system.db_manager.get_recent_inspections(limit=20)
        return JSONResponse(content=[{
            'id': r.id,
            'timestamp': r.timestamp.isoformat(),
            'part_number': r.part_number,
            'status': r.status,
            'confidence': r.confidence
        } for r in records])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting web application...")
    uvicorn.run(app, host="127.0.0.1", port=8000)
