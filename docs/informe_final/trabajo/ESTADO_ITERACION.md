# Proyecto Aurora — Estado del plan de revisión y avance del informe

**Actualización:** 23-11-2026 (revisión contra plantilla y rúbrica; iteración 11 planificada)  
**Versiones vigentes:** documento maestro **1.0-rc** · registro de revisiones v0.19 · PDF `Proyecto_Aurora_Informe_Final.pdf` (160 páginas)  
**Estado general:** informe completo en versión candidata. La revisión contra la plantilla institucional y la rúbrica de defensa
(Escala de Apreciación N°5) dejó cinco mejoras propuestas (iteración 11), aún **sin aplicar y sin aprobación del equipo**. Siguen
los pendientes del equipo antes de la entrega (ver abajo y registro, sección 4.15). Traspaso al siguiente agente: `../HANDOFF_ITERACION_11.md`.

## Revisión contra plantilla y rúbrica (23-11-2026, sin cambios en el maestro)

**Insumos:** `Plantilla_Informe_Final_TIHI84_Apoquindo.docx` y `TIHI84_U3_ES3_EA5.xlsx` (hoja EA_Calidad, 6 indicadores).
Los dos documentos fuente reenviados por el usuario (`Neira_Campos_Meneses.docx` = U2 y `Campos_Meneses_Neira.docx` = U1) son
idénticos (sha256) a los ya usados en las iteraciones 0–10; no aportan contenido nuevo.

**Plantilla:** los 95 títulos de la plantilla están presentes y en orden. Dos desvíos introducidos por nosotros:
1. 10.4.3 quedó como «Diccionario de datos.»; la plantilla dice literalmente «Diccionario de datos (puede ir como anexo).» → revertir.
2. Se agregó un 10.8 que no existe en la plantilla → moverlo como 10.7.1 (título de nivel 4 bajo 10.7).

**Rúbrica (indicador, puntaje, estado en el maestro 1.0-rc):**

| Ind. | Criterio | Pje. | Estado | Brecha |
|---|---|---|---|---|
| 1 | Plataformas adecuadas | 15 | Cubierto | IX (AHP) y X justifican plataformas. |
| 2 | Herramientas se complementan | 20 | Parcial | Falta una subsección explícita de integración del stack (cómo encajan FastAPI, PostgreSQL, React, servicio de inferencia, AWS, CI). |
| 3 | Procesos de negocio y solución sustentable | 20 | Parcial | VIII describe procesos; falta argumento de sustentabilidad (operación, costos recurrentes, mantención, continuidad). |
| 4 | Innovación frente a soluciones existentes | 15 | **No cubierto** | No hay comparación con soluciones existentes. U1 (3.1) solo nombra «revisión bibliográfica y de proyectos similares» como instrumento, sin resultados; U2 no tiene contenido. Requiere fuentes externas reales. |
| 5 | Buenas prácticas/normas y evaluación técnica, operativa, económica, legal y ambiental | 15 | Parcial | Económica completa (XIV); normas en XII. El «Estudio de factibilidad» de U2 (técnica, económica, implementativa; líneas 685–697 del texto de U2) **no se integró** al maestro. No hay factibilidad ambiental en ninguna fuente; operativa y legal no están explícitas. |
| 6 | Estabilidad, rendimiento y buen diseño | 15 | Parcial | p95 aparece solo como meta (XI); no hay prueba de rendimiento ejecutada (Locust no implementado). |

**Contradicciones a resolver al reutilizar la factibilidad implementativa de U2:**
- U2 dice «capacitación de usuarios (planificada del 10 al 25 de noviembre)»; lo declarado por el equipo es que **no hubo capacitación**,
  sino una presentación el 20-11-2026 a 2 médicos y 1 enfermera (D-15-02). Reescribir como planificado y no ejecutado.
- U2 llama a Nueva Clínica Cordillera «cliente piloto» con interés; mantener la regla: institución de referencia, sin compromiso
  formal (riesgo R12), no cliente ni patrocinador ni piloto.

**Correcciones del docente:** no se han recibido. Servirían para verificar que las observaciones U1-xx y U2-xx del registro estén
efectivamente atendidas; se pidieron al usuario.

## Iteración 10 — Cierre editorial (maestro 1.0-rc)

- Siete figuras anchas en páginas horizontales (Gantt línea base, BPMN 1–3, topología, arquitectura, Gantt de ejecución), con el encabezado del capítulo.
- Tabla de contenido, índice de tablas (60) e índice de figuras (11) regenerados en el PDF; Word pedirá actualizar campos al abrir.
- Tabla de historias con leyenda (Tabla 1), anchos y letra uniformes; nota de plantilla retirada del diccionario de datos; encabezados vacíos eliminados.
- Portada con fecha «Diciembre, 2026». Sección interna «Control de integración» retirada (su función la cumple el registro).
- Exportación reproducible: `python3 herramientas/exportar_pdf.py trabajo/Proyecto_Aurora_Informe_Final_Maestro.docx trabajo/Proyecto_Aurora_Informe_Final.pdf`.

### Pendientes del equipo antes de la entrega
1. Dedicatoria y agradecimientos (páginas vacías).
2. Cita «Shah et al., 2023» (cap. IV): completar o reemplazar.
3. Título del informe de Unidad 2 (2026c) y descripción de 2026b; fechas de OMS 2026, NEMA 2026 y ACR 2025.
4. Notas/acta de la revisión del 20-11 (opcional, como anexo).
5. Prueba de restauración de respaldo y escaneo ZAP (actualizar XII y XIII si se ejecutan).
6. Alerta de presupuesto AWS ≥ USD 30; comentario de K5 en el código.
7. Confirmar CU18 y los casos PI-06 a PS-08; contrastar con la plantilla institucional.
8. Lectura completa y aceptación de la versión 1.0.

## 000000000. Iteración 9 — Capítulos XVI a XVIII (maestro v0.13)

- **XVI:** conclusiones por objetivo específico, gestión y aprendizajes; nueve recomendaciones.
- **XVII:** glosario de 23 términos (estilo «Glorario») y 56 referencias APA 7 (estilo «Bibliografía y Referencias»), contrastadas con todas las citas del texto; «s. f.» normalizado.
- **XVIII:** Anexo 1 especificación de CU01–CU18; Anexo 2 diccionario de datos de las 18 tablas (generado del código); Anexo 3 configuración inicial del triage (verificada en código); Anexo 4 evidencia de pruebas; material complementario.
- **Pendientes:** Shah et al. (2023) sin identificar (N-17-01); título del informe de Unidad 2 (N-17-02); fechas de fuentes web (N-17-03); descripción de 2026b (N-17-04).
- **Siguiente:** iteración 10 — cierre editorial: TDC e índices, páginas horizontales para diagramas anchos, tabla de historias, retiro de «Control de integración», PDF final y cierre del registro.

## 00000000. Iteración 8 — Capítulos I a V (maestro v0.12)

- **Decisiones del usuario:** K5 = exactitud respecto de la validación médica ≥ 0,85 con ≥ 30 imágenes (D-08-01); RF09 agregado (D-08-02); presupuesto de Unidad 2 vigente (D-08-03).
- **Resumen, abstract, palabras clave e introducción** redactados (antes vacíos).
- **Capítulo III:** criterios de HU01–HU07 de la formulación inicial (Tabla 1); verificación de HU01–HU12 con pruebas (Tabla 2: verificadas, salvo HU06/HU07 parciales por interfaz); RF01–RF09 (Tabla 3; RF08 actualizado, RF09 nuevo); RNF01–RNF05 (Tabla 4); restricciones; títulos ajustados a la plantilla (3.1.x).
- **V, XI, XII, XIV** sincronizados con las decisiones.
- **Pendiente menor:** comentario del código del dashboard dice 90% (N-08-01); anchos de la tabla de historias (N-08-04, iteración 10).
- **Siguiente:** iteración 9 — conclusiones y recomendaciones, referencias APA y glosario, anexos (diccionario de datos, especificación de casos de uso, matriz de riesgos).

## 0000000. Iteración 7 — Capítulo XV (maestro v0.11)

- **Carta Gantt real (Figura 11, `figuras/cap15_gantt_estado.png`, regenerable con `herramientas/gantt_xv.py`):** línea base frente a ejecución, color por responsable, hitos cumplidos y sin evidencia, corte 23-11.
- **Criterio D-15-01:** no se inventan fechas de ejecución; S1–S6 según Unidad 2, desde octubre según Git/CHANGELOG; sin registro = «sin registro de ejecución».
- **Tablas:** estado por fase (50), entregables por sprint y responsable (51), ajustes A1–A4 con resultado (52), hitos (53), matriz de riesgos actualizada con R18 (54).
- **Desviaciones:** Sprint 7 +11 días (cierre 11-11); Sprint 8 cierre 16-11 con pendientes; validación clínica, capacitación y piloto sin registro.
- **Hechos declarados por el equipo (D-15-02):** entrenamiento del modelo por Juan Francisco Meneses (sep.–nov., fila 3.6b); presentación y revisión del prototipo con 2 médicos y 1 enfermera el 20-11 (revisión funcional, no validación clínica formal); sin capacitación independiente. Actualizados XV y XII (PB-01).
- **Para el equipo:** si existen notas o acta de la revisión del 20-11, adjuntarlas como anexo; siguen sin evidencia la firma del SLA, el acta de decisión del modelo y el piloto.
- **Siguiente:** iteración 8 — revisión de capítulos I–V con la evidencia acumulada (criterios de aceptación, K5, RF09, interesados).

## 000000. Iteración 6 — Capítulo XIV y equipo de inferencia (maestro v0.10)

- **Dato del usuario:** equipo de inferencia HP Victus 16 (i7-11800H, 16 GB, RTX 3060 Laptop 6 GB, SSD 512 GB PCIe 4.0 + 1 TB PCIe 3.0); incorporado en VI (Tabla 8), X (Tablas 26 y 27) y XIV.
- **XIV:** mercado y demanda como supuesto no validado (Tabla 43); presupuesto estimado del prototipo $47.074.638 como valoración (Tabla 44); costo real de la demostración ≈ USD 26/mes con créditos USD 177,53 vigentes hasta el 10-05-2027, frente a USD 241,09/mes estimados para un piloto (Tabla 45); cotización de equipos (Tabla 46); flujo de caja, VAN $134.801.449, TIR 45,0%, recuperación 2,84 años y sensibilidad, recalculados y coincidentes (Tablas 47–49).
- **Pendientes:** confirmar presupuesto aprobado (N-14-03); ajustar alerta de presupuesto AWS a ≥ USD 26 (N-14-04); costear licencia YOLO (N-14-06); costo del dominio (N-14-07).
- **Siguiente:** iteración 7 — capítulo XV (requiere estado del cronograma aprobado por el equipo).

## 00000. Iteración 5 — Capítulos XI y XIII (maestro v0.9)

- **XI KPI:** K1–K11 con fórmula, meta, implementación en la plataforma y estado de medición (Tabla 28); umbrales y responsables (Tabla 29). Implementados en el dashboard: K1, K2, K5, K6; K11 por diseño (probado). Ningún KPI medido en operación real.
- **XI SLA:** propuesta para un eventual piloto, institución usuaria por definir (Tablas 30–31); se retira a NCC como «cliente».
- **XIII:** disponibilidad planificado vs. estado actual (Tabla 38); BIA (Tabla 39); escenarios con preparación (Tabla 40); configuración (Tabla 41); versionado, despliegue manual, cambios e incidentes (Tabla 42, incidente real del 15-11).
- **Decisiones pendientes:** definición única de K5 (N-11-01) y metas del capítulo V sin KPI (N-11-03).
- **Acción recomendada antes de la defensa:** probar la restauración de un respaldo (N-13-02).
- **Siguiente:** iteración 6 — capítulo XIV (factibilidad económica).

## 0000. Iteración 4 — Capítulo XII (maestro v0.8)

- **Ejecución propia (23-11-2026, commit 53ee1b1):** 314/314 pruebas aprobadas; cobertura 97% (servicios 96,1%); ruff, ESLint y TypeScript sin errores. Evidencia en `../evidencias/pruebas_2026-11-23/`. CI de `main` en verde (run 61, 16-11-2026).
- **12.1 Plan de pruebas:** parámetros (Tabla 28), matriz de casos con la prueba automatizada que implementa cada uno y su resultado (Tabla 29), resultados (Tabla 30), pruebas por archivo (Tabla 31), matriz de trazabilidad RF/RNF–HU–CU–prueba–evidencia (Tabla 32).
- **12.2 Normas:** Tabla 33 con aplicación concreta en el proyecto; sin declaración de cumplimiento.
- **No ejecutado:** ZAP (0 corridas), carga y estrés (Locust no implementado), alfa y beta (sin evidencia), pruebas de interfaz.
- **Observaciones:** N-12-01 a N-12-09 (registro v0.12, sección 4.8). Para aprobar: RF09 para HU10 y los casos de prueba nuevos (PI-06 a PS-08).
- **Siguiente:** iteración 5 — capítulos XI (KPI y SLA) y XIII (plan de implementación).

## 000. Iteración 3 — Capítulo X (maestro v0.7)

- **10.1 BPMN:** tres procesos de Unidad 2 reutilizados; reglas contrastadas con el código (escalamiento BI-RADS 4–5 o síntoma de alarma, umbrales 60/30, firma con contraseña, cierre con imágenes validadas).
- **10.2 Casos de uso:** diagrama y catálogo actualizados (CU17 implementado en 2.3.0; CU18 nuevo para solicitudes de titulares, a confirmar).
- **10.3 Componentes, 10.5 Topología, 10.6 Infraestructura, 10.7 Arquitectura:** diagramas nuevos desde código y `docs/ESTADO_AWS.md` (D-07-01), reemplazan el diseño objetivo de Unidad 2.
- **10.4 Modelo de datos:** modelo lógico generado desde SQLAlchemy (18 tablas; 5 relaciones 1:1), modelo físico (Tabla 24); diccionario de datos derivado a anexos.
- **10.8 Componente de análisis automatizado (subsección agregada):** servicio de inferencia inspeccionado; métricas declaradas (AUC 0,838; sens. 0,849; esp. 0,641; mAP50 0,538) no reproducibles; umbral 0,35 fijo en código; sin validación clínica.
- **Observaciones:** N-10-01 a N-10-09 (registro v0.11, sección 4.7) y evidencia de las observaciones técnicas del componente inference (identificación, contrato, preprocesamiento y persistencia verificados en código; pruebas por ejecutar; sin validación clínica).
- **Figuras:** `../figuras/` (regenerables con `herramientas/diagramas_cap10.py`).
- **Siguiente:** iteración 4 — capítulo XII (ejecución propia de la suite de pruebas y matriz de trazabilidad HU ↔ RF/RNF ↔ endpoint/entidad ↔ prueba).

## 00. Iteración 2 — Capítulo IX (maestro v0.6)

- **Decisión D-07-01:** se documenta la arquitectura actual implementada; no hay cambios arquitectónicos pendientes y las mejoras menores quedan fuera de esta entrega. El capítulo X usará diagramas de la arquitectura actual.
- **9.1 Análisis cualitativo/cuantitativo:** criterios (Tabla 14), AHP recalculado (Tabla 15; RC 0,013), escala anclada (Tabla 16), ventajas y desventajas (Tabla 17), matriz ponderada (Tabla 18), sensibilidad (Tabla 19) y consideraciones posteriores (región us-east-2 de la demostración; licencia AGPL-3.0 de YOLO; IA en dos etapas).
- **9.2 Herramientas:** versiones reales de dependencias al 23-11-2026 con estado (Tabla 20) y servicios TI (Tabla 21). Locust, Prometheus y Grafana: no implementados; Cloudflare: no adoptado; ZAP: configurado sin resultados revisados.
- **Observaciones:** N-09-01 a N-09-08 (registro v0.10, sección 4.6). Abiertas: N-09-03 (pruebas, it. 4), N-09-04 (número de tablas, it. 3), N-09-06 (región para datos reales), N-09-07 (licencia YOLO), N-09-08 (cita Stack Overflow).
- **Siguiente:** iteración 3 — capítulo X (arquitectura a implementar) con inspección directa de `backend/inference_service`.

## 0. Iteración 1 — Capítulos VII y VIII (maestro v0.5)

- **VII Definición de arquitectura TI (7.1):** arquitectura N-tier cliente-servidor con API REST; monolito modular con servicio de análisis de imágenes desacoplado tras interfaz de proveedor; Tabla 10 (capas, componentes y nivel de evidencia), Tabla 11 (decisiones de arquitectura); relación con requerimientos; evolución respecto de Unidad 1 (los diagramas de U1 no se reproducen por incluir componentes no evidenciados: Grafana, Prometheus, gRPC, Cloudflare, DICOM en S3, sa-east-1).
- **VIII Arquitectura empresarial (8.1–8.3):** emprendimiento SaaS B2B con estructura plana (Tabla 12; QA como rol contemplado no asignado); procesos de negocio con actor, apoyo previsto e historias HU01–HU12 (Tabla 13); revisión y evaluación asignadas al médico (corrige el diagrama de U1); limitación de doble registro por falta de integración HIS/RIS/PACS.
- **Evidencia:** estructura de capas verificada por inspección de la organización del código; entorno desplegado según documentación del repositorio; sin ejecución de pruebas.
- **Observaciones:** N-07-01 a N-07-06 (registro v0.9, sección 4.5). Abiertas: N-07-02 (QA), N-07-04 (plantilla), N-07-06 (inspección de `inference_service`, iteración 3).
- **Siguiente:** iteración 2 — capítulo IX (tecnologías: AHP de Unidad 2 contrastado con versiones reales de dependencias).

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
