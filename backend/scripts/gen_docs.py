"""Genera docs/modelo_datos.md (desde los modelos SQLAlchemy) y docs/endpoints.md (desde las rutas FastAPI).

Uso (desde backend/):  python -m scripts.gen_docs
No necesita conexión a la BD.
"""

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT.parent / "docs"
sys.path.insert(0, str(ROOT))
os.environ.setdefault("DB_DSN", "postgresql+psycopg2://docs:docs@localhost:5432/docs")
os.environ.setdefault("SECRET_KEY", "solo-para-generar-documentacion")

from fastapi.routing import APIRoute  # noqa: E402
from sqlalchemy import CheckConstraint, Enum, Index, UniqueConstraint  # noqa: E402

import app.db.models  # noqa: E402,F401
from app.db.base import Base  # noqa: E402
from app.main import app  # noqa: E402

TABLE_DESCRIPTIONS = {
    "users": "Usuarios de la plataforma y su rol.",
    "patients": "Pacientes (datos ficticios en desarrollo) con antecedentes y consentimiento informado.",
    "cases": "Casos clínicos con código anónimo, estado, síntomas y BI-RADS informado.",
    "images": "Imágenes del caso (archivo cifrado en el StorageBackend).",
    "inference_results": "Resultado del proveedor de IA por imagen (marcado si es simulado).",
    "triage_configs": "Versiones de los parámetros de triage (una activa).",
    "triage_results": "Cálculos de triage por caso; uno vigente y el resto como historial.",
    "notifications": "Avisos a médicos cuando un caso queda en ALTA.",
    "clinical_reviews": "Revisión médica que cierra el caso.",
    "reports": "Registro de cada PDF generado (SHA-256 y metadatos tipo DICOM).",
    "audit_log": "Bitácora append-only de accesos y cambios (trigger bloquea UPDATE/DELETE).",
    "request_metrics": "Duración de cada request de la API (p95 del dashboard).",
}

COLUMN_DESCRIPTIONS = {
    "users.rut": "RUT del usuario (validado con dígito verificador)",
    "users.role": "ADMIN, MEDICO o ADMINISTRATIVO",
    "users.password_hash": "Hash bcrypt",
    "patients.consent_given": "Consentimiento informado registrado (obligatorio para crear casos)",
    "patients.consent_registered_by": "Usuario que registró el consentimiento",
    "cases.code": "Código anónimo AUR-AAAA-NNNNNN (secuencia case_code_seq)",
    "cases.status": "ABIERTO, PRIORIZADO, EN_REVISION o CERRADO",
    "cases.birads_reported": "BI-RADS informado (0–6)",
    "images.filepath": "Clave del archivo cifrado (nombre aleatorio)",
    "images.sha256": "SHA-256 del archivo original (integridad)",
    "inference_results.is_simulated": "true si lo generó el proveedor simulado",
    "triage_results.breakdown": "Aporte de cada factor y regla disparada",
    "triage_results.final_level": "Nivel vigente: el calculado o el fijado por override",
    "reports.content_hash": "SHA-256 del PDF generado en el frontend",
    "reports.dicom_metadata": "PatientID (= código del caso), StudyDate, Modality=MG, hallazgos (SC-02)",
    "audit_log.detail": "Contexto de la acción, sin datos sensibles en claro",
}


def column_type(col) -> str:
    t = col.type
    if isinstance(t, Enum):
        return f"ENUM({', '.join(t.enums)})"
    try:
        return str(t.compile())
    except Exception:
        return type(t).__name__.upper()


def constraints(col, table) -> str:
    parts = []
    if col.primary_key:
        parts.append("PK")
    for fk in col.foreign_keys:
        parts.append(f"FK → {fk.column.table.name}.{fk.column.name}")
    if col.unique or any(
        isinstance(c, UniqueConstraint) and list(c.columns.keys()) == [col.name] for c in table.constraints
    ):
        parts.append("UNIQUE")
    parts.append("NULL" if col.nullable and not col.primary_key else "NOT NULL")
    if col.server_default is not None:
        parts.append(f"DEFAULT {getattr(col.server_default, 'arg', col.server_default)}")
    return ", ".join(str(p) for p in parts)


def gen_data_model() -> str:
    tables = sorted(
        Base.metadata.tables.values(),
        key=lambda t: list(TABLE_DESCRIPTIONS).index(t.name) if t.name in TABLE_DESCRIPTIONS else 99,
    )
    out = [
        "# Modelo de datos — Proyecto Aurora",
        "",
        "Generado automáticamente desde los modelos SQLAlchemy con `python -m scripts.gen_docs`. No editar a mano.",
        "",
        "## Diccionario de datos",
        "",
    ]
    for table in tables:
        out += [f"### {table.name}", "", TABLE_DESCRIPTIONS.get(table.name, ""), ""]
        out += ["| Campo | Tipo | Restricción | Descripción |", "|---|---|---|---|"]
        for col in table.columns:
            desc = COLUMN_DESCRIPTIONS.get(f"{table.name}.{col.name}", "")
            out.append(f"| {col.name} | {column_type(col)} | {constraints(col, table)} | {desc} |")
        extras = [str(c.sqltext) for c in table.constraints if isinstance(c, CheckConstraint)]
        idx = [
            f"{i.name} ({', '.join(c.name for c in i.columns)})"
            + (
                f" WHERE {i.dialect_options['postgresql']['where']}"
                if i.dialect_options["postgresql"].get("where") is not None
                else ""
            )
            for i in table.indexes
            if isinstance(i, Index) and i.unique
        ]
        if extras:
            out += ["", "CHECK: " + "; ".join(f"`{e}`" for e in extras)]
        if idx:
            out += ["", "Índices únicos: " + "; ".join(f"`{i}`" for i in idx)]
        out.append("")

    out += ["## Diagrama entidad-relación", "", "```mermaid", "erDiagram"]
    for table in tables:
        out.append(f"    {table.name} {{")
        for col in table.columns:
            t = "enum" if isinstance(col.type, Enum) else type(col.type).__name__.lower()
            key = "PK" if col.primary_key else ("FK" if col.foreign_keys else "")
            out.append(f"        {t} {col.name} {key}".rstrip())
        out.append("    }")
    seen = set()
    for table in tables:
        for col in table.columns:
            for fk in col.foreign_keys:
                parent = fk.column.table.name
                rel = (parent, table.name, col.name)
                if rel in seen:
                    continue
                seen.add(rel)
                card = "||--o|" if col.unique else "||--o{"
                out.append(f'    {parent} {card} {table.name} : "{col.name}"')
    out += ["```", ""]
    return "\n".join(out)


def roles_of(route: APIRoute) -> str:
    found: set[str] = set()
    authenticated = False

    def walk(dep):
        nonlocal authenticated
        call = dep.call
        if hasattr(call, "allowed_roles"):
            found.update(call.allowed_roles)
        if getattr(call, "__name__", "") == "get_current_user":
            authenticated = True
        for sub in dep.dependencies:
            walk(sub)

    walk(route.dependant)
    if found:
        return ", ".join(sorted(found))
    return "Cualquier usuario autenticado" if authenticated else "Público"


def gen_endpoints() -> str:
    out = [
        "# Endpoints — Proyecto Aurora API",
        "",
        "Generado automáticamente desde las rutas FastAPI con `python -m scripts.gen_docs`. La especificación completa",
        "está en `/openapi.json` y la documentación interactiva en `/docs` del backend.",
        "",
        "| Método | Ruta | Roles permitidos | Descripción |",
        "|---|---|---|---|",
    ]
    routes = [r for r in app.routes if isinstance(r, APIRoute)]
    for r in sorted(routes, key=lambda r: (r.path, sorted(r.methods)[0])):
        doc = (r.description or r.summary or r.name.replace("_", " ")).strip().splitlines()[0]
        for method in sorted(r.methods):
            out.append(f"| {method} | `{r.path}` | {roles_of(r)} | {doc} |")
    out.append("")
    return "\n".join(out)


def main() -> None:
    DOCS.mkdir(exist_ok=True)
    (DOCS / "modelo_datos.md").write_text(gen_data_model(), encoding="utf-8")
    (DOCS / "endpoints.md").write_text(gen_endpoints(), encoding="utf-8")
    print("Generados docs/modelo_datos.md y docs/endpoints.md")


if __name__ == "__main__":
    main()
