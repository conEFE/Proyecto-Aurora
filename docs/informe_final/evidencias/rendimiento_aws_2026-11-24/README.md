# Prueba de rendimiento en el entorno de demostración (AWS) — 24-11-2026

**Estado: incompleta.** Se midió la versión 2.10.1 con 10, 25 y 50 usuarios. PC-01 (100 usuarios, 15 min) no llegó a
medirse: la prueba encontró un segundo defecto bajo carga, corregido en la **2.10.2**, que **no está desplegada**.

## Entorno
- Servidor: EC2 `t4g.micro` (2 vCPU arm64, 1 GB de RAM + 2 GB de swap), API 2.10.1 con **un proceso**
  (`WEB_CONCURRENCY=1`), Caddy con TLS delante. Base: RDS `db.t4g.micro` (PostgreSQL 16).
- **Datos:** copia de la base real en un esquema aparte (`carga`) de la misma RDS. El backend apuntó a esa copia
  durante la prueba (02:37–03:00 UTC, aprox.), así que la bitácora y los datos reales no recibieron tráfico. La copia se
  borró al terminar y se verificó la vuelta a la base real (316 casos, `/health` 200).
- Usuario: médico de prueba (ficticio), con una clave válida solo en la copia.
- **Generador:** contenedor de desarrollo en Google Cloud (Iowa, EE. UU.), por Internet hasta us-east-2 y a través de
  un proxy de salida. Las cifras incluyen esa red (≈ 200 ms por solicitud con conexión TLS nueva; la prueba reutiliza
  conexiones). Créditos de CPU de EC2 y RDS al máximo (288) al empezar.

## Resultados (2.10.1, 60 s por corrida)
| Usuarios | Solicitudes | Errores | Solicitudes/s | p50 (ms) | p95 (ms) | Máx. (ms) | Archivo |
|---|---|---|---|---|---|---|---|
| 10 | 1.315 | 0 | 21,8 | 429,1 | 897,8 | 1371,0 | `carga_10_usuarios.json` |
| 25 | 1.272 | 0 | 20,9 | 1144,1 | 2102,9 | 3152,8 | `carga_25_usuarios.json` |
| 50 | 1.273 | 0 | 20,3 | 2269,6 | 4519,7 | 7653,3 | `carga_50_usuarios.json` |

La meta p95 ≤ 3 s se cumple hasta 25 usuarios virtuales y no con 50. La capacidad es ≈ 21 solicitudes/s, constante
desde 10 usuarios: el proceso único satura un núcleo (CPU de EC2 con máximo de 50 % en los dos núcleos; RDS ≤ 21 %).
Inicio de sesión (bcrypt): mediana ≈ 314 ms.

## Defecto encontrado (corregido en 2.10.2, no desplegado)
Con 100 usuarios el proxy del generador retuvo y cortó conexiones. La API dejó de responder, incluido `/health`
(contenedor *unhealthy*, CPU en reposo), y siguió así después de que terminó la carga: 15 conexiones de la base
«idle in transaction» y los 40 hilos esperando conexión (`QueuePool limit of size 5 overflow 10 reached`).
Causa: con más solicitudes simultáneas que conexiones, una solicitud autenticada retiene su conexión mientras espera un
hilo para el endpoint, y los hilos esperan conexiones; solo el tiempo de espera del pool (30 s) deshace el ciclo.
Reproducido en local con `reproduccion_bloqueo.py` (3 rondas de 100 clientes que abandonan sus solicitudes): la API se
recuperó solo después de ≈ 3,5 min.

Corrección (`1ec7904`, versión 2.10.2): `ConcurrencyLimitMiddleware` admite 10 solicitudes a la vez por proceso y deja
las demás en cola (503 después de 20 s); `/health` es asíncrono y queda fuera del límite. Con la corrección, la misma
reproducción responde de inmediato (≈ 40 ms) y sin errores de pool. Medición local con **un proceso** (60 s):

| Usuarios | Solicitudes | Errores | p50 (ms) | p95 (ms) | Máx. (ms) | Archivo |
|---|---|---|---|---|---|---|
| 50 | 3.278 | 0 | 1005,4 | 1459,1 | 1790,2 | `local_2.10.2_1proceso_50_usuarios.json` |
| 100 | 3.158 | 0 | 2142,7 | 3101,0 | 3386,9 | `local_2.10.2_1proceso_100_usuarios.json` |

## Pendiente
Desplegar la 2.10.2 y ejecutar PC-01 en AWS con el generador **dentro de AWS** (sin el proxy), con la misma copia
temporal de la base.
