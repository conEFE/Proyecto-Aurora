"""sprint6: revisión médica, registro de reportes y métricas de requests

Revision ID: f6d0b8a5c406
Revises: e5c9a7f4b305
Create Date: 2026-10-07 20:00:00
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "f6d0b8a5c406"
down_revision: str | Sequence[str] | None = "e5c9a7f4b305"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "clinical_reviews",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("case_id", sa.Integer(), sa.ForeignKey("cases.id"), nullable=False, unique=True),
        sa.Column("medico_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("birads_final", sa.SmallInteger(), nullable=False),
        sa.Column("findings", sa.Text(), nullable=False),
        sa.Column("recommendation", sa.String(30), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.CheckConstraint("birads_final BETWEEN 0 AND 6", name="ck_clinical_reviews_birads"),
        sa.CheckConstraint(
            "recommendation IN ('CONTROL_RUTINA','CONTROL_6_MESES','ESTUDIO_COMPLEMENTARIO','BIOPSIA','DERIVACION')",
            name="ck_clinical_reviews_recommendation",
        ),
    )
    op.create_table(
        "reports",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("case_id", sa.Integer(), sa.ForeignKey("cases.id"), nullable=False),
        sa.Column("generated_by", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("generated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.Column("dicom_metadata", postgresql.JSONB(), nullable=False),
        sa.Column("content_hash", sa.String(64), nullable=False),
    )
    op.create_index("ix_reports_case_id", "reports", ["case_id"])
    op.create_table(
        "request_metrics",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        sa.Column("method", sa.String(10), nullable=False),
        sa.Column("path", sa.String(200), nullable=False),
        sa.Column("status_code", sa.Integer(), nullable=False),
        sa.Column("duration_ms", sa.Float(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
    )
    op.create_index("ix_request_metrics_created_at", "request_metrics", ["created_at"])


def downgrade() -> None:
    op.drop_index("ix_request_metrics_created_at", table_name="request_metrics")
    op.drop_table("request_metrics")
    op.drop_index("ix_reports_case_id", table_name="reports")
    op.drop_table("reports")
    op.drop_table("clinical_reviews")
