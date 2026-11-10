"""Servicio de inferencia de Aurora: POST /predict recibe una mamografía y responde con la CNN y YOLO.

Corre igual en el PC de un integrante (GPU) o en AWS (CPU): la plataforma solo conoce su URL y el token.
"""

import hmac
import os

from analyzer import CLINICALLY_VALIDATED, DEVICE, MODEL_VERSION, Analyzer
from fastapi import Depends, FastAPI, File, Header, HTTPException, UploadFile

# Token compartido con la plataforma (INFERENCE_API_TOKEN en ambos lados). Sin token, solo para pruebas locales.
API_TOKEN = os.environ.get("INFERENCE_API_TOKEN", "")
MAX_UPLOAD_MB = int(os.environ.get("MAX_UPLOAD_MB", "60"))

app = FastAPI(
    title="Aurora - servicio de inferencia",
    docs_url="/docs" if os.environ.get("ENABLE_API_DOCS", "true").lower() == "true" else None,
    redoc_url=None,
)
analyzer = Analyzer()


def require_token(authorization: str | None = Header(default=None)) -> None:
    if not API_TOKEN:
        return
    expected = f"Bearer {API_TOKEN}"
    if not authorization or not hmac.compare_digest(authorization.encode(), expected.encode()):
        raise HTTPException(status_code=401, detail="Token inválido o ausente")


@app.get("/health", dependencies=[Depends(require_token)])
def health():
    return {
        "status": "ok",
        "model_version": MODEL_VERSION,
        "device": DEVICE,
        "clinically_validated": CLINICALLY_VALIDATED,
    }


@app.post("/predict", dependencies=[Depends(require_token)])
def predict(file: UploadFile = File(...)):
    content = file.file.read(MAX_UPLOAD_MB * 1024 * 1024 + 1)
    if not content:
        raise HTTPException(status_code=400, detail="El archivo está vacío")
    if len(content) > MAX_UPLOAD_MB * 1024 * 1024:
        raise HTTPException(status_code=413, detail=f"La imagen supera {MAX_UPLOAD_MB} MB")
    try:
        return analyzer.analyze(content)
    except ValueError as exc:
        raise HTTPException(status_code=415, detail=str(exc)) from exc
