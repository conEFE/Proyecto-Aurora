"""Mide consultas SQL y tiempo por endpoint (TestClient, un hilo). Uso: python bench.py [repeticiones]"""
import statistics, sys, time
from sqlalchemy import event
from fastapi.testclient import TestClient
from app.deps import engine
from app.main import app

N = int(sys.argv[1]) if len(sys.argv) > 1 else 20
count = {"n": 0}
@event.listens_for(engine, "before_cursor_execute")
def _c(*a, **k):
    count["n"] += 1

ENDPOINTS = {
    "MEDICO": ["/cases", "/cases?page=2", "/triage/queue", "/patients/page", "/notifications", "/dashboard/metrics", "/dashboard/cases", "/cases/{id}"],
    "JEFATURA": ["/dashboard/metrics", "/dashboard/doctors/compare"],
}
with TestClient(app) as c:
    for rut, eps in [("11111111-1", ENDPOINTS["MEDICO"]), ("33333333-3", ENDPOINTS["JEFATURA"])]:
        tok = c.post("/auth/login", json={"rut": rut, "password": "Clave-Prueba-123"}).json()["access_token"]
        h = {"Authorization": f"Bearer {tok}"}
        cid = c.get("/cases", headers=h).json()["items"][0]["id"] if "/cases/{id}" in eps else None
        for ep in eps:
            url = ep.replace("{id}", str(cid))
            times, qs = [], []
            for _ in range(N):
                count["n"] = 0
                t = time.perf_counter(); r = c.get(url, headers=h); times.append((time.perf_counter()-t)*1000)
                qs.append(count["n"])
                assert r.status_code == 200, (url, r.status_code, r.text[:200])
            print(f"{rut[:2]} {url:32s} consultas={statistics.median(qs):5.0f}  mediana={statistics.median(times):7.1f} ms  p95={sorted(times)[int(0.95*N)-1]:7.1f} ms")
