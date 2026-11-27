# -*- coding: utf-8 -*-
"""Iteración 4: inserta el capítulo XII en el maestro (v0.7 -> v0.8)."""
import sys, os
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import maestro_lib as L
from cap12_contenido import S121, S122
root = sys.argv[1]; p = os.path.join(root, "word", "document.xml")
x = open(p, encoding="utf-8").read(); L.init_ids(x)
x = L.insert_after_bookmark(x, "_Toc177988505", L.render(root, S121, os.path.dirname(HERE)))
x = L.insert_after_bookmark(x, "_Toc177988506", L.render(root, S122, os.path.dirname(HERE)))
x = L.set_control_row(x, "XII. Pruebas y calidad",
    "Redacción inicial en v0.8: plan de pruebas, matriz de casos con prueba automatizada y resultado, ejecución propia del 23-11-2026 (314/314; cobertura 97%), matriz de trazabilidad RF/RNF–HU–CU–prueba y normas.",
    "Pendiente: pruebas de carga/estrés (Locust no implementado), escaneo ZAP, pruebas alfa/beta y pruebas automatizadas de interfaz.")
x = L.set_control_version(x, "0.8", "23-11-2026")
x, nums = L.renumerar(x)
open(p, "w", encoding="utf-8").write(x)
print("ok", {k: v for k, v in nums.items() if k.startswith("_Ref_T_") and k[7:] in ("param","casos","result","archivos","traza","normas")})
