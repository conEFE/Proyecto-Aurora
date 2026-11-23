# -*- coding: utf-8 -*-
"""Inserta el capítulo VI en el document.xml desempaquetado del maestro.
Uso: python3 insertar_cap6.py <dir_desempaquetado> <png_gantt>"""
import sys, os, re, shutil
from xml.sax.saxutils import escape
sys.path.insert(0, os.path.dirname(__file__))
from cap6_contenido import S61, S62, S63, S64

root, png = sys.argv[1], sys.argv[2]
docp = os.path.join(root, "word", "document.xml")
x = open(docp, encoding="utf-8").read()

bm_id = [9100]
def nbm():
    bm_id[0] += 1
    return bm_id[0]

# Precalcular numeración de tablas y figuras del capítulo (SEQ con valor en caché)
order = {"T": [], "F": []}
for sec in (S61, S62, S63, S64):
    for b in sec:
        if b[0] == "tabla": order["T"].append(b[2])
        if b[0] == "figura": order["F"].append(b[2])
# Las tablas/figuras previas del maestro no tienen leyenda SEQ, por lo que el capítulo VI inicia en 1.
num = {("T", k): i + 1 for i, k in enumerate(order["T"])}
num.update({("F", k): i + 1 for i, k in enumerate(order["F"])})
LAB = {"T": "Tabla", "F": "Figura"}
def bmname(kind, key): return "_RefCap6_%s_%s" % (kind, key)

def run(t, rpr=""):
    return '<w:r>%s<w:t xml:space="preserve">%s</w:t></w:r>' % (rpr, escape(t))

def field(instr, cached, rpr=""):
    return ('<w:r>%s<w:fldChar w:fldCharType="begin"/></w:r><w:r>%s<w:instrText xml:space="preserve"> %s </w:instrText></w:r>'
            '<w:r>%s<w:fldChar w:fldCharType="separate"/></w:r><w:r>%s<w:t>%s</w:t></w:r><w:r>%s<w:fldChar w:fldCharType="end"/></w:r>'
            % (rpr, rpr, instr, rpr, rpr, escape(cached), rpr))

def rich(text):
    out, pos = [], 0
    for m in re.finditer(r"\{([TF]):(\w+)\}", text):
        out.append(run(text[pos:m.start()]))
        k, key = m.group(1), m.group(2)
        out.append(field("REF %s \\h" % bmname(k, key), "%s %d" % (LAB[k], num[(k, key)])))
        pos = m.end()
    out.append(run(text[pos:]))
    return "".join(o for o in out if o != run(""))

def para(text):  # mismo formato que los capítulos III–V (estilo Normal)
    return "<w:p><w:pPr/>%s</w:p>" % rich(text)

def bullet(text):
    return "<w:p><w:pPr/>%s</w:p>" % run("• " + text)

def heading(style, text):
    return '<w:p><w:pPr><w:pStyle w:val="%s"/></w:pPr>%s</w:p>' % (style, run(text))

def caption(kind, key, title):
    b = nbm(); n = num[(kind, key)]
    return ('<w:p><w:pPr><w:pStyle w:val="FiguraoTablaTtulo"/></w:pPr>'
            '<w:bookmarkStart w:id="%d" w:name="%s"/>%s%s<w:bookmarkEnd w:id="%d"/>%s</w:p>'
            % (b, bmname(kind, key), run(LAB[kind] + " "), field("SEQ %s \\* ARABIC" % LAB[kind], str(n)), b, run(". " + title)))

def source(text):
    return '<w:p><w:pPr><w:pStyle w:val="FiguraoTablaFuente"/><w:jc w:val="left"/></w:pPr>%s</w:p>' % run(text, "<w:rPr><w:b w:val=\"0\"/><w:sz w:val=\"18\"/><w:szCs w:val=\"18\"/></w:rPr>")

def table(widths, rows):
    tw = sum(widths)
    g = "".join('<w:gridCol w:w="%d"/>' % w for w in widths)
    out = ['<w:tbl><w:tblPr><w:tblStyle w:val="Tablaconcuadrcula"/><w:tblW w:type="dxa" w:w="%d"/><w:jc w:val="center"/>'
           '<w:tblLayout w:type="fixed"/><w:tblLook w:firstColumn="1" w:firstRow="1" w:lastColumn="0" w:lastRow="0" w:noHBand="0" w:noVBand="1" w:val="04A0"/></w:tblPr>'
           '<w:tblGrid>%s</w:tblGrid>' % (tw, g)]
    for ri, r in enumerate(rows):
        hdr = ri == 0
        trpr = '<w:trPr><w:tblHeader/><w:cantSplit/></w:trPr>' if hdr else '<w:trPr><w:cantSplit/></w:trPr>'
        cells = []
        for w, c in zip(widths, r):
            shd = '<w:shd w:val="clear" w:color="auto" w:fill="D9EAF7"/>' if hdr else ''
            rpr = '<w:rPr><w:b/><w:sz w:val="16"/><w:szCs w:val="16"/></w:rPr>' if hdr else '<w:rPr><w:sz w:val="16"/><w:szCs w:val="16"/></w:rPr>'
            cells.append('<w:tc><w:tcPr><w:tcW w:type="dxa" w:w="%d"/>%s</w:tcPr><w:p><w:pPr><w:spacing w:before="20" w:after="20"/></w:pPr>%s</w:p></w:tc>'
                         % (w, shd, run(c, rpr)))
        out.append("<w:tr>%s%s</w:tr>" % (trpr, "".join(cells)))
    out.append("</w:tbl>")
    return "".join(out)

# Imagen
media = os.path.join(root, "word", "media")
shutil.copy(png, os.path.join(media, "cap6_gantt_linea_base.png"))
relp = os.path.join(root, "word", "_rels", "document.xml.rels")
rels = open(relp, encoding="utf-8").read()
if "cap6_gantt_linea_base.png" not in rels:
    rels = rels.replace("</Relationships>", '<Relationship Id="rIdCap6Gantt" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" Target="media/cap6_gantt_linea_base.png"/></Relationships>')
    open(relp, "w", encoding="utf-8").write(rels)

def figure(fname):
    from PIL import Image as _I; _w,_h=_I.open(png).size; cx = 5425000; cy = int(cx * _h / _w)
    return ('<w:p><w:pPr><w:keepNext/><w:jc w:val="center"/></w:pPr><w:r><w:drawing><wp:inline distT="0" distB="0" distL="0" distR="0">'
            '<wp:extent cx="%d" cy="%d"/><wp:effectExtent l="0" t="0" r="0" b="0"/><wp:docPr id="9601" name="Gantt línea base" descr="Carta Gantt de la línea base de Proyecto Aurora, 11-04-2026 a 10-12-2026"/>'
            '<wp:cNvGraphicFramePr><a:graphicFrameLocks xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" noChangeAspect="1"/></wp:cNvGraphicFramePr>'
            '<a:graphic xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"><a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/picture">'
            '<pic:pic xmlns:pic="http://schemas.openxmlformats.org/drawingml/2006/picture"><pic:nvPicPr><pic:cNvPr id="0" name="%s"/><pic:cNvPicPr/></pic:nvPicPr>'
            '<pic:blipFill><a:blip r:embed="rIdCap6Gantt"/><a:stretch><a:fillRect/></a:stretch></pic:blipFill>'
            '<pic:spPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="%d" cy="%d"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom></pic:spPr></pic:pic>'
            '</a:graphicData></a:graphic></wp:inline></w:drawing></w:r></w:p>' % (cx, cy, fname, cx, cy))

def render(blocks):
    out = []
    for b in blocks:
        t = b[0]
        if t == "p": out.append(para(b[1]))
        elif t == "b": out.append(bullet(b[1]))
        elif t == "h4": out.append(heading("Ttulo4", b[1]))
        elif t == "h5": out.append(heading("Ttulo5", b[1]))
        elif t == "tabla":
            _, title, key, src, widths, rows = b
            out += [caption("T", key, title), table(widths, rows), source(src)]
        elif t == "figura":
            _, title, key, src, path = b
            out += [caption("F", key, title), figure(os.path.basename(path)), source(src)]
    return "".join(out)

# Sustituir el párrafo vacío que sigue a cada encabezado Ttulo3 del capítulo VI
bms = {"_Toc177988475": S61, "_Toc177988476": S62, "_Toc177988477": S63, "_Toc177988478": S64}
for bm, blocks in bms.items():
    i = x.find('w:name="%s"' % bm)
    assert i > 0 and x.count('w:name="%s"' % bm) == 1, bm
    hend = x.find("</w:p>", i) + 6
    nxt_end = x.find("</w:p>", hend)
    nxt_selfclose = x.find("/>", hend)
    nxt = x[hend:hend + 400]
    m = re.match(r'<w:p [^>]*?(/>|><w:pPr><w:pStyle w:val="Prrafo"/></w:pPr></w:p>)', nxt)
    assert m, (bm, nxt[:200])
    x = x[:hend] + render(blocks) + x[hend + m.end():]

open(docp, "w", encoding="utf-8").write(x)
print("ok", num)
