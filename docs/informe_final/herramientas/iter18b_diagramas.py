# -*- coding: utf-8 -*-
"""Iteración 18b: los diagramas propios del capítulo X pasan a notación estándar con fuente editable en draw.io
(figuras/drawio/*.drawio, generados con diagramas_drawio.py): componentes (UML), modelo lógico (ER con pata de gallo),
topología e infraestructura (UML de despliegue), arquitectura por capas y componente de análisis.
Uso: python3 iter18b_diagramas.py <dir_desempaquetado_maestro> <dir_figuras>"""
import os, re, shutil, sys
from PIL import Image

root, figs = sys.argv[1], sys.argv[2]
p = os.path.join(root, "word", "document.xml")
x = open(p, encoding="utf-8").read()
MEDIA = {"cap10_componentes.png": "cap10_componentes.png", "cap10_modelo_logico.png": "cap10_modelo_logico.png",
         "cap10_topologia.png": "cap10_topologia.png", "cap10_infraestructura.png": "cap10_infraestructura.png",
         "cap10_arquitectura.png": "cap10_arquitectura.png", "it15_cnn.png": "it15_cnn.png"}
for name, src in MEDIA.items():
    png = os.path.join(figs, src)
    shutil.copy(png, os.path.join(root, "word", "media", name))
    w, h = Image.open(png).size
    i = x.find('name="%s"' % name); assert i > 0, name
    s = x.rfind("<w:drawing>", 0, i); e = x.find("</w:drawing>", i)
    d = x[s:e]
    cx, cy = map(int, re.search(r'<wp:extent cx="(\d+)" cy="(\d+)"/>', d).groups())
    area = cx * cy  # misma superficie aproximada, sin superar el ancho anterior
    ncx = min(cx, int((area * w / h) ** 0.5)); ncy = int(ncx * h / w)
    for tag in ("wp:extent", "a:ext"):
        d = d.replace('<%s cx="%d" cy="%d"/>' % (tag, cx, cy), '<%s cx="%d" cy="%d"/>' % (tag, ncx, ncy))
    x = x[:s] + d + x[e:]
open(p, "w", encoding="utf-8").write(x)
print("ok")
