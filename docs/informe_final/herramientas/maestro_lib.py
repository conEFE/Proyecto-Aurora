# -*- coding: utf-8 -*-
"""Funciones comunes para editar el document.xml desempaquetado del maestro.

Bloques de contenido admitidos:
  ("p", texto)            párrafo (estilo Normal, como capítulos III–VI); admite {T:clave} y {F:clave}
  ("b", texto)            viñeta con «•» (mismo formato que capítulos III–VI)
  ("h3"|"h4"|"h5", texto) encabezados Ttulo3/Ttulo4/Ttulo5 (numeración automática de la plantilla)
  ("tabla", titulo, clave, fuente, anchos_dxa, filas)
  ("figura", titulo, clave, fuente, ruta_png)
Las leyendas usan campos SEQ y marcadores _Ref_<T|F>_<clave>; las referencias del texto usan campos REF.
`renumerar()` recalcula en orden de documento los valores en caché de SEQ y REF.
"""
import os, re, shutil
from xml.sax.saxutils import escape

LAB = {"T": "Tabla", "F": "Figura"}
_bm = [9300]
_img = [9700]

def _nbm():
    _bm[0] += 1
    return _bm[0]

def run(t, rpr=""):
    return '<w:r>%s<w:t xml:space="preserve">%s</w:t></w:r>' % (rpr, escape(t))

def field(instr, cached, rpr=""):
    return ('<w:r>%s<w:fldChar w:fldCharType="begin"/></w:r><w:r>%s<w:instrText xml:space="preserve"> %s </w:instrText></w:r>'
            '<w:r>%s<w:fldChar w:fldCharType="separate"/></w:r><w:r>%s<w:t>%s</w:t></w:r><w:r>%s<w:fldChar w:fldCharType="end"/></w:r>'
            % (rpr, rpr, instr, rpr, rpr, escape(cached), rpr))

def bmname(kind, key):
    return "_Ref_%s_%s" % (kind, key)

def rich(text):
    out, pos = [], 0
    for m in re.finditer(r"\{([TF]):(\w+)\}", text):
        if text[pos:m.start()]:
            out.append(run(text[pos:m.start()]))
        k, key = m.group(1), m.group(2)
        out.append(field("REF %s \\h" % bmname(k, key), "%s ?" % LAB[k]))
        pos = m.end()
    if text[pos:]:
        out.append(run(text[pos:]))
    return "".join(out)

def para(text):
    return "<w:p><w:pPr/>%s</w:p>" % rich(text)

def bullet(text):
    return "<w:p><w:pPr/>%s</w:p>" % rich("• " + text)

def heading(style, text):
    return '<w:p><w:pPr><w:pStyle w:val="%s"/></w:pPr>%s</w:p>' % (style, run(text))

def caption(kind, key, title):
    b = _nbm()
    return ('<w:p><w:pPr><w:pStyle w:val="FiguraoTablaTtulo"/></w:pPr>'
            '<w:bookmarkStart w:id="%d" w:name="%s"/>%s%s<w:bookmarkEnd w:id="%d"/>%s</w:p>'
            % (b, bmname(kind, key), run(LAB[kind] + " "), field("SEQ %s \\* ARABIC" % LAB[kind], "?"), b, run(". " + title)))

def source(text):
    return ('<w:p><w:pPr><w:pStyle w:val="FiguraoTablaFuente"/><w:jc w:val="left"/></w:pPr>%s</w:p>'
            % run(text, '<w:rPr><w:b w:val="0"/><w:sz w:val="18"/><w:szCs w:val="18"/></w:rPr>'))

def table(widths, rows):
    g = "".join('<w:gridCol w:w="%d"/>' % w for w in widths)
    out = ['<w:tbl><w:tblPr><w:tblStyle w:val="Tablaconcuadrcula"/><w:tblW w:type="dxa" w:w="%d"/><w:jc w:val="center"/>'
           '<w:tblLayout w:type="fixed"/><w:tblLook w:firstColumn="1" w:firstRow="1" w:lastColumn="0" w:lastRow="0" w:noHBand="0" w:noVBand="1" w:val="04A0"/></w:tblPr>'
           '<w:tblGrid>%s</w:tblGrid>' % (sum(widths), g)]
    for ri, r in enumerate(rows):
        hdr = ri == 0
        trpr = '<w:trPr><w:tblHeader/><w:cantSplit/></w:trPr>' if hdr else '<w:trPr><w:cantSplit/></w:trPr>'
        shd = '<w:shd w:val="clear" w:color="auto" w:fill="D9EAF7"/>' if hdr else ''
        rpr = ('<w:rPr><w:b/><w:sz w:val="16"/><w:szCs w:val="16"/></w:rPr>' if hdr
               else '<w:rPr><w:sz w:val="16"/><w:szCs w:val="16"/></w:rPr>')
        cells = "".join('<w:tc><w:tcPr><w:tcW w:type="dxa" w:w="%d"/>%s</w:tcPr><w:p><w:pPr><w:spacing w:before="20" w:after="20"/></w:pPr>%s</w:p></w:tc>'
                        % (w, shd, run(c, rpr)) for w, c in zip(widths, r))
        out.append("<w:tr>%s%s</w:tr>" % (trpr, cells))
    out.append("</w:tbl>")
    return "".join(out)

def add_image(root, png, name):
    from PIL import Image
    media = os.path.join(root, "word", "media")
    shutil.copy(png, os.path.join(media, name))
    relp = os.path.join(root, "word", "_rels", "document.xml.rels")
    rels = open(relp, encoding="utf-8").read()
    rid = "rIdImg_" + re.sub(r"\W", "_", name)
    if rid not in rels:
        rels = rels.replace("</Relationships>", '<Relationship Id="%s" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" Target="media/%s"/></Relationships>' % (rid, name))
        open(relp, "w", encoding="utf-8").write(rels)
    w, h = Image.open(png).size
    return rid, w, h

def figure(root, png, descr):
    name = os.path.basename(png)
    rid, w, h = add_image(root, png, name)
    _img[0] += 1
    cx = 5425000; cy = int(cx * h / w)
    return ('<w:p><w:pPr><w:keepNext/><w:jc w:val="center"/></w:pPr><w:r><w:drawing><wp:inline distT="0" distB="0" distL="0" distR="0">'
            '<wp:extent cx="%d" cy="%d"/><wp:effectExtent l="0" t="0" r="0" b="0"/><wp:docPr id="%d" name="%s" descr="%s"/>'
            '<wp:cNvGraphicFramePr><a:graphicFrameLocks xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" noChangeAspect="1"/></wp:cNvGraphicFramePr>'
            '<a:graphic xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"><a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/picture">'
            '<pic:pic xmlns:pic="http://schemas.openxmlformats.org/drawingml/2006/picture"><pic:nvPicPr><pic:cNvPr id="0" name="%s"/><pic:cNvPicPr/></pic:nvPicPr>'
            '<pic:blipFill><a:blip r:embed="%s"/><a:stretch><a:fillRect/></a:stretch></pic:blipFill>'
            '<pic:spPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="%d" cy="%d"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom></pic:spPr></pic:pic>'
            '</a:graphicData></a:graphic></wp:inline></w:drawing></w:r></w:p>'
            % (cx, cy, _img[0], escape(name), escape(descr), escape(name), rid, cx, cy))

def render(root, blocks, base_dir="."):
    out = []
    for b in blocks:
        t = b[0]
        if t == "p": out.append(para(b[1]))
        elif t == "b": out.append(bullet(b[1]))
        elif t in ("h3", "h4", "h5"): out.append(heading({"h3": "Ttulo3", "h4": "Ttulo4", "h5": "Ttulo5"}[t], b[1]))
        elif t == "tabla":
            _, title, key, src, widths, rows = b
            assert sum(widths) <= 8544, (title, sum(widths))
            out += [caption("T", key, title), table(widths, rows), source(src)]
        elif t == "figura":
            _, title, key, src, path = b
            out += [caption("F", key, title), figure(root, os.path.join(base_dir, path), title), source(src)]
        else:
            raise ValueError(t)
    return "".join(out)

def insert_after_bookmark(x, bm, xml, drop_empty_next=True):
    """Inserta xml después del párrafo que contiene el marcador bm (encabezado).
    Si el párrafo siguiente es vacío, lo reemplaza."""
    tag = 'w:name="%s"' % bm
    assert x.count(tag) == 1, bm
    i = x.find(tag)
    hend = x.find("</w:p>", i) + 6
    cut = hend
    if drop_empty_next:
        m = re.match(r'<w:p(?: [^>]*?)?(/>|><w:pPr><w:pStyle w:val="Prrafo"/></w:pPr></w:p>)', x[hend:hend + 500])
        if m:
            cut = hend + m.end()
    return x[:hend] + xml + x[cut:]

def renumerar(x):
    """Recalcula los números en caché de SEQ Tabla/Figura (orden de documento) y de los REF asociados."""
    nums, cnt = {}, {"Tabla": 0, "Figura": 0}
    pat = re.compile(r'<w:bookmarkStart w:id="\d+" w:name="(_Ref\w*?_([TF])_(\w+))"/>(.*?)<w:bookmarkEnd', re.S)
    def seq_fix(m):
        name, kind = m.group(1), m.group(2)
        lab = LAB[kind]; cnt[lab] += 1; nums[name] = cnt[lab]
        inner = re.sub(r'(SEQ %s \\\* ARABIC </w:instrText></w:r><w:r>(?:<w:rPr>.*?</w:rPr>)?<w:fldChar w:fldCharType="separate"/></w:r><w:r>(?:<w:rPr>.*?</w:rPr>)?<w:t>)[^<]*(</w:t>)' % lab,
                       lambda mm: mm.group(1) + str(cnt[lab]) + mm.group(2), m.group(4), flags=re.S)
        return m.group(0).replace(m.group(4), inner)
    x = pat.sub(seq_fix, x)
    def ref_fix(m):
        name = m.group(1)
        if name not in nums: return m.group(0)
        lab = LAB[re.search(r"_([TF])_", name).group(1)]
        return m.group(0)[:m.start(3) - m.start(0)] + "%s %d" % (lab, nums[name]) + m.group(0)[m.end(3) - m.start(0):]
    x = re.sub(r'REF (_Ref\w+) \\h </w:instrText></w:r><w:r>(?:<w:rPr>.*?</w:rPr>)?<w:fldChar w:fldCharType="separate"/></w:r><w:r>(?:<w:rPr>.*?</w:rPr>)?<w:t>([^<]*)</w:t>',
               lambda m: _ref_sub(m, nums), x, flags=re.S)
    return x, nums

def _ref_sub(m, nums):
    name = m.group(1)
    if name not in nums: return m.group(0)
    lab = LAB[re.search(r"_([TF])_", name).group(1)]
    s = m.group(0)
    return s[:s.rfind("<w:t>") + 5] + "%s %d" % (lab, nums[name]) + "</w:t>"
