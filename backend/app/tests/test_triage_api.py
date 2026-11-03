import copy
from datetime import datetime, timedelta, timezone

import pytest

from app.db.models.audit_log import AuditLog
from app.db.models.case import Case, CaseStatus
from app.db.models.triage import Notification, TriageConfig, TriageResult
from app.services.triage_engine import DEFAULT_PARAMS_V1
from app.tests.conftest import auth
from app.tests.factories import birth_date_for_age, create_case, create_patient


def test_seed_config_v1_is_active(client, tokens):
    r = client.get("/triage/config", headers=auth(tokens["MEDICO"]))
    assert r.status_code == 200
    body = r.json()
    assert body["version"] == 1 and body["is_active"] is True
    assert body["params"]["weights"]["ai"] == 40
    # ADMIN puede consultarla, ADMINISTRATIVO no
    assert client.get("/triage/config", headers=auth(tokens["ADMIN"])).status_code == 200
    assert client.get("/triage/config", headers=auth(tokens["ADMINISTRATIVO"])).status_code == 403


def test_case_creation_computes_triage_and_prioritizes(client, tokens, db):
    h = auth(tokens["MEDICO"])
    case = create_case(client, h, birads_reported=4)
    assert case["status"] == "PRIORIZADO"
    assert case["triage_level"] == "ALTA"
    r = client.get(f"/cases/{case['id']}/triage", headers=h)
    assert r.status_code == 200
    t = r.json()
    assert t["escalation_rule"] == "R_BIRADS"
    assert t["computed_level"] == t["final_level"] == "ALTA"
    assert t["config_version"] == 1
    assert "ai" in t["breakdown"] and "age" in t["breakdown"]


def test_triage_detail_only_for_medico(client, tokens):
    h_adm = auth(tokens["ADMINISTRATIVO"])
    case = create_case(client, h_adm)
    assert client.get(f"/cases/{case['id']}/triage", headers=h_adm).status_code == 403
    assert client.post(f"/cases/{case['id']}/triage", headers=h_adm).status_code == 403
    assert client.get(f"/cases/{case['id']}/triage", headers=auth(tokens["ADMIN"])).status_code == 403


def test_editing_symptoms_recalculates_and_keeps_history(client, tokens, db):
    h = auth(tokens["MEDICO"])
    case = create_case(client, h)
    assert case["triage_level"] == "BAJA"
    r = client.patch(f"/cases/{case['id']}", json={"palpable_mass": True}, headers=h)
    assert r.json()["triage_level"] == "ALTA"
    assert r.json()["status"] == "PRIORIZADO"
    results = db.query(TriageResult).filter(TriageResult.case_id == case["id"]).all()
    assert len(results) == 2
    assert sum(1 for x in results if x.is_current) == 1
    history = client.get(f"/cases/{case['id']}/triage/history", headers=h).json()
    assert [x["final_level"] for x in history] == ["ALTA", "BAJA"]


def test_editing_patient_history_recalculates(client, tokens):
    h = auth(tokens["MEDICO"])
    patient = create_patient(client, h, birth_date=birth_date_for_age(30))
    case = create_case(client, h, patient["id"])
    before = client.get(f"/cases/{case['id']}/triage", headers=h).json()["score"]
    client.put(f"/patients/{patient['id']}", json={"previous_breast_cancer": True}, headers=h)
    after = client.get(f"/cases/{case['id']}/triage", headers=h).json()["score"]
    assert after == pytest.approx(before + 20, abs=0.05)


def test_manual_recalculation(client, tokens):
    h = auth(tokens["MEDICO"])
    case = create_case(client, h)
    r = client.post(f"/cases/{case['id']}/triage", headers=h)
    assert r.status_code == 200
    assert r.json()["is_current"] is True


def test_override_requires_reason(client, tokens):
    h = auth(tokens["MEDICO"])
    case = create_case(client, h)
    url = f"/cases/{case['id']}/triage/override"
    assert client.post(url, json={"level": "ALTA"}, headers=h).status_code == 422
    assert client.post(url, json={"level": "ALTA", "reason": ""}, headers=h).status_code == 422
    assert client.post(url, json={"level": "ALTA", "reason": "    "}, headers=h).status_code == 422
    assert (
        client.post(url, json={"level": "URGENTE", "reason": "motivo válido"}, headers=h).status_code == 422
    )


def test_override_sets_final_level_and_is_audited(client, tokens, users, db):
    h = auth(tokens["MEDICO"])
    case = create_case(client, h)
    r = client.post(
        f"/cases/{case['id']}/triage/override",
        json={"level": "MEDIA", "reason": "Hallazgo clínico en el examen físico"},
        headers=h,
    )
    assert r.status_code == 200
    t = r.json()
    assert t["final_level"] == "MEDIA"
    assert t["computed_level"] == "BAJA"
    assert t["override_by"] == users["MEDICO"].id
    entry = db.query(AuditLog).filter(AuditLog.action == "OVERRIDE").one()
    assert entry.detail["from"] == "BAJA" and entry.detail["to"] == "MEDIA"


def test_only_medico_can_override(client, tokens):
    h_adm = auth(tokens["ADMINISTRATIVO"])
    case = create_case(client, h_adm)
    r = client.post(
        f"/cases/{case['id']}/triage/override", json={"level": "ALTA", "reason": "intento"}, headers=h_adm
    )
    assert r.status_code == 403


def test_override_on_closed_case_is_409(client, tokens, db):
    h = auth(tokens["MEDICO"])
    case = create_case(client, h)
    c = db.get(Case, case["id"])
    c.status = CaseStatus.CERRADO
    db.commit()
    r = client.post(
        f"/cases/{case['id']}/triage/override", json={"level": "ALTA", "reason": "motivo"}, headers=h
    )
    assert r.status_code == 409


# --- Cola -------------------------------------------------------------------------


def _set_created(db, case_id, days_ago):
    c = db.get(Case, case_id)
    c.created_at = datetime.now(timezone.utc) - timedelta(days=days_ago)
    db.commit()


def test_queue_order(client, tokens, db):
    h = auth(tokens["MEDICO"])
    young = create_patient(client, h, birth_date=birth_date_for_age(30))
    target = create_patient(client, h, birth_date=birth_date_for_age(55))
    risky = create_patient(client, h, birth_date=birth_date_for_age(55), previous_breast_cancer=True)

    baja_old = create_case(client, h, young["id"])
    baja_new = create_case(client, h, young["id"])
    media = create_case(client, h, risky["id"])  # 15 + 20 = 35 → MEDIA
    media_low = create_case(client, h, target["id"], birads_reported=None)  # 15 → BAJA
    alta_a = create_case(client, h, young["id"], birads_reported=5)
    alta_b = create_case(client, h, young["id"], palpable_mass=True)
    # Antigüedades: la más antigua va primero a igual nivel y puntaje
    _set_created(db, baja_old["id"], 2)
    _set_created(db, alta_b["id"], 1)
    for c in (baja_old, baja_new, media, media_low, alta_a, alta_b):
        client.post(f"/cases/{c['id']}/triage", headers=h)

    queue = client.get("/triage/queue", headers=h).json()
    levels = [item["level"] for item in queue]
    assert levels == sorted(levels, key=["ALTA", "MEDIA", "BAJA"].index)
    by_code = [item["code"] for item in queue]
    # ALTA: alta_b tiene más tiempo de espera → mayor puntaje → primero
    assert by_code.index(alta_b["code"]) < by_code.index(alta_a["code"])
    # MEDIA antes que BAJA
    assert by_code.index(media["code"]) < by_code.index(media_low["code"])
    # Dentro de BAJA: mayor puntaje primero (edad 55 > edad 30)
    assert by_code.index(media_low["code"]) < by_code.index(baja_new["code"])
    # Mismo nivel: score desc; baja_old espera 2 días (más puntaje) y va antes que baja_new
    assert by_code.index(baja_old["code"]) < by_code.index(baja_new["code"])
    scores_in_level = [i["score"] for i in queue if i["level"] == "BAJA"]
    assert scores_in_level == sorted(scores_in_level, reverse=True)


def test_queue_tiebreak_by_age(client, tokens, db):
    h = auth(tokens["MEDICO"])
    p = create_patient(client, h, birth_date=birth_date_for_age(30))
    p_params = copy.deepcopy(DEFAULT_PARAMS_V1)
    p_params["weights"] = {"ai": 50, "age": 15, "family_history": 15, "previous_cancer": 20, "wait_time": 0}
    client.post("/triage/config", json={"params": p_params, "change_reason": "Sin peso de espera"}, headers=h)
    first = create_case(client, h, p["id"])
    second = create_case(client, h, p["id"])
    _set_created(db, second["id"], 3)
    queue = client.get("/triage/queue", headers=h).json()
    codes = [i["code"] for i in queue]
    assert codes.index(second["code"]) < codes.index(first["code"])  # mismo puntaje → más antiguo primero


def test_queue_for_administrativo_is_minimal(client, tokens):
    h_adm = auth(tokens["ADMINISTRATIVO"])
    create_case(client, h_adm, birads_reported=4)
    r = client.get("/triage/queue", headers=h_adm)
    assert r.status_code == 200
    item = r.json()[0]
    assert set(item) == {"code", "level", "status", "waiting_hours"}


def test_queue_forbidden_for_admin(client, tokens):
    assert client.get("/triage/queue", headers=auth(tokens["ADMIN"])).status_code == 403


def test_filter_cases_by_level(client, tokens):
    h = auth(tokens["MEDICO"])
    create_case(client, h, birads_reported=4)
    create_case(client, h)
    r = client.get("/cases?level=ALTA", headers=h).json()
    assert r["total"] == 1 and r["items"][0]["triage_level"] == "ALTA"


# --- Configuración ------------------------------------------------------------


def test_new_config_creates_version_and_recalculates(client, tokens, db):
    h = auth(tokens["MEDICO"])
    case = create_case(client, h, palpable_mass=True)
    assert case["triage_level"] == "ALTA"
    new = copy.deepcopy(DEFAULT_PARAMS_V1)
    new["escalation"]["symptoms_alta"] = False
    r = client.post(
        "/triage/config", json={"params": new, "change_reason": "Revisión del equipo médico"}, headers=h
    )
    assert r.status_code == 201, r.text
    assert r.json()["config"]["version"] == 2
    assert r.json()["recalculated_cases"] == 1
    t = client.get(f"/cases/{case['id']}/triage", headers=h).json()
    assert t["config_version"] == 2 and t["final_level"] == "BAJA"
    assert db.query(TriageConfig).filter(TriageConfig.is_active.is_(True)).count() == 1
    history = client.get("/triage/config/history", headers=h).json()
    assert [c["version"] for c in history] == [2, 1]
    assert db.query(AuditLog).filter(AuditLog.action == "CONFIG_CHANGE").count() == 1


def test_config_change_keeps_medical_override(client, tokens):
    h = auth(tokens["MEDICO"])
    case = create_case(client, h)
    client.post(
        f"/cases/{case['id']}/triage/override",
        json={"level": "ALTA", "reason": "Criterio clínico"},
        headers=h,
    )
    new = copy.deepcopy(DEFAULT_PARAMS_V1)
    new["thresholds"] = {"alta": 70, "media": 40}
    client.post("/triage/config", json={"params": new, "change_reason": "Ajuste de umbrales"}, headers=h)
    t = client.get(f"/cases/{case['id']}/triage", headers=h).json()
    assert t["final_level"] == "ALTA" and t["override_reason"] == "Criterio clínico"


def test_config_weights_not_100_is_422(client, tokens):
    bad = copy.deepcopy(DEFAULT_PARAMS_V1)
    bad["weights"]["ai"] = 50
    r = client.post(
        "/triage/config", json={"params": bad, "change_reason": "prueba"}, headers=auth(tokens["MEDICO"])
    )
    assert r.status_code == 422


def test_config_requires_reason(client, tokens):
    r = client.post(
        "/triage/config",
        json={"params": DEFAULT_PARAMS_V1, "change_reason": ""},
        headers=auth(tokens["MEDICO"]),
    )
    assert r.status_code == 422


def test_admin_cannot_edit_config(client, tokens):
    r = client.post(
        "/triage/config",
        json={"params": DEFAULT_PARAMS_V1, "change_reason": "intento de admin"},
        headers=auth(tokens["ADMIN"]),
    )
    assert r.status_code == 403


# --- Notificaciones ------------------------------------------------------------


def test_alta_creates_notifications_for_active_medicos(client, tokens, users, db):
    h = auth(tokens["ADMINISTRATIVO"])
    case = create_case(client, h, nipple_discharge=True)
    notes = db.query(Notification).all()
    assert len(notes) == 1 and notes[0].user_id == users["MEDICO"].id
    assert case["code"] in notes[0].message

    h_med = auth(tokens["MEDICO"])
    r = client.get("/notifications", headers=h_med)
    assert r.status_code == 200 and len(r.json()) == 1
    nid = r.json()[0]["id"]
    r = client.patch(f"/notifications/{nid}/read", headers=h_med)
    assert r.status_code == 200 and r.json()["read_at"] is not None
    assert client.get("/notifications?unread_only=true", headers=h_med).json() == []
    # No se puede marcar la notificación de otro usuario
    assert client.patch(f"/notifications/{nid}/read", headers=h).status_code == 404


def test_no_duplicate_notification_while_still_alta(client, tokens, db):
    h = auth(tokens["MEDICO"])
    case = create_case(client, h, birads_reported=5)
    client.patch(f"/cases/{case['id']}", json={"palpable_mass": True}, headers=h)
    assert db.query(Notification).count() == 1


def test_triage_view_is_audited(client, tokens, db):
    h = auth(tokens["MEDICO"])
    case = create_case(client, h)
    client.get(f"/cases/{case['id']}/triage", headers=h)
    assert db.query(AuditLog).filter(AuditLog.entity == "triage", AuditLog.action == "VIEW").count() >= 1
