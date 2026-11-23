# Plan del Informe Final — Proyecto Aurora

**Creado:** 23-11-2026 · **Documento maestro vigente:** v0.6 · **Registro de revisiones:** v0.10

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
| X. Arquitectura a implementar | — | III.1–III.8 (incluye clasificador CNN) | `modelo_datos.md`, `despliegue_aws.md`, `ESTADO_AWS.md`, `backend/inference_service/` | **Por redactar** |
| XI. KPI y SLA | 5.2.3–5.2.4 | IV | Dashboard (HU07) | **Por redactar** |
| XII. Pruebas y calidad | — | V | `backend/app/tests/`, `resultados_tests.md`, `seguridad_owasp.md` | **Por redactar** |
| XIII. Plan de implementación | — | VI | `ESTADO_AWS.md`, respaldos | **Por redactar** |
| XIV. Factibilidad económica | Anexo citado (no existe) | VIII (Tablas 55–61) | `ESTADO_AWS.md` (costos reales) | **Por redactar** |
| XV. Ajustes del cronograma | — | VII (Tablas 51–54, Figura 11, corte 18-10) | `CHANGELOG_SPRINTS.md`, historial Git | **Por redactar**; requiere estado aprobado |
| XVI. Conclusiones | 9 | Conclusiones | — | Al final |
| XVII. Referencias y glosario | 10 | Referencias, glosario | — | Al final |
| XVIII. Anexos | 11 (matriz de riesgos) | Anexos (casos de uso, diccionario, parámetros) | — | Al final |

## 5. Iteraciones

Las fechas son una propuesta, a confirmar contra la fecha real de entrega. La línea base del proyecto fija
la documentación final entre el 20-11 y el 05-12-2026 y la entrega entre el 01-12 y el 10-12-2026.

| It. | Alcance | Insumos necesarios | Fecha objetivo |
|---|---|---|---|
| 0 | Capítulos I–VI en versión inicial | — | **Hecha (23-11)** |
| 1 | VII Definición de arquitectura TI y VIII Arquitectura empresarial | Plantilla, `TIHI84_ES2_…_AVANCE.docx`, U1 cap. 7–8 | **Hecha (23-11)**; falta contraste con plantilla |
| 2 | IX Tecnologías: AHP de U2 contrastado con las versiones reales de las dependencias | U2 cap. II, archivos de dependencias | **Hecha (23-11)** |
| 3 | X Arquitectura a implementar: BPMN, casos de uso, componentes, modelo de datos, topología, infraestructura y arquitectura; **inspección directa de `inference_service`** (cierra N-03-16 a N-03-21 o los deja con evidencia) | U2 cap. III y figuras, código | 26-11 |
| 4 | XII Pruebas y calidad: **ejecución propia de la suite de pruebas** y **matriz de trazabilidad HU01–HU12 ↔ RF/RNF ↔ endpoint/entidad ↔ prueba**; con eso se revisan los criterios de aceptación del cap. III | Código, base de datos de pruebas | 27-11 |
| 5 | XI KPI y SLA (alineado con cap. V y HU07) y XIII Plan de implementación (disponibilidad, continuidad, mantención) | U2 cap. IV y VI, `ESTADO_AWS.md` | 28-11 |
| 6 | XIV Factibilidad económica: conciliar presupuesto del prototipo, costo del piloto y costo real de la demostración | U2 cap. VIII; confirmación del equipo | 29-11 |
| 7 | XV Ajustes del cronograma: estado real, desviaciones, hitos, ruta crítica, matriz de riesgos | **Estado aprobado por el equipo al cierre** | 30-11 |
| 8 | Revisión de I–V con la evidencia acumulada: introducción, resumen/abstract, criterios de aceptación, matriz de interesados | Resultados de iteraciones 3–7 | 01-12 |
| 9 | XVI Conclusiones, XVII Referencias y glosario (APA normalizado), XVIII Anexos | Todas las fuentes | 02-12 |
| 10 | Cierre editorial: leyendas y numeración de tablas/figuras, TDC e índices, retiro de «Control de integración», PDF final, cierre del registro | — | 03-12 |

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

## 7. Registro de iteraciones

| It. | Fecha | Maestro | Registro | Resumen |
|---|---|---|---|---|
| 0 | 23-11-2026 | v0.4 | v0.8 | Capítulo VI redactado; decisiones D-06-01 a D-06-04; observaciones N-06-01 a N-06-14. |
| 1 | 23-11-2026 | v0.5 | v0.9 | Capítulos VII y VIII redactados (Tablas 10–13); observaciones N-07-01 a N-07-06. Plantilla aún no disponible: subdivisión según Unidad 1. |
| 2 | 23-11-2026 | v0.6 | v0.10 | Capítulo IX redactado (Tablas 14–21) con AHP recalculado y versiones reales; decisión D-07-01 (documentar la arquitectura actual); observaciones N-09-01 a N-09-08. |
