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

## 2.2.0 — Desempeño del modelo por versión y firma médica del reporte (E5)

La validación médica de cada imagen (2.1.0) ya registraba el acuerdo o desacuerdo con la IA, pero no se usaba para
medir el modelo en funcionamiento, y el reporte se emitía sin un acto de conformidad del médico.

### Desempeño del modelo (KPI K5)
- `GET /dashboard/model-performance` (ADMIN, MEDICO; filtro `from`/`to` por fecha del caso): matriz de confusión
  por versión del modelo a partir de `ai_validations` (VP = concordante con hallazgo, VN = concordante sin hallazgo,
  FP y FN según el veredicto), exactitud, sensibilidad, especificidad, VPP, VPN e intervalos de confianza de Wilson
  al 95 %. Usa la copia guardada en cada validación (versión, hallazgo, simulado), así un cambio de modelo no altera
  las métricas de las versiones anteriores.
- `meets_k5` (exactitud ≥ 90 %) solo se evalúa con resultados reales y al menos 30 imágenes evaluables; con IA
  simulada o muestra menor queda en `null`. La referencia es la validación del médico, no la confirmación
  histológica, y así se declara en la respuesta.
- Dashboard: tabla «Desempeño del modelo por versión» con badge IA SIMULADA (solo MEDICO y ADMIN).

### Firma (conformidad) del médico sobre el reporte
- Migración `b8f2d0c7e608` (reversible): tabla `report_signatures` (una por caso) y `reports.signature_id`. Los
  reportes anteriores quedan con la firma en NULL: no se inventa una firma que no se hizo.
- `POST /cases/{id}/reports/signature`: solo el médico que registró la revisión, con el caso cerrado y confirmando su
  contraseña. Guarda el SHA-256 del contenido del reporte (metadatos en JSON canónico) y un HMAC-SHA256 del servidor
  sobre caso, médico, fecha y ese hash. Audita `SIGN`; un intento con contraseña incorrecta audita `SIGN_FAIL`.
- `GET /cases/{id}/reports/signature`: devuelve la firma con `valid`, que es falso si el HMAC no coincide o si el
  contenido del reporte cambió después de firmar.
- `POST /cases/{id}/reports` exige la firma (409 sin ella) y guarda `signature_id`. Los metadatos del reporte llevan
  el bloque `MedicalSignature` (firmante, fecha, código de verificación y hash del contenido).
- Frontend: paso «Firma del médico» en la revisión (declaración de conformidad y contraseña); el PDF se habilita
  después de firmar e incluye la sección «Firma del médico». La bitácora de ADMIN filtra por `SIGN` y `SIGN_FAIL`.

### Pruebas
- 13 tests nuevos (`test_signature_model_performance.py`): firma con caso abierto (409), contraseña incorrecta (422 y
  `SIGN_FAIL`), solo el médico revisor (403), firma única (409), verificación, bloque en metadatos, reporte sin
  firma (409), contenido alterado invalida la firma, métricas por versión con datos controlados, K5 solo con
  resultados reales, permisos e intervalo de Wilson. Se ajustaron los tests de reporte y el E2E para firmar antes de
  emitir. Total: 206 tests aprobados, cobertura 96 %.

---

## 2.3.0 — Cuentas, seguridad y registro de errores (E6)

Responde a los comentarios C10 (cambio de contraseña) y C12 (tabla de errores) del informe. Por pedido explícito del
equipo (09-11-2026) incluye además dos ítems de S7: el límite de intentos con bloqueo de login y la revisión OWASP
Top 10. El resto de S7–S8 sigue pendiente. El login se mantiene con **RUT y contraseña**.

### Cuentas y contraseñas
- Migración `c9a3e1d8f709` (reversible): `users.must_change_password`, `password_changed_at`,
  `failed_login_attempts` (CHECK ≥ 0) y `locked_until`. Los usuarios existentes no quedan obligados a cambiar la
  contraseña al migrar.
- Política de contraseñas (`password_policy.py`): mínimo `PASSWORD_MIN_LENGTH` (10), letras y números, distinta de
  la actual, sin el RUT y fuera de una lista de contraseñas comunes. Se aplica al crear, restablecer y cambiar, y en
  `init_user.py` y el seed.
- `POST /auth/change-password` (contraseña actual + nueva): audita `PASSWORD_CHANGE` (con `forced`) o
  `PASSWORD_CHANGE_FAIL` (con su motivo, nunca la contraseña), con un máximo de 5 intentos por minuto. Devuelve un
  token nuevo.
- **Revocación de sesiones:** el token lleva una marca (`pwd`) de la última contraseña. Cambiarla o que el ADMIN la
  restablezca invalida los tokens anteriores (401).
- **Cambio obligatorio:** los usuarios que crea el ADMIN, las contraseñas restablecidas y el primer ADMIN
  (`init_user.py`) quedan con `must_change_password`. Mientras tanto la API solo permite `GET /auth/me` y el cambio
  de contraseña; el resto responde 403 «Debe cambiar su contraseña antes de continuar».
- Los usuarios del seed de desarrollo no quedan obligados (comodidad para las demostraciones).

### Bloqueo de login y límite por IP
- Tras `LOGIN_MAX_FAILED_ATTEMPTS` (5) fallos seguidos, la cuenta se bloquea `LOGIN_LOCKOUT_MINUTES` (15) y responde
  423. Mientras dura el bloqueo no se evalúa la contraseña. Un login correcto reinicia el contador. Se audita como
  `LOGIN_FAIL` con motivo `credenciales`, `bloqueo` o `bloqueado`.
- `POST /admin/users/{id}/unlock` (ADMIN) quita el bloqueo antes de que venza (auditado como UPDATE con `unlock`).
  Restablecer la contraseña también lo quita.
- Límite de `LOGIN_RATE_LIMIT_PER_MINUTE` (10) intentos por IP por minuto (429 con `Retry-After`). Vive en memoria
  por proceso, y el rechazo se audita una vez por ventana (`limite_ip`).
- Con un RUT inexistente igual se calcula un bcrypt, para que el tiempo de respuesta no revele qué RUT tienen cuenta.
- La IP del cliente solo se toma de `X-Forwarded-For` con `TRUST_PROXY_HEADERS=true` (antes se confiaba siempre en
  ese encabezado y se podía evadir el límite).

### Registro de errores (KPI K9)
- Tabla `error_log` (misma migración): `occurred_at`, `method`, `path` (plantilla, sin ids), `status_code`,
  `error_type`, `message`, `location` (archivo:línea), `user_id`, `request_id`.
- El middleware genera un `X-Request-ID` por request. Ante una excepción no controlada registra el error y responde
  500 con un mensaje genérico que incluye el código. Las respuestas 5xx también se registran.
- El mensaje se sanea: sin SQL ni parámetros, sin `DETAIL` de PostgreSQL, con RUT, emails, números y valores entre
  comillas reemplazados, y truncado a 500 caracteres.
- `GET /admin/errors` (filtros por fecha, tipo y código, con paginación) y `GET /admin/errors/types` (solo ADMIN).
- Dashboard: `server_errors` y `server_error_rate` (proporción sobre las requests medidas).

### Revisión OWASP Top 10
Detalle en `docs/seguridad_owasp.md`. Además de lo anterior:
- `SECRET_KEY` de al menos 32 caracteres (la API no arranca con una más corta).
- JWT con **PyJWT** en lugar de `python-jose`, que tiene una vulnerabilidad sin corrección (igual que `ecdsa`, que
  llega con ella). Algoritmo fijo y claims obligatorios. Se agregó una prueba de que un token `alg: none` se rechaza.
- Dependencias actualizadas por vulnerabilidades conocidas: FastAPI 0.115.0 → 0.135.4 con starlette 1.10.0 (fijada
  aparte), python-multipart 0.0.33, Pillow 13.0.0, jsPDF 4.2.1, jspdf-autotable 5.0.9 y black 26.10.1. Se eligió
  FastAPI 0.135.4 porque las versiones siguientes cambian la estructura interna de las rutas incluidas, lo que
  rompía la plantilla de ruta de las métricas y `gen_docs`. `pip-audit` y `npm audit --omit=dev` quedan en 0.
- Encabezados de seguridad en todas las respuestas (nosniff, `X-Frame-Options`, `Referrer-Policy`,
  `Permissions-Policy`, HSTS, `Cache-Control: no-store`, CSP restrictiva en las respuestas JSON), CORS limitado a
  `Authorization` y `Content-Type`, `/docs` configurable con `ENABLE_API_DOCS`, y largo máximo del RUT y la
  contraseña en el login.

### Frontend
- Pantalla de cambio de contraseña obligatorio (antes de mostrar la aplicación) y opción «Contraseña» en el
  encabezado. Muestra las reglas de la política mientras se escribe.
- Panel de administración: la contraseña inicial pasa a llamarse temporal (mín. 10 caracteres). Se agregan los
  estados «Bloqueado · desbloquear» y «Cambio de contraseña pendiente», la acción «Restablecer» y la pestaña
  «Errores», con filtros por tipo y fecha. La bitácora suma `PASSWORD_CHANGE` y `PASSWORD_CHANGE_FAIL`.
- Dashboard: tarjeta «Errores del servidor (5xx)».

### Otros
- `requirements-dev.txt`: `pgserver` solo para Python < 3.13. El README explica cómo usar `TEST_DB_DSN`.
- `scripts/gen_docs.py`: reconoce `get_authenticated_user` y documenta `error_log`. Se regeneraron `endpoints.md` y
  `modelo_datos.md`.
- `init_db.py`: imports ordenados (`ruff`).
- Versión 2.3.0 (API y `package.json`).

### Pruebas
- 35 tests nuevos (`test_account_security.py`) y ajuste de `test_auth.py` a PyJWT. Total: **241 tests aprobados,
  cobertura 97 %**. Migración probada con `downgrade -1` / `upgrade`.
- Flujo en el navegador (Playwright): cambio obligatorio del ADMIN, alta de usuario, bloqueo, desbloqueo, vista de
  errores y PDF generado con jsPDF 4.

### Pendiente (para confirmar con el equipo)
- **Rotar las credenciales expuestas del Sprint 1.** Sigue pendiente y no depende del código.
- Escaneo dinámico con OWASP ZAP, límite por IP en un almacén compartido si hay réplicas, CSP del sitio del frontend
  y avisos de `npm audit` en las herramientas de desarrollo (exigen subir Vite a una versión mayor). Todo esto va
  en S7.

---

## 2.4.0 — Cumplimiento de la Ley 21.719 (derechos de los titulares y consentimiento versionado)

Pedido del equipo (10-11-2026): el informe declara cumplir la Ley 19.628, y la Ley 21.719 entra en vigencia el
1-12-2026. Se revisó la plataforma contra ambas y contra la Ley 20.584, y se implementó lo que faltaba en el código.
El análisis completo está en `docs/cumplimiento_legal.md`: matriz de cumplimiento, evaluación de impacto,
procedimiento ante vulneraciones, conservación y transferencia internacional.

### Backend
- Migración `c1d4f2a8e910` (reversible):
  - `consent_texts`: versiones inmutables del texto, con una sola activa (índice único parcial). Se crea la
    `2026-11-v1`.
  - `patient_consent_events`: historial de otorgamiento y retiro con la versión aceptada.
  - `patients.consent_text_id`, `blocked_at`, `blocked_by` y `block_reason`.
  - `data_subject_requests`: tipo, estado, fecha de recepción y vencimiento, respuesta, quién registró y quién
    resolvió.
- **Decisión sobre datos existentes:** los pacientes con consentimiento previo reciben un evento `OTORGADO` **sin
  versión de texto** («Registrado antes de la versión 2.4.0»). No se inventa una versión que no vieron, y la interfaz
  sugiere registrarlo de nuevo.
- **Consentimiento versionado:** `POST /patients` exige `consent_text_version` igual al texto vigente (422 si falta,
  409 si está obsoleto). `GET /privacy/consent-text` y `GET /privacy/consent-texts/{version}` lo entregan. El texto
  vive en `app/services/consent_text.py`, y la migración guarda una copia congelada (un test verifica que coincidan).
- **Retiro** (`POST /patients/{id}/consent/withdraw`) y **nuevo registro** (`POST /patients/{id}/consent`): el retiro
  bloquea casos e imágenes nuevos (409). Los casos abiertos pueden terminar y la ficha se conserva. El motivo va al
  historial, no a la auditoría. `PUT /patients` ya no cambia el consentimiento (422).
- **Bloqueo** (`POST /patients/{id}/block` y `unblock`), en lugar de la supresión mientras la ficha deba
  conservarse:
  - Exige casos cerrados y un motivo.
  - Un paciente bloqueado no aparece en las búsquedas (salvo con `include_blocked=true`), no se edita y no admite
    casos nuevos.
- **Exportación** (`GET /patients/{id}/export`, solo MEDICO, audita `EXPORT`): JSON con paciente, historial de
  consentimiento, casos, historial de triage, imágenes (metadatos, sin la ruta interna), IA, validación médica,
  revisión, reportes y solicitudes.
- **Solicitudes de los titulares:**
  - `POST /patients/{id}/requests`, `GET /privacy/requests` (filtros por estado, vencidas y paciente) y
    `PATCH /privacy/requests/{id}`.
  - Vencimiento automático a 30 días corridos. Transiciones válidas y respuesta obligatoria al resolver o rechazar.
  - `GET /privacy/requests/summary` da al ADMIN los conteos y las vencidas, sin datos de pacientes.
- Auditoría: `CONSENT_GRANT`, `CONSENT_WITHDRAW`, `BLOCK` y `UNBLOCK`. Las solicitudes se auditan como
  CREATE/UPDATE, sin el detalle.

### Frontend
- Registro de paciente: muestra el texto de consentimiento vigente completo, con su versión, y la envía al registrar.
- Nueva sección **«Privacidad»** (MEDICO y ADMINISTRATIVO):
  - Lista de solicitudes con filtro por estado, marca de vencidas y acciones «En proceso», «Resolver» y «Rechazar».
  - Vista por paciente con el estado del consentimiento, su historial y las acciones: retirar, registrar con el texto
    vigente, bloquear o levantar el bloqueo, exportar en JSON (solo MEDICO) y registrar solicitudes.
- Panel de ADMIN: resumen de las solicitudes y nuevas acciones en el filtro de la bitácora.

### Pruebas
- 16 tests nuevos (`test_privacy.py`) y una prueba de migración con datos previos (`test_migrations.py`). Total:
  **258 tests aprobados, cobertura 97 %**. Migración probada con `downgrade -1` / `upgrade`.
- Flujo en el navegador (Playwright), sin errores de consola: registro con el texto, solicitud, exportación, retiro,
  bloqueo, resolución y resumen del ADMIN.

### Pendiente (para confirmar con el equipo)
Ver la sección 7 de `docs/cumplimiento_legal.md`: validar el texto v1, acceso por equipo tratante (Ley 20.584),
plazos de conservación y la tarea de anonimización, región de la nube y DPA, y volver a registrar el consentimiento
de los pacientes anteriores a la 2.4.0.

---

## Sprint 7 — Seguridad e infraestructura: preparación del despliegue en AWS (2.5.0)

Pedido del equipo (10-11-2026): rotar las credenciales expuestas y dejar todo listo para desplegar en AWS. El
equipo también **validó `docs/cumplimiento_legal.md`** y el texto de consentimiento v1. No se desplegó nada: no hay
credenciales de AWS en el proyecto. La guía paso a paso está en `docs/despliegue_aws.md`.

### Rotación de las credenciales expuestas
- `scripts/rotate_secrets.py` rota los tres secretos que quedaron en el historial público:
  - Genera una `SECRET_KEY` nueva, que cierra todas las sesiones.
  - Genera una `ENCRYPTION_KEY` nueva y **vuelve a cifrar cada imagen**.
  - Con `--db-password`, cambia la contraseña del rol de PostgreSQL de `DB_DSN`.
- Cómo protege los datos:
  - Verifica antes de tocar nada (`--dry-run`) y nunca imprime los valores.
  - Es reanudable: mientras dura, `.env` guarda `ENCRYPTION_KEY_PREVIOUS` y la API descifra con cualquiera de las
    dos claves (`MultiFernet`).
  - El `ALTER ROLE` solo se confirma después de guardar el DSN nuevo.
  - Deja una copia del `.env` anterior (permisos 600) para recuperar en caso de error.
- **La rotación se ejecuta en cada instalación** (`backend/.env` de cada integrante). Los valores reales no están en
  este entorno. Instrucciones en el README, en «Rotación de secretos».
- Limpiar el historial de Git (`filter-repo` + `force push`) **no se hizo** (regla 9). Con los secretos rotados, los
  valores del historial dejan de servir.

### Almacenamiento
- `StorageBackend` separa el cifrado (Fernet, en la aplicación) del medio donde se guarda: `write_raw`, `read_raw`,
  `iter_keys` y `rotate`. La escritura local es atómica.
- **`S3EncryptedStorage`** (boto3): cifrado en la aplicación y además **SSE-KMS** en S3, con clave KMS propia
  opcional. Se elige con `STORAGE_BACKEND=local|s3`, y lo configuran `S3_BUCKET`, `S3_PREFIX`, `S3_KMS_KEY_ID` y
  `AWS_REGION`. Las credenciales salen del rol de la instancia, nunca de `.env`.

### Contenedores
- `backend/Dockerfile`:
  - Python 3.12.16-slim, usuario sin privilegios y healthcheck.
  - Migraciones al iniciar (`RUN_MIGRATIONS`) y `ENABLE_API_DOCS=false` por defecto.
  - `--root-path /api`.
- `Dockerfile` (raíz): build de Vite con `VITE_API_URL=/api` y una imagen **Caddy** que sirve el sitio y hace de
  proxy hacia la API en el mismo dominio. Esto quita la necesidad de CORS y le da al sitio **TLS automático** con
  Let's Encrypt, con su propia CSP y encabezados de seguridad.
- `docker-compose.yml` (local: PostgreSQL + API + sitio en `:8080`) y `deploy/docker-compose.prod.yml`:
  - puertos 80 y 443;
  - logs a **CloudWatch** (`awslogs`);
  - `restart: always`;
  - dominio y origen obligatorios.
- Imágenes base desde `public.ecr.aws/docker/library`, que no tiene el límite de descargas de Docker Hub.
- `deploy/.env.example` (todas las variables comentadas), `deploy/backup_db.sh` (respaldo diario de PostgreSQL a S3
  con SSE-KMS), `deploy/aws/iam-policy-ec2.json` (permisos mínimos para S3, KMS y CloudWatch) y
  `deploy/aws/ec2-user-data.sh` (Docker, Compose y swap en Amazon Linux 2023).

### GitHub Actions
- `ci.yml` (cada PR y push a `main`):
  - Backend: ruff, pytest con PostgreSQL 16 (cobertura mínima 90 %) y pip-audit.
  - Frontend: lint, typecheck, build y `npm audit`.
  - Docker: build de las imágenes, `compose up` y prueba de humo de `/api/health` y de los encabezados.
- `publish.yml`: publica las imágenes **amd64/arm64** en ghcr.io al crear un tag `vX.Y.Z`. El servidor solo hace
  `docker compose pull`, sin compilar.
- `zap.yml`: escaneo **OWASP ZAP baseline** a pedido sobre el stack completo, con el informe como artefacto.

### Correcciones que salieron al probar con Docker
- **`httpx` estaba solo en `requirements-dev.txt`**, pero `app/inference/providers.py` lo importa: la API no habría
  arrancado en producción. Se movió a `requirements.txt`.
- El sitio cargaba la fuente Inter desde **Google Fonts**, lo que enviaba la IP de cada usuario a un tercero y la CSP
  lo bloqueaba. Se quitó y se usa la fuente del sistema.

### Pruebas
- 12 tests nuevos:
  - `test_rotate_secrets.py`: `.env`, imágenes, reanudación, simulación, archivo ilegible y contraseña de
    PostgreSQL.
  - `test_storage_s3.py`: S3 y KMS simulados con moto.
- Total: **270 tests aprobados, cobertura 97 %**. `pip-audit` y `npm audit --omit=dev` sin hallazgos.
- Stack Docker probado en este entorno:
  - Imagen del backend construida.
  - Sitio servido por la imagen de Caddy con el build local. La imagen `node` no se pudo descargar aquí; el
    `Dockerfile` completo lo construye CI.
  - Configuración de Caddy validada y `compose config` de producción verificado.
  - Flujo completo en el navegador a través de Caddy: cambio obligatorio de contraseña, alta de usuario, paciente
    con consentimiento, caso e imagen subida y mostrada.
  - Sin errores de CSP; archivo cifrado en el volumen; IP real del cliente en la auditoría.

### Pendiente
- Ejecutar el despliegue siguiendo `docs/despliegue_aws.md`. Necesita la cuenta de AWS y un dominio.
- Correr el workflow ZAP y revisar los hallazgos.
- Rotar los secretos en cada instalación existente.

---

## 2.5.1 — Despliegue ajustado al proyecto de AWS (us-east-2, costo mínimo)

- El proyecto de AWS del equipo usa la nueva experiencia de AWS: plan gratuito con USD 100 de créditos hasta el
  10-05-2027 y región fija en `us-east-2` (Ohio), asignada por la dirección de contacto. Se verificó con el AWS CLI:
  `sa-east-1` responde «no autorizado» y la región de Chile no aparece.
- Valores por defecto: `AWS_REGION=us-east-2` (config, `.env.example`, logs de CloudWatch).
- `docs/despliegue_aws.md` con costo mínimo, ≈ USD 11 al mes descontados de los créditos:
  - `t4g.micro` con swap y disco de 10 GB;
  - clave administrada por AWS `aws/s3` (sin el USD 1 al mes de una clave propia);
  - `sslip.io` como dominio gratuito;
  - pasos de la nueva experiencia (AWS Settings, *team members*, créditos y presupuesto).
- `deploy/aws/iam-policy-ec2.json` ya no incluye permisos de KMS: la clave `aws/s3` los da por sí misma.
- `docs/cumplimiento_legal.md`: la ley no exige alojar en Chile. La demostración usa `us-east-2` solo con datos
  ficticios. Para el piloto con datos reales se elige entre la región de Chile (funciones avanzadas), `us-east-2` con
  DPA o la instalación local.
- `CLAUDE.md`: reglas del AWS Agent Toolkit para la nueva experiencia de AWS.

---

## Sprint 8 (parte 1) — Modelo de IA real como prototipo, en un PC con GPU y movible a AWS (2.6.0)

Pedido del equipo (10-11-2026): integrar el servicio de inferencia de Juan Meneses (`backend/inference_service/`:
CNN ResNet18 + YOLO11s) con la **opción B**. La plataforma queda en AWS (≈ USD 11 al mes, de los créditos) y el
modelo corre en el PC de Juan con GPU, conectado por Tailscale, **programado para poder moverse a AWS** cambiando
solo `INFERENCE_URL`.

### Plataforma (backend)
- `HttpInferenceProvider` (antes `HttpYoloProvider`, que se mantiene como alias):
  - Envía `Authorization: Bearer INFERENCE_API_TOKEN`, con un tiempo máximo configurable
    (`INFERENCE_TIMEOUT_SECONDS`, 60).
  - Valida el contrato: campos obligatorios y `confidence` en 0–100.
- `FallbackProvider` (`INFERENCE_FALLBACK_SIMULATED=true`): si el modelo no responde, la imagen se analiza con la IA
  simulada, con su marca y un mensaje que lo explica. La plataforma nunca queda sin resultado.
- `POST /cases/{id}/images/{id}/inference/retry` (MEDICO): vuelve a analizar con el modelo real una imagen que quedó
  con el respaldo simulado. No reemplaza resultados validados por el médico. Responde 503 si el modelo sigue
  apagado. Recalcula el triage y queda auditado.
- `GET /inference/status` (todos los roles, sin datos de pacientes): proveedor, si el modelo responde, versión,
  dispositivo y si está validado clínicamente.
- Migración `d2e7b3c9a011` (reversible): `inference_results.clinically_validated` (false).
- El triage agrega `ai_is_prototype` y los metadatos del reporte agregan `AIIsPrototype`. Este último **solo cuando
  hay resultados del prototipo**, para que los reportes ya firmados conserven su hash y su firma siga válida.

### Servicio del modelo (`backend/inference_service/`)
- Token obligatorio cuando `INFERENCE_API_TOKEN` está definido, con comparación en tiempo constante. Límite de
  tamaño y `/docs` configurable.
- `clinically_validated=false` en `/predict` y `/health`.
- Pesos de la CNN cargados con `weights_only=True`.
- Dependencias alineadas con el backend (FastAPI 0.135.4, starlette 1.10.0, python-multipart 0.0.33; antes tenía
  las versiones vulnerables) y `opencv-python-headless`.
- `Dockerfile` único: CPU por defecto (AWS) o CUDA con `--build-arg TORCH_INDEX=...cu124` (PC de Juan).
  `docker-compose.gpu.yml` para el PC.
- Perfil `inference` en el `docker-compose.yml` de la raíz (opción «todo en AWS»). `publish.yml` publica también la
  imagen `-inference`.
- Imports ordenados (ruff) en la integración anterior. No se cambió la lógica del modelo.

### Interfaz
- Badge **«MODELO PROTOTIPO — NO VALIDADO»** en los resultados del modelo real, en el triage y en el PDF (franja y
  tablas). La IA simulada mantiene «IA SIMULADA».
- Cajas de YOLO dibujadas sobre la imagen real (antes quedaban corridas en un recuadro 16:9) y también cuando la CNN
  no supera el umbral.
- Botón «Analizar con el modelo» cuando la imagen quedó con el respaldo simulado y el modelo ya responde.
- La carga de imágenes y el inicio indican si el modelo está conectado. Textos de «hoy: simulado» actualizados.

### Documentación
- `docs/inferencia_remota.md`: opción B paso a paso (token, Tailscale sin abrir puertos, firewall, configuración) y
  cómo mover el modelo a AWS (mismo servidor `t4g.medium` o Lambda).
- README del servicio actualizado (token, Docker, contrato, pendientes resueltos).

### Pruebas
- 19 tests nuevos (`test_inference_model.py`), sin PyTorch:
  - Cliente HTTP con token y contrato.
  - Fallas: red, 500, 401, JSON inválido, campos faltantes y `confidence` fuera de rango.
  - Respaldo a la IA simulada y selección del proveedor.
  - Resultado guardado como prototipo, triage y metadatos del reporte.
  - Reanálisis y sus reglas.
  - Estado del modelo.
  - Contrato del servicio con el analizador simulado: token, 400, 413 y 415.
- Total: **289 tests aprobados**. Lint y typecheck limpios.
- La imagen Docker del modelo no se construyó en este entorno (necesita descargar PyTorch). La construye GitHub
  Actions (`publish.yml`).

### Pendiente
- Configurar Tailscale y levantar el servicio en el PC de Juan (`docs/inferencia_remota.md`).
- KPI K5 con AUC ≥ 0,80 y sensibilidad ≥ 0,80, umbral 0,35 como parámetro versionado, y pesos (≈63 MB) fuera de Git.

---

## Pendiente para S8 (no implementado, según la regla 2)
Pruebas de carga con Locust y soporte DICOM en la carga (el servicio del modelo ya lee DICOM; la plataforma
todavía no lo acepta). De S7 queda ejecutar el
despliegue (guía lista) y correr el escaneo ZAP (workflow listo).
