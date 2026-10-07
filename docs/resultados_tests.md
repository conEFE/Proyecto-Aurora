# Resultados de pruebas — Proyecto Aurora (cierre Sprint 6)

Ejecución: 07-10-2026, Windows 10, Python 3.11.9, PostgreSQL 16.2 embebido (`pgserver`), BD aislada por corrida.
El esquema se crea con `alembic upgrade head` (no `create_all`).

```bash
cd backend
pytest --cov=app
```

## Resumen

| Indicador | Resultado | Meta |
|---|---|---|
| Tests ejecutados | **178** | — |
| Aprobados | **178 (100%)** | 100% |
| Fallidos | 0 | 0 |
| Cobertura total de `app/` | **96%** (1.866 sentencias, 76 sin cubrir) | — |
| Cobertura de `app/services/` | **≈94%** (856 sentencias, 52 sin cubrir) | ≥ 70% |
| Duración | ≈ 43 s | — |
| `ruff check` | sin hallazgos | 0 |
| `npm run lint` / `npm run typecheck` | 0 errores / 0 errores | 0 |

## Tests por archivo

| Archivo | Tests | Qué cubre |
|---|---:|---|
| `test_auth.py` | 11 | S1: login correcto/incorrecto, token expirado, manipulado, firmado con otra clave, `Bearer 1-ADMIN`, rol leído desde la BD, header de tiempos |
| `test_migrations.py` | 2 | `downgrade base` → `upgrade head`; migración de filas de la v1.0 (caso sin paciente, código libre, paciente sin nombre) |
| `test_users_patients.py` | 32 | S2: RUT (módulo 11), CRUD de usuarios solo ADMIN, desactivación, ADMIN sin acceso a pacientes, consentimiento obligatorio, auditoría y `audit_log` append-only |
| `test_cases.py` | 25 | S3: 4 transiciones válidas y 8 inválidas (409), caso sin consentimiento (409), BI-RADS fuera de rango, caso cerrado no editable, filtros, auditoría |
| `test_images.py` | 17 | S4: carga PNG/JPEG, límite de tamaño (413), formatos (415), cifrado en disco, ADMINISTRATIVO sube pero no ve (403), inferencia simulada marcada |
| `test_triage_engine.py` | 46 | S5 unitarios de `compute_triage`: cada regla, cada banda de edad, límites 59,99/60/29,99/30, factores y validación de parámetros |
| `test_triage_api.py` | 23 | S5: triage al crear, recálculo e historial, override con motivo, orden de la cola, vista mínima, versiones de configuración, notificaciones |
| `test_reviews_reports.py` | 22 | S6: toma y revisión, cierre solo con revisión, reporte registrado y auditado (EXPORT), métricas con datos controlados, endpoints viejos eliminados y **E2E completo** |

## Cobertura por módulo

```
Name                                Stmts   Miss  Cover
-------------------------------------------------------
app\api\rutas_admin.py                 49      4    92%
app\api\rutas_auth.py                  33      0   100%
app\api\rutas_cases.py                 28      0   100%
app\api\rutas_dashboard.py             13      0   100%
app\api\rutas_images.py                30      0   100%
app\api\rutas_patients.py              22      1    95%
app\api\rutas_reports.py               31      0   100%
app\api\rutas_triage.py                48      0   100%
app\auth\bearer.py                     20      0   100%
app\auth\rbac.py                       11      0   100%
app\auth\security.py                   29      3    90%
app\config.py                          27      1    96%
app\inference\providers.py             48      8    83%
app\middleware.py                      30      2    93%
app\schemas\*                         344      4    99%
app\services\audit_service.py          21      3    86%
app\services\auth_service.py           22      0   100%
app\services\case_service.py           88      3    97%
app\services\dashboard_service.py      68      2    97%
app\services\image_service.py         109     10    91%
app\services\patient_service.py        57     13    77%
app\services\review_service.py         72      3    96%
app\services\triage_engine.py          79      2    97%
app\services\triage_service.py        167      5    97%
app\services\user_service.py           52      8    85%
app\storage\local.py                   42      4    90%
app\utils\quality.py                   27      0   100%
app\utils\rut.py                       29      0   100%
-------------------------------------------------------
TOTAL                                1866     76    96%
```

Lo no cubierto es principalmente `HttpYoloProvider` (stub del Sprint 8, sin servicio YOLO disponible) y ramas de
error poco probables (fallas de disco o de red).

## Prueba manual en el navegador

Con la BD de desarrollo cargada con `scripts/seed_dev.py` se recorrió como MEDICO: login → cola de triage
(orden correcto por nivel, puntaje y antigüedad) → detalle del caso (desglose, regla R_BIRADS, badge IA SIMULADA,
imagen y detección) → tomar caso → revisión → construcción del PDF (2 páginas, con «IA SIMULADA», metadatos
DICOM incrustados y **sin RUT ni nombre de la paciente**) → dashboard. Sin errores en la consola.
