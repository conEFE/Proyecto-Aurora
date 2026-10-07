import hashlib
import io
from pathlib import Path

import pytest
from cryptography.fernet import Fernet, InvalidToken
from PIL import Image as PILImage

from app.config import settings
from app.db.models.audit_log import AuditLog
from app.db.models.case import Case, CaseStatus
from app.db.models.image import Image
from app.db.models.inference_result import InferenceResult
from app.inference.providers import SimulatedProvider
from app.storage.local import LocalEncryptedStorage, StorageConfigError
from app.tests.conftest import auth
from app.tests.factories import create_case


def make_png(size=(256, 256), color=(120, 40, 200), noise=False) -> bytes:
    if noise:
        import os

        img = PILImage.frombytes("RGB", size, os.urandom(size[0] * size[1] * 3))
    else:
        img = PILImage.new("RGB", size, color)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def make_jpeg(size=(200, 200)) -> bytes:
    buf = io.BytesIO()
    PILImage.new("RGB", size, (10, 200, 30)).save(buf, format="JPEG")
    return buf.getvalue()


def upload(client, headers, case_id, content, filename="mamo.png", **form):
    data = {"exam_type": "MAMOGRAFIA", **form}
    return client.post(
        f"/cases/{case_id}/images",
        files={"file": (filename, content, "application/octet-stream")},
        data=data,
        headers=headers,
    )


@pytest.mark.parametrize("role", ["ADMINISTRATIVO", "MEDICO"])
def test_upload_png_and_jpeg(client, tokens, users, db, role):
    h = auth(tokens[role])
    case = create_case(client, h)
    png = make_png()
    r = upload(client, h, case["id"], png, laterality="L")
    assert r.status_code == 201, r.text
    body = r.json()
    assert body["exam_type"] == "MAMOGRAFIA"
    assert body["laterality"] == "L"
    assert body["uploaded_by"] == users[role].id
    assert body["sha256"] == hashlib.sha256(png).hexdigest()
    assert body["mime_type"] == "image/png"

    r = upload(client, h, case["id"], make_jpeg(), filename="eco.jpg", exam_type="ECOGRAFIA", laterality="R")
    assert r.status_code == 201, r.text
    assert r.json()["mime_type"] == "image/jpeg"
    assert r.json()["exam_type"] == "ECOGRAFIA"


def test_upload_rejects_oversized_file(client, tokens, monkeypatch):
    h = auth(tokens["MEDICO"])
    case = create_case(client, h)
    monkeypatch.setattr(settings, "MAX_UPLOAD_MB", 1)
    big = make_png(size=(800, 800), noise=True)
    assert len(big) > 1024 * 1024
    r = upload(client, h, case["id"], big)
    assert r.status_code == 413
    assert "1 MB" in r.json()["detail"]


def test_default_limit_is_60mb():
    assert settings.MAX_UPLOAD_MB == 60


def test_upload_rejects_non_image_and_other_formats(client, tokens):
    h = auth(tokens["MEDICO"])
    case = create_case(client, h)
    assert upload(client, h, case["id"], b"%PDF-1.4 no es imagen", filename="x.pdf").status_code == 415
    buf = io.BytesIO()
    PILImage.new("RGB", (200, 200)).save(buf, format="GIF")
    assert upload(client, h, case["id"], buf.getvalue(), filename="x.gif").status_code == 415


def test_upload_rejects_tiny_image_and_bad_laterality(client, tokens):
    h = auth(tokens["MEDICO"])
    case = create_case(client, h)
    assert upload(client, h, case["id"], make_png(size=(50, 50))).status_code == 422
    assert upload(client, h, case["id"], make_png(), laterality="X").status_code == 422


def test_file_is_encrypted_on_disk(client, tokens, db):
    h = auth(tokens["MEDICO"])
    case = create_case(client, h)
    png = make_png()
    image_id = upload(client, h, case["id"], png, filename="Juana Perez.png").json()["id"]
    image = db.get(Image, image_id)
    on_disk = (Path(settings.FILES_DIR) / image.filepath).read_bytes()

    assert on_disk != png
    assert b"PNG" not in on_disk[:64]
    assert "Juana" not in image.filepath  # el nombre en disco es aleatorio
    # No es legible con otra clave
    with pytest.raises(InvalidToken):
        Fernet(Fernet.generate_key()).decrypt(on_disk)
    # Con la clave correcta se recupera el original
    storage = LocalEncryptedStorage(settings.FILES_DIR, settings.ENCRYPTION_KEY)
    assert storage.load(image.filepath) == png


def test_storage_requires_encryption_key(tmp_path):
    with pytest.raises(StorageConfigError):
        LocalEncryptedStorage(str(tmp_path), "")


def test_storage_rejects_path_traversal(tmp_path):
    storage = LocalEncryptedStorage(str(tmp_path), Fernet.generate_key().decode())
    with pytest.raises(ValueError):
        storage.save("../fuera.bin", b"x")


def test_administrativo_uploads_but_cannot_view(client, tokens):
    h_adm = auth(tokens["ADMINISTRATIVO"])
    case = create_case(client, h_adm)
    image_id = upload(client, h_adm, case["id"], make_png()).json()["id"]

    assert client.get(f"/cases/{case['id']}/images/{image_id}/file", headers=h_adm).status_code == 403
    assert client.get(f"/cases/{case['id']}/images/{image_id}/inference", headers=h_adm).status_code == 403
    listing = client.get(f"/cases/{case['id']}/images", headers=h_adm).json()
    assert listing[0]["inference"] is None  # sin resultados de IA para ADMINISTRATIVO

    h_med = auth(tokens["MEDICO"])
    r = client.get(f"/cases/{case['id']}/images/{image_id}/file", headers=h_med)
    assert r.status_code == 200
    assert r.content == make_png()
    assert r.headers["content-type"] == "image/png"


def test_admin_cannot_upload_or_view(client, tokens):
    h_med = auth(tokens["MEDICO"])
    case = create_case(client, h_med)
    h = auth(tokens["ADMIN"])
    assert upload(client, h, case["id"], make_png()).status_code == 403
    assert client.get(f"/cases/{case['id']}/images", headers=h).status_code == 403


def test_view_file_is_audited(client, tokens, db):
    h = auth(tokens["MEDICO"])
    case = create_case(client, h)
    image_id = upload(client, h, case["id"], make_png()).json()["id"]
    client.get(f"/cases/{case['id']}/images/{image_id}/file", headers=h)
    entries = db.query(AuditLog).filter(AuditLog.entity == "image", AuditLog.action == "VIEW").all()
    assert len(entries) == 1 and entries[0].entity_id == image_id


def test_inference_runs_automatically_and_is_marked_simulated(client, tokens, db):
    h = auth(tokens["MEDICO"])
    case = create_case(client, h)
    image_id = upload(client, h, case["id"], make_png()).json()["id"]
    # TestClient ejecuta las BackgroundTasks al terminar la request
    result = db.query(InferenceResult).filter(InferenceResult.image_id == image_id).one()
    assert result.is_simulated is True
    assert result.model_version == "simulado-v1"
    assert result.message.startswith("[IA SIMULADA]")

    r = client.get(f"/cases/{case['id']}/images/{image_id}/inference", headers=h)
    assert r.status_code == 200
    assert r.json()["is_simulated"] is True
    listing = client.get(f"/cases/{case['id']}/images", headers=h).json()
    assert listing[0]["inference"]["is_simulated"] is True
    assert listing[0]["inference_status"] == "LISTO"


def test_simulated_provider_is_deterministic_and_fast():
    provider = SimulatedProvider()
    a = provider.analyze(make_png(color=(1, 2, 3)))
    b = provider.analyze(make_png(color=(1, 2, 3)))
    assert a == b or (
        a.detected == b.detected and a.confidence == b.confidence and a.detections == b.detections
    )
    assert a.is_simulated is True
    assert a.processing_time_ms < 1000  # sin time.sleep
    outputs = {provider.analyze(make_png(color=(i, i, i))).detected for i in range(30)}
    assert outputs == {True, False}  # produce ambos resultados según la imagen


def test_cannot_upload_to_closed_case(client, tokens, db):
    h = auth(tokens["MEDICO"])
    case = create_case(client, h)
    db_case = db.get(Case, case["id"])
    db_case.status = CaseStatus.CERRADO
    db.commit()
    assert upload(client, h, case["id"], make_png()).status_code == 409


def test_upload_reopens_prioritized_case(client, tokens, db):
    h = auth(tokens["MEDICO"])
    case = create_case(client, h)
    db_case = db.get(Case, case["id"])
    db_case.status = CaseStatus.PRIORIZADO
    db.commit()
    upload(client, h, case["id"], make_png())
    db.expire_all()
    # Vuelve a ABIERTO al subir y la inferencia recalcula el triage → PRIORIZADO otra vez
    assert db.get(Case, case["id"]).status == CaseStatus.PRIORIZADO


def test_upload_to_missing_case_is_404(client, tokens):
    assert upload(client, auth(tokens["MEDICO"]), 999, make_png()).status_code == 404
