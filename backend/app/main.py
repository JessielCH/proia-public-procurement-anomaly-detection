from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import shutil
import os
from .engine import AnomalyEngine
from .database import init_db, save_feedback

app = FastAPI()

# Configuración de CORS para que React pueda comunicarse con FastAPI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Instanciamos el motor de IA local
engine = AnomalyEngine()
init_db()  # Inicializar la base de datos de retroalimentación

class FeedbackModel(BaseModel):
    document_name: str
    patron_texto: str
    score_ia: float
    es_anomalia_real: bool

@app.post("/analyze")
async def analyze_document(file: UploadFile = File(...)):
    temp_path = f"temp_{file.filename}"
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # 1. Extraer párrafos
    paragraphs = engine.extract_text(temp_path)
    
    # 2. Analizar e inferir gráficos (Esto devuelve un diccionario)
    analysis_data = engine.analyze_consistency(paragraphs)
    
    os.remove(temp_path)
    
    # 3. Devolver la data en el nuevo formato que espera React
    return {
        "document_name": file.filename,
        "total_findings": len(analysis_data["findings"]),
        "findings": analysis_data["findings"],
        "graficos": analysis_data["graficos"]
    }

@app.post("/feedback")
async def register_feedback(feedback: FeedbackModel):
    """Guarda el criterio del auditor para entrenar la IA en el futuro."""
    save_feedback(
        feedback.document_name, 
        feedback.patron_texto, 
        feedback.score_ia, 
        feedback.es_anomalia_real
    )
    return {"status": "Feedback registrado para entrenamiento"}