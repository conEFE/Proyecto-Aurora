"""E6: seguridad de cuentas (cambio de contraseña, bloqueo de login) y registro de errores

Revision ID: c9a3e1d8f709
Revises: b8f2d0c7e608
Create Date: 2026-11-09 12:00:00

Los usuarios existentes quedan con must_change_password = false (no se les obliga a cambiarla al migrar),
sin intentos fallidos y sin bloqueo. password_changed_at queda NULL: los tokens vigentes siguen sirviendo
hasta que el usuario cambie su contraseña.
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "c9a3e1d8f709"
down_revision: str | Sequence[str] | None = "b8f2d0c7e608"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("must_change_password", sa.Boolean(), nullable=False, server_default=sa.text("false")),
    )
    op.add_column("users", sa.Column("password_changed_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column(
        "users",
        sa.Column("failed_login_attempts", sa.Integer(), nullable=False, server_default=sa.text("0")),
    )
    op.add_column("users", sa.Column("locked_until", sa.DateTime(timezone=True), nullable=True))
    op.create_check_constraint("ck_users_failed_login_attempts", "users", "failed_login_attempts >= 0")

    op.create_table(
        "error_log",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        sa.Column("occurred_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("method", sa.String(10), nullable=False),
        sa.Column("path", sa.String(200), nullable=False),
        sa.Column("status_code", sa.Integer(), nullable=False),
        sa.Column("error_type", sa.String(120), nullable=False),
        sa.Column("message", sa.String(500), nullable=True),
        sa.Column("location", sa.String(200), nullable=True),
        sa.Column(
            "user_id", sa.Integer(), sa.ForeignKey("users.id", name="fk_error_log_user_id"), nullable=True
        ),
        sa.Column("request_id", sa.String(32), nullable=False),
    )
    op.create_index("ix_error_log_occurred_at", "error_log", ["occurred_at"])
    op.create_index("ix_error_log_error_type", "error_log", ["error_type"])
    op.create_index("ix_error_log_request_id", "error_log", ["request_id"])


def downgrade() -> None:
    op.drop_index("ix_error_log_request_id", table_name="error_log")
    op.drop_index("ix_error_log_error_type", table_name="error_log")
    op.drop_index("ix_error_log_occurred_at", table_name="error_log")
    op.drop_table("error_log")
    op.drop_constraint("ck_users_failed_login_attempts", "users", type_="check")
    op.drop_column("users", "locked_until")
    op.drop_column("users", "failed_login_attempts")
    op.drop_column("users", "password_changed_at")
    op.drop_column("users", "must_change_password")
