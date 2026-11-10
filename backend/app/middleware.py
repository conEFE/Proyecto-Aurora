"""Middleware de tiempos de respuesta, request_id, registro de errores 5xx y encabezados de seguridad."""

import logging
import time
import uuid

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from app.config import settings

logger = logging.getLogger("aurora.requests")

GENERIC_ERROR = "Error interno del servidor. Si el problema persiste, informe el código {request_id}"

# OWASP A05: encabezados para una API JSON (la documentación /docs necesita cargar sus scripts)
SECURITY_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "Referrer-Policy": "no-referrer",
    "Cross-Origin-Opener-Policy": "same-origin",
    "Permissions-Policy": "camera=(), microphone=(), geolocation=()",
    # Los navegadores solo lo aplican si la respuesta llega por HTTPS
    "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
}
_DOCS_PATHS = ("/docs", "/redoc", "/openapi.json")


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
        from app.services.error_log_service import record_error

        start = time.perf_counter()
        request_id = uuid.uuid4().hex
        request.state.request_id = request_id
        try:
            response = await call_next(request)
        except Exception as exc:  # error no controlado: se registra y se responde sin detalles internos
            path = _route_template(request)
            logger.exception("Error no controlado %s en %s %s", request_id, request.method, path)
            record_error(request.method, path, 500, request_id, exc, getattr(request.state, "user_id", None))
            response = JSONResponse(
                status_code=500,
                content={"detail": GENERIC_ERROR.format(request_id=request_id), "request_id": request_id},
            )
        else:
            if response.status_code >= 500:
                record_error(
                    request.method,
                    _route_template(request),
                    response.status_code,
                    request_id,
                    user_id=getattr(request.state, "user_id", None),
                )
        elapsed_ms = (time.perf_counter() - start) * 1000
        response.headers["X-Process-Time-Ms"] = f"{elapsed_ms:.1f}"
        response.headers["X-Request-ID"] = request_id
        for name, value in SECURITY_HEADERS.items():
            response.headers.setdefault(name, value)
        if not request.url.path.startswith(_DOCS_PATHS):
            response.headers.setdefault("Cache-Control", "no-store")  # datos clínicos: sin caché
            response.headers.setdefault(
                "Content-Security-Policy", "default-src 'none'; frame-ancestors 'none'"
            )
        path = _route_template(request)
        logger.info("%s %s -> %s %.1fms", request.method, path, response.status_code, elapsed_ms)
        if settings.REQUEST_METRICS_ENABLED and request.method != "OPTIONS" and path != "/health":
            _store_metric(request.method, path, response.status_code, elapsed_ms)
        return response
