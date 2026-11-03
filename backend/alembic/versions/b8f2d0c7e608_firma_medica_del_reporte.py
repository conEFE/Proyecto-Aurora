"""firma (conformidad) del médico sobre el reporte clínico

Revision ID: b8f2d0c7e608
Revises: a7e1c9b6d507
Create Date: 2026-10-18 20:00:00

Los reportes ya emitidos quedan con signature_id NULL (no se inventa una firma que el médico no hizo);
la API exige la firma para todo reporte nuevo.
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "b8f2d0c7e608"
down_revision: str | Sequence[str] | None = "a7e1c9b6d507"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "report_signatures",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("case_id", sa.Integer(), sa.ForeignKey("cases.id"), nullable=False, unique=True),
        sa.Column("medico_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("signed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("content_hash", sa.String(64), nullable=False),
        sa.Column("signature", sa.String(64), nullable=False),
    )
    op.add_column("reports", sa.Column("signature_id", sa.Integer(), nullable=True))
    op.create_foreign_key(
        "fk_reports_signature_id", "reports", "report_signatures", ["signature_id"], ["id"]
    )


def downgrade() -> None:
    op.drop_constraint("fk_reports_signature_id", "reports", type_="foreignkey")
    op.drop_column("reports", "signature_id")
    op.drop_table("report_signatures")
