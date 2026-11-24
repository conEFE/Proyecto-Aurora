"""Prueba de carga simple de la API: mide latencia (p50, p95, máximo), errores y rendimiento por endpoint.

Pensada para el entorno LOCAL o de pruebas, con datos ficticios (scripts.seed_dev y scripts.seed_demo).
No la ejecute contra producción sin acuerdo del equipo: genera tráfico y registros de auditoría (VIEW).

Cada usuario virtual inicia sesión una vez como MEDICO y luego recorre en bucle las consultas más usadas
(lista de casos, cola de triage, pacientes, detalle de caso, notificaciones y dashboard) hasta completar la
duración. El inicio de sesión se mide aparte y en serie, porque tiene límite de intentos por IP.

Uso (desde backend/, con la API levantada):
    AURORA_LOAD_RUT=10000004-0 AURORA_LOAD_PASSWORD=... \
        python -m scripts.load_test --base-url http://127.0.0.1:8000 --users 10 --seconds 60 --out resultado.json
"""

import argparse
import asyncio
import json
import os
import platform
import random
import statistics
import time
from datetime import datetime, timezone

import httpx

ENDPOINTS = [
    ("GET /cases", "/cases?page=1&size=20"),
    ("GET /triage/queue", "/triage/queue"),
    ("GET /patients/page", "/patients/page?page=1&size=25"),
    ("GET /cases/{id}", None),  # detalle de un caso al azar
    ("GET /notifications", "/notifications"),
    ("GET /dashboard/metrics", "/dashboard/metrics"),
]


def percentile(values: list[float], p: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    k = (len(ordered) - 1) * p / 100
    lo, hi = int(k), min(int(k) + 1, len(ordered) - 1)
    return ordered[lo] + (ordered[hi] - ordered[lo]) * (k - lo)


async def login(client: httpx.AsyncClient, rut: str, password: str) -> tuple[str, float]:
    t0 = time.perf_counter()
    r = await client.post("/auth/login", json={"rut": rut, "password": password})
    elapsed = (time.perf_counter() - t0) * 1000
    r.raise_for_status()
    return r.json()["access_token"], elapsed


async def virtual_user(client, token, case_ids, deadline, samples, errors):
    headers = {"Authorization": f"Bearer {token}"}
    while time.perf_counter() < deadline:
        for name, path in ENDPOINTS:
            if time.perf_counter() >= deadline:
                return
            url = path or f"/cases/{random.choice(case_ids)}"
            t0 = time.perf_counter()
            try:
                r = await client.get(url, headers=headers)
                ok = r.status_code < 400
            except httpx.HTTPError:
                ok = False
            samples.setdefault(name, []).append((time.perf_counter() - t0) * 1000)
            if not ok:
                errors[name] = errors.get(name, 0) + 1


async def run(args) -> dict:
    rut, password = os.environ["AURORA_LOAD_RUT"], os.environ["AURORA_LOAD_PASSWORD"]
    limits = httpx.Limits(max_connections=args.users * 2)
    async with httpx.AsyncClient(base_url=args.base_url, timeout=30, limits=limits) as client:
        login_ms = []
        token = None
        for _ in range(args.login_samples):
            token, ms = await login(client, rut, password)
            login_ms.append(ms)
        headers = {"Authorization": f"Bearer {token}"}
        page = (await client.get("/cases?page=1&size=100", headers=headers)).json()
        case_ids = [c["id"] for c in page["items"]]
        if not case_ids:
            raise SystemExit(
                "No hay casos: cargue datos ficticios antes (scripts.seed_dev / scripts.seed_demo)"
            )

        samples: dict[str, list[float]] = {}
        errors: dict[str, int] = {}
        start = time.perf_counter()
        deadline = start + args.seconds
        await asyncio.gather(
            *(virtual_user(client, token, case_ids, deadline, samples, errors) for _ in range(args.users))
        )
        wall = time.perf_counter() - start

    all_ms = [v for vs in samples.values() for v in vs]
    rows = {
        name: {
            "requests": len(vs),
            "errors": errors.get(name, 0),
            "p50_ms": round(percentile(vs, 50), 1),
            "p95_ms": round(percentile(vs, 95), 1),
            "max_ms": round(max(vs), 1),
            "mean_ms": round(statistics.fmean(vs), 1),
        }
        for name, vs in samples.items()
    }
    return {
        "fecha_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "base_url": args.base_url,
        "usuarios_virtuales": args.users,
        "duracion_s": round(wall, 1),
        "python": platform.python_version(),
        "plataforma": platform.platform(),
        "login": {
            "muestras": len(login_ms),
            "p50_ms": round(percentile(login_ms, 50), 1),
            "max_ms": round(max(login_ms), 1),
        },
        "total": {
            "requests": len(all_ms),
            "errors": sum(errors.values()),
            "req_por_s": round(len(all_ms) / wall, 1),
            "p50_ms": round(percentile(all_ms, 50), 1),
            "p95_ms": round(percentile(all_ms, 95), 1),
            "max_ms": round(max(all_ms), 1),
        },
        "endpoints": rows,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--base-url", default="http://127.0.0.1:8000")
    parser.add_argument("--users", type=int, default=10)
    parser.add_argument("--seconds", type=int, default=60)
    parser.add_argument("--login-samples", type=int, default=5)
    parser.add_argument("--out", default=None, help="Guarda el resultado en JSON")
    args = parser.parse_args()
    result = asyncio.run(run(args))
    text = json.dumps(result, ensure_ascii=False, indent=2)
    print(text)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as fh:
            fh.write(text + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
