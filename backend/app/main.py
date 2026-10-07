import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api import (
    rutas_admin,
    rutas_auth,
    rutas_cases,
    rutas_images,
    rutas_patients,
    rutas_reports,
    rutas_results,
    rutas_user,
)
from app.config import settings
from app.middleware import ProcessTimeMiddleware
from app.services.errors import DomainError

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")

app = FastAPI(title="Proyecto Aurora API", version="1.1.0")

app.add_middleware(ProcessTimeMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["X-Process-Time-Ms"],
)


@app.exception_handler(DomainError)
async def domain_error_handler(_: Request, exc: DomainError):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.message})


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
