# Handoff — después de la iteración 17 del Informe Final (Proyecto Aurora)

**Fecha:** 25-11-2026 · **Rama:** `claude/bold-maxwell-13fkwp` · **Punto de partida:** maestro **1.7-rc**, registro **v0.26**,
PDF de 199 páginas, 68 tablas y 28 figuras. Reemplaza a `HANDOFF_ITERACION_17.md` (que queda como historia).

Lee este documento, luego `trabajo/PENDIENTES_EQUIPO.md` y `trabajo/ESTADO_ITERACION.md`.

## 1. Estado

- **Código:** `main` = 2.11.0, **desplegada** en `demo.auroracare.cl` el 25-11-2026. Esta rama = **2.12.0** (merge de
  `main` + `470479f`): optimización de consultas (de 23 a 95 solicitudes/s por proceso en local) y servicio de inferencia
  de respaldo (`INFERENCE_BACKUP_URL`). **Sin fusionar en `main` ni desplegar.** 340 pruebas en verde.
- **Informe:** integra la 2.11.0 y la 2.12.0 (iteración 17, `herramientas/iter17_versiones.py`), con A2 hecho
  (`evidencias/pruebas_2026-11-25`). Lo que depende del código está completo.
- **Decisiones del equipo tomadas:** defensa con el PC de Juan como servicio principal y una instancia de AWS como
  respaldo (no creada); optimizar consultas en lugar de agrandar la instancia (hecho en código; falta medir en AWS).

## 2. Qué falta (todo en `trabajo/PENDIENTES_EQUIPO.md`)

- **Con el JSON + script** (`trabajo/pendientes_equipo.json`, `herramientas/completar_pendientes.sh`): dedicatoria,
  agradecimientos, Shah et al. (2023), marcas «[FALTA INFORMACIÓN…]» del capítulo II (GLOBOCAN y GES), referencias
  2026b/2026c/OMS/NEMA/ACR, fecha de despliegue de la 2.12.0, PC-01 en AWS con la 2.12.0 e instancia de respaldo.
  El script escribe el texto según el resultado (PC-01 aprobada o no). Después: registro (siguiente v0.27, sección
  4.23) y `ESTADO_ITERACION.md`.
- **A mano:** A3 (modelo de IA desde U2, sección 3.8; pedir U2), correcciones del docente, etiquetas de versión
  v2.10.1–v2.12.0, alerta de presupuesto, lectura y aceptación de la 1.0.

## 3. Si te piden desplegar la 2.12.0 o medir PC-01

- Fusionar la rama en `main` solo con pedido explícito; despliegue habitual por Session Manager (`docs/ESTADO_AWS.md`).
- PC-01 en AWS: `backend/scripts/load_test.py` sobre una copia de la base (método en
  `evidencias/rendimiento_aws_2026-11-24/README.md`). Guardar los JSON en `evidencias/rendimiento_aws_<fecha>/`,
  copiar los totales en `pendientes_equipo.json` y ejecutar el script.
- Instancia de respaldo: `docs/inferencia_remota.md`, sección 5.1 (`t4g.small`, sin IP pública, entrada 8080 solo desde
  el grupo de seguridad de `aurora-prod`, detenida fuera de las demostraciones). Requiere credenciales de AWS y
  confirmación del usuario (tiene costo).

## 4. Reglas que no cambian

- El maestro es el único informe que se edita; respalda antes (`respaldos/*_pre-it18`). `completar_pendientes.sh`
  respalda solo.
- No inventes información ni declares desplegado, medido o validado sin evidencia. La 2.12.0 no está desplegada;
  PC-01 con la 2.12.0 solo está medida en local. La revisión del 20-11 no es validación clínica.
- Commits **sin coautoría de Claude** (`CLAUDE.md`). Sin `push --force`.
- El proyecto de AWS no permite recursos ni copias en otra región.

## 5. Cómo se trabaja el maestro

Como en las iteraciones anteriores (`herramientas/iter17_versiones.py` es el ejemplo más completo: filas de tablas
clonadas, imágenes reemplazadas, subsecciones nuevas): descomprimir, script con `maestro_lib.py` (`init_ids`, `render`,
`renumerar`), comprimir con `zip -XrDqy` y `zip -d '*/'`, validar con `scripts/office/validate.py` de la skill docx,
exportar con `herramientas/exportar_pdf.py`. Figuras: `diagramas_cap10.py schema_modelos.json <dir>` (modelo lógico y
casos de uso) y `diagramas_it15/render.cjs` (arquitectura y cloud). Capturas: `herramientas/capturas_2.11.0.cjs` con
la API en :8000 y Vite en :5173 sobre datos de `seed_demo`.

## 6. Fuentes fuera del repositorio

U1, U2, la plantilla y la rúbrica las sube el usuario y no se versionan; pídelas si no las tienes.
