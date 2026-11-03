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
