"""validación médica del resultado de IA (por imagen) y evaluación del triage (en la revisión)

Revision ID: a7e1c9b6d507
Revises: f6d0b8a5c406
Create Date: 2026-10-08 10:00:00

Las revisiones existentes quedan con triage_assessment NULL (no se inventa una evaluación que el médico no hizo);
la API la exige para toda revisión nueva.
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "a7e1c9b6d507"
down_revision: str | Sequence[str] | None = "f6d0b8a5c406"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "ai_validations",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("image_id", sa.Integer(), sa.ForeignKey("images.id"), nullable=False, unique=True),
        sa.Column("inference_result_id", sa.Integer(), sa.ForeignKey("inference_results.id"), nullable=False),
        sa.Column("medico_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("verdict", sa.String(20), nullable=False),
        sa.Column("comment", sa.Text(), nullable=True),
        sa.Column("ai_detected", sa.Boolean(), nullable=False),
        sa.Column("ai_model_version", sa.String(), nullable=False),
        sa.Column("ai_was_simulated", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.CheckConstraint(
            "verdict IN ('CONCORDANTE','FALSO_POSITIVO','FALSO_NEGATIVO','NO_EVALUABLE')",
            name="ck_ai_validations_verdict",
        ),
    )
    op.add_column("clinical_reviews", sa.Column("triage_assessment", sa.String(15), nullable=True))
    op.add_column("clinical_reviews", sa.Column("triage_comment", sa.Text(), nullable=True))
    op.add_column("clinical_reviews", sa.Column("triage_level_at_review", sa.String(5), nullable=True))
    op.add_column(
        "clinical_reviews", sa.Column("triage_config_version_at_review", sa.Integer(), nullable=True)
    )
    op.create_check_constraint(
        "ck_clinical_reviews_triage_assessment",
        "clinical_reviews",
        "triage_assessment IN ('APROPIADO','SOBREESTIMADO','SUBESTIMADO')",
    )


def downgrade() -> None:
    op.drop_constraint("ck_clinical_reviews_triage_assessment", "clinical_reviews", type_="check")
    for col in (
        "triage_config_version_at_review",
        "triage_level_at_review",
        "triage_comment",
        "triage_assessment",
    ):
        op.drop_column("clinical_reviews", col)
    op.drop_table("ai_validations")
