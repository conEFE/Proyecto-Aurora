import re

from alembic import command
from sqlalchemy import inspect, text

from app.deps import engine
from app.tests.conftest import alembic_config, truncate_all


def test_downgrade_to_base_and_upgrade_to_head():
    """Toda migración debe ser reversible: base -> head -> base -> head."""
    cfg = alembic_config()
    command.downgrade(cfg, "base")
    tables = set(inspect(engine).get_table_names()) - {"alembic_version"}
    assert tables == set()
    command.upgrade(cfg, "head")
    assert {"users", "patients", "cases", "images", "inference_results"} <= set(
        inspect(engine).get_table_names()
    )


def test_upgrade_handles_v1_legacy_rows():
    """Filas de la v1.0 (caso sin paciente, código libre, paciente sin nombre) migran sin perderse."""
    cfg = alembic_config()
    command.downgrade(cfg, "56aef21d9c1b")  # esquema de la v1.0
    try:
        with engine.begin() as conn:
            conn.execute(
                text(
                    "INSERT INTO users (id, email, role, rut, password_hash) "
                    "VALUES (1, 'legacy@aurora-demo.cl', 'MEDICO', '11111111-1', 'x')"
                )
            )
            conn.execute(text("INSERT INTO patients (id, rut) VALUES (1, '22222222-2')"))
            conn.execute(
                text(
                    "INSERT INTO cases (id, code, medico_id, patient_id) VALUES "
                    "(1, 'Juana Perez 1', 1, NULL), (2, 'codigo-libre-muy-largo-de-la-v1', 1, 1)"
                )
            )
            for table in ("users", "patients", "cases"):
                conn.execute(text(f"SELECT setval('{table}_id_seq', 10)"))
        command.upgrade(cfg, "head")
        with engine.connect() as conn:
            rows = conn.execute(
                text("SELECT id, code, patient_id, status, created_by FROM cases ORDER BY id")
            ).all()
            assert all(re.match(r"^AUR-\d{4}-\d{6}$", r.code) for r in rows)
            assert all(r.status == "ABIERTO" and r.created_by == 1 for r in rows)
            placeholder = conn.execute(
                text("SELECT id, first_name, consent_given FROM patients WHERE rut = '1-9'")
            ).one()
            assert placeholder.first_name == "SIN-ASIGNAR" and placeholder.consent_given is False
            assert rows[0].patient_id == placeholder.id
            legacy = conn.execute(text("SELECT first_name, birth_date FROM patients WHERE id = 1")).one()
            assert legacy.first_name == "SIN REGISTRO"
            assert str(legacy.birth_date) == "1900-01-01"
            full_name = conn.execute(text("SELECT full_name FROM users WHERE id = 1")).scalar_one()
            assert full_name == "legacy@aurora-demo.cl"
    finally:
        command.upgrade(cfg, "head")
        truncate_all()


def test_upgrade_records_unversioned_consent_for_existing_patients():
    """2.4.0: los pacientes con consentimiento previo reciben un evento OTORGADO sin versión de texto."""
    cfg = alembic_config()
    truncate_all()
    command.downgrade(cfg, "c9a3e1d8f709")
    try:
        with engine.begin() as conn:
            conn.execute(
                text(
                    "INSERT INTO users (id, email, full_name, role, rut, password_hash) "
                    "VALUES (1, 'legacy@aurora-demo.cl', 'Legacy', 'MEDICO', '11111111-1', 'x')"
                )
            )
            conn.execute(
                text(
                    "INSERT INTO patients (id, rut, first_name, last_name, birth_date, consent_given, "
                    "consent_at, consent_registered_by) VALUES "
                    "(1, '22222222-2', 'Ana', 'Ficticia', '1970-01-01', true, now(), 1), "
                    "(2, '33333333-3', 'Bea', 'Ficticia', '1970-01-01', false, NULL, NULL)"
                )
            )
        command.upgrade(cfg, "head")
        with engine.connect() as conn:
            events = conn.execute(
                text(
                    "SELECT patient_id, action, consent_text_id, registered_by, note FROM patient_consent_events"
                )
            ).all()
            assert [(e.patient_id, e.action, e.consent_text_id, e.registered_by) for e in events] == [
                (1, "OTORGADO", None, 1)
            ]
            assert "no versionado" in events[0].note
            active = conn.execute(text("SELECT version FROM consent_texts WHERE is_active")).scalar_one()
            assert active.startswith("2026-11")
    finally:
        command.upgrade(cfg, "head")
        truncate_all()
