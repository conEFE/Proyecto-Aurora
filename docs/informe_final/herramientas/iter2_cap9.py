# -*- coding: utf-8 -*-
"""Iteración 2: inserta el capítulo IX en el maestro (v0.5 -> v0.6).
Uso: python3 iter2_cap9.py <dir_desempaquetado_maestro>"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import maestro_lib as L
from cap9_contenido import S91, S92

root = sys.argv[1]
p = os.path.join(root, "word", "document.xml")
x = open(p, encoding="utf-8").read()
L.init_ids(x)
x = L.insert_after_bookmark(x, "_Toc177988485", L.render(root, S91))
x = L.insert_after_bookmark(x, "_Toc177988486", L.render(root, S92))
x = L.set_control_row(x, "IX. Tecnologías",
    "Redacción inicial en v0.6: matriz de decisión ponderada y AHP de Unidad 2 recalculados; análisis cualitativo, cuantitativo y de sensibilidad; versiones reales de dependencias y servicios TI con estado.",
    "Pendiente: verificar citas (Stack Overflow 2024 y otras) en el capítulo XVII; confirmar decisión de región y licencia de YOLO para una fase comercial.")
x = L.set_control_version(x, "0.6", "23-11-2026")
x, nums = L.renumerar(x)
open(p, "w", encoding="utf-8").write(x)
print("ok", {k: v for k, v in nums.items() if k.startswith("_Ref_")})
