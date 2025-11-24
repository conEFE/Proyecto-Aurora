from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.api import rutas_auth, rutas_cases, rutas_images, rutas_results, rutas_reports, rutas_patients, rutas_admin, rutas_user

app = FastAPI(title="Plataforma Médica API", version="0.1.0")

# Configurar CORS antes de agregar las rutas
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",  # Puerto actual del frontend
        "http://localhost:3000"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"status": "ok", "message": "API is running"}

app.include_router(rutas_auth.router, prefix="/auth", tags=["auth"])
app.include_router(rutas_cases.router, prefix="/cases", tags=["cases"])
app.include_router(rutas_images.router, prefix="/cases", tags=["images"])
app.include_router(rutas_results.router, prefix="/images", tags=["results"])
app.include_router(rutas_reports.router, prefix="/reports", tags=["reports"])
app.include_router(rutas_patients.router, prefix="/patients", tags=["patients"])
app.include_router(rutas_admin.router, prefix="/admin", tags=["admin"])
app.include_router(rutas_user.router, prefix="/user", tags=["user"])