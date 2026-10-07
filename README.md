# Proyecto Aurora

Plataforma web de apoyo a la **detección temprana y priorización (triage)** de casos sospechosos de cáncer de mama.
Proyecto de título — INACAP. **La plataforma apoya, no reemplaza, el criterio médico.**

> **IA simulada.** El análisis de imágenes usa hoy un proveedor simulado. Todo resultado queda marcado
> `is_simulated = true` y se muestra con el badge **«IA SIMULADA»**. No tiene valor clínico.

## Qué hace

- Registro de pacientes con **consentimiento informado** y RUT validado.
- Casos con código anónimo `AUR-AAAA-NNNNNN`, síntomas, BI-RADS y estados
  `ABIERTO → PRIORIZADO → EN_REVISION → CERRADO`.
- Carga de mamografías/ecografías **cifradas en disco** (Fernet) con SHA-256 e inferencia automática.
- **Triage** por reglas de escalamiento y puntaje ponderado, con desglose por factor, override médico con motivo
  y parámetros versionados que edita el equipo médico.
- Cola priorizada, notificaciones de casos ALTA, revisión médica, reporte PDF con metadatos tipo DICOM y
  dashboard de KPIs.
- JWT firmado, autorización por rol leída desde la BD y **bitácora de auditoría** append-only (Ley 19.628).

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
| Registrar la revisión médica y cerrar el caso | – | ✔ | – |
| Generar reporte PDF | – | ✔ | – |
| Editar parámetros de triage | – | ✔ | – (solo consulta) |
| Ver el dashboard de métricas (agregadas) | ✔ | ✔ | ✔ |

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
| `SECRET_KEY` | ✔ | Clave de firma de los JWT. La API no arranca sin ella. `python -c "import secrets; print(secrets.token_urlsafe(48))"` |
| `ENCRYPTION_KEY` | ✔ | Clave Fernet de las imágenes: `python generate_key.py` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | | Validez del token (30) |
| `ALLOWED_ORIGINS` | | Orígenes CORS separados por coma |
| `FILES_DIR` | | Carpeta de imágenes cifradas (`./data/images`) |
| `MAX_UPLOAD_MB` | | Tamaño máximo de imagen (60) |
| `INFERENCE_PROVIDER` | | `simulated` (por defecto) o `http` |
| `INFERENCE_URL` | | URL del servicio YOLO si `INFERENCE_PROVIDER=http` |
| `ALTA_PENDING_HOURS` | | Umbral de casos ALTA pendientes en el dashboard (24) |

Cree el esquema y el primer administrador (credenciales solo por variables de entorno):

```bash
python init_db.py                # crea la base si no existe
alembic upgrade head
set AURORA_ADMIN_RUT=12345678-5
set AURORA_ADMIN_EMAIL=admin@hospital.cl
set AURORA_ADMIN_NAME=Administrador
set AURORA_ADMIN_PASSWORD=...    # mínimo 8 caracteres
python init_user.py
uvicorn app.main:app --reload --port 8000
```

Documentación interactiva de la API: <http://localhost:8000/docs>.

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

## Pruebas y calidad

```bash
cd backend
pytest --cov=app                 # BD aislada: TEST_DB_DSN o PostgreSQL embebido (pgserver)
ruff check app scripts
cd ..
npm run lint && npm run typecheck
```

Resultados del cierre del Sprint 6: 178 tests aprobados y 96% de cobertura (`docs/resultados_tests.md`).

## Documentación

| Documento | Contenido |
|---|---|
| `docs/ESPEC_AGENTE_Aurora_alineacion_sprints.md` | Especificación rectora (S1–S8) |
| `docs/CHANGELOG_SPRINTS.md` | Qué se hizo en cada sprint y decisiones tomadas |
| `docs/modelo_datos.md` | Diccionario de datos y diagrama ER (generado: `python -m scripts.gen_docs`) |
| `docs/endpoints.md` | Endpoints con roles permitidos (generado) |
| `docs/resultados_tests.md` | Salida de pytest y cobertura |
| `docs/stack.md` | Versiones exactas y propósito de cada dependencia |

## Seguridad

- Las credenciales que estuvieron versionadas en la v1.0 (`backend/.env`, `backend/create_user.sql`) siguen en el
  historial de Git: **deben rotarse** (ver `docs/CHANGELOG_SPRINTS.md`, Sprint 1).
- Use solo datos ficticios y RUT de prueba fuera de producción.
