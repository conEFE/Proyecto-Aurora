from datetime import datetime, timedelta, timezone

from jose import jwt

from app.auth.security import create_access_token
from app.tests.conftest import PASSWORD, auth, login


def test_login_ok_returns_jwt(client, users):
    r = client.post("/auth/login", json={"rut": "11111111-1", "password": PASSWORD})
    assert r.status_code == 200
    body = r.json()
    assert body["token_type"] == "bearer"
    assert body["role"] == "MEDICO"
    assert "full_name" in body
    claims = jwt.get_unverified_claims(body["access_token"])
    assert claims["sub"] == str(users["MEDICO"].id)
    assert claims["role"] == "MEDICO"
    assert {"exp", "iat"} <= claims.keys()


def test_login_wrong_password(client, users):
    r = client.post("/auth/login", json={"rut": "11111111-1", "password": "incorrecta"})
    assert r.status_code == 401
    assert r.json()["detail"] == "RUT o contraseña incorrectos"


def test_login_unknown_user(client, users):
    r = client.post("/auth/login", json={"rut": "99999999-9", "password": PASSWORD})
    assert r.status_code == 401


def test_me_with_valid_token(client, users):
    token = login(client, "11111111-1")
    r = client.get("/auth/me", headers=auth(token))
    assert r.status_code == 200
    assert r.json()["rut"] == "11111111-1"


def test_missing_token_is_401(client, users):
    assert client.get("/auth/me").status_code == 401


def test_expired_token_is_401(client, users):
    token = create_access_token(users["MEDICO"].id, "MEDICO", expires_minutes=-1)
    assert client.get("/auth/me", headers=auth(token)).status_code == 401


def test_tampered_token_is_401(client, users):
    token = login(client, "11111111-1")
    header, payload, signature = token.split(".")
    tampered = f"{header}.{payload}.{signature[:-4]}AAAA"
    assert client.get("/auth/me", headers=auth(tampered)).status_code == 401


def test_token_signed_with_other_key_is_401(client, users):
    now = datetime.now(timezone.utc)
    forged = jwt.encode(
        {
            "sub": str(users["ADMIN"].id),
            "role": "ADMIN",
            "iat": int(now.timestamp()),
            "exp": int((now + timedelta(minutes=5)).timestamp()),
        },
        "otra-clave",
        algorithm="HS256",
    )
    assert client.get("/auth/me", headers=auth(forged)).status_code == 401


def test_legacy_rut_role_token_is_401(client, users):
    assert client.get("/auth/me", headers=auth("1-ADMIN")).status_code == 401
    assert client.get("/auth/me", headers=auth("22222222-2-ADMIN")).status_code == 401


def test_role_is_read_from_db_not_from_token(client, users):
    # Un MEDICO con un token que dice ADMIN sigue siendo MEDICO para la API
    token = create_access_token(users["MEDICO"].id, "ADMIN")
    assert client.get("/admin/stats", headers=auth(token)).status_code == 403


def test_process_time_header(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert "X-Process-Time-Ms" in r.headers
