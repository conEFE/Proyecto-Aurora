# Proyecto Aurora — Estado del plan de revisión y avance del informe

**Actualización:** 23-11-2026  
**Estado general:** revisión en curso; prioridades HU09–HU12 aprobadas e incorporadas; capítulos IV y V redactados en versión inicial.

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

## 6. Próximos pasos

1. Obtener y revisar la especificación rectora y los documentos de Unidad 1 y Unidad 2 que definan RF/RNF y criterios de aceptación.
2. Construir matriz HU01–HU12 ↔ RF/RNF ↔ endpoint/entidad ↔ prueba ↔ evidencia y estado.
3. Inspeccionar el directorio `inference`, su cliente desde backend, esquemas, configuración y pruebas.
4. Revisar y normalizar referencias bibliográficas del capítulo IV en el capítulo XVII.
5. Continuar con el **Capítulo VI: Metodología de Trabajo**, siguiendo la plantilla: metodología y desarrollo de la solución, duración y cronograma, equipo de trabajo y plan de recursos.

## 7. Regla de cierre

No declarar implementado, probado o validado aquello que solo aparece descrito en documentación. No asumir procesos internos de Nueva Clínica Cordillera: se mantiene como institución de referencia sin compromiso formal ni levantamiento documentado de su flujo interno.
