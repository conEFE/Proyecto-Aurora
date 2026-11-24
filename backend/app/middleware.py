"""Middleware de tiempos de respuesta, request_id, registro de errores 5xx y encabezados de seguridad."""

import asyncio
import json
import logging
import time
import uuid

from starlette.concurrency import run_in_threadpool
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
    from app.deps import AuxSessionLocal

    try:
        with AuxSessionLocal() as db:
            db.add(RequestMetric(method=method, path=path, status_code=status_code, duration_ms=duration_ms))
            db.commit()
    except Exception:  # la métrica nunca debe romper la request
        logger.warning("No se pudo registrar la métrica de %s %s", method, path, exc_info=True)


class ProcessTimeMiddleware(BaseHTTPMiddleware):
    # Las escrituras en la base (métrica y error) son síncronas: se ejecutan en el pool de hilos para no
    # bloquear el bucle de eventos. Si esperaran una conexión dentro del bucle con el pool agotado, las
    # solicitudes que ocupan las conexiones no podrían terminar (interbloqueo bajo carga concurrente).
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
            await run_in_threadpool(
                record_error,
                request.method,
                path,
                500,
                request_id,
                exc,
                getattr(request.state, "user_id", None),
            )
            response = JSONResponse(
                status_code=500,
                content={"detail": GENERIC_ERROR.format(request_id=request_id), "request_id": request_id},
            )
        else:
            if response.status_code >= 500:
                await run_in_threadpool(
                    record_error,
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
            await run_in_threadpool(_store_metric, request.method, path, response.status_code, elapsed_ms)
        return response


BUSY_MESSAGE = "El servicio está ocupado. Intente nuevamente en unos segundos."


class ConcurrencyLimitMiddleware:
    """Limita las solicitudes que se atienden a la vez y deja a las demás en cola dentro del bucle de eventos.

    Sin este límite, bajo carga una solicitud ya autenticada retiene su conexión de la base mientras espera un
    hilo para el endpoint, y los hilos quedan ocupados esperando conexiones: solo el tiempo de espera del pool
    (30 s) deshace el ciclo y la API deja de responder (también /health). Con el límite por debajo del pool,
    toda solicitud admitida obtiene conexión e hilo sin esperar. /health y OPTIONS no pasan por el límite.
    """

    def __init__(self, app, limit: int, queue_timeout: float):
        self.app = app
        self.queue_timeout = queue_timeout
        self._slots = asyncio.Semaphore(max(1, limit))

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http" or scope["method"] == "OPTIONS" or scope["path"].endswith("/health"):
            await self.app(scope, receive, send)
            return
        try:
            await asyncio.wait_for(self._slots.acquire(), timeout=self.queue_timeout)
        except TimeoutError:
            logger.warning("Servicio ocupado: %s %s esperó %.0f s en cola", scope["method"], scope["path"][:200],
                           self.queue_timeout)
            body = json.dumps({"detail": BUSY_MESSAGE}, ensure_ascii=False).encode()
            await send({"type": "http.response.start", "status": 503, "headers": [
                (b"content-type", b"application/json"), (b"retry-after", b"5"), (b"cache-control", b"no-store")]})
            await send({"type": "http.response.body", "body": body})
            return
        try:
            await self.app(scope, receive, send)
        finally:
            self._slots.release()
