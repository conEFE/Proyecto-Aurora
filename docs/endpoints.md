# Endpoints — Proyecto Aurora API

Generado automáticamente desde las rutas FastAPI con `python -m scripts.gen_docs`. La especificación completa
está en `/openapi.json` y la documentación interactiva en `/docs` del backend.

| Método | Ruta | Roles permitidos | Descripción |
|---|---|---|---|
| GET | `/admin/audit` | ADMIN | Bitácora de auditoría con filtros por usuario, acción, entidad y fecha (paginada). |
| GET | `/admin/errors` | ADMIN | Errores 5xx del servidor (sin datos sensibles), con filtros por fecha, tipo y código. |
| GET | `/admin/errors/types` | ADMIN | Tipos de error registrados y su frecuencia (para el filtro de la vista). |
| GET | `/admin/stats` | ADMIN | Conteos agregados del sistema (sin datos clínicos). |
| GET | `/admin/users` | ADMIN | Lista usuarios (filtros por rol y estado). |
| POST | `/admin/users` | ADMIN | Crea un usuario con su rol (reemplaza al signup público). |
| PATCH | `/admin/users/{user_id}` | ADMIN | Cambia rol, datos o estado activo de un usuario. |
| POST | `/admin/users/{user_id}/unlock` | ADMIN | Quita el bloqueo por intentos fallidos de inicio de sesión. |
| POST | `/auth/change-password` | Cualquier usuario autenticado | Cambia la contraseña del usuario autenticado. Revoca los tokens anteriores y entrega uno nuevo. |
| POST | `/auth/login` | Público | Login con RUT y contraseña. Devuelve un JWT firmado (HS256). |
| GET | `/auth/me` | Cualquier usuario autenticado | Información del usuario autenticado (incluye si debe cambiar su contraseña). |
| GET | `/cases` | ADMINISTRATIVO, MEDICO | Lista casos con filtros por estado, nivel de triage vigente y paciente. |
| POST | `/cases` | ADMINISTRATIVO, MEDICO | Crea un caso para un paciente con consentimiento registrado (409 si no lo tiene). |
| GET | `/cases/{case_id}` | ADMINISTRATIVO, MEDICO | Detalle del caso (registra VIEW). |
| PATCH | `/cases/{case_id}` | ADMINISTRATIVO, MEDICO | Edita síntomas y BI-RADS informado. Bloqueado si el caso está CERRADO (409). |
| GET | `/cases/{case_id}/images` | ADMINISTRATIVO, MEDICO | Metadatos de las imágenes del caso. El resultado de IA solo se incluye para el rol MEDICO. |
| POST | `/cases/{case_id}/images` | ADMINISTRATIVO, MEDICO | Sube una imagen (PNG o JPEG, máx. MAX_UPLOAD_MB). La inferencia corre en segundo plano. |
| GET | `/cases/{case_id}/images/{image_id}/file` | MEDICO | Devuelve la imagen descifrada (solo MEDICO; queda registrado como VIEW). |
| GET | `/cases/{case_id}/images/{image_id}/inference` | MEDICO | Resultado de la inferencia de una imagen (solo MEDICO). |
| POST | `/cases/{case_id}/images/{image_id}/inference/retry` | MEDICO | Vuelve a analizar la imagen con el modelo real (sin resultado o con el respaldo simulado). Solo MEDICO. |
| PUT | `/cases/{case_id}/images/{image_id}/validation` | MEDICO | El médico aprueba o rechaza el resultado de IA de la imagen (concordante, falso positivo/negativo, no evaluable). |
| GET | `/cases/{case_id}/reports` | MEDICO | Reportes PDF registrados del caso. |
| POST | `/cases/{case_id}/reports` | MEDICO | Registra un PDF generado (SHA-256) y devuelve sus metadatos DICOM. Exige la firma del médico. Auditado (EXPORT). |
| GET | `/cases/{case_id}/reports/metadata` | MEDICO | Metadatos tipo DICOM (SC-02) que el frontend incrusta en el PDF antes de calcular su SHA-256. |
| GET | `/cases/{case_id}/reports/signature` | MEDICO | Firma del reporte y su verificación (HMAC válido y contenido sin cambios desde la firma). |
| POST | `/cases/{case_id}/reports/signature` | MEDICO | El médico que revisó el caso firma su conformidad con el reporte, confirmando su contraseña. Queda auditado (SIGN). |
| GET | `/cases/{case_id}/review` | MEDICO | Revisión médica del caso. |
| POST | `/cases/{case_id}/review` | MEDICO | Registra la revisión (incluida la evaluación del triage) y cierra el caso (EN_REVISION → CERRADO). |
| POST | `/cases/{case_id}/take` | MEDICO | El médico toma el caso: PRIORIZADO → EN_REVISION. |
| GET | `/cases/{case_id}/triage` | MEDICO | Triage vigente con el desglose por factor (solo MEDICO). |
| POST | `/cases/{case_id}/triage` | MEDICO | Recalcula el triage del caso con la configuración activa. |
| GET | `/cases/{case_id}/triage/history` | MEDICO | Todos los cálculos del caso, del más reciente al más antiguo. |
| POST | `/cases/{case_id}/triage/override` | MEDICO | El médico fija el nivel final. El motivo es obligatorio y queda en la auditoría (OVERRIDE). |
| GET | `/dashboard/metrics` | ADMIN, ADMINISTRATIVO, MEDICO | Métricas agregadas: volumen por estado y nivel, KPIs de tiempo, ALTA pendientes, p95 y overrides. |
| GET | `/dashboard/model-performance` | ADMIN, MEDICO | Desempeño del modelo por versión (matriz de confusión, exactitud, sensibilidad, especificidad, IC 95 %). |
| GET | `/health` | Público | Estado de la API. |
| GET | `/inference/status` | ADMIN, ADMINISTRATIVO, MEDICO | Qué proveedor de IA usa la plataforma y si el modelo real responde (sin datos de pacientes). |
| GET | `/notifications` | Cualquier usuario autenticado | Notificaciones del usuario autenticado (no leídas primero). |
| PATCH | `/notifications/{notification_id}/read` | Cualquier usuario autenticado | Marca como leída una notificación propia. |
| GET | `/patients` | ADMINISTRATIVO, MEDICO | Busca pacientes por RUT o nombre (registra VIEW). Los bloqueados solo aparecen si se piden. |
| POST | `/patients` | ADMINISTRATIVO, MEDICO | Registra un paciente. El consentimiento informado es obligatorio. |
| GET | `/patients/{patient_id}` | ADMINISTRATIVO, MEDICO | Detalle del paciente (registra VIEW). |
| PUT | `/patients/{patient_id}` | ADMINISTRATIVO, MEDICO | Edita datos y antecedentes del paciente; recalcula el triage de sus casos abiertos. |
| POST | `/patients/{patient_id}/block` | ADMINISTRATIVO, MEDICO | Bloquea el tratamiento de los datos (exige casos cerrados). Los datos se conservan por la Ley 20.584. |
| POST | `/patients/{patient_id}/consent` | ADMINISTRATIVO, MEDICO | Registra el consentimiento con el texto vigente (nuevo otorgamiento o actualización de versión). |
| GET | `/patients/{patient_id}/consent/events` | ADMINISTRATIVO, MEDICO | Historial del consentimiento con la versión del texto aceptado. |
| POST | `/patients/{patient_id}/consent/withdraw` | ADMINISTRATIVO, MEDICO | Retira el consentimiento: impide nuevos casos e imágenes; la ficha clínica se conserva. |
| GET | `/patients/{patient_id}/export` | MEDICO | Copia de todos los datos del paciente en JSON (derechos de acceso y portabilidad). Registra EXPORT. |
| POST | `/patients/{patient_id}/requests` | ADMINISTRATIVO, MEDICO | Registra una solicitud del titular; el plazo de respuesta es de 30 días corridos. |
| POST | `/patients/{patient_id}/unblock` | ADMINISTRATIVO, MEDICO | Levanta el bloqueo de los datos del paciente. |
| GET | `/privacy/consent-text` | ADMINISTRATIVO, MEDICO | Texto de consentimiento vigente, para mostrarlo al paciente antes de registrarlo. |
| GET | `/privacy/consent-texts/{version}` | ADMINISTRATIVO, MEDICO | Una versión del texto de consentimiento (para saber qué aceptó cada paciente). |
| GET | `/privacy/requests` | ADMINISTRATIVO, MEDICO | Solicitudes de los titulares, ordenadas por vencimiento del plazo. |
| GET | `/privacy/requests/summary` | ADMIN, ADMINISTRATIVO, MEDICO | Conteo de solicitudes por estado y vencidas (sin datos de pacientes; visible para el ADMIN). |
| PATCH | `/privacy/requests/{request_id}` | ADMINISTRATIVO, MEDICO | Avanza el estado de una solicitud; resolverla o rechazarla exige una respuesta. |
| GET | `/triage/config` | ADMIN, MEDICO | Configuración de triage activa. |
| POST | `/triage/config` | MEDICO | Crea una nueva versión activa (solo MEDICO) y recalcula los casos no cerrados. |
| GET | `/triage/config/history` | ADMIN, MEDICO | Todas las versiones de la configuración de triage. |
| GET | `/triage/queue` | ADMINISTRATIVO, MEDICO | Cola priorizada. ADMINISTRATIVO solo recibe código, nivel, estado y antigüedad. |
