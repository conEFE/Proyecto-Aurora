"""sprint4: metadatos de imagen (tipo de examen, lateralidad, sha256) e inferencia simulada marcada

Revision ID: d4b8f6e3a204
Revises: c3a7e5d2f103
Create Date: 2026-10-07 16:00:00

Decisiones sobre filas existentes:
- Las imágenes existentes quedan como MAMOGRAFIA, sin lateralidad, sin uploaded_by ni sha256.
- Todos los resultados de inferencia existentes se marcan is_simulated = true (en la v1.0 eran aleatorios).
- model_version nulo se rellena con 'placeholder-v1.0' (el valor por defecto que usaba la v1.0).
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "d4b8f6e3a204"
down_revision: str | Sequence[str] | None = "c3a7e5d2f103"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

exam_type = sa.Enum("MAMOGRAFIA", "ECOGRAFIA", "OTRO", name="examtype")


def upgrade() -> None:
    exam_type.create(op.get_bind(), checkfirst=True)
    op.add_column("images", sa.Column("exam_type", exam_type, server_default="MAMOGRAFIA", nullable=False))
    op.add_column("images", sa.Column("laterality", sa.String(1), nullable=True))
    op.create_check_constraint("ck_images_laterality", "images", "laterality IN ('L','R')")
    op.add_column("images", sa.Column("uploaded_by", sa.Integer(), nullable=True))
    op.create_foreign_key("fk_images_uploaded_by", "images", "users", ["uploaded_by"], ["id"])
    op.add_column("images", sa.Column("sha256", sa.String(64), nullable=True))
    op.create_index("ix_images_case_id", "images", ["case_id"])

    op.add_column(
        "inference_results",
        sa.Column("is_simulated", sa.Boolean(), server_default=sa.text("true"), nullable=False),
    )
    op.execute("UPDATE inference_results SET model_version = 'placeholder-v1.0' WHERE model_version IS NULL")
    op.alter_column("inference_results", "model_version", existing_type=sa.String(), nullable=False)


def downgrade() -> None:
    op.alter_column("inference_results", "model_version", existing_type=sa.String(), nullable=True)
    op.drop_column("inference_results", "is_simulated")

    op.drop_index("ix_images_case_id", table_name="images")
    op.drop_column("images", "sha256")
    op.drop_constraint("fk_images_uploaded_by", "images", type_="foreignkey")
    op.drop_column("images", "uploaded_by")
    op.drop_constraint("ck_images_laterality", "images", type_="check")
    op.drop_column("images", "laterality")
    op.drop_column("images", "exam_type")
    exam_type.drop(op.get_bind(), checkfirst=True)
