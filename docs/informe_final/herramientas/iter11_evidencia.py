# -*- coding: utf-8 -*-
"""Genera el README de evidencias/rendimiento_2026-11-24 a partir de los JSON de load_test.py.
Uso: python3 iter11_evidencia.py <dir_evidencia>"""
import glob, json, os, sys

d = sys.argv[1]
num = lambda v: ("%.1f" % v).replace(".", ",")
miles = lambda v: f"{v:,}".replace(",", ".")
res = {}
for f in glob.glob(os.path.join(d, "carga_*.json")):
    if "antes" not in f:
        r = json.load(open(f, encoding="utf-8")); res[r["usuarios_virtuales"]] = (os.path.basename(f), r)
antes = json.load(open(os.path.join(d, "carga_50_usuarios_antes_correccion.json"), encoding="utf-8"))

L = ["# Prueba de rendimiento en entorno local — 24-11-2026", "",
     "**Alcance:** entorno local de desarrollo, con datos ficticios. **No** corresponde al entorno de demostración en AWS",
     "(`t4g.micro`, 2 vCPU arm64, 1 GB de RAM + 2 GB de swap, base en RDS `db.t4g.micro`), cuyo rendimiento no se midió.", "",
     "## Entorno",
     "- Contenedor Linux de 4 vCPU (Intel Xeon 2,30 GHz) y 15 GB de RAM.",
     "- PostgreSQL 16.15 local; API FastAPI con `uvicorn --workers 2` (mismo número de procesos que la imagen de producción).",
     "- `INFERENCE_PROVIDER=simulated`; datos de `scripts.seed_dev` + `scripts.seed_demo --patients 120 --weeks 10`",
     "  (130 pacientes y 147 casos ficticios).", "",
     "## Procedimiento",
     "`python -m scripts.load_test --users N --seconds T --login-samples 3 --out carga_N_usuarios.json` como usuario MEDICO.",
     "Cada usuario virtual recorre sin pausa: lista de casos, cola de triage, lista de pacientes, detalle de un caso al azar,",
     "notificaciones y métricas del dashboard. El inicio de sesión se mide aparte (en serie). Entre corridas, 65 s de pausa.", "",
     "## Defecto detectado y corregido",
     "La primera corrida con 50 usuarios (`carga_50_usuarios_antes_correccion.json`) terminó con **%s errores de %s solicitudes**"
     % (miles(antes["total"]["errors"]), miles(antes["total"]["requests"])),
     "(tiempo agotado de 30 s): la API quedó bloqueada porque el middleware de métricas pedía una segunda conexión al mismo",
     "pool que retenía el endpoint (`QueuePool limit of size 5 overflow 10 reached`). Corrección: pool auxiliar en",
     "`app/deps.py`, escrituras del middleware y carga de imágenes fuera del bucle de eventos, prueba",
     "`test_middleware_pool.py` (suite de 316 pruebas, 0 fallos). Las corridas siguientes son con el código corregido.", "",
     "## Resultados (código corregido)",
     "| Usuarios | Duración | Solicitudes | Errores | Solicitudes/s | p50 (ms) | p95 (ms) | Máx. (ms) | Archivo |",
     "|---|---|---|---|---|---|---|---|---|"]
for u in sorted(res):
    f, r = res[u]; t = r["total"]
    L.append("| %d | %d s | %s | %d | %s | %s | %s | %s | `%s` |" % (u, round(r["duracion_s"]), miles(t["requests"]), t["errors"],
             num(t["req_por_s"]), num(t["p50_ms"]), num(t["p95_ms"]), num(t["max_ms"]), f))
r100 = res[max(res)][1]
L += ["", "PC-01 (100 usuarios, 15 minutos): p95 de %s ms con %d errores; meta p95 ≤ 3 s." % (num(r100["total"]["p95_ms"]), r100["total"]["errors"]),
      "Inicio de sesión (bcrypt): mediana ≈ %s ms. Detalle por endpoint en cada JSON." % num(r100["login"]["p50_ms"]), "",
      "## Limitaciones",
      "- Usuarios virtuales sin tiempo de espera entre acciones: carga más intensa que el uso clínico real.",
      "- No incluye carga de imágenes ni inferencia (la inferencia real depende del PC con GPU vía Tailscale).",
      "- El servidor y el generador de carga comparten máquina. PC-02 (estrés) no se ejecutó.", ""]
open(os.path.join(d, "README.md"), "w", encoding="utf-8").write("\n".join(L))
print("ok", sorted(res))
