# Proyecto Aurora — Estado del plan de revisión y avance del informe

**Actualización:** 24-11-2026 (iteración 15: diagramas y capturas)
**Versiones vigentes:** documento maestro **1.5-rc** · registro de revisiones v0.24 · PDF `Proyecto_Aurora_Informe_Final.pdf` (186 páginas)
**Estado general:** informe completo en versión candidata, con los cinco ajustes de la rúbrica aplicados. Quedan los
pendientes del equipo (abajo y registro, secciones 4.15 y 4.16). Traspaso al siguiente agente: `../HANDOFF_ITERACION_16.md`.

## Iteración 15 — Diagramas y capturas (maestro 1.5-rc)

Pedida por el usuario («faltan un montón de BPMN, el diagrama de la arquitectura y el cloud»), con U1 y U2 reenviados.

| Capítulo | Figura | Origen |
|---|---|---|
| V (Proceso de negocio afectado) | BPMN del proceso de atención y priorización (página horizontal) | U1, figura 2 |
| VIII | Organigrama (con nota de roles reales y QA no incorporado); proceso de negocio (horizontal) | U1, figuras 7 y 8 |
| X | Diagrama cloud desplegado (reemplaza la figura de infraestructura; horizontal) | Nuevo, `herramientas/diagramas_it15/cloud.html` |
| X | Infraestructura de U1 y de U2 «diseño, no implementado tal cual» | U1 figura 6; U2 figura 8 |
| X | Arquitectura por capas (reemplaza la figura-tabla) y arquitectura de aplicaciones de U1 «diseño» | Nuevo `arquitectura.html`; U1 figura 5 |
| 10.7.1 | Componente de análisis (CNN + YOLO) | Redibujado (`cnn.html`): U2 decía 512 × 512, el código usa 672 × 1024 |
| Anexo nuevo | 8 capturas de la 2.10.2 (local, datos ficticios, IA simulada) | `figuras/capturas_2.10.2/` |

Diagramas: HTML + `render.cjs` (Playwright) → PNG. Registro 4.20. VII: se retiró la frase «los diagramas de la formulación no se reproducen».

## Iteración 14 — Escaneo de seguridad, restauración y monitoreo (maestro 1.4-rc)

Elegida por el usuario: restauración, ZAP y monitoreo con alarmas (aprobó usar su correo para las alertas).

- **ZAP** (workflow `zap.yml`, sobre el stack levantado en el CI, no sobre la demo): 0 altas, 1 media, 3 bajas. COOP y
  CORP agregados en `deploy/Caddyfile` (`a2f4da4`, desplegado); aceptados `style-src 'unsafe-inline'` y la falta de COEP.
  Evidencia: `evidencias/zap_2026-11-24/`. La API autenticada no quedó cubierta.
- **Restauración:** volcado diario de las 06:15 UTC restaurado en un esquema temporal: 19 tablas coincidentes, 258
  imágenes en S3, 5 descifradas con hash correcto, ≈ 3 s. Evidencia: `evidencias/restauracion_2026-11-24/`.
- **Monitoreo:** `deploy/monitor_salud.sh` (crontab, cada minuto) → CloudWatch Logs `/aurora/monitor` → métrica
  `Aurora/ChequeosOK` → alarma `aurora-demo-sin-respuesta` y `aurora-ec2-estado` → SNS `aurora-alertas` (correo de
  Felipe, confirmado). Todo en us-east-2 (SNS en us-east-1 está bloqueado por la política del proyecto, así que no se usa
  el chequeo de Route 53). Probado: ALARM durante la instalación y OK a las 13:36 UTC.
- **Informe:** nuevo 12.1.5 (Tabla 45; la Matriz de trazabilidad pasa a 12.1.6); resumen, abstract, XI (K3), XII (PS-04),
  XIII (Tabla de disponibilidad, continuidad), 14.3.1, XV (riesgos) y XVI. Registro 4.19.

## Iteración 13 — Rendimiento en el entorno de demostración (maestro 1.3-rc)

Pedida por el usuario («mide en AWS»); eligió hacerlo sobre una copia de la base y luego autorizó desplegar la 2.10.2.

- **Método:** API apuntada a una copia de la base en el esquema temporal `carga` de la misma RDS (sin tocar la bitácora
  real; borrada al terminar). Generador en el propio servidor (el externo pasa por un proxy que limita conexiones).
- **Resultados (2.10.2):** ≈ 20 solicitudes/s con un proceso; p95 923 ms (10 usuarios), 2.308 ms (25), 6.132 ms (50);
  **PC-01 (100, 15 min): 15.013 solicitudes, 0 errores, p95 14.979 ms → no cumple**. `/health` estable todo el tiempo.
- **Segundo defecto** (2.10.1, 100 usuarios): bloqueo entre hilos y conexiones; la API y `/health` dejaban de responder.
  Reproducido en local y corregido en **2.10.2** (`1ec7904`, `ConcurrencyLimitMiddleware`, 321 pruebas), desplegada el
  24-11 con respaldo `backups/aurora-20261124T032923Z.sql.gz`.
- **Informe:** nuevo 12.1.4 (Tabla 44; las siguientes se renumeran; «Matriz de trazabilidad» pasa a 12.1.5); resumen,
  abstract, XI (indicador p95), XII (PC-01 y RNF03), XIII (versión 2.10.2), Tabla de factibilidad de 14.3.1 y XVI.
  Registro 4.18 (D-13-01..03, N-12-01 cerrada, N-13-01..03).
- Evidencia: `evidencias/rendimiento_aws_2026-11-24/` (README con método, tablas y limitaciones).

## Iteración 12 — Despliegue de la corrección (maestro 1.2-rc)

Decidida por el usuario el 24-11-2026 («Desplegar la corrección»).

- **Código:** la corrección `9043857` entró a `main` como **2.10.1** (`eecc255`, autoría del equipo; 316 pruebas, lint y
  typecheck sin errores). Imágenes publicadas con «Publicar imágenes» y desplegadas por Session Manager con respaldo previo
  (`backups/aurora-20261124T022416Z.sql.gz`). Sin migraciones. Verificado: sitio y `/api/health` en 200, inicio de sesión
  responde. Volver atrás: `AURORA_VERSION=sha-d945a06…` (`docs/ESTADO_AWS.md` en `main`).
- **Informe:** 12.1.3 («se desplegó… el rendimiento en ese entorno no se ha medido»), XIII (versión publicada 2.10.1) y
  Tabla 58 de 14.3.1. Registro v0.21, sección 4.17 (D-12-01; N-11-07 cerrada; N-12-01 rendimiento en AWS sin medir;
  N-12-02 sin etiqueta `v2.10.1`). PDF de 167 páginas.
- **Sin cambios:** las «314 pruebas» del resumen, de XVI y del anexo corresponden a la ejecución del 23-11 (evidencia
  `pruebas_2026-11-23`); la de 316 está en 12.1.3.

## Iteración 11 — Plantilla y rúbrica de defensa (maestro 1.1-rc)

Aprobada por el usuario el 24-11-2026 («aplica los cinco puntos»).

| Ajuste | Indicador EA5 | Cambio en el maestro |
|---|---|---|
| (a) | Plantilla | 10.4.3 con su título literal; «Componente de análisis automatizado de imágenes» pasa a 10.7.1; 5 encabezados vacíos retirados |
| (b) | 4. Innovación | 4.8 «Soluciones existentes y diferenciación» con Tabla 6 (Transpara, Lunit INSIGHT MMG, ProFound AI) y evidencia (Dembrower 2020, Freeman 2021, MASAI 2023) |
| (c) | 5. Evaluación integral | 14.3.1 síntesis de factibilidad técnica, operativa, económica, legal y ambiental (Tabla 58), corrigiendo lo de U2 (sin capacitación; institución sin compromiso) |
| (d) | 2 y 3. Complementariedad y sustentabilidad | 9.2.1 integración del stack (Tabla 28); 8.3.1 sustentabilidad |
| (e) | 6. Estabilidad y rendimiento | 12.1.3 prueba de rendimiento local: PC-01 con 100 usuarios durante 15 min, **p95 3.974 ms: no cumple la meta de 3 s** (sí hasta 50 usuarios); XI, XII, XV, XVI, resumen y abstract actualizados |

**Hallazgo y corrección de código (no solo documental).** La primera corrida con 50 usuarios bloqueó la API por completo
(100 % de errores por tiempo agotado). Causa: el middleware de métricas pedía una segunda conexión al mismo pool que retiene
el endpoint. Corregido en `9043857` (pool auxiliar, escrituras y carga de imágenes fuera del bucle de eventos, prueba de
regresión; 316 pruebas, 0 fallos). **No desplegado**: `demo.auroracare.cl` sigue en la 2.10.0 con el defecto.

**Revisión de nube frente a HU:** `trabajo/REVISION_NUBE_VS_HU.md`. Ningún componente de nube descartado impide una HU;
la inferencia fuera de la nube afecta el valor de HU08 y HU12 (respaldo simulado si el PC está apagado).

**Correcciones de texto derivadas:** la recomendación «copias fuera de la región» se cambió por «copia cifrada fuera de AWS»
(el proyecto de AWS no admite acciones entre regiones). Seis referencias APA nuevas; término CADe/CADx en el glosario.

**No verificado (no entró al informe):** el régimen chileno de control sanitario de dispositivos médicos aplicable al
software de imágenes (el sitio de la fuente no era accesible); el informe solo declara la evaluación como requisito previo
a un uso clínico (N-11-02).

## Revisión contra plantilla y rúbrica (23-11-2026, diagnóstico previo a la iteración 11)

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
