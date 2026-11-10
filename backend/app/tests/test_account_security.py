"""E6: cambio de contraseña, cambio obligatorio, bloqueo de login, límite por IP, registro de errores y OWASP."""

from datetime import datetime, timedelta, timezone

import pytest
from fastapi import Depends, HTTPException
from fastapi.routing import APIRoute
from fastapi.testclient import TestClient

from app.auth.bearer import PASSWORD_CHANGE_REQUIRED, get_current_user
from app.config import settings
from app.db.models.audit_log import AuditLog
from app.db.models.error_log import ErrorLog
from app.db.models.user import User, UserRole
from app.services.error_log_service import sanitize_message
from app.services.password_policy import policy_errors
from app.tests.conftest import PASSWORD, auth, login, make_user

NEW_PASSWORD = "NuevaClave-2026x"
MEDICO_RUT = "11111111-1"


def _change(client, token, current=PASSWORD, new=NEW_PASSWORD):
    return client.post(
        "/auth/change-password",
        json={"current_password": current, "new_password": new},
        headers=auth(token),
    )


def _audit(db, action, user_id=None):
    db.expire_all()
    q = db.query(AuditLog).filter(AuditLog.action == action)
    if user_id is not None:
        q = q.filter(AuditLog.user_id == user_id)
    return q.order_by(AuditLog.id).all()


def _fail_login(client, rut=MEDICO_RUT, headers=None):
    return client.post("/auth/login", json={"rut": rut, "password": "Incorrecta-999"}, headers=headers)


# --- Política de contraseñas ------------------------------------------------------------------


@pytest.mark.parametrize(
    "password, fragment",
    [
        ("Corta-1", "al menos 10 caracteres"),
        ("SoloLetrasLargas", "letras y números"),
        ("12345678901234", "letras y números"),
        ("password123", "demasiado común"),
        ("clave11111111x", "no puede contener su RUT"),
    ],
)
def test_password_policy_rejects(password, fragment):
    assert any(fragment in e for e in policy_errors(password, MEDICO_RUT))


def test_password_policy_accepts_good_password():
    assert policy_errors(NEW_PASSWORD, MEDICO_RUT) == []


# --- Cambio de contraseña ---------------------------------------------------------------------


def test_change_password_ok_revokes_old_tokens(client, users, db):
    old = login(client, MEDICO_RUT)
    r = _change(client, old)
    assert r.status_code == 200, r.text
    new = r.json()["access_token"]
    assert r.json()["must_change_password"] is False

    assert client.get("/auth/me", headers=auth(old)).status_code == 401
    assert client.get("/auth/me", headers=auth(new)).status_code == 200
    assert client.post("/auth/login", json={"rut": MEDICO_RUT, "password": PASSWORD}).status_code == 401
    login(client, MEDICO_RUT, NEW_PASSWORD)

    entries = _audit(db, "PASSWORD_CHANGE", users["MEDICO"].id)
    assert len(entries) == 1
    assert entries[0].detail == {"forced": False}
    assert NEW_PASSWORD not in str(entries[0].detail)


def test_change_password_wrong_current(client, users, db):
    token = login(client, MEDICO_RUT)
    r = _change(client, token, current="NoEsLaActual-1")
    assert r.status_code == 422
    assert r.json()["detail"] == "La contraseña actual no es correcta"
    assert _audit(db, "PASSWORD_CHANGE_FAIL", users["MEDICO"].id)[0].detail == {"reason": "actual_incorrecta"}
    # La contraseña no cambió
    login(client, MEDICO_RUT)


@pytest.mark.parametrize("new", ["Corta-1", "SoloLetrasLargas", PASSWORD])
def test_change_password_policy(client, users, db, new):
    token = login(client, MEDICO_RUT)
    r = _change(client, token, new=new)
    assert r.status_code == 422
    assert r.json()["detail"].startswith("La contraseña ")
    assert _audit(db, "PASSWORD_CHANGE_FAIL", users["MEDICO"].id)[0].detail == {"reason": "politica"}


def test_change_password_same_as_current_message(client, users):
    token = login(client, MEDICO_RUT)
    r = _change(client, token, new=PASSWORD)
    assert "distinta de la contraseña actual" in r.json()["detail"]


def test_change_password_requires_auth(client, users):
    r = client.post(
        "/auth/change-password", json={"current_password": PASSWORD, "new_password": NEW_PASSWORD}
    )
    assert r.status_code == 401


def test_change_password_attempts_are_limited(client, users):
    token = login(client, MEDICO_RUT)
    codes = [_change(client, token, current="NoEsLaActual-1").status_code for _ in range(6)]
    assert codes[:5] == [422] * 5
    assert codes[5] == 429


# --- Cambio obligatorio en el primer ingreso --------------------------------------------------


def _create_user(client, admin_token, password="Temporal-2026a"):
    return client.post(
        "/admin/users",
        json={
            "rut": "15555555-6",
            "email": "nueva@aurora-demo.cl",
            "full_name": "Médica Nueva",
            "password": password,
            "role": "MEDICO",
        },
        headers=auth(admin_token),
    )


def test_new_user_must_change_password(client, tokens, db):
    r = _create_user(client, tokens["ADMIN"])
    assert r.status_code == 201, r.text
    assert r.json()["must_change_password"] is True

    r = client.post("/auth/login", json={"rut": "15555555-6", "password": "Temporal-2026a"})
    assert r.status_code == 200
    assert r.json()["must_change_password"] is True
    token = r.json()["access_token"]

    # Solo puede ver su perfil y cambiar la contraseña
    r = client.get("/patients", headers=auth(token))
    assert r.status_code == 403
    assert r.json()["detail"] == PASSWORD_CHANGE_REQUIRED
    me = client.get("/auth/me", headers=auth(token))
    assert me.status_code == 200 and me.json()["must_change_password"] is True

    r = _change(client, token, current="Temporal-2026a")
    assert r.status_code == 200
    new = r.json()["access_token"]
    assert client.get("/patients", headers=auth(new)).status_code == 200
    assert client.get("/auth/me", headers=auth(new)).json()["must_change_password"] is False
    assert _audit(db, "PASSWORD_CHANGE")[0].detail == {"forced": True}


def test_admin_create_user_weak_password(client, tokens):
    r = _create_user(client, tokens["ADMIN"], password="corta")
    assert r.status_code == 422
    assert "al menos 10 caracteres" in r.json()["detail"]


def test_admin_reset_password_forces_change_and_revokes(client, users, tokens):
    medico_token = tokens["MEDICO"]
    r = client.patch(
        f"/admin/users/{users['MEDICO'].id}",
        json={"password": "Restablecida-2026"},
        headers=auth(tokens["ADMIN"]),
    )
    assert r.status_code == 200, r.text
    assert r.json()["must_change_password"] is True
    # La sesión que tenía antes del restablecimiento deja de servir
    assert client.get("/auth/me", headers=auth(medico_token)).status_code == 401
    r = client.post("/auth/login", json={"rut": MEDICO_RUT, "password": "Restablecida-2026"})
    assert r.json()["must_change_password"] is True


def test_admin_reset_password_weak(client, users, tokens):
    r = client.patch(
        f"/admin/users/{users['MEDICO'].id}", json={"password": "123"}, headers=auth(tokens["ADMIN"])
    )
    assert r.status_code == 422


# --- Bloqueo por intentos fallidos ------------------------------------------------------------


def test_lockout_after_max_failed_attempts(client, users, db):
    n = settings.LOGIN_MAX_FAILED_ATTEMPTS
    codes = [_fail_login(client).status_code for _ in range(n)]
    assert codes[:-1] == [401] * (n - 1)
    assert codes[-1] == 423

    # Bloqueada: ni la contraseña correcta sirve, y no se evalúa
    r = client.post("/auth/login", json={"rut": MEDICO_RUT, "password": PASSWORD})
    assert r.status_code == 423
    assert "bloqueada temporalmente" in r.json()["detail"]

    reasons = [e.detail["reason"] for e in _audit(db, "LOGIN_FAIL", users["MEDICO"].id)]
    assert reasons == ["credenciales"] * (n - 1) + ["bloqueo", "bloqueado"]

    # Al vencer el bloqueo vuelve a entrar y el contador parte de cero
    user = db.get(User, users["MEDICO"].id)
    user.locked_until = datetime.now(timezone.utc) - timedelta(seconds=1)
    db.commit()
    login(client, MEDICO_RUT)
    db.expire_all()
    user = db.get(User, users["MEDICO"].id)
    assert user.failed_login_attempts == 0 and user.locked_until is None


def test_successful_login_resets_counter(client, users):
    n = settings.LOGIN_MAX_FAILED_ATTEMPTS
    for _ in range(n - 1):
        assert _fail_login(client).status_code == 401
    login(client, MEDICO_RUT)
    for _ in range(n - 1):
        assert _fail_login(client).status_code == 401


def test_unknown_rut_never_locks(client, users):
    for _ in range(settings.LOGIN_MAX_FAILED_ATTEMPTS + 2):
        assert _fail_login(client, rut="99999999-9").status_code == 401


def test_admin_unlocks_user(client, users, tokens, db):
    for _ in range(settings.LOGIN_MAX_FAILED_ATTEMPTS):
        _fail_login(client)
    listed = client.get("/admin/users", headers=auth(tokens["ADMIN"])).json()
    assert next(u for u in listed if u["id"] == users["MEDICO"].id)["locked_until"] is not None

    assert (
        client.post(f"/admin/users/{users['MEDICO'].id}/unlock", headers=auth(tokens["MEDICO"])).status_code
        == 403
    )
    r = client.post(f"/admin/users/{users['MEDICO'].id}/unlock", headers=auth(tokens["ADMIN"]))
    assert r.status_code == 200
    assert r.json()["locked_until"] is None
    login(client, MEDICO_RUT)
    assert any(e.detail.get("unlock") for e in _audit(db, "UPDATE", users["ADMIN"].id))


# --- Límite por IP ----------------------------------------------------------------------------


def test_ip_rate_limit(client, users, db, monkeypatch):
    monkeypatch.setattr(settings, "LOGIN_RATE_LIMIT_PER_MINUTE", 3)
    codes = [_fail_login(client, rut="99999999-9").status_code for _ in range(5)]
    assert codes == [401, 401, 401, 429, 429]

    r = client.post("/auth/login", json={"rut": MEDICO_RUT, "password": PASSWORD})
    assert r.status_code == 429
    assert int(r.headers["Retry-After"]) > 0
    # Se audita una vez por ventana, sin RUT
    limited = [e for e in _audit(db, "LOGIN_FAIL") if e.detail["reason"] == "limite_ip"]
    assert len(limited) == 1 and limited[0].user_id is None


def test_ip_rate_limit_ignores_spoofed_forwarded_for(client, users, monkeypatch):
    monkeypatch.setattr(settings, "LOGIN_RATE_LIMIT_PER_MINUTE", 2)
    codes = [
        _fail_login(client, rut="99999999-9", headers={"X-Forwarded-For": f"10.0.0.{i}"}).status_code
        for i in range(3)
    ]
    assert codes == [401, 401, 429]


# --- Registro de errores 5xx ------------------------------------------------------------------


@pytest.fixture
def failing_routes():
    from app.main import app

    def boom(user: User = Depends(get_current_user)):
        raise RuntimeError("fallo con paciente 12.345.678-5, correo ana@correo.cl y monto 987654")

    def unavailable():
        raise HTTPException(status_code=503, detail="Servicio no disponible")

    app.add_api_route("/__test/boom", boom, methods=["GET"])
    app.add_api_route("/__test/unavailable", unavailable, methods=["GET"])
    yield
    app.router.routes[:] = [
        r for r in app.router.routes if getattr(r, "path", "") not in ("/__test/boom", "/__test/unavailable")
    ]


def test_unhandled_error_is_logged_without_sensitive_data(failing_routes, users, tokens, db):
    from app.main import app

    with TestClient(app, raise_server_exceptions=False) as c:
        r = c.get("/__test/boom", headers=auth(tokens["MEDICO"]))
    assert r.status_code == 500
    body = r.json()
    request_id = r.headers["X-Request-ID"]
    assert body["request_id"] == request_id
    assert "RuntimeError" not in body["detail"] and "12.345.678" not in body["detail"]

    row = db.query(ErrorLog).one()
    assert row.request_id == request_id
    assert row.status_code == 500
    assert row.error_type == "builtins.RuntimeError"
    assert row.path == "/__test/boom" and row.method == "GET"
    assert row.user_id == users["MEDICO"].id
    assert "12.345.678-5" not in row.message and "ana@correo.cl" not in row.message
    assert "987654" not in row.message
    assert "[rut]" in row.message and "[email]" in row.message
    assert row.location.startswith("app/tests/test_account_security.py:")
    assert row.location.endswith("en boom")


def test_http_5xx_is_logged_and_4xx_is_not(failing_routes, client, tokens, db):
    assert client.get("/__test/unavailable").status_code == 503
    assert client.get("/patients").status_code == 401
    assert client.get("/patients/999999", headers=auth(tokens["MEDICO"])).status_code == 404
    rows = db.query(ErrorLog).all()
    assert [(r.status_code, r.error_type, r.user_id) for r in rows] == [(503, "HTTP_503", None)]


def test_sanitize_sql_error():
    exc = Exception(
        "(psycopg2.errors.UniqueViolation) duplicate key value violates unique constraint "
        '"ix_patients_rut"\nDETAIL:  Key (rut)=(12345678-5) already exists.\n'
        "[SQL: INSERT INTO patients (rut, first_name) VALUES (%(rut)s, %(first_name)s)]\n"
        "[parameters: {'rut': '12345678-5', 'first_name': 'Ana'}]"
    )
    msg = sanitize_message(exc)
    assert "12345678-5" not in msg and "Ana" not in msg
    assert "UniqueViolation" in msg and "[SQL omitido]" in msg


def test_admin_error_view(failing_routes, client, tokens):
    for _ in range(2):
        client.get("/__test/unavailable")
    h = auth(tokens["ADMIN"])
    page = client.get("/admin/errors", headers=h).json()
    assert page["total"] == 2 and page["items"][0]["error_type"] == "HTTP_503"
    assert client.get("/admin/errors?error_type=Runtime", headers=h).json()["total"] == 0
    assert client.get("/admin/errors?status_code=503", headers=h).json()["total"] == 2
    future = (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()
    assert client.get("/admin/errors", params={"from": future}, headers=h).json()["total"] == 0
    assert client.get("/admin/errors/types", headers=h).json() == [{"error_type": "HTTP_503", "count": 2}]
    for role in ("MEDICO", "ADMINISTRATIVO"):
        assert client.get("/admin/errors", headers=auth(tokens[role])).status_code == 403


def test_dashboard_counts_server_errors(failing_routes, client, tokens):
    client.get("/__test/unavailable")
    m = client.get("/dashboard/metrics", headers=auth(tokens["ADMIN"])).json()
    assert m["server_errors"] == 1
    assert m["server_error_rate"] is not None and 0 < m["server_error_rate"] <= 1


# --- Revisión OWASP ---------------------------------------------------------------------------


def test_security_headers(client):
    r = client.get("/health")
    assert r.headers["X-Content-Type-Options"] == "nosniff"
    assert r.headers["X-Frame-Options"] == "DENY"
    assert r.headers["Cache-Control"] == "no-store"
    assert "frame-ancestors 'none'" in r.headers["Content-Security-Policy"]
    assert len(r.headers["X-Request-ID"]) == 32


PUBLIC = {("/health", "GET"), ("/auth/login", "POST")}


def test_every_route_requires_authentication(client):
    """A01: ninguna ruta de la API (salvo login y health) responde sin token."""
    from app.main import app

    checked = 0
    for route in app.routes:
        if not isinstance(route, APIRoute) or route.path.startswith("/__test"):
            continue
        path = route.path
        for param in route.param_convertors:
            path = path.replace("{" + param + "}", "1")
        for method in route.methods - {"HEAD"}:
            if (route.path, method) in PUBLIC:
                continue
            r = client.request(method, path, json={})
            assert r.status_code == 401, f"{method} {route.path} respondió {r.status_code}"
            checked += 1
    assert checked > 30


def test_secret_key_min_length():
    from pydantic import ValidationError

    from app.config import Settings

    with pytest.raises(ValidationError):
        Settings(DB_DSN="postgresql://x", SECRET_KEY="corta")


def test_login_rejects_huge_payload(client, users):
    r = client.post("/auth/login", json={"rut": MEDICO_RUT, "password": "x" * 5000})
    assert r.status_code == 422


def test_admin_role_from_db_not_token_for_new_routes(client, users, db):
    """Un usuario MEDICO con token válido no accede a las rutas nuevas de ADMIN."""
    token = login(client, MEDICO_RUT)
    assert client.get("/admin/errors", headers=auth(token)).status_code == 403
    user = make_user(db, UserRole.ADMINISTRATIVO, "44444444-4")
    assert client.post(f"/admin/users/{user.id}/unlock", headers=auth(token)).status_code == 403


def test_token_with_alg_none_is_rejected(client, users):
    """A02/A07: un token sin firma ("alg": "none") no se acepta."""
    import base64
    import json

    def b64(data: dict) -> str:
        return base64.urlsafe_b64encode(json.dumps(data).encode()).rstrip(b"=").decode()

    now = int(datetime.now(timezone.utc).timestamp())
    payload = {"sub": str(users["ADMIN"].id), "role": "ADMIN", "pwd": 0, "iat": now, "exp": now + 300}
    token = f"{b64({'alg': 'none', 'typ': 'JWT'})}.{b64(payload)}."
    assert client.get("/auth/me", headers=auth(token)).status_code == 401
