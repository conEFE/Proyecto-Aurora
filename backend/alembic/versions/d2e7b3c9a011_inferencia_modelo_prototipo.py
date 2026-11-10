"""Inferencia con modelo real: marca de validación clínica del modelo

Revision ID: d2e7b3c9a011
Revises: c1d4f2a8e910
Create Date: 2026-11-10 18:00:00

inference_results.clinically_validated: false salvo que el servicio de inferencia declare un modelo validado
clínicamente. Los resultados existentes (todos de la IA simulada) quedan en false.
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "d2e7b3c9a011"
down_revision: str | Sequence[str] | None = "c1d4f2a8e910"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "inference_results",
        sa.Column("clinically_validated", sa.Boolean(), nullable=False, server_default=sa.text("false")),
    )


def downgrade() -> None:
    op.drop_column("inference_results", "clinically_validated")
