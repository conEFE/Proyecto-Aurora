# Evidencia de rendimiento — 25-11-2026 (versión 2.12.0, entorno local)

Mide el efecto de las optimizaciones de la 2.12.0 (`470479f`) frente a la 2.11.0, en el mismo entorno y con los
mismos datos. **No reemplaza a PC-01 en el entorno de demostración**: la 2.12.0 todavía no está desplegada, y la meta
de RNF03 se evalúa allá (método en `../rendimiento_aws_2026-11-24/README.md`).

## Condiciones

- Contenedor Linux de 4 vCPU, Python 3.13, PostgreSQL 16 local. **La API corre en un solo proceso de uvicorn fijado a
  un núcleo** (`taskset -c 0`) y el generador de carga en los otros tres, para acercarse a la capacidad de la
  `t4g.micro`. Por eso estos números **no se comparan** con los de `../rendimiento_2026-11-24/` (sin fijar núcleos).
- Datos ficticios: `scripts.seed_demo --patients 250 --weeks 10 --reviewers 3` (250 pacientes, 283 casos) y 60.000 filas
  sintéticas en `request_metrics` (se vuelven a cargar antes de cada corrida, para que todas partan igual).
- Script: `backend/scripts/load_test.py` (el mismo de PC-01), 60 s por corrida, usuario MEDICO. Comando en `carga_local.sh`.
- La corrida de la 2.11.0 se hizo sobre el mismo árbol, con los archivos de la aplicación de la 2.11.0 restaurados.

## Resultados

| Versión | Usuarios | Solicitudes | Solicitudes/s | p50 (ms) | p95 (ms) | Máx. (ms) | Errores | Archivo |
|---|---|---|---|---|---|---|---|---|
| 2.11.0 | 50 | 1.502 | 23,4 | 1.074,5 | 7.050,1 | 9.049,9 | 0 | `local_2.11.0_50_usuarios.json` |
| 2.12.0 | 50 | 5.724 | 94,6 | 389,6 | 1.142,3 | 1.754,7 | 0 | `local_2.12.0_50_usuarios.json` |
| 2.12.0 | 100 | 6.069 | 99,0 | 694,8 | 2.531,7 | 3.057,5 | 0 | `local_2.12.0_100_usuarios.json` |

Consultas SQL por solicitud y tiempo de una solicitud aislada (`consultas_por_endpoint.py`, 20 repeticiones, sin
concurrencia; detalle en `consultas_por_endpoint.txt`):

| Endpoint | Consultas 2.11.0 | Consultas 2.12.0 | Mediana 2.11.0 (ms) | Mediana 2.12.0 (ms) |
|---|---|---|---|---|
| `GET /cases` | 63 | 6 | 40,6 | 13,9 |
| `GET /patients/page` | 54 | 6 | 41,6 | 13,3 |
| `GET /triage/queue` | 34 | 3 | 36,2 | 12,2 |
| `GET /dashboard/metrics` | 8 | 8 | 212,9 | 50,8 |

## Lectura

- La capacidad del proceso subió unas cuatro veces (de 23 a 95 solicitudes/s) y, en este entorno, el p95 con 100
  usuarios queda bajo 3 s (2,53 s), sin errores.
- La 2.11.0 en este entorno (23,4 solicitudes/s) se comporta parecido a la 2.10.2 en el entorno de demostración
  (≈ 20 solicitudes/s), lo que sugiere que la mejora podría trasladarse, pero **solo la repetición de PC-01 en AWS lo
  confirma**.
- `/dashboard/metrics` sigue siendo el endpoint más pesado: su costo crece con `request_metrics` (≈ 20 ms en la base
  con 60.000 filas). Una política de retención de esa tabla lo acotaría.
