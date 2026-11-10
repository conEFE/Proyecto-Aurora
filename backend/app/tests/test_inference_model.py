"""2.6.0: modelo de inferencia real (prototipo) por HTTP, con token, respaldo simulado, reanálisis y marca de
modelo no validado. Los tests no necesitan PyTorch: el servicio se simula con httpx.MockTransport."""

import importlib.util
import sys
import types
from pathlib import Path

import httpx
import pytest
from fastapi.testclient import TestClient

from app.db.models.inference_result import InferenceResult
from app.db.models.triage import TriageResult
from app.inference import providers
from app.inference.providers import (
    FallbackProvider,
    HttpInferenceProvider,
    InferenceUnavailable,
    SimulatedProvider,
)
from app.services import image_service
from app.tests.conftest import auth
from app.tests.factories import create_case
from app.tests.test_images import make_png, upload
from app.tests.test_reviews_reports import _take_and_review

TOKEN = "token-de-prueba-del-modelo"
PROTOTYPE = "cnn-resnet18-672x1024+yolo11s-masa-1280"


def model_response(**overrides):
    data = {
        "detected": True,
        "confidence": 72.5,
        "probability": 0.725,
        "threshold": 0.35,
        "detections": [
            {"x": 0.2, "y": 0.3, "width": 0.1, "height": 0.1, "confidence": 0.81, "class_name": "masa"}
        ],
        "processing_time_ms": 640,
        "model_version": PROTOTYPE,
        "is_simulated": False,
        "clinically_validated": False,
        "message": "Probabilidad de malignidad 72,5% (sobre el umbral de 35%). Masas marcadas: 1.",
    }
    data.update(overrides)
    return data


def http_provider(handler, token=TOKEN):
    return HttpInferenceProvider(
        "http://modelo.test:8080", token, 5.0, client=httpx.Client(transport=httpx.MockTransport(handler))
    )


def ok_handler(seen=None):
    def handler(request: httpx.Request):
        if seen is not None:
            seen.append(request)
        if request.url.path == "/health":
            return httpx.Response(200, json={"status": "ok", "model_version": PROTOTYPE, "device": "cuda:0"})
        return httpx.Response(200, json=model_response())

    return handler


def down_handler(request: httpx.Request):
    raise httpx.ConnectError("conexión rechazada", request=request)


@pytest.fixture
def use_provider(monkeypatch):
    def _use(provider):
        monkeypatch.setattr(image_service, "get_provider", lambda: provider)
        monkeypatch.setattr(providers, "get_provider", lambda: provider)
        return provider

    return _use


# --- Cliente HTTP -------------------------------------------------------------------------------


def test_http_provider_sends_token_and_parses_contract():
    seen = []
    out = http_provider(ok_handler(seen)).analyze(b"imagen")
    assert seen[0].headers["Authorization"] == f"Bearer {TOKEN}"
    assert seen[0].url.path == "/predict"
    assert out.is_simulated is False and out.clinically_validated is False
    assert out.confidence == 72.5 and out.detected is True and out.model_version == PROTOTYPE
    assert out.detections[0]["class_name"] == "masa"


def test_http_provider_without_token_sends_no_header():
    seen = []
    http_provider(ok_handler(seen), token="").analyze(b"x")
    assert "Authorization" not in seen[0].headers


@pytest.mark.parametrize(
    "handler",
    [
        down_handler,
        lambda r: httpx.Response(500, json={"detail": "error"}),
        lambda r: httpx.Response(401, json={"detail": "Token inválido"}),
        lambda r: httpx.Response(200, content=b"no es json"),
        lambda r: httpx.Response(200, json={"detected": True}),  # faltan campos
        lambda r: httpx.Response(200, json=model_response(confidence=150)),
        lambda r: httpx.Response(200, json=model_response(confidence="alto")),
    ],
)
def test_http_provider_rejects_failures_and_broken_contract(handler):
    with pytest.raises(InferenceUnavailable):
        http_provider(handler).analyze(b"x")


def test_fallback_uses_simulated_and_marks_it():
    out = FallbackProvider(http_provider(down_handler)).analyze(b"imagen")
    assert out.is_simulated is True and out.clinically_validated is False
    assert out.model_version == SimulatedProvider.MODEL_VERSION
    assert out.message.startswith("[IA SIMULADA]") and "no estaba disponible" in out.message


def test_get_provider_from_settings(monkeypatch):
    from app.config import settings

    providers.get_provider.cache_clear()
    try:
        monkeypatch.setattr(settings, "INFERENCE_PROVIDER", "http")
        monkeypatch.setattr(settings, "INFERENCE_FALLBACK_SIMULATED", True)
        assert isinstance(providers.get_provider(), FallbackProvider)
        providers.get_provider.cache_clear()
        monkeypatch.setattr(settings, "INFERENCE_FALLBACK_SIMULATED", False)
        assert isinstance(providers.get_provider(), HttpInferenceProvider)
        providers.get_provider.cache_clear()
        monkeypatch.setattr(settings, "INFERENCE_PROVIDER", "simulated")
        assert isinstance(providers.get_provider(), SimulatedProvider)
    finally:
        providers.get_provider.cache_clear()


# --- Plataforma con el modelo real --------------------------------------------------------------


def test_upload_with_real_model_is_stored_as_prototype(client, tokens, db, use_provider):
    use_provider(FallbackProvider(http_provider(ok_handler())))
    h = auth(tokens["MEDICO"])
    case = create_case(client, h)
    image_id = upload(client, h, case["id"], make_png()).json()["id"]

    result = db.query(InferenceResult).filter(InferenceResult.image_id == image_id).one()
    assert result.is_simulated is False and result.clinically_validated is False
    assert result.model_version == PROTOTYPE
    listing = client.get(f"/cases/{case['id']}/images", headers=h).json()
    assert listing[0]["inference"]["clinically_validated"] is False

    triage = db.query(TriageResult).filter(TriageResult.case_id == case["id"], TriageResult.is_current).one()
    assert triage.breakdown["ai_is_simulated"] is False
    assert triage.breakdown["ai_is_prototype"] is True


def test_report_metadata_marks_prototype_only_when_used(client, tokens, use_provider):
    h = auth(tokens["MEDICO"])
    simulated_case = create_case(client, h, birads_reported=4)
    upload(client, h, simulated_case["id"], make_png())
    _take_and_review(client, h, simulated_case["id"])
    meta = client.get(f"/cases/{simulated_case['id']}/reports/metadata", headers=h).json()
    assert "AIIsPrototype" not in meta  # los reportes anteriores conservan su contenido (y su firma)

    use_provider(FallbackProvider(http_provider(ok_handler())))
    real_case = create_case(client, h, birads_reported=4)
    upload(client, h, real_case["id"], make_png(color=(10, 200, 30)))
    _take_and_review(client, h, real_case["id"])
    meta = client.get(f"/cases/{real_case['id']}/reports/metadata", headers=h).json()
    assert meta["AIIsPrototype"] is True and meta["AIIsSimulated"] is False


def test_model_down_on_upload_falls_back_then_reanalyze(client, tokens, db, use_provider):
    use_provider(FallbackProvider(http_provider(down_handler)))
    h = auth(tokens["MEDICO"])
    case = create_case(client, h)
    image_id = upload(client, h, case["id"], make_png()).json()["id"]
    result = db.query(InferenceResult).filter(InferenceResult.image_id == image_id).one()
    assert result.is_simulated is True  # la imagen no quedó sin resultado

    url = f"/cases/{case['id']}/images/{image_id}/inference/retry"
    # El modelo sigue apagado: 503 y no se reemplaza nada
    r = client.post(url, headers=h)
    assert r.status_code == 503
    # El modelo vuelve: el reanálisis reemplaza el resultado simulado y recalcula el triage
    use_provider(FallbackProvider(http_provider(ok_handler())))
    r = client.post(url, headers=h)
    assert r.status_code == 200, r.text
    assert r.json()["is_simulated"] is False and r.json()["model_version"] == PROTOTYPE
    db.expire_all()
    assert db.query(InferenceResult).filter(InferenceResult.image_id == image_id).count() == 1
    triage = db.query(TriageResult).filter(TriageResult.case_id == case["id"], TriageResult.is_current).one()
    assert triage.breakdown["ai_is_prototype"] is True
    # Ya tiene el resultado del modelo: no se vuelve a analizar
    assert client.post(url, headers=h).status_code == 409


def test_reanalyze_rules(client, tokens, db, use_provider):
    h = auth(tokens["MEDICO"])
    case = create_case(client, h)
    image_id = upload(client, h, case["id"], make_png()).json()["id"]
    url = f"/cases/{case['id']}/images/{image_id}/inference/retry"
    # Con la IA simulada configurada no hay modelo con qué reanalizar
    r = client.post(url, headers=h)
    assert r.status_code == 409 and "IA simulada" in r.json()["detail"]
    # Solo MEDICO
    assert client.post(url, headers=auth(tokens["ADMINISTRATIVO"])).status_code == 403
    # Imagen de otro caso
    other = create_case(client, h)
    use_provider(FallbackProvider(http_provider(ok_handler())))
    assert (
        client.post(f"/cases/{other['id']}/images/{image_id}/inference/retry", headers=h).status_code == 404
    )


def test_reanalyze_does_not_replace_validated_result(client, tokens, use_provider):
    from app.tests.test_validation import _validate

    h = auth(tokens["MEDICO"])
    case = create_case(client, h)
    image_id = upload(client, h, case["id"], make_png()).json()["id"]
    client.post(f"/cases/{case['id']}/take", headers=h)
    assert _validate(client, h, case["id"], image_id, "NO_EVALUABLE").status_code == 200
    use_provider(FallbackProvider(http_provider(ok_handler())))
    r = client.post(f"/cases/{case['id']}/images/{image_id}/inference/retry", headers=h)
    assert r.status_code == 409 and "validó" in r.json()["detail"]


def test_inference_status(client, tokens, use_provider):
    h = auth(tokens["ADMIN"])
    assert client.get("/inference/status", headers=h).json()["provider"] == "simulated"
    use_provider(FallbackProvider(http_provider(ok_handler())))
    data = client.get("/inference/status", headers=h).json()
    assert data["provider"] == "http" and data["reachable"] is True and data["fallback"] is True
    assert data["model_version"] == PROTOTYPE and data["clinically_validated"] is False
    assert "url" not in data
    use_provider(FallbackProvider(http_provider(down_handler)))
    data = client.get("/inference/status", headers=auth(tokens["ADMINISTRATIVO"])).json()
    assert data["reachable"] is False


# --- Servicio de inferencia (contrato), con el analizador simulado ----------------------------------


@pytest.fixture
def inference_app(monkeypatch):
    """Carga backend/inference_service/app.py sin PyTorch: el módulo `analyzer` se reemplaza por uno falso."""
    fake = types.ModuleType("analyzer")
    fake.CLINICALLY_VALIDATED = False
    fake.DEVICE = "cpu"
    fake.MODEL_VERSION = PROTOTYPE

    class FakeAnalyzer:
        def analyze(self, content: bytes) -> dict:
            if content == b"no-es-imagen":
                raise ValueError("El archivo no es una imagen PNG, JPEG ni DICOM válida")
            return model_response()

    fake.Analyzer = FakeAnalyzer
    monkeypatch.setitem(sys.modules, "analyzer", fake)
    monkeypatch.setenv("INFERENCE_API_TOKEN", TOKEN)
    monkeypatch.setenv("MAX_UPLOAD_MB", "1")
    path = Path(__file__).resolve().parents[2] / "inference_service" / "app.py"
    spec = importlib.util.spec_from_file_location("aurora_inference_app", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.app


def test_inference_service_requires_token(inference_app):
    c = TestClient(inference_app)
    assert c.get("/health").status_code == 401
    assert c.get("/health", headers={"Authorization": "Bearer otro"}).status_code == 401
    r = c.get("/health", headers={"Authorization": f"Bearer {TOKEN}"})
    assert r.status_code == 200 and r.json()["clinically_validated"] is False
    assert c.post("/predict", files={"file": ("m.png", b"x")}).status_code == 401


def test_inference_service_contract_matches_platform(inference_app):
    c = TestClient(inference_app)
    h = {"Authorization": f"Bearer {TOKEN}"}
    r = c.post("/predict", files={"file": ("m.png", b"imagen")}, headers=h)
    assert r.status_code == 200
    # Lo que responde el servicio lo entiende el cliente de la plataforma
    out = http_provider(lambda req: httpx.Response(200, json=r.json())).analyze(b"imagen")
    assert out.is_simulated is False and out.clinically_validated is False
    assert c.post("/predict", files={"file": ("m.png", b"")}, headers=h).status_code == 400
    assert c.post("/predict", files={"file": ("m.png", b"no-es-imagen")}, headers=h).status_code == 415
    big = b"0" * (1024 * 1024 + 10)
    assert c.post("/predict", files={"file": ("m.png", big)}, headers=h).status_code == 413
    assert c.get("/docs").status_code == 200  # ENABLE_API_DOCS por defecto en local
