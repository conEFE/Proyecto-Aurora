# Proyecto Aurora

Plataforma web de apoyo a la **detección temprana y priorización (triage)** de casos sospechosos de cáncer de mama.
Proyecto de título — INACAP. **La plataforma apoya, no reemplaza, el criterio médico.**

> **IA simulada.** El análisis de imágenes usa hoy un proveedor simulado. Todo resultado queda marcado
> `is_simulated = true` y se muestra con el badge **«IA SIMULADA»**. No tiene valor clínico.

## Qué hace

- Registro de pacientes con **consentimiento informado versionado** (se guarda qué texto aceptó cada paciente) y
  RUT validado.
- Casos con código anónimo `AUR-AAAA-NNNNNN`, síntomas, BI-RADS y estados
  `ABIERTO → PRIORIZADO → EN_REVISION → CERRADO`.
- Carga de mamografías/ecografías **cifradas en disco** (Fernet) con SHA-256 e inferencia automática.
- **Triage** por reglas de escalamiento y puntaje ponderado, con desglose por factor, override médico con motivo
  y parámetros versionados que edita el equipo médico.
- Cola priorizada, notificaciones de casos ALTA, revisión médica, reporte PDF con metadatos tipo DICOM y
  dashboard de KPIs.
- **Validación médica:** el médico aprueba o rechaza el resultado de IA de cada imagen (concordante, falso
  positivo/negativo) y evalúa el nivel de triage al cerrar el caso. La concordancia se mide en el dashboard.
- JWT firmado, autorización por rol leída desde la BD y **bitácora de auditoría** append-only (Ley 19.628).
- **Derechos de los titulares (Ley 21.719):** retiro del consentimiento, bloqueo de datos (la ficha se conserva por
  la Ley 20.584), copia de los datos en JSON (acceso y portabilidad) y registro de solicitudes con plazo de 30 días.
  Ver `docs/cumplimiento_legal.md`.

## Roles

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
| Validar el resultado de IA y evaluar el triage | – | ✔ | – |
| Registrar la revisión médica y cerrar el caso | – | ✔ | – |
| Generar reporte PDF | – | ✔ | – |
| Editar parámetros de triage | – | ✔ | – (solo consulta) |
| Ver el dashboard de métricas (agregadas) | ✔ | ✔ | ✔ |
| Retirar o registrar consentimiento, bloquear datos, gestionar solicitudes de titulares | ✔ | ✔ | – |
| Exportar todos los datos de un paciente (JSON) | – | ✔ | – |
| Ver el resumen de solicitudes de titulares (sin datos de pacientes) | ✔ | ✔ | ✔ |

## Requisitos

- Python ≥ 3.10, Node.js ≥ 18 y PostgreSQL ≥ 14.

## Instalación

### Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate            # Linux/Mac: source venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt
copy .env.example .env           # Linux/Mac: cp .env.example .env
```

Complete `backend/.env` (nunca se versiona):

| Variable | Obligatoria | Descripción |
|---|:-:|---|
| `DB_DSN` | ✔ | `postgresql+psycopg2://usuario:clave@localhost:5432/aurora` |
| `SECRET_KEY` | ✔ | Clave de firma de los JWT, mínimo 32 caracteres. La API no arranca sin ella. `python -c "import secrets; print(secrets.token_urlsafe(48))"` |
| `ENCRYPTION_KEY` | ✔ | Clave Fernet de las imágenes: `python generate_key.py` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | | Validez del token (30) |
| `ALLOWED_ORIGINS` | | Orígenes CORS separados por coma |
| `FILES_DIR` | | Carpeta de imágenes cifradas (`./data/images`) |
| `MAX_UPLOAD_MB` | | Tamaño máximo de imagen (60) |
| `INFERENCE_PROVIDER` | | `simulated` (por defecto) o `http` |
| `INFERENCE_URL` | | URL del servicio YOLO si `INFERENCE_PROVIDER=http` |
| `ALTA_PENDING_HOURS` | | Umbral de casos ALTA pendientes en el dashboard (24) |
| `PASSWORD_MIN_LENGTH` | | Largo mínimo de contraseña (10) |
| `LOGIN_MAX_FAILED_ATTEMPTS` / `LOGIN_LOCKOUT_MINUTES` | | Bloqueo de la cuenta tras N fallos seguidos, por M minutos (5 / 15) |
| `LOGIN_RATE_LIMIT_PER_MINUTE` | | Intentos de login por IP por minuto (10) |
| `TRUST_PROXY_HEADERS` | | `true` solo detrás de un proxy propio que agrega `X-Forwarded-For` (`false`) |
| `ENABLE_API_DOCS` | | Publica `/docs` y `/openapi.json` (`true`; desactivar en producción) |

Cree el esquema y el primer administrador (credenciales solo por variables de entorno):

```bash
python init_db.py                # crea la base si no existe
alembic upgrade head
set AURORA_ADMIN_RUT=12345678-5
set AURORA_ADMIN_EMAIL=admin@hospital.cl
set AURORA_ADMIN_NAME=Administrador
set AURORA_ADMIN_PASSWORD=...    # temporal: mínimo 10 caracteres, con letras y números
python init_user.py              # el ADMIN deberá cambiarla en su primer ingreso
uvicorn app.main:app --reload --port 8000
```

Documentación interactiva de la API: <http://localhost:8000/docs>.

### Cuentas y contraseñas

- El login es con **RUT y contraseña**. Las cuentas las crea el ADMIN con una contraseña temporal; el usuario debe
  cambiarla en su primer ingreso (hasta entonces la API solo le permite ver su perfil y cambiarla).
- Política: mínimo 10 caracteres, letras y números, distinta de la actual y sin el RUT.
- Cambiar o restablecer una contraseña cierra las demás sesiones (los tokens anteriores dejan de servir).
- Tras 5 intentos fallidos seguidos la cuenta queda bloqueada 15 minutos (el ADMIN puede desbloquearla antes) y cada
  IP tiene un máximo de 10 intentos de login por minuto. Todo queda en la bitácora de auditoría.

### Datos de prueba (opcional)

Crea 3 usuarios (uno por rol), 10 pacientes ficticios y casos en los 3 niveles de triage:

```bash
set AURORA_SEED_PASSWORD=...     # contraseña de los usuarios de prueba
python -m scripts.seed_dev
```

### Frontend

```bash
npm install
copy .env.example .env.local     # VITE_API_URL=http://localhost:8000
npm run dev
```

### Con Docker (todo el sistema)

Requiere Docker con Compose v2. Levanta PostgreSQL, la API y el sitio (Caddy) en <http://localhost:8080>:

```bash
cp deploy/.env.example deploy/.env     # complete POSTGRES_PASSWORD, SECRET_KEY, ENCRYPTION_KEY y AURORA_ADMIN_*
docker compose --env-file deploy/.env up -d --build
docker compose --env-file deploy/.env exec backend python init_user.py
```

La API queda en `/api` (mismo dominio, sin CORS). Despliegue en AWS: `docs/despliegue_aws.md`.

## Pruebas y calidad

```bash
cd backend
pytest --cov=app                 # BD aislada: TEST_DB_DSN o PostgreSQL embebido (pgserver)
ruff check app scripts
cd ..
npm run lint && npm run typecheck
```

La suite crea una base aislada por corrida. Con Python ≤ 3.12 usa PostgreSQL embebido (`pgserver`). Con
Python 3.13 o superior `pgserver` no existe: cree una base vacía en un PostgreSQL local y apúntela con `TEST_DB_DSN`
(las pruebas borran sus datos en cada test; no use una base con datos reales):

```bash
createdb aurora_test
set TEST_DB_DSN=postgresql+psycopg2://usuario:clave@localhost:5432/aurora_test   # Linux/Mac: export
pytest --cov=app
```

Resultados de la versión 2.5.0: 270 tests aprobados y 97% de cobertura (`docs/resultados_tests.md`).

GitHub Actions (`.github/workflows/`) corre lo mismo en cada PR: `ci.yml` (ruff, pytest con PostgreSQL 16,
pip-audit, lint, typecheck, build, npm audit, imágenes Docker y prueba de humo), `publish.yml` (publica las imágenes
en ghcr.io al crear un tag `vX.Y.Z`) y `zap.yml` (escaneo OWASP ZAP a pedido).

## Documentación

| Documento | Contenido |
|---|---|
| `docs/ESPEC_AGENTE_Aurora_alineacion_sprints.md` | Especificación rectora (S1–S8) |
| `docs/CHANGELOG_SPRINTS.md` | Qué se hizo en cada sprint y decisiones tomadas |
| `docs/modelo_datos.md` | Diccionario de datos y diagrama ER (generado: `python -m scripts.gen_docs`) |
| `docs/endpoints.md` | Endpoints con roles permitidos (generado) |
| `docs/resultados_tests.md` | Salida de pytest y cobertura |
| `docs/stack.md` | Versiones exactas y propósito de cada dependencia |
| `docs/seguridad_owasp.md` | Revisión OWASP Top 10 (2021) y controles de seguridad |
| `docs/cumplimiento_legal.md` | Cumplimiento Ley 19.628 / 21.719 / 20.584: matriz, evaluación de impacto, brechas y conservación |
| `docs/despliegue_aws.md` | Despliegue en AWS paso a paso (EC2 + Docker + Caddy + S3/KMS + CloudWatch; variante RDS) |

## Crear ZIP del proyecto para distribución

Desde la raíz del proyecto:

```powershell
.\crear-zip.ps1                  # genera Proyecto-Aurora-Limpio.zip
```

El ZIP incluye el código fuente, la configuración (`package.json`, `requirements.txt`, etc.), los scripts, la
documentación y los `.env.example`. Excluye `node_modules/`, `venv/`, `__pycache__/`, `dist/`, `dist-ssr/`,
`.vscode/`, `.idea/`, los archivos `.env`, `.pyc` y `.log`.

Para instalar desde el ZIP, extráigalo y siga la sección [Instalación](#instalación).

## Seguridad

- Use solo datos ficticios y RUT de prueba fuera de producción.
- Revisión OWASP y controles: `docs/seguridad_owasp.md`. Cumplimiento legal: `docs/cumplimiento_legal.md`.

### Rotación de secretos

Las credenciales que estuvieron versionadas en la v1.0 (`backend/.env` y `backend/create_user.sql`: contraseña del
rol de PostgreSQL, `SECRET_KEY` y `ENCRYPTION_KEY`) siguen en el historial público de Git y **deben rotarse** en
cada instalación que las use. El script lo hace en un paso, sin mostrar los valores nuevos:

```bash
cd backend
python -m scripts.rotate_secrets --dry-run          # 1. verifica que todas las imágenes se pueden descifrar
python -m scripts.rotate_secrets --db-password      # 2. rota (con la API detenida)
```

- Genera una `SECRET_KEY` nueva (cierra todas las sesiones) y una `ENCRYPTION_KEY` nueva, y vuelve a cifrar cada
  imagen. Si se interrumpe, se vuelve a ejecutar: mientras dura, la API lee con la clave nueva o la anterior.
- Con `--db-password`, cambia la contraseña del rol de PostgreSQL de `DB_DSN` y actualiza `.env`. El cambio solo se
  confirma después de guardar el `.env` nuevo.
- Deja `.env.antes-de-rotar-FECHA` para recuperar en caso de error: **bórrelo** después de comprobar que la API
  inicia y muestra las imágenes.
- Si el rol tiene otro nombre en su PostgreSQL (por ejemplo `"Aurora"` de `create_user.sql`) y ya no se usa,
  elimínelo: `DROP ROLE "Aurora";`.
