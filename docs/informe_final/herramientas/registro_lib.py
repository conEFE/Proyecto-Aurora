# -*- coding: utf-8 -*-
"""Funciones para actualizar el registro de revisiones (document.xml desempaquetado)."""
import re
from xml.sax.saxutils import escape

RPR = '<w:rPr><w:rFonts w:ascii="Arial" w:hAnsi="Arial"/><w:sz w:val="16"/></w:rPr>'

def set_version(x, nueva):
    x2 = re.sub(r"(Documento de control de observaciones, acciones y estados \| Versión )[0-9.]+( \(\d\d-\d\d-\d{4}\))?",
                lambda m: m.group(1) + nueva, x, count=1)
    assert x2 != x
    return x2

def add_version_rows(x, rows):
    i = x.find("4. Historial de versiones del informe"); e = x.find("</w:tbl>", i)
    xml = "".join("<w:tr>" + "".join('<w:tc><w:tcPr><w:tcW w:type="dxa" w:w="2045"/></w:tcPr><w:p><w:r>%s<w:t>%s</w:t></w:r></w:p></w:tc>' % (RPR, escape(v)) for v in r) + "</w:tr>" for r in rows)
    return x[:e] + xml + x[e:]

def P(t): return '<w:p><w:r><w:t xml:space="preserve">%s</w:t></w:r></w:p>' % escape(t)
def H(t, lvl=3): return '<w:p><w:pPr><w:pStyle w:val="Heading%d"/></w:pPr><w:r><w:t>%s</w:t></w:r></w:p>' % (lvl, escape(t))

def TABLE(widths, rows):
    out = ['<w:tbl><w:tblPr><w:tblStyle w:val="TableGrid"/><w:tblW w:type="dxa" w:w="%d"/><w:tblLayout w:type="fixed"/><w:tblLook w:firstColumn="1" w:firstRow="1" w:lastColumn="0" w:lastRow="0" w:noHBand="0" w:noVBand="1" w:val="04A0"/></w:tblPr><w:tblGrid>%s</w:tblGrid>'
           % (sum(widths), "".join('<w:gridCol w:w="%d"/>' % w for w in widths))]
    for ri, r in enumerate(rows):
        b = "<w:b/>" if ri == 0 else ""
        rpr = '<w:rPr><w:rFonts w:ascii="Arial" w:hAnsi="Arial"/>%s<w:sz w:val="16"/></w:rPr>' % b
        tr = '<w:trPr><w:tblHeader/></w:trPr>' if ri == 0 else ''
        shd = '<w:shd w:val="clear" w:color="auto" w:fill="D9EAF7"/>' if ri == 0 else ''
        out.append("<w:tr>%s%s</w:tr>" % (tr, "".join('<w:tc><w:tcPr><w:tcW w:type="dxa" w:w="%d"/>%s</w:tcPr><w:p><w:r>%s<w:t xml:space="preserve">%s</w:t></w:r></w:p></w:tc>' % (w, shd, rpr, escape(c)) for w, c in zip(widths, r))))
    out.append("</w:tbl>")
    return "".join(out)

OBS_W = [900, 1300, 4424, 2400, 1200]  # ID, Capítulo, Observación, Acción, Estado

def append_section(x, xml):
    k = x.rfind("<w:sectPr")
    return x[:k] + xml + x[k:]
