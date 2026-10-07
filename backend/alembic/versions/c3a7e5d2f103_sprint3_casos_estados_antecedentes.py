"""sprint3: estados de caso, síntomas, BI-RADS y paciente obligatorio

Revision ID: c3a7e5d2f103
Revises: b2f1c0a9d801
Create Date: 2026-10-07 14:00:00

Decisiones sobre filas existentes:
- Casos con patient_id NULL se asignan a un paciente de prueba "SIN-ASIGNAR" (RUT ficticio 1-9,
  sin consentimiento). Así no se pierden casos ni imágenes de desarrollo.
- Todos los códigos existentes se regeneran con el formato AUR-AAAA-NNNNNN: los códigos de la v1.0 eran
  texto libre ingresado a mano y podían contener datos identificables.
- Los casos existentes quedan en estado ABIERTO.
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "c3a7e5d2f103"
down_revision: str | Sequence[str] | None = "b2f1c0a9d801"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

PLACEHOLDER_RUT = "1-9"
case_status = sa.Enum("ABIERTO", "PRIORIZADO", "EN_REVISION", "CERRADO", name="casestatus")


def upgrade() -> None:
    conn = op.get_bind()

    # Paciente "SIN-ASIGNAR" solo si hay casos huérfanos
    orphans = conn.execute(sa.text("SELECT count(*) FROM cases WHERE patient_id IS NULL")).scalar()
    if orphans:
        conn.execute(
            sa.text(
                "INSERT INTO patients (rut, first_name, last_name, birth_date, consent_given) "
                "VALUES (:rut, 'SIN-ASIGNAR', 'SIN-ASIGNAR', DATE '1900-01-01', false) "
                "ON CONFLICT (rut) DO NOTHING"
            ),
            {"rut": PLACEHOLDER_RUT},
        )
        conn.execute(
            sa.text(
                "UPDATE cases SET patient_id = (SELECT id FROM patients WHERE rut = :rut) "
                "WHERE patient_id IS NULL"
            ),
            {"rut": PLACEHOLDER_RUT},
        )
    op.alter_column("cases", "patient_id", existing_type=sa.Integer(), nullable=False)
    op.create_index("ix_cases_patient_id", "cases", ["patient_id"])

    # Código anónimo: secuencia global y regeneración de los códigos existentes
    op.execute("CREATE SEQUENCE IF NOT EXISTS case_code_seq START 1")
    op.execute(
        "UPDATE cases SET code = 'AUR-' || to_char(COALESCE(created_at, now()), 'YYYY') || '-' "
        "|| lpad(nextval('case_code_seq')::text, 6, '0')"
    )
    op.alter_column("cases", "code", type_=sa.String(20), existing_nullable=False)

    # medico_id -> created_by, y médico asignado
    op.alter_column("cases", "medico_id", new_column_name="created_by")
    op.add_column("cases", sa.Column("assigned_medico_id", sa.Integer(), nullable=True))
    op.create_foreign_key("fk_cases_assigned_medico_id", "cases", "users", ["assigned_medico_id"], ["id"])

    # Estado, síntomas, BI-RADS y timestamps
    case_status.create(conn, checkfirst=True)
    op.add_column("cases", sa.Column("status", case_status, server_default="ABIERTO", nullable=False))
    op.create_index("ix_cases_status", "cases", ["status"])
    for col in ("palpable_mass", "nipple_discharge", "skin_or_nipple_changes"):
        op.add_column("cases", sa.Column(col, sa.Boolean(), server_default=sa.text("false"), nullable=False))
    op.add_column("cases", sa.Column("birads_reported", sa.SmallInteger(), nullable=True))
    op.create_check_constraint("ck_cases_birads_reported", "cases", "birads_reported BETWEEN 0 AND 6")
    op.add_column(
        "cases",
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
    )
    op.add_column("cases", sa.Column("closed_at", sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    op.drop_column("cases", "closed_at")
    op.drop_column("cases", "updated_at")
    op.drop_constraint("ck_cases_birads_reported", "cases", type_="check")
    op.drop_column("cases", "birads_reported")
    for col in ("skin_or_nipple_changes", "nipple_discharge", "palpable_mass"):
        op.drop_column("cases", col)
    op.drop_index("ix_cases_status", table_name="cases")
    op.drop_column("cases", "status")
    case_status.drop(op.get_bind(), checkfirst=True)

    op.drop_constraint("fk_cases_assigned_medico_id", "cases", type_="foreignkey")
    op.drop_column("cases", "assigned_medico_id")
    op.alter_column("cases", "created_by", new_column_name="medico_id")

    op.alter_column("cases", "code", type_=sa.String(), existing_nullable=False)
    op.execute("DROP SEQUENCE IF EXISTS case_code_seq")

    op.drop_index("ix_cases_patient_id", table_name="cases")
    op.alter_column("cases", "patient_id", existing_type=sa.Integer(), nullable=True)
    conn = op.get_bind()
    conn.execute(
        sa.text(
            "UPDATE cases SET patient_id = NULL "
            "WHERE patient_id = (SELECT id FROM patients WHERE rut = :rut AND first_name = 'SIN-ASIGNAR')"
        ),
        {"rut": PLACEHOLDER_RUT},
    )
    conn.execute(
        sa.text("DELETE FROM patients WHERE rut = :rut AND first_name = 'SIN-ASIGNAR'"),
        {"rut": PLACEHOLDER_RUT},
    )
