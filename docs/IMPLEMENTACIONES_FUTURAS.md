# Implementaciones futuras — Proyecto Aurora

Trabajo pendiente en el repositorio, ordenado por épica, a partir de la revisión del informe de la Unidad 2 y de
las correcciones del 05-10-2026. Lo implementado hasta la versión 2.2.0 está en `docs/CHANGELOG_SPRINTS.md`.

Actualizado: 18-10-2026.

## Estado por épica

| Épica | Tema | Estado en el repo |
|---|---|---|
| E5 | Validación médica del informe de IA, métricas del modelo por versión y firma del reporte | Hecho (2.1.0 y 2.2.0) |
| E6 | Cuentas, seguridad y registro de errores | Pendiente |
| E7 | Versionado, CI/CD y despliegue (local → staging → piloto) | Pendiente (solo tags y `.env.example`) |
| E9 | Pruebas no funcionales (carga, estrés y seguridad) | Pendiente (unitarias, integración y E2E listas) |
| E10 | Clasificador CNN (ResNet18) y YOLO para el triage | Modelo CNN entrenado fuera del repo (AUC 0,843); integración pendiente; YOLO en desarrollo |
| — | Mejoras menores detectadas | Pendiente |

## E6 · Cuentas, seguridad y registro de errores

Responde a los comentarios C10 (cambio de contraseña) y C12 (tabla de errores) del informe.

- [ ] **Cambio de contraseña**: `POST /auth/change-password` (contraseña actual + nueva), política mínima (largo,
  no repetir la actual), evento `PASSWORD_CHANGE` en `audit_log` y pantalla en el menú de usuario.
- [ ] **Cambio obligatorio en el primer inicio de sesión**: columna `users.must_change_password`; el ADMIN la
  activa al crear o restablecer un usuario.
- [ ] **Tabla `error_log`** (migración reversible): `id`, `occurred_at`, `method`, `path` (plantilla, sin ids),
  `status_code`, `error_type`, `message` (sin datos sensibles), `user_id` nullable, `request_id`.
  Handler global de excepciones 5xx que registra en la tabla y responde un mensaje genérico con el `request_id`.
- [ ] Vista de errores para ADMIN (filtro por fecha y tipo) y conteo en el dashboard; alimenta el KPI K9.
- [ ] **Rate limiting y bloqueo de login** (p. ej. `slowapi`): N intentos fallidos por RUT/IP → bloqueo temporal,
  auditado como `LOGIN_FAIL` con motivo.
- [ ] Revisión OWASP Top 10 (A01, A02, A05, A07) y corrección de hallazgos.
- [ ] Tests: cambio de contraseña (correcta, incorrecta, política), bloqueo por intentos, registro en `error_log`
  sin datos sensibles.

## E7 · Versionado, CI/CD y despliegue

Responde a «entorno local → deploy» y a los comentarios C13 y C14 (acceso a Internet y respaldo si cae AWS).

### Versionado
- [ ] **GitHub Flow** con `main` protegida (PR + 1 revisión + CI en verde) y ramas cortas `feature/*`, `fix/*`,
  `hotfix/*`. No se usa rama `develop`.
- [ ] **SemVer 2.0.0** y **Conventional Commits** (`feat:`, `fix:`, `docs:`, `chore:`).
- [ ] **release-please** (GitHub Action): PR de release que sube la versión en `package.json` y `pyproject.toml`,
  actualiza el `CHANGELOG.md` y crea el tag y la GitHub Release. La 3.0.0 queda reservada para el cambio de
  contrato de inferencia (CNN).

### Contenedores y entornos
- [ ] `Dockerfile` para API (Uvicorn), frontend (build de Vite servido por Nginx) e inferencia.
- [ ] `docker-compose.yml` para local (con PostgreSQL) y `docker-compose.prod.yml` para staging y piloto.
- [ ] Healthchecks y política de reinicio automático.

### CI/CD (GitHub Actions)
- [ ] **CI en cada PR**: ruff, black, pytest con `--cov-fail-under=70` y PostgreSQL de servicio, prueba de
  downgrade de Alembic, ESLint, `tsc`, `npm run build`, gitleaks.
- [ ] **Build al hacer merge**: imágenes Docker etiquetadas con versión y SHA, escaneo Trivy, push a GHCR.
- [ ] **Deploy a staging** automático: OIDC hacia AWS (sin llaves fijas), SSM Run Command en EC2,
  `alembic upgrade head` y `docker compose up -d`.
- [ ] **Verificación**: prueba de humo (`/health`, login, cola) y OWASP ZAP baseline sobre staging.
- [ ] **Deploy a piloto** al crear un tag `vX.Y.Z`, con aprobación manual (GitHub Environments).
- [ ] **Rollback**: volver a desplegar el tag anterior; la BD se revierte solo si la migración lo exige.
- [ ] Dependabot para pip, npm y GitHub Actions.

### Infraestructura AWS (sa-east-1)
- [ ] `S3EncryptedStorage` (implementación de `IStorage` con SSE-KMS y versionado) en reemplazo del disco local.
- [ ] EC2 t3.large, RDS PostgreSQL db.t3.medium (50 GB gp3), S3, KMS, AWS Backup, CloudWatch; secretos en SSM
  Parameter Store. Costo estimado del piloto: US$241 al mes (detalle en el informe, sección VIII).
- [ ] Cloudflare delante del origen (DNS, TLS Full Strict, WAF); EC2 solo acepta tráfico de los rangos de Cloudflare.

### Respaldo y plan B si cae AWS
- [ ] Nivel 1: reinicio automático de contenedores y recuperación automática de EC2.
- [ ] Nivel 2: RDS con recuperación a un punto en el tiempo y S3 con versionado.
- [ ] Nivel 3: copia de respaldos a una segunda región (us-east-1) con AWS Backup.
- [ ] Nivel 4: copia **fuera de AWS** (`pg_dump` nocturno cifrado e imágenes) en Cloudflare R2; como todo corre en
  Compose, se puede levantar en otro proveedor.
- [ ] Página de mantenimiento en Cloudflare durante una caída y procedimiento manual (cola por orden de llegada).
- [ ] Simulacro mensual de restauración.

### Observabilidad
- [ ] `prometheus-fastapi-instrumentator`, Prometheus y Grafana; alarmas en CloudWatch (CPU, 5xx, p95, almacenamiento
  de RDS) y monitor externo de `/health` cada minuto (KPI K3).

## E9 · Pruebas no funcionales
- [ ] Carga con Locust: 100 usuarios concurrentes durante 15 minutos, p95 ≤ 3 s y errores < 1 % (PC-01).
- [ ] Estrés con Locust hasta el punto de quiebre y recuperación sin pérdida de datos (PC-02).
- [ ] OWASP ZAP sobre staging sin hallazgos de riesgo alto (PS-04).
- [ ] Publicar los resultados en `docs/resultados_tests.md`, incluidas las pruebas fallidas y su corrección.

## E10 · Clasificador CNN (ResNet18) y YOLO

Estado al 18-10-2026: la CNN está entrenada y medida fuera del repositorio (ResNet18 preentrenada, 1 canal,
salida sigmoide; 6.601 mamografías de CBIS-DDSM y CMMD; AUC 0,843, sensibilidad 0,843 y especificidad 0,664 con
umbral 0,35). Detalle en el informe, sección 3.8. YOLO (localización de la lesión) sigue en desarrollo.

### Modelo
- [x] Arquitectura con licencia permisiva: ResNet18 de torchvision (BSD) con transferencia desde ImageNet.
- [ ] Versionar en el repo los scripts de entrenamiento (`preparar_completas.py`, script de CMMD, `config_torch.py`,
  `datos_torch.py`, `entrenar_transfer2.py`, `umbrales.py`) en una carpeta `ml/`, sin los datos ni los pesos.
- [ ] Guardar los pesos (`transfer_combinado.pt`) fuera de Git (almacenamiento de artefactos o Git LFS) y registrar
  su hash y versión.
- [ ] Corregir el filtro de CBIS-DDSM que dejó fuera 230 mamografías completas.
- [ ] Reentrenar con división **por paciente** (`division.csv`, la misma que usará YOLO) y medir con un conjunto
  externo no usado en el entrenamiento.

### Integración con la plataforma
- [ ] Servicio de inferencia en contenedor propio (puerto 8080) que implemente `POST /predict`: recibe la imagen,
  aplica el mismo preprocesamiento (escala de grises, CLAHE 2,0 / 8×8, 512×512) y devuelve `probability`,
  `detected` (según el umbral), `model_version` e `is_simulated=false`.
- [ ] Adaptar `HttpYoloProvider` (renombrar a `HttpInferenceProvider`) para leer la probabilidad y guardarla en
  `inference_results.confidence`.
- [ ] Umbral de operación (0,35) como parámetro clínico versionado en `triage_configs`, editable por el médico (CU13).
- [ ] Usar la probabilidad como factor IA del triage en lugar de la confianza simulada.

### KPI K5 alineado con el informe
- [ ] Cambiar `meets_k5` en `/dashboard/model-performance`: hoy evalúa exactitud ≥ 90 %, y el informe fija
  **AUC ≥ 0,80 y sensibilidad ≥ 0,80**. Para calcular el AUC en operación se necesita la probabilidad de cada
  resultado (ya queda en `inference_results.confidence`) junto con el veredicto del médico.
- [ ] Actualizar los tests de `test_signature_model_performance.py` a los nuevos criterios.

### YOLO (segunda etapa)
- [ ] Integrar la detección de la lesión (cajas en `inference_results.detections`) y combinarla con la probabilidad
  de la CNN en la regla de prioridad.
- [ ] Publicar la integración del modelo real como versión 3.0.0 (cambia el contrato de inferencia).

## Mejoras menores detectadas
- [ ] Recálculo periódico del triage (tarea programada) para que el factor «tiempo de espera» suba sin datos nuevos.
- [ ] Actualizar `docs/resultados_tests.md` a la versión 2.2.0 (206 tests).
- [ ] La suite usa `pgserver`, que no tiene versión para Python 3.13; documentar `TEST_DB_DSN` con un PostgreSQL
  local como alternativa en el README.
