# Especificación para agente de código — Proyecto Aurora

**Objetivo:** llevar el repositorio `conEFE/Proyecto-Aurora` (commit "Proyecto Aurora - Versión 1.0", 23-11-2025) al estado que describen los informes del proyecto: Sprints 1 a 6 del cronograma, con el Sprint 6 cerrando el 15-10-2026.
**Fuente de verdad:** los informes del proyecto (Informe 1 de Proyecto de Título, Informe 4 de Gestión de Proyectos y avance ES2). Cuando el código y los informes no coinciden, manda el informe.
**Idioma:** el código y los identificadores siguen en inglés, como hoy. Los textos de la interfaz y los mensajes al usuario van en español.

---

## 0. Reglas para el agente

1. Trabaja en una rama nueva (`feature/alineacion-sprints`) y haz **un commit o PR por sprint**, con mensajes del tipo `sprint-3: estados de caso y antecedentes clínicos`. No reescribas el historial de Git sin aprobación explícita del equipo.
2. Implementa en orden **S1 → S6**. Al terminar cada sprint: corre las migraciones, los tests y el lint, y deja un resumen en `docs/CHANGELOG_SPRINTS.md`. **No avances a S7–S8** (sección 9) hasta que el equipo lo pida.
3. Usa **Alembic** para todo cambio de esquema. Nunca uses `create_all` en producción. Cada migración debe ser reversible (`downgrade`).
4. **La inferencia de IA sigue siendo simulada** en esta etapa. Está prohibido presentar resultados simulados como si fueran reales. Todo resultado simulado debe quedar marcado en la base de datos (`is_simulated = true`) y en la interfaz (badge visible "IA SIMULADA").
5. No inventes datos clínicos de pacientes reales. Los seeds y fixtures usan datos ficticios y RUT de prueba.
6. Si una instrucción de este documento entra en conflicto con el código de una forma no prevista, detente y repórtalo en el CHANGELOG en vez de improvisar.

---

## 1. Estado actual (diagnóstico)

| Área | Estado actual | Problema |
|---|---|---|
| Autenticación | El token es el string `"RUT-ROL"`, sin firma (`rutas_auth.py`, línea ~90) | Cualquiera puede falsificarlo |
| Autorización | `rbac.require_role` lee el rol **desde el token**, no desde la BD | Escalamiento de privilegios trivial (`Bearer 1-ADMIN`) |
| Registro | `/auth/signup` es público y permite elegir rol `ADMIN` | Cualquiera se crea una cuenta de administrador |
| Secretos | `backend/.env` y `backend/create_user.sql` (con contraseña) están versionados en un repo público | Exposición de credenciales |
| CORS | Orígenes fijos en `main.py`, ignora `settings.ALLOWED_ORIGINS` | Configuración no portable |
| Roles | Solo `MEDICO` y `ADMIN` | Los informes definen 3 roles (falta `ADMINISTRATIVO`) |
| Casos | Sin estado; `patient_id` puede ser nulo | El flujo de proceso (BPMN) requiere estados y que todo caso tenga paciente |
| Triage | No existe. Solo `inference_results` por imagen, con datos aleatorios | Falta el módulo central (RF05) |
| Revisión médica | No existe | El proceso de negocio incluye "registro de resultado/diagnóstico" |
| Reportes | El PDF se genera en el navegador (jsPDF) y no queda registro | Falta trazabilidad (RF06 + SC-02 DICOM básico) |
| Auditoría | No existe | RNF05 y la Ley 19.628 (registro de accesos) la exigen |
| Consentimiento | No existe | El Informe Final exige consentimiento registrado antes de cargar un caso |
| Imágenes | Límite de 10 MB | INC-04 menciona mamografías >50 MB |
| Tests | La carpeta `app/tests` está vacía | Sin evidencia para el plan de pruebas |
| Frontend | Dependencia `@supabase/supabase-js` sin uso | Ruido en el stack |

---

## 2. Decisiones de diseño asumidas

Las marcadas con ⚠️ quedan **pendientes de confirmación del equipo**. El agente debe implementarlas así y dejarlas parametrizables donde se indica.

| # | Decisión | Detalle |
|---|---|---|
| D1 | Se mantienen IDs `INTEGER` autoincrementales | No se migra a UUID; el informe se ajustará al código |
| D2 | 3 roles: `ADMIN`, `MEDICO`, `ADMINISTRATIVO` | Matriz de permisos en la sección 3 |
| D3 | ⚠️ Triage **por caso** (no por imagen) | Agrega las imágenes del caso; la inferencia sigue siendo por imagen |
| D4 | ⚠️ 3 niveles de triage: `ALTA`, `MEDIA`, `BAJA` | Umbrales configurables |
| D5 | ⚠️ Los parámetros de triage los edita el rol `MEDICO` | Cada cambio crea una nueva versión y queda auditado; `ADMIN` solo los consulta |
| D6 | Triage basado en reglas + puntaje ponderado | La IA es una entrada más del puntaje, no decide sola (sección 5) |
| D7 | El médico puede sobrescribir el nivel (override) | Motivo obligatorio y registro en la auditoría |
| D8 | El PDF se sigue generando en el frontend (jsPDF) | El backend registra los metadatos de cada reporte generado |
| D9 | Almacenamiento local cifrado (Fernet) detrás de una interfaz | Permite pasar a S3 en el Sprint 7 sin tocar los endpoints |
| D10 | El servicio de inferencia queda detrás de una interfaz (`InferenceProvider`) | Hoy usa `SimulatedProvider`; mañana `HttpYoloProvider` (`INFERENCE_URL`) |
| D11 | Mínimo privilegio: `ADMIN` no accede a datos clínicos | Coherente con la sección de normativa del Informe Final |

---

## 3. Matriz de permisos (objetivo)

| Acción | ADMINISTRATIVO | MEDICO | ADMIN |
|---|:-:|:-:|:-:|
| Crear y editar usuarios, asignar roles | – | – | ✔ |
| Ver la bitácora de auditoría | – | – | ✔ |
| Registrar y editar pacientes (con consentimiento) | ✔ | ✔ | – |
| Crear casos y registrar antecedentes/síntomas | ✔ | ✔ | – |
| Cargar imágenes a un caso | ✔ | ✔ | – |
| Ver imágenes | – | ✔ | – |
| Ver el detalle del triage y los resultados de IA | – | ✔ | – |
| Ver la cola priorizada (solo código de caso + nivel) | ✔ | ✔ | – |
| Override de triage | – | ✔ | – |
| Registrar la revisión médica y cerrar el caso | – | ✔ | – |
| Generar reporte PDF | – | ✔ | – |
| Editar parámetros de triage | – | ✔ | – |
| Ver el dashboard de métricas (agregadas) | ✔ | ✔ | ✔ |

Implementación: dependencia `require_roles(*roles)` que obtiene el usuario **desde la BD** usando el `sub` del JWT y verifica `user.role` y `user.is_active`.

---

## 4. Modelo de datos objetivo

Las tablas y campos marcados con **(nuevo)** no existen hoy.

### users
| Campo | Tipo | Restricción |
|---|---|---|
| id | INTEGER | PK |
| rut | VARCHAR(12) | UNIQUE, NOT NULL |
| email | VARCHAR(150) | UNIQUE, NOT NULL |
| full_name **(nuevo)** | VARCHAR(150) | NOT NULL |
| password_hash | VARCHAR | NOT NULL (bcrypt) |
| role | ENUM(ADMIN, MEDICO, ADMINISTRATIVO) | NOT NULL |
| is_active **(nuevo)** | BOOLEAN | DEFAULT true |
| created_at **(nuevo)** | TIMESTAMPTZ | DEFAULT now() |
| last_login_at **(nuevo)** | TIMESTAMPTZ | NULL |

### patients
| Campo | Tipo | Restricción |
|---|---|---|
| id | INTEGER | PK |
| rut | VARCHAR(12) | UNIQUE, NOT NULL, validar dígito verificador |
| first_name, last_name | VARCHAR(100) | NOT NULL **(hoy nullable)** |
| birth_date | DATE | NOT NULL **(hoy nullable)** |
| sex | VARCHAR(1) | CHECK IN ('F','M','O') |
| medical_history | TEXT | NULL |
| family_history_first_degree **(nuevo)** | BOOLEAN | DEFAULT false |
| previous_breast_cancer **(nuevo)** | BOOLEAN | DEFAULT false |
| consent_given **(nuevo)** | BOOLEAN | NOT NULL, DEFAULT false |
| consent_at **(nuevo)** | TIMESTAMPTZ | NULL |
| consent_registered_by **(nuevo)** | INTEGER | FK → users.id |
| created_by **(nuevo)** | INTEGER | FK → users.id |
| created_at | TIMESTAMPTZ | DEFAULT now() |

Regla: no se puede crear un caso para un paciente con `consent_given = false` (HTTP 409).

### cases
| Campo | Tipo | Restricción |
|---|---|---|
| id | INTEGER | PK |
| code | VARCHAR(20) | UNIQUE, NOT NULL (código anónimo, ej. `AUR-2026-000123`) |
| patient_id | INTEGER | FK → patients.id, **NOT NULL** (hoy nullable) |
| created_by **(renombrar `medico_id`)** | INTEGER | FK → users.id |
| assigned_medico_id **(nuevo)** | INTEGER | FK → users.id, NULL |
| status **(nuevo)** | ENUM | ver estados abajo |
| palpable_mass **(nuevo)** | BOOLEAN | DEFAULT false |
| nipple_discharge **(nuevo)** | BOOLEAN | DEFAULT false |
| skin_or_nipple_changes **(nuevo)** | BOOLEAN | DEFAULT false |
| birads_reported **(nuevo)** | SMALLINT | NULL, CHECK 0–6 |
| created_at | TIMESTAMPTZ | DEFAULT now() |
| updated_at **(nuevo)** | TIMESTAMPTZ | |
| closed_at **(nuevo)** | TIMESTAMPTZ | NULL |

**Estados del caso** y transiciones permitidas (validar en el servicio y devolver 409 si la transición es inválida):

```
ABIERTO → PRIORIZADO → EN_REVISION → CERRADO
   ↑          │
   └──────────┘  (si se agregan imágenes o antecedentes, se recalcula el triage)
```

- `ABIERTO`: caso creado, aún sin triage.
- `PRIORIZADO`: tiene un triage vigente y está en la cola.
- `EN_REVISION`: un médico lo tomó.
- `CERRADO`: tiene revisión médica registrada. Es de solo lectura.

### images
Se mantienen los campos actuales y se agregan:

| Campo | Tipo | Restricción |
|---|---|---|
| exam_type **(nuevo)** | ENUM(MAMOGRAFIA, ECOGRAFIA, OTRO) | NOT NULL, DEFAULT MAMOGRAFIA |
| laterality **(nuevo)** | VARCHAR(1) | CHECK IN ('L','R'), NULL |
| uploaded_by **(nuevo)** | INTEGER | FK → users.id |
| sha256 **(nuevo)** | VARCHAR(64) | integridad del archivo |

Cambiar el límite de tamaño a `settings.MAX_UPLOAD_MB` (por defecto 60).

### inference_results
Se mantiene y se agrega `is_simulated BOOLEAN NOT NULL DEFAULT true`. `model_version` pasa a NOT NULL.

### triage_configs (nuevo)
| Campo | Tipo | Restricción |
|---|---|---|
| id | INTEGER | PK |
| version | INTEGER | UNIQUE, NOT NULL |
| params | JSONB | NOT NULL (ver sección 5) |
| is_active | BOOLEAN | solo una fila activa |
| created_by | INTEGER | FK → users.id |
| created_at | TIMESTAMPTZ | DEFAULT now() |
| change_reason | TEXT | NOT NULL |

### triage_results (nuevo)
| Campo | Tipo | Restricción |
|---|---|---|
| id | INTEGER | PK |
| case_id | INTEGER | FK → cases.id |
| config_version | INTEGER | FK → triage_configs.version |
| score | NUMERIC(5,2) | 0–100 |
| computed_level | ENUM(ALTA, MEDIA, BAJA) | NOT NULL |
| escalation_rule | VARCHAR(50) | NULL (regla de escalamiento que se disparó) |
| breakdown | JSONB | aporte de cada factor |
| final_level | ENUM(ALTA, MEDIA, BAJA) | = computed_level salvo override |
| override_by | INTEGER | FK → users.id, NULL |
| override_reason | TEXT | obligatorio si hay override |
| is_current | BOOLEAN | solo uno vigente por caso |
| computed_at | TIMESTAMPTZ | DEFAULT now() |

Los resultados anteriores no se borran (`is_current = false`), para mantener historial e integridad.

### clinical_reviews (nuevo)
| Campo | Tipo | Restricción |
|---|---|---|
| id | INTEGER | PK |
| case_id | INTEGER | FK → cases.id, UNIQUE |
| medico_id | INTEGER | FK → users.id |
| birads_final | SMALLINT | CHECK 0–6, NOT NULL |
| findings | TEXT | NOT NULL |
| recommendation | VARCHAR(30) | CHECK IN (CONTROL_RUTINA, CONTROL_6_MESES, ESTUDIO_COMPLEMENTARIO, BIOPSIA, DERIVACION) |
| created_at | TIMESTAMPTZ | DEFAULT now() |

### reports (nuevo)
| Campo | Tipo | Restricción |
|---|---|---|
| id | INTEGER | PK |
| case_id | INTEGER | FK → cases.id |
| generated_by | INTEGER | FK → users.id |
| generated_at | TIMESTAMPTZ | DEFAULT now() |
| dicom_metadata | JSONB | PatientID (= código del caso), StudyDate, Modality=MG, hallazgos (SC-02) |
| content_hash | VARCHAR(64) | SHA-256 del PDF enviado por el frontend |

### audit_log (nuevo)
Tabla **append-only**: sin UPDATE ni DELETE desde la API.

| Campo | Tipo | Restricción |
|---|---|---|
| id | BIGINT | PK |
| user_id | INTEGER | FK → users.id, NULL (login fallido) |
| action | VARCHAR(40) | LOGIN_OK, LOGIN_FAIL, VIEW, CREATE, UPDATE, DOWNLOAD, OVERRIDE, CONFIG_CHANGE, EXPORT |
| entity | VARCHAR(30) | patient, case, image, triage, report, user, triage_config |
| entity_id | INTEGER | NULL |
| ip_address | VARCHAR(45) | |
| detail | JSONB | sin datos sensibles en claro |
| created_at | TIMESTAMPTZ | DEFAULT now() |

Implementar con una función `audit(db, user, action, entity, entity_id, detail)` llamada desde los servicios. **Toda lectura de paciente, imagen o triage registra `VIEW`.**

---

## 5. Módulo de triage (pre-diseño, Sprint 5)

> Es una propuesta técnica para el prototipo, **no un criterio clínico validado**. Los valores por defecto deben ser revisados y ajustados por los médicos usuarios desde la interfaz de configuración.

**Entrada:** caso + paciente + resultados de inferencia de sus imágenes.

### Paso 1 — Reglas de escalamiento directo
Si se cumple cualquiera de estas reglas, el nivel es `ALTA` sin calcular el puntaje:

| Regla | Condición |
|---|---|
| R_BIRADS | `birads_reported` ∈ `escalation.birads_alta` (por defecto [4, 5]) |
| R_SINTOMA | `palpable_mass` o `nipple_discharge` o `skin_or_nipple_changes`, si `escalation.symptoms_alta = true` |

### Paso 2 — Puntaje ponderado (0–100)
Cada factor se normaliza entre 0 y 1 y se multiplica por su peso. Los pesos suman 100.

| Factor | Normalización | Peso por defecto |
|---|---|---|
| IA: máxima `confidence` entre imágenes con `detected = true` | confidence/100; 0 si no hay detección | 40 |
| Edad | 1 si está en [50, 69]; 0,5 si está en [40, 49] o ≥70; 0 en otro caso | 15 |
| Antecedente familiar de primer grado | 1/0 | 15 |
| Cáncer de mama previo | 1/0 | 20 |
| Tiempo de espera desde `created_at` | min(días / `max_wait_days`, 1) | 10 |

### Paso 3 — Umbrales
- `score ≥ thresholds.alta` (por defecto 60) → `ALTA`
- `score ≥ thresholds.media` (por defecto 30) → `MEDIA`
- en otro caso → `BAJA`

### Configuración por defecto (`triage_configs.params`, versión 1)
```json
{
  "escalation": { "birads_alta": [4, 5], "symptoms_alta": true },
  "weights": { "ai": 40, "age": 15, "family_history": 15, "previous_cancer": 20, "wait_time": 10 },
  "age_bands": { "high": [50, 69], "medium": [[40, 49], [70, 120]] },
  "max_wait_days": 30,
  "thresholds": { "alta": 60, "media": 30 }
}
```
Validar con Pydantic que los pesos sumen 100 y que `alta > media`.

### Cuándo se calcula
- Automáticamente al terminar la inferencia de una imagen, al editar antecedentes o síntomas del caso, o al activar una nueva configuración (recalcula los casos no cerrados).
- Manualmente con `POST /cases/{id}/triage`.
- Guardar `breakdown` con el aporte de cada factor, para que el médico vea **por qué** quedó en ese nivel.

### Cola priorizada
Orden: `final_level` (ALTA > MEDIA > BAJA), luego `score` descendente y luego `created_at` ascendente.

### Requisito de KPI
Medir el tiempo desde `cases.created_at` hasta el primer `triage_results.computed_at`. La meta del informe es ≤ 5 minutos.

---

## 6. Plan por sprint

Cada sprint lista **backend**, **frontend** y la **Definición de Hecho (DoD)**. Los tests van en `backend/app/tests/` con pytest, `TestClient` y una BD de pruebas aislada.

### Sprint 1 — Base del sistema (16–31 jul)
**Backend**
- Eliminar `backend/.env` y `backend/create_user.sql` del repo; agregarlos a `.gitignore`; crear `backend/.env.example` sin valores reales. Dejar en el CHANGELOG la nota **"ROTAR credenciales expuestas"**.
- `config.py`: `SECRET_KEY` obligatorio, sin valor por defecto (falla al arrancar si falta); `ACCESS_TOKEN_EXPIRE_MINUTES=30`; `MAX_UPLOAD_MB=60`.
- Autenticación con **JWT HS256** (`python-jose`, ya instalado): claims `sub` (user id), `role`, `exp`, `iat`. Login devuelve `{access_token, token_type, role, full_name}`.
- Reescribir `auth/bearer.py` y `auth/rbac.py`: decodificar el JWT, cargar el usuario desde la BD y verificar `is_active` y el rol con `require_roles(...)`. Eliminar la lógica de `"RUT-ROL"` y las funciones duplicadas.
- CORS desde `settings.ALLOWED_ORIGINS`.
- `/health` sin cambios. Agregar un middleware que envíe el header `X-Process-Time-Ms` y registre la duración de cada request en el log (insumo del KPI de tiempo de respuesta ≤ 3 s).
- Estructura de capas: `app/services/` con la lógica de negocio; las rutas solo validan y delegan.

**Frontend**
- Adaptar `services/api.ts` al nuevo formato de login (`access_token`). Ante un 401, cerrar sesión y volver al login.
- Quitar `@supabase/supabase-js` si se confirma que no se usa.

**DoD:** tests de login correcto e incorrecto, token expirado → 401, token manipulado → 401, y `Bearer 1-ADMIN` → 401.

### Sprint 2 — Usuarios y pacientes (1–15 ago)
**Backend**
- Agregar el rol `ADMINISTRATIVO` (migración del enum) y los campos nuevos de `users`.
- `/auth/signup` deja de ser público: se reemplaza por `POST /admin/users` (solo ADMIN). Agregar `PATCH /admin/users/{id}` (rol, activar/desactivar) y `GET /admin/users`.
- Script `init_user.py`: crea el primer ADMIN leyendo credenciales de variables de entorno, nunca del código.
- Pacientes: campos nuevos, validación de RUT con dígito verificador, consentimiento obligatorio (`consent_given`, `consent_at` y `consent_registered_by` automáticos), `PUT /patients/{id}`.
- Tabla `audit_log` y función `audit(...)`. Registrar LOGIN_OK, LOGIN_FAIL, CREATE/UPDATE/VIEW de pacientes y los cambios de usuarios.
- `GET /admin/audit` (solo ADMIN), con filtros por usuario, acción y fecha, paginado.

**Frontend**
- AdminPanel: CRUD de usuarios con selector de 3 roles y visor de auditoría.
- PatientModal: nuevos campos, checkbox de consentimiento obligatorio con texto explicativo, y validación de RUT.
- Ocultar o eliminar la pantalla pública de Signup.

**DoD:** tests de permisos (un ADMINISTRATIVO no crea usuarios; un ADMIN no ve pacientes), RUT inválido → 422, y escritura en la auditoría verificada.

### Sprint 3 — Casos clínicos y antecedentes (16–31 ago)
**Backend**
- `cases`: `patient_id` NOT NULL (la migración debe manejar filas existentes con NULL: asignarlas a un paciente "SIN-ASIGNAR" de prueba o eliminarlas en entorno de desarrollo, documentando la decisión), `status`, síntomas, `birads_reported` y timestamps.
- Generador de `code` con formato `AUR-AAAA-NNNNNN`.
- Máquina de estados en `services/case_service.py`, con validación de transiciones.
- Endpoints: `POST /cases` (requiere paciente con consentimiento), `GET /cases` (filtros por estado y nivel), `GET /cases/{id}`, `PATCH /cases/{id}` (síntomas y BI-RADS; bloqueado si está CERRADO).
- Auditar VIEW y UPDATE de casos.

**Frontend**
- CaseManagement: creación ligada a un paciente, formulario de síntomas y BI-RADS, badge de estado y filtros.

**DoD:** tests de transiciones válidas e inválidas, caso sin consentimiento → 409, y caso cerrado no editable.

### Sprint 4 — Exámenes e imágenes (1–15 sep)
**Backend**
- Interfaz `StorageBackend` con los métodos `save`, `load` y `delete`, y la implementación `LocalEncryptedStorage` (código actual de `storage/fs.py` + Fernet). Calcular `sha256` del archivo original.
- Agregar `exam_type`, `laterality` y `uploaded_by` en la subida. Límite `MAX_UPLOAD_MB`. Aceptar PNG y JPEG (DICOM queda para S7–S8).
- Interfaz `InferenceProvider.analyze(image_bytes) -> InferenceOutput`, con:
  - `SimulatedProvider`: lógica actual de `rutas_results.py`, pero **sin `time.sleep`**, determinística por `sha256` y con `model_version="simulado-v1"` e `is_simulated=true`.
  - `HttpYoloProvider`: stub que hace POST a `INFERENCE_URL/predict`; se usa si `INFERENCE_PROVIDER=http`.
- Ejecutar la inferencia automáticamente al subir una imagen (BackgroundTasks de FastAPI) y luego disparar el recálculo del triage del caso (el triage se implementa en S5; aquí basta dejar el hook).
- `GET /cases/{id}/images/{image_id}/file`: solo MEDICO; registrar `VIEW` en la auditoría.

**Frontend**
- ImageUpload: selector de tipo de examen y lateralidad, barra de progreso y badge **"IA SIMULADA"** en todo resultado con `is_simulated`.
- Compresión en el cliente opcional (mitigación de INC-04), detrás de un flag.

**DoD:** tests de subida, límite de tamaño, archivo cifrado en disco (no legible sin la clave), ADMINISTRATIVO puede subir pero recibe 403 al ver, e inferencia simulada marcada como tal.

### Sprint 5 — Triage y priorización (16–30 sep)
**Backend**
- Tablas `triage_configs` y `triage_results`; seed de la configuración v1 (sección 5).
- `services/triage_service.py`: función pura `compute_triage(case, patient, inferences, params) -> TriageOutput`, fácil de testear sin BD.
- Endpoints:
  - `POST /cases/{id}/triage`: recalcula el triage.
  - `GET /cases/{id}/triage`: resultado vigente con su `breakdown` (solo MEDICO).
  - `POST /cases/{id}/triage/override` con `{level, reason}`, solo MEDICO; registra `OVERRIDE` en la auditoría.
  - `GET /triage/queue`: cola priorizada. ADMINISTRATIVO solo ve `code`, nivel, estado y antigüedad.
  - `GET /triage/config` (MEDICO y ADMIN) y `POST /triage/config` con `{params, change_reason}`, solo MEDICO. Crea una nueva versión activa y recalcula los casos no cerrados.
- Al calcular, cambiar el caso a `PRIORIZADO`. Si el nivel es `ALTA`, crear una notificación en una tabla simple `notifications` (`user_id`, `case_id`, `message`, `read_at`) para los médicos activos, con `GET /notifications` y `PATCH /notifications/{id}/read`.

**Frontend**
- Vista **Cola de triage**: tabla ordenada con colores por nivel y antigüedad.
- Detalle de triage: desglose por factor, regla disparada y botón de override con motivo obligatorio.
- Panel **Parámetros de triage** (MEDICO): edición de pesos, umbrales y reglas, validación de que los pesos sumen 100, motivo del cambio e historial de versiones.
- Campana de notificaciones para los casos ALTA.

**DoD:** tests unitarios de `compute_triage` que cubran cada regla de escalamiento, cada banda de edad, los límites de umbral (59,99 / 60 / 29,99 / 30), pesos que no suman 100 → 422, override sin motivo → 422 y el orden correcto de la cola. Medir y loguear el tiempo de creación a triage.

### Sprint 6 — Dashboard y reportes (1–15 oct, en curso)
**Backend**
- `POST /cases/{id}/review` (MEDICO): crea `clinical_reviews` y pasa el caso a `CERRADO` con `closed_at`. `POST /cases/{id}/take`: pasa el caso a `EN_REVISION` y asigna el médico.
- `POST /cases/{id}/reports` con `{content_hash}`: registra el reporte y devuelve los `dicom_metadata` que el frontend incrusta en el PDF (SC-02). Registrar `EXPORT` en la auditoría.
- Reemplazar `/reports/statistics` y `/reports/monthly` por `GET /dashboard/metrics?from=&to=`, que devuelve:
  - Volumen de casos por estado y por nivel de triage.
  - Tiempo promedio de creación → triage (KPI ≤ 5 min).
  - Tiempo promedio de triage → revisión, por nivel.
  - Casos ALTA pendientes con más de X horas (configurable).
  - p95 del tiempo de respuesta de la API (desde los logs del middleware de S1, o una tabla `request_metrics` si es más simple).
  - Proporción de overrides sobre el total de triages (señal de calidad del modelo de reglas).
- Eliminar los endpoints viejos de `rutas_results.py` y `rutas_reports.py` que quedaron sin uso, y `rutas_user.py /tickets` si no tiene respaldo en los informes (reportarlo en el CHANGELOG antes de borrar).

**Frontend**
- Dashboard con tarjetas de KPI y gráficos simples (barras por nivel, línea de casos por semana), con filtro de fechas.
- Formulario de revisión médica: BI-RADS final, hallazgos y recomendación.
- `generatePdf.ts`: el PDF incluye datos del caso (con el código anónimo), nivel de triage y su desglose, badge de IA simulada, revisión médica, metadatos tipo DICOM (SC-02), fecha y médico. Calcular el SHA-256 del PDF y registrarlo con `POST /cases/{id}/reports`.

**DoD:** tests del endpoint de métricas con datos de prueba controlados, cierre del caso solo con revisión, reporte registrado y auditado, y un test E2E del flujo completo: crear paciente → caso → imagen → triage → revisión → reporte.

---

## 7. Calidad transversal (aplicar desde S1)

- **Backend:** `ruff` + `black`; tipado con Pydantic v2 en todos los requests y responses; manejo de errores con HTTPException y mensajes en español.
- **Frontend:** `npm run lint` y `npm run typecheck` sin errores.
- **Tests:** `pytest` con cobertura reportada (`pytest-cov`), con meta ≥ 70% en `app/services/`. Agregar `pytest`, `pytest-cov`, `httpx` y `ruff` a `requirements-dev.txt`.
- **Seed de desarrollo** (`backend/scripts/seed_dev.py`): 3 usuarios (uno por rol), 10 pacientes ficticios y casos variados que cubran los 3 niveles de triage.
- **README:** actualizar la instalación, las variables de entorno (`.env.example`), cómo correr los tests y el seed, y la matriz de roles.

---

## 8. Entregables para el informe (el agente debe generarlos)

Al terminar S6, crear en `docs/`:
1. `CHANGELOG_SPRINTS.md`: qué se hizo en cada sprint y las decisiones tomadas.
2. `modelo_datos.md`: diccionario de datos **generado desde los modelos SQLAlchemy finales** (tabla, campo, tipo, restricción y descripción) y un diagrama ER en Mermaid (`erDiagram`).
3. `endpoints.md`: tabla de endpoints con método, ruta, roles permitidos y descripción (se puede exportar desde OpenAPI `/openapi.json`).
4. `resultados_tests.md`: salida resumida de pytest y la cobertura.
5. `stack.md`: versiones exactas de todas las dependencias (backend y frontend) y su propósito.

---

## 9. Siguiente fase — NO implementar hasta que el equipo lo pida

**Sprint 7 — Seguridad e infraestructura (16–31 oct)**
- Dockerfiles (backend, frontend, inferencia) y `docker-compose.yml` para el entorno local.
- GitHub Actions: lint + tests en cada PR, y build de imágenes.
- `S3EncryptedStorage` (boto3 con SSE-KMS) que implemente `StorageBackend`.
- Rate limiting en `/auth/login` y bloqueo tras N intentos fallidos.
- Revisión OWASP Top 10 y escaneo con OWASP ZAP.
- Despliegue de referencia en AWS (EC2, RDS PostgreSQL, S3 y CloudWatch en sa-east-1), según el diagrama de infraestructura del Informe 1.

**Sprint 8 — Integración y estabilización (1–15 nov)**
- `HttpYoloProvider` real (servicio Ultralytics YOLO) si el modelo está disponible; si no, se mantiene el simulado con su marca visible.
- Pruebas de carga con Locust (100 usuarios concurrentes; meta p95 < 3 s).
- Soporte opcional de archivos DICOM (pydicom) en la subida.
