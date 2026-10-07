import re

import pytest

from app.db.models.audit_log import AuditLog
from app.db.models.case import Case, CaseStatus
from app.db.models.patient import Patient
from app.services import case_service
from app.services.errors import ConflictError
from app.tests.conftest import auth
from app.tests.factories import create_case, create_patient

CODE_RE = re.compile(r"^AUR-\d{4}-\d{6}$")


# --- Máquina de estados (unitario) -----------------------------------------

VALID = [
    (CaseStatus.ABIERTO, CaseStatus.PRIORIZADO),
    (CaseStatus.PRIORIZADO, CaseStatus.ABIERTO),
    (CaseStatus.PRIORIZADO, CaseStatus.EN_REVISION),
    (CaseStatus.EN_REVISION, CaseStatus.CERRADO),
]
INVALID = [
    (CaseStatus.ABIERTO, CaseStatus.EN_REVISION),
    (CaseStatus.ABIERTO, CaseStatus.CERRADO),
    (CaseStatus.PRIORIZADO, CaseStatus.CERRADO),
    (CaseStatus.EN_REVISION, CaseStatus.ABIERTO),
    (CaseStatus.EN_REVISION, CaseStatus.PRIORIZADO),
    (CaseStatus.CERRADO, CaseStatus.ABIERTO),
    (CaseStatus.CERRADO, CaseStatus.PRIORIZADO),
    (CaseStatus.CERRADO, CaseStatus.EN_REVISION),
]


@pytest.mark.parametrize("current,target", VALID)
def test_valid_transitions(current, target):
    case = Case(status=current)
    case_service.transition(case, target)
    assert case.status == target
    if target == CaseStatus.CERRADO:
        assert case.closed_at is not None


@pytest.mark.parametrize("current,target", INVALID)
def test_invalid_transitions_raise_409(current, target):
    case = Case(status=current)
    with pytest.raises(ConflictError) as exc:
        case_service.transition(case, target)
    assert exc.value.status_code == 409
    assert case.status == current


def test_mark_data_changed_reopens_only_prioritized():
    prioritized = Case(status=CaseStatus.PRIORIZADO)
    case_service.mark_data_changed(prioritized)
    assert prioritized.status == CaseStatus.ABIERTO
    in_review = Case(status=CaseStatus.EN_REVISION)
    case_service.mark_data_changed(in_review)
    assert in_review.status == CaseStatus.EN_REVISION


# --- API -------------------------------------------------------------------


@pytest.mark.parametrize("role", ["ADMINISTRATIVO", "MEDICO"])
def test_create_case_for_patient_with_consent(client, tokens, users, role):
    h = auth(tokens[role])
    case = create_case(client, h, palpable_mass=True, birads_reported=3)
    assert CODE_RE.match(case["code"])
    # Desde S5 el triage se calcula al crear el caso, que pasa de ABIERTO a PRIORIZADO
    assert case["status"] == "PRIORIZADO"
    assert case["triage_level"] in ("ALTA", "MEDIA", "BAJA")
    assert case["created_by"] == users[role].id
    assert case["palpable_mass"] is True and case["birads_reported"] == 3
    assert case["patient"]["first_name"] == "Paciente"


def test_case_codes_are_unique_and_sequential(client, tokens):
    h = auth(tokens["MEDICO"])
    pid = create_patient(client, h)["id"]
    codes = [create_case(client, h, pid)["code"] for _ in range(3)]
    assert len(set(codes)) == 3
    numbers = [int(c.rsplit("-", 1)[1]) for c in codes]
    assert numbers == sorted(numbers)


def test_case_without_consent_is_409(client, tokens, db):
    patient = Patient(rut="5126663-3", first_name="Sin", last_name="Consentimiento", birth_date="1960-01-01")
    db.add(patient)
    db.commit()
    r = client.post("/cases", json={"patient_id": patient.id}, headers=auth(tokens["MEDICO"]))
    assert r.status_code == 409
    assert "consentimiento" in r.json()["detail"]


def test_case_for_missing_patient_is_404(client, tokens):
    r = client.post("/cases", json={"patient_id": 999}, headers=auth(tokens["MEDICO"]))
    assert r.status_code == 404


def test_case_requires_patient(client, tokens):
    r = client.post("/cases", json={}, headers=auth(tokens["MEDICO"]))
    assert r.status_code == 422


def test_birads_out_of_range_is_422(client, tokens):
    h = auth(tokens["MEDICO"])
    pid = create_patient(client, h)["id"]
    r = client.post("/cases", json={"patient_id": pid, "birads_reported": 7}, headers=h)
    assert r.status_code == 422


def test_update_symptoms_and_birads(client, tokens, db):
    h = auth(tokens["ADMINISTRATIVO"])
    case = create_case(client, h)
    r = client.patch(f"/cases/{case['id']}", json={"nipple_discharge": True, "birads_reported": 4}, headers=h)
    assert r.status_code == 200
    assert r.json()["nipple_discharge"] is True
    assert r.json()["birads_reported"] == 4
    # Quitar el BI-RADS informado
    r = client.patch(f"/cases/{case['id']}", json={"birads_reported": None}, headers=h)
    assert r.json()["birads_reported"] is None


def test_closed_case_is_read_only(client, tokens, db):
    h = auth(tokens["MEDICO"])
    case = create_case(client, h)
    db_case = db.get(Case, case["id"])
    db_case.status = CaseStatus.CERRADO
    db.commit()
    r = client.patch(f"/cases/{case['id']}", json={"palpable_mass": True}, headers=h)
    assert r.status_code == 409


def test_list_cases_with_status_filter(client, tokens, db):
    h = auth(tokens["MEDICO"])
    a = create_case(client, h)
    create_case(client, h)
    db_case = db.get(Case, a["id"])
    db_case.status = CaseStatus.EN_REVISION
    db.commit()

    r = client.get("/cases", headers=h)
    assert r.status_code == 200 and r.json()["total"] == 2
    r = client.get("/cases?status=EN_REVISION", headers=h)
    assert r.json()["total"] == 1
    assert r.json()["items"][0]["id"] == a["id"]


def test_admin_cannot_access_cases(client, tokens):
    h = auth(tokens["ADMIN"])
    assert client.get("/cases", headers=h).status_code == 403
    assert client.post("/cases", json={"patient_id": 1}, headers=h).status_code == 403
    assert client.get("/cases/1", headers=h).status_code == 403


def test_case_view_and_update_are_audited(client, tokens, db):
    h = auth(tokens["MEDICO"])
    case = create_case(client, h)
    client.get(f"/cases/{case['id']}", headers=h)
    client.patch(f"/cases/{case['id']}", json={"palpable_mass": True}, headers=h)
    actions = {
        a.action
        for a in db.query(AuditLog).filter(AuditLog.entity == "case", AuditLog.entity_id == case["id"])
    }
    assert {"CREATE", "VIEW", "UPDATE"} <= actions
