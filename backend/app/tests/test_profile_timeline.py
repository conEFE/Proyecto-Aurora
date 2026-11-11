"""Mi perfil (datos propios y cambio de email) y línea de tiempo del paciente."""

from app.db.models.audit_log import AuditLog
from app.tests.conftest import PASSWORD, auth
from app.tests.factories import create_case, create_patient
from app.tests.test_images import make_png, upload
from app.tests.test_reviews_reports import _take_and_review

# --- Mi perfil -------------------------------------------------------------------


def test_me_includes_profile_dates(client, tokens):
    r = client.get("/auth/me", headers=auth(tokens["MEDICO"]))
    assert r.status_code == 200
    body = r.json()
    assert body["created_at"] is not None
    assert body["last_login_at"] is not None
    assert "password_changed_at" in body


def test_change_own_email(client, tokens, users, db):
    h = auth(tokens["ADMINISTRATIVO"])
    r = client.put(
        "/auth/me/email", json={"email": "nuevo@aurora-demo.cl", "current_password": PASSWORD}, headers=h
    )
    assert r.status_code == 200, r.text
    assert r.json()["email"] == "nuevo@aurora-demo.cl"
    assert client.get("/auth/me", headers=h).json()["email"] == "nuevo@aurora-demo.cl"
    entry = (
        db.query(AuditLog)
        .filter(
            AuditLog.action == "UPDATE",
            AuditLog.entity == "user",
            AuditLog.entity_id == users["ADMINISTRATIVO"].id,
        )
        .one()
    )
    assert entry.detail == {"fields": ["email"], "self_service": True}
    # La sesión sigue válida (el email no revoca tokens)
    assert client.get("/auth/me", headers=h).status_code == 200


def test_change_email_requires_current_password(client, tokens):
    r = client.put(
        "/auth/me/email",
        json={"email": "otro@aurora-demo.cl", "current_password": "incorrecta"},
        headers=auth(tokens["MEDICO"]),
    )
    assert r.status_code == 422
    assert "contraseña actual" in r.json()["detail"]


def test_change_email_rejects_duplicate_and_invalid(client, tokens):
    h = auth(tokens["MEDICO"])
    taken = "ocupado@aurora-demo.cl"
    ok = client.put(
        "/auth/me/email", json={"email": taken, "current_password": PASSWORD}, headers=auth(tokens["ADMIN"])
    )
    assert ok.status_code == 200, ok.text
    r = client.put("/auth/me/email", json={"email": taken, "current_password": PASSWORD}, headers=h)
    assert r.status_code == 409
    r = client.put("/auth/me/email", json={"email": "no-es-email", "current_password": PASSWORD}, headers=h)
    assert r.status_code == 422


def test_change_email_requires_login(client):
    r = client.put("/auth/me/email", json={"email": "x@aurora-demo.cl", "current_password": PASSWORD})
    assert r.status_code == 401


# --- Línea de tiempo del paciente ----------------------------------------------------


def _kinds(events):
    return [e["kind"] for e in events]


def test_timeline_full_history_for_medico(client, tokens, db):
    h = auth(tokens["MEDICO"])
    patient = create_patient(client, h)
    case = create_case(client, h, patient["id"], palpable_mass=True)
    upload(client, h, case["id"], make_png(), laterality="L")
    _take_and_review(client, h, case["id"])

    r = client.get(f"/patients/{patient['id']}/timeline", headers=h)
    assert r.status_code == 200, r.text
    events = r.json()
    kinds = _kinds(events)
    for kind in (
        "PATIENT_REGISTERED",
        "CONSENT_GRANTED",
        "CASE_CREATED",
        "IMAGES_UPLOADED",
        "REVIEW_REGISTERED",
        "CASE_CLOSED",
    ):
        assert kind in kinds, kind
    # Del más reciente al más antiguo
    stamps = [e["at"] for e in events]
    assert stamps == sorted(stamps, reverse=True)
    created = next(e for e in events if e["kind"] == "CASE_CREATED")
    assert created["case_code"] == case["code"]
    assert created["detail"]["symptoms"] == ["masa palpable"]
    assert created["actor_name"]
    review = next(e for e in events if e["kind"] == "REVIEW_REGISTERED")
    assert review["detail"] == {"birads_final": 4, "recommendation": "BIOPSIA"}
    assert next(e for e in events if e["kind"] == "IMAGES_UPLOADED")["detail"]["count"] == 1
    assert (
        db.query(AuditLog)
        .filter(AuditLog.action == "VIEW", AuditLog.entity == "patient", AuditLog.entity_id == patient["id"])
        .filter(AuditLog.detail["timeline"].astext == "true")
        .count()
        == 1
    )


def test_timeline_hides_clinical_events_from_administrativo(client, tokens):
    hm = auth(tokens["MEDICO"])
    patient = create_patient(client, hm)
    case = create_case(client, hm, patient["id"])
    upload(client, hm, case["id"], make_png(), laterality="R")
    _take_and_review(client, hm, case["id"])

    r = client.get(f"/patients/{patient['id']}/timeline", headers=auth(tokens["ADMINISTRATIVO"]))
    assert r.status_code == 200
    kinds = _kinds(r.json())
    assert "CASE_CREATED" in kinds and "CASE_CLOSED" in kinds
    assert "REVIEW_REGISTERED" not in kinds
    assert "TRIAGE_OVERRIDE" not in kinds


def test_timeline_includes_consent_withdrawal(client, tokens):
    h = auth(tokens["MEDICO"])
    patient = create_patient(client, h)
    r = client.post(
        f"/patients/{patient['id']}/consent/withdraw", json={"reason": "Lo pidió la paciente"}, headers=h
    )
    assert r.status_code == 200, r.text
    events = client.get(f"/patients/{patient['id']}/timeline", headers=h).json()
    assert events[0]["kind"] == "CONSENT_WITHDRAWN"
    assert events[0]["detail"]["note"] == "Lo pidió la paciente"


def test_timeline_permissions_and_not_found(client, tokens):
    h = auth(tokens["MEDICO"])
    patient = create_patient(client, h)
    assert client.get(f"/patients/{patient['id']}/timeline", headers=auth(tokens["ADMIN"])).status_code == 403
    assert client.get("/patients/999999/timeline", headers=h).status_code == 404
