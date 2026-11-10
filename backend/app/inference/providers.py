"""Proveedores de inferencia (D10). El resultado del proveedor simulado SIEMPRE lleva is_simulated=True.

El servicio real se consume solo por HTTP (INFERENCE_URL + INFERENCE_API_TOKEN): da lo mismo si corre en el PC de
un integrante (con GPU, vía Tailscale) o en AWS (contenedor en EC2 o Lambda). Moverlo es cambiar la URL.
"""

import hashlib
import logging
import random
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from functools import lru_cache
from typing import Any

import httpx

from app.config import settings

logger = logging.getLogger("aurora.inference")


@dataclass
class InferenceOutput:
    detected: bool
    confidence: float  # 0-100
    detections: list[dict[str, Any]] = field(default_factory=list)
    processing_time_ms: int = 0
    model_version: str = ""
    is_simulated: bool = True
    message: str = ""
    # Solo un modelo con validación clínica puede declararlo; el prototipo actual no la tiene
    clinically_validated: bool = False


class InferenceProvider(ABC):
    @abstractmethod
    def analyze(self, image_bytes: bytes) -> InferenceOutput: ...


class SimulatedProvider(InferenceProvider):
    """Genera un resultado ficticio, determinístico por el SHA-256 de la imagen y sin esperas artificiales.

    NO es un modelo clínico: sirve para probar el flujo mientras no exista el servicio YOLO real.
    """

    MODEL_VERSION = "simulado-v1"

    def analyze(self, image_bytes: bytes) -> InferenceOutput:
        start = time.perf_counter()
        digest = hashlib.sha256(image_bytes).hexdigest()
        rng = random.Random(int(digest[:16], 16))
        detected = rng.random() > 0.4
        confidence = rng.uniform(55.0, 97.0) if detected else rng.uniform(80.0, 99.0)
        detections = []
        if detected:
            for _ in range(rng.randint(1, 3)):
                detections.append(
                    {
                        "x": round(rng.uniform(0.1, 0.65), 4),
                        "y": round(rng.uniform(0.1, 0.65), 4),
                        "width": round(rng.uniform(0.08, 0.25), 4),
                        "height": round(rng.uniform(0.08, 0.25), 4),
                        "confidence": round(rng.uniform(max(confidence - 8, 0), confidence) / 100, 4),
                        "class_name": "hallazgo_simulado",
                    }
                )
        message = (
            f"[IA SIMULADA] Hallazgo simulado con {confidence:.1f}% de confianza"
            if detected
            else f"[IA SIMULADA] Sin hallazgos simulados ({confidence:.1f}% de confianza)"
        )
        return InferenceOutput(
            detected=detected,
            confidence=round(confidence, 2),
            detections=detections,
            processing_time_ms=int((time.perf_counter() - start) * 1000),
            model_version=self.MODEL_VERSION,
            is_simulated=True,
            message=message,
        )


class InferenceUnavailable(RuntimeError):
    """El servicio de inferencia no respondió o respondió algo que no cumple el contrato."""


REQUIRED_FIELDS = ("detected", "confidence", "model_version")


class HttpInferenceProvider(InferenceProvider):
    """Cliente del servicio de inferencia: POST {INFERENCE_URL}/predict con la imagen (multipart).

    Contrato de respuesta: detected, confidence (0-100), detections, processing_time_ms, model_version,
    is_simulated, clinically_validated y message. Ver backend/inference_service/README.md.
    """

    def __init__(
        self, base_url: str, token: str = "", timeout: float = 60.0, client: httpx.Client | None = None
    ):
        self.base_url = base_url.rstrip("/")
        self.token = token
        self.timeout = timeout
        self.client = client

    def _headers(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {self.token}"} if self.token else {}

    def analyze(self, image_bytes: bytes) -> InferenceOutput:
        start = time.perf_counter()
        try:
            response = (self.client or httpx).post(
                f"{self.base_url}/predict",
                files={"file": ("image", image_bytes, "application/octet-stream")},
                headers=self._headers(),
                timeout=self.timeout,
            )
            response.raise_for_status()
            data = response.json()
        except (httpx.HTTPError, ValueError) as exc:
            raise InferenceUnavailable(f"{type(exc).__name__}: {exc}") from exc
        missing = [f for f in REQUIRED_FIELDS if f not in data]
        if missing:
            raise InferenceUnavailable(f"Respuesta sin los campos {', '.join(missing)}")
        try:
            confidence = float(data["confidence"])
        except (TypeError, ValueError) as exc:
            raise InferenceUnavailable("confidence no es numérico") from exc
        if not 0 <= confidence <= 100:
            raise InferenceUnavailable("confidence fuera de 0-100")
        return InferenceOutput(
            detected=bool(data["detected"]),
            confidence=round(confidence, 2),
            detections=list(data.get("detections") or []),
            processing_time_ms=int(data.get("processing_time_ms") or (time.perf_counter() - start) * 1000),
            model_version=str(data["model_version"])[:200],
            # Un servicio real nunca debe decir que es simulado, pero si lo dice, se respeta la marca
            is_simulated=bool(data.get("is_simulated", False)),
            clinically_validated=bool(data.get("clinically_validated", False)),
            message=str(data.get("message", ""))[:2000],
        )

    def status(self) -> dict[str, Any]:
        """Estado del servicio (GET /health) para mostrar en la interfaz si el modelo está conectado."""
        try:
            response = (self.client or httpx).get(
                f"{self.base_url}/health", headers=self._headers(), timeout=5.0
            )
            response.raise_for_status()
            data = response.json()
            return {
                "reachable": True,
                "model_version": data.get("model_version"),
                "device": data.get("device"),
                "clinically_validated": bool(data.get("clinically_validated", False)),
            }
        except (httpx.HTTPError, ValueError) as exc:
            return {"reachable": False, "error": type(exc).__name__}


class FallbackProvider(InferenceProvider):
    """Usa el servicio real y, si no responde, la IA simulada (con su marca): la plataforma nunca se queda sin
    resultado porque el PC o la instancia del modelo estén apagados."""

    def __init__(self, primary: HttpInferenceProvider, fallback: InferenceProvider | None = None):
        self.primary = primary
        self.fallback = fallback or SimulatedProvider()

    def analyze(self, image_bytes: bytes) -> InferenceOutput:
        try:
            return self.primary.analyze(image_bytes)
        except InferenceUnavailable as exc:
            logger.warning("Servicio de inferencia no disponible (%s); se usa la IA simulada", exc)
            output = self.fallback.analyze(image_bytes)
            output.message = f"{output.message}. El modelo no estaba disponible: resultado simulado"
            return output

    def status(self) -> dict[str, Any]:
        return self.primary.status()


# Nombre anterior (Sprint 4): se mantiene por compatibilidad
HttpYoloProvider = HttpInferenceProvider


@lru_cache
def get_provider() -> InferenceProvider:
    if settings.INFERENCE_PROVIDER == "http":
        http = HttpInferenceProvider(
            settings.INFERENCE_URL, settings.INFERENCE_API_TOKEN, settings.INFERENCE_TIMEOUT_SECONDS
        )
        return FallbackProvider(http) if settings.INFERENCE_FALLBACK_SIMULATED else http
    return SimulatedProvider()


def provider_status() -> dict[str, Any]:
    """Qué proveedor está configurado y si el modelo real responde."""
    provider = get_provider()
    if isinstance(provider, SimulatedProvider):
        return {"provider": "simulated", "reachable": None, "fallback": False}
    info = provider.status()
    info.update(provider="http", fallback=isinstance(provider, FallbackProvider))
    return info
