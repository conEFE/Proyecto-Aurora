# Plan del Informe Final — Proyecto Aurora

**Creado:** 23-11-2026 · **Documento maestro vigente:** 1.0-rc · **Registro de revisiones:** v0.19

Hoja de ruta para llegar a la versión final del Informe de Proyecto de Título. El trabajo avanza por
iteraciones cortas sobre un único documento maestro. Este archivo es el plan general: se actualiza al
cerrar cada iteración. El detalle de cada iteración (qué se hizo y qué quedó abierto) está en
`trabajo/ESTADO_ITERACION.md`, y las decisiones y observaciones formales en el registro de revisiones.

## 1. Archivos de trabajo

| Archivo | Rol |
|---|---|
| `trabajo/Proyecto_Aurora_Informe_Final_Maestro.docx` | **Único** documento maestro. Todo el informe se edita aquí. |
| `trabajo/Proyecto_Aurora_Registro_de_Revisiones.docx` | Registro formal: observaciones, decisiones, estados, historial de versiones. |
| `trabajo/ESTADO_ITERACION.md` | Estado operativo y pendientes de la iteración en curso. |
| `trabajo/Proyecto_Aurora_Informe_Final.pdf` | PDF del maestro con índices actualizados (`herramientas/exportar_pdf.py`). |
| `PLAN_INFORME_FINAL.md` | Este plan: iteraciones, mapa de fuentes y criterios de cierre. |
| `respaldos/` | Copia de los tres archivos anteriores antes de cada hito (`*_pre-<hito>`). |
| `herramientas/` | Scripts usados para editar el maestro y generar figuras (trazabilidad de cambios). `maestro_lib.py` y `registro_lib.py` son la base común; cada iteración tiene su script `iterN_*.py`. |

Fuentes que **no** están en el repositorio y deben estar disponibles en cada sesión: formulación de
Unidad 1 (`Campos, Meneses, Neira.docx`), informe de Unidad 2 (`Neira, Campos, Meneses.docx`),
`TIHI84_ES2_Informe_Arquitectura_ProyectoAurora_AVANCE.docx`, `proyecto de titulo con correcciones.docx`
y la plantilla `Plantilla Informe Final TIHI84 Apoquindo.docx`.

## 2. Reglas que se mantienen en todas las iteraciones

1. Se respetan la plantilla institucional (18 capítulos, títulos y jerarquía) y la redacción académica
   impersonal.
2. Se distinguen cinco niveles de evidencia: **planificado**, **documentado** (README, informes),
   **verificado en código**, **probado** (pruebas ejecutadas y reproducibles) y **validado clínicamente**.
   Nada sube de nivel sin evidencia.
3. No se inventan datos, entrevistas, métricas, fechas ni referencias. Lo que falta queda como pendiente
   explícito en el registro.
4. Nueva Clínica Cordillera es institución de referencia sin compromiso formal; no hay piloto, SLA firmado,
   validación clínica ni integración HIS/RIS/PACS/DICOM/FHIR acreditados.
5. Las decisiones aprobadas (prioridades MoSCoW, HU08 reformulada, D-06-01 a D-06-04) no se cambian sin
   consultar.
6. Si dos fuentes se contradicen y la diferencia afecta el contenido, se consulta antes de redactar.

## 3. Ciclo de cada iteración

1. **Respaldo** de maestro, registro y estado en `respaldos/`.
2. **Contraste** de fuentes (Unidad 1, Unidad 2, repositorio) para los capítulos de la iteración.
3. **Consulta** al equipo solo por contradicciones o datos que bloqueen la redacción.
4. **Redacción** en el maestro, sin duplicar contenido de otros capítulos (se usan remisiones).
5. **Verificación**: validación del DOCX, exportación a PDF y revisión visual de las páginas modificadas.
6. **Sincronización**: registro de revisiones (versión, decisiones, observaciones) y `ESTADO_ITERACION.md`.
7. **Commit** de la iteración en la rama de trabajo.

**Hecho de una iteración:** capítulos redactados conforme a la plantilla; cada afirmación técnica con su
nivel de evidencia; contradicciones registradas o resueltas; DOCX válido y revisado en PDF; registro y
estado actualizados; respaldo guardado.

## 4. Mapa de integración de fuentes

| Capítulo del informe final | Unidad 1 (formulación) | Unidad 2 (desarrollo) | Repositorio / otras | Estado |
|---|---|---|---|---|
| I. Introducción | 1 | I | README | Inicial; actualizar al cierre |
| II. Identificación del problema | 2 | — | — | Borrador v0.2 |
| III. Levantamiento de requerimientos | 3 (HU01–HU08, RF, RNF) | — | ESPEC, `endpoints.md`, `resultados_tests.md` | HU01–HU12 integradas; criterios abiertos; falta matriz de trazabilidad |
| IV. Marco teórico | 4 | — | — | Inicial; referencias por normalizar |
| V. Objetivos | 5 | — | — | Inicial; falta matriz de interesados |
| VI. Metodología | 6 | «Metodología: Scrumban»; VII (Tablas 51–52) | — | Inicial v0.4 |
| VII. Definición de arquitectura TI | 7 | III (parcial) | `stack.md`, estructura de `backend/` | Inicial v0.5 |
| VIII. Arquitectura empresarial | 8 | III.1 (BPMN) | — | Inicial v0.5 |
| IX. Tecnologías a implementar | — | II (AHP, Tablas 1–14) | `requirements*.txt`, `package.json` | Inicial v0.6 |
| X. Arquitectura a implementar | — | III.1–III.8 (incluye clasificador CNN) | `modelo_datos.md`, `despliegue_aws.md`, `ESTADO_AWS.md`, `backend/inference_service/` | Inicial v0.7 |
| XI. KPI y SLA | 5.2.3–5.2.4 | IV | Dashboard (HU07) | Inicial v0.9 |
| XII. Pruebas y calidad | — | V | `backend/app/tests/`, `resultados_tests.md`, `seguridad_owasp.md` | Inicial v0.8 (pruebas ejecutadas) |
| XIII. Plan de implementación | — | VI | `ESTADO_AWS.md`, respaldos | Inicial v0.9 |
| XIV. Factibilidad económica | Anexo citado (no existe) | VIII (Tablas 55–61) | `ESTADO_AWS.md` (costos reales) | Inicial v0.10 |
| XV. Ajustes del cronograma | — | VII (Tablas 51–54, Figura 11, corte 18-10) | `CHANGELOG_SPRINTS.md`, historial Git | Inicial v0.11 (Gantt real con evidencia) |
| XVI. Conclusiones | 9 | Conclusiones | — | Inicial v0.13 |
| XVII. Referencias y glosario | 10 | Referencias, glosario | — | Inicial v0.13 |
| XVIII. Anexos | 11 (matriz de riesgos) | Anexos (casos de uso, diccionario, parámetros) | — | Inicial v0.13 |

## 5. Iteraciones

Las fechas son una propuesta, a confirmar contra la fecha real de entrega. La línea base del proyecto fija
la documentación final entre el 20-11 y el 05-12-2026 y la entrega entre el 01-12 y el 10-12-2026.

| It. | Alcance | Insumos necesarios | Fecha objetivo |
|---|---|---|---|
| 0 | Capítulos I–VI en versión inicial | — | **Hecha (23-11)** |
| 1 | VII Definición de arquitectura TI y VIII Arquitectura empresarial | Plantilla, `TIHI84_ES2_…_AVANCE.docx`, U1 cap. 7–8 | **Hecha (23-11)**; falta contraste con plantilla |
| 2 | IX Tecnologías: AHP de U2 contrastado con las versiones reales de las dependencias | U2 cap. II, archivos de dependencias | **Hecha (23-11)** |
| 3 | X Arquitectura a implementar: BPMN, casos de uso, componentes, modelo de datos, topología, infraestructura y arquitectura; **inspección directa de `inference_service`** (cierra N-03-16 a N-03-21 o los deja con evidencia) | U2 cap. III y figuras, código | **Hecha (23-11)** |
| 4 | XII Pruebas y calidad: **ejecución propia de la suite de pruebas** y **matriz de trazabilidad HU01–HU12 ↔ RF/RNF ↔ endpoint/entidad ↔ prueba**; con eso se revisan los criterios de aceptación del cap. III | Código, base de datos de pruebas | **Hecha (23-11)** |
| 5 | XI KPI y SLA (alineado con cap. V y HU07) y XIII Plan de implementación (disponibilidad, continuidad, mantención) | U2 cap. IV y VI, `ESTADO_AWS.md` | **Hecha (23-11)** |
| 6 | XIV Factibilidad económica: conciliar presupuesto del prototipo, costo del piloto y costo real de la demostración | U2 cap. VIII; confirmación del equipo | **Hecha (23-11)**; falta confirmar presupuesto aprobado |
| 7 | XV Ajustes del cronograma: estado real, desviaciones, hitos, ruta crítica, matriz de riesgos | **Estado aprobado por el equipo al cierre** | **Hecha (23-11)**; actividades sin registro por confirmar |
| 8 | Revisión de I–V con la evidencia acumulada: introducción, resumen/abstract, criterios de aceptación, matriz de interesados | Resultados de iteraciones 3–7 | **Hecha (23-11)** |
| 9 | XVI Conclusiones, XVII Referencias y glosario (APA normalizado), XVIII Anexos | Todas las fuentes | **Hecha (23-11)** |
| 10 | Cierre editorial: leyendas y numeración de tablas/figuras, TDC e índices, retiro de «Control de integración», PDF final, cierre del registro | — | **Hecha (23-11)**; quedan pendientes del equipo |
| 11 | Ajustes por plantilla y rúbrica de defensa (EA5): (a) revertir título 10.4.3 y mover 10.8 a 10.7.1; (b) comparación con soluciones existentes e innovación (cap. V o IV); (c) estudio de factibilidad integral técnica, operativa, económica, legal y ambiental (recuperando U2); (d) integración del stack en IX y sustentabilidad en 8.3; (e) prueba de rendimiento local (p95) en XI/XII | Plantilla, rúbrica, U2 «Estudio de factibilidad», fuentes externas para (b) y ambiental; aprobación del equipo; correcciones del docente (opcional) | **Hecha (24-11)**; incluye corrección de un bloqueo bajo carga en el backend |

Las iteraciones 2 a 5 dependen sobre todo del repositorio y pueden avanzar sin esperar al equipo. Las
iteraciones 6 y 7 necesitan datos que solo tiene el equipo; conviene pedirlos desde ya.

## 6. Pendientes que bloquean iteraciones

| Pendiente | Bloquea | Responsable |
|---|---|---|
| Plantilla institucional e informe `TIHI84_ES2_…_AVANCE.docx` | It. 1 | Usuario |
| Estado del cronograma aprobado al cierre (o Gantt actualizada); evidencia de hitos: propuesta de SLA, decisión del modelo, capacitación, validación clínica, piloto | It. 7 | Equipo |
| Confirmación de la RACI (Tabla 7) y del apoyo de QA | Cierre del cap. VI | Equipo |
| Presupuesto vigente y su fuente (Equipo Proyecto Aurora 2026b) | It. 6 | Equipo |
| Aprobación para renumerar IDs duplicados N-03-16 a N-03-21 del registro | Higiene del registro | Usuario |
| Fecha real de entrega del informe | Calendario de este plan | Usuario |
| Aprobación de los cinco ajustes de la iteración 11 | It. 11 (resuelto 24-11) | Usuario |
| Despliegue de la corrección del bloqueo bajo carga (`9043857`) en el entorno de demostración | Coherencia entre informe y demostración | Equipo |
| Monitoreo y alarmas de disponibilidad; prueba de restauración (ver `trabajo/REVISION_NUBE_VS_HU.md`) | Medición de K3; cierre de XIII | Equipo (acceso a AWS) |
| Correcciones del docente a U1 y U2 (para verificar U1-xx/U2-xx) | Verificación de observaciones | Usuario |
| Fuentes reales sobre soluciones existentes (p. ej., productos comerciales de IA en mamografía) y sobre impacto ambiental | It. 11 (b) y (c) | Agente con búsqueda web / equipo |

## 7. Registro de iteraciones

| It. | Fecha | Maestro | Registro | Resumen |
|---|---|---|---|---|
| 0 | 23-11-2026 | v0.4 | v0.8 | Capítulo VI redactado; decisiones D-06-01 a D-06-04; observaciones N-06-01 a N-06-14. |
| 1 | 23-11-2026 | v0.5 | v0.9 | Capítulos VII y VIII redactados (Tablas 10–13); observaciones N-07-01 a N-07-06. Plantilla aún no disponible: subdivisión según Unidad 1. |
| 2 | 23-11-2026 | v0.6 | v0.10 | Capítulo IX redactado (Tablas 14–21) con AHP recalculado y versiones reales; decisión D-07-01 (documentar la arquitectura actual); observaciones N-09-01 a N-09-08. |
| 3 | 23-11-2026 | v0.7 | v0.11 | Capítulo X redactado (Figuras 2–10, Tablas 22–27): diagramas de la arquitectura actual, modelo de datos generado desde el código, servicio de inferencia inspeccionado; observaciones N-10-01 a N-10-09. |
| 4 | 23-11-2026 | v0.8 | v0.12 | Capítulo XII redactado (Tablas 28–33) con ejecución propia de 314 pruebas (100% aprobadas, cobertura 97%) y matriz de trazabilidad; observaciones N-12-01 a N-12-09. |
| 5 | 23-11-2026 | v0.9 | v0.13 | Capítulos XI y XIII redactados (Tablas 28–31 y 38–42); KPI con estado de implementación y medición; SLA como propuesta; continuidad con preparación real; observaciones N-11-01 a N-13-05. |
| 6 | 23-11-2026 | v0.10 | v0.14 | Capítulo XIV redactado (Tablas 43–49) con costo real de la nube y cálculos verificados; especificaciones del equipo de inferencia en VI y X; observaciones N-14-01 a N-14-07. |
| 7 | 23-11-2026 | v0.11 | v0.15 | Capítulo XV redactado: carta Gantt con línea base, ejecución, responsables e hitos (Figura 11; Tablas 50–54); criterio D-15-01; observaciones N-15-01 a N-15-06. |
| 8 | 23-11-2026 | v0.12 | v0.17 | Resumen, abstract e introducción; capítulo III completo (criterios, verificación, RF01–RF09, RNF, restricciones); decisiones D-08-01 a D-08-03 aplicadas en V, XI, XII y XIV. |
| 9 | 23-11-2026 | v0.13 | v0.18 | Capítulos XVI, XVII y XVIII redactados: conclusiones y recomendaciones, glosario y 56 referencias APA, anexos 1 a 4 y material complementario; observaciones N-17-01 a N-17-05. |
| 10 | 23-11-2026 | 1.0-rc | v0.19 | Cierre editorial: páginas horizontales, índices de tablas y figuras, tabla de historias, portada, retiro del control interno; PDF de 160 páginas. Pendientes del equipo consolidados en el registro (4.15). |
| — | 23-11-2026 | 1.0-rc | v0.19 | Revisión contra plantilla (95 títulos presentes; 2 desvíos) y rúbrica EA5 (ind. 4 no cubierto; 2, 3, 5 y 6 parciales). Sin cambios en el maestro; se planifica la iteración 11. |
| 11 | 24-11-2026 | 1.1-rc | v0.20 | Ajustes por plantilla y rúbrica EA5 (4.8, 8.3.1, 9.2.1, 10.7.1, 12.1.3, 14.3.1); PC-01 local no cumplido con 100 usuarios (p95 3.974 ms; sí con 50) tras corregir un bloqueo bajo carga en el backend; revisión de nube frente a HU; PDF de 167 páginas. |
| 12 | 24-11-2026 | 1.2-rc | v0.21 | Corrección del bloqueo bajo carga desplegada como 2.10.1 en el entorno de demostración; actualizados 12.1.3, XIII y 14.3.1; N-11-07 cerrada. PDF de 167 páginas. |
