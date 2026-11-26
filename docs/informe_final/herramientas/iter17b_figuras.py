# -*- coding: utf-8 -*-
"""Iteración 17b: diagramas de componentes y de topología al día con la 2.11.0/2.12.0 (maestro 1.7-rc -> 1.7.1-rc).
Figuras regeneradas con diagramas_cap10.py: componentes (envío de correos, proveedor con respaldo, 19 tablas, respaldo
planificado) y topología (rol de jefatura entre los usuarios).
Uso: python3 iter17b_figuras.py <dir_desempaquetado_maestro> <dir_png_generados>"""
import os, re, shutil, sys
from xml.sax.saxutils import escape
from PIL import Image

root, pngs = sys.argv[1], sys.argv[2]
p = os.path.join(root, "word", "document.xml")
x = open(p, encoding="utf-8").read()


def rep(old, new, n=1):
    global x
    o, nn = escape(old), escape(new)
    assert x.count(o) == n, (old[:80], x.count(o))
    x = x.replace(o, nn)


def replace_image(name, png):
    """Reemplaza word/media/<name> y ajusta el dibujo a la nueva proporción sin superar el alto anterior + 15 %."""
    global x
    shutil.copy(png, os.path.join(root, "word", "media", name))
    w, h = Image.open(png).size
    i = x.find('name="%s"' % name); assert i > 0, name
    s = x.rfind("<w:drawing>", 0, i); e = x.find("</w:drawing>", i)
    d = x[s:e]
    cx, cy = map(int, re.search(r'<wp:extent cx="(\d+)" cy="(\d+)"/>', d).groups())
    ncx, ncy = cx, int(cx * h / w)
    if ncy > cy * 1.15:
        ncy = int(cy * 1.15); ncx = int(ncy * w / h)
    for tag in ("wp:extent", "a:ext"):
        d = d.replace('<%s cx="%d" cy="%d"/>' % (tag, cx, cy), '<%s cx="%d" cy="%d"/>' % (tag, ncx, ncy))
    x = x[:s] + d + x[e:]


for f in ("cap10_componentes.png", "cap10_topologia.png"):
    replace_image(f, os.path.join(pngs, f))

rep("y accede a recursos externos mediante dos interfaces: almacenamiento (local o S3 cifrado) y proveedor de inferencia (simulado o HTTP, con respaldo simulado). El servicio de inferencia es un componente independiente que expone POST /predict y GET /health.",
    "y accede a recursos externos mediante tres interfaces: almacenamiento (local o S3 cifrado), envío de correos (consola o SMTP, para los enlaces de activación de la versión 2.11.0) y proveedor de inferencia. El proveedor consulta el servicio principal y, si no responde, el servicio de respaldo (versión 2.12.0; su instancia en AWS está planificada, por eso se dibuja con borde punteado) y, por último, el proveedor simulado. El servicio de inferencia es un componente independiente que expone POST /predict y GET /health.")

# Fuente de la Figura 9, de la Tabla 30 y de la Figura 11 (la Tabla 32 no cambia y conserva su fecha)
SRC = escape("Fuente: Elaboración propia a partir del código fuente y de la documentación del repositorio (23-11-2026).")
NEW = escape("Fuente: Elaboración propia a partir del código fuente y de la documentación del repositorio (25-11-2026).")
assert x.count(SRC) == 4, x.count(SRC)
for _ in range(3):
    x = x.replace(SRC, NEW, 1)

open(p, "w", encoding="utf-8").write(x)
print("ok")
