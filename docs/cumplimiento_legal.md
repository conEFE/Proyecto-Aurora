# Cumplimiento legal en protección de datos — Proyecto Aurora 2.5.0

Documento de cumplimiento de la plataforma frente a la normativa chilena de datos personales y de salud.
Fecha: 10-11-2026. **Validado por el equipo del proyecto el 10-11-2026**, incluido el texto de consentimiento v1.

> **Advertencia.** Es un análisis técnico hecho por el equipo del proyecto, no una asesoría legal. Antes de
> tratar datos reales de pacientes, un abogado o el encargado de protección de datos del establecimiento debe
> validarlo. En desarrollo y en las demostraciones solo se usan datos ficticios y RUT de prueba.

## 1. Marco normativo

| Norma | Qué regula | Vigencia |
|---|---|---|
| **Ley 19.628** sobre protección de la vida privada | Tratamiento de datos personales. Los datos de salud son datos sensibles | Vigente hasta que la reemplace la Ley 21.719 |
| **Ley 21.719** (modifica y reemplaza a la Ley 19.628) | Principios, derechos de los titulares, decisiones automatizadas, evaluación de impacto, seguridad, transferencias internacionales. Crea la Agencia de Protección de Datos Personales | **1 de diciembre de 2026**. Hay un proyecto en el Senado (Boletín 18.623-07) que la posterga a 2027, pero aún no es ley |
| **Ley 20.584** de derechos y deberes de los pacientes y su reglamento de fichas clínicas | Confidencialidad de la ficha clínica y plazo de conservación (al menos 15 años) | Vigente |
| **Ley 19.799** de firma electrónica | Valor de la firma del médico sobre el reporte | Vigente (hoy se usa firma electrónica simple) |

**Rol de la plataforma.** El **responsable** del tratamiento es el establecimiento de salud que usa Aurora.
Aurora es la herramienta, y quien la opere o la aloje (por ejemplo, el proveedor de nube) es **encargado** del
tratamiento.

## 2. Matriz de cumplimiento

Estado: ✅ implementado y con pruebas · 🟡 parcial o depende del despliegue · 📄 lo cubre un procedimiento de este
documento · ⏳ pendiente.

| Requisito | Norma | Cómo lo cumple Aurora | Evidencia | Estado |
|---|---|---|---|---|
| **Consentimiento** para datos sensibles (salud), específico e informado | 19.628 art. 10; 21.719 | Es obligatorio antes de crear un caso. El texto se muestra completo al registrar al paciente y se guarda **qué versión aceptó**, quién lo registró y cuándo. Un texto obsoleto se rechaza (409) | `consent_texts`, `patient_consent_events`; `test_privacy.py` | ✅ |
| **Información al titular** (responsable, finalidad, datos, derechos, conservación, alojamiento) | 21.719 (transparencia) | El texto de consentimiento v1 (`2026-11-v1`) cubre esos puntos en 8 secciones | `backend/app/services/consent_text.py` | ✅ (validar redacción con el establecimiento) |
| **Retiro del consentimiento** en cualquier momento | 21.719 | Endpoint y acción en «Privacidad». Bloquea casos e imágenes nuevos. Lo anterior sigue siendo lícito y la ficha se conserva | `POST /patients/{id}/consent/withdraw` | ✅ |
| **Finalidad y proporcionalidad** | 21.719 (principios) | Solo los datos necesarios para el triage. El PDF identifica el caso con un código anónimo. El ADMIN no accede a datos clínicos. Los registros de auditoría y de errores no guardan RUT, nombres ni términos de búsqueda | Matriz de permisos; `test_users_patients.py`; `test_account_security.py` | ✅ |
| **Calidad / rectificación** | 21.719 | Edición de pacientes (`PUT /patients/{id}`), RUT validado y solicitudes de rectificación registradas | `test_users_patients.py`, `test_privacy.py` | ✅ |
| **Derecho de acceso y portabilidad** | 21.719 | Exportación completa en JSON estructurado: paciente, consentimientos, casos, triage, imágenes (metadatos), IA, revisión, reportes y solicitudes. Solo la puede hacer un MEDICO y queda auditada (`EXPORT`) | `GET /patients/{id}/export` | ✅ (las imágenes se entregan aparte, a pedido) |
| **Supresión y bloqueo** | 21.719; 20.584 | La ficha clínica debe conservarse, así que la supresión se reemplaza por **bloqueo**: los datos se conservan, pero no se editan, no aparecen en las búsquedas y no admiten casos nuevos. Exige que los casos estén cerrados | `POST /patients/{id}/block` / `unblock` | ✅ |
| **Oposición** | 21.719 | Se registra como solicitud. En la práctica se resuelve con el retiro del consentimiento o el bloqueo | `data_subject_requests` | ✅ |
| **Plazo de respuesta** (30 días corridos, prorrogables una vez) | 21.719 | Registro de solicitudes con fecha de recepción, vencimiento automático a 30 días, estados, respuesta obligatoria al cerrar y alerta de vencidas. El ADMIN ve un resumen sin datos de pacientes | `/privacy/requests`, `/privacy/requests/summary` | ✅ (la prórroga se anota en la respuesta) |
| **Decisiones automatizadas** (derecho a no ser objeto de decisiones basadas solo en tratamiento automatizado) | 21.719 art. 8 bis | Ninguna decisión es solo automática. El triage muestra su desglose (es explicable). El médico valida cada resultado de IA, puede corregir el nivel de triage con un motivo, registra la revisión y **firma** el reporte. La IA simulada se marca siempre | Sprints 5–6, 2.1.0, 2.2.0; `test_validation.py`, `test_triage_api.py` | ✅ |
| **Evaluación de impacto** (tratamiento de alto riesgo) | 21.719 art. 15 ter | Ver la sección 3 | Este documento | 📄 |
| **Seguridad** (medidas técnicas y organizativas) | 21.719; 19.628 art. 11 | Control de acceso por rol leído desde la BD, contraseñas bcrypt con política y cambio obligatorio, bloqueo por intentos, revocación de sesiones, imágenes cifradas (Fernet, y SSE-KMS en S3), encabezados de seguridad, dependencias sin vulnerabilidades conocidas, rotación de secretos. Despliegue preparado con TLS automático, EBS/S3/respaldos cifrados con KMS y sin puerto 22. Revisión OWASP en `seguridad_owasp.md` | `test_account_security.py`, `test_storage_s3.py`, `test_rotate_secrets.py`; `docs/seguridad_owasp.md`; `docs/despliegue_aws.md` | ✅ en la aplicación · 🟡 se cumple al desplegar según la guía |
| **Registro y responsabilidad** (poder demostrar el cumplimiento) | 21.719 (responsabilidad) | Bitácora append-only (un trigger impide modificarla) de accesos (`VIEW`), cambios, exportaciones, consentimientos, bloqueos y firmas. Registro de errores 5xx | `audit_log`, `error_log` | ✅ |
| **Notificación de vulneraciones de seguridad** | 21.719 | Ver la sección 4 | Este documento | 📄 |
| **Transferencia internacional** (alojamiento fuera de Chile) | 21.719 | Ver la sección 6 | Este documento | 📄 · ⏳ decisión de región |
| **Encargado del tratamiento** (proveedor de nube) | 21.719 | Contrato de tratamiento de datos (DPA) del proveedor. Ver la sección 6 | — | ⏳ al desplegar |
| **Confidencialidad de la ficha clínica** | 20.584 | El acceso está limitado a MEDICO y ADMINISTRATIVO y queda auditado. El ADMIN no ve datos clínicos | Matriz de permisos | 🟡 cualquier MEDICO o ADMINISTRATIVO ve todos los casos (sin asignación por equipo tratante); decisión de diseño a revisar |
| **Conservación limitada** | 21.719; 20.584 | Ver la sección 5 | Este documento | 📄 · ⏳ tarea de anonimización al vencer el plazo |

## 3. Evaluación de impacto en protección de datos (EIPD)

La Ley 21.719 exige una evaluación previa cuando el tratamiento puede generar un alto riesgo. Aurora trata
**datos de salud (sensibles)** y hace una **evaluación automatizada** (triage asistido por IA), así que se
considera obligatoria.

### 3.1 Descripción del tratamiento
- **Titulares:** pacientes con sospecha de cáncer de mama derivados al establecimiento.
- **Datos:** identificación (RUT, nombre, fecha de nacimiento, sexo), antecedentes (familiares y personales),
  síntomas, BI-RADS informado, imágenes mamarias, resultados de IA, nivel de triage, revisión y reporte médico.
- **Finalidad:** priorizar casos y apoyar la revisión médica. No se usa para otros fines.
- **Usuarios:** administrativos (registro), médicos (revisión) y administradores (cuentas, sin datos clínicos).
- **Ciclo de vida:** registro con consentimiento → caso → imágenes → IA y triage → revisión y firma → cierre →
  conservación (ficha) → anonimización o eliminación al vencer el plazo.

### 3.2 Necesidad y proporcionalidad
Los datos que se recogen son los que usa el triage (edad, antecedentes, síntomas, BI-RADS) y los que identifican al
paciente en su ficha. El reporte PDF y los registros técnicos no llevan datos identificables. La IA solo apoya, y el
médico decide.

### 3.3 Riesgos y medidas

| Riesgo | Prob. | Impacto | Medidas | Riesgo residual |
|---|:-:|:-:|---|:-:|
| Acceso no autorizado a datos clínicos | Media | Alto | Control de acceso por rol, mínimo privilegio, bloqueo por intentos, revocación de sesiones, auditoría de accesos | Bajo |
| Robo de credenciales o fuerza bruta | Media | Alto | Política de contraseñas, bloqueo de cuenta, límite de intentos por IP, tokens de 30 min | Bajo |
| Filtración de imágenes o de la base de datos | Baja | Muy alto | Imágenes cifradas (Fernet + SSE-KMS en S3). Guía de despliegue: disco EBS y respaldos cifrados con KMS, TLS automático, bucket privado | Bajo al desplegar según la guía |
| Decisión clínica tomada solo por la IA | Media | Muy alto | Médico en el circuito (valida, corrige, firma), triage explicable, badge IA SIMULADA, métricas del modelo por versión (K5) | Bajo |
| Sesgo o error del modelo de IA | Media | Alto | Validación médica de cada resultado, métricas de concordancia y desempeño por versión, KPI K5 solo con resultados reales | Medio (depende del modelo real, E10) |
| Uso para otra finalidad o cesión indebida | Baja | Alto | Finalidad en el consentimiento, exportación solo por MEDICO y auditada | Bajo |
| Imposibilidad de ejercer derechos a tiempo | Media | Medio | Registro de solicitudes con plazo y alerta de vencidas, exportación, bloqueo | Bajo |
| Datos conservados más allá de lo necesario | Media | Medio | Política de conservación (sección 5). **Pendiente:** tarea automática de anonimización | Medio |
| Transferencia a un país sin protección adecuada | Media | Alto | Región y garantías contractuales (sección 6) | Bajo con DPA |
| Datos personales en registros técnicos | Baja | Medio | Auditoría sin RUT ni términos de búsqueda, `error_log` saneado, nombres de archivo aleatorios en disco | Bajo |

### 3.4 Conclusión
El tratamiento es aceptable si antes de usar datos reales se cumplen tres condiciones: (1) desplegar según
`docs/despliegue_aws.md` (cifrado en reposo de la BD y TLS); (2) contrato de tratamiento con el proveedor de nube y una decisión sobre la región; y
(3) validación de este documento y del texto de consentimiento por el establecimiento. La EIPD se revisa al cambiar
el modelo de IA (E10) o la infraestructura.

## 4. Procedimiento ante vulneraciones de seguridad

1. **Detección.** Revisar la bitácora (`LOGIN_FAIL` con motivo `bloqueo` o `limite_ip`, exportaciones inusuales,
   accesos `VIEW` masivos), el registro de errores 5xx y las alertas de la infraestructura (S7).
2. **Contención (inmediata).**
   - Desactivar las cuentas comprometidas o restablecer sus contraseñas, lo que revoca sus sesiones.
   - Rotar `SECRET_KEY`, que invalida todos los tokens.
   - Si la clave de cifrado de imágenes se vio comprometida, rotarla también.
3. **Evaluación.** Qué datos y cuántos titulares se vieron afectados, y si hay riesgo para sus derechos. Los datos de
   salud se consideran de alto riesgo.
4. **Notificación.**
   - Informar al responsable (el establecimiento) **sin demora**.
   - El responsable notifica a la **Agencia de Protección de Datos Personales** según los plazos y el formato que
     fije la ley y su reglamento. Si los datos afectados son sensibles, también a los **titulares**, en lenguaje claro.
   - Ocultar una vulneración es una infracción gravísima.
5. **Registro.** Documentar el incidente (fecha, alcance, medidas, notificaciones), aunque no se haya notificado.
6. **Mejora.** Corregir la causa y actualizar la EIPD.

## 5. Política de conservación

| Dato | Plazo | Al vencer |
|---|---|---|
| Ficha del paciente, casos, triage, revisiones, reportes e imágenes | Lo que exija la normativa de fichas clínicas (al menos 15 años desde la última atención) | Anonimizar (reemplazar identificación por un código) o eliminar, según decida el establecimiento |
| Historial de consentimiento y solicitudes de los titulares | Igual que la ficha (son la prueba del cumplimiento) | Igual que la ficha |
| Bitácora de auditoría | Al menos 5 años (plazo propuesto; confirmar con el establecimiento) | Archivar fuera de línea y luego eliminar |
| Registro de errores y métricas de requests | 12 meses (sin datos personales) | Eliminar |
| Copias de seguridad | Ciclo de rotación del despliegue (S7) | Se eliminan al rotar |

Pendiente: una tarea programada que detecte las fichas vencidas y las proponga para anonimizar (requiere decidir
el plazo exacto con el establecimiento).

## 6. Alojamiento en la nube y transferencia internacional

- Alojar los datos en una región fuera de Chile (por ejemplo, AWS `sa-east-1`, São Paulo) es una **transferencia
  internacional**. La Ley 21.719 la permite hacia países con nivel de protección adecuado, o con garantías
  (cláusulas contractuales). El texto de consentimiento v1 ya informa que los datos pueden alojarse fuera de Chile.
- Antes de usar datos reales:
  1. Revisar si el proveedor tiene una región en Chile; si la hay, preferirla.
  2. Firmar o aceptar el contrato de tratamiento de datos (DPA) del proveedor como encargado del tratamiento.
  3. Activar el cifrado en reposo (RDS y S3 con KMS) y TLS en tránsito.
  4. Restringir el acceso administrativo a la nube (MFA, mínimo privilegio) y registrarlo (CloudTrail).

## 7. Decisiones pendientes para el equipo

1. ~~Validar el texto de consentimiento v1~~: validado por el equipo (10-11-2026). Si el establecimiento pide cambios,
   la redacción nueva va en una versión nueva, en una migración, y obliga a mostrársela de nuevo a los pacientes (la
   plataforma lo detecta).
2. **Acceso por equipo tratante** (Ley 20.584): hoy cualquier MEDICO o ADMINISTRATIVO ve todos los casos.
3. **Plazos de conservación** exactos y la tarea de anonimización.
4. **Región de la nube** y garantías de la transferencia internacional. Preparado en la 2.5.0: región configurable
   (`AWS_REGION`, por defecto `sa-east-1`). AWS anunció una región en Chile para fines de 2026 que no estaba confirmada
   como disponible al 10-11-2026. Si existe al desplegar, conviene usarla. Si no, se usa `sa-east-1` con el DPA de AWS
   (ver `docs/despliegue_aws.md`).
5. **Pacientes registrados antes de la 2.4.0**: su consentimiento quedó sin versión de texto. La plataforma lo marca
   y permite registrarlo de nuevo con el texto vigente. Conviene hacerlo en su próxima atención.
6. **Encargado de protección de datos** del establecimiento y canal para recibir las solicitudes de los titulares.

## Referencias

- Ley 21.719 — [BCN LeyChile](https://www.bcn.cl/leychile/navegar?idNorma=1209272)
- Vigencia y proyecto de postergación — [Araya & Cía.](https://araya.cl/ley-de-proteccion-de-datos-se-postergara-su-entrada-en-vigencia/)
- Revisión técnica de seguridad — `docs/seguridad_owasp.md`
