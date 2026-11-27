# Handoff — después de la iteración 15 del Informe Final (Proyecto Aurora)

**Fecha:** 24-11-2026 · **Rama:** `claude/bold-maxwell-13fkwp` · **Punto de partida:** maestro **1.5-rc**, registro **v0.24**,
PDF de 186 páginas y 26 figuras. Reemplaza a `HANDOFF_ITERACION_15.md` (que queda como historia).

**Iteración 15 (hecha):** diagramas de procesos y arquitectura, cloud, CNN y capturas (detalle en `trabajo/ESTADO_ITERACION.md`).
Para rehacer un diagrama: editar `herramientas/diagramas_it15/*.html` y `node render.cjs <html> <png> <ancho>`.

**Iteración 14 (hecha):** escaneo ZAP (PS-04 aprobado), prueba de restauración (completa) y monitoreo con alarmas por
correo. Detalle en `trabajo/ESTADO_ITERACION.md`. La decisión 4 de abajo quedó resuelta.

**Iteración 13 (hecha):** PC-01 medida en AWS con la **2.10.2** (desplegada): 0 errores, p95 14.979 ms con 100 usuarios
(no cumple; sí hasta 25). Detalle en `trabajo/ESTADO_ITERACION.md` y `evidencias/rendimiento_aws_2026-11-24/README.md`.
La decisión 3 de abajo (capacidad) sigue abierta: ahora con datos del entorno real (≈ 20 solicitudes/s, un proceso).

**Iteración 12 (hecha):** la corrección del bloqueo bajo carga está en `main` como **2.10.1** y **desplegada** en
`demo.auroracare.cl` (24-11-2026). Informe actualizado en 12.1.3, XIII y 14.3.1; registro 4.17. La decisión 1 de abajo
quedó resuelta; el resto sigue igual.

Lee este documento, luego `trabajo/ESTADO_ITERACION.md`, `PLAN_INFORME_FINAL.md` y `trabajo/REVISION_NUBE_VS_HU.md`.

## 1. Qué está hecho

- Iteraciones 0 a 11 cerradas. La iteración 11 aplicó los cinco ajustes de la plantilla y la rúbrica de defensa (EA5):
  4.8 soluciones existentes; 8.3.1 sustentabilidad; 9.2.1 integración del stack; 10.4.3 y 10.7.1 según la plantilla;
  12.1.3 prueba de rendimiento local; 14.3.1 factibilidad técnica, operativa, económica, legal y ambiental.
- **Código (it. 13):** 2.10.2 (`1ec7904`, `ConcurrencyLimitMiddleware`) corrige un segundo bloqueo bajo carga; 321
  pruebas; desplegada en `demo.auroracare.cl` el 24-11-2026.
- **Código (it. 11):** la prueba de carga encontró un bloqueo total de la API con ~50 usuarios. Corregido en `9043857`
  (`backend/app/deps.py`, `middleware.py`, `error_log_service.py`, `api/rutas_images.py`; prueba
  `test_middleware_pool.py`; 316 pruebas, 0 fallos). PC-01 local (100 usuarios, 15 min): p95 de 3.974 ms, **no cumple** la meta de 3 s (sí hasta 50 usuarios;
  con 100 hubo saturación, no bloqueo).
  Evidencia en `evidencias/rendimiento_2026-11-24/` (incluye la corrida previa a la corrección).
- Revisión de nube frente a historias de usuario: `trabajo/REVISION_NUBE_VS_HU.md`.

## 2. Qué falta

### Decisiones del equipo (no las tomes tú)
1. ~~**Desplegar `9043857`**~~ **Hecho (24-11, versión 2.10.1).** en `demo.auroracare.cl` (sigue en la 2.10.0 con el defecto). Requiere fusionar y el despliegue
   habitual por Session Manager (`docs/ESTADO_AWS.md`). Si se despliega, actualizar en el informe XII (12.1.3: «no se ha
   desplegado») y XIII (versión publicada).
2. **Inferencia el día de la defensa:** PC de Juan encendido y conectado, o mover el modelo a AWS (`t4g.medium`, CPU).
3. **Capacidad para la meta de rendimiento:** medida en AWS el 24-11 (2.10.2): ≈ 20 solicitudes/s con un proceso;
   p95 ≤ 3 s solo hasta 25 usuarios; con 100, 14.979 ms. Opciones: `WEB_CONCURRENCY=2` (vigilar memoria de 1 GB),
   instancia mayor u optimizar `/cases` y `/dashboard/metrics`. Si se cambia, repetir PC-01 sobre una copia de la base.
4. ~~**Monitoreo y alarmas** y **prueba de restauración**~~ **Hechos (24-11, iteración 14).** Texto anterior: requieren acceso
   a AWS. Con resultados, actualizar K3 (XI), 13.1–13.2 (XIII) y la Tabla de resultados de XII.

### Pendientes documentales del equipo (registro, secciones 4.15 y 4.16)
Dedicatoria y agradecimientos; cita Shah et al. (2023); título de 2026c y descripción de 2026b; fechas de OMS 2026,
NEMA 2026 y ACR 2025; acta de la revisión del 20-11 (opcional); alerta de presupuesto AWS; comentario
de K5 en el código; confirmar CU18 y PI-06…PS-08; N-11-02 (dispositivo médico: si el equipo aporta una fuente oficial,
se puede precisar en 14.3.1); correcciones del docente a U1/U2 para verificar U1-xx/U2-xx; lectura y aceptación de 1.0.

### Siguiente iteración posible (12), solo si el equipo entrega insumos
- ~~Integrar despliegue, alarmas, restauración y ZAP en XI–XIII~~ (hecho en las iteraciones 12 a 14).
- Textos personales (dedicatoria, agradecimientos) y correcciones del docente.
- Exportar PDF final y cerrar la versión 1.0.

## 3. Reglas que no cambian

- El maestro (`trabajo/Proyecto_Aurora_Informe_Final_Maestro.docx`) es el único informe que se edita; respalda antes
  (`respaldos/*_pre-it16`).
- No inventes información ni declares implementado, probado, desplegado o validado sin evidencia. Hay pruebas de carga
  local y en AWS (24-11); no hay prueba de estrés (PC-02). La revisión del 20-11 **no** es validación clínica.
- Se rechazó inventar fechas del Gantt (D-15-01). Nueva Clínica Cordillera: institución de referencia, no cliente ni piloto.
- El proyecto de AWS no permite recursos ni copias en otra región.
- Commits **sin coautoría de Claude** (`CLAUDE.md`). Sin `push --force`; si el remoto diverge, `git merge -s ours` y push
  normal solo si el contenido remoto ya está incluido.

## 4. Cómo se trabaja el maestro

Igual que en la iteración 11 (ver `herramientas/iter11_rubrica.py` como ejemplo): descomprimir con `zipfile`, script
con `maestro_lib.py` (`init_ids`, `render`, `renumerar`; **no** `set_control_row`), volver a comprimir
(`zip -XrDqy` y `zip -d '*/'`), validar con `scripts/office/validate.py` de la skill docx, exportar el PDF con
`herramientas/exportar_pdf.py`, registro con `registro_lib.py` (siguiente: v0.25, sección 4.21), y actualizar
`ESTADO_ITERACION.md` y la tabla 7 del plan.

Para repetir la prueba de carga: `backend/scripts/load_test.py` (instrucciones en su docstring y en el README de la evidencia).
Contra `demo.auroracare.cl`, solo con acuerdo del equipo y sobre una copia de la base (método en
`evidencias/rendimiento_aws_2026-11-24/README.md`): la bitácora no admite borrado.

## 5. Fuentes fuera del repositorio

U1, U2, la plantilla y la rúbrica las sube el usuario y no se versionan; pídelas si no las tienes.
