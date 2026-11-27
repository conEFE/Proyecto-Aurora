# Prueba de restauración de respaldo — 24-11-2026

**Resultado: aprobada.** El respaldo diario automático se restauró completo y coincide con la base en producción.

## Procedimiento
1. Respaldo usado: `backups/aurora-20261124T061501Z.sql.gz` (el automático de las 06:15 UTC del 24-11-2026, generado
   por `deploy/backup_db.sh` desde la RDS), 283.271 bytes, SHA-256 `fa2f301044037bbd…`.
2. En el servidor `aurora-prod`, por Session Manager: descarga desde S3, `gunzip -t` (íntegro), marca
   «PostgreSQL database dump complete» presente y 19 tablas con datos.
3. Restauración en un **esquema temporal** (`restauracion`) de la misma RDS, sin tocar la base en uso ni interrumpir el
   sitio (mismo método que la copia de la prueba de carga). El esquema se eliminó al terminar.
4. Comparación del conteo de filas de las 19 tablas, versión de migración (Alembic), último id de la bitácora y
   triggers, entre lo restaurado y la base en uso.
5. Archivos: cruce de las 258 filas de `images` con los objetos del bucket (`images/`), y descifrado de 5 imágenes
   al azar con la clave de la aplicación, comparando su SHA-256 con el registrado en la base.

## Resultados
| Tabla | Restaurado | En uso |
|---|---|---|
| ai_validations | 220 | 220 |
| alembic_version | 1 | 1 |
| audit_log | 3.407 | 3.407 |
| cases | 316 | 316 |
| clinical_reviews | 270 | 270 |
| consent_texts | 1 | 1 |
| data_subject_requests | 0 | 0 |
| error_log | 0 | 0 |
| images | 258 | 258 |
| inference_results | 258 | 258 |
| notifications | 209 | 209 |
| patient_consent_events | 275 | 275 |
| patients | 275 | 275 |
| report_signatures | 1 | 1 |
| reports | 1 | 1 |
| request_metrics | 6.855 | 6.855 |
| triage_configs | 1 | 1 |
| triage_results | 587 | 587 |
| users | 8 | 8 |

- Migración `d2e7b3c9a011` en ambos; último id de `audit_log` 3.407 en ambos; 1 trigger (bitácora inmutable) en ambos.
- Tiempo: descarga y verificación 2,1 s; carga 1,0 s (base de ≈ 280 KB comprimida).
- Imágenes: 258 de 258 con su objeto en S3; 5 de 5 descifradas con SHA-256 correcto (imágenes sintéticas de 1,3 KB de
  los datos de demostración).

## Alcance
- Datos ficticios. La coincidencia exacta se explica porque no hubo escrituras en la base entre las 06:15 UTC y la
  prueba; en uso normal, lo posterior al último respaldo diario se perdería (RPO de hasta 24 h; RDS además guarda
  1 día de respaldos automáticos propios, no probados aquí).
- No se restauró sobre una instancia nueva ni se probó la recuperación del servidor completo (EC2) ni de las imágenes
  desde versiones anteriores del bucket.
