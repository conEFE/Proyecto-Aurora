# -*- coding: utf-8 -*-
"""Iteración 1: inserta capítulos VII y VIII en el maestro (v0.4 -> v0.5).
Uso: python3 iter1_cap7_8.py <dir_desempaquetado_maestro>"""
import sys, os, re
from xml.sax.saxutils import escape
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import maestro_lib as L
from cap7_8_contenido import CAP7, CAP8

root = sys.argv[1]
p = os.path.join(root, "word", "document.xml")
x = open(p, encoding="utf-8").read()

x = L.insert_after_bookmark(x, "_Toc177988480", L.render(root, CAP7))
x = L.insert_after_bookmark(x, "_Toc177988482", L.render(root, CAP8))

def setrow(x, label, col2, col3):
    t = "<w:t>%s</w:t>" % escape(label)
    assert x.count(t) == 1, label
    i = x.find(t); s = x.rfind("<w:tr>", 0, i); e = x.find("</w:tr>", i) + 7
    row = x[s:e]; ts = re.findall(r"<w:t>[^<]*</w:t>", row); assert len(ts) == 3
    row = row.replace(ts[1], "<w:t>%s</w:t>" % escape(col2), 1).replace(ts[2], "<w:t>%s</w:t>" % escape(col3), 1)
    return x[:s] + row + x[e:]

x = setrow(x, "VII. Definición de arquitectura TI",
    "Redacción inicial en v0.5: arquitectura N-tier, monolito modular con servicio de análisis desacoplado, capas con nivel de evidencia, decisiones de arquitectura y evolución respecto de Unidad 1.",
    "Pendiente: contrastar con la plantilla institucional (no disponible); confirmar arquitectura desplegada en el capítulo X.")
x = setrow(x, "VIII. Arquitectura empresarial",
    "Redacción inicial en v0.5: tipo y estructura de la organización, procesos de negocio con apoyo previsto e historias relacionadas, relación de la solución con los procesos.",
    "Pendiente: contrastar con la plantilla institucional; BPMN detallado en el capítulo X.")
old = "Registro interno de trabajo para la versión 0.4 del documento maestro (23-11-2026)."
assert x.count(old) == 1
x = x.replace(old, "Registro interno de trabajo para la versión 0.5 del documento maestro (23-11-2026).")

x, nums = L.renumerar(x)
open(p, "w", encoding="utf-8").write(x)
print("ok", nums)
