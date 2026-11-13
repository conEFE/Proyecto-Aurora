"""Resumen para el administrador: estado de las cuentas, seguridad y actividad (sin datos clínicos)."""

from datetime import date, datetime, timedelta, timezone

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.config import settings
from app.db.models.audit_log import AuditLog
from app.db.models.error_log import ErrorLog
from app.db.models.user import User, UserRole
from app.schemas.admin import AdminOverview, DayLogins

# Los días se cuentan en la hora de Chile, como los ve el equipo
LOCAL_TZ = "America/Santiago"
SECURITY_ACTIONS = ("LOGIN_FAIL", "PASSWORD_CHANGE_FAIL", "SIGN_FAIL")


def overview(db: Session, now: datetime | None = None, days: int = 14) -> AdminOverview:
    now = now or datetime.now(timezone.utc)
    users = db.query(User).all()
    active = [u for u in users if u.is_active]

    def aware(dt: datetime | None) -> datetime | None:
        if dt is None:
            return None
        return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)

    idle_cutoff = now - timedelta(days=30)
    by_role = {r.value: 0 for r in UserRole}
    for u in active:
        by_role[u.role.value] += 1

    # Ingresos correctos y fallidos por día (hora de Chile), con los días sin movimiento en cero
    local_day = func.date(func.timezone(LOCAL_TZ, AuditLog.created_at))
    since = now - timedelta(days=days)
    rows = (
        db.query(local_day, AuditLog.action, func.count(AuditLog.id))
        .filter(AuditLog.action.in_(("LOGIN_OK", "LOGIN_FAIL")), AuditLog.created_at >= since)
        .group_by(local_day, AuditLog.action)
        .all()
    )
    counts: dict[date, dict[str, int]] = {}
    for d, action, n in rows:
        counts.setdefault(d, {})[action] = n
    # «Hoy» también en hora de Chile, calculado por la BD (no depende de tzdata en el contenedor)
    today = db.query(func.date(func.timezone(LOCAL_TZ, now))).scalar()
    per_day = []
    for i in range(days - 1, -1, -1):
        d = today - timedelta(days=i)
        c = counts.get(d, {})
        per_day.append(DayLogins(day=d.isoformat(), ok=c.get("LOGIN_OK", 0), failed=c.get("LOGIN_FAIL", 0)))

    week = now - timedelta(days=7)
    actions_7d = dict(
        db.query(AuditLog.action, func.count(AuditLog.id))
        .filter(AuditLog.created_at >= week)
        .group_by(AuditLog.action)
        .all()
    )
    security_24h = (
        db.query(func.count(AuditLog.id))
        .filter(AuditLog.action.in_(SECURITY_ACTIONS), AuditLog.created_at >= now - timedelta(hours=24))
        .scalar()
        or 0
    )
    errors_7d = db.query(func.count(ErrorLog.id)).filter(ErrorLog.occurred_at >= week).scalar() or 0
    last_error = db.query(func.max(ErrorLog.occurred_at)).scalar()

    return AdminOverview(
        version=settings.AURORA_VERSION,
        users_total=len(users),
        users_active=len(active),
        users_by_role=by_role,
        users_locked=sum(1 for u in active if aware(u.locked_until) and aware(u.locked_until) > now),
        users_pending_password=sum(1 for u in active if u.must_change_password),
        users_idle_30d=sum(
            1 for u in active if u.last_login_at is None or aware(u.last_login_at) < idle_cutoff
        ),
        admins_active=by_role[UserRole.ADMIN.value],
        security_events_24h=security_24h,
        logins_per_day=per_day,
        actions_7d=actions_7d,
        server_errors_7d=errors_7d,
        last_server_error_at=last_error,
        audit_total=db.query(func.count(AuditLog.id)).scalar() or 0,
    )
