# Evidencia de pruebas — 25-11-2026

Ejecución propia para el capítulo XII del informe final, sobre el commit `a2c4761` (rama `claude/bold-maxwell-13fkwp`):
versión **2.12.0**, que contiene la 2.11.0 desplegada en el entorno de demostración más las optimizaciones de
rendimiento y el modelo de respaldo (aún no desplegadas). Reemplaza como ejecución vigente a `pruebas_2026-11-23`
(314 pruebas, versión 2.10.0), que se conserva como historia.

- Entorno: contenedor Linux, Python 3.13.18, PostgreSQL 16 local (`TEST_DB_DSN`), BD aislada creada con Alembic.
- Comando: `pytest -q --cov=app --junitxml=...` desde `backend/`.
- Resultado: **340 pruebas, 0 fallidas, 0 errores, 0 omitidas**; 68,4 s; cobertura total **97%** (3.817 sentencias,
  127 sin cubrir); `app/services` 94,5% (1.812 sentencias, 100 sin cubrir).
- Análisis estático: `ruff check .` sin hallazgos; `npm run lint`, `npm run typecheck` y `npm run build` sin errores.
- No ejecutado aquí: `pip-audit` y `npm audit` (los ejecuta el CI).
- Archivos: `junit_backend.xml` (detalle por prueba) y `cobertura_resumen.txt` (cobertura por archivo).

Pruebas nuevas desde la ejecución del 23-11: `test_middleware_pool.py` y `test_concurrency_limit.py` (bloqueos bajo
carga, 2.10.1 y 2.10.2), `test_jefatura_activacion.py` (2.11.0), `test_query_counts.py` y cinco del modelo de respaldo
en `test_inference_model.py` (2.12.0).
