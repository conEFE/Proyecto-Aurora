# Implementaciones futuras — Proyecto Aurora

Trabajo pendiente en el repositorio, ordenado por épica, a partir de la revisión del informe de la Unidad 2 y de
las correcciones del 05-10-2026. Lo implementado hasta la versión 2.5.0 está en `docs/CHANGELOG_SPRINTS.md`.

Actualizado: 10-11-2026.

## Estado por épica

| Épica | Tema | Estado en el repo |
|---|---|---|
| E5 | Validación médica del informe de IA, métricas del modelo por versión y firma del reporte | Hecho (2.1.0 y 2.2.0) |
| E6 | Cuentas, seguridad y registro de errores | Hecho (2.3.0); workflow ZAP listo para ejecutar (2.5.0) |
| E7 | Versionado, CI/CD y despliegue (local → staging → piloto) | Preparado (2.5.0): Docker, CI/CD y guía de AWS; falta ejecutar el despliegue |
| E9 | Pruebas no funcionales (carga, estrés y seguridad) | Pendiente (unitarias, integración y E2E listas) |
| E10 | Clasificador CNN (ResNet18) y YOLO para el triage | Modelo CNN entrenado fuera del repo (AUC 0,843); integración pendiente; YOLO en desarrollo |
| — | Cumplimiento Ley 19.628 / 21.719 / 20.584 | Hecho en código (2.4.0); quedan decisiones del equipo |
| — | Mejoras menores detectadas | Pendiente |

## E6 · Cuentas, seguridad y registro de errores

Responde a los comentarios C10 (cambio de contraseña) y C12 (tabla de errores) del informe.

- [x] **Cambio de contraseña**: `POST /auth/change-password` (contraseña actual + nueva), política mínima (largo,
  no repetir la actual), evento `PASSWORD_CHANGE` en `audit_log` y pantalla en el menú de usuario.
- [x] **Cambio obligatorio en el primer inicio de sesión**: columna `users.must_change_password`; el ADMIN la
  activa al crear o restablecer un usuario.
- [x] **Tabla `error_log`** (migración reversible): `id`, `occurred_at`, `method`, `path` (plantilla, sin ids),
  `status_code`, `error_type`, `message` (sin datos sensibles), `user_id` nullable, `request_id`.
  Handler global de excepciones 5xx que registra en la tabla y responde un mensaje genérico con el `request_id`.
- [x] Vista de errores para ADMIN (filtro por fecha y tipo) y conteo en el dashboard; alimenta el KPI K9.
- [x] **Rate limiting y bloqueo de login** (limitador propio, sin dependencias nuevas): N intentos fallidos por RUT/IP → bloqueo temporal,
  auditado como `LOGIN_FAIL` con motivo.
- [x] Revisión OWASP Top 10 y corrección de hallazgos (`docs/seguridad_owasp.md`).
- [ ] Escaneo dinámico con OWASP ZAP sobre staging (S7).
- [x] Tests: cambio de contraseña (correcta, incorrecta, política), bloqueo por intentos, registro en `error_log`
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
- [x] `Dockerfile` para API (Uvicorn) y frontend (build de Vite servido por **Caddy**, que además da TLS automático)
  (2.5.0).
- [ ] `Dockerfile` del servicio de inferencia (cuando exista el servicio real, E10/S8).
- [x] `docker-compose.yml` para local (con PostgreSQL) y `deploy/docker-compose.prod.yml` para producción (2.5.0).
- [x] Healthchecks y política de reinicio automático (2.5.0).

### CI/CD (GitHub Actions)
- [x] **CI en cada PR** (`ci.yml`, 2.5.0): ruff, pytest con `--cov-fail-under=90` y PostgreSQL de servicio (incluye
  la prueba de downgrade de Alembic), pip-audit, ESLint, `tsc`, `npm run build` y npm audit.
- [ ] Agregar `black --check` (falta formatear `init_db.py`) y gitleaks.
- [x] **Imágenes** amd64/arm64 etiquetadas con versión y SHA y publicadas en GHCR al crear un tag (`publish.yml`,
  2.5.0).
- [ ] Escaneo Trivy de las imágenes.
- [ ] **Deploy a staging** automático: OIDC hacia AWS (sin llaves fijas), SSM Run Command en EC2,
  `alembic upgrade head` y `docker compose up -d`.
- [x] Prueba de humo en CI (`/api/health` y encabezados detrás de Caddy) y workflow ZAP baseline a pedido (2.5.0).
- [ ] **Verificación sobre staging** (login, cola) y ZAP contra staging.
- [ ] **Deploy a piloto** al crear un tag `vX.Y.Z`, con aprobación manual (GitHub Environments).
- [ ] **Rollback**: volver a desplegar el tag anterior; la BD se revierte solo si la migración lo exige.
- [ ] Dependabot para pip, npm y GitHub Actions.

### Infraestructura AWS
- [x] **Etapa de demostración** lista para desplegar en `us-east-2`, la región fija del proyecto de AWS:
  `docs/despliegue_aws.md` (EC2 t4g.micro + Docker Compose + Caddy + S3 con `aws/s3` + CloudWatch, ≈ USD 11 al mes
  descontados de los créditos del plan gratuito; variante con RDS). Lo que sigue es la arquitectura del
  **piloto** del informe.
- [x] `S3EncryptedStorage` con SSE-KMS (más el cifrado Fernet de la aplicación); el versionado se activa en el bucket
  (guía) (2.5.0).
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

## Gestión del proyecto en GitHub (respaldo de lo que declara el informe)

El informe describe prácticas que deben existir en el repositorio para que la evidencia sea verificable
(rúbrica 2.1.5 y 2.1.6).

- [ ] **Tablero Scrumban** en GitHub Projects con las columnas y límites WIP de la Tabla 8 del informe (Backlog, Listo
  ≤ 6, En progreso ≤ 2 por persona, En revisión ≤ 3, QA ≤ 3, Hecho) y la vista de flujo acumulado (Insights).
- [ ] Campos del tablero para medir lead time, cycle time y throughput desde el Sprint 7.
- [ ] **Plantillas de issue** para solicitud de cambio (SC-nn: descripción, justificación, impacto en horas, costo,
  riesgo y sprint) e incidente (INC-nn: prioridad P1–P4, detección, acción, verificación).
- [ ] Etiquetas `cambio`, `incidente`, `P1`–`P4`, `épica:E5`…`E10` y registrar SC-02, SC-03 y SC-04 como issues.
- [ ] Protección de la rama `main` (PR + 1 revisión + CI en verde) tal como lo describe la sección 6.3.

## Seguridad del reporte firmado
- [ ] Evaluar firma electrónica avanzada (Ley 19.799) con un prestador acreditado para la fase productiva; hoy la
  conformidad es una firma electrónica simple (contraseña + HMAC + auditoría).

## Cumplimiento legal (detalle en `docs/cumplimiento_legal.md`)
- [x] Consentimiento versionado, retiro, bloqueo, exportación (acceso/portabilidad) y registro de solicitudes con
  plazo de 30 días (2.4.0).
- [x] Evaluación de impacto, procedimiento ante vulneraciones y política de conservación (documento).
- [x] Validar el texto de consentimiento v1 (equipo, 10-11-2026).
- [ ] Acceso por equipo tratante (Ley 20.584): hoy todo MEDICO/ADMINISTRATIVO ve todos los casos.
- [ ] Tarea programada que proponga anonimizar las fichas con el plazo de conservación vencido.
- [ ] Región de la nube y DPA del proveedor al desplegar (cifrado y TLS ya preparados en la 2.5.0).

## Mejoras menores detectadas
- [ ] Recálculo periódico del triage (tarea programada) para que el factor «tiempo de espera» suba sin datos nuevos.
- [x] Actualizar `docs/resultados_tests.md` (2.3.0: 241 tests).
- [x] La suite usa `pgserver`, que no tiene versión para Python 3.13; documentar `TEST_DB_DSN` con un PostgreSQL
  local como alternativa en el README.
