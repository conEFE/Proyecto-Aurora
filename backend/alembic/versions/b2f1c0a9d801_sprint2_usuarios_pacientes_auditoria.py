"""sprint2: rol ADMINISTRATIVO, campos de usuario y paciente, consentimiento y audit_log

Revision ID: b2f1c0a9d801
Revises: 56aef21d9c1b
Create Date: 2026-10-07 12:00:00

Decisiones sobre filas existentes:
- users.full_name: se rellena con el email del usuario.
- patients.first_name / last_name nulos: se rellenan con 'SIN REGISTRO'.
- patients.birth_date nulo: se rellena con 1900-01-01 (marcador evidente, revisar a mano).
- patients.sex fuera de F/M/O: se deja en NULL.
- Pacientes existentes quedan con consent_given = false (deben registrar consentimiento).
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "b2f1c0a9d801"
down_revision: str | Sequence[str] | None = "56aef21d9c1b"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # --- users -------------------------------------------------------------
    op.execute("ALTER TYPE userrole ADD VALUE IF NOT EXISTS 'ADMINISTRATIVO'")
    op.add_column("users", sa.Column("full_name", sa.String(150), nullable=True))
    op.execute("UPDATE users SET full_name = email WHERE full_name IS NULL")
    op.alter_column("users", "full_name", nullable=False)
    op.add_column(
        "users", sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False)
    )
    op.add_column(
        "users",
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
    )
    op.add_column("users", sa.Column("last_login_at", sa.DateTime(timezone=True), nullable=True))
    op.alter_column("users", "rut", type_=sa.String(12), existing_nullable=False)
    op.alter_column("users", "email", type_=sa.String(150), existing_nullable=False)

    # --- patients ----------------------------------------------------------
    op.execute("UPDATE patients SET first_name = 'SIN REGISTRO' WHERE first_name IS NULL")
    op.execute("UPDATE patients SET last_name = 'SIN REGISTRO' WHERE last_name IS NULL")
    op.execute("UPDATE patients SET birth_date = DATE '1900-01-01' WHERE birth_date IS NULL")
    op.execute("UPDATE patients SET sex = NULL WHERE sex IS NOT NULL AND sex NOT IN ('F','M','O')")
    op.alter_column("patients", "rut", type_=sa.String(12), existing_nullable=False)
    op.alter_column("patients", "first_name", type_=sa.String(100), nullable=False)
    op.alter_column("patients", "last_name", type_=sa.String(100), nullable=False)
    op.alter_column("patients", "birth_date", existing_type=sa.Date(), nullable=False)
    op.alter_column("patients", "sex", type_=sa.String(1), existing_nullable=True)
    op.create_check_constraint("ck_patients_sex", "patients", "sex IN ('F','M','O')")
    for col in ("family_history_first_degree", "previous_breast_cancer", "consent_given"):
        op.add_column(
            "patients", sa.Column(col, sa.Boolean(), server_default=sa.text("false"), nullable=False)
        )
    op.add_column("patients", sa.Column("consent_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("patients", sa.Column("consent_registered_by", sa.Integer(), nullable=True))
    op.add_column("patients", sa.Column("created_by", sa.Integer(), nullable=True))
    op.create_foreign_key(
        "fk_patients_consent_registered_by", "patients", "users", ["consent_registered_by"], ["id"]
    )
    op.create_foreign_key("fk_patients_created_by", "patients", "users", ["created_by"], ["id"])

    # --- audit_log (append-only) -------------------------------------------
    op.create_table(
        "audit_log",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("action", sa.String(40), nullable=False),
        sa.Column("entity", sa.String(30), nullable=False),
        sa.Column("entity_id", sa.Integer(), nullable=True),
        sa.Column("ip_address", sa.String(45), nullable=True),
        sa.Column("detail", postgresql.JSONB(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
    )
    op.create_index("ix_audit_log_user_id", "audit_log", ["user_id"])
    op.create_index("ix_audit_log_action", "audit_log", ["action"])
    op.create_index("ix_audit_log_created_at", "audit_log", ["created_at"])
    op.execute("""
        CREATE OR REPLACE FUNCTION audit_log_append_only() RETURNS trigger AS $$
        BEGIN
            RAISE EXCEPTION 'audit_log es append-only: % no permitido', TG_OP;
        END;
        $$ LANGUAGE plpgsql;
        """)
    op.execute(
        "CREATE TRIGGER trg_audit_log_append_only BEFORE UPDATE OR DELETE ON audit_log "
        "FOR EACH ROW EXECUTE FUNCTION audit_log_append_only()"
    )


def downgrade() -> None:
    op.execute("DROP TRIGGER IF EXISTS trg_audit_log_append_only ON audit_log")
    op.execute("DROP FUNCTION IF EXISTS audit_log_append_only()")
    op.drop_index("ix_audit_log_created_at", table_name="audit_log")
    op.drop_index("ix_audit_log_action", table_name="audit_log")
    op.drop_index("ix_audit_log_user_id", table_name="audit_log")
    op.drop_table("audit_log")

    op.drop_constraint("fk_patients_created_by", "patients", type_="foreignkey")
    op.drop_constraint("fk_patients_consent_registered_by", "patients", type_="foreignkey")
    for col in (
        "created_by",
        "consent_registered_by",
        "consent_at",
        "consent_given",
        "previous_breast_cancer",
        "family_history_first_degree",
    ):
        op.drop_column("patients", col)
    op.drop_constraint("ck_patients_sex", "patients", type_="check")
    op.alter_column("patients", "sex", type_=sa.String(), existing_nullable=True)
    op.alter_column("patients", "birth_date", existing_type=sa.Date(), nullable=True)
    op.alter_column("patients", "last_name", type_=sa.String(), nullable=True)
    op.alter_column("patients", "first_name", type_=sa.String(), nullable=True)
    op.alter_column("patients", "rut", type_=sa.String(), existing_nullable=False)

    op.alter_column("users", "email", type_=sa.String(), existing_nullable=False)
    op.alter_column("users", "rut", type_=sa.String(), existing_nullable=False)
    op.drop_column("users", "last_login_at")
    op.drop_column("users", "created_at")
    op.drop_column("users", "is_active")
    op.drop_column("users", "full_name")

    # Postgres no permite quitar un valor de un enum: se recrea el tipo.
    conn = op.get_bind()
    n = conn.execute(sa.text("SELECT count(*) FROM users WHERE role = 'ADMINISTRATIVO'")).scalar()
    if n:
        raise RuntimeError(
            f"No se puede revertir: existen {n} usuarios ADMINISTRATIVO. "
            "Reasígnelos o elimínelos antes del downgrade."
        )
    op.execute("ALTER TYPE userrole RENAME TO userrole_new")
    op.execute("CREATE TYPE userrole AS ENUM ('MEDICO', 'ADMIN')")
    op.execute("ALTER TABLE users ALTER COLUMN role TYPE userrole USING role::text::userrole")
    op.execute("DROP TYPE userrole_new")
