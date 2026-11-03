"""Middleware de tiempos de respuesta (insumo del KPI ≤ 3 s y del p95 del dashboard)."""

import logging
import time

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from app.config import settings

logger = logging.getLogger("aurora.requests")


def _route_template(request: Request) -> str:
    route = request.scope.get("route")
    path = getattr(route, "path", None) or request.url.path
    return path[:200]


def _store_metric(method: str, path: str, status_code: int, duration_ms: float) -> None:
    from app.db.models.review import RequestMetric
    from app.deps import SessionLocal

    try:
        with SessionLocal() as db:
            db.add(RequestMetric(method=method, path=path, status_code=status_code, duration_ms=duration_ms))
            db.commit()
    except Exception:  # la métrica nunca debe romper la request
        logger.warning("No se pudo registrar la métrica de %s %s", method, path, exc_info=True)


class ProcessTimeMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start = time.perf_counter()
        response = await call_next(request)
        elapsed_ms = (time.perf_counter() - start) * 1000
        response.headers["X-Process-Time-Ms"] = f"{elapsed_ms:.1f}"
        path = _route_template(request)
        logger.info("%s %s -> %s %.1fms", request.method, path, response.status_code, elapsed_ms)
        if settings.REQUEST_METRICS_ENABLED and request.method != "OPTIONS" and path != "/health":
            _store_metric(request.method, path, response.status_code, elapsed_ms)
        return response
