"""Las listas no hacen una consulta por fila (N+1): el número de consultas no crece con el tamaño de la página.

Con la prueba de carga en AWS (24-11-2026), /cases y /dashboard/metrics fueron los endpoints más lentos: /cases
hacía tres consultas por caso (paciente, imágenes y nivel) y /patients/page recargaba cada paciente después de
auditar. Estas pruebas fijan que el costo por solicitud sea constante.
"""

from contextlib import contextmanager

from sqlalchemy import event

from app.deps import engine
from app.tests.conftest import auth
from app.tests.factories import create_case, create_patient


@contextmanager
def count_queries():
    counter = {"n": 0}

    def _count(*_args, **_kwargs):
        counter["n"] += 1

    event.listen(engine, "before_cursor_execute", _count)
    try:
        yield counter
    finally:
        event.remove(engine, "before_cursor_execute", _count)


def _queries(client, url, headers) -> int:
    with count_queries() as counter:
        r = client.get(url, headers=headers)
    assert r.status_code == 200, r.text
    return counter["n"]


def test_list_endpoints_do_not_query_per_row(client, tokens):
    admin = auth(tokens["ADMINISTRATIVO"])
    medico = auth(tokens["MEDICO"])
    create_case(client, admin)
    urls = ["/cases?size=50", "/patients/page?size=50", "/triage/queue"]
    few = {url: _queries(client, url, medico) for url in urls}

    for _ in range(6):
        create_case(client, admin)
        create_patient(client, admin)
    many = {url: _queries(client, url, medico) for url in urls}

    assert many == few, f"Consultas con 1 fila: {few}; con 7 filas: {many}"


def test_case_list_keeps_patient_images_and_level(client, tokens):
    admin = auth(tokens["ADMINISTRATIVO"])
    created = create_case(client, admin)
    item = next(c for c in client.get("/cases", headers=admin).json()["items"] if c["id"] == created["id"])
    detail = client.get(f"/cases/{created['id']}", headers=admin).json()
    assert item["patient"] == detail["patient"] and item["patient"] is not None
    assert item["image_count"] == detail["image_count"] == 0
    assert item["triage_level"] == detail["triage_level"] and item["triage_level"] is not None


def test_patient_page_keeps_consent_version(client, tokens):
    admin = auth(tokens["ADMINISTRATIVO"])
    patient = create_patient(client, admin)
    item = next(p for p in client.get("/patients/page", headers=admin).json()["items"] if p["id"] == patient["id"])
    assert item["consent_text_version"] == patient["consent_text_version"] is not None
