# Revisión: componentes de nube no adoptados frente a las historias de usuario

**Fecha:** 24-11-2026 · **Fuentes:** informe de Unidad 2 (arquitectura objetivo, cap. III; SLA y continuidad, cap. IV–VI),
`docs/ESTADO_AWS.md` (16-11-2026), `docs/IMPLEMENTACIONES_FUTURAS.md`, `docs/inferencia_remota.md`, `docs/cumplimiento_legal.md`
y el código del repositorio. Sin acceso a la cuenta de AWS desde esta sesión: el estado de la nube es el documentado.

## Conclusión

**Ningún componente de nube descartado impide cumplir una historia de usuario.** Las doce HU son funcionales y se
cumplen en la aplicación: la autenticación, el triage, las notificaciones, los reportes, la auditoría y la privacidad
viven en el código, no en servicios de AWS. Lo descartado afecta a **requerimientos no funcionales, KPI y SLA**
(disponibilidad, respaldo, seguridad perimetral y rendimiento). Hay **un caso que sí toca el valor de dos HU**:
la inferencia fuera de la nube (HU08 y HU12).

## Detalle

| # | Planificado en U2 | Estado actual | HU / requisito afectado | ¿Bloquea una HU? | Recomendación |
|---|---|---|---|---|---|
| 1 | Inferencia en la instancia de la nube (incluida en el cómputo del piloto) | En el PC con GPU de Juan, por Tailscale; si no responde, **respaldo simulado** | **HU08** (resultados del análisis) y **HU12** (evaluación médica del resultado) | No: la HU funciona, pero con el PC apagado el resultado es «IA SIMULADA» | **Candidata a implementar ahora** si la defensa depende del modelo real: `t4g.medium` con el perfil `inference` (≈ USD 28/mes más, CPU, varios segundos por imagen; `docs/inferencia_remota.md` §5). Si no, asegurar el PC encendido el día de la defensa |
| 2 | Alarmas de CloudWatch (CPU > 80%, 5xx > 1%, p95 > 3 s, almacenamiento de RDS < 20%) y monitor externo de `/health` | Solo logs en CloudWatch (30 días); sin alarmas ni monitor | KPI **K2** (p95) y **K3** (disponibilidad), SLA-01; RNF04 | No | **Implementar ahora** (bajo costo): chequeo de salud de Route 53 sobre `/health` + alarma + correo SNS; filtro de métricas 5xx en los logs. Primeras 10 alarmas sin costo; el chequeo de salud ≈ USD 0,50/mes. Da la primera medición real de K3. Requiere que alguien con acceso a AWS lo ejecute |
| 3 | AWS Backup con 30 días de retención y copia en `us-east-1` | `pg_dump` diario a S3 (35 días) + respaldo automático de RDS de 1 día (límite del plan gratuito) | RNF de continuidad; indirectamente **HU11** (la bitácora vive en la base) | No | **Implementar ahora la prueba de restauración** (sigue pendiente). La copia en otra región **no es posible** en este proyecto de AWS (sin acciones entre regiones): reemplazar por copia fuera de AWS (U2 la contemplaba). Corregido en la recomendación del cap. XVI |
| 4 | Cloudflare: DNS, CDN, WAF y protección DDoS | Route 53 + Caddy (TLS de Let's Encrypt, encabezados de seguridad) + grupo de seguridad | RNF de seguridad; **HU01** se protege en la aplicación (límite de intentos por IP, bloqueo de cuenta) | No | Postergar. Un WAF de AWS exige ALB o CloudFront (costo y cambio de arquitectura, contra D-07-01). Ejecutar el escaneo ZAP pendiente |
| 5 | Región `sa-east-1` (São Paulo) | `us-east-2` (Ohio), fijada por el proyecto de AWS | **HU09** (consentimiento) y **HU10** (derechos de titulares): transferencia internacional (Ley 21.719) | No: la demostración usa solo datos ficticios | Documentado (`docs/cumplimiento_legal.md` §6). Para un piloto con datos reales: decidir región o documentar la transferencia y el DPA; evaluar si el texto del consentimiento debe mencionar el alojamiento en el extranjero (cambio de versión del texto, decisión del equipo) |
| 6 | Despliegue continuo con credenciales temporales (OIDC) a staging | Despliegue manual por Session Manager | Ninguna HU; gestión de cambios | No | Postergar |
| 7 | RDS Multi-AZ y recuperación a un punto en el tiempo | RDS de instancia única, respaldo de 1 día | RNF04 (fase comercial) | No | Postergar a la fase comercial (U2 ya lo ubicaba ahí) |
| 8 | Prometheus y Grafana | No adoptados | **HU07** cubre las métricas clínicas en el Dashboard propio (incluye p95 de la API) | No | Descartar para el prototipo; el punto 2 cubre la operación |
| 9 | Acceso a S3 por VPC endpoint | No documentado | Ninguna HU | No | Opcional (endpoint de gateway sin costo) |

## Hallazgo de la prueba de carga que sí afecta a todas las HU (24-11-2026)

No viene de la nube sino del código: con ~50 usuarios concurrentes, **la API se bloqueaba por completo** (el middleware
de métricas pedía una segunda conexión al mismo pool de la base). Afecta a todas las HU porque deja la plataforma
sin responder, y al SLA-01, que promete p95 ≤ 3 s con 50 usuarios. Está **corregido en esta rama** (pool auxiliar,
prueba de regresión, 316 pruebas en verde) pero **no desplegado**: `demo.auroracare.cl` sigue en la 2.10.0 con el
defecto. En una demostración con pocos usuarios no se nota; con un curso entero entrando a la vez, sí podría.

Con la corrección, la meta p95 ≤ 3 s se cumple en local hasta 50 usuarios virtuales (p95 1.592 ms) y **no con 100**
(p95 3.974 ms, 59 errores por saturación, sin bloqueo). La `t4g.micro` tiene menos capacidad que el entorno local:
antes de un piloto hay que dimensionar (procesos, pool, instancia) y medir allí.

## Qué implementaría ahora, en orden

0. **Desplegar la corrección del bloqueo bajo carga** (requiere fusionar la rama y el despliegue habitual por
   Session Manager; decisión y ejecución del equipo).
1. **Monitoreo y alarmas (punto 2).** Es el de mejor relación valor/costo, deja evidencia para K3 en el informe y responde
   a la rúbrica (estabilidad). Puedo dejar preparado un script `deploy/aws/` con los comandos; debe ejecutarlo quien tenga
   acceso a la cuenta.
2. **Prueba de restauración del respaldo (punto 3).** Sin costo; cierra un pendiente del informe (XII y XIII).
3. **Inferencia el día de la defensa (punto 1).** Decidir entre mover el modelo a AWS (más costo y latencia en CPU) o
   asegurar el PC de Juan encendido y conectado. Es la única decisión que afecta directamente lo que ve un médico en HU08/HU12.

Los puntos 4 a 9 no se recomiendan antes de la entrega: cambian la arquitectura aprobada (D-07-01) o no aportan a una HU.
