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
