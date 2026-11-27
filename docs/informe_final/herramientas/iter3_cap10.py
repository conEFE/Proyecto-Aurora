# -*- coding: utf-8 -*-
"""Iteración 3: inserta el capítulo X en el maestro (v0.6 -> v0.7).
Uso: python3 iter3_cap10.py <dir_desempaquetado_maestro>   (ejecutar desde docs/informe_final)"""
import sys, os
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import maestro_lib as L
import cap10_contenido as C

root = sys.argv[1]
base = os.path.dirname(HERE)
p = os.path.join(root, "word", "document.xml")
x = open(p, encoding="utf-8").read()
L.init_ids(x)
plan = [("_Toc177988488", C.INTRO), ("_Toc177988489", C.BPMN), ("_Toc177988490", C.CU), ("_Toc177988491", C.COMP),
        ("_Toc177988492", C.DATOS), ("_Toc177988493", C.LOGICO), ("_Toc177988494", C.FISICO), ("_Toc177988495", C.DICC),
        ("_Toc177988496", C.TOPO), ("_Toc177988497", C.INFRA),
        ("_Toc177988498", C.ARQ + [("h3", "Componente de análisis automatizado de imágenes.")] + C.IA)]
for bm, blocks in plan:
    x = L.insert_after_bookmark(x, bm, L.render(root, blocks, base))
x = L.set_control_row(x, "X. Arquitectura",
    "Redacción inicial en v0.7: BPMN (U2, reglas contrastadas con código), casos de uso actualizados (CU17, CU18), componentes, modelo lógico generado desde el código (18 tablas), modelo físico, topología, infraestructura y arquitectura actuales; servicio de inferencia inspeccionado.",
    "Pendiente: diccionario de datos en anexos; especificación de casos de uso en anexos; confirmar infraestructura con la cuenta AWS (fuente: documentación del repositorio).")
x = L.set_control_version(x, "0.7", "23-11-2026")
x, nums = L.renumerar(x)
open(p, "w", encoding="utf-8").write(x)
print("ok", {k: v for k, v in nums.items() if k.startswith("_Ref_")})
