"""Helpers para crear datos ficticios en los tests (RUT de prueba, sin datos reales)."""

from datetime import date

from app.utils.rut import compute_dv

_counter = {"n": 20000000}


def fake_rut() -> str:
    _counter["n"] += 1
    body = str(_counter["n"])
    return f"{body}-{compute_dv(body)}"


def patient_payload(**overrides) -> dict:
    data = {
        "rut": fake_rut(),
        "first_name": "Paciente",
        "last_name": "Ficticia",
        "birth_date": "1970-05-20",
        "sex": "F",
        "family_history_first_degree": False,
        "previous_breast_cancer": False,
        "consent_given": True,
    }
    data.update(overrides)
    return data


def birth_date_for_age(age: int) -> str:
    today = date.today()
    return date(today.year - age, 1, 1).isoformat()


def create_patient(client, headers, **overrides) -> dict:
    r = client.post("/patients", json=patient_payload(**overrides), headers=headers)
    assert r.status_code == 201, r.text
    return r.json()


def create_case(client, headers, patient_id: int | None = None, **fields) -> dict:
    if patient_id is None:
        patient_id = create_patient(client, headers)["id"]
    r = client.post("/cases", json={"patient_id": patient_id, **fields}, headers=headers)
    assert r.status_code == 201, r.text
    return r.json()
