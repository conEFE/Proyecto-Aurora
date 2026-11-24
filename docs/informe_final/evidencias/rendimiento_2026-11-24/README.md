# Prueba de rendimiento en entorno local — 24-11-2026

**Alcance:** entorno local de desarrollo, con datos ficticios. **No** corresponde al entorno de demostración en AWS
(`t4g.micro`, 2 vCPU arm64, 1 GB de RAM + 2 GB de swap, base en RDS `db.t4g.micro`), cuyo rendimiento no se midió.

## Entorno
- Contenedor Linux de 4 vCPU (Intel Xeon 2,30 GHz) y 15 GB de RAM.
- PostgreSQL 16.15 local; API FastAPI con `uvicorn --workers 2` (mismo número de procesos que la imagen de producción).
- Código del repositorio en el commit `43c698f` más `backend/scripts/load_test.py`; `INFERENCE_PROVIDER=simulated`.
- Datos: `scripts.seed_dev` (3 usuarios, 10 pacientes) + `scripts.seed_demo --patients 120 --weeks 10`
  (120 pacientes ficticios, 137 casos). Total: 130 pacientes y 147 casos.

## Procedimiento
`python -m scripts.load_test --users N --seconds 60 --login-samples 3 --out carga_N_usuarios.json`, con N = 10 y 25,
como usuario MEDICO. Cada usuario virtual recorre sin pausa: lista de casos, cola de triage, lista de pacientes,
detalle de un caso al azar, notificaciones y métricas del dashboard. El inicio de sesión se mide aparte (en serie).

## Resultados
| Usuarios | Solicitudes | Errores | Solicitudes/s | p50 (ms) | p95 (ms) | Máx. (ms) |
|---|---|---|---|---|---|---|
| 10 | 5.635 | 0 | 93,9 | 85,9 | 263,7 | 406,2 |
| 25 | 5.059 | 0 | 83,9 | 295,5 | 537,8 | 775,7 |

Inicio de sesión (bcrypt): mediana ≈ 240 ms. Detalle por endpoint en los JSON.
El endpoint más lento es la lista de casos (p95 593,6 ms con 25 usuarios). Todos quedan bajo la meta de p95 ≤ 3 s.

## Limitaciones
- Usuarios virtuales sin tiempo de espera entre acciones: es una carga más intensa que el uso clínico real.
- No incluye carga de imágenes ni inferencia (la inferencia real depende del PC con GPU vía Tailscale).
- El servidor y el generador de carga comparten máquina.
