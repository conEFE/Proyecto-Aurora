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
