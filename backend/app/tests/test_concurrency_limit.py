"""Límite de solicitudes simultáneas (ConcurrencyLimitMiddleware).

Regresión de la prueba de carga en AWS del 24-11-2026: con 100 usuarios y un proceso, las solicitudes
autenticadas retenían su conexión esperando un hilo mientras los hilos esperaban conexiones, y la API
(incluido /health) dejaba de responder hasta que se vaciaba la cola.
"""

import asyncio

import httpx
import pytest
from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route

from app import deps
from app.config import settings
from app.middleware import BUSY_MESSAGE, ConcurrencyLimitMiddleware


@pytest.fixture
def anyio_backend():
    return "asyncio"


async def _slow(request):
    await asyncio.sleep(0.4)
    return JSONResponse({"ok": True})


async def _boom(request):
    raise RuntimeError("falla")


async def _health(request):
    return JSONResponse({"status": "ok"})


def _app(limit=1, timeout=0.1):
    inner = Starlette(routes=[Route("/slow", _slow), Route("/boom", _boom), Route("/health", _health)])
    return ConcurrencyLimitMiddleware(inner, limit=limit, queue_timeout=timeout)


def _client(app):
    transport = httpx.ASGITransport(app=app, raise_app_exceptions=False)
    return httpx.AsyncClient(transport=transport, base_url="http://test")


@pytest.mark.anyio
async def test_excess_requests_wait_and_then_get_503():
    async with _client(_app(limit=1, timeout=0.1)) as c:
        first, second = await asyncio.gather(c.get("/slow"), c.get("/slow"))
    codes = sorted([first.status_code, second.status_code])
    assert codes == [200, 503]
    busy = first if first.status_code == 503 else second
    assert busy.json()["detail"] == BUSY_MESSAGE
    assert busy.headers["retry-after"] == "5"


@pytest.mark.anyio
async def test_queued_request_is_served_when_a_slot_frees():
    async with _client(_app(limit=1, timeout=2)) as c:
        first, second = await asyncio.gather(c.get("/slow"), c.get("/slow"))
    assert first.status_code == second.status_code == 200


@pytest.mark.anyio
async def test_health_bypasses_the_limit():
    async with _client(_app(limit=1, timeout=0.05)) as c:
        slow = asyncio.create_task(c.get("/slow"))
        await asyncio.sleep(0.05)
        health = await c.get("/health")
        assert health.status_code == 200
        assert (await slow).status_code == 200


@pytest.mark.anyio
async def test_slot_is_released_after_an_error():
    async with _client(_app(limit=1, timeout=0.1)) as c:
        assert (await c.get("/boom")).status_code == 500
        assert (await c.get("/slow")).status_code == 200


def test_limit_is_below_the_database_pool():
    pool = deps.engine.pool
    assert settings.MAX_CONCURRENT_REQUESTS < pool.size() + pool._max_overflow
