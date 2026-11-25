"""Rol JEFATURA, nombre y apellido separados, especialidad médica y verificación de email

Revision ID: e7f1a2b3c412
Revises: d2e7b3c9a011
Create Date: 2026-11-25 12:00:00

- userrole: nuevo valor JEFATURA (jefatura y finanzas: dashboard y comparador de médicos, sin datos clínicos).
- users.first_name / users.last_name: se completan partiendo full_name en el primer espacio. full_name se mantiene
  (lo usan reportes, bitácora y dashboard) y el servicio lo recalcula desde nombre y apellido.
- users.specialty: enum medicalspecialty, obligatorio solo para médicos (lo valida el servicio). Los médicos
  existentes quedan con NULL hasta que el administrador la complete.
- users.email_verified_at: los usuarios existentes quedan verificados (se crearon a mano por el administrador).
- email_tokens: tokens de un solo uso (activación de cuenta); se guarda solo el hash SHA-256.
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "e7f1a2b3c412"
down_revision: str | Sequence[str] | None = "d2e7b3c9a011"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

SPECIALTIES = (
    "MEDICINA_GENERAL",
    "GINECOLOGIA",
    "ONCOLOGIA",
    "MASTOLOGIA",
    "RADIOLOGIA",
    "CIRUGIA_GENERAL",
    "MEDICINA_FAMILIAR",
    "OTRA",
)


def upgrade() -> None:
    op.execute("ALTER TYPE userrole ADD VALUE IF NOT EXISTS 'JEFATURA'")

    specialty = sa.Enum(*SPECIALTIES, name="medicalspecialty")
    specialty.create(op.get_bind(), checkfirst=True)

    op.add_column("users", sa.Column("first_name", sa.String(75), nullable=True))
    op.add_column("users", sa.Column("last_name", sa.String(75), nullable=True))
    op.execute(
        """
        UPDATE users SET
            first_name = split_part(btrim(full_name), ' ', 1),
            last_name = CASE WHEN position(' ' in btrim(full_name)) > 0
                             THEN btrim(substr(btrim(full_name), position(' ' in btrim(full_name)) + 1))
                             ELSE '' END
        """
    )
    op.alter_column("users", "first_name", nullable=False)
    op.alter_column("users", "last_name", nullable=False, server_default="")
    op.add_column(
        "users", sa.Column("specialty", sa.Enum(*SPECIALTIES, name="medicalspecialty", create_type=False))
    )
    op.add_column("users", sa.Column("email_verified_at", sa.DateTime(timezone=True), nullable=True))
    op.execute("UPDATE users SET email_verified_at = COALESCE(created_at, now())")

    op.create_table(
        "email_tokens",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("purpose", sa.String(20), nullable=False),
        sa.Column("token_hash", sa.String(64), nullable=False, unique=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("used_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_email_tokens_user_id", "email_tokens", ["user_id"])


def downgrade() -> None:
    conn = op.get_bind()
    n = conn.execute(sa.text("SELECT count(*) FROM users WHERE role = 'JEFATURA'")).scalar()
    if n:
        raise RuntimeError(
            f"No se puede revertir: existen {n} usuarios JEFATURA. Reasígnelos o elimínelos antes del downgrade."
        )
    op.drop_index("ix_email_tokens_user_id", table_name="email_tokens")
    op.drop_table("email_tokens")
    op.drop_column("users", "email_verified_at")
    op.drop_column("users", "specialty")
    sa.Enum(name="medicalspecialty").drop(conn, checkfirst=True)
    op.drop_column("users", "last_name")
    op.drop_column("users", "first_name")
    # Postgres no permite quitar un valor de un enum: se recrea el tipo.
    op.execute("ALTER TYPE userrole RENAME TO userrole_old")
    op.execute("CREATE TYPE userrole AS ENUM ('MEDICO', 'ADMIN', 'ADMINISTRATIVO')")
    op.execute("ALTER TABLE users ALTER COLUMN role TYPE userrole USING role::text::userrole")
    op.execute("DROP TYPE userrole_old")
