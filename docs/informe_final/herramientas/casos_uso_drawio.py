# -*- coding: utf-8 -*-
"""Diagrama de casos de uso con la disposición definida por el equipo (27-11-2026).

Genera, desde una sola especificación:
  - <dir>/cap10_casos_uso.drawio  (editable en diagrams.net / draw.io)
  - <dir>/cap10_casos_uso.svg     (para exportar a PNG con svg_a_png.cjs)

Uso: python3 casos_uso_drawio.py <dir_salida>
Coordenadas = centro de cada elemento, en el lienzo de 1560 × 1570 del diagrama del equipo.
"""
import math, os, sys
from xml.sax.saxutils import escape

out = sys.argv[1]
W, H = 1560, 1570
BOX = (440, 0, 690, H)  # límite del sistema: x, y, ancho, alto
NUEVO = "#FFF2CC"       # casos agregados después de la U2

CU = {  # id: (cx, cy, nombre, ancho, alto)
    "CU13": (660, 170, "Configurar parámetros de triage", 120, 80),
    "CU14": (830, 150, "Visualizar dashboard de métricas", 120, 80),
    "CU20": (800, 280, "Activar cuenta por correo", 120, 80),
    "CU02": (790, 405, "Gestionar usuarios y roles", 120, 80),
    "CU03": (660, 450, "Consultar bitácora de auditoría", 120, 80),
    "CU19": (785, 570, "Comparar desempeño de médicos", 120, 80),
    "CU01": (670, 640, "Iniciar sesión", 120, 80),
    "CU17": (810, 740, "Cambiar contraseña", 120, 80),
    "CU04": (680, 810, "Registrar paciente y consentimiento", 120, 80),
    "CU09": (838, 900, "Consultar cola priorizada", 120, 80),
    "CU05": (718, 1000, "Crear y gestionar caso clínico", 120, 80),
    "CU18": (910, 1000, "Gestionar solicitudes de titulares de datos", 120, 80),
    "CU15": (605, 1080, "Validar informe de IA por imagen", 120, 80),
    "CU06": (785, 1120, "Cargar exámenes e imágenes", 120, 80),
    "CU07": (1040, 1110, "Analizar imagen", 120, 80),
    "CU08": (850, 1235, "Calcular triage", 120, 80),
    "CU11": (570, 1220, "Revisar caso y registrar resultado", 120, 80),
    "CU10": (740, 1290, "Sobrescribir nivel de triage", 120, 80),
    "CU16": (520, 1390, "Firmar reporte clínico", 120, 80),
    "CU12": (680, 1480, "Generar reporte clínico PDF", 120, 80),
}
NUEVOS = {"CU17", "CU18", "CU19", "CU20"}

ACT = {  # id: (cx, y_superior, nombre)
    "med": (65, 660, "Médico"),
    "jef": (275, 590, "Jefatura y finanzas"),
    "adm": (1295, 660, "Administrador del sistema"),
    "per": (1495, 740, "Personal administrativo"),
}
ASOC = {
    "med": ["CU13", "CU14", "CU20", "CU01", "CU17", "CU04", "CU09", "CU05", "CU18", "CU06",
            "CU15", "CU11", "CU10", "CU16", "CU12"],
    "jef": ["CU14", "CU20", "CU19", "CU01", "CU17"],
    "adm": ["CU14", "CU20", "CU02", "CU03", "CU19", "CU01", "CU17"],
    "per": ["CU14", "CU20", "CU01", "CU17", "CU04", "CU09", "CU05", "CU18", "CU06"],
}
# (origen, destino, estereotipo): la flecha va del origen al destino
REL = [("CU06", "CU07", "include"), ("CU07", "CU08", "include"), ("CU11", "CU15", "include"),
       ("CU10", "CU11", "extend"), ("CU12", "CU11", "extend"), ("CU12", "CU16", "include")]


def wrap(txt, n=17):
    lines, cur = [], ""
    for w in txt.split():
        if cur and len(cur) + 1 + len(w) > n:
            lines.append(cur); cur = w
        else:
            cur = (cur + " " + w).strip()
    return lines + [cur]


def borde_elipse(cid, px, py):
    cx, cy, _, w, h = CU[cid]
    dx, dy = px - cx, py - cy
    t = 1 / math.sqrt((dx / (w / 2)) ** 2 + (dy / (h / 2)) ** 2)
    return cx + dx * t, cy + dy * t


def ancla_actor(aid, px, py):
    cx, top, _ = ACT[aid]
    ay = top + 30
    dx = px - cx
    return cx + (15 if dx > 0 else -15), ay


# ---------------------------------------------------------------- SVG
s = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
     'font-family="Helvetica, Arial, \'Liberation Sans\', sans-serif">',
     '<defs><marker id="ab" viewBox="0 0 10 10" refX="10" refY="5" markerWidth="8" markerHeight="8" '
     'orient="auto"><path d="M0,1 L10,5 L0,9 L3,5 z" fill="#000"/></marker></defs>',
     f'<rect width="{W}" height="{H}" fill="#fff"/>',
     f'<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" fill="none" stroke="#000"/>',
     f'<rect x="{BOX[0]}" y="{BOX[1]+0.5}" width="{BOX[2]}" height="{BOX[3]-1}" fill="#F5F5F5" stroke="#666"/>',
     f'<text x="{BOX[0]+BOX[2]/2}" y="34" text-anchor="middle" font-size="22" font-weight="bold">Plataforma Aurora</text>']

for aid, lst in ASOC.items():
    for cid in lst:
        cx, cy = CU[cid][:2]
        ax, ay = ancla_actor(aid, cx, cy)
        ex, ey = borde_elipse(cid, ax, ay)
        s.append(f'<line x1="{ax:.1f}" y1="{ay:.1f}" x2="{ex:.1f}" y2="{ey:.1f}" stroke="#000" stroke-width="1"/>')

for a, b, st in REL:
    ax, ay = CU[a][:2]; bx, by = CU[b][:2]
    x1, y1 = borde_elipse(a, bx, by); x2, y2 = borde_elipse(b, ax, ay)
    s.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="#000" '
             'stroke-dasharray="6 4" marker-end="url(#ab)"/>')
    mx, my = (x1 + x2) / 2, (y1 + y2) / 2
    lab = f"&lt;&lt;{st}&gt;&gt;"
    s.append(f'<rect x="{mx-30}" y="{my-7}" width="60" height="13" fill="#F5F5F5"/>'
             f'<text x="{mx}" y="{my+3}" text-anchor="middle" font-size="10">{lab}</text>')

for cid, (cx, cy, name, w, h) in CU.items():
    fill = NUEVO if cid in NUEVOS else "#fff"
    s.append(f'<ellipse cx="{cx}" cy="{cy}" rx="{w/2}" ry="{h/2}" fill="{fill}" stroke="#000"/>')
    lines = [cid] + wrap(name)
    y0 = cy - (len(lines) - 1) * 7.5 + 4
    for i, ln in enumerate(lines):
        s.append(f'<text x="{cx}" y="{y0 + i*15:.1f}" text-anchor="middle" font-size="12">{escape(ln)}</text>')

for aid, (cx, top, name) in ACT.items():
    hy = top + 8
    s.append(f'<g fill="none" stroke="#000" stroke-width="1.2"><circle cx="{cx}" cy="{hy}" r="8" fill="#fff"/>'
             f'<line x1="{cx}" y1="{hy+8}" x2="{cx}" y2="{top+42}"/>'
             f'<line x1="{cx-15}" y1="{top+24}" x2="{cx+15}" y2="{top+24}"/>'
             f'<line x1="{cx}" y1="{top+42}" x2="{cx-13}" y2="{top+60}"/>'
             f'<line x1="{cx}" y1="{top+42}" x2="{cx+13}" y2="{top+60}"/></g>')
    s.append(f'<text x="{cx}" y="{top+76}" text-anchor="middle" font-size="12">{escape(name)}</text>')

s.append("</svg>")
open(os.path.join(out, "cap10_casos_uso.svg"), "w", encoding="utf-8").write("\n".join(s))

# ---------------------------------------------------------------- draw.io
cells = ['<mxCell id="0"/>', '<mxCell id="1" parent="0"/>',
         f'<mxCell id="sys" value="Plataforma Aurora" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#f5f5f5;'
         f'strokeColor=#666666;verticalAlign=top;fontStyle=1;fontSize=22;" vertex="1" parent="1">'
         f'<mxGeometry x="{BOX[0]}" y="{BOX[1]}" width="{BOX[2]}" height="{BOX[3]}" as="geometry"/></mxCell>']
for cid, (cx, cy, name, w, h) in CU.items():
    fill = NUEVO if cid in NUEVOS else "#FFFFFF"
    v = escape(f"{cid}<br>{name}")
    cells.append(f'<mxCell id="{cid}" value="{v}" style="ellipse;whiteSpace=wrap;html=1;fillColor={fill};" '
                 f'vertex="1" parent="1"><mxGeometry x="{cx-w/2}" y="{cy-h/2}" width="{w}" height="{h}" '
                 'as="geometry"/></mxCell>')
for aid, (cx, top, name) in ACT.items():
    cells.append(f'<mxCell id="{aid}" value="{escape(name)}" style="shape=umlActor;verticalLabelPosition=bottom;'
                 f'verticalAlign=top;html=1;outlineConnect=0;" vertex="1" parent="1">'
                 f'<mxGeometry x="{cx-15}" y="{top}" width="30" height="60" as="geometry"/></mxCell>')
n = 0
for aid, lst in ASOC.items():
    for cid in lst:
        n += 1
        cells.append(f'<mxCell id="e{n}" style="endArrow=none;html=1;" edge="1" parent="1" source="{aid}" '
                     f'target="{cid}"><mxGeometry relative="1" as="geometry"/></mxCell>')
for a, b, st in REL:
    n += 1
    cells.append(f'<mxCell id="e{n}" value="{escape("<<" + st + ">>")}" style="endArrow=open;dashed=1;html=1;'
                 f'endFill=0;fontSize=10;" edge="1" parent="1" source="{a}" target="{b}">'
                 '<mxGeometry relative="1" as="geometry"/></mxCell>')
xml = ('<mxfile host="Proyecto Aurora"><diagram name="Casos de uso" id="cu">'
       f'<mxGraphModel dx="{W}" dy="{H}" grid="1" gridSize="10" pageWidth="{W}" pageHeight="{H}"><root>'
       + "".join(cells) + '</root></mxGraphModel></diagram></mxfile>')
open(os.path.join(out, "cap10_casos_uso.drawio"), "w", encoding="utf-8").write(xml)
print("ok")
