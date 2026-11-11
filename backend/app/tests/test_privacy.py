"""2.4.0: consentimiento versionado y retiro, bloqueo, exportación y solicitudes de los titulares (Ley 21.719)."""

import importlib.util
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from app.db.models.audit_log import AuditLog
from app.db.models.privacy import ConsentEvent, DataSubjectRequest
from app.services.consent_text import CONSENT_TEXT_BODY, CONSENT_TEXT_VERSION
from app.tests.conftest import auth
from app.tests.factories import create_case, create_patient, patient_payload


def _audit(db, action, entity="patient"):
    db.expire_all()
    return db.query(AuditLog).filter(AuditLog.action == action, AuditLog.entity == entity).all()


def _close_case(db, case_id):
    from app.db.models.case import Case, CaseStatus

    case = db.get(Case, case_id)
    case.status = CaseStatus.CERRADO
    case.closed_at = datetime.now(timezone.utc)
    db.commit()


# --- Texto de consentimiento ------------------------------------------------------------------


def test_active_consent_text(client, tokens):
    r = client.get("/privacy/consent-text", headers=auth(tokens["ADMINISTRATIVO"]))
    assert r.status_code == 200
    assert r.json()["version"] == CONSENT_TEXT_VERSION
    assert "Retiro del consentimiento" in r.json()["body"]
    assert client.get("/privacy/consent-text", headers=auth(tokens["ADMIN"])).status_code == 403
    r = client.get(f"/privacy/consent-texts/{CONSENT_TEXT_VERSION}", headers=auth(tokens["MEDICO"]))
    assert r.status_code == 200
    assert client.get("/privacy/consent-texts/no-existe", headers=auth(tokens["MEDICO"])).status_code == 404


def test_migration_text_matches_code():
    """La migración guarda una copia congelada de la v1: debe coincidir con el código."""
    path = next(Path(__file__).resolve().parents[2].glob("alembic/versions/c1d4f2a8e910_*.py"))
    spec = importlib.util.spec_from_file_location("mig_c1d4", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    assert module.CONSENT_TEXT_VERSION_V1 == CONSENT_TEXT_VERSION
    assert module.CONSENT_TEXT_BODY_V1 == CONSENT_TEXT_BODY


def test_patient_creation_records_text_version(client, tokens, db):
    p = create_patient(client, auth(tokens["ADMINISTRATIVO"]))
    assert p["consent_text_version"] == CONSENT_TEXT_VERSION
    events = client.get(f"/patients/{p['id']}/consent/events", headers=auth(tokens["MEDICO"])).json()
    assert [(e["action"], e["consent_text_version"]) for e in events] == [("OTORGADO", CONSENT_TEXT_VERSION)]


@pytest.mark.parametrize("version, status", [(None, 422), ("2020-01-v0", 409)])
def test_patient_creation_requires_current_text(client, tokens, version, status):
    r = client.post(
        "/patients", json=patient_payload(consent_text_version=version), headers=auth(tokens["MEDICO"])
    )
    assert r.status_code == status


# --- Retiro y nuevo otorgamiento ----------------------------------------------------------------


def test_withdraw_consent_blocks_new_cases_and_images(client, tokens, db):
    h = auth(tokens["MEDICO"])
    p = create_patient(client, h)
    case = create_case(client, h, p["id"])

    r = client.post(
        f"/patients/{p['id']}/consent/withdraw", json={"reason": "Lo pidió en consulta"}, headers=h
    )
    assert r.status_code == 200
    assert r.json()["consent_given"] is False

    # Sin consentimiento: ni casos nuevos ni imágenes nuevas; los datos existentes se conservan
    assert client.post("/cases", json={"patient_id": p["id"]}, headers=h).status_code == 409
    from app.tests.test_images import make_png, upload

    r = upload(client, h, case["id"], make_png())
    assert r.status_code == 409
    assert "retiró su consentimiento" in r.json()["detail"]
    assert client.get(f"/cases/{case['id']}", headers=h).status_code == 200

    # El motivo queda en el historial, no en la auditoría
    events = client.get(f"/patients/{p['id']}/consent/events", headers=h).json()
    assert events[-1]["action"] == "RETIRADO" and events[-1]["note"] == "Lo pidió en consulta"
    assert _audit(db, "CONSENT_WITHDRAW")[0].detail is None

    # Retirar dos veces → 409
    assert client.post(f"/patients/{p['id']}/consent/withdraw", json={}, headers=h).status_code == 409


def test_grant_consent_again(client, tokens, db):
    h = auth(tokens["ADMINISTRATIVO"])
    p = create_patient(client, h)
    assert client.post(f"/patients/{p['id']}/consent/withdraw", json={}, headers=h).status_code == 200
    r = client.post(f"/patients/{p['id']}/consent", json={"consent_text_version": "vieja"}, headers=h)
    assert r.status_code == 409
    r = client.post(
        f"/patients/{p['id']}/consent", json={"consent_text_version": CONSENT_TEXT_VERSION}, headers=h
    )
    assert r.status_code == 200 and r.json()["consent_given"] is True
    assert client.post("/cases", json={"patient_id": p["id"]}, headers=h).status_code == 201
    # Ya vigente con el mismo texto → 409
    r = client.post(
        f"/patients/{p['id']}/consent", json={"consent_text_version": CONSENT_TEXT_VERSION}, headers=h
    )
    assert r.status_code == 409
    actions = [e.action for e in db.query(ConsentEvent).filter(ConsentEvent.patient_id == p["id"]).all()]
    assert actions == ["OTORGADO", "RETIRADO", "OTORGADO"]
    assert _audit(db, "CONSENT_GRANT")[0].detail == {"version": CONSENT_TEXT_VERSION}


def test_consent_cannot_change_by_edit(client, tokens):
    h = auth(tokens["MEDICO"])
    p = create_patient(client, h)
    r = client.put(f"/patients/{p['id']}", json={"consent_given": False}, headers=h)
    assert r.status_code == 422
    assert (
        client.put(
            f"/patients/{p['id']}", json={"consent_given": True, "first_name": "Ana"}, headers=h
        ).status_code
        == 200
    )


# --- Bloqueo ------------------------------------------------------------------------------------


def test_block_requires_closed_cases(client, tokens, db):
    h = auth(tokens["MEDICO"])
    p = create_patient(client, h)
    case = create_case(client, h, p["id"])
    r = client.post(f"/patients/{p['id']}/block", json={"reason": "Solicitud de supresión"}, headers=h)
    assert r.status_code == 409 and "sin cerrar" in r.json()["detail"]
    _close_case(db, case["id"])
    r = client.post(f"/patients/{p['id']}/block", json={"reason": "Solicitud de supresión"}, headers=h)
    assert r.status_code == 200 and r.json()["blocked_at"] is not None


def test_blocked_patient_is_hidden_and_frozen(client, tokens, db):
    h = auth(tokens["ADMINISTRATIVO"])
    p = create_patient(client, h, last_name="Bloqueada")
    assert (
        client.post(
            f"/patients/{p['id']}/block", json={"reason": "Ejerció su derecho"}, headers=h
        ).status_code
        == 200
    )

    assert all(x["id"] != p["id"] for x in client.get("/patients?search=Bloqueada", headers=h).json())
    listed = client.get("/patients?search=Bloqueada&include_blocked=true", headers=h).json()
    assert [x["id"] for x in listed] == [p["id"]]
    # Se conserva (ficha clínica): se puede consultar, pero no editar ni crear casos
    assert client.get(f"/patients/{p['id']}", headers=h).status_code == 200
    assert client.put(f"/patients/{p['id']}", json={"first_name": "X"}, headers=h).status_code == 409
    assert client.post("/cases", json={"patient_id": p["id"]}, headers=h).status_code == 409
    assert (
        client.post(f"/patients/{p['id']}/block", json={"reason": "otra vez"}, headers=h).status_code == 409
    )
    assert [a.entity_id for a in _audit(db, "BLOCK")] == [p["id"]]

    r = client.post(f"/patients/{p['id']}/unblock", headers=h)
    assert r.status_code == 200 and r.json()["blocked_at"] is None
    assert client.post(f"/patients/{p['id']}/unblock", headers=h).status_code == 409
    assert client.put(f"/patients/{p['id']}", json={"first_name": "Ana"}, headers=h).status_code == 200


def test_delete_patient_without_cases(client, tokens, db):
    h = auth(tokens["ADMINISTRATIVO"])
    p = create_patient(client, h, last_name="Errónea")
    assert client.delete(f"/patients/{p['id']}", headers=h).status_code == 204
    assert client.get(f"/patients/{p['id']}", headers=h).status_code == 404
    assert db.query(ConsentEvent).filter(ConsentEvent.patient_id == p["id"]).count() == 0
    assert [a.entity_id for a in _audit(db, "DELETE")] == [p["id"]]
    assert client.delete(f"/patients/{p['id']}", headers=h).status_code == 404


def test_delete_patient_with_cases_is_rejected(client, tokens, db):
    h = auth(tokens["MEDICO"])
    p = create_patient(client, h)
    create_case(client, h, p["id"])
    r = client.delete(f"/patients/{p['id']}", headers=h)
    assert r.status_code == 409 and "20.584" in r.json()["detail"]
    assert client.get(f"/patients/{p['id']}", headers=h).status_code == 200


def test_admin_cannot_delete_patient(client, tokens):
    p = create_patient(client, auth(tokens["MEDICO"]))
    assert client.delete(f"/patients/{p['id']}", headers=auth(tokens["ADMIN"])).status_code == 403


def test_block_reason_is_required(client, tokens):
    h = auth(tokens["MEDICO"])
    p = create_patient(client, h)
    assert client.post(f"/patients/{p['id']}/block", json={"reason": ""}, headers=h).status_code == 422


# --- Exportación -------------------------------------------------------------------------------


def test_export_contains_all_patient_data(client, tokens, db):
    h = auth(tokens["MEDICO"])
    p = create_patient(client, h)
    case = create_case(client, h, p["id"], palpable_mass=True)
    from app.tests.test_images import make_png, upload

    assert upload(client, h, case["id"], make_png()).status_code == 201
    client.post(f"/patients/{p['id']}/requests", json={"request_type": "ACCESO"}, headers=h)

    r = client.get(f"/patients/{p['id']}/export", headers=h)
    assert r.status_code == 200
    data = r.json()
    assert data["patient"]["rut"] == p["rut"]
    assert data["consent_events"][0]["consent_text_version"] == CONSENT_TEXT_VERSION
    assert len(data["cases"]) == 1
    exported_case = data["cases"][0]
    assert exported_case["code"] == case["code"]
    assert exported_case["triage_history"]
    image = exported_case["images"][0]
    assert "filepath" not in image  # ruta interna del almacenamiento cifrado
    assert image["inference"]["is_simulated"] is True
    assert data["data_subject_requests"][0]["request_type"] == "ACCESO"
    assert "IA simulada" in data["note"]
    assert _audit(db, "EXPORT")[0].entity_id == p["id"]


def test_export_only_medico(client, tokens):
    p = create_patient(client, auth(tokens["MEDICO"]))
    for role in ("ADMINISTRATIVO", "ADMIN"):
        assert client.get(f"/patients/{p['id']}/export", headers=auth(tokens[role])).status_code == 403


# --- Solicitudes de los titulares --------------------------------------------------------------


def test_request_lifecycle(client, tokens, db):
    h = auth(tokens["ADMINISTRATIVO"])
    p = create_patient(client, h)
    r = client.post(
        f"/patients/{p['id']}/requests",
        json={"request_type": "RECTIFICACION", "detail": "Corregir fecha de nacimiento"},
        headers=h,
    )
    assert r.status_code == 201
    req = r.json()
    received = datetime.fromisoformat(req["received_at"])
    assert datetime.fromisoformat(req["due_at"]) - received == timedelta(days=30)
    assert req["status"] == "RECIBIDA" and req["overdue"] is False
    assert req["patient_rut"] == p["rut"]

    url = f"/privacy/requests/{req['id']}"
    assert client.patch(url, json={"status": "EN_PROCESO"}, headers=h).json()["status"] == "EN_PROCESO"
    # Resolver exige una respuesta
    assert client.patch(url, json={"status": "RESUELTA"}, headers=h).status_code == 422
    r = client.patch(url, json={"status": "RESUELTA", "resolution": "Fecha corregida en la ficha"}, headers=h)
    assert r.status_code == 200 and r.json()["resolved_at"] is not None
    # Estado final: no se reabre
    assert client.patch(url, json={"status": "EN_PROCESO"}, headers=h).status_code == 409
    statuses = [a.detail.get("status") for a in _audit(db, "UPDATE", "data_subject_request")]
    assert statuses == ["EN_PROCESO", "RESUELTA"]
    assert "Corregir" not in str(_audit(db, "CREATE", "data_subject_request")[0].detail)


def test_overdue_requests_and_summary(client, tokens, db):
    h = auth(tokens["MEDICO"])
    p = create_patient(client, h)
    old = (datetime.now(timezone.utc) - timedelta(days=31)).isoformat()
    client.post(
        f"/patients/{p['id']}/requests", json={"request_type": "ACCESO", "received_at": old}, headers=h
    )
    client.post(f"/patients/{p['id']}/requests", json={"request_type": "OPOSICION"}, headers=h)

    overdue = client.get("/privacy/requests?overdue=true", headers=h).json()
    assert [r["request_type"] for r in overdue] == ["ACCESO"] and overdue[0]["overdue"] is True
    assert len(client.get("/privacy/requests", headers=h).json()) == 2
    assert len(client.get(f"/privacy/requests?patient_id={p['id']}&status=RECIBIDA", headers=h).json()) == 2

    # El ADMIN ve el resumen (sin datos de pacientes), pero no la lista
    summary = client.get("/privacy/requests/summary", headers=auth(tokens["ADMIN"])).json()
    assert summary == {
        "by_status": {"RECIBIDA": 2, "EN_PROCESO": 0, "RESUELTA": 0, "RECHAZADA": 0},
        "open_total": 2,
        "overdue": 1,
    }
    assert client.get("/privacy/requests", headers=auth(tokens["ADMIN"])).status_code == 403


def test_request_validation(client, tokens, db):
    h = auth(tokens["MEDICO"])
    p = create_patient(client, h)
    assert (
        client.post(f"/patients/{p['id']}/requests", json={"request_type": "OTRA"}, headers=h).status_code
        == 422
    )
    future = (datetime.now(timezone.utc) + timedelta(days=2)).isoformat()
    r = client.post(
        f"/patients/{p['id']}/requests", json={"request_type": "ACCESO", "received_at": future}, headers=h
    )
    assert r.status_code == 422
    assert (
        client.post("/patients/999999/requests", json={"request_type": "ACCESO"}, headers=h).status_code
        == 404
    )
    assert db.query(DataSubjectRequest).count() == 0
