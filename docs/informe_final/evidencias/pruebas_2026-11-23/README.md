# Evidencia de pruebas — 23-11-2026

Ejecución propia para el capítulo XII del informe final, sobre el commit `53ee1b1` (rama `claude/bold-maxwell-13fkwp`,
mismo código de aplicación que `main` en `c318a45`).

- Entorno: contenedor Linux, Python 3.13.18, PostgreSQL 16 local (`TEST_DB_DSN`), BD aislada creada con Alembic.
- Comando: `pytest -q --cov=app --junitxml=...` desde `backend/`.
- Resultado: 314 pruebas, 0 fallidas, 0 errores, 0 omitidas; 53,2 s; cobertura total 97% (3.348 sentencias, 85 sin cubrir);
  `app/services` 96,1%.
- Análisis estático: `ruff check app` sin hallazgos; `npm run lint` y `npm run typecheck` sin errores.
- No ejecutado aquí: `pip-audit` y `npm audit` (los ejecuta el CI; última corrida de CI en `main`: run 61, 16-11-2026, exitosa).
- Archivos: `junit_backend.xml` (detalle por prueba) y `cobertura_resumen.txt` (cobertura por archivo).
