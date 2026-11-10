# Stack tecnológico — Proyecto Aurora 2.5

Versiones exactas de la 2.5.0 (fijadas en `backend/requirements*.txt` y `package-lock.json`). En la 2.3.0 se
actualizaron las dependencias con vulnerabilidades conocidas (ver `docs/seguridad_owasp.md`, A06).

## Backend (`backend/`)

| Componente | Versión | Propósito |
|---|---|---|
| Python | 3.10+ (probado en 3.11.9 y 3.13) | Lenguaje del backend |
| PostgreSQL | 14+ (probado en 16.2) | Base de datos relacional (JSONB, enums, índices parciales, triggers) |
| fastapi | 0.135.4 | Framework de la API REST y OpenAPI |
| starlette | 1.10.0 | Base ASGI de FastAPI (middleware, BackgroundTasks). Fijada aparte por seguridad |
| uvicorn[standard] | 0.32.0 | Servidor ASGI |
| SQLAlchemy | 2.0.36 | ORM y construcción de consultas |
| alembic | 1.13.2 | Migraciones de esquema reversibles |
| psycopg2-binary | 2.9.10 | Driver de PostgreSQL |
| pydantic | 2.9.2 | Validación de requests/responses y parámetros de triage |
| pydantic-settings | 2.6.0 | Configuración desde variables de entorno / `.env` |
| email-validator | 2.2.0 | Validación de emails de usuarios |
| python-multipart | 0.0.33 | Carga de archivos (multipart/form-data) |
| PyJWT | 2.15.1 | Firma y verificación de JWT HS256 (reemplaza a python-jose, sin corrección para su vulnerabilidad) |
| bcrypt | 5.0.0 | Hash de contraseñas |
| cryptography | 50.0.2 | Cifrado Fernet de las imágenes en disco |
| python-dotenv | 1.2.4 | Carga de `backend/.env` en scripts y Alembic |
| Pillow | 13.0.0 | Validación de formato y dimensiones de imágenes |
| boto3 | 1.43.127 | Cliente de AWS para `S3EncryptedStorage` (S3 con SSE-KMS) |
| httpx | 0.27.2 | Cliente HTTP del `HttpYoloProvider` (y de `TestClient`). Desde la 2.5.0 en `requirements.txt` |

### Desarrollo y pruebas (`requirements-dev.txt`)

| Componente | Versión | Propósito |
|---|---|---|
| pytest | 9.1.1 | Ejecución de pruebas |
| pytest-cov | 7.1.0 | Cobertura |
| moto[s3,kms] | 5.2.5 | S3 y KMS simulados para las pruebas de almacenamiento |
| ruff | 0.16.10 | Linter |
| black | 26.10.1 | Formateo |
| pgserver | 0.1.4 | PostgreSQL embebido para la BD de pruebas aislada (si no hay `TEST_DB_DSN`). Solo Python < 3.13 |

## Frontend (raíz)

| Componente | Versión | Propósito |
|---|---|---|
| Node.js | 18+ (probado en 25.8) | Entorno de build |
| react / react-dom | 18.3.1 | Interfaz de usuario |
| typescript | 5.6.3 | Tipado estático |
| vite | 5.4.21 | Servidor de desarrollo y build |
| @vitejs/plugin-react | 4.3.2 | Soporte React en Vite |
| tailwindcss | 3.4.17 | Estilos utilitarios |
| postcss / autoprefixer | 8.5.32 / 10.4.20 | Procesamiento de CSS |
| lucide-react | 0.344.0 | Íconos |
| jspdf | 4.2.1 | Generación del reporte PDF en el navegador |
| jspdf-autotable | 5.0.9 | Tablas en el PDF |
| eslint / @eslint/js | 9.12.0 | Linter |
| typescript-eslint | 8.8.1 | Reglas de ESLint para TypeScript |
| eslint-plugin-react-hooks | 5.1.0-rc | Reglas de hooks |
| eslint-plugin-react-refresh | 0.4.12 | Reglas de Fast Refresh |
| globals | 15.11.0 | Globales del navegador para ESLint |
| @types/react / @types/react-dom | 18.3.11 / 18.3.0 | Tipos de React |

Se eliminaron `@supabase/supabase-js` (sin uso) y `@types/jspdf` (obsoleto: jsPDF trae sus propios tipos).

## Servicios externos (no incluidos, próximos sprints)

| Componente | Estado | Sprint |
|---|---|---|
| Servicio de inferencia YOLO (Ultralytics) | Interfaz `HttpYoloProvider` lista; hoy se usa `SimulatedProvider` | S8 |
| AWS (EC2, RDS, S3 con SSE-KMS, CloudWatch) | `StorageBackend` preparado para `S3EncryptedStorage` | S7 |
| Docker / GitHub Actions | No implementado | S7 |

## Contenedores y despliegue (2.5.0)

| Componente | Versión | Propósito |
|---|---|---|
| Imagen base de la API | `public.ecr.aws/docker/library/python:3.12.16-slim` | Runtime de la API (usuario sin privilegios) |
| Imagen de build del frontend | `public.ecr.aws/docker/library/node:22-alpine` | `npm ci` y build de Vite |
| Caddy | `public.ecr.aws/docker/library/caddy:2.11-alpine` (2.11.9) | Sitio estático, proxy de `/api`, TLS automático (Let's Encrypt), CSP |
| PostgreSQL | `public.ecr.aws/docker/library/postgres:16-alpine` (16.15) | Base de datos en contenedor (local y demo en EC2) |
| Docker Compose | v2 (probado con 5.6.1) | Orquestación local y en EC2 |
| GitHub Actions | `actions/checkout@v4`, `setup-python@v5`, `setup-node@v4`, `docker/*-action@v3`, `build-push-action@v6`, `upload-artifact@v4` | CI, publicación de imágenes en GHCR y escaneo ZAP |
| OWASP ZAP | `ghcr.io/zaproxy/zaproxy:stable` | Escaneo baseline (workflow a pedido) |
