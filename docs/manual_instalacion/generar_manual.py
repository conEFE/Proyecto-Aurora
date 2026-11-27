# -*- coding: utf-8 -*-
"""Genera el manual de instalación en Word y PDF desde MANUAL_INSTALACION.md.
Uso (desde la raíz del repositorio): python3 docs/manual_instalacion/generar_manual.py
Requiere pandoc, python-docx y LibreOffice (para el PDF, con docs/informe_final/herramientas/exportar_pdf.py)."""
import os, subprocess, sys, tempfile
from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Pt, RGBColor, Cm

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
MD = os.path.join(HERE, "MANUAL_INSTALACION.md")
DOCX = os.path.join(HERE, "Manual_de_instalacion_Aurora.docx")
PDF = os.path.join(HERE, "Manual_de_instalacion_Aurora.pdf")
ROSA, MORADO = RGBColor(0xA2, 0x1C, 0x5A), RGBColor(0x4B, 0x1D, 0x6B)

tmp = tempfile.mkdtemp()
ref = os.path.join(tmp, "ref.docx")
subprocess.run(["pandoc", "-o", ref, "--print-default-data-file", "reference.docx"], check=True)
# Estilos base del documento de referencia
d = Document(ref)


class _ById:
    def __init__(self, styles):
        self.m = {}
        for x in styles:
            self.m[x.name] = x; self.m[x.style_id] = x; self.m[x.name.lower()] = x

    def __getitem__(self, k):
        return self.m.get(k) or self.m.get(k.replace(" ", "")) or self.m[k.lower()]

    def __iter__(self):
        return iter(set(self.m.values()))


st = _ById(d.styles)
st["Normal"].font.name = "Arial"; st["Normal"].font.size = Pt(10.5)
for name in ("Body Text", "First Paragraph", "Compact"):
    if name in st.m or name.replace(" ", "") in st.m:
        st[name].font.name = "Arial"; st[name].font.size = Pt(10.5)
        st[name].paragraph_format.space_after = Pt(6)
for name, size, color in (("Title", 26, MORADO), ("Subtitle", 13, ROSA), ("Heading 1", 18, MORADO),
                          ("Heading 2", 13.5, ROSA), ("Heading 3", 11.5, MORADO)):
    s = st[name]; s.font.name = "Arial"; s.font.size = Pt(size); s.font.color.rgb = color; s.font.bold = True
    s.font.italic = False
st["Heading 1"].paragraph_format.page_break_before = True
for name in ("Author", "Date"):
    st[name].font.name = "Arial"; st[name].font.size = Pt(11)
for sec in d.sections:
    sec.left_margin = sec.right_margin = Cm(2.2); sec.top_margin = sec.bottom_margin = Cm(2)
d.save(ref)

subprocess.run(["pandoc", MD, "-o", DOCX, "--reference-doc", ref, "--toc", "--toc-depth=2",
                "-M", "toc-title=Contenido"], check=True)

# Tablas con bordes y encabezado sombreado; citas como recuadros de aviso
doc = Document(DOCX)


def shade(cell, fill):
    tcPr = cell._tc.get_or_add_tcPr()
    sh = OxmlElement("w:shd"); sh.set(qn("w:val"), "clear"); sh.set(qn("w:color"), "auto"); sh.set(qn("w:fill"), fill)
    tcPr.append(sh)


for t in doc.tables:
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    tblPr = t._tbl.tblPr
    borders = OxmlElement("w:tblBorders")
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        e = OxmlElement("w:%s" % edge)
        e.set(qn("w:val"), "single"); e.set(qn("w:sz"), "4"); e.set(qn("w:color"), "BFBFBF")
        borders.append(e)
    tblPr.append(borders)
    w = OxmlElement("w:tblW"); w.set(qn("w:w"), "5000"); w.set(qn("w:type"), "pct"); tblPr.append(w)
    for i, row in enumerate(t.rows):
        for c in row.cells:
            if i == 0:
                shade(c, "F3E5EE")
            for p in c.paragraphs:
                p.paragraph_format.space_after = Pt(2)
                for r in p.runs:
                    r.font.size = Pt(9.5)
                    if i == 0:
                        r.font.bold = True

for p in doc.paragraphs:
    if p.style.name in ("Block Text", "BlockText", "block text"):
        pPr = p._p.get_or_add_pPr()
        bd = OxmlElement("w:pBdr")
        left = OxmlElement("w:left")
        left.set(qn("w:val"), "single"); left.set(qn("w:sz"), "24"); left.set(qn("w:space"), "8"); left.set(qn("w:color"), "A21C5A")
        bd.append(left); pPr.append(bd)
        sh = OxmlElement("w:shd"); sh.set(qn("w:val"), "clear"); sh.set(qn("w:color"), "auto"); sh.set(qn("w:fill"), "FBF1F6")
        pPr.append(sh)
        for r in p.runs:
            r.font.size = Pt(10)
doc.save(DOCX)
print("ok", DOCX)

if "--sin-pdf" not in sys.argv:
    subprocess.run([sys.executable, os.path.join(REPO, "docs", "informe_final", "herramientas", "exportar_pdf.py"), DOCX, PDF],
                   check=True)
    print("ok", PDF)
