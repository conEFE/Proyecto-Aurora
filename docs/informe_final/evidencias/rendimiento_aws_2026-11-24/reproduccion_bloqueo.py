"""Reproduce el bloqueo de la 2.10.1: N clientes abandonan sus solicitudes en curso y luego se mide si la API responde.
Uso: AURORA_LOAD_RUT=... AURORA_LOAD_PASSWORD=... python reproduccion_bloqueo.py <rondas> <usuarios> <segundos_antes_del_corte>
Solo en local, contra una API con un proceso (uvicorn --workers 1 --port 8010) y datos ficticios."""
import asyncio, httpx, os, sys, time
B = "http://127.0.0.1:8010"
async def main(rounds, users, cut):
    async with httpx.AsyncClient(base_url=B, timeout=30) as c:
        tok = (await c.post("/auth/login", json={"rut": os.environ["AURORA_LOAD_RUT"], "password": os.environ["AURORA_LOAD_PASSWORD"]})).json()["access_token"]
    H = {"Authorization": f"Bearer {tok}"}
    paths = ["/cases?page=1&size=20", "/triage/queue", "/patients/page?page=1&size=25", "/dashboard/metrics", "/notifications"]
    for r in range(rounds):
        c = httpx.AsyncClient(base_url=B, timeout=60, limits=httpx.Limits(max_connections=users*2))
        async def u(i):
            while True:
                await c.get(paths[i % len(paths)], headers=H)
        tasks = [asyncio.create_task(u(i)) for i in range(users)]
        await asyncio.sleep(cut)
        for t in tasks: t.cancel()          # corte abrupto: el cliente abandona las solicitudes en curso
        await asyncio.gather(*tasks, return_exceptions=True)
        await c.aclose()
    await asyncio.sleep(2)
    for k in range(3):
        t0 = time.perf_counter()
        try:
            async with httpx.AsyncClient(base_url=B, timeout=40) as c:
                r1 = await c.get("/cases?page=1&size=20", headers=H)
            print("tras cortes: /cases", r1.status_code, f"{(time.perf_counter()-t0)*1000:.0f} ms")
        except Exception as e:
            print("tras cortes: /cases FALLA", type(e).__name__, f"{(time.perf_counter()-t0)*1000:.0f} ms")
asyncio.run(main(int(sys.argv[1]), int(sys.argv[2]), float(sys.argv[3])))
