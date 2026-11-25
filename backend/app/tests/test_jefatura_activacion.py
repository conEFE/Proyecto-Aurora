"""Ficha del médico (nombre, apellido, especialidad), activación por email y comparador de médicos (JEFATURA)."""

import re
from datetime import datetime, timedelta, timezone

import pytest

from app.db.models.email_token import EmailToken
from app.db.models.user import User, UserRole
from app.services import email_service
from app.tests.conftest import auth, login, make_user
from app.tests.factories import create_case
from app.tests.test_reviews_reports import _take_and_review


@pytest.fixture(autouse=True)
def _clean_outbox():
    email_service.outbox.clear()
    yield
    email_service.outbox.clear()


def _payload(**over):
    data = {
        "rut": "15555555-6",
        "email": "dra.ficticia@aurora-demo.cl",
        "first_name": "Ana María",
        "last_name": "Pérez Soto",
        "role": "MEDICO",
        "specialty": "GINECOLOGIA",
    }
    data.update(over)
    return data


def _token_from_outbox() -> str:
    assert email_service.outbox, "no se envió ningún email"
    m = re.search(r"/activar\?token=([\w-]+)", email_service.outbox[-1].text)
    assert m
    return m.group(1)


# --- Ficha del médico ------------------------------------------------------------------------


def test_create_doctor_with_names_and_specialty(client, tokens):
    r = client.post("/admin/users", json=_payload(), headers=auth(tokens["ADMIN"]))
    assert r.status_code == 201, r.text
    body = r.json()
    assert body["first_name"] == "Ana María" and body["last_name"] == "Pérez Soto"
    assert body["full_name"] == "Ana María Pérez Soto"
    assert body["specialty"] == "GINECOLOGIA"
    assert body["email_verified_at"] is None and body["activation_sent"] is True


def test_doctor_requires_specialty_and_last_name(client, tokens):
    h = auth(tokens["ADMIN"])
    r = client.post("/admin/users", json=_payload(specialty=None), headers=h)
    assert r.status_code == 422 and "especialidad" in r.text
    r = client.post("/admin/users", json=_payload(last_name=""), headers=h)
    assert r.status_code == 422 and "apellido" in r.text


def test_specialty_only_for_doctors(client, tokens):
    h = auth(tokens["ADMIN"])
    r = client.post("/admin/users", json=_payload(role="JEFATURA"), headers=h)
    assert r.status_code == 201 and r.json()["specialty"] is None
    uid = r.json()["id"]
    assert client.patch(f"/admin/users/{uid}", json={"specialty": "ONCOLOGIA"}, headers=h).status_code == 422
    r = client.patch(f"/admin/users/{uid}", json={"role": "MEDICO", "specialty": "ONCOLOGIA"}, headers=h)
    assert r.status_code == 200 and r.json()["specialty"] == "ONCOLOGIA"
    r = client.patch(f"/admin/users/{uid}", json={"last_name": "Rojas"}, headers=h)
    assert r.json()["full_name"] == "Ana María Rojas"


# --- Activación por email --------------------------------------------------------------------


def test_activation_link_sets_password_and_verifies_email(client, tokens, db):
    r = client.post("/admin/users", json=_payload(), headers=auth(tokens["ADMIN"]))
    assert r.status_code == 201
    token = _token_from_outbox()
    assert email_service.outbox[-1].to == "dra.ficticia@aurora-demo.cl"
    # Solo se guarda el hash
    assert db.query(EmailToken).filter(EmailToken.token_hash == token).count() == 0

    preview = client.get("/auth/activation", params={"token": token})
    assert preview.status_code == 200 and preview.json()["first_name"] == "Ana María"

    assert client.post("/auth/activate", json={"token": token, "password": "corta"}).status_code == 422
    r = client.post("/auth/activate", json={"token": token, "password": "Nueva-Clave-2026"})
    assert r.status_code == 200, r.text
    assert r.json()["must_change_password"] is False
    me = client.get("/auth/me", headers=auth(r.json()["access_token"])).json()
    assert me["email_verified"] is True and me["specialty"] == "GINECOLOGIA"
    login(client, "15555555-6", "Nueva-Clave-2026")

    # Un solo uso
    assert (
        client.post("/auth/activate", json={"token": token, "password": "Otra-Clave-2026"}).status_code == 422
    )


def test_expired_and_resent_links(client, tokens, db):
    h = auth(tokens["ADMIN"])
    uid = client.post("/admin/users", json=_payload(), headers=h).json()["id"]
    old = _token_from_outbox()
    db.query(EmailToken).update({EmailToken.expires_at: datetime.now(timezone.utc) - timedelta(minutes=1)})
    db.commit()
    r = client.post("/auth/activate", json={"token": old, "password": "Nueva-Clave-2026"})
    assert r.status_code == 422 and "venció" in r.text

    r = client.post(f"/admin/users/{uid}/resend-activation", headers=h)
    assert r.status_code == 200 and r.json()["sent"] is True
    new = _token_from_outbox()
    assert new != old
    assert (
        client.post("/auth/activate", json={"token": new, "password": "Nueva-Clave-2026"}).status_code == 200
    )
    # Ya verificado: no se reenvía
    assert client.post(f"/admin/users/{uid}/resend-activation", headers=h).status_code == 422


def test_temp_password_still_works_without_activation(client, tokens):
    r = client.post(
        "/admin/users",
        json=_payload(password="Temporal-2026a", send_activation=False),
        headers=auth(tokens["ADMIN"]),
    )
    assert r.status_code == 201 and r.json()["activation_sent"] is None
    assert email_service.outbox == []
    assert (
        client.post("/auth/login", json={"rut": "15555555-6", "password": "Temporal-2026a"}).status_code
        == 200
    )


def test_email_change_requires_new_verification(client, tokens, users, db):
    h = auth(tokens["ADMIN"])
    medico = users["MEDICO"]
    medico.email_verified_at = datetime.now(timezone.utc)
    db.commit()
    r = client.patch(f"/admin/users/{medico.id}", json={"email": "otro@aurora-demo.cl"}, headers=h)
    assert r.status_code == 200 and r.json()["email_verified_at"] is None


def test_invalid_token_is_rejected(client):
    assert client.get("/auth/activation", params={"token": "x" * 40}).status_code == 422


# --- JEFATURA y comparador de médicos ---------------------------------------------------------


@pytest.fixture
def jefatura_token(client, db):
    make_user(db, UserRole.JEFATURA, "44444444-4")
    return login(client, "44444444-4")


def test_jefatura_has_no_clinical_access(client, jefatura_token):
    h = auth(jefatura_token)
    for path in ("/patients", "/cases", "/triage/queue", "/admin/users", "/dashboard/model-performance"):
        assert client.get(path, headers=h).status_code == 403, path
    assert client.get("/dashboard/metrics", headers=h).status_code == 200


def test_compare_doctors_permissions(client, tokens, jefatura_token):
    assert client.get("/dashboard/doctors/compare", headers=auth(jefatura_token)).status_code == 200
    assert client.get("/dashboard/doctors/compare", headers=auth(tokens["ADMIN"])).status_code == 200
    for role in ("MEDICO", "ADMINISTRATIVO"):
        assert client.get("/dashboard/doctors/compare", headers=auth(tokens[role])).status_code == 403


def test_compare_doctors_counts_activity(client, tokens, users, db, jefatura_token):
    h_med = auth(tokens["MEDICO"])
    for _ in range(2):
        case = create_case(client, h_med)
        _take_and_review(client, h_med, case["id"])
    other = make_user(db, UserRole.MEDICO, "16666666-1", first_name="Luis", last_name="Ríos", full_name=None)
    assert other.full_name == "Luis Ríos"

    r = client.get(
        "/dashboard/doctors/compare",
        params=[("ids", users["MEDICO"].id), ("ids", other.id)],
        headers=auth(jefatura_token),
    )
    assert r.status_code == 200, r.text
    body = r.json()
    by_id = {d["id"]: d for d in body["doctors"]}
    me = by_id[users["MEDICO"].id]
    assert me["reviews"] == 2 and me["cases_closed"] == 2 and me["open_assigned"] == 0
    assert me["triage_agreement_rate"] == 1.0 and me["avg_review_hours"] is not None
    assert by_id[other.id]["reviews"] == 0 and by_id[other.id]["avg_review_hours"] is None
    assert body["team"]["reviews"] == 1

    # Filtro por especialidad: el médico de prueba no tiene especialidad asignada
    db.query(User).filter(User.id == other.id).update({User.specialty: "ONCOLOGIA"})
    db.commit()
    r = client.get(
        "/dashboard/doctors/compare", params={"specialty": "ONCOLOGIA"}, headers=auth(jefatura_token)
    )
    assert [d["id"] for d in r.json()["doctors"]] == [other.id]
