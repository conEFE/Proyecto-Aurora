# Prueba de rendimiento en el entorno de demostración (AWS) — 24-11-2026

**Resultado:** PC-01 (100 usuarios virtuales, 15 min) ejecutada en AWS con la versión 2.10.2: **0 errores y sin
bloqueo, pero p95 de 14.979 ms: no cumple la meta de 3 s.** En este entorno la meta se cumple hasta 25 usuarios
virtuales. La prueba también encontró un defecto bajo carga en la 2.10.1, corregido y desplegado como 2.10.2.

## Entorno
- Servidor: EC2 `t4g.micro` (2 vCPU arm64, 1 GB de RAM + 2 GB de swap), API con **un proceso** de uvicorn
  (`WEB_CONCURRENCY=1`, por la memoria disponible), Caddy con TLS delante. Base: RDS `db.t4g.micro` (PostgreSQL 16).
  Créditos de CPU de EC2 y RDS al máximo (288) al empezar.
- **Datos:** copia de la base real en un esquema aparte (`carga`) de la misma RDS (316 casos, 275 pacientes ficticios).
  El backend apuntó a esa copia durante cada serie; la bitácora y los datos reales no recibieron tráfico. La copia se
  borró al terminar y se verificó la vuelta a la base real (316 casos, `/health` 200).
  Ventanas: 02:37–03:00 UTC (2.10.1) y 03:30–03:59 UTC (2.10.2).
- Usuario: médico de prueba (ficticio), con una clave válida solo en la copia.
- Procedimiento: `python -m scripts.load_test --base-url https://demo.auroracare.cl/api --users N --seconds T
  --login-samples 3`, igual que la prueba local; 65 s de pausa entre corridas.

## Resultados con la 2.10.2 (generador en el mismo servidor)
El generador corrió en un contenedor del propio servidor (imagen de la 2.10.2), contra la dirección pública (Caddy y
TLS incluidos), sin la red externa. Usó entre 0,2 % y 40 % de CPU (mayormente bajo 7 %); el backend, ≈ 100 % (un núcleo).

| Usuarios | Duración | Solicitudes | Errores | Solicitudes/s | p50 (ms) | p95 (ms) | Máx. (ms) | Archivo |
|---|---|---|---|---|---|---|---|---|
| 10 | 60 s | 1.251 | 0 | 20,7 | 451,4 | 922,6 | 1337,9 | `servidor_2.10.2_10_usuarios.json` |
| 25 | 61 s | 1.259 | 0 | 20,7 | 1123,3 | 2308,2 | 3115,0 | `servidor_2.10.2_25_usuarios.json` |
| 50 | 64 s | 1.233 | 0 | 19,4 | 2124,8 | 6132,4 | 7408,9 | `servidor_2.10.2_50_usuarios.json` |
| 100 | 912 s | 15.013 | 0 | 16,5 | 4454,6 | 14978,7 | 18489,0 | `servidor_2.10.2_100_usuarios.json` |

- **PC-01 no se aprueba** (p95 de 14,98 s > 3 s). La capacidad del entorno es ≈ 20 solicitudes/s; con más usuarios
  la latencia crece en proporción (cola), sin errores. Ningún usuario esperó los 20 s del límite de cola (máximo 18,5 s),
  así que no hubo respuestas 503.
- Durante los 15 minutos, `/health` respondió siempre 200 (0,04–0,32 s) y la memoria libre se mantuvo sobre 300 MB
  (`servidor_2.10.2_pc01_recursos.txt`).
- Endpoints más lentos con 100 usuarios: `/cases` (p95 16.157 ms) y `/dashboard/metrics` (p95 16.508 ms). El
  rendimiento bajó de 20,7 a 16,5 solicitudes/s a lo largo de la serie; una explicación posible, no verificada, es que
  `/dashboard/metrics` calcula sobre `request_metrics`, que crece con cada solicitud de la prueba.
- Inicio de sesión (bcrypt): mediana ≈ 292 ms.

## Primera serie con la 2.10.1 (generador externo)
Generador en un contenedor de desarrollo en Google Cloud (Iowa, EE. UU.), por Internet y a través de un proxy de salida.

| Usuarios | Solicitudes | Errores | Solicitudes/s | p50 (ms) | p95 (ms) | Máx. (ms) | Archivo |
|---|---|---|---|---|---|---|---|
| 10 | 1.315 | 0 | 21,8 | 429,1 | 897,8 | 1371,0 | `externo_2.10.1_10_usuarios.json` |
| 25 | 1.272 | 0 | 20,9 | 1144,1 | 2102,9 | 3152,8 | `externo_2.10.1_25_usuarios.json` |
| 50 | 1.273 | 0 | 20,3 | 2269,6 | 4519,7 | 7653,3 | `externo_2.10.1_50_usuarios.json` |

Las cifras con 10 y 25 usuarios coinciden con las de la 2.10.2 desde el servidor: el límite es la CPU del servidor, no
la red ni el generador.

## Defecto encontrado en la 2.10.1 y corregido en la 2.10.2
Con 100 usuarios el proxy del generador externo retuvo y cortó conexiones. La API dejó de responder, incluido `/health`
(contenedor *unhealthy*, CPU en reposo), y siguió así después de la carga: 15 conexiones «idle in transaction» y los
40 hilos esperando conexión (`QueuePool limit of size 5 overflow 10 reached`). Causa: con más solicitudes simultáneas
que conexiones, una solicitud autenticada retiene su conexión mientras espera un hilo para el endpoint, y los hilos
esperan conexiones; solo el tiempo de espera del pool (30 s) deshace el ciclo. Reproducido en local con
`reproduccion_bloqueo.py` (la API tardó ≈ 3,5 min en recuperarse).

Corrección (`1ec7904`, 2.10.2, desplegada el 24-11-2026 a las 03:29 UTC): `ConcurrencyLimitMiddleware` admite 10
solicitudes a la vez por proceso y deja las demás en cola (503 después de 20 s); `/health` es asíncrono y no pasa por
el límite. Con la corrección, la reproducción responde de inmediato. Medición local con un proceso (60 s):

| Usuarios | Solicitudes | Errores | p50 (ms) | p95 (ms) | Máx. (ms) | Archivo |
|---|---|---|---|---|---|---|
| 50 | 3.278 | 0 | 1005,4 | 1459,1 | 1790,2 | `local_2.10.2_1proceso_50_usuarios.json` |
| 100 | 3.158 | 0 | 2142,7 | 3101,0 | 3386,9 | `local_2.10.2_1proceso_100_usuarios.json` |

## Limitaciones
- Usuarios virtuales sin pausa entre acciones: carga más intensa que el uso clínico real; el resultado no equivale a
  un número de usuarios clínicos soportados.
- Sin carga de imágenes ni inferencia. PC-02 (estrés) no se ejecutó.
- En la serie de la 2.10.2 el generador compartió la máquina con el servidor (uso de CPU bajo, ver arriba).
