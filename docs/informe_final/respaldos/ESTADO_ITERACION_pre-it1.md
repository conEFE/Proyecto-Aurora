# Proyecto Aurora — Estado del plan de revisión y avance del informe

**Actualización:** 23-11-2026 (iteración capítulo VI)  
**Versiones vigentes:** documento maestro v0.4 · registro de revisiones v0.8  
**Estado general:** revisión en curso; prioridades HU09–HU12 aprobadas e incorporadas; capítulos IV, V y VI redactados en versión inicial.

## 1. Decisión aprobada: prioridades HU09–HU12

| Historia | Prioridad MoSCoW aprobada | Fundamento resumido |
|---|---|---|
| HU09 – Consentimiento informado | Must Have | Control relevante vinculado al registro y gestión de pacientes y trazabilidad del consentimiento. |
| HU10 – Solicitudes y derechos de titulares | Should Have | Capacidad importante de privacidad y seguimiento, complementaria al flujo operativo principal. |
| HU11 – Bitácora de auditoría | Must Have | Control transversal de trazabilidad para operaciones sobre información clínica. |
| HU12 – Revisión profesional de resultados automatizados | Should Have | Diferencia evaluación médica y salida automatizada; agrega trazabilidad sin sustituir la gestión principal. |

La aprobación de prioridad no demuestra implementación ni cierra criterios de aceptación.

## 2. Estado de revisión de HU01–HU12

- **HU01–HU07:** las historias y prioridades existentes se mantienen. Falta construir la matriz de trazabilidad entre historias, RF/RNF, endpoints, entidades, controles y pruebas. Los criterios no deben inventarse si no están definidos en la especificación rectora.
- **HU08:** historia reformulada como necesidad funcional del profesional médico para consultar resultados del análisis automatizado asociados a imágenes y casos. Los criterios continúan propuestos y pendientes de verificación.
- **HU09–HU12:** historias complementarias incorporadas y priorizadas según aprobación del usuario. Los criterios siguen siendo propuestas pendientes de contraste con especificación, código y pruebas.
- **No se cierra ningún criterio de aceptación** sin evidencia suficiente y trazable.

## 3. Separación de niveles de evidencia

1. **Documentado:** declarado en README, informes u otra documentación del proyecto.
2. **Verificado en código:** observado directamente en implementación y configuración.
3. **Probado:** respaldado por pruebas identificables y resultados reproducibles.
4. **Validado clínicamente:** respaldado por protocolo, datos, métricas y evaluación clínica pertinente.

La carpeta `inference` no fue inspeccionada directamente en esta iteración. No atribuir validación clínica al prototipo ni confundir la existencia de proveedor HTTP con una integración probada.

## 4. Capítulo IV — Marco Teórico

Se incorporó una versión inicial al documento maestro con estos apartados:

- Cáncer de mama y detección temprana.
- Imágenes mamarias y clasificación BI-RADS.
- Sistemas de información en imagenología: HIS, RIS y PACS.
- Estándares DICOM y HL7 FHIR.
- Inteligencia artificial aplicada al análisis de imágenes médicas.
- Sistemas de apoyo a la decisión clínica y priorización.
- Seguridad, privacidad y trazabilidad de la información clínica.
- Relación del marco teórico con Proyecto Aurora.

La redacción diferencia los fundamentos teóricos de las capacidades efectivamente implementadas. Las referencias bibliográficas deben normalizarse y consolidarse en el capítulo XVII.

## 5. Capítulo V — Objetivos del Proyecto

Se incorporó una redacción inicial que cubre solución tecnológica, alcance y restricciones, proceso de negocio afectado, interesados, KPI, SLA, objetivo general y objetivos específicos. Se diferenció el alcance del prototipo de una eventual puesta en producción; las metas KPI/SLA se presentan como objetivos de planificación y no como resultados medidos. También se explicitó la diferencia entre la formulación inicial (IA como evolución futura) y la documentación más reciente del repositorio (prototipo de inferencia simulado/HTTP), sin afirmar integración productiva ni validación clínica.

Pendientes del capítulo V: incorporar la matriz de interesados aprobada, precisar la definición y método de medición de cada KPI/SLA, y revisar los objetivos contra el alcance definitivo.

## 5.1. Capítulo VI — Metodología de Trabajo (maestro v0.4)

Redacción inicial incorporada en 6.1–6.4, previo contraste de Unidad 1 (`Campos_Meneses_Neira.docx`), Unidad 2 (`Neira_Campos_Meneses.docx`, corte 18-10-2026) y documentación del repositorio.

| Apartado | Contenido incorporado |
|---|---|
| 6.1 Metodología y desarrollo | Dos niveles: predictivo (línea base, hitos, control de cambios; PMBOK) y Scrumban en ejecución. Evolución desde el híbrido predictivo + Scrum de U1. Tablas 1–2 (comparación cualitativa y ponderada: Scrumban 4,55; Scrum 3,80; Kanban 3,50), Tabla 3 (elementos), Tabla 4 (tablero y WIP), Definición de Hecho, ocho sprints y métricas de flujo como metas sin resultados. |
| 6.2 Duración y cronograma | Línea base 11-04-2026 a 10-12-2026 (~35 semanas), Tabla 5 por fase y actividad, Figura 1 (Gantt regenerada, corrige desfase de filas de la figura de U1), hitos. Validación clínica y piloto marcados como condicionados. Estado real → cap. XV. |
| 6.3 Equipo de trabajo | Tabla 6 (roles), Tabla 7 (RACI actualizada); QA especializado contemplado pero sin registro de incorporación. |
| 6.4 Plan de recursos | Recursos humanos, tecnológicos (Tabla 8, incluye equipo con GPU), software y herramientas, infraestructura y servicios (Tabla 9); cifras → cap. XIV; configuración efectiva → caps. X y XIII. |

**Decisiones aprobadas (23-11-2026):**
- D-06-01: Scrumban como evolución del enfoque híbrido de U1.
- D-06-02: cap. VI = línea base; cap. XV = estado real, desviaciones y ruta crítica.
- D-06-03: Juan Francisco Meneses desarrolla y entrena el modelo y su servicio de inferencia; Felipe Campos lo integra en el backend.
- D-06-04: RACI actualizada con roles de U2; «Patrocinador/Cliente» → «Institución de referencia (sin compromiso formal)»; se retira «Focus Group»; QA a cargo del equipo de desarrollo.

**Observaciones nuevas:** N-06-01 a N-06-14 en el registro v0.8 (sección 4.4). Abiertas: N-06-03 (sin datos de métricas de flujo), N-06-04 (sin cronograma aprobado posterior al 18-10-2026; hitos de SLA, decisión IA, capacitación, validación clínica y piloto sin evidencia), N-06-07 (confirmar RACI con el equipo), N-06-08 (QA especializado), N-06-09 (conciliar presupuesto U2 vs. infraestructura documentada), N-06-10 (claves bibliográficas Equipo Proyecto Aurora 2026a/2026b/U2), N-06-11 (numeración de tablas e índices), N-06-12 (IDs N-03-16 a N-03-21 duplicados en el registro; renumeración requiere aprobación), N-06-14 (archivos del paquete no recibidos).

**Observaciones de evaluación actualizadas:** U1-07 y U1-08 pasan a «En curso» (incorporadas en v0.4; cierre sujeto a revisión del equipo).

## 6. Próximos pasos

1. Confirmar con el equipo la RACI (Tabla 7) y la asignación del modelo de IA (N-06-07).
2. Obtener el estado del cronograma aprobado al 23-11-2026 (o Carta Gantt actualizada) para el capítulo XV (N-06-04).
3. Aprobar o rechazar la renumeración de los IDs duplicados N-03-16 a N-03-21 en el registro (N-06-12).
4. Obtener y revisar la especificación rectora y los documentos de Unidad 1 y Unidad 2 que definan RF/RNF y criterios de aceptación.
5. Construir matriz HU01–HU12 ↔ RF/RNF ↔ endpoint/entidad ↔ prueba ↔ evidencia y estado (incluye relación sprint ↔ historia citada en 6.1).
6. Inspeccionar el directorio `inference`, su cliente desde backend, esquemas, configuración y pruebas.
7. Revisar y normalizar referencias bibliográficas de los capítulos IV y VI en el capítulo XVII (N-06-10).
8. Al abrir el maestro en Word, actualizar campos (Ctrl+A, F9) para regenerar TDC, numeración y referencias cruzadas.
9. Continuar con el **Capítulo VII: Definición de Arquitectura TI**; requiere la plantilla institucional y el informe `TIHI84_ES2_…_AVANCE.docx` (N-06-14).

## 6.1. Respaldos de este hito

- `Proyecto_Aurora_Informe_Final_Maestro_v0.3_pre-capVI.docx`
- `Proyecto_Aurora_Registro_de_Revisiones_v0.7_pre-capVI.docx`
- `Proyecto_Aurora_Estado_Plan_Revision_HU08_pre-capVI.md`

## 7. Regla de cierre

No declarar implementado, probado o validado aquello que solo aparece descrito en documentación. No asumir procesos internos de Nueva Clínica Cordillera: se mantiene como institución de referencia sin compromiso formal ni levantamiento documentado de su flujo interno.
