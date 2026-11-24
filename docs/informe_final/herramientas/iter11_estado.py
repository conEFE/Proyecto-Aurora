# -*- coding: utf-8 -*-
"""Actualiza ESTADO_ITERACION.md y PLAN_INFORME_FINAL.md al cierre de la iteración 11.
Uso: python3 iter11_estado.py <p95_100_ms> <paginas_pdf>"""
import os, sys
base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
p95, pags = sys.argv[1], sys.argv[2]

p = os.path.join(base, "trabajo", "ESTADO_ITERACION.md"); s = open(p, encoding="utf-8").read()
old_head = s[:s.index("## Revisión contra plantilla y rúbrica (23-11-2026")]
new_head = f"""# Proyecto Aurora — Estado del plan de revisión y avance del informe

**Actualización:** 24-11-2026 (iteración 11: plantilla y rúbrica de defensa)
**Versiones vigentes:** documento maestro **1.1-rc** · registro de revisiones v0.20 · PDF `Proyecto_Aurora_Informe_Final.pdf` ({pags} páginas)
**Estado general:** informe completo en versión candidata, con los cinco ajustes de la rúbrica aplicados. Quedan los
pendientes del equipo (abajo y registro, secciones 4.15 y 4.16). Traspaso al siguiente agente: `../HANDOFF_ITERACION_12.md`.

## Iteración 11 — Plantilla y rúbrica de defensa (maestro 1.1-rc)

Aprobada por el usuario el 24-11-2026 («aplica los cinco puntos»).

| Ajuste | Indicador EA5 | Cambio en el maestro |
|---|---|---|
| (a) | Plantilla | 10.4.3 con su título literal; «Componente de análisis automatizado de imágenes» pasa a 10.7.1; 5 encabezados vacíos retirados |
| (b) | 4. Innovación | 4.8 «Soluciones existentes y diferenciación» con Tabla 6 (Transpara, Lunit INSIGHT MMG, ProFound AI) y evidencia (Dembrower 2020, Freeman 2021, MASAI 2023) |
| (c) | 5. Evaluación integral | 14.3.1 síntesis de factibilidad técnica, operativa, económica, legal y ambiental (Tabla 58), corrigiendo lo de U2 (sin capacitación; institución sin compromiso) |
| (d) | 2 y 3. Complementariedad y sustentabilidad | 9.2.1 integración del stack (Tabla 26); 8.3.1 sustentabilidad |
| (e) | 6. Estabilidad y rendimiento | 12.1.3 prueba de rendimiento local: PC-01 con 100 usuarios durante 15 min, **p95 {p95} ms**; XI, XII, XV, XVI, resumen y abstract actualizados |

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

"""
s = new_head + s[len(old_head):]
s = s.replace("## Revisión contra plantilla y rúbrica (23-11-2026, sin cambios en el maestro)",
              "## Revisión contra plantilla y rúbrica (23-11-2026, diagnóstico previo a la iteración 11)", 1)
open(p, "w", encoding="utf-8").write(s)

p = os.path.join(base, "PLAN_INFORME_FINAL.md"); s = open(p, encoding="utf-8").read()
a = "| Plantilla, rúbrica, U2 «Estudio de factibilidad», fuentes externas para (b) y ambiental; aprobación del equipo; correcciones del docente (opcional) | **Planificada**; detalle en `HANDOFF_ITERACION_11.md` |"
assert s.count(a) == 1
s = s.replace(a, "| Plantilla, rúbrica, U2 «Estudio de factibilidad», fuentes externas para (b) y ambiental; aprobación del equipo; correcciones del docente (opcional) | **Hecha (24-11)**; incluye corrección de un bloqueo bajo carga en el backend |")
a = "| Aprobación de los cinco ajustes de la iteración 11 | It. 11 | Usuario |\n"
assert s.count(a) == 1
s = s.replace(a, "| Aprobación de los cinco ajustes de la iteración 11 | It. 11 (resuelto 24-11) | Usuario |\n| Despliegue de la corrección del bloqueo bajo carga (`9043857`) en el entorno de demostración | Coherencia entre informe y demostración | Equipo |\n| Monitoreo y alarmas de disponibilidad; prueba de restauración (ver `trabajo/REVISION_NUBE_VS_HU.md`) | Medición de K3; cierre de XIII | Equipo (acceso a AWS) |\n")
s = s.rstrip("\n") + f"\n| 11 | 24-11-2026 | 1.1-rc | v0.20 | Ajustes por plantilla y rúbrica EA5 (4.8, 8.3.1, 9.2.1, 10.7.1, 12.1.3, 14.3.1); PC-01 local con p95 de {p95} ms tras corregir un bloqueo bajo carga en el backend; revisión de nube frente a HU; PDF de {pags} páginas. |\n"
open(p, "w", encoding="utf-8").write(s)
print("ok")
