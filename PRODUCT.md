# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

Equipo de un centro de atención primaria de salud (CESFAM o consultorio), en Chile, con alto volumen de pacientes y poco tiempo por caso:

- **ADMINISTRATIVO**: personal de admisión, a menudo con poca experiencia digital. Registra pacientes con consentimiento informado, crea casos, anota síntomas y antecedentes y carga imágenes. Ve la cola priorizada solo como código de caso y nivel.
- **MEDICO**: revisa la cola priorizada, ve imágenes y resultados de IA, valida cada resultado de IA, evalúa o corrige el nivel de triage con motivo, registra la revisión, cierra el caso, firma el reporte y edita los parámetros de triage.
- **ADMIN**: gestiona usuarios y roles y consulta la bitácora de auditoría.

Todos ven el dashboard de métricas agregadas. Además, la comisión evaluadora de INACAP revisa la interfaz y la evidencia (informe, KPIs) como parte del proyecto de título.

## Product Purpose

Apoyar la detección temprana y la priorización (triage) de casos sospechosos de cáncer de mama para que los casos de mayor riesgo se revisen primero. La plataforma **apoya, no reemplaza**, el criterio médico. Que funcione significa que los casos ALTA llegan antes a revisión, que cada decisión queda trazable y que el desempeño de la IA se mide contra el juicio del médico.

## Positioning

Triage transparente y corregible, con la IA siempre subordinada al médico: un puntaje de reglas y factores ponderados que muestra el detalle de cada factor, parámetros versionados que edita el equipo médico, override con motivo obligatorio, validación médica de cada resultado de IA y una firma del médico sobre el reporte. Todo queda auditado.

## Operating Context

- PC de escritorio en admisión o en el box, y notebooks; no hay uso en tablet ni en celular.
- Estados del caso: `ABIERTO → PRIORIZADO → EN_REVISION → CERRADO`, con código anónimo `AUR-AAAA-NNNNNN`.
- Contexto normativo chileno: RUT validado, consentimiento informado y bitácora append-only (Ley 19.628). La firma del reporte es una firma electrónica simple (Ley 19.799).
- Entregables del proyecto de título: informe, manual de instalación, manual de usuario, KPIs (K3, K5, K9…) y rúbrica INACAP.

## Capabilities and Constraints

- Registro de pacientes, casos, síntomas y BI-RADS; carga de mamografías y ecografías cifradas (Fernet) con SHA-256.
- Triage por reglas de escalamiento y puntaje ponderado, cola priorizada, notificaciones de casos ALTA, revisión médica, reporte PDF con metadatos tipo DICOM, dashboard de KPIs y desempeño del modelo por versión.
- **IA simulada**: hoy todo resultado de IA viene del proveedor simulado, lleva `is_simulated = true` y el badge visible «IA SIMULADA», y no tiene valor clínico. Nunca se presenta como resultado clínico real.
- Una CNN (ResNet18) está entrenada fuera del repo pero aún no se integra. YOLO, para localizar la lesión, está en desarrollo.
- Interfaz, mensajes y documentación en español; código en inglés.
- Solo datos ficticios y RUT de prueba fuera de producción.
- Pendiente (E6): cambio de contraseña, cambio obligatorio en el primer ingreso, registro de errores y bloqueo de login.

## Brand Commitments

- Nombre: **Aurora Care** (antes «Proyecto Aurora»; dominio `auroracare.cl`). Logo en `src/assets/logo-aurora.png`.
- Mensajes fijos: «La plataforma apoya, no reemplaza, el criterio médico» y el badge «IA SIMULADA».

## Evidence on Hand

- Código y documentación del repo: `docs/` (changelog por sprint, endpoints, modelo de datos, resultados de tests: 206 tests, 96 % de cobertura).
- Métricas de la CNN medidas fuera del repo (AUC 0,843, sensibilidad 0,843, especificidad 0,664 con umbral 0,35), descritas en el informe.
- No existen pacientes reales, testimonios, centros piloto confirmados ni resultados clínicos: no se inventan.

## Product Principles

1. **El médico decide.** La IA y el triage sugieren; toda sugerencia se puede corregir con motivo y queda registrada.
2. **Transparencia antes que magia.** Cada nivel de prioridad muestra por qué; nada se presenta como más certero de lo que es.
3. **Honestidad sobre la IA.** Lo simulado se ve como simulado, y las métricas declaran su referencia y su tamaño de muestra.
4. **Obvio para quien tiene poco tiempo.** Las tareas frecuentes del administrativo y del médico se completan sin entrenamiento y sin errores costosos.
5. **Privacidad por defecto.** Cada rol ve solo lo que necesita, y todo acceso o cambio sensible queda auditado.

## Accessibility & Inclusion

- **WCAG 2.1 AA** como mínimo: contraste, navegación completa con teclado y compatibilidad con lectores de pantalla.
- Pensado para usuarios no técnicos: etiquetas claras en español, errores que explican qué hacer y acciones irreversibles confirmadas.
