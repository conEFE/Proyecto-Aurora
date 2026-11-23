# -*- coding: utf-8 -*-
"""Iteración 10: cierre editorial del maestro (v0.13 -> v1.0-rc).
- Páginas horizontales para figuras anchas.
- Índice de figuras apuntando a la secuencia «Figura».
- Leyenda y anchos de la tabla de historias de usuario.
- Fecha de portada.
- Retiro de la sección interna «Control de integración del informe».
- Actualización de campos al abrir en Word.
Uso: python3 iter10_editorial.py <dir_desempaquetado_maestro>"""
import sys, os, re
from xml.sax.saxutils import escape
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import maestro_lib as L

root = sys.argv[1]
p = os.path.join(root, "word", "document.xml")
x = open(p, encoding="utf-8").read(); L.init_ids(x)

def para_span(i):
    s = max(x.rfind("<w:p ", 0, i), x.rfind("<w:p>", 0, i)); e = x.find("</w:p>", i) + 6
    return s, e

# 1) Fecha de portada
assert x.count("[MES, AÑO DE ENTREGA]") == 1
x = x.replace("[MES, AÑO DE ENTREGA]", "Diciembre, 2026")

# 1b) Títulos de plantilla: encabezados vacíos y nota «(puede ir como anexo)»
x = x.replace('<w:p><w:pPr><w:pStyle w:val="Ttulo3"/><w:numPr><w:ilvl w:val="0"/><w:numId w:val="0"/></w:numPr><w:ind w:left="1080"/></w:pPr></w:p>', '<w:p/>')
_i = x.rfind("puede ir como anexo"); assert _i > 0
_s = max(x.rfind("<w:p ", 0, _i), x.rfind("<w:p>", 0, _i)); _e = x.find("</w:p>", _i) + 6
_seg = re.sub(r"<w:r\b[^>]*>(?:(?!</w:r>).)*?<w:t[^>]*>[^<]*</w:t></w:r>", "", x[_s:_e], flags=re.S)
_seg = _seg.replace("</w:p>", "<w:r><w:t>Diccionario de datos.</w:t></w:r></w:p>")
_seg = re.sub(r"(<w:bookmarkEnd[^>]*/>)(<w:r><w:t>Diccionario de datos.</w:t></w:r>)", r"\2\1", _seg)
x = x[:_s] + _seg + x[_e:]

# 2) Índice de figuras: secuencia «Figura»
assert x.count('TOC \\h \\z \\c &quot;Ilustración&quot;') == 1
x = x.replace('TOC \\h \\z \\c &quot;Ilustración&quot;', 'TOC \\h \\z \\c &quot;Figura&quot;')

# 3) Tabla de historias de usuario: anchos coherentes y leyenda
i = x.find(escape("Historia de usuario / necesidad")); assert i > 0
t0 = x.rfind("<w:tbl>", 0, i); t1 = x.find("</w:tbl>", i) + 8
tbl = x[t0:t1]
widths = [792, 2880, 1368, 3504]
tbl = re.sub(r"<w:tblGrid>.*?</w:tblGrid>", "<w:tblGrid>" + "".join('<w:gridCol w:w="%d"/>' % w for w in widths) + "</w:tblGrid>", tbl, count=1, flags=re.S)
tbl = tbl.replace('<w:tcW w:type="dxa" w:w="3672"/>', '<w:tcW w:type="dxa" w:w="3504"/>')
tbl = tbl.replace('<w:tblW w:type="auto" w:w="0"/>', '<w:tblW w:type="dxa" w:w="8544"/>', 1)
# tamaño de letra uniforme (las filas HU08–HU12 se agregaron sin tamaño explícito)
tbl = re.sub(r"<w:r>(<w:t[ >])", r'<w:r><w:rPr><w:sz w:val="15"/><w:szCs w:val="15"/></w:rPr>\1', tbl)
cap = L.caption("T", "hu", "Historias de usuario y priorización MoSCoW")
src = L.source("Fuente: Elaboración propia a partir de la formulación inicial (Equipo Proyecto Aurora, 2026a); HU08 reformulada y HU09–HU12 con prioridades aprobadas en este informe.")
x = x[:t0] + cap + tbl + src + x[t1:]

# 4) Retiro de «Control de integración del informe» (registro interno; su contenido está en el registro de revisiones)
i = x.find("<w:t>Control de integración del informe</w:t>"); assert i > 0
s, _ = para_span(i)
pb = x.rfind('<w:p><w:r><w:br w:type="page"/></w:r></w:p>', 0, s)
start = pb if pb >= 0 and s - pb < 80 else s
end = x.rfind("<w:sectPr", 0, len(x))
assert end > start
x = x[:start] + x[end:]

# 5) Páginas horizontales para figuras anchas
LAND = ["_RefCap6_F_gantt", "_Ref_F_bpmn1", "_Ref_F_bpmn2", "_Ref_F_bpmn3", "_Ref_F_topo", "_Ref_F_arq", "_Ref_F_gantt_xv"]
MAX_W, MAX_H = 7680000, 4400000   # EMU: ancho útil horizontal (~8,4 in) y alto disponible bajo la leyenda

def find_sect_after(pos):
    m = re.compile(r"<w:sectPr\b.*?</w:sectPr>", re.S).search(x, pos)
    return m

positions = []
for bm in LAND:
    i = x.find('w:name="%s"' % bm); assert i > 0, bm
    positions.append((i, bm))
for i, bm in sorted(positions, reverse=True):
    cs, ce = para_span(i)                        # leyenda
    fs, fe = para_span(x.find("<w:drawing>", ce))  # figura
    assert fs == ce, bm
    ss, se = para_span(x.find("FiguraoTablaFuente", fe))  # fuente
    assert ss == fe, bm
    # ampliar la figura
    fig = x[fs:fe]
    cx, cy = map(int, re.search(r'<wp:extent cx="(\d+)" cy="(\d+)"/>', fig).groups())
    k = min(MAX_W / cx, MAX_H / cy)
    ncx, ncy = int(cx * k), int(cy * k)
    fig = fig.replace('<wp:extent cx="%d" cy="%d"/>' % (cx, cy), '<wp:extent cx="%d" cy="%d"/>' % (ncx, ncy))
    fig = fig.replace('<a:ext cx="%d" cy="%d"/>' % (cx, cy), '<a:ext cx="%d" cy="%d"/>' % (ncx, ncy))
    # secciones
    m = find_sect_after(se); orig = m.group(0)
    base = re.sub(r"<w:pgNumType[^>]*/>", "", orig)
    base = re.sub(r"<w:titlePg[^>]*/>", "", base)
    base = re.sub(r"<w:(header|footer)Reference[^>]*/>", "", base)
    portrait_type = re.search(r'<w:type w:val="([^"]+)"/>', orig)
    s1 = orig  # la primera parte conserva todas las propiedades originales
    land = re.sub(r"<w:type[^>]*/>", "", base)
    land = land.replace('<w:pgSz w:w="12240" w:h="15840" w:code="1"/>', '<w:pgSz w:w="15840" w:h="12240" w:orient="landscape" w:code="1"/>')
    assert 'w:orient="landscape"' in land, bm
    land = land.replace("<w:sectPr>", '<w:sectPr><w:type w:val="nextPage"/>', 1) if "<w:sectPr>" in land else re.sub(r"(<w:sectPr\b[^>]*>)", r'\1<w:type w:val="nextPage"/>', land, count=1)
    rest = re.sub(r"<w:type[^>]*/>", "", base)
    rest = re.sub(r"(<w:sectPr\b[^>]*>)", r'\1<w:type w:val="nextPage"/>', rest, count=1)
    # sustituir la sección original por la del resto; insertar las dos nuevas
    x = x[:m.start()] + rest + x[m.end():]
    x = x[:se] + '<w:p><w:pPr><w:sectPr>%s</w:sectPr></w:pPr></w:p>' % land[land.find(">") + 1:land.rfind("</w:sectPr>")] + x[se:]
    x = x[:cs] + '<w:p><w:pPr><w:sectPr>%s</w:sectPr></w:pPr></w:p>' % s1[s1.find(">") + 1:s1.rfind("</w:sectPr>")] + x[cs:cs + (fs - cs)] + fig + x[fe:]

x, nums = L.renumerar(x)
open(p, "w", encoding="utf-8").write(x)

# 6) Actualizar campos al abrir en Word
sp = os.path.join(root, "word", "settings.xml")
s = open(sp, encoding="utf-8").read()
if "w:updateFields" not in s:
    for tag in ("<w:hdrShapeDefaults", "<w:footnotePr", "<w:endnotePr", "<w:compat", "<w:docVars", "<w:rsids", "<m:mathPr", "<w:themeFontLang", "<w:clrSchemeMapping"):
        k = s.find(tag)
        if k > 0:
            s = s[:k] + '<w:updateFields w:val="true"/>' + s[k:]; break
    else:
        raise SystemExit("settings.xml sin punto de inserción para updateFields")
    open(sp, "w", encoding="utf-8").write(s)
print("ok", len(nums))
