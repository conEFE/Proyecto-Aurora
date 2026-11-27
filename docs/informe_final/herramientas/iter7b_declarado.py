# -*- coding: utf-8 -*-
"""Iteración 7b: actualiza el capítulo XII con la revisión declarada del 20-11-2026 (PB-01)."""
import sys, os, re
from xml.sax.saxutils import escape
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import maestro_lib as L
root = sys.argv[1]; p = os.path.join(root, "word", "document.xml")
x = open(p, encoding="utf-8").read()

def row_replace(anchor, old, new):
    global x
    a = escape(anchor); assert x.count(a) == 1, anchor
    i = x.find(a); s = x.rfind("<w:tr>", 0, i); e = x.find("</w:tr>", i) + 7
    row = x[s:e]; o = escape(old); assert row.count(o) == 1, (anchor, old)
    x = x[:s] + row.replace(o, escape(new)) + x[e:]

row_replace("Prueba beta con profesionales clínicos y datos ficticios", "Sin evidencia registrada",
            "Realizada parcialmente: presentación y revisión con 2 médicos y 1 enfermera el 20-11 (declarado); sin encuesta")
row_replace("Pruebas alfa y beta (PA-01, PB-01)", "Sin evidencia registrada",
            "Alfa sin registro; beta parcial: revisión con 2 médicos y 1 enfermera el 20-11 (declarado), sin encuesta de satisfacción")
x, _ = L.renumerar(x)
open(p, "w", encoding="utf-8").write(x)
print("ok")
