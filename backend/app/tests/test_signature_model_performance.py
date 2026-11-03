"""Firma (conformidad) del médico sobre el reporte y desempeño del modelo por versión (2.2.0)."""

import hashlib
import re

import pytest

from app.db.models.audit_log import AuditLog
from app.db.models.inference_result import InferenceResult
from app.db.models.review import ClinicalReview, ReportSignature
from app.db.models.user import UserRole
from app.services import dashboard_service
from app.services.dashboard_service import wilson_interval
from app.tests.conftest import auth, login, make_user
from app.tests.factories import create_case
from app.tests.test_images import make_png, upload
from app.tests.test_reviews_reports import _sign, _take_and_review
from app.tests.test_validation import _validate


def _closed_case(client, h):
    case = create_case(client, h, birads_reported=4)
    upload(client, h, case["id"], make_png())
    _take_and_review(client, h, case["id"])
    return case


# --- Firma del reporte -------------------------------------------------------------


def test_sign_requires_closed_case(client, tokens):
    h = auth(tokens["MEDICO"])
    case = create_case(client, h)
    assert _sign(client, h, case["id"]).status_code == 409


def test_sign_with_wrong_password_is_rejected_and_audited(client, tokens, db):
    h = auth(tokens["MEDICO"])
    case = _closed_case(client, h)
    r = _sign(client, h, case["id"], password="no-es-la-clave")
    assert r.status_code == 422
    assert db.query(ReportSignature).count() == 0
    assert db.query(AuditLog).filter(AuditLog.action == "SIGN_FAIL").count() == 1


def test_only_the_reviewing_medico_signs(client, tokens, db):
    h = auth(tokens["MEDICO"])
    case = _closed_case(client, h)
    other = make_user(db, UserRole.MEDICO, "44444444-4")
    assert _sign(client, auth(login(client, other.rut)), case["id"]).status_code == 403
    for role in ("ADMIN", "ADMINISTRATIVO"):
        assert _sign(client, auth(tokens[role]), case["id"]).status_code == 403


def test_signature_is_registered_audited_and_verifiable(client, tokens, users, db):
    h = auth(tokens["MEDICO"])
    case = _closed_case(client, h)
    r = _sign(client, h, case["id"])
    assert r.status_code == 201, r.text
    body = r.json()
    assert body["valid"] is True
    assert body["medico_id"] == users["MEDICO"].id
    assert re.fullmatch(r"[0-9A-F]{4}(-[0-9A-F]{4}){3}", body["verification_code"])
    audit = db.query(AuditLog).filter(AuditLog.action == "SIGN").one()
    assert audit.detail["content_sha256"] == body["content_hash"]
    # Una sola firma por caso
    assert _sign(client, h, case["id"]).status_code == 409
    assert client.get(f"/cases/{case['id']}/reports/signature", headers=h).json()["valid"] is True


def test_metadata_carries_signature_over_its_own_content(client, tokens):
    h = auth(tokens["MEDICO"])
    case = _closed_case(client, h)
    assert "MedicalSignature" not in client.get(f"/cases/{case['id']}/reports/metadata", headers=h).json()
    sig = _sign(client, h, case["id"]).json()
    meta = client.get(f"/cases/{case['id']}/reports/metadata", headers=h).json()
    block = meta["MedicalSignature"]
    assert block["VerificationCode"] == sig["verification_code"]
    assert block["ContentSHA256"] == sig["content_hash"]


def test_report_cannot_be_issued_without_signature(client, tokens):
    h = auth(tokens["MEDICO"])
    case = _closed_case(client, h)
    pdf_hash = hashlib.sha256(b"%PDF-1.7").hexdigest()
    assert (
        client.post(f"/cases/{case['id']}/reports", json={"content_hash": pdf_hash}, headers=h).status_code
        == 409
    )
    sig = _sign(client, h, case["id"]).json()
    r = client.post(f"/cases/{case['id']}/reports", json={"content_hash": pdf_hash}, headers=h)
    assert r.status_code == 201
    assert r.json()["signature_id"] == sig["id"]


def test_changed_content_invalidates_signature(client, tokens, db):
    h = auth(tokens["MEDICO"])
    case = _closed_case(client, h)
    _sign(client, h, case["id"])
    review = db.query(ClinicalReview).filter(ClinicalReview.case_id == case["id"]).one()
    review.findings = "Texto alterado fuera de la aplicación"
    db.commit()
    assert client.get(f"/cases/{case['id']}/reports/signature", headers=h).json()["valid"] is False


def test_signature_not_found_before_signing(client, tokens):
    h = auth(tokens["MEDICO"])
    case = _closed_case(client, h)
    assert client.get(f"/cases/{case['id']}/reports/signature", headers=h).status_code == 404


# --- Desempeño del modelo por versión ------------------------------------------------


def _validated_image(client, h, db, version, simulated, detected, verdict):
    case = create_case(client, h)
    image_id = upload(client, h, case["id"], make_png()).json()["id"]
    result = db.query(InferenceResult).filter(InferenceResult.image_id == image_id).one()
    result.detected = detected
    result.model_version = version
    result.is_simulated = simulated
    db.commit()
    assert _validate(client, h, case["id"], image_id, verdict).status_code == 200


# VP 3, VN 2, FP 1, FN 1 y 1 no evaluable para la versión real; 1 VP para la simulada
SAMPLE = (
    [("yolo-v1", False, True, "CONCORDANTE")] * 3
    + [("yolo-v1", False, False, "CONCORDANTE")] * 2
    + [("yolo-v1", False, True, "FALSO_POSITIVO")]
    + [("yolo-v1", False, False, "FALSO_NEGATIVO")]
    + [("yolo-v1", False, True, "NO_EVALUABLE")]
    + [("simulado-v1", True, True, "CONCORDANTE")]
)


def test_model_performance_by_version(client, tokens, db):
    h = auth(tokens["MEDICO"])
    for row in SAMPLE:
        _validated_image(client, h, db, *row)
    r = client.get("/dashboard/model-performance", headers=h)
    assert r.status_code == 200
    body = r.json()
    assert body["k5_target"] == 0.9
    by_version = {v["model_version"]: v for v in body["versions"]}
    # Primero los resultados reales, después los simulados
    assert [v["model_version"] for v in body["versions"]] == ["yolo-v1", "simulado-v1"]

    real = by_version["yolo-v1"]
    assert (
        real["true_positives"],
        real["true_negatives"],
        real["false_positives"],
        real["false_negatives"],
    ) == (
        3,
        2,
        1,
        1,
    )
    assert real["validations"] == 8 and real["evaluable"] == 7 and real["not_evaluable"] == 1
    assert real["accuracy"] == pytest.approx(5 / 7, abs=1e-4)
    assert real["sensitivity"] == 0.75
    assert real["specificity"] == pytest.approx(2 / 3, abs=1e-4)
    assert real["ppv"] == 0.75
    assert real["npv"] == pytest.approx(2 / 3, abs=1e-4)
    lo, hi = real["accuracy_ci95"]
    assert lo < real["accuracy"] < hi
    # Muestra menor al mínimo: el K5 no se evalúa
    assert real["meets_k5"] is None

    sim = by_version["simulado-v1"]
    assert sim["is_simulated"] is True and sim["meets_k5"] is None


def test_k5_is_evaluated_only_for_real_results_with_enough_sample(client, tokens, db, monkeypatch):
    monkeypatch.setattr(dashboard_service, "K5_MIN_SAMPLE", 5)
    h = auth(tokens["MEDICO"])
    for row in SAMPLE:
        _validated_image(client, h, db, *row)
    versions = {
        v["model_version"]: v
        for v in client.get("/dashboard/model-performance", headers=h).json()["versions"]
    }
    assert versions["yolo-v1"]["meets_k5"] is False  # 71,4 % < 90 %
    assert versions["simulado-v1"]["meets_k5"] is None  # nunca con IA simulada


def test_model_performance_roles(client, tokens):
    assert client.get("/dashboard/model-performance", headers=auth(tokens["ADMIN"])).status_code == 200
    assert (
        client.get("/dashboard/model-performance", headers=auth(tokens["ADMINISTRATIVO"])).status_code == 403
    )


def test_model_performance_empty(client, tokens):
    assert client.get("/dashboard/model-performance", headers=auth(tokens["MEDICO"])).json()["versions"] == []


def test_wilson_interval():
    assert wilson_interval(0, 0) is None
    lo, hi = wilson_interval(10, 10)
    assert lo == pytest.approx(0.7225, abs=1e-3) and hi == 1.0
    lo, hi = wilson_interval(5, 7)
    assert lo == pytest.approx(0.359, abs=1e-3) and hi == pytest.approx(0.918, abs=1e-3)
