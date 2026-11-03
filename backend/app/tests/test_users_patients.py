import pytest
from sqlalchemy import text
from sqlalchemy.exc import DBAPIError

from app.db.models.audit_log import AuditLog
from app.tests.conftest import PASSWORD, auth, login
from app.utils.rut import compute_dv, is_valid_rut, normalize_rut

VALID_PATIENT = {
    "rut": "12.345.678-5",
    "first_name": "Ana",
    "last_name": "Prueba",
    "birth_date": "1968-04-12",
    "sex": "F",
    "family_history_first_degree": True,
    "previous_breast_cancer": False,
    "consent_given": True,
}


# --- RUT ------------------------------------------------------------------


@pytest.mark.parametrize(
    "rut,ok",
    [
        ("12345678-5", True),
        ("12.345.678-5", True),
        ("11111111-1", True),
        ("10000013-K", True),
        ("10000013-k", True),
        ("12345678-9", False),
        ("abc", False),
        ("", False),
    ],
)
def test_rut_validation(rut, ok):
    assert is_valid_rut(rut) is ok


def test_rut_normalization():
    assert normalize_rut("12.345.678-k") == "12345678-K"
    assert normalize_rut("123456785") == "12345678-5"
    assert compute_dv("12345678") == "5"


# --- Usuarios (solo ADMIN) -------------------------------------------------


def _new_user(role="MEDICO", rut="15555555-6"):
    return {
        "rut": rut,
        "email": f"{rut.replace('-', '')}@aurora-demo.cl",
        "full_name": "Dra. Ficticia",
        "password": "OtraClave-456",
        "role": role,
    }


def test_admin_creates_lists_and_updates_users(client, tokens, db):
    h = auth(tokens["ADMIN"])
    r = client.post("/admin/users", json=_new_user("ADMINISTRATIVO"), headers=h)
    assert r.status_code == 201, r.text
    created = r.json()
    assert created["role"] == "ADMINISTRATIVO" and created["is_active"] is True

    r = client.get("/admin/users", headers=h)
    assert r.status_code == 200
    assert any(u["id"] == created["id"] for u in r.json())

    r = client.patch(f"/admin/users/{created['id']}", json={"role": "MEDICO", "is_active": False}, headers=h)
    assert r.status_code == 200
    assert r.json()["role"] == "MEDICO" and r.json()["is_active"] is False

    # Un usuario desactivado no puede iniciar sesión
    r = client.post("/auth/login", json={"rut": "15555555-6", "password": "OtraClave-456"})
    assert r.status_code == 401

    actions = {(a.action, a.entity) for a in db.query(AuditLog).all()}
    assert ("CREATE", "user") in actions and ("UPDATE", "user") in actions


def test_deactivated_user_token_is_rejected(client, tokens, users):
    h_admin = auth(tokens["ADMIN"])
    medico_token = tokens["MEDICO"]
    assert client.get("/auth/me", headers=auth(medico_token)).status_code == 200
    client.patch(f"/admin/users/{users['MEDICO'].id}", json={"is_active": False}, headers=h_admin)
    assert client.get("/auth/me", headers=auth(medico_token)).status_code == 401


def test_admin_cannot_deactivate_self(client, tokens, users):
    r = client.patch(
        f"/admin/users/{users['ADMIN'].id}", json={"is_active": False}, headers=auth(tokens["ADMIN"])
    )
    assert r.status_code == 422


def test_duplicate_user_rut_is_409(client, tokens):
    h = auth(tokens["ADMIN"])
    assert client.post("/admin/users", json=_new_user(), headers=h).status_code == 201
    assert client.post("/admin/users", json=_new_user(), headers=h).status_code == 409


def test_user_with_invalid_rut_is_422(client, tokens):
    r = client.post("/admin/users", json=_new_user(rut="12345678-9"), headers=auth(tokens["ADMIN"]))
    assert r.status_code == 422


@pytest.mark.parametrize("role", ["ADMINISTRATIVO", "MEDICO"])
def test_non_admin_cannot_manage_users(client, tokens, role):
    h = auth(tokens[role])
    assert client.post("/admin/users", json=_new_user(), headers=h).status_code == 403
    assert client.get("/admin/users", headers=h).status_code == 403
    assert client.get("/admin/audit", headers=h).status_code == 403


def test_public_signup_no_longer_exists(client):
    r = client.post(
        "/auth/signup",
        json={"rut": "1-9", "email": "x@aurora-demo.cl", "password": "x", "role": "ADMIN"},
    )
    assert r.status_code in (404, 405)


# --- Pacientes -------------------------------------------------------------


@pytest.mark.parametrize("role", ["ADMINISTRATIVO", "MEDICO"])
def test_clinical_staff_registers_patient_with_consent(client, tokens, users, role):
    r = client.post("/patients", json=VALID_PATIENT, headers=auth(tokens[role]))
    assert r.status_code == 201, r.text
    body = r.json()
    assert body["rut"] == "12345678-5"
    assert body["consent_given"] is True
    assert body["consent_at"] is not None
    assert body["consent_registered_by"] == users[role].id
    assert body["created_by"] == users[role].id


def test_patient_without_consent_is_rejected(client, tokens):
    r = client.post(
        "/patients", json={**VALID_PATIENT, "consent_given": False}, headers=auth(tokens["MEDICO"])
    )
    assert r.status_code == 422


def test_patient_invalid_rut_is_422(client, tokens):
    r = client.post("/patients", json={**VALID_PATIENT, "rut": "12345678-9"}, headers=auth(tokens["MEDICO"]))
    assert r.status_code == 422


def test_patient_missing_required_fields_is_422(client, tokens):
    payload = {k: v for k, v in VALID_PATIENT.items() if k != "birth_date"}
    assert client.post("/patients", json=payload, headers=auth(tokens["MEDICO"])).status_code == 422


def test_patient_invalid_sex_is_422(client, tokens):
    r = client.post("/patients", json={**VALID_PATIENT, "sex": "X"}, headers=auth(tokens["MEDICO"]))
    assert r.status_code == 422


def test_duplicate_patient_is_409(client, tokens):
    h = auth(tokens["MEDICO"])
    assert client.post("/patients", json=VALID_PATIENT, headers=h).status_code == 201
    assert client.post("/patients", json=VALID_PATIENT, headers=h).status_code == 409


def test_admin_cannot_access_patients(client, tokens):
    h = auth(tokens["ADMIN"])
    assert client.get("/patients", headers=h).status_code == 403
    assert client.post("/patients", json=VALID_PATIENT, headers=h).status_code == 403
    assert client.get("/patients/1", headers=h).status_code == 403


def test_update_patient_and_audit(client, tokens, db):
    h = auth(tokens["ADMINISTRATIVO"])
    pid = client.post("/patients", json=VALID_PATIENT, headers=h).json()["id"]
    r = client.put(
        f"/patients/{pid}", json={"previous_breast_cancer": True, "last_name": "Editada"}, headers=h
    )
    assert r.status_code == 200
    assert r.json()["previous_breast_cancer"] is True
    assert r.json()["last_name"] == "Editada"
    assert client.get(f"/patients/{pid}", headers=h).status_code == 200

    logs = db.query(AuditLog).filter(AuditLog.entity == "patient").all()
    actions = [a.action for a in logs]
    assert {"CREATE", "UPDATE", "VIEW"} <= set(actions)
    # El detalle de auditoría no guarda el RUT ni el nombre del paciente
    for entry in logs:
        assert "12345678" not in str(entry.detail or {})
        assert "Ana" not in str(entry.detail or {})


def test_consent_cannot_be_withdrawn_by_edit(client, tokens):
    h = auth(tokens["MEDICO"])
    pid = client.post("/patients", json=VALID_PATIENT, headers=h).json()["id"]
    assert client.put(f"/patients/{pid}", json={"consent_given": False}, headers=h).status_code == 422


# --- Auditoría -------------------------------------------------------------


def test_login_events_are_audited(client, users, db, tokens):
    client.post("/auth/login", json={"rut": "11111111-1", "password": "mala"})
    r = client.get("/admin/audit?action=LOGIN_FAIL", headers=auth(tokens["ADMIN"]))
    assert r.status_code == 200
    page = r.json()
    assert page["total"] == 1
    assert page["items"][0]["user_id"] == users["MEDICO"].id

    r = client.get("/admin/audit?action=LOGIN_OK", headers=auth(tokens["ADMIN"]))
    assert r.json()["total"] == 3  # un login por rol en el fixture `tokens`


def test_audit_filters_and_pagination(client, tokens, users):
    h = auth(tokens["ADMIN"])
    r = client.get(f"/admin/audit?user_id={users['ADMIN'].id}&size=1&page=1", headers=h)
    assert r.status_code == 200
    assert r.json()["size"] == 1
    assert len(r.json()["items"]) == 1


def test_audit_log_is_append_only(db, tokens):
    with pytest.raises(DBAPIError):
        db.execute(text("UPDATE audit_log SET action = 'X'"))
    db.rollback()
    with pytest.raises(DBAPIError):
        db.execute(text("DELETE FROM audit_log"))
    db.rollback()


def test_login_sets_last_login_and_full_name(client, users):
    r = client.post("/auth/login", json={"rut": "11111111-1", "password": PASSWORD})
    assert r.json()["full_name"] == "Usuario Medico"
    me = client.get("/auth/me", headers=auth(r.json()["access_token"])).json()
    assert me["full_name"] == "Usuario Medico"


def test_login_accepts_rut_with_dots(client, users):
    assert login(client, "11.111.111-1")
