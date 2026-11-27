# Prueba de rendimiento en entorno local — 24-11-2026

**Alcance:** entorno local de desarrollo, con datos ficticios. **No** corresponde al entorno de demostración en AWS
(`t4g.micro`, 2 vCPU arm64, 1 GB de RAM + 2 GB de swap, base en RDS `db.t4g.micro`), cuyo rendimiento no se midió.

## Entorno
- Contenedor Linux de 4 vCPU (Intel Xeon 2,30 GHz) y 15 GB de RAM.
- PostgreSQL 16.15 local; API FastAPI con `uvicorn --workers 2` (mismo número de procesos que la imagen de producción).
- `INFERENCE_PROVIDER=simulated`; datos de `scripts.seed_dev` + `scripts.seed_demo --patients 120 --weeks 10`
  (130 pacientes y 147 casos ficticios).

## Procedimiento
`python -m scripts.load_test --users N --seconds T --login-samples 3 --out carga_N_usuarios.json` como usuario MEDICO.
Cada usuario virtual recorre sin pausa: lista de casos, cola de triage, lista de pacientes, detalle de un caso al azar,
notificaciones y métricas del dashboard. El inicio de sesión se mide aparte (en serie). Entre corridas, 65 s de pausa.

## Defecto detectado y corregido
La primera corrida con 50 usuarios (`carga_50_usuarios_antes_correccion.json`) terminó con **500 errores de 500 solicitudes**
(tiempo agotado de 30 s): la API quedó bloqueada porque el middleware de métricas pedía una segunda conexión al mismo
pool que retenía el endpoint (`QueuePool limit of size 5 overflow 10 reached`). Corrección: pool auxiliar en
`app/deps.py`, escrituras del middleware y carga de imágenes fuera del bucle de eventos, prueba
`test_middleware_pool.py` (suite de 316 pruebas, 0 fallos). Las corridas siguientes son con el código corregido.

## Resultados (código corregido)
| Usuarios | Duración | Solicitudes | Errores | Solicitudes/s | p50 (ms) | p95 (ms) | Máx. (ms) | Archivo |
|---|---|---|---|---|---|---|---|---|
| 10 | 60 s | 4.219 | 0 | 70,1 | 123,2 | 327,5 | 752,2 | `carga_10_usuarios.json` |
| 25 | 60 s | 4.198 | 0 | 69,7 | 321,1 | 713,7 | 1067,6 | `carga_25_usuarios.json` |
| 50 | 61 s | 3.791 | 0 | 62,5 | 733,7 | 1591,8 | 3351,6 | `carga_50_usuarios.json` |
| 100 | 902 s | 42.803 | 59 | 47,5 | 1860,9 | 3974,4 | 30087,8 | `carga_100_usuarios.json` |

PC-01 (100 usuarios, 15 minutos): p95 de 3974,4 ms con 59 errores: **no cumple** la meta p95 ≤ 3 s. La meta se cumple hasta 50 usuarios.
Con 100 usuarios no hubo bloqueo (el servicio atendió los 15 minutos) sino saturación: los errores son esperas de más de 30 s por una conexión libre (`QueuePool ... timeout 30`).
Inicio de sesión (bcrypt): mediana ≈ 239,1 ms. Detalle por endpoint en cada JSON.

## Limitaciones
- Usuarios virtuales sin tiempo de espera entre acciones: carga más intensa que el uso clínico real.
- No incluye carga de imágenes ni inferencia (la inferencia real depende del PC con GPU vía Tailscale).
- El servidor y el generador de carga comparten máquina. PC-02 (estrés) no se ejecutó.
