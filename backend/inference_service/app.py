"""Servicio de inferencia de Aurora: POST /predict recibe una mamografía y responde con la CNN y YOLO."""

from analyzer import DEVICE, MODEL_VERSION, Analyzer
from fastapi import FastAPI, File, HTTPException, UploadFile

app = FastAPI(title="Aurora - servicio de inferencia")
analyzer = Analyzer()


@app.get("/health")
def health():
    return {"status": "ok", "model_version": MODEL_VERSION, "device": DEVICE}


@app.post("/predict")
def predict(file: UploadFile = File(...)):
    content = file.file.read()
    if not content:
        raise HTTPException(status_code=400, detail="El archivo está vacío")
    try:
        return analyzer.analyze(content)
    except ValueError as exc:
        raise HTTPException(status_code=415, detail=str(exc))
