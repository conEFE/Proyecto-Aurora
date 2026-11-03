"""Validación médica del resultado de IA y evaluación del triage."""

import pytest

from app.db.models.audit_log import AuditLog
from app.db.models.inference_result import InferenceResult
from app.db.models.review import AIValidation, ClinicalReview
from app.services.dashboard_service import metrics
from app.tests.conftest import auth
from app.tests.factories import create_case
from app.tests.test_images import make_png, upload
from app.tests.test_reviews_reports import REVIEW


def _case_with_image(client, h, detected: bool, db, **case_fields):
    case = create_case(client, h, **case_fields)
    image_id = upload(client, h, case["id"], make_png()).json()["id"]
    # Fijar el resultado simulado para que el test no dependa del hash de la imagen
    result = db.query(InferenceResult).filter(InferenceResult.image_id == image_id).one()
    result.detected = detected
    result.confidence = 80.0 if detected else 95.0
    db.commit()
    return case, image_id


def _validate(client, h, case_id, image_id, verdict, comment=None):
    return client.put(
        f"/cases/{case_id}/images/{image_id}/validation",
        json={"verdict": verdict, "comment": comment},
        headers=h,
    )


def test_medico_validates_ai_result(client, tokens, users, db):
    h = auth(tokens["MEDICO"])
    case, image_id = _case_with_image(client, h, True, db)
    r = _validate(client, h, case["id"], image_id, "FALSO_POSITIVO", "Imagen sin lesión al revisar")
    assert r.status_code == 200
    body = r.json()
    assert body["verdict"] == "FALSO_POSITIVO"
    assert body["medico_id"] == users["MEDICO"].id
    assert body["ai_detected"] is True and body["ai_was_simulated"] is True
    assert body["ai_model_version"] == "simulado-v1"
    # Se muestra en el listado de imágenes del médico
    listing = client.get(f"/cases/{case['id']}/images", headers=h).json()
    assert listing[0]["validation"]["verdict"] == "FALSO_POSITIVO"


def test_validation_can_be_corrected_and_is_audited(client, tokens, db):
    h = auth(tokens["MEDICO"])
    case, image_id = _case_with_image(client, h, True, db)
    _validate(client, h, case["id"], image_id, "FALSO_POSITIVO")
    _validate(client, h, case["id"], image_id, "CONCORDANTE")
    assert db.query(AIValidation).count() == 1
    assert db.query(AIValidation).one().verdict == "CONCORDANTE"
    audit = [
        a
        for a in db.query(AuditLog).filter(AuditLog.entity == "image").all()
        if a.detail and "ai_validation" in a.detail
    ]
    assert [a.action for a in audit] == ["CREATE", "UPDATE"]
    assert audit[1].detail["previous"] == "FALSO_POSITIVO"


@pytest.mark.parametrize(
    "detected,verdict,status",
    [
        (True, "FALSO_POSITIVO", 200),
        (True, "FALSO_NEGATIVO", 422),
        (False, "FALSO_NEGATIVO", 200),
        (False, "FALSO_POSITIVO", 422),
        (False, "CONCORDANTE", 200),
        (True, "NO_EVALUABLE", 200),
        (True, "TAL_VEZ", 422),
    ],
)
def test_verdict_must_match_ai_output(client, tokens, db, detected, verdict, status):
    h = auth(tokens["MEDICO"])
    case, image_id = _case_with_image(client, h, detected, db)
    assert _validate(client, h, case["id"], image_id, verdict).status_code == status


def test_only_medico_validates(client, tokens, db):
    h_med = auth(tokens["MEDICO"])
    case, image_id = _case_with_image(client, h_med, True, db)
    for role in ("ADMINISTRATIVO", "ADMIN"):
        assert _validate(client, auth(tokens[role]), case["id"], image_id, "CONCORDANTE").status_code == 403


def test_case_cannot_close_without_ai_validation(client, tokens, db):
    h = auth(tokens["MEDICO"])
    case, image_id = _case_with_image(client, h, True, db)
    client.post(f"/cases/{case['id']}/take", headers=h)
    r = client.post(f"/cases/{case['id']}/review", json=REVIEW, headers=h)
    assert r.status_code == 409
    assert "validar el resultado de IA" in r.json()["detail"]
    _validate(client, h, case["id"], image_id, "CONCORDANTE")
    assert client.post(f"/cases/{case['id']}/review", json=REVIEW, headers=h).status_code == 201
    # Cerrado: la validación queda fija
    assert _validate(client, h, case["id"], image_id, "FALSO_POSITIVO").status_code == 409


def test_review_requires_triage_assessment(client, tokens):
    h = auth(tokens["MEDICO"])
    case = create_case(client, h)
    client.post(f"/cases/{case['id']}/take", headers=h)
    payload = {k: v for k, v in REVIEW.items() if k != "triage_assessment"}
    assert client.post(f"/cases/{case['id']}/review", json=payload, headers=h).status_code == 422
    bad = {**REVIEW, "triage_assessment": "QUIZAS"}
    assert client.post(f"/cases/{case['id']}/review", json=bad, headers=h).status_code == 422


def test_review_stores_triage_assessment_snapshot(client, tokens, db):
    h = auth(tokens["MEDICO"])
    case = create_case(client, h, birads_reported=4)
    client.post(f"/cases/{case['id']}/take", headers=h)
    review = {
        **REVIEW,
        "triage_assessment": "SOBREESTIMADO",
        "triage_comment": "BI-RADS 4 por calcificaciones benignas",
    }
    r = client.post(f"/cases/{case['id']}/review", json=review, headers=h)
    assert r.status_code == 201
    body = r.json()
    assert body["triage_assessment"] == "SOBREESTIMADO"
    assert body["triage_level_at_review"] == "ALTA"
    assert body["triage_config_version_at_review"] == 1
    assert body["triage_comment"].startswith("BI-RADS 4")
    meta = client.get(f"/cases/{case['id']}/reports/metadata", headers=h).json()
    assert meta["TriageAssessment"] == "SOBREESTIMADO"


def test_report_metadata_includes_ai_validation(client, tokens, db):
    h = auth(tokens["MEDICO"])
    case, image_id = _case_with_image(client, h, True, db)
    client.post(f"/cases/{case['id']}/take", headers=h)
    _validate(client, h, case["id"], image_id, "FALSO_POSITIVO")
    client.post(f"/cases/{case['id']}/review", json=REVIEW, headers=h)
    meta = client.get(f"/cases/{case['id']}/reports/metadata", headers=h).json()
    assert meta["AIValidation"] == "FALSO_POSITIVO x1"


def test_dashboard_agreement_metrics(client, tokens, db):
    h = auth(tokens["MEDICO"])
    plan = [
        (True, "CONCORDANTE", "APROPIADO"),
        (True, "FALSO_POSITIVO", "SOBREESTIMADO"),
        (False, "CONCORDANTE", "APROPIADO"),
        (False, "FALSO_NEGATIVO", "SUBESTIMADO"),
        (True, "NO_EVALUABLE", "APROPIADO"),
    ]
    for detected, verdict, assessment in plan:
        case, image_id = _case_with_image(client, h, detected, db)
        client.post(f"/cases/{case['id']}/take", headers=h)
        _validate(client, h, case["id"], image_id, verdict)
        r = client.post(
            f"/cases/{case['id']}/review", json={**REVIEW, "triage_assessment": assessment}, headers=h
        )
        assert r.status_code == 201, r.text

    m = metrics(db)
    assert m.ai_validations_total == 5
    assert m.ai_validations_by_verdict == {
        "CONCORDANTE": 2,
        "FALSO_POSITIVO": 1,
        "FALSO_NEGATIVO": 1,
        "NO_EVALUABLE": 1,
    }
    assert m.ai_agreement_rate == 0.5  # 2 concordantes de 4 evaluables
    assert m.ai_validations_simulated == 5
    assert m.triage_assessments_by_value == {"APROPIADO": 3, "SOBREESTIMADO": 1, "SUBESTIMADO": 1}
    assert m.triage_agreement_rate == 0.6
    assert db.query(ClinicalReview).count() == 5

    api = client.get("/dashboard/metrics", headers=auth(tokens["ADMIN"])).json()
    assert api["ai_agreement_rate"] == 0.5 and api["triage_agreement_rate"] == 0.6
