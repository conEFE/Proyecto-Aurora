"""sprint5: configuración de triage versionada, resultados de triage y notificaciones

Revision ID: e5c9a7f4b305
Revises: d4b8f6e3a204
Create Date: 2026-10-07 18:00:00

Incluye el seed de la configuración v1 (sección 5 de la especificación). Es una propuesta técnica,
no un criterio clínico validado: los médicos deben revisarla desde la interfaz.
"""

import json
from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "e5c9a7f4b305"
down_revision: str | Sequence[str] | None = "d4b8f6e3a204"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

DEFAULT_PARAMS_V1 = {
    "escalation": {"birads_alta": [4, 5], "symptoms_alta": True},
    "weights": {"ai": 40, "age": 15, "family_history": 15, "previous_cancer": 20, "wait_time": 10},
    "age_bands": {"high": [50, 69], "medium": [[40, 49], [70, 120]]},
    "max_wait_days": 30,
    "thresholds": {"alta": 60, "media": 30},
}

triage_level = postgresql.ENUM("ALTA", "MEDIA", "BAJA", name="triagelevel", create_type=False)


def upgrade() -> None:
    postgresql.ENUM("ALTA", "MEDIA", "BAJA", name="triagelevel").create(op.get_bind(), checkfirst=True)

    op.create_table(
        "triage_configs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("version", sa.Integer(), nullable=False, unique=True),
        sa.Column("params", postgresql.JSONB(), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("created_by", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.Column("change_reason", sa.Text(), nullable=False),
    )
    op.create_index(
        "uq_triage_configs_active",
        "triage_configs",
        ["is_active"],
        unique=True,
        postgresql_where=sa.text("is_active"),
    )

    op.create_table(
        "triage_results",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("case_id", sa.Integer(), sa.ForeignKey("cases.id"), nullable=False),
        sa.Column("config_version", sa.Integer(), sa.ForeignKey("triage_configs.version"), nullable=False),
        sa.Column("score", sa.Numeric(5, 2), nullable=False),
        sa.Column("computed_level", triage_level, nullable=False),
        sa.Column("escalation_rule", sa.String(50), nullable=True),
        sa.Column("breakdown", postgresql.JSONB(), nullable=True),
        sa.Column("final_level", triage_level, nullable=False),
        sa.Column("override_by", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("override_reason", sa.Text(), nullable=True),
        sa.Column("is_current", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("computed_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint("score >= 0 AND score <= 100", name="ck_triage_results_score"),
        sa.CheckConstraint(
            "override_by IS NULL OR (override_reason IS NOT NULL AND length(trim(override_reason)) > 0)",
            name="ck_triage_results_override_reason",
        ),
    )
    op.create_index("ix_triage_results_case_id", "triage_results", ["case_id"])
    op.create_index(
        "uq_triage_results_current",
        "triage_results",
        ["case_id"],
        unique=True,
        postgresql_where=sa.text("is_current"),
    )

    op.create_table(
        "notifications",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("case_id", sa.Integer(), sa.ForeignKey("cases.id"), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("read_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
    )
    op.create_index("ix_notifications_user_id", "notifications", ["user_id"])

    op.get_bind().execute(
        sa.text(
            "INSERT INTO triage_configs (version, params, is_active, created_by, change_reason) "
            "VALUES (1, CAST(:params AS JSONB), true, NULL, :reason)"
        ),
        {
            "params": json.dumps(DEFAULT_PARAMS_V1),
            "reason": "Configuración inicial v1 (propuesta técnica, pendiente de validación médica)",
        },
    )


def downgrade() -> None:
    op.drop_index("ix_notifications_user_id", table_name="notifications")
    op.drop_table("notifications")
    op.drop_index("uq_triage_results_current", table_name="triage_results")
    op.drop_index("ix_triage_results_case_id", table_name="triage_results")
    op.drop_table("triage_results")
    op.drop_index("uq_triage_configs_active", table_name="triage_configs")
    op.drop_table("triage_configs")
    postgresql.ENUM(name="triagelevel").drop(op.get_bind(), checkfirst=True)
