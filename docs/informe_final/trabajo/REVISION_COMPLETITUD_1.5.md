# Revisión de completitud del maestro 1.5-rc (24-11-2026)

Revisión hecha sobre `Proyecto_Aurora_Informe_Final_Maestro.docx` 1.5-rc y su PDF (186 páginas), contra U1, U2,
el código y las iteraciones 12 a 15. Números de párrafo = orden en `word/document.xml` (referencial).

## A. Lo puedo corregir yo (sin insumos del equipo)

**Estado (25-11-2026):** A1, A4, A5 y A6 corregidos en la iteración 16 (maestro 1.6-rc). Pendientes: A2 y A3.
En A4, la cita «OMS, 2021» resultó correcta (la sigla se presenta en la primera cita, en IV) y se mantuvo.

### A1. Afirmaciones desactualizadas por las iteraciones 12 a 15
| Dónde | Dice hoy | Debe decir |
|---|---|---|
| XII, matriz de trazabilidad (RNF de seguridad) | «Parcial: PS-04 no ejecutado» | PS-04 ejecutado el 24-11 (0 altas) |
| XIII, Tabla de disponibilidad, fila Capacidad | «Prueba con 100 usuarios: No ejecutada» | Ejecutada en AWS el 24-11 (p95 14,98 s, 0 errores) |
| XIII, párrafo de brechas para un piloto | pide «monitor externo, alarmas de errores y latencia, y la prueba de carga en ese entorno» | alarmas de disponibilidad y prueba de carga ya hechas; quedan monitor externo y alarmas de latencia/errores |
| X, Tabla 33 (componentes de infraestructura) | sin monitoreo; fuente al 16-11 | agregar chequeo de /health, alarmas y SNS; fuente al 24-11 |
| XII, texto de ejecución de pruebas | «última corrida en la rama principal (16-11-2026)» | CI en verde el 24-11 (2.10.2) |
| XV, ajuste A1 (Sprint 7) | «escaneo de seguridad no ejecutado» | ejecutado el 24-11 |
| XV, hitos | «la prueba de carga se ejecutó después, el 24-11, en entorno local» | también en el entorno de demostración |
| XV, ruta crítica | «antes de la entrega se recomienda ejecutar la prueba de restauración y el escaneo» | ambos hechos el 24-11 |
| VI, Scrumban | «matriz de trazabilidad pendiente del capítulo III» | existe en 12.1.6 |
| IX, tabla de herramientas (inferencia) | «funcionamiento del servicio y del modelo pendiente de inspección (capítulo X)» | inspeccionado en 10.7.1 |
| XV, Gantt y entregables | Sprint 8 «2.6.0–2.10.0»; corte 23-11 | mencionar 2.10.1 y 2.10.2 (24-11) como correcciones posteriores |

### A2. Número de pruebas
Resumen, conclusiones y anexo dicen **314 pruebas** (ejecución formal del 23-11). La suite actual tiene **321**
(2.10.2). Opción: repetir la ejecución con JUnit y cobertura, guardar la evidencia `pruebas_2026-11-24` y actualizar
las Tablas 41 y 42 de XII, el resumen, el abstract y las conclusiones.

### A3. Modelo de IA (10.7.1) más completo
U2 (sección 3.8) explica la CNN, los datos (CBIS-DDSM 2.857 y CMMD 3.744 imágenes), la división, el entrenamiento en
dos etapas, los resultados con distintos umbrales y los 7 intentos hasta el modelo elegido. El maestro solo trae la
Tabla 34 y las métricas del modelo reentrenado. Se puede integrar como «desarrollo del modelo (Unidad 2)», aclarando
que el modelo desplegado se reentrenó con división por paciente y entrada de 672 × 1024, y que los detalles de ese
reentrenamiento no están en el repositorio.

### A4. Referencias
- Sin cita en el texto: AWS «Regions and Availability Zones» (s. f.-b), APA (2020) e ITIL 4 (AXELOS, 2019). Citarlas
  donde corresponde (región en VII/XIII; APA en la introducción o en la nota de formato; ITIL en XIII) o retirarlas.
- «OMS, 2021» en el texto frente a «Organización Mundial de la Salud. (2021)» en la lista: APA pide el nombre completo
  en la primera cita, con la sigla entre corchetes.

### A5. Glosario
24 términos. Faltan siglas usadas 3 o más veces: AWS, RDS, EC2, S3, TLS, HTTPS, DNS, GPU, BPMN, UML, OWASP, ZAP, RACI,
CDN, IAM, KMS, SSE, VAN, TIR, PRI, CBIS-DDSM, CMMD, OMS, FDA, ISO/IEC, JWT, CSP, SNS, RTO/RPO, p95, entre otras.

### A6. Formato
- Un encabezado de nivel 1 vacío antes de «Índice de Tablas» (aparece como línea en blanco en la estructura).
- En el DOCX los índices de tablas y figuras dicen «No se encuentran elementos…» hasta que Word actualiza los campos
  (el PDF ya los trae). Recordar «Actualizar campos» antes de entregar el DOCX, o entregar el PDF.

## B. Requiere insumos del equipo
1. Dedicatoria y agradecimientos (páginas vacías).
2. Cita «Shah et al., 2023» (cap. IV): completar la referencia o reemplazar la cita.
3. Título de 2026c y descripción de 2026b; fechas de OMS 2026, NEMA 2026 y ACR 2025.
4. Correcciones del docente a U1/U2 (para verificar las observaciones U1-xx y U2-xx).
5. Decisiones: capacidad para la meta de 100 usuarios; inferencia el día de la defensa; etiqueta v2.10.2.
6. Lectura final y aceptación de la versión 1.0.

## C. Revisado y sin problemas
- Estructura de la plantilla (95 títulos; los apartados agregados son de nivel 4 o anexos).
- Sin marcas de pendiente, «[…]», «Error!» ni referencias cruzadas rotas en el PDF.
- Cifras coherentes entre capítulos: 18 tablas de la aplicación (19 con la de migraciones), 316 casos, VAN y TIR,
  AUC 0,838, sensibilidad 0,849, p95 local y en AWS, fechas de hitos.
- Resumen (306 palabras en dos párrafos) y abstract equivalentes.
- U1 y U2: todas sus secciones tienen equivalente en el maestro, salvo el detalle del modelo de IA (A3).
