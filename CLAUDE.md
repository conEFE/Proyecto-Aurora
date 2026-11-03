# Proyecto Aurora — instrucciones para Claude Code

Plataforma web de apoyo a la **detección temprana y priorización (triage)** de casos sospechosos de cáncer de mama. Es un proyecto de título (INACAP). La plataforma **apoya, no reemplaza**, el criterio médico.

## Documento rector
La especificación completa está en **`docs/ESPEC_AGENTE_Aurora_alineacion_sprints.md`**. Léela entera antes de tocar código. Define el diagnóstico del código actual, el modelo de datos objetivo, la matriz de permisos, el módulo de triage y el plan por sprint (S1–S6) con su Definición de Hecho.

## Stack
- **Backend** (`backend/`): Python ≥3.10, FastAPI, SQLAlchemy 2, Alembic, Pydantic v2, PostgreSQL ≥14.
- **Frontend** (raíz): React 18 + TypeScript + Vite + Tailwind; los PDF se generan con jsPDF.

## Comandos
```bash
# Backend (desde backend/)
python -m venv venv && source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt -r requirements-dev.txt
alembic upgrade head
uvicorn app.main:app --reload --port 8000
pytest --cov=app

# Frontend (desde la raíz)
npm install
npm run dev
npm run lint && npm run typecheck
```

## Reglas de trabajo
1. **Un sprint a la vez**, en orden S1 → S6, en la rama `feature/alineacion-sprints`.
   - Haz un commit por sprint con el prefijo `sprint-N:`.
   - Al cerrar cada sprint, **detente**, resume lo hecho en `docs/CHANGELOG_SPRINTS.md` y espera aprobación antes de seguir.
2. **No implementes S7–S8** (Docker, CI, AWS, YOLO real) hasta que se pida explícitamente.
3. Todo cambio de esquema va con **migración Alembic reversible**. Nunca uses `create_all`.
4. **Secretos:**
   - Nada de credenciales en el código ni en el repositorio.
   - Usa `.env` (en `.gitignore`) y mantén `.env.example` sin valores reales.
5. **IA simulada:**
   - Todo resultado del proveedor simulado lleva `is_simulated = true` y un badge visible «IA SIMULADA» en la interfaz.
   - Nunca lo presentes como resultado clínico real.
6. **Datos:** solo datos ficticios y RUT de prueba en seeds y tests.
7. **Idioma:**
   - Código e identificadores en inglés.
   - Textos de interfaz y mensajes de error en español.
8. **Conflictos:** si algo de la especificación choca con el código de una forma no prevista, detente y pregunta; no improvises.
9. **Historial de Git:** no reescribas el historial (por ejemplo, `filter-repo` o `force push`) sin aprobación explícita.

## Definición de Hecho (todo sprint)
- `pytest` en verde, con los tests de la DoD del sprint según la especificación.
- `npm run lint` y `npm run typecheck` sin errores.
- Migraciones aplicadas y con `downgrade` probado.
- Entrada del sprint registrada en `docs/CHANGELOG_SPRINTS.md`.
