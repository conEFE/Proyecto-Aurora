# CHANGELOG de alineación por sprints — Proyecto Aurora

Registro de lo implementado en cada sprint según `docs/ESPEC_AGENTE_Aurora_alineacion_sprints.md`.
Rama de trabajo: `feature/alineacion-sprints` (un commit por sprint, prefijo `sprint-N:`).

---

## Sprint 1 — Base del sistema

### ⚠️ ROTAR credenciales expuestas
`backend/.env` y `backend/create_user.sql` estuvieron versionados en un repositorio **público**
desde el commit "Proyecto Aurora - Versión 1.0". Se quitaron del índice y se agregaron a `.gitignore`,
pero **siguen en el historial de Git** (no se reescribió el historial, por la regla 9 de `CLAUDE.md`).
Acciones pendientes del equipo:
- Cambiar la contraseña del usuario de PostgreSQL que aparecía en `DB_DSN` / `create_user.sql`.
- Generar una nueva `ENCRYPTION_KEY` y volver a cifrar (o descartar) las imágenes de desarrollo.
- Decidir si se limpia el historial (`git filter-repo`), lo que requiere aprobación explícita.

También se quitaron del repo las imágenes de prueba de `backend/data/images/` (datos locales).

### Backend
- `config.py`: `SECRET_KEY` obligatorio y sin valor por defecto (la app no arranca si falta),
  `ACCESS_TOKEN_EXPIRE_MINUTES=30`, `MAX_UPLOAD_MB=60`, `JWT_ALGORITHM=HS256`.
- Autenticación con **JWT HS256** (`python-jose`): claims `sub` (id de usuario), `role`, `exp`, `iat`.
  `POST /auth/login` devuelve `{access_token, token_type, role, full_name}`.
- `auth/bearer.py` y `auth/rbac.py` reescritos: se decodifica el JWT, el usuario se carga **desde la BD**
  y el rol se verifica con `require_roles(...)` contra `user.role` (no contra el token).
  Se eliminó el token `"RUT-ROL"` y las funciones duplicadas.
- CORS desde `settings.ALLOWED_ORIGINS`.
- Middleware `ProcessTimeMiddleware`: header `X-Process-Time-Ms` y log de duración por request.
- Capa de servicios: `app/services/auth_service.py`.
- `app/db/base.py` ya no crea un segundo engine; solo define `Base`.
- `backend/.env.example` sin valores reales; `requirements-dev.txt` (pytest, pytest-cov, httpx, ruff, black, pgserver).
- Se corrigieron dos `downgrade` heredados que no eran reversibles (FK sin nombre en `7422d5d08f56` y el
  tipo enum `userrole` que quedaba huérfano en `87f4c51bde56`). Solo se tocó el `downgrade`.

### Frontend
- `services/api.ts`: login con `access_token`; ante un 401 con sesión activa se cierra la sesión y se vuelve
  al login (un 401 por contraseña incorrecta ya no recarga la página). Sin `any`.
- Se quitó `@supabase/supabase-js` (sin uso) y `@types/jspdf` (obsoleto; jsPDF trae sus propios tipos).
- Errores heredados de lint/typecheck corregidos (21 de ESLint y 21 de TypeScript).

### Pruebas (DoD)
- Login correcto e incorrecto, usuario inexistente, token expirado → 401, token manipulado → 401,
  token firmado con otra clave → 401, `Bearer 1-ADMIN` → 401, rol leído desde la BD.
- Migraciones: `downgrade base` → `upgrade head` probado en test.
- BD de pruebas aislada: PostgreSQL embebido (`pgserver`) o `TEST_DB_DSN`.

---

## Sprint 2 — Usuarios y pacientes

### Backend
- Migración `b2f1c0a9d801` (reversible):
  - Enum `userrole` + `ADMINISTRATIVO`; `users.full_name`, `is_active`, `created_at`, `last_login_at`;
    `rut` VARCHAR(12) y `email` VARCHAR(150).
  - `patients`: `first_name`, `last_name`, `birth_date` NOT NULL, `sex` con CHECK (`F`,`M`,`O`),
    `family_history_first_degree`, `previous_breast_cancer`, `consent_given`, `consent_at`,
    `consent_registered_by`, `created_by`.
  - Tabla `audit_log` **append-only**: además de no exponer UPDATE/DELETE en la API, un trigger en la BD
    rechaza cualquier UPDATE o DELETE.
- **Decisiones sobre datos existentes** (documentadas en la migración): `full_name` se rellena con el email;
  nombres nulos de pacientes → `'SIN REGISTRO'`; `birth_date` nula → `1900-01-01` (marcador evidente para
  revisión manual); pacientes existentes quedan con `consent_given = false`.
- El `downgrade` recrea el enum sin `ADMINISTRATIVO` y **se detiene con un error** si aún hay usuarios con ese
  rol (para no convertirlos silenciosamente a otro rol).
- `/auth/signup` eliminado. Nuevos `POST/GET /admin/users` y `PATCH /admin/users/{id}` (solo ADMIN). Un ADMIN no
  puede desactivarse ni quitarse el rol a sí mismo. Un usuario desactivado no puede iniciar sesión y sus tokens
  vigentes dejan de servir (el usuario se lee de la BD en cada request).
- `init_user.py` reescrito: crea el primer ADMIN desde `AURORA_ADMIN_*` (variables de entorno). Ya no genera
  `create_user.sql` con contraseñas.
- Pacientes: solo `ADMINISTRATIVO` y `MEDICO` (un ADMIN recibe 403, D11). RUT validado con dígito verificador
  (módulo 11) y normalizado (`12.345.678-k` → `12345678-K`); consentimiento obligatorio con `consent_at` y
  `consent_registered_by` automáticos; `PUT /patients/{id}`. El consentimiento no se puede retirar desde la edición.
- Auditoría con `audit(db, user, action, entity, entity_id, detail)`: LOGIN_OK, LOGIN_FAIL (sin guardar el RUT
  intentado), CREATE/UPDATE/VIEW de pacientes (el listado también registra VIEW, sin el término buscado) y
  CREATE/UPDATE de usuarios. `GET /admin/audit` con filtros (usuario, acción, entidad, fechas) y paginación.
- Errores de dominio (`app/services/errors.py`) traducidos a HTTP con mensajes en español.
- `BCRYPT_ROUNDS` configurable (12 por defecto; los tests usan 4 para ir rápido).

### Frontend
- AdminPanel: CRUD de usuarios con selector de 3 roles, activar/desactivar y visor de auditoría con filtros
  y paginación. El ADMIN solo ve la sección de Administración.
- PatientModal: campos nuevos, antecedentes, validación de RUT en el cliente y checkbox de consentimiento
  obligatorio con texto explicativo.
- Se eliminó la pantalla pública de Signup y el "¿Olvidó su contraseña?" que no hacía nada. Los errores de login
  se muestran en pantalla (antes con `alert`).
- Navegación filtrada por rol.

### Pruebas (DoD)
- Permisos: ADMINISTRATIVO y MEDICO no gestionan usuarios ni ven la auditoría (403); ADMIN no ve pacientes (403).
- RUT inválido → 422 (usuarios y pacientes); paciente sin consentimiento → 422; duplicados → 409.
- Auditoría verificada (LOGIN_OK/LOGIN_FAIL, CREATE/UPDATE/VIEW) y sin RUT ni nombre en `detail`.
- `audit_log` rechaza UPDATE y DELETE a nivel de BD.

---

## Sprint 3 — Casos clínicos y antecedentes

### Backend
- Migración `c3a7e5d2f103` (reversible):
  - `cases.patient_id` NOT NULL; `medico_id` renombrado a `created_by`; nuevos `assigned_medico_id`,
    `status` (enum `casestatus`), `palpable_mass`, `nipple_discharge`, `skin_or_nipple_changes`,
    `birads_reported` (CHECK 0–6), `updated_at`, `closed_at`; `code` VARCHAR(20).
  - **Decisión sobre casos sin paciente:** se asignan a un paciente de prueba `SIN-ASIGNAR` (RUT ficticio `1-9`,
    sin consentimiento) en lugar de borrarlos, para no perder imágenes de desarrollo. El `downgrade` deshace la
    asignación y elimina ese paciente.
  - **Decisión sobre códigos existentes:** se regeneran todos con el formato `AUR-AAAA-NNNNNN`. En la v1.0 el
    código era texto libre escrito a mano (podía contener nombres u otros datos identificables).
- Generador de código `AUR-AAAA-NNNNNN` con la secuencia de BD `case_code_seq` (única y sin colisiones entre
  requests concurrentes; el año es el de creación y el correlativo es global).
- Máquina de estados en `services/case_service.py`: `ABIERTO → PRIORIZADO → EN_REVISION → CERRADO` y
  `PRIORIZADO → ABIERTO` cuando cambian los datos. Toda otra transición → 409.
- Endpoints: `POST /cases` (409 si el paciente no tiene consentimiento), `GET /cases` (filtros por estado y
  paciente, paginado), `GET /cases/{id}`, `PATCH /cases/{id}` (síntomas y BI-RADS; 409 si está CERRADO).
  El filtro por nivel de triage se agrega en S5, cuando existe el triage.
- Casos visibles para todo el personal clínico (MEDICO y ADMINISTRATIVO), no solo para su creador: la cola
  de triage es compartida. ADMIN recibe 403 (D11).
- Auditoría de CREATE, VIEW y UPDATE de casos.
- Rutas heredadas (imágenes, resultados, reportes, `/user`) adaptadas a `created_by` hasta su reemplazo en S4–S6.

### Frontend
- CaseManagement reescrito: creación ligada a un paciente (buscar o registrar con consentimiento), formulario de
  síntomas y BI-RADS, badge de estado, filtro por estado y paginación. El detalle permite editar antecedentes
  y queda en solo lectura si el caso está cerrado.
- ImageUpload ya no crea casos con un código escrito a mano: se elige un caso abierto existente.

### Pruebas (DoD)
- Transiciones válidas (4) e inválidas (8, todas 409); reapertura de un caso priorizado al cambiar datos.
- Caso sin consentimiento → 409; paciente inexistente → 404; BI-RADS fuera de rango → 422; caso cerrado no
  editable → 409; ADMIN sin acceso a casos; auditoría de casos.
- Migración con datos de la v1.0 (caso sin paciente, código libre, paciente sin nombre) probada.

---

## Sprint 4 — Exámenes e imágenes

### Backend
- Migración `d4b8f6e3a204` (reversible): `images.exam_type` (enum MAMOGRAFIA/ECOGRAFIA/OTRO, por defecto
  MAMOGRAFIA), `laterality` (CHECK `L`/`R`), `uploaded_by`, `sha256`; `inference_results.is_simulated` NOT NULL
  (los resultados existentes quedan en `true`, eran aleatorios) y `model_version` NOT NULL.
- `StorageBackend` (`save`, `load`, `delete`) con la implementación `LocalEncryptedStorage` (Fernet). Se conserva
  la derivación de clave de la v1.0 para poder leer archivos ya cifrados. **Cambio:** si falta `ENCRYPTION_KEY`
  la carga falla con un error claro; antes se generaba una clave aleatoria en cada arranque y las imágenes
  quedaban ilegibles al reiniciar. El nombre del archivo en disco es aleatorio (el nombre original puede traer
  datos del paciente) y se protege contra path traversal.
- SHA-256 del archivo original. Límite `MAX_UPLOAD_MB` (60 por defecto) → 413. Solo PNG y JPEG → 415.
  Mínimo 100×100 px → 422. Caso cerrado → 409.
- `InferenceProvider.analyze(bytes) -> InferenceOutput` con:
  - `SimulatedProvider`: sin `time.sleep`, determinístico por SHA-256, `model_version="simulado-v1"`,
    `is_simulated=True` y mensaje con prefijo `[IA SIMULADA]`.
  - `HttpYoloProvider`: stub que hace POST a `INFERENCE_URL/predict` si `INFERENCE_PROVIDER=http`.
- La inferencia se ejecuta automáticamente al subir (BackgroundTasks, con su propia sesión de BD) y deja el hook
  `on_inference_completed` para el triage (S5). Subir una imagen a un caso PRIORIZADO lo devuelve a ABIERTO.
- `GET /cases/{id}/images/{image_id}/file` y `/inference`: solo MEDICO, registran VIEW. `GET /cases/{id}/images`
  devuelve metadatos al personal clínico; el resultado de IA solo se incluye para MEDICO.
- Se eliminó `rutas_results.py` (`POST /images/{id}/results`, que generaba resultados con `time.sleep` aleatorio):
  la inferencia ahora es automática.
- `ALLOWED_ORIGINS` pasa a leerse como texto separado por comas (el tipo `str | list[str]` fallaba al venir de
  una variable de entorno).

### Frontend
- ImageUpload: selector de caso, tipo de examen y lateralidad; barra de progreso real (XMLHttpRequest);
  resultados con badge **«IA SIMULADA»** y aviso de que no tienen valor clínico.
- Las imágenes se piden con el header `Authorization` y se muestran como object URL. Antes se armaba
  `?token=...` en la URL (exponía el token y el backend no lo aceptaba, así que las imágenes no cargaban).
- El detalle de caso muestra imágenes, cajas de detección y resultado para MEDICO; ADMINISTRATIVO solo ve
  metadatos.
- Compresión opcional en el cliente detrás de `VITE_CLIENT_COMPRESSION` (desactivada por defecto: re-codificar a
  JPEG pierde información).
- Home y Login sin afirmaciones no respaldadas ("92% de precisión", "1.200+ casos", "HIPAA", "modelo entrenado
  con miles de imágenes"): la IA es simulada y así se indica.

### Pruebas (DoD)
- Subida PNG/JPEG con metadatos y SHA-256; límite de tamaño (413), formatos no soportados (415), imagen
  diminuta y lateralidad inválida (422), caso cerrado (409), caso inexistente (404).
- Archivo cifrado en disco: distinto del original, no descifrable con otra clave, recuperable con la correcta.
- ADMINISTRATIVO sube pero recibe 403 al ver el archivo o la inferencia; ADMIN sin acceso.
- Inferencia automática marcada `is_simulated=true`; proveedor simulado determinístico y sin esperas.

---

## Sprint 5 — Triage y priorización

### Backend
- Migración `e5c9a7f4b305` (reversible): tablas `triage_configs`, `triage_results` y `notifications`, enum
  `triagelevel` y **seed de la configuración v1** (sección 5). Índices únicos parciales garantizan en la BD una
  sola configuración activa y un solo triage vigente por caso; un CHECK exige motivo cuando hay override.
- `services/triage_engine.compute_triage(case, patient, inferences, params, now)`: función pura, sin BD
  (re-exportada en `services/triage_service.py`). Paso 1 reglas `R_BIRADS` y `R_SINTOMA`; paso 2 puntaje
  ponderado 0–100 con aritmética decimal (redondeo a 2 decimales, para que los límites 59,99/60 sean exactos);
  paso 3 umbrales. El `breakdown` guarda valor, normalizado, peso y aporte de cada factor, la regla disparada y
  si la IA usada era simulada.
- Validación Pydantic de parámetros: pesos que suman 100, `alta > media`, BI-RADS 0–6, bandas de edad válidas.
- Recálculo automático al terminar la inferencia, al crear/editar el caso, al editar antecedentes del paciente
  (sus casos abiertos) y al activar una configuración nueva (todos los casos no cerrados). Manual con
  `POST /cases/{id}/triage`. Al calcular, el caso pasa de ABIERTO a PRIORIZADO; los resultados anteriores
  quedan con `is_current=false` (historial en `GET /cases/{id}/triage/history`).
- `POST /cases/{id}/triage/override` (solo MEDICO, motivo obligatorio, registra OVERRIDE con nivel anterior y
  nuevo). `GET /triage/queue` (ADMINISTRATIVO recibe solo código, nivel, estado y antigüedad).
  `GET /triage/config`, `GET /triage/config/history` (MEDICO y ADMIN) y `POST /triage/config` (solo MEDICO,
  registra CONFIG_CHANGE). `GET /cases?level=` filtra por nivel vigente.
- Notificaciones a los médicos activos cuando un caso pasa a ALTA (no se repiten mientras siga en ALTA).
  `GET /notifications`, `PATCH /notifications/{id}/read` (solo las propias).
- KPI creación → primer triage registrado en el log (`aurora.triage`). Como el triage se calcula al crear el
  caso, el primer valor queda en segundos (meta ≤ 5 min).

### Decisiones de interpretación (para confirmar con el equipo)
- **Puntaje con escalamiento:** cuando se dispara una regla el nivel es ALTA sin mirar el puntaje, pero el puntaje
  se calcula y se guarda igual, como dato informativo y para ordenar la cola dentro de ALTA.
- **Override y recálculo:** si se recalcula por un cambio de configuración (mismos datos clínicos) se conserva el
  override del médico. Si cambian los datos del caso (imagen nueva, síntomas, antecedentes) el override no se
  arrastra: el nivel vuelve al calculado y el médico debe reevaluar. El override anterior queda en el historial.
- **Triage al crear el caso:** se calcula de inmediato aunque no haya imágenes (la IA aporta 0). Así las reglas
  de BI-RADS y síntomas priorizan el caso desde el primer momento.
- La cola incluye casos PRIORIZADOS y EN_REVISION (este último se puede ocultar con `include_in_review=false`).

### Frontend
- **Cola de triage**: tabla ordenada con color por nivel, contadores por nivel, antigüedad y refresco cada 30 s.
  El ADMINISTRATIVO ve la versión mínima.
- **Detalle de triage** en el caso (MEDICO): desglose por factor, regla disparada, badge IA SIMULADA cuando
  corresponde, recálculo, historial y cambio de nivel con motivo obligatorio.
- **Parámetros de triage**: edición de pesos (validación de suma 100), umbrales, reglas y bandas de edad, motivo
  del cambio e historial de versiones. MEDICO edita; ADMIN solo consulta.
- **Campana de notificaciones** para MEDICO con los casos ALTA; al hacer clic abre el caso.

### Pruebas (DoD)
- `compute_triage`: cada regla de escalamiento (R_BIRADS 4 y 5, cada síntoma, regla desactivable, precedencia),
  cada banda de edad (39/40/49/50/69/70/120), límites 59,99 / 60 / 29,99 / 30 (directo y vía cálculo),
  factor IA, tope del tiempo de espera, ejemplo completo y validaciones de parámetros.
- API: pesos que no suman 100 → 422; override sin motivo → 422; orden correcto de la cola (nivel, puntaje y
  antigüedad); vista mínima para ADMINISTRATIVO; nueva versión recalcula; override conservado al cambiar la
  configuración; notificaciones; permisos y auditoría.

---

## Sprint 6 — Dashboard y reportes

### Backend
- Migración `f6d0b8a5c406` (reversible): `clinical_reviews` (una por caso, CHECK de BI-RADS 0–6 y de
  recomendación), `reports` y `request_metrics`.
- `POST /cases/{id}/take` (PRIORIZADO → EN_REVISION, asigna al médico) y `POST /cases/{id}/review`
  (EN_REVISION → CERRADO con `closed_at`). **Un caso solo se cierra con revisión**: no hay otra vía en la API y
  la máquina de estados no permite saltar a CERRADO. `GET /cases/{id}/review`.
- Reportes (SC-02): `GET /cases/{id}/reports/metadata` entrega los metadatos tipo DICOM (`PatientID` = código del
  caso, `StudyDate`, `Modality=MG`, hallazgos, BI-RADS, recomendación, nivel de triage, versiones del modelo y si la
  IA es simulada) y `POST /cases/{id}/reports` con `{content_hash}` registra el PDF y devuelve esos metadatos,
  con auditoría EXPORT. Solo para casos cerrados con revisión.
  - **Ajuste respecto de la especificación:** la especificación pide que el POST devuelva los metadatos que el
    frontend incrusta en el PDF, pero el POST también recibe el SHA-256 de ese mismo PDF: no se puede calcular el
    hash de un archivo que todavía no tiene los metadatos. Por eso se agregó el GET previo; el POST conserva el
    contrato pedido.
- `GET /dashboard/metrics?from=&to=&alta_pending_hours=` (los 3 roles, solo agregados): casos por estado y por nivel,
  promedio creación → primer triage (KPI ≤ 5 min), promedio triage → revisión por nivel, casos ALTA pendientes por
  más de X horas (`ALTA_PENDING_HOURS`, 24 por defecto), p95 de la API desde la tabla `request_metrics` (la llena el
  middleware de S1 con la plantilla de la ruta, sin ids), proporción de overrides y casos por semana.
- **Endpoints eliminados** (reportado aquí antes de borrar):
  - `GET /reports/statistics` y `GET /reports/monthly`: reemplazados por `/dashboard/metrics`.
  - `GET /user/tickets`: devolvía dos tickets de soporte escritos a mano en el código; no tiene respaldo en los
    informes ni modelo de datos.
  - `GET /user/info` y `GET /user/patients`: duplicaban `/auth/me` y `/patients`.
  - (En S4 ya se había quitado `POST /images/{id}/results`.)
- `scripts/seed_dev.py`: 3 usuarios (uno por rol), 10 pacientes ficticios y 10 casos que cubren ALTA, MEDIA y BAJA.
  La contraseña de prueba se lee de `AURORA_SEED_PASSWORD`; es idempotente.
- `scripts/gen_docs.py`: genera `docs/modelo_datos.md` desde los modelos SQLAlchemy y `docs/endpoints.md` desde las
  rutas (con los roles leídos de las dependencias `require_roles`).

### Frontend
- **Dashboard** (reemplaza a Reportes, visible para los 3 roles): tarjetas de KPI con indicador de meta, barras por
  nivel, línea de casos por semana con tooltip, tiempos triage → revisión, proporción de overrides, filtro de
  fechas y vista de tabla.
- **Revisión médica** en el detalle del caso: tomar caso, formulario de BI-RADS final, hallazgos y recomendación;
  resumen cuando el caso está cerrado.
- `generatePdf.ts` reescrito: código anónimo (sin nombre ni RUT; solo la edad), nivel de triage y desglose, badge
  IA SIMULADA, revisión médica, metadatos DICOM (tabla y propiedades del PDF), fecha y médico. Se calcula el SHA-256
  de los bytes exactos que se descargan y se registran con `POST /cases/{id}/reports`.
- Se quitó «Mi panel» (dependía de `/user/*` y de tickets ficticios). Título de la página: «Proyecto Aurora».

### Pruebas (DoD)
- Métricas con datos de prueba controlados (tiempos exactos, p95 sobre 100 valores, ALTA pendientes, overrides,
  filtro de fechas) y percentil unitario.
- Cierre solo con revisión; revisión duplicada (409); validaciones (422); solo MEDICO.
- Reporte registrado, auditado (EXPORT) y sin datos identificables en los metadatos.
- **E2E**: paciente → caso → imagen → triage → revisión → reporte, con ADMINISTRATIVO y MEDICO, más dashboard y
  auditoría vistos por ADMIN.
- Total: 178 tests aprobados, cobertura 96% (servicios ≈ 94%). Detalle en `docs/resultados_tests.md`.

### Limitación conocida (para el equipo)
- El factor «tiempo de espera» se fija al calcular el triage. Un caso que no recibe datos nuevos no sube de puntaje
  solo por esperar hasta que se recalcule (manualmente o al cambiar la configuración). Un recálculo periódico
  (tarea programada) se puede sumar en S7 junto con la infraestructura.

---

## 2.1.0 — Validación médica de la IA y del triage (complemento del Sprint 6)

Faltaba un canal para que el médico **apruebe o rechace** el resultado de la IA y el nivel de triage, y que ese
resultado quede registrado. Antes solo existía el override (que registra el desacuerdo, pero no el acuerdo).

### Backend
- Migración `a7e1c9b6d507` (reversible): tabla `ai_validations` (una por imagen) y en `clinical_reviews` los campos
  `triage_assessment`, `triage_comment`, `triage_level_at_review` y `triage_config_version_at_review`. Las revisiones
  existentes quedan con la evaluación en NULL: no se inventa una evaluación que no se hizo.
- `PUT /cases/{id}/images/{image_id}/validation` (solo MEDICO): `CONCORDANTE`, `FALSO_POSITIVO` (solo si la IA
  informó hallazgo), `FALSO_NEGATIVO` (solo si no lo informó) o `NO_EVALUABLE`, con comentario opcional. Se puede
  corregir hasta el cierre. Guarda una copia de lo evaluado (hallazgo, versión del modelo y si era simulado) y se
  audita como CREATE/UPDATE de la imagen con el veredicto anterior.
- La revisión exige `triage_assessment` (`APROPIADO`, `SOBREESTIMADO`, `SUBESTIMADO`) y guarda el nivel y la versión
  de configuración evaluados. **No se puede cerrar el caso** si alguna imagen con resultado de IA no fue validada (409).
- Dashboard: concordancia IA–médico (concordantes sobre evaluables), conteo por veredicto, cuántas validaciones son
  sobre IA simulada, y tasa de aprobación del triage con conteo por evaluación.
- Metadatos del reporte: `TriageAssessment` y `AIValidation` (resumen de veredictos).

### Frontend
- En cada imagen (MEDICO): «¿Está de acuerdo con el resultado de la IA?» con los veredictos que aplican al
  resultado, comentario y opción de cambiarlo hasta el cierre.
- En la revisión: bloque «Evaluación del triage» con el nivel vigente. Si el médico ya había ajustado el nivel, se
  sugiere sobreestimado o subestimado según el sentido del ajuste. Aviso y botón deshabilitado mientras falten
  validaciones.
- Dashboard: tarjetas «Concordancia IA – médico» (con advertencia cuando es sobre IA simulada) y «Aprobación del
  triage».
- PDF: sección «Validación médica de la IA y del triage».

### Pruebas
- 15 tests nuevos (`test_validation.py`): validación y corrección auditadas, coherencia veredicto–resultado (422),
  permisos, cierre bloqueado sin validación, evaluación del triage obligatoria con copia del nivel, metadatos del
  reporte y métricas de concordancia con datos controlados. Total: 193 tests aprobados, cobertura 96%.

---

## Pendiente para S7–S8 (no implementado, según la regla 2)
Docker y docker-compose, GitHub Actions, `S3EncryptedStorage`, rate limiting y bloqueo de login, revisión OWASP,
despliegue en AWS, `HttpYoloProvider` real, pruebas de carga con Locust y soporte DICOM en la carga.
