"""Proveedores de inferencia (D10). El resultado del proveedor simulado SIEMPRE lleva is_simulated=True."""

import hashlib
import random
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from functools import lru_cache
from typing import Any

import httpx

from app.config import settings


@dataclass
class InferenceOutput:
    detected: bool
    confidence: float  # 0-100
    detections: list[dict[str, Any]] = field(default_factory=list)
    processing_time_ms: int = 0
    model_version: str = ""
    is_simulated: bool = True
    message: str = ""


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


class HttpYoloProvider(InferenceProvider):
    """Cliente del servicio de inferencia YOLO (POST {INFERENCE_URL}/predict). Stub hasta el Sprint 8."""

    def __init__(self, base_url: str, timeout: float = 30.0):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def analyze(self, image_bytes: bytes) -> InferenceOutput:
        start = time.perf_counter()
        response = httpx.post(
            f"{self.base_url}/predict",
            files={"file": ("image", image_bytes, "application/octet-stream")},
            timeout=self.timeout,
        )
        response.raise_for_status()
        data = response.json()
        return InferenceOutput(
            detected=bool(data["detected"]),
            confidence=float(data["confidence"]),
            detections=list(data.get("detections", [])),
            processing_time_ms=int(data.get("processing_time_ms") or (time.perf_counter() - start) * 1000),
            model_version=str(data.get("model_version", "yolo-desconocido")),
            is_simulated=bool(data.get("is_simulated", False)),
            message=str(data.get("message", "")),
        )


@lru_cache
def get_provider() -> InferenceProvider:
    if settings.INFERENCE_PROVIDER == "http":
        return HttpYoloProvider(settings.INFERENCE_URL)
    return SimulatedProvider()
