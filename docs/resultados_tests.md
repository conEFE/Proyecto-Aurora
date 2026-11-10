# Resultados de pruebas — Proyecto Aurora 2.3.0

Ejecución: 09-11-2026, Linux, Python 3.13, PostgreSQL 16 local vía `TEST_DB_DSN` (con Python 3.13 no existe
`pgserver`; ver README), BD aislada por corrida.
El esquema se crea con `alembic upgrade head` (no `create_all`).

```bash
cd backend
pytest --cov=app
```

## Resumen

| Indicador | Resultado | Meta |
|---|---|---|
| Tests ejecutados | **241** | — |
| Aprobados | **241 (100%)** | 100% |
| Fallidos | 0 | 0 |
| Cobertura total de `app/` | **97%** (2.460 sentencias, 85 sin cubrir) | — |
| Cobertura de `app/services/` | **≈95%** (1.090 sentencias, 54 sin cubrir) | ≥ 70% |
| Duración | ≈ 40 s | — |
| `ruff check` | sin hallazgos | 0 |
| `npm run lint` / `npm run typecheck` | 0 errores / 0 errores | 0 |
| `pip-audit` / `npm audit --omit=dev` | 0 / 0 vulnerabilidades | 0 |

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
| `test_validation.py` | 15 | 2.1.0: validación médica de la IA por imagen, evaluación del triage, cierre bloqueado sin validación, métricas de concordancia |
| `test_reviews_reports.py` | 22 | S6: toma y revisión, cierre solo con revisión, reporte registrado y auditado (EXPORT), métricas con datos controlados, endpoints viejos eliminados y **E2E completo** |
| `test_signature_model_performance.py` | 13 | 2.2.0: firma del médico sobre el reporte y desempeño del modelo por versión (K5) |
| `test_account_security.py` | 35 | 2.3.0 (E6): política de contraseñas, cambio de contraseña y revocación de tokens, cambio obligatorio, bloqueo y desbloqueo, límite por IP (sin confiar en `X-Forwarded-For`), `error_log` sin datos sensibles, vista de errores, K9, encabezados de seguridad, todas las rutas exigen token, `SECRET_KEY` corta, `alg: none` |

## Cobertura por módulo

```
Name                                Stmts   Miss  Cover
-------------------------------------------------------
app/api/rutas_admin.py                 60      4    93%
app/api/rutas_auth.py                  41      0   100%
app/api/rutas_cases.py                 28      0   100%
app/api/rutas_dashboard.py             17      0   100%
app/api/rutas_images.py                30      0   100%
app/api/rutas_patients.py              22      0   100%
app/api/rutas_reports.py               40      0   100%
app/api/rutas_triage.py                48      0   100%
app/auth/bearer.py                     29      0   100%
app/auth/rbac.py                       11      0   100%
app/auth/security.py                   31      3    90%
app/config.py                          35      1    97%
app/deps.py                            11      0   100%
app/inference/providers.py             48      8    83%
app/main.py                            30      0   100%
app/middleware.py                      52      2    96%
app/schemas/*                          442      4    99%
app/services/audit_service.py          22      3    86%
app/services/auth_service.py           85      0   100%
app/services/case_service.py           88      3    97%
app/services/dashboard_service.py     129      5    96%
app/services/error_log_service.py      54      5    91%
app/services/errors.py                 13      0   100%
app/services/image_service.py         115     10    91%
app/services/password_policy.py        26      1    96%
app/services/patient_service.py        57      7    88%
app/services/review_service.py        180      5    97%
app/services/seed_service.py            4      0   100%
app/services/triage_engine.py          79      2    97%
app/services/triage_service.py        167      5    97%
app/services/user_service.py           71      8    89%
app/storage/base.py                     8      0   100%
app/storage/local.py                   42      4    90%
app/utils/quality.py                   27      0   100%
app/utils/rate_limit.py                35      5    86%
app/utils/rut.py                       29      0   100%
-------------------------------------------------------
TOTAL                                2460     85    97%
```

Lo no cubierto es principalmente `HttpYoloProvider` (stub del Sprint 8, sin servicio YOLO disponible) y ramas de
error poco probables (fallas de disco o de red).

## Prueba manual en el navegador

Con la BD de desarrollo cargada con `scripts/seed_dev.py` se recorrió como MEDICO: login → cola de triage
(orden correcto por nivel, puntaje y antigüedad) → detalle del caso (desglose, regla R_BIRADS, badge IA SIMULADA,
imagen y detección) → tomar caso → revisión → construcción del PDF (2 páginas, con «IA SIMULADA», metadatos
DICOM incrustados y **sin RUT ni nombre de la paciente**) → dashboard. Sin errores en la consola.

### 2.3.0 (E6), con Playwright

- Primer ingreso del ADMIN creado con `init_user.py`: se exige cambiar la contraseña antes de entrar al panel.
- El ADMIN crea un médico con una contraseña temporal; 5 intentos fallidos lo bloquean. El panel muestra
  «Bloqueado · desbloquear» y «Cambio de contraseña pendiente», y el login informa del bloqueo con los minutos
  restantes. El ADMIN lo desbloquea y el médico entra a la pantalla de cambio obligatorio.
- Pestaña «Errores» del panel y tarjeta «Errores del servidor (5xx)» del dashboard.
- Con jsPDF 4.2.1 y jspdf-autotable 5.0.9, el reporte de un caso del seed se genera bien (PDF de 2 páginas con
  tablas, sin errores en la consola).
- Migración `c9a3e1d8f709`: `upgrade` → `downgrade -1` → `upgrade` sobre la BD de desarrollo, además de
  `test_migrations.py` (`downgrade base` → `upgrade head`).
