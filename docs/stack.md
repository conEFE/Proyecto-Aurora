# Stack tecnológico — Proyecto Aurora 2.0

Versiones exactas usadas al cierre del Sprint 6 (fijadas en `backend/requirements*.txt` y `package-lock.json`).

## Backend (`backend/`)

| Componente | Versión | Propósito |
|---|---|---|
| Python | 3.10+ (probado en 3.11.9) | Lenguaje del backend |
| PostgreSQL | 14+ (probado en 16.2) | Base de datos relacional (JSONB, enums, índices parciales, triggers) |
| fastapi | 0.115.0 | Framework de la API REST y OpenAPI |
| starlette | 0.38.6 | Base ASGI de FastAPI (middleware, BackgroundTasks) |
| uvicorn[standard] | 0.32.0 | Servidor ASGI |
| SQLAlchemy | 2.0.36 | ORM y construcción de consultas |
| alembic | 1.13.2 | Migraciones de esquema reversibles |
| psycopg2-binary | 2.9.10 | Driver de PostgreSQL |
| pydantic | 2.9.2 | Validación de requests/responses y parámetros de triage |
| pydantic-settings | 2.6.0 | Configuración desde variables de entorno / `.env` |
| email-validator | 2.2.0 | Validación de emails de usuarios |
| python-multipart | 0.0.12 | Carga de archivos (multipart/form-data) |
| python-jose[cryptography] | 3.5.0 | Firma y verificación de JWT HS256 |
| bcrypt | 5.0.0 | Hash de contraseñas |
| cryptography | 50.0.2 | Cifrado Fernet de las imágenes en disco |
| python-dotenv | 1.2.4 | Carga de `backend/.env` en scripts y Alembic |
| Pillow | 11.0.0 | Validación de formato y dimensiones de imágenes |

### Desarrollo y pruebas (`requirements-dev.txt`)

| Componente | Versión | Propósito |
|---|---|---|
| pytest | 9.1.1 | Ejecución de pruebas |
| pytest-cov | 7.1.0 | Cobertura |
| httpx | 0.27.2 | Cliente HTTP de `TestClient` (y del `HttpYoloProvider`) |
| ruff | 0.16.10 | Linter |
| black | 26.10.0 | Formateo |
| pgserver | 0.1.4 | PostgreSQL embebido para la BD de pruebas aislada (si no hay `TEST_DB_DSN`) |

## Frontend (raíz)

| Componente | Versión | Propósito |
|---|---|---|
| Node.js | 18+ (probado en 25.8) | Entorno de build |
| react / react-dom | 18.3.1 | Interfaz de usuario |
| typescript | 5.6.3 | Tipado estático |
| vite | 5.4.8 | Servidor de desarrollo y build |
| @vitejs/plugin-react | 4.3.2 | Soporte React en Vite |
| tailwindcss | 3.4.17 | Estilos utilitarios |
| postcss / autoprefixer | 8.4.47 / 10.4.20 | Procesamiento de CSS |
| lucide-react | 0.344.0 | Íconos |
| jspdf | 3.0.4 | Generación del reporte PDF en el navegador |
| jspdf-autotable | 5.0.2 | Tablas en el PDF |
| eslint / @eslint/js | 9.12.0 | Linter |
| typescript-eslint | 8.8.1 | Reglas de ESLint para TypeScript |
| eslint-plugin-react-hooks | 5.1.0-rc | Reglas de hooks |
| eslint-plugin-react-refresh | 0.4.12 | Reglas de Fast Refresh |
| globals | 15.11.0 | Globales del navegador para ESLint |
| @types/react / @types/react-dom | 18.3.11 / 18.3.0 | Tipos de React |

Se eliminaron `@supabase/supabase-js` (sin uso) y `@types/jspdf` (obsoleto: jsPDF 3 trae sus propios tipos).

## Servicios externos (no incluidos, próximos sprints)

| Componente | Estado | Sprint |
|---|---|---|
| Servicio de inferencia YOLO (Ultralytics) | Interfaz `HttpYoloProvider` lista; hoy se usa `SimulatedProvider` | S8 |
| AWS (EC2, RDS, S3 con SSE-KMS, CloudWatch) | `StorageBackend` preparado para `S3EncryptedStorage` | S7 |
| Docker / GitHub Actions | No implementado | S7 |
