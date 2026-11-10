"""Cumplimiento Ley 21.719: consentimiento versionado, historial, bloqueo y solicitudes de los titulares

Revision ID: c1d4f2a8e910
Revises: c9a3e1d8f709
Create Date: 2026-11-10 12:00:00

- consent_texts: versiones inmutables del texto de consentimiento; se crea la v1 activa.
- patient_consent_events: historial de otorgamiento y retiro. Los pacientes con consentimiento registrado antes de
  esta versión reciben un evento OTORGADO con consent_text_id NULL (el texto que aceptaron no estaba versionado);
  no se inventa una versión que no vieron.
- patients: consent_text_id, blocked_at, blocked_by, block_reason.
- data_subject_requests: solicitudes de acceso, rectificación, supresión, oposición, portabilidad y bloqueo.
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "c1d4f2a8e910"
down_revision: str | Sequence[str] | None = "c9a3e1d8f709"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

# Copia congelada de app/services/consent_text.py (v1). No editar: una versión nueva va en otra migración.
CONSENT_TEXT_VERSION_V1 = "2026-11-v1"
CONSENT_TEXT_BODY_V1 = (
    "CONSENTIMIENTO INFORMADO PARA EL TRATAMIENTO DE DATOS PERSONALES Y DE SALUD\n"
    "Plataforma Aurora de apoyo a la detección temprana y priorización de casos sospechosos de cáncer de mama\n"
    "\n"
    "1. Responsable. El establecimiento de salud que la atiende es responsable del tratamiento de sus datos. Puede contactarlo por los canales de atención del establecimiento para cualquier consulta o solicitud sobre sus datos.\n"
    "\n"
    "2. Datos que se tratan. Datos de identificación (RUT, nombre, fecha de nacimiento y sexo), antecedentes clínicos relevantes (antecedentes familiares y personales de cáncer de mama, síntomas y BI-RADS informado) e imágenes mamarias (mamografía, ecografía o resonancia). Los datos de salud son datos sensibles.\n"
    "\n"
    "3. Finalidad. Apoyar la priorización (triage) y la revisión médica de su caso. La plataforma usa reglas y un sistema de inteligencia artificial como apoyo: ninguna decisión se toma solo de forma automatizada, porque un médico revisa, puede corregir y firma el resultado. Sus datos no se usan para otros fines ni se ceden a terceros sin una base legal.\n"
    "\n"
    "4. Seguridad. El acceso está limitado al personal autorizado según su función y queda registrado. Las imágenes se guardan cifradas y los reportes identifican el caso con un código anónimo.\n"
    "\n"
    "5. Conservación. Los datos forman parte de su ficha clínica y se conservan por el plazo que exige la ley (Ley 20.584, al menos 15 años). Cumplido el plazo, se eliminan o se anonimizan.\n"
    "\n"
    "6. Alojamiento. Los datos pueden alojarse en servidores de un proveedor de nube, incluso fuera de Chile, con contratos que garantizan un nivel de protección adecuado y cifrado.\n"
    "\n"
    "7. Sus derechos. Puede pedir acceso a sus datos, su rectificación, su supresión o bloqueo, oponerse a su tratamiento y solicitar una copia en formato electrónico (portabilidad). La respuesta se entrega en un plazo de 30 días corridos. Cuando la ley obligue a conservar la ficha clínica, la supresión se reemplaza por el bloqueo de los datos.\n"
    "\n"
    "8. Retiro del consentimiento. Puede retirar este consentimiento en cualquier momento, sin expresión de causa. El retiro impide registrar nuevos casos e imágenes en la plataforma, pero no afecta la licitud del tratamiento anterior ni la obligación de conservar la ficha clínica.\n"
    "\n"
    "Declaro haber sido informada o informado de lo anterior y autorizo el tratamiento de mis datos personales y de salud para la finalidad descrita (Ley 19.628 y Ley 21.719)."
)


def upgrade() -> None:
    op.create_table(
        "consent_texts",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("version", sa.String(20), nullable=False, unique=True),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
    )
    op.create_index(
        "uq_consent_texts_active",
        "consent_texts",
        ["is_active"],
        unique=True,
        postgresql_where=sa.text("is_active"),
    )
    op.get_bind().execute(
        sa.text("INSERT INTO consent_texts (version, body, is_active) VALUES (:v, :b, true)"),
        {"v": CONSENT_TEXT_VERSION_V1, "b": CONSENT_TEXT_BODY_V1},
    )

    op.add_column("patients", sa.Column("consent_text_id", sa.Integer(), nullable=True))
    op.create_foreign_key(
        "fk_patients_consent_text_id", "patients", "consent_texts", ["consent_text_id"], ["id"]
    )
    op.add_column("patients", sa.Column("blocked_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("patients", sa.Column("blocked_by", sa.Integer(), nullable=True))
    op.create_foreign_key("fk_patients_blocked_by", "patients", "users", ["blocked_by"], ["id"])
    op.add_column("patients", sa.Column("block_reason", sa.String(500), nullable=True))

    op.create_table(
        "patient_consent_events",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("patient_id", sa.Integer(), sa.ForeignKey("patients.id"), nullable=False),
        sa.Column("action", sa.String(10), nullable=False),
        sa.Column("consent_text_id", sa.Integer(), sa.ForeignKey("consent_texts.id"), nullable=True),
        sa.Column("occurred_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("registered_by", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("note", sa.String(500), nullable=True),
        sa.CheckConstraint("action IN ('OTORGADO','RETIRADO')", name="ck_patient_consent_events_action"),
    )
    op.create_index("ix_patient_consent_events_patient_id", "patient_consent_events", ["patient_id"])
    op.get_bind().execute(
        sa.text(
            "INSERT INTO patient_consent_events (patient_id, action, consent_text_id, occurred_at, "
            "registered_by, note) "
            "SELECT id, 'OTORGADO', NULL, COALESCE(consent_at, created_at, now()), consent_registered_by, "
            "'Registrado antes de la versión 2.4.0 (texto no versionado)' "
            "FROM patients WHERE consent_given"
        )
    )

    op.create_table(
        "data_subject_requests",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("patient_id", sa.Integer(), sa.ForeignKey("patients.id"), nullable=False),
        sa.Column("request_type", sa.String(20), nullable=False),
        sa.Column("status", sa.String(12), nullable=False, server_default=sa.text("'RECIBIDA'")),
        sa.Column("detail", sa.String(1000), nullable=True),
        sa.Column("received_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("due_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("registered_by", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("resolved_by", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("resolution", sa.String(1000), nullable=True),
        sa.CheckConstraint(
            "request_type IN ('ACCESO','RECTIFICACION','SUPRESION','OPOSICION','PORTABILIDAD','BLOQUEO')",
            name="ck_data_subject_requests_type",
        ),
        sa.CheckConstraint(
            "status IN ('RECIBIDA','EN_PROCESO','RESUELTA','RECHAZADA')",
            name="ck_data_subject_requests_status",
        ),
    )
    op.create_index("ix_data_subject_requests_patient_id", "data_subject_requests", ["patient_id"])
    op.create_index("ix_data_subject_requests_due_at", "data_subject_requests", ["due_at"])


def downgrade() -> None:
    op.drop_index("ix_data_subject_requests_due_at", table_name="data_subject_requests")
    op.drop_index("ix_data_subject_requests_patient_id", table_name="data_subject_requests")
    op.drop_table("data_subject_requests")
    op.drop_index("ix_patient_consent_events_patient_id", table_name="patient_consent_events")
    op.drop_table("patient_consent_events")
    op.drop_column("patients", "block_reason")
    op.drop_constraint("fk_patients_blocked_by", "patients", type_="foreignkey")
    op.drop_column("patients", "blocked_by")
    op.drop_column("patients", "blocked_at")
    op.drop_constraint("fk_patients_consent_text_id", "patients", type_="foreignkey")
    op.drop_column("patients", "consent_text_id")
    op.drop_index("uq_consent_texts_active", table_name="consent_texts")
    op.drop_table("consent_texts")
