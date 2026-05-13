from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from .engine import AnomalyEngine
import shutil
import os

app = FastAPI()
engine = AnomalyEngine()

# Configurar CORS para que React pueda comunicarse
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/analyze")
async def analyze_tdr(file: UploadFile = File(...)):
    # Guardar temporalmente el archivo
    temp_path = f"temp_{file.filename}"
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    try:
        # 1. Extraer párrafos
        paragraphs = engine.extract_text(temp_path)
        
        # 2. Correr motor de IA
        findings = engine.analyze_consistency(paragraphs)
        
        return {
            "status": "success",
            "document_name": file.filename,
            "total_findings": len(findings),
            "findings": findings
        }
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)