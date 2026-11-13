from datetime import datetime, timedelta, timezone

from app.db.models.audit_log import AuditLog
from app.db.models.user import UserRole
from app.tests.conftest import PASSWORD, auth, make_user


def test_overview_requires_admin(client, tokens):
    for role in ("MEDICO", "ADMINISTRATIVO"):
        assert client.get("/admin/overview", headers=auth(tokens[role])).status_code == 403


def test_overview_counts_accounts_and_security(client, tokens, users, db):
    now = datetime.now(timezone.utc)
    make_user(db, UserRole.MEDICO, "44444444-4", must_change_password=True)
    make_user(db, UserRole.MEDICO, "55555555-5", locked_until=now + timedelta(minutes=10))
    make_user(db, UserRole.ADMINISTRATIVO, "66666666-6", is_active=False)
    # Un ingreso fallido hoy (no guarda el RUT intentado)
    r = client.post("/auth/login", json={"rut": users["MEDICO"].rut, "password": PASSWORD + "x"})
    assert r.status_code == 401

    body = client.get("/admin/overview", headers=auth(tokens["ADMIN"])).json()
    assert body["users_total"] == 6 and body["users_active"] == 5
    assert body["users_by_role"] == {"MEDICO": 3, "ADMIN": 1, "ADMINISTRATIVO": 1}
    assert body["users_pending_password"] == 1
    assert body["users_locked"] == 1
    # Los dos nuevos sin ingreso cuentan como sin uso; el inactivo no se cuenta
    assert body["users_idle_30d"] == 2
    assert body["admins_active"] == 1
    assert body["security_events_24h"] == 1
    assert len(body["logins_per_day"]) == 14
    today = body["logins_per_day"][-1]
    assert today["ok"] == 3 and today["failed"] == 1  # los tres ingresos del fixture y el fallido
    assert body["actions_7d"]["LOGIN_OK"] == 3
    assert body["version"]


def test_overview_ignores_old_logins(client, tokens, db):
    db.add(AuditLog(user_id=None, action="LOGIN_FAIL", entity="user",
                    created_at=datetime.now(timezone.utc) - timedelta(days=40)))
    db.commit()
    body = client.get("/admin/overview", headers=auth(tokens["ADMIN"])).json()
    assert sum(d["failed"] for d in body["logins_per_day"]) == 0
    assert body["security_events_24h"] == 0


def test_audit_filter_accepts_several_actions(client, tokens, users):
    client.post("/auth/login", json={"rut": users["MEDICO"].rut, "password": PASSWORD + "x"})
    r = client.get("/admin/audit?action=LOGIN_FAIL,SIGN_FAIL", headers=auth(tokens["ADMIN"]))
    assert r.status_code == 200
    items = r.json()["items"]
    assert items and all(i["action"] in ("LOGIN_FAIL", "SIGN_FAIL") for i in items)
