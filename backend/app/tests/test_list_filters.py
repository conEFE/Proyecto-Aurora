"""Filtros nuevos: casos por código parcial y fechas, pacientes por estado y dashboard por nivel y médico."""

from datetime import datetime, timedelta, timezone

from app.db.models.case import Case
from app.db.models.user import UserRole
from app.tests.conftest import auth, login, make_user
from app.tests.factories import create_case, create_patient
from app.tests.test_reviews_reports import _take_and_review


def _codes(r):
    assert r.status_code == 200, r.text
    return {c["code"] for c in r.json()["items"]}


# --- Casos -----------------------------------------------------------------------


def test_cases_search_by_partial_code_and_number(client, tokens):
    h = auth(tokens["ADMINISTRATIVO"])
    created = [create_case(client, h)["code"] for _ in range(3)]
    target = created[1]
    number = str(int(target.rsplit("-", 1)[1]))  # «000002» → «2»

    assert _codes(client.get(f"/cases?q={target[-6:]}", headers=h)) == {target}
    assert target in _codes(client.get(f"/cases?q={number}", headers=h))
    assert _codes(client.get(f"/cases?q={target.lower()}", headers=h)) == {target}
    assert _codes(client.get("/cases?q=AUR", headers=h)) == set(created)
    assert _codes(client.get("/cases?q=999999", headers=h)) == set()


def test_cases_filter_by_creation_date(client, tokens, db):
    h = auth(tokens["ADMINISTRATIVO"])
    old = create_case(client, h)
    recent = create_case(client, h)
    db.get(Case, old["id"]).created_at = datetime.now(timezone.utc) - timedelta(days=20)
    db.commit()
    since = (datetime.now(timezone.utc) - timedelta(days=5)).date().isoformat()
    until = (datetime.now(timezone.utc) - timedelta(days=10)).date().isoformat()

    assert _codes(client.get(f"/cases?from={since}T00:00:00", headers=h)) == {recent["code"]}
    assert _codes(client.get(f"/cases?to={until}T23:59:59", headers=h)) == {old["code"]}


# --- Pacientes -------------------------------------------------------------------


def test_patients_filter_by_status(client, tokens):
    h = auth(tokens["ADMINISTRATIVO"])
    active = create_patient(client, h)
    withdrawn = create_patient(client, h)
    blocked = create_patient(client, h)
    assert client.post(f"/patients/{withdrawn['id']}/consent/withdraw", json={}, headers=h).status_code == 200
    r = client.post(f"/patients/{blocked['id']}/block", json={"reason": "Solicitud de supresión"}, headers=h)
    assert r.status_code == 200, r.text

    def ids(status):
        r = client.get(f"/patients?status={status}", headers=h)
        assert r.status_code == 200, r.text
        return {p["id"] for p in r.json()}

    assert ids("activo") == {active["id"]}
    assert ids("sin_consentimiento") == {withdrawn["id"]}
    assert ids("bloqueado") == {blocked["id"]}
    assert client.get("/patients?status=otro", headers=h).status_code == 422


# --- Dashboard -------------------------------------------------------------------


def test_dashboard_filters_by_level_and_reviewer(client, tokens, users, db):
    h = auth(tokens["MEDICO"])
    other = make_user(db, UserRole.MEDICO, "77777777-7")
    h2 = auth(login(client, other.rut))
    alta = create_case(client, h, birads_reported=5)  # ALTA
    baja = create_case(client, h)  # BAJA
    _take_and_review(client, h, alta["id"])  # revisado por el médico del fixture
    assert client.post(f"/cases/{baja['id']}/take", headers=h2).status_code == 200  # en revisión con el otro

    admin = auth(tokens["ADMIN"])
    m = client.get("/dashboard/metrics?level=ALTA", headers=admin).json()
    assert m["total_cases"] == 1 and m["cases_by_level"]["ALTA"] == 1
    m = client.get(f"/dashboard/metrics?medico_id={users['MEDICO'].id}", headers=admin).json()
    assert m["total_cases"] == 1 and m["cases_by_status"]["CERRADO"] == 1
    m = client.get(f"/dashboard/metrics?medico_id={other.id}", headers=admin).json()
    assert m["total_cases"] == 1 and m["cases_by_status"]["EN_REVISION"] == 1

    names = {r["full_name"] for r in client.get("/dashboard/reviewers", headers=auth(tokens["ADMINISTRATIVO"])).json()}
    assert names == {users["MEDICO"].full_name, other.full_name}


def test_dashboard_case_rows_mark_late_alta(client, tokens, db):
    h = auth(tokens["MEDICO"])
    late = create_case(client, h, birads_reported=5)  # ALTA sin revisar
    fresh = create_case(client, h, birads_reported=5)
    db.get(Case, late["id"]).created_at = datetime.now(timezone.utc) - timedelta(hours=30)
    db.commit()

    rows = client.get("/dashboard/cases?alta_pending_hours=24", headers=auth(tokens["ADMIN"])).json()
    assert [r["code"] for r in rows][0] == late["code"]  # los atrasados primero
    by_code = {r["code"]: r for r in rows}
    assert by_code[late["code"]]["late"] is True and by_code[late["code"]]["waiting_hours"] >= 30
    assert by_code[fresh["code"]]["late"] is False
    assert by_code[late["code"]]["level"] == "ALTA"
    # Solo el código anónimo: nada del paciente
    assert not any(k.startswith("patient") for k in rows[0])


# --- Búsqueda sin tildes y paginación de pacientes ----------------------------------


def test_patient_search_ignores_accents(client, tokens):
    h = auth(tokens["ADMINISTRATIVO"])
    maria = create_patient(client, h, first_name="María José", last_name="Núñez")
    create_patient(client, h, first_name="Mario", last_name="Pérez")

    def names(term, path="/patients"):
        r = client.get(f"{path}?search={term}", headers=h)
        assert r.status_code == 200, r.text
        body = r.json()
        return {p["id"] for p in (body["items"] if isinstance(body, dict) else body)}

    for term in ("Maria", "maría", "MARIA JOSE", "nunez", "Núñez", "maria jose nunez"):
        assert maria["id"] in names(term), term
        assert maria["id"] in names(term, "/patients/page"), term
    assert maria["id"] not in names("Mario")


def test_patient_pages_cover_everyone_with_total(client, tokens):
    h = auth(tokens["ADMINISTRATIVO"])
    created = {create_patient(client, h)["id"] for _ in range(7)}
    seen = set()
    for page in (1, 2, 3):
        body = client.get(f"/patients/page?page={page}&size=3", headers=h).json()
        assert body["total"] == 7 and body["page"] == page
        seen |= {p["id"] for p in body["items"]}
    assert seen == created
    # El total también respeta los filtros
    assert client.get("/patients/page?status=bloqueado", headers=h).json()["total"] == 0


# --- Sesión que se renueva con la actividad -----------------------------------------


def test_refresh_issues_new_token_until_password_changes(client, tokens):
    old = tokens["MEDICO"]
    r = client.post("/auth/refresh", headers=auth(old))
    assert r.status_code == 200, r.text
    new = r.json()["access_token"]
    assert client.get("/auth/me", headers=auth(new)).status_code == 200
    # Sin token o con un token inválido no se renueva
    assert client.post("/auth/refresh").status_code == 401
    assert client.post("/auth/refresh", headers=auth("x.y.z")).status_code == 401
