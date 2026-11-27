# -*- coding: utf-8 -*-
"""Iteración 18c: se retiran las figuras de diseño de la formulación y de la Unidad 2 (infraestructura de U1 y U2 y
arquitectura de aplicaciones de U1), que mostraban componentes no adoptados (Cloudflare, São Paulo, Prometheus,
Grafana, AWS Backup) y se confundían con lo desplegado. Las diferencias quedan descritas en el texto.
Uso: python3 iter18c_sin_disenos.py <dir_desempaquetado_maestro>"""
import os, re, sys
from xml.sax.saxutils import escape
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import maestro_lib as L

root = sys.argv[1]
p = os.path.join(root, "word", "document.xml")
x = open(p, encoding="utf-8").read(); L.init_ids(x)
PARA = re.compile(r"<w:p\b(?:(?!<w:p\b).)*?</w:p>", re.S)
text_of = lambda px: "".join(re.findall(r"<w:t[^>]*>([^<]*)</w:t>", px))


def para_with(fragment):
    ms = [m for m in PARA.finditer(x) if fragment in text_of(m.group(0))]
    assert len(ms) == 1, (fragment, len(ms))
    return ms[0]


def replace_para(fragment, new_text):
    global x
    m = para_with(fragment)
    x = x[:m.start()] + L.para(new_text) + x[m.end():]


def drop_figure(bm):
    """Borra desde la leyenda (con el marcador bm) hasta el párrafo de fuente, y la imagen del paquete."""
    global x
    i = x.find('w:name="%s"' % bm); assert i > 0, bm
    s = max(x.rfind("<w:p>", 0, i), x.rfind("<w:p ", 0, i))
    e = x.find("FiguraoTablaFuente", i); e = x.find("</w:p>", e) + 6
    seg = x[s:e]
    rids = re.findall(r'r:embed="([^"]+)"', seg)
    x = x[:s] + x[e:]
    relp = os.path.join(root, "word", "_rels", "document.xml.rels")
    rels = open(relp, encoding="utf-8").read()
    for rid in rids:
        if 'r:embed="%s"' % rid in x:
            continue
        m = re.search(r'<Relationship Id="%s"[^>]*Target="([^"]+)"[^>]*/>' % rid, rels)
        if m:
            rels = rels.replace(m.group(0), "")
            f = os.path.join(root, "word", m.group(1))
            if os.path.exists(f):
                os.remove(f)
    open(relp, "w", encoding="utf-8").write(rels)


replace_para("Como contraste, la ",
    "Los diseños de infraestructura de la formulación y de la Unidad 2 ubicaban la solución en la región de São Paulo y "
    "contemplaban Cloudflare como capa de borde, Prometheus y Grafana para el monitoreo, AWS Backup y copias en otra región. "
    "Ninguno de esos componentes se adoptó: el entorno desplegado usa la región us-east-2 asignada al proyecto de AWS, que no "
    "admite recursos ni copias en otras regiones, con Caddy para el HTTPS, Route 53 para el DNS, CloudWatch para el monitoreo "
    "y volcados diarios a S3 como respaldo. Por eso este informe presenta solo la infraestructura desplegada ({F:infra}); "
    "las diferencias y su justificación se detallan en el capítulo VII y en la {T:infra_tab}.")
replace_para("muestra la arquitectura de aplicaciones de la formulación",
    "Respecto de la arquitectura de aplicaciones de la formulación, se mantuvieron las capas y el monolito modular; el "
    "análisis de imágenes pasó de un módulo con modelos YOLO a un servicio independiente con una CNN y YOLO, y el monitoreo "
    "con Prometheus y Grafana se reemplazó por CloudWatch.")
for bm in ("_Ref_F_u1infra", "_Ref_F_u2infra", "_Ref_F_u1apps"):
    drop_figure(bm)
# Tabla de costos: la columna del piloto es la estimación de la Unidad 2
old = escape("0 (Cloudflare)")
assert x.count(old) == 1
x = x.replace(old, escape("0 (estimación de la Unidad 2, que suponía Cloudflare; con Route 53, ≈ 0,5)"))
x, nums = L.renumerar(x)
open(p, "w", encoding="utf-8").write(x)
print("ok; figuras", max(v for k, v in nums.items() if "_F_" in k))
