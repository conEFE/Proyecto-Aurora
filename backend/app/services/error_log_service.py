"""Registro de errores 5xx (KPI K9). Nunca guarda datos personales: el mensaje se recorta y se sanea."""

import logging
import re
import traceback
from datetime import datetime

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.db.models.error_log import ErrorLog

logger = logging.getLogger("aurora.errors")

_REDACTIONS = [
    (re.compile(r"\[SQL:.*", re.S), "[SQL omitido]"),  # SQLAlchemy agrega la consulta y sus parámetros
    (re.compile(r"\[parameters:.*", re.S), ""),
    (re.compile(r"DETAIL:[^\n]*"), ""),  # PostgreSQL repite los valores en conflicto
    (re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+"), "[email]"),
    (re.compile(r"\b\d{1,2}\.?\d{3}\.?\d{3}-?[\dkK]\b"), "[rut]"),
    (re.compile(r"\d{4,}"), "[n]"),
    (re.compile(r"'[^']{0,200}'"), "'…'"),  # valores entre comillas
]


def sanitize_message(exc: BaseException) -> str | None:
    text = str(exc).strip()
    if not text:
        return None
    for pattern, repl in _REDACTIONS:
        text = pattern.sub(repl, text)
    text = " ".join(text.split())
    return text[:500] or None


def _location(exc: BaseException) -> str | None:
    """Último punto del código propio (app/) donde ocurrió el error: archivo:línea en función."""
    frames = traceback.extract_tb(exc.__traceback__) if exc.__traceback__ else []
    own = [f for f in frames if "/app/" in f.filename.replace("\\", "/")]
    frame = (own or frames or [None])[-1]
    if frame is None:
        return None
    path = frame.filename.replace("\\", "/")
    path = path[path.rfind("/app/") + 1 :] if "/app/" in path else path.rsplit("/", 1)[-1]
    return f"{path}:{frame.lineno} en {frame.name}"[:200]


def record_error(
    method: str,
    path: str,
    status_code: int,
    request_id: str,
    exc: BaseException | None = None,
    user_id: int | None = None,
) -> None:
    """Guarda el error en una sesión propia; si falla, solo lo deja en el log (nunca rompe la respuesta)."""
    from app.deps import SessionLocal

    if exc is not None:
        error_type = f"{type(exc).__module__}.{type(exc).__qualname__}"
        message, location = sanitize_message(exc), _location(exc)
    else:
        error_type, message, location = f"HTTP_{status_code}", None, None
    try:
        with SessionLocal() as db:
            db.add(
                ErrorLog(
                    method=method[:10],
                    path=path[:200],
                    status_code=status_code,
                    error_type=error_type[:120],
                    message=message,
                    location=location,
                    user_id=user_id,
                    request_id=request_id,
                )
            )
            db.commit()
    except Exception:
        logger.warning("No se pudo registrar el error %s de %s %s", request_id, method, path, exc_info=True)


def list_errors(
    db: Session,
    date_from: datetime | None,
    date_to: datetime | None,
    error_type: str | None,
    status_code: int | None,
    page: int,
    size: int,
) -> tuple[list[ErrorLog], int]:
    q = db.query(ErrorLog)
    if date_from:
        q = q.filter(ErrorLog.occurred_at >= date_from)
    if date_to:
        q = q.filter(ErrorLog.occurred_at <= date_to)
    if error_type:
        q = q.filter(ErrorLog.error_type.ilike(f"%{error_type}%"))
    if status_code:
        q = q.filter(ErrorLog.status_code == status_code)
    total = q.count()
    items = q.order_by(ErrorLog.id.desc()).offset((page - 1) * size).limit(size).all()
    return items, total


def error_types(db: Session) -> list[dict]:
    rows = (
        db.query(ErrorLog.error_type, func.count(ErrorLog.id))
        .group_by(ErrorLog.error_type)
        .order_by(func.count(ErrorLog.id).desc())
        .all()
    )
    return [{"error_type": t, "count": c} for t, c in rows]
