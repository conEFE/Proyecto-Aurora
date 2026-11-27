# Handoff — Iteración 11 del Informe Final (Proyecto Aurora)

**Fecha:** 23-11-2026 · **Rama:** `claude/bold-maxwell-13fkwp` · **Punto de partida:** maestro **1.0-rc**, registro **v0.19**, PDF de 160 páginas.

Este documento es para el agente que continúe el informe. Léelo completo y luego `PLAN_INFORME_FINAL.md` y
`trabajo/ESTADO_ITERACION.md` (sección «Revisión contra plantilla y rúbrica»).

## 1. Qué está hecho

- Iteraciones 0 a 10 cerradas: los 18 capítulos de la plantilla redactados en el maestro, con leyendas, índices,
  referencias cruzadas, páginas horizontales y PDF exportado con índices actualizados.
- Revisión contra la plantilla institucional y la rúbrica de defensa (Escala de Apreciación N°5, `TIHI84_U3_ES3_EA5.xlsx`).
  **Solo diagnóstico: el maestro no se modificó.** Hallazgos en `trabajo/ESTADO_ITERACION.md`.
- Los documentos fuente reenviados por el usuario (`Neira_Campos_Meneses.docx` = U2, `Campos_Meneses_Neira.docx` = U1)
  son idénticos (sha256) a los usados en todas las iteraciones. No traen contenido nuevo.

## 2. Qué falta: iteración 11 (pendiente de aprobación del usuario)

Se propusieron cinco ajustes; el usuario **aún no los aprobó explícitamente**. Confírmalo antes de editar el maestro.

| # | Ajuste | Dónde | Fuente | Notas |
|---|---|---|---|---|
| a | Revertir el título 10.4.3 a «Diccionario de datos (puede ir como anexo).» y bajar «Componente de análisis automatizado de imágenes» (hoy 10.8, nivel 3) a 10.7.1 (nivel 4, bajo «Diagrama de Arquitectura.») | Cap. X | Plantilla | Revertir el paso 1b de `iter10_editorial.py`. Revisar también el título vacío de nivel 3 que sigue a 10.1 (pandoc lo muestra como `### {#section-1}`): su `pPr` no coincidió con el reemplazo de la iteración 10. |
| b | Comparación con soluciones existentes e innovación del proyecto (diferenciación) | Cap. IV (Marco teórico) o V | **Externa** | Indicador 4 de la rúbrica, hoy **no cubierto**. U1 (sección 3.1) solo menciona la «revisión de proyectos similares» como instrumento, sin resultados. Usa solo productos y estudios reales con referencia APA verificable. No inventes datos comerciales. |
| c | Estudio de factibilidad integral: técnica, operativa, económica, legal y ambiental | Cap. XIV (introducción) o una subsección nueva sin romper la plantilla | U2 «Estudio de factibilidad» (técnica, económica, implementativa) + XII/XIII/XIV + fuente externa para la ambiental | Indicador 5. La factibilidad de U2 **no se integró** al maestro. Ninguna fuente trae la ambiental: redáctala con lo verificable (nube compartida y AWS, PC de inferencia local, sin papel) y fuentes reales; si no hay evidencia, decláralo. |
| d | Integración del stack (cómo se complementan las herramientas) y argumento de sustentabilidad de la solución | IX (subsección final) y 8.3 | Código, IX, XIII, XIV | Indicadores 2 y 3. Usa la arquitectura actual (D-07-01: no rediseñar). |
| e | Prueba de rendimiento local (p95) documentada como entorno local, no producción | XI y XII | Ejecución propia | Indicador 6. Hoy p95 es solo meta; Locust no está implementado. Si se ejecuta, registra comando, entorno, datos y resultado en `evidencias/`. Si no, no lo declares. |

### Contradicciones al reutilizar la factibilidad de U2 (texto de U2, líneas 685–697 del extracto)
- U2 dice «capacitación de usuarios (planificada del 10 al 25 de noviembre)». Lo declarado por el equipo es que **no hubo
  capacitación**: hubo una presentación el **20-11-2026** a 2 médicos y 1 enfermera para revisar el funcionamiento y validar el
  modelo (D-15-02). Escríbelo como «planificado, no ejecutado» y no lo presentes como validación clínica.
- U2 llama a Nueva Clínica Cordillera «cliente piloto». Regla vigente: es institución de referencia, sin compromiso formal
  (riesgo R12). No la presentes como cliente, patrocinador ni piloto.

## 3. Reglas que no cambian

- El maestro (`trabajo/Proyecto_Aurora_Informe_Final_Maestro.docx`) es el único informe que se edita. Respalda antes en `respaldos/` (`*_pre-it11`).
- No inventes información ni declares implementado, probado o validado sin evidencia (niveles: planificado / documentado /
  verificado en código / probado / validado clínicamente). KPI y SLA son metas de planificación.
- El usuario pidió antes inventar fechas del Gantt y se rechazó (D-15-01). Mantén ese criterio.
- Ante contradicciones o falta de evidencia, avisa antes de asumir una solución.
- Estilo académico impersonal, en español; APA 7.
- Commits **sin coautoría de Claude** (pedido del equipo, `CLAUDE.md`). No se puede usar `git push --force`; si el remoto diverge,
  usa `git merge -s ours` y luego un push normal, solo si el contenido remoto ya está incluido.

## 4. Cómo se trabaja el maestro (herramientas en `herramientas/`)

1. Descomprime el maestro en una carpeta temporal con `zipfile` de Python.
2. Escribe `iter11_*.py` usando `maestro_lib.py`: `init_ids(x)` al inicio; `rich` acepta `{T:clave}`/`{F:clave}`; `table(widths, rows)`
   con anchos que sumen ≤ 8544; `insert_after_bookmark`; `renumerar(x)` al final.
   **No llames a `set_control_row` ni `set_control_version`**: la sección «Control de integración» se retiró en la iteración 10 y fallan.
3. Vuelve a comprimir: `(cd m && zip -XrDqy ../maestro.docx .)` y luego `zip -d maestro.docx '*/'`.
4. Valida con `scripts/office/validate.py` de la skill docx.
5. Exporta el PDF con índices actualizados:
   `python3 herramientas/exportar_pdf.py trabajo/Proyecto_Aurora_Informe_Final_Maestro.docx trabajo/Proyecto_Aurora_Informe_Final.pdf`
   y revisa las páginas afectadas.
6. Registro de revisiones: crea `iter11_registro.py` con `registro_lib.py` (`set_version` v0.20, `add_version_rows`, `append_section`
   con la sección 4.16), con decisiones y observaciones nuevas (IDs N-11-xx de iteración 11 / D-xx-xx según capítulo).
7. Actualiza `trabajo/ESTADO_ITERACION.md` y la tabla 7 de `PLAN_INFORME_FINAL.md`; haz commit y push a la rama.

## 5. Pendientes del equipo (sin cambios; registro, sección 4.15)

Dedicatoria y agradecimientos; cita Shah et al. (2023); título de 2026c y descripción de 2026b; fechas de OMS 2026, NEMA 2026
y ACR 2025; acta de la revisión del 20-11 (opcional); prueba de restauración y escaneo ZAP; alerta de presupuesto AWS ≥ USD 30;
comentario de K5 en el código; confirmar CU18 y PI-06…PS-08; lectura completa y aceptación de la versión 1.0.
Además: **correcciones del docente a U1 y U2** (se pidieron, sin recibir) para verificar que las observaciones U1-xx/U2-xx estén atendidas.

## 6. Fuentes de trabajo (fuera del repositorio)

Los informes de U1 y U2, la plantilla y la rúbrica son archivos que sube el usuario y no se versionan. Si el siguiente agente
no los tiene, debe pedirlos. Los extractos de texto de la sesión anterior estaban en el scratchpad, que no persiste.
