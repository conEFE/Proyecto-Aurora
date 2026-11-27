# -*- coding: utf-8 -*-
"""Diagramas con el aspecto y la notación de draw.io (UML, BPMN, ER), definidos con coordenadas explícitas.

Cada diagrama se escribe una vez y se exporta a:
  - <nombre>.drawio : editable en diagrams.net / draw.io (los elementos conservan posición, texto y estilo)
  - <nombre>.svg    : para exportar a PNG con svg_a_png.cjs (Chromium)
Paleta: la de draw.io por defecto (#dae8fc, #d5e8d4, #fff2cc, #f8cecc, #e1d5e7, #f5f5f5).
"""
import math
from xml.sax.saxutils import escape

FONT = "Helvetica, Arial, 'Liberation Sans', sans-serif"
AZUL, VERDE, AMARILLO, ROJO, MORADO, GRIS = "#dae8fc", "#d5e8d4", "#fff2cc", "#f8cecc", "#e1d5e7", "#f5f5f5"
BORDE = {AZUL: "#6c8ebf", VERDE: "#82b366", AMARILLO: "#d6b656", ROJO: "#b85450", MORADO: "#9673a6", GRIS: "#666666",
         "#ffffff": "#000000", "none": "#000000"}


def _lines(t):
    return t.split("\n") if t else []


class Diagram:
    def __init__(self, w, h):
        self.w, self.h = w, h
        self.svg, self.cells, self.n = [], [], 0

    def _id(self):
        self.n += 1
        return "c%d" % self.n

    # ------------------------------------------------------------------ texto
    def _text_svg(self, x, y, w, h, label, size=12, align="center", valign="middle", bold_first=False, pad=6,
                  color="#000"):
        ls = _lines(label)
        if not ls:
            return
        lh = size * 1.2
        tot = lh * len(ls)
        if valign == "top":
            y0 = y + pad + size
        elif valign == "bottom":
            y0 = y + h - pad - tot + size
        else:
            y0 = y + (h - tot) / 2 + size * 0.95
        if align == "left":
            tx, anchor = x + pad, "start"
        elif align == "right":
            tx, anchor = x + w - pad, "end"
        else:
            tx, anchor = x + w / 2, "middle"
        for i, ln in enumerate(ls):
            wt = ' font-weight="bold"' if (bold_first and i == 0) or ln.startswith("**") else ""
            ln = ln.replace("**", "")
            it = ' font-style="italic"' if ln.startswith("«") and not wt else ""
            self.svg.append('<text x="%.1f" y="%.1f" text-anchor="%s" font-size="%s"%s%s fill="%s">%s</text>'
                            % (tx, y0 + i * lh, anchor, size, wt, it, color, escape(ln)))

    @staticmethod
    def _html(label, bold_first=False):
        out = []
        for i, ln in enumerate(_lines(label)):
            b = (bold_first and i == 0) or ln.startswith("**")
            ln = escape(ln.replace("**", ""))
            out.append("<b>%s</b>" % ln if b else ln)
        return "<br>".join(out)

    def _cell(self, value, style, x, y, w, h):
        cid = self._id()
        self.cells.append('<mxCell id="%s" value="%s" style="%s" vertex="1" parent="1"><mxGeometry x="%.0f" y="%.0f" '
                          'width="%.0f" height="%.0f" as="geometry"/></mxCell>' % (cid, escape(value, {'"': "&quot;"}),
                                                                                   style, x, y, w, h))
        return cid

    # ------------------------------------------------------------------ formas
    def box(self, x, y, w, h, label="", fill="#ffffff", kind="rect", size=12, align="center", valign="middle",
            bold_first=False, dashed=False, stroke=None):
        st = stroke or BORDE.get(fill, "#000000")
        post = None
        da = ' stroke-dasharray="6 4"' if dashed else ""
        f = fill if fill != "none" else "none"
        s = self.svg
        if kind in ("rect", "rounded", "group"):
            rx = 8 if kind == "rounded" else 0
            s.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="%d" fill="%s" stroke="%s"%s/>'
                     % (x, y, w, h, rx, f, st, da))
            dstyle = "rounded=%d;whiteSpace=wrap;html=1;" % (kind == "rounded")
        elif kind == "component":  # UML: rectángulo con el ícono de componente arriba a la derecha
            s.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="%s" stroke="%s"%s/>' % (x, y, w, h, f, st, da))
            ix, iy = x + w - 22, y + 6
            s.append('<rect x="%.1f" y="%.1f" width="14" height="16" fill="#fff" stroke="%s"/>' % (ix + 3, iy, st))
            s.append('<rect x="%.1f" y="%.1f" width="8" height="4" fill="#fff" stroke="%s"/>' % (ix, iy + 3, st))
            s.append('<rect x="%.1f" y="%.1f" width="8" height="4" fill="#fff" stroke="%s"/>' % (ix, iy + 9, st))
            dstyle = "html=1;whiteSpace=wrap;"
            post = (ix, iy)
        elif kind == "node":  # UML: nodo de despliegue (caja 3D)
            d = 10
            s.append('<path d="M%.1f %.1f l%d %d h%.1f v%.1f l%d %d" fill="%s" stroke="%s"%s/>'
                     % (x, y + d, d, -d, w - d, h - d, -d, d, f, st, da))
            s.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s"%s/>' % (x + w - d, y + d, x + w, y, st, da))
            s.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="%s" stroke="%s"%s/>'
                     % (x, y + d, w - d, h - d, f, st, da))
            y, h, w = y + d, h - d, w - d
            dstyle = "shape=cube;size=10;direction=south;flipH=1;whiteSpace=wrap;html=1;"
            y, h, w = y - d, h + d, w + d
        elif kind == "cylinder":
            e = 10
            s.append('<path d="M%.1f %.1f a%.1f %d 0 0 1 %.1f 0 v%.1f a%.1f %d 0 0 1 %.1f 0 z" fill="%s" stroke="%s"%s/>'
                     % (x, y + e, w / 2, e, w, h - 2 * e, w / 2, e, -w, f, st, da))
            s.append('<path d="M%.1f %.1f a%.1f %d 0 0 0 %.1f 0" fill="none" stroke="%s"/>' % (x, y + e, w / 2, e, w, st))
            dstyle = "shape=cylinder3;boundedLbl=1;backgroundOutline=1;size=10;whiteSpace=wrap;html=1;"
        elif kind == "folder":
            s.append('<path d="M%.1f %.1f h%.1f l6 -8 h%.1f l6 8 h%.1f v%.1f h%.1f z" fill="%s" stroke="%s"%s/>'
                     % (x, y + 8, 4, w * 0.3, w * 0.7 - 16, h - 8, -w, f, st, da))
            dstyle = "shape=folder;tabWidth=%d;tabHeight=8;tabPosition=left;whiteSpace=wrap;html=1;" % (w * 0.3)
        elif kind == "cloud":
            s.append('<path d="M%.1f %.1f c%.1f %.1f %.1f %.1f %.1f %.1f c%.1f %.1f %.1f %.1f %.1f %.1f '
                     'c%.1f %.1f %.1f %.1f %.1f %.1f c%.1f %.1f %.1f %.1f %.1f %.1f z" fill="%s" stroke="%s"/>'
                     % (x + 0.25 * w, y + 0.8 * h,
                        -0.3 * w, 0, -0.3 * w, -0.45 * h, 0, -0.45 * h,
                        -0.05 * w, -0.4 * h, 0.35 * w, -0.4 * h, 0.4 * w, -0.2 * h,
                        0.15 * w, -0.25 * h, 0.5 * w, -0.1 * h, 0.4 * w, 0.25 * h,
                        0.25 * w, 0.05 * h, 0.2 * w, 0.45 * h, -0.15 * w, 0.4 * h, f, st))
            self.svg.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s"/>'
                            % (x + 0.25 * w, y + 0.8 * h, x + 0.85 * w, y + 0.8 * h, st))
            dstyle = "ellipse;shape=cloud;whiteSpace=wrap;html=1;"
        elif kind == "ellipse":
            s.append('<ellipse cx="%.1f" cy="%.1f" rx="%.1f" ry="%.1f" fill="%s" stroke="%s"/>' % (x + w / 2, y + h / 2, w / 2, h / 2, f, st))
            dstyle = "ellipse;whiteSpace=wrap;html=1;"
        elif kind == "note":
            s.append('<path d="M%.1f %.1f h%.1f l12 12 v%.1f h%.1f z" fill="%s" stroke="%s"/>' % (x, y, w - 12, h - 12, -w, f, st))
            dstyle = "shape=note;size=12;whiteSpace=wrap;html=1;"
        else:
            raise ValueError(kind)
        if kind == "node":
            self._text_svg(x, y + 10, w - 10, h - 10, label, size, align, valign, bold_first)
        else:
            self._text_svg(x, y, w, h, label, size, align, valign, bold_first)
        ds = dstyle + "fillColor=%s;strokeColor=%s;fontSize=%d;align=%s;verticalAlign=%s;%s" % (
            fill, st, size, align, valign, "dashed=1;" if dashed else "")
        if kind == "node":
            ds += "spacingTop=10;"
        # el contenedor va antes que su contenido en draw.io: los elementos se agregan en orden de dibujo
        self._cell(self._html(label, bold_first), ds, x, y, w, h)
        if post:
            self._cell("", "shape=module;jettyWidth=8;jettyHeight=4;html=1;", post[0], post[1], 17, 16)
        return (x, y, w, h)

    def text(self, x, y, w, h, label, size=12, align="center", valign="middle", bold_first=False):
        self._text_svg(x, y, w, h, label, size, align, valign, bold_first, pad=2)
        self._cell(self._html(label, bold_first), "text;html=1;align=%s;verticalAlign=%s;fontSize=%d;whiteSpace=wrap;"
                   % (align, valign, size), x, y, w, h)

    def lollipop(self, cx, cy, label, side="right"):
        """Interfaz provista (UML): círculo con su nombre."""
        self.svg.append('<circle cx="%.1f" cy="%.1f" r="7" fill="#fff" stroke="#000"/>' % (cx, cy))
        tx = cx + 12 if side == "right" else cx - 12
        anc = "start" if side == "right" else "end"
        self.svg.append('<text x="%.1f" y="%.1f" text-anchor="%s" font-size="11" font-style="italic">%s</text>'
                        % (tx, cy + 4, anc, escape(label)))
        self._cell("", "ellipse;html=1;fillColor=#ffffff;", cx - 7, cy - 7, 14, 14)
        self._cell(escape(label), "text;html=1;fontSize=11;fontStyle=2;align=%s;" % ("left" if side == "right" else "right"),
                   cx + 10 if side == "right" else cx - 130, cy - 10, 120, 20)

    # ------------------------------------------------------------------ conectores
    def edge(self, pts, label=None, dashed=False, end="block", start=None, label_at=None, size=11, dotted=False):
        """pts: lista de puntos absolutos (polilínea ortogonal). end/start: block | open | erOne | erMany | None."""
        da = ' stroke-dasharray="6 4"' if dashed else (' stroke-dasharray="2 3"' if dotted else "")
        d = "M" + " L".join("%.1f %.1f" % p for p in pts)
        self.svg.append('<path d="%s" fill="none" stroke="#000"%s/>' % (d, da))
        for tip, prev, kind in ((pts[-1], pts[-2], end), (pts[0], pts[1], start)):
            if kind:
                self._marker(tip, prev, kind)
        if label:
            if label_at:
                lx, ly = label_at
            else:  # punto medio del tramo más largo
                segs = list(zip(pts, pts[1:]))
                a, b = max(segs, key=lambda s: math.dist(*s))
                lx, ly = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
            ls = _lines(label)
            wmax = max(len(l) for l in ls) * size * 0.55 + 6
            hh = len(ls) * size * 1.2 + 2
            self.svg.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="#fff"/>' % (lx - wmax / 2, ly - hh / 2, wmax, hh))
            self._text_svg(lx - wmax / 2, ly - hh / 2, wmax, hh, label, size, pad=0)
        arr = {"block": "classic", "open": "open", "erOne": "ERmandOne", "erMany": "ERmany", None: "none"}
        st = "edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;endArrow=%s;startArrow=%s;fontSize=%d;%s%s" % (
            arr[end], arr[start], size, "dashed=1;" if dashed else "", "dashed=1;dashPattern=1 2;" if dotted else "")
        if end == "open" or start == "open":
            st += "endFill=0;"
        cid = self._id()
        mid = "".join('<mxPoint x="%.0f" y="%.0f"/>' % p for p in pts[1:-1])
        self.cells.append('<mxCell id="%s" value="%s" style="%s" edge="1" parent="1"><mxGeometry relative="1" as="geometry">'
                          '<mxPoint x="%.0f" y="%.0f" as="sourcePoint"/><mxPoint x="%.0f" y="%.0f" as="targetPoint"/>'
                          '%s</mxGeometry></mxCell>' % (cid, escape(self._html(label or ""), {'"': "&quot;"}), st,
                                                        pts[0][0], pts[0][1], pts[-1][0], pts[-1][1],
                                                        '<Array as="points">%s</Array>' % mid if mid else ""))

    def _marker(self, tip, prev, kind):
        ang = math.atan2(tip[1] - prev[1], tip[0] - prev[0])
        ca, sa = math.cos(ang), math.sin(ang)
        P = lambda dx, dy: (tip[0] + dx * ca - dy * sa, tip[1] + dx * sa + dy * ca)
        s = self.svg
        if kind == "block":
            pts = [P(0, 0), P(-11, -4.5), P(-8, 0), P(-11, 4.5)]
            s.append('<path d="M%s z" fill="#000"/>' % " L".join("%.1f %.1f" % p for p in pts))
        elif kind == "open":
            pts = [P(-11, -5), P(0, 0), P(-11, 5)]
            s.append('<path d="M%s" fill="none" stroke="#000"/>' % " L".join("%.1f %.1f" % p for p in pts))
        elif kind == "erOne":
            for dx in (-6, -11):
                a, b = P(dx, -6), P(dx, 6)
                s.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="#000"/>' % (a + b))
        elif kind == "erMany":
            o = P(-12, 0)
            for dy in (-7, 0, 7):
                a = P(0, dy)
                s.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="#000"/>' % (o + a))
            a, b = P(-14, -6), P(-14, 6)
            s.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="#000"/>' % (a + b))

    # ------------------------------------------------------------------ entidad (ER)
    def entity(self, x, y, w, name, rows, fill=AZUL, row_h=18):
        """Tabla de modelo lógico: encabezado + filas (clave, nombre, tipo). Devuelve {columna: y_centro}."""
        st = BORDE.get(fill, "#000")
        h = 24 + row_h * len(rows)
        self.svg.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="#fff" stroke="%s"/>' % (x, y, w, h, st))
        self.svg.append('<rect x="%.1f" y="%.1f" width="%.1f" height="24" fill="%s" stroke="%s"/>' % (x, y, w, fill, st))
        self._text_svg(x, y, w, 24, name, 12, bold_first=True, pad=0)
        cid = self._id()
        self.cells.append('<mxCell id="%s" value="%s" style="swimlane;fontStyle=1;childLayout=stackLayout;horizontal=1;'
                          'startSize=24;fillColor=%s;strokeColor=%s;horizontalStack=0;resizeParent=1;collapsible=0;html=1;" '
                          'vertex="1" parent="1"><mxGeometry x="%.0f" y="%.0f" width="%.0f" height="%.0f" as="geometry"/></mxCell>'
                          % (cid, escape(name), fill, st, x, y, w, h))
        ys = {}
        for i, (k, col, typ) in enumerate(rows):
            ry = y + 24 + i * row_h
            ys[col] = ry + row_h / 2
            if k:
                self.svg.append('<text x="%.1f" y="%.1f" font-size="10" font-weight="bold">%s</text>' % (x + 5, ry + 13, k))
            und = ' text-decoration="underline"' if k == "PK" else ""
            self.svg.append('<text x="%.1f" y="%.1f" font-size="10.5"%s>%s</text>' % (x + 28, ry + 13, und, escape(col)))
            self.svg.append('<text x="%.1f" y="%.1f" font-size="9.5" fill="#555" text-anchor="end">%s</text>'
                            % (x + w - 5, ry + 13, escape(typ)))
            rid = self._id()
            self.cells.append('<mxCell id="%s" value="%s" style="text;html=1;align=left;verticalAlign=middle;spacingLeft=4;'
                              'fontSize=10;%s" vertex="1" parent="%s"><mxGeometry y="%.0f" width="%.0f" height="%d" as="geometry"/>'
                              '</mxCell>' % (rid, escape("%s %s : %s" % (k or "  ", col, typ)), "fontStyle=4;" if k == "PK" else "",
                                             cid, 24 + i * row_h, w, row_h))
        return ys, (x, y, w, h)

    # ------------------------------------------------------------------ salida
    def save(self, base):
        svg = ('<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="0 0 %d %d" font-family="%s">'
               '<rect width="%d" height="%d" fill="#fff"/>%s</svg>'
               % (self.w, self.h, self.w, self.h, FONT.replace("'", "&apos;"), self.w, self.h, "\n".join(self.svg)))
        open(base + ".svg", "w", encoding="utf-8").write(svg)
        xml = ('<mxfile host="Proyecto Aurora"><diagram name="%s" id="d1"><mxGraphModel grid="1" gridSize="10" '
               'pageWidth="%d" pageHeight="%d"><root><mxCell id="0"/><mxCell id="1" parent="0"/>%s</root></mxGraphModel>'
               '</diagram></mxfile>' % (escape(base.split("/")[-1]), self.w, self.h, "".join(self.cells)))
        open(base + ".drawio", "w", encoding="utf-8").write(xml)
