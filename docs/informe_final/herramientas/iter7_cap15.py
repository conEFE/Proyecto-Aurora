# -*- coding: utf-8 -*-
"""Iteración 7: capítulo XV (v0.10 -> v0.11)."""
import sys, os
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import maestro_lib as L
import cap15_contenido as C
root = sys.argv[1]; p = os.path.join(root, "word", "document.xml")
x = open(p, encoding="utf-8").read(); L.init_ids(x)
x = L.insert_after_bookmark(x, "_Toc177988520", L.render(root, C.INTRO, os.path.dirname(HERE)))
x = L.insert_after_bookmark(x, "_Toc177988521", L.render(root, C.GANTT + C.AJUSTES + C.RIESGOS, os.path.dirname(HERE)))
x = L.set_control_row(x, "XV. Ajustes del cronograma",
    "Redacción inicial en v0.11: carta Gantt con línea base, ejecución, responsables e hitos (corte 23-11); estado por fase; entregables por sprint; desviaciones y ajustes; hitos y ruta crítica; matriz de riesgos actualizada.",
    "Pendiente: confirmar con el equipo las actividades sin registro (validación clínica, capacitación, piloto, firma de SLA, decisión del modelo) y la aceptación del MVP (24-11).")
x = L.set_control_version(x, "0.11", "23-11-2026")
x, nums = L.renumerar(x)
open(p, "w", encoding="utf-8").write(x)
print("ok", {k[5:]: v for k, v in nums.items() if k[7:] in ("estado","entregables","ajustes","hitos","riesgos","gantt_xv")})
