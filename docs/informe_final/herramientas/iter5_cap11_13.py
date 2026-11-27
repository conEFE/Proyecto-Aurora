# -*- coding: utf-8 -*-
"""Iteración 5: inserta los capítulos XI y XIII en el maestro (v0.8 -> v0.9)."""
import sys, os
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import maestro_lib as L
import cap11_13_contenido as C
root = sys.argv[1]; p = os.path.join(root, "word", "document.xml")
x = open(p, encoding="utf-8").read(); L.init_ids(x)
for bm, blocks in [("_Toc177988500", C.K_INTRO), ("_Toc177988501", C.KPI), ("_Toc177988502", C.SLA),
                   ("_Toc177988509", C.DISP), ("_Toc177988510", C.CONT), ("_Toc177988511", C.MANT)]:
    x = L.insert_after_bookmark(x, bm, L.render(root, blocks, os.path.dirname(HERE)))
x = L.set_control_row(x, "XI. KPI y SLA",
    "Redacción inicial en v0.9: K1–K11 con fórmula, meta, implementación en la plataforma y estado de medición; umbrales; propuesta de SLA sin institución comprometida.",
    "Pendiente: armonizar definición de K5 y metas del capítulo V (adopción, desviación presupuestaria, precisión 90%); sin mediciones reales.")
x = L.set_control_row(x, "XIII. Plan de implementación",
    "Redacción inicial en v0.9: disponibilidad (planificado frente a estado actual), continuidad (BIA y escenarios con preparación), configuración, versionado, despliegue, cambios e incidentes.",
    "Pendiente: prueba de restauración de respaldo, monitor de disponibilidad y alarmas, copia de respaldo fuera de la región.")
x = L.set_control_version(x, "0.9", "23-11-2026")
x, nums = L.renumerar(x)
open(p, "w", encoding="utf-8").write(x)
print("ok", {k[7:]: v for k, v in nums.items() if k.startswith("_Ref_T_") and k[7:] in ("kpi","kpi_umb","sla_gen","sla_srv","disp","bia","escen","ci","prio")})
