# Handoff — después de la iteración 11 del Informe Final (Proyecto Aurora)

**Fecha:** 24-11-2026 · **Rama:** `claude/bold-maxwell-13fkwp` · **Punto de partida:** maestro **1.1-rc**, registro **v0.20**,
PDF de 167 páginas. Reemplaza a `HANDOFF_ITERACION_11.md` (que queda como historia).

Lee este documento, luego `trabajo/ESTADO_ITERACION.md`, `PLAN_INFORME_FINAL.md` y `trabajo/REVISION_NUBE_VS_HU.md`.

## 1. Qué está hecho

- Iteraciones 0 a 11 cerradas. La iteración 11 aplicó los cinco ajustes de la plantilla y la rúbrica de defensa (EA5):
  4.8 soluciones existentes; 8.3.1 sustentabilidad; 9.2.1 integración del stack; 10.4.3 y 10.7.1 según la plantilla;
  12.1.3 prueba de rendimiento local; 14.3.1 factibilidad técnica, operativa, económica, legal y ambiental.
- **Código:** la prueba de carga encontró un bloqueo total de la API con ~50 usuarios. Corregido en `9043857`
  (`backend/app/deps.py`, `middleware.py`, `error_log_service.py`, `api/rutas_images.py`; prueba
  `test_middleware_pool.py`; 316 pruebas, 0 fallos). PC-01 local (100 usuarios, 15 min): p95 de 3.974 ms, **no cumple** la meta de 3 s (sí hasta 50 usuarios;
  con 100 hubo saturación, no bloqueo).
  Evidencia en `evidencias/rendimiento_2026-11-24/` (incluye la corrida previa a la corrección).
- Revisión de nube frente a historias de usuario: `trabajo/REVISION_NUBE_VS_HU.md`.

## 2. Qué falta

### Decisiones del equipo (no las tomes tú)
1. **Desplegar `9043857`** en `demo.auroracare.cl` (sigue en la 2.10.0 con el defecto). Requiere fusionar y el despliegue
   habitual por Session Manager (`docs/ESTADO_AWS.md`). Si se despliega, actualizar en el informe XII (12.1.3: «no se ha
   desplegado») y XIII (versión publicada).
2. **Inferencia el día de la defensa:** PC de Juan encendido y conectado, o mover el modelo a AWS (`t4g.medium`, CPU).
3. **Capacidad para la meta de rendimiento:** con 100 usuarios virtuales la meta no se cumple en local; la
   `t4g.micro` de la demostración tiene menos capacidad. Dimensionar (procesos, pool, instancia) y medir en ese entorno.
4. **Monitoreo y alarmas** (chequeo de salud de Route 53 + alarma + SNS) y **prueba de restauración**: requieren acceso
   a AWS. Con resultados, actualizar K3 (XI), 13.1–13.2 (XIII) y la Tabla de resultados de XII.

### Pendientes documentales del equipo (registro, secciones 4.15 y 4.16)
Dedicatoria y agradecimientos; cita Shah et al. (2023); título de 2026c y descripción de 2026b; fechas de OMS 2026,
NEMA 2026 y ACR 2025; acta de la revisión del 20-11 (opcional); escaneo ZAP; alerta de presupuesto AWS; comentario
de K5 en el código; confirmar CU18 y PI-06…PS-08; N-11-02 (dispositivo médico: si el equipo aporta una fuente oficial,
se puede precisar en 14.3.1); correcciones del docente a U1/U2 para verificar U1-xx/U2-xx; lectura y aceptación de 1.0.

### Siguiente iteración posible (12), solo si el equipo entrega insumos
- Integrar los resultados de despliegue, alarmas, restauración o ZAP en XI–XIII y en la síntesis de factibilidad.
- Textos personales (dedicatoria, agradecimientos) y correcciones del docente.
- Exportar PDF final y cerrar la versión 1.0.

## 3. Reglas que no cambian

- El maestro (`trabajo/Proyecto_Aurora_Informe_Final_Maestro.docx`) es el único informe que se edita; respalda antes
  (`respaldos/*_pre-it12`).
- No inventes información ni declares implementado, probado, desplegado o validado sin evidencia. La prueba de carga es
  **local**; el rendimiento del entorno de demostración no está medido. La revisión del 20-11 **no** es validación clínica.
- Se rechazó inventar fechas del Gantt (D-15-01). Nueva Clínica Cordillera: institución de referencia, no cliente ni piloto.
- El proyecto de AWS no permite recursos ni copias en otra región.
- Commits **sin coautoría de Claude** (`CLAUDE.md`). Sin `push --force`; si el remoto diverge, `git merge -s ours` y push
  normal solo si el contenido remoto ya está incluido.

## 4. Cómo se trabaja el maestro

Igual que en la iteración 11 (ver `herramientas/iter11_rubrica.py` como ejemplo): descomprimir con `zipfile`, script
con `maestro_lib.py` (`init_ids`, `render`, `renumerar`; **no** `set_control_row`), volver a comprimir
(`zip -XrDqy` y `zip -d '*/'`), validar con `scripts/office/validate.py` de la skill docx, exportar el PDF con
`herramientas/exportar_pdf.py`, registro con `registro_lib.py` (siguiente: v0.21, sección 4.17), y actualizar
`ESTADO_ITERACION.md` y la tabla 7 del plan.

Para repetir la prueba de carga: `backend/scripts/load_test.py` (instrucciones en su docstring y en el README de la evidencia).
No la ejecutes contra `demo.auroracare.cl` sin acuerdo del equipo.

## 5. Fuentes fuera del repositorio

U1, U2, la plantilla y la rúbrica las sube el usuario y no se versionan; pídelas si no las tienes.
