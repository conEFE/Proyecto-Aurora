import hashlib
from datetime import datetime, timedelta, timezone

import pytest

from app.db.models.audit_log import AuditLog
from app.db.models.case import Case, CaseStatus
from app.db.models.review import Report, RequestMetric
from app.db.models.triage import TriageResult
from app.services import case_service
from app.services.dashboard_service import metrics, percentile
from app.services.errors import ConflictError
from app.tests.conftest import auth
from app.tests.factories import birth_date_for_age, create_case, create_patient
from app.tests.test_images import make_png, upload

REVIEW = {
    "birads_final": 4,
    "findings": "Nódulo espiculado en CSE izquierdo",
    "recommendation": "BIOPSIA",
    "triage_assessment": "APROPIADO",
}


def _validate_all(client, h, case_id, verdict=None):
    """Valida el resultado de IA de cada imagen analizada del caso."""
    for img in client.get(f"/cases/{case_id}/images", headers=h).json():
        if img["inference"]:
            v = verdict or "CONCORDANTE"
            r = client.put(f"/cases/{case_id}/images/{img['id']}/validation", json={"verdict": v}, headers=h)
            assert r.status_code == 200, r.text


def _take_and_review(client, h, case_id, review=None):
    assert client.post(f"/cases/{case_id}/take", headers=h).status_code == 200
    _validate_all(client, h, case_id)
    r = client.post(f"/cases/{case_id}/review", json=review or REVIEW, headers=h)
    assert r.status_code == 201, r.text
    return r.json()


# --- Toma y revisión -----------------------------------------------------------


def test_take_assigns_medico_and_moves_to_review(client, tokens, users):
    h = auth(tokens["MEDICO"])
    case = create_case(client, h)
    r = client.post(f"/cases/{case['id']}/take", headers=h)
    assert r.status_code == 200
    assert r.json()["status"] == "EN_REVISION"
    assert r.json()["assigned_medico_id"] == users["MEDICO"].id
    # Tomar dos veces no es una transición válida
    assert client.post(f"/cases/{case['id']}/take", headers=h).status_code == 409


def test_review_closes_case(client, tokens, users, db):
    h = auth(tokens["MEDICO"])
    case = create_case(client, h)
    review = _take_and_review(client, h, case["id"])
    assert review["medico_id"] == users["MEDICO"].id
    c = client.get(f"/cases/{case['id']}", headers=h).json()
    assert c["status"] == "CERRADO" and c["closed_at"] is not None
    assert client.get(f"/cases/{case['id']}/review", headers=h).json()["recommendation"] == "BIOPSIA"


def test_case_closes_only_with_review(client, tokens):
    h = auth(tokens["MEDICO"])
    case = create_case(client, h)
    # Sin tomar el caso (PRIORIZADO) no se puede registrar la revisión
    assert client.post(f"/cases/{case['id']}/review", json=REVIEW, headers=h).status_code == 409
    # No existe otra vía para cerrar: PATCH no acepta status
    client.patch(f"/cases/{case['id']}", json={"status": "CERRADO"}, headers=h)
    assert client.get(f"/cases/{case['id']}", headers=h).json()["status"] == "PRIORIZADO"
    # La máquina de estados no permite saltar a CERRADO
    c = Case(status=CaseStatus.PRIORIZADO)
    with pytest.raises(ConflictError):
        case_service.transition(c, CaseStatus.CERRADO)


def test_second_review_is_409(client, tokens):
    h = auth(tokens["MEDICO"])
    case = create_case(client, h)
    _take_and_review(client, h, case["id"])
    assert client.post(f"/cases/{case['id']}/review", json=REVIEW, headers=h).status_code == 409


@pytest.mark.parametrize(
    "payload",
    [
        {**REVIEW, "birads_final": 7},
        {**REVIEW, "findings": ""},
        {**REVIEW, "recommendation": "OPERAR"},
        {"birads_final": 2, "recommendation": "CONTROL_RUTINA"},
    ],
)
def test_review_validation(client, tokens, payload):
    h = auth(tokens["MEDICO"])
    case = create_case(client, h)
    client.post(f"/cases/{case['id']}/take", headers=h)
    assert client.post(f"/cases/{case['id']}/review", json=payload, headers=h).status_code == 422


def test_only_medico_takes_and_reviews(client, tokens):
    h_adm = auth(tokens["ADMINISTRATIVO"])
    case = create_case(client, h_adm)
    assert client.post(f"/cases/{case['id']}/take", headers=h_adm).status_code == 403
    assert client.post(f"/cases/{case['id']}/review", json=REVIEW, headers=h_adm).status_code == 403


def test_closed_case_is_not_recalculated(client, tokens, db):
    h = auth(tokens["MEDICO"])
    case = create_case(client, h)
    _take_and_review(client, h, case["id"])
    before = db.query(TriageResult).filter(TriageResult.case_id == case["id"]).count()
    assert client.post(f"/cases/{case['id']}/triage", headers=h).status_code == 409
    assert db.query(TriageResult).filter(TriageResult.case_id == case["id"]).count() == before


# --- Reportes ------------------------------------------------------------------


def test_report_requires_closed_case(client, tokens):
    h = auth(tokens["MEDICO"])
    case = create_case(client, h)
    assert client.get(f"/cases/{case['id']}/reports/metadata", headers=h).status_code == 409
    assert (
        client.post(f"/cases/{case['id']}/reports", json={"content_hash": "a" * 64}, headers=h).status_code
        == 409
    )


def test_report_registered_with_dicom_metadata_and_audited(client, tokens, db):
    h = auth(tokens["MEDICO"])
    case = create_case(client, h, birads_reported=4)
    upload(client, h, case["id"], make_png())
    _take_and_review(client, h, case["id"])

    meta = client.get(f"/cases/{case['id']}/reports/metadata", headers=h).json()
    assert meta["PatientID"] == case["code"]
    assert meta["Modality"] == "MG"
    assert len(meta["StudyDate"]) == 8
    assert meta["Findings"] == REVIEW["findings"]
    assert meta["AIIsSimulated"] is True
    assert meta["TriageLevel"] == "ALTA"
    # Nunca datos identificables del paciente
    assert case["patient"]["rut"] not in str(meta)
    assert case["patient"]["first_name"] not in str(meta)

    pdf_hash = hashlib.sha256(b"%PDF-1.7 contenido de prueba").hexdigest()
    r = client.post(f"/cases/{case['id']}/reports", json={"content_hash": pdf_hash}, headers=h)
    assert r.status_code == 201
    assert r.json()["content_hash"] == pdf_hash
    assert r.json()["dicom_metadata"]["PatientID"] == case["code"]
    assert db.query(Report).count() == 1
    export = db.query(AuditLog).filter(AuditLog.action == "EXPORT").one()
    assert export.entity == "report" and export.detail["sha256"] == pdf_hash
    assert len(client.get(f"/cases/{case['id']}/reports", headers=h).json()) == 1


def test_report_hash_must_be_sha256(client, tokens):
    h = auth(tokens["MEDICO"])
    case = create_case(client, h)
    _take_and_review(client, h, case["id"])
    assert (
        client.post(f"/cases/{case['id']}/reports", json={"content_hash": "xyz"}, headers=h).status_code
        == 422
    )


def test_report_only_medico(client, tokens):
    h_med = auth(tokens["MEDICO"])
    case = create_case(client, h_med)
    _take_and_review(client, h_med, case["id"])
    for role in ("ADMINISTRATIVO", "ADMIN"):
        r = client.post(
            f"/cases/{case['id']}/reports", json={"content_hash": "a" * 64}, headers=auth(tokens[role])
        )
        assert r.status_code == 403


# --- Dashboard -------------------------------------------------------------------


def test_percentile():
    assert percentile([], 95) is None
    assert percentile([10.0], 95) == 10.0
    assert percentile([float(i) for i in range(1, 101)], 95) == 95.0
    assert percentile([float(i) for i in range(1, 21)], 95) == 19.0


def test_metrics_with_controlled_data(client, tokens, db):
    h = auth(tokens["MEDICO"])
    young = create_patient(client, h, birth_date=birth_date_for_age(30))
    alta_old = create_case(client, h, young["id"], birads_reported=5)  # ALTA, pendiente
    alta_closed = create_case(client, h, young["id"], palpable_mass=True)  # ALTA, se cierra
    baja = create_case(client, h, young["id"])  # BAJA
    media = create_case(client, h, young["id"])
    client.post(
        f"/cases/{media['id']}/triage/override",
        json={"level": "MEDIA", "reason": "Criterio clínico"},
        headers=h,
    )
    _take_and_review(client, h, alta_closed["id"])

    now = datetime.now(timezone.utc)
    # Datos controlados: creación hace 2 días, primer triage 120 s después, revisión 6 h después del triage
    for c in (alta_old, alta_closed, baja, media):
        db.get(Case, c["id"]).created_at = now - timedelta(days=2)
    for r in db.query(TriageResult).all():
        r.computed_at = now - timedelta(days=2) + timedelta(seconds=120)
    from app.db.models.review import ClinicalReview

    rv = db.query(ClinicalReview).one()
    rv.created_at = now - timedelta(days=2) + timedelta(seconds=120) + timedelta(hours=6)
    db.query(RequestMetric).delete()
    for ms in [float(i) for i in range(1, 101)]:
        db.add(RequestMetric(method="GET", path="/x", status_code=200, duration_ms=ms))
    db.commit()

    m = metrics(db, now=now)
    assert m.total_cases == 4
    assert m.cases_by_status == {"ABIERTO": 0, "PRIORIZADO": 3, "EN_REVISION": 0, "CERRADO": 1}
    assert m.cases_by_level == {"ALTA": 2, "MEDIA": 1, "BAJA": 1}
    assert m.avg_creation_to_triage_seconds == 120.0
    assert m.avg_triage_to_review_hours_by_level["ALTA"] == 6.0
    assert m.avg_triage_to_review_hours_by_level["BAJA"] is None
    assert m.alta_pending_over_hours == 1  # alta_old: 48 h > 24 h y sin cerrar
    assert m.api_p95_ms == 95.0 and m.api_requests == 100
    assert m.triage_overrides == 1
    assert m.override_ratio == round(1 / m.triage_total, 4)
    assert sum(p.cases for p in m.cases_per_week) == 4

    # Filtro de fechas: nada creado en el futuro
    empty = metrics(db, date_from=now + timedelta(days=1), now=now)
    assert empty.total_cases == 0 and empty.override_ratio is None


@pytest.mark.parametrize("role", ["ADMIN", "MEDICO", "ADMINISTRATIVO"])
def test_metrics_endpoint_for_all_roles(client, tokens, role):
    r = client.get("/dashboard/metrics?alta_pending_hours=12", headers=auth(tokens[role]))
    assert r.status_code == 200
    body = r.json()
    assert body["alta_pending_threshold_hours"] == 12
    assert "cases_by_level" in body and "api_p95_ms" in body


def test_requests_are_measured(client, tokens, db):
    client.get("/auth/me", headers=auth(tokens["MEDICO"]))
    paths = {m.path for m in db.query(RequestMetric).all()}
    assert "/auth/me" in paths
    assert "/health" not in paths


def test_legacy_endpoints_removed(client, tokens):
    h = auth(tokens["MEDICO"])
    assert client.get("/reports/statistics", headers=h).status_code == 404
    assert client.get("/reports/monthly", headers=h).status_code == 404
    assert client.get("/user/tickets", headers=h).status_code == 404
    assert client.post("/images/1/results", headers=h).status_code == 404


# --- E2E -------------------------------------------------------------------------


def test_e2e_full_flow(client, tokens, users, db):
    """Paciente → caso → imagen → triage → revisión → reporte, con los roles reales del proceso."""
    h_adm = auth(tokens["ADMINISTRATIVO"])
    h_med = auth(tokens["MEDICO"])

    # 1. ADMINISTRATIVO registra a la paciente con consentimiento y crea el caso con síntomas
    patient = create_patient(
        client, h_adm, birth_date=birth_date_for_age(58), family_history_first_degree=True
    )
    case = create_case(client, h_adm, patient["id"], palpable_mass=True)
    assert case["status"] == "PRIORIZADO" and case["triage_level"] == "ALTA"

    # 2. ADMINISTRATIVO carga la mamografía; la inferencia simulada corre sola
    img = upload(client, h_adm, case["id"], make_png(color=(200, 10, 10)), laterality="L")
    assert img.status_code == 201

    # 3. La cola lo muestra; el médico recibe la notificación
    queue = client.get("/triage/queue", headers=h_med).json()
    assert queue[0]["code"] == case["code"] and queue[0]["level"] == "ALTA"
    notes = client.get("/notifications", headers=h_med).json()
    assert any(case["code"] in n["message"] for n in notes)

    # 4. El médico ve el triage (con IA simulada considerada) y la imagen
    triage = client.get(f"/cases/{case['id']}/triage", headers=h_med).json()
    assert triage["escalation_rule"] == "R_SINTOMA"
    assert triage["breakdown"]["ai_is_simulated"] is True
    assert triage["breakdown"]["images_analyzed"] == 1
    assert client.get(f"/cases/{case['id']}/images/{img.json()['id']}/file", headers=h_med).status_code == 200

    # 5. Toma el caso, registra la revisión y lo cierra
    _take_and_review(client, h_med, case["id"])
    assert (
        client.patch(f"/cases/{case['id']}", json={"palpable_mass": False}, headers=h_med).status_code == 409
    )

    # 6. Genera el reporte y lo registra
    meta = client.get(f"/cases/{case['id']}/reports/metadata", headers=h_med).json()
    pdf_hash = hashlib.sha256(repr(meta).encode()).hexdigest()
    rep = client.post(f"/cases/{case['id']}/reports", json={"content_hash": pdf_hash}, headers=h_med)
    assert rep.status_code == 201

    # 7. El dashboard refleja el caso cerrado y el ADMIN ve la trazabilidad completa
    m = client.get("/dashboard/metrics", headers=auth(tokens["ADMIN"])).json()
    assert m["cases_by_status"]["CERRADO"] == 1
    actions = {
        a["action"]
        for a in client.get("/admin/audit?size=200", headers=auth(tokens["ADMIN"])).json()["items"]
    }
    assert {"LOGIN_OK", "CREATE", "VIEW", "UPDATE", "EXPORT"} <= actions
