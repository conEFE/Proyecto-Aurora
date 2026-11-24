"""El middleware escribe métricas y errores con un pool de conexiones propio.

Regresión de la prueba de carga del 24-11-2026: con el mismo pool que los endpoints, 50 usuarios concurrentes
agotaban las conexiones y la API quedaba bloqueada (cada solicitud retenía una conexión y esperaba otra).
"""

from app import deps
from app.db.models.review import RequestMetric


def test_auxiliary_pool_is_separate_and_small():
    assert deps.aux_engine is not deps.engine
    assert deps.aux_engine.pool.timeout() <= 5


def test_metric_is_written_with_auxiliary_session(client, db, monkeypatch):
    used = []
    real = deps.AuxSessionLocal

    def spy():
        used.append(True)
        return real()

    monkeypatch.setattr(deps, "AuxSessionLocal", spy)
    client.get("/auth/me")  # sin token: 401, igual se registra la métrica
    assert used
    assert db.query(RequestMetric).filter(RequestMetric.path == "/auth/me").count() == 1
