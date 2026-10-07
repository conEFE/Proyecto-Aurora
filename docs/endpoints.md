# Endpoints — Proyecto Aurora API

Generado automáticamente desde las rutas FastAPI con `python -m scripts.gen_docs`. La especificación completa
está en `/openapi.json` y la documentación interactiva en `/docs` del backend.

| Método | Ruta | Roles permitidos | Descripción |
|---|---|---|---|
| GET | `/admin/audit` | ADMIN | Bitácora de auditoría con filtros por usuario, acción, entidad y fecha (paginada). |
| GET | `/admin/stats` | ADMIN | Conteos agregados del sistema (sin datos clínicos). |
| GET | `/admin/users` | ADMIN | Lista usuarios (filtros por rol y estado). |
| POST | `/admin/users` | ADMIN | Crea un usuario con su rol (reemplaza al signup público). |
| PATCH | `/admin/users/{user_id}` | ADMIN | Cambia rol, datos o estado activo de un usuario. |
| POST | `/auth/login` | Público | Login con RUT y contraseña. Devuelve un JWT firmado (HS256). |
| GET | `/auth/me` | Cualquier usuario autenticado | Información del usuario autenticado. |
| GET | `/cases` | ADMINISTRATIVO, MEDICO | Lista casos con filtros por estado, nivel de triage vigente y paciente. |
| POST | `/cases` | ADMINISTRATIVO, MEDICO | Crea un caso para un paciente con consentimiento registrado (409 si no lo tiene). |
| GET | `/cases/{case_id}` | ADMINISTRATIVO, MEDICO | Detalle del caso (registra VIEW). |
| PATCH | `/cases/{case_id}` | ADMINISTRATIVO, MEDICO | Edita síntomas y BI-RADS informado. Bloqueado si el caso está CERRADO (409). |
| GET | `/cases/{case_id}/images` | ADMINISTRATIVO, MEDICO | Metadatos de las imágenes del caso. El resultado de IA solo se incluye para el rol MEDICO. |
| POST | `/cases/{case_id}/images` | ADMINISTRATIVO, MEDICO | Sube una imagen (PNG o JPEG, máx. MAX_UPLOAD_MB). La inferencia corre en segundo plano. |
| GET | `/cases/{case_id}/images/{image_id}/file` | MEDICO | Devuelve la imagen descifrada (solo MEDICO; queda registrado como VIEW). |
| GET | `/cases/{case_id}/images/{image_id}/inference` | MEDICO | Resultado de la inferencia de una imagen (solo MEDICO). |
| GET | `/cases/{case_id}/reports` | MEDICO | Reportes PDF registrados del caso. |
| POST | `/cases/{case_id}/reports` | MEDICO | Registra un PDF generado (SHA-256) y devuelve sus metadatos DICOM. Queda auditado como EXPORT. |
| GET | `/cases/{case_id}/reports/metadata` | MEDICO | Metadatos tipo DICOM (SC-02) que el frontend incrusta en el PDF antes de calcular su SHA-256. |
| GET | `/cases/{case_id}/review` | MEDICO | Revisión médica del caso. |
| POST | `/cases/{case_id}/review` | MEDICO | Registra la revisión médica y cierra el caso (EN_REVISION → CERRADO). |
| POST | `/cases/{case_id}/take` | MEDICO | El médico toma el caso: PRIORIZADO → EN_REVISION. |
| GET | `/cases/{case_id}/triage` | MEDICO | Triage vigente con el desglose por factor (solo MEDICO). |
| POST | `/cases/{case_id}/triage` | MEDICO | Recalcula el triage del caso con la configuración activa. |
| GET | `/cases/{case_id}/triage/history` | MEDICO | Todos los cálculos del caso, del más reciente al más antiguo. |
| POST | `/cases/{case_id}/triage/override` | MEDICO | El médico fija el nivel final. El motivo es obligatorio y queda en la auditoría (OVERRIDE). |
| GET | `/dashboard/metrics` | ADMIN, ADMINISTRATIVO, MEDICO | Métricas agregadas: volumen por estado y nivel, KPIs de tiempo, ALTA pendientes, p95 y overrides. |
| GET | `/health` | Público | Estado de la API. |
| GET | `/notifications` | Cualquier usuario autenticado | Notificaciones del usuario autenticado (no leídas primero). |
| PATCH | `/notifications/{notification_id}/read` | Cualquier usuario autenticado | Marca como leída una notificación propia. |
| GET | `/patients` | ADMINISTRATIVO, MEDICO | Busca pacientes por RUT o nombre (registra VIEW). |
| POST | `/patients` | ADMINISTRATIVO, MEDICO | Registra un paciente. El consentimiento informado es obligatorio. |
| GET | `/patients/{patient_id}` | ADMINISTRATIVO, MEDICO | Detalle del paciente (registra VIEW). |
| PUT | `/patients/{patient_id}` | ADMINISTRATIVO, MEDICO | Edita datos y antecedentes del paciente; recalcula el triage de sus casos abiertos. |
| GET | `/triage/config` | ADMIN, MEDICO | Configuración de triage activa. |
| POST | `/triage/config` | MEDICO | Crea una nueva versión activa (solo MEDICO) y recalcula los casos no cerrados. |
| GET | `/triage/config/history` | ADMIN, MEDICO | Todas las versiones de la configuración de triage. |
| GET | `/triage/queue` | ADMINISTRATIVO, MEDICO | Cola priorizada. ADMINISTRATIVO solo recibe código, nivel, estado y antigüedad. |
