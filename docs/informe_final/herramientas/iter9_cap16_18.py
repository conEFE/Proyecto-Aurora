# -*- coding: utf-8 -*-
"""Iteración 9: capítulos XVI, XVII y XVIII (v0.12 -> v0.13)."""
import sys, os, re, json
from xml.sax.saxutils import escape
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import maestro_lib as L
import cap16_18_contenido as C
root = sys.argv[1]; cu_json = sys.argv[2]
p = os.path.join(root, "word", "document.xml")
x = open(p, encoding="utf-8").read(); L.init_ids(x)
base = os.path.dirname(HERE)
R = lambda b: L.render(root, b, base)

def rep(old, new):
    global x
    o, n = escape(old), escape(new); assert x.count(o) == 1, (old[:60], x.count(o)); x = x.replace(o, n)

def styled(style, runs):
    return '<w:p><w:pPr><w:pStyle w:val="%s"/></w:pPr>%s</w:p>' % (style, "".join(runs))

def ref_par(text):
    runs = []
    for k, part in enumerate(re.split(r"\*", text)):
        if part:
            runs.append(L.run(part, "<w:rPr><w:i/></w:rPr>" if k % 2 else ""))
    return styled("BibliografayReferencias", runs)

def glos_par(term, defi):
    return styled("Glorario", [L.run(term + ": ", "<w:rPr><w:b/></w:rPr>"), L.run(defi)])

def anexo(title):
    return styled("Anexos", [L.run(title)])

def bold_p(text):
    return "<w:p><w:pPr><w:keepNext/></w:pPr>%s</w:p>" % L.run(text, "<w:rPr><w:b/></w:rPr>")

# XVI
x = L.insert_after_bookmark(x, "_Toc177988523", R(C.CONCLUSIONES))
x = L.insert_after_bookmark(x, "_Toc177988524", R(C.RECOMENDACIONES))
# XVII
x = L.insert_after_bookmark(x, "_Toc177988526", "".join(glos_par(t, d) for t, d in C.GLOSARIO))
x = L.insert_after_bookmark(x, "_Toc177988527", "".join(ref_par(r) for r in C.REFERENCIAS))
# XVIII
cus = json.load(open(cu_json, encoding="utf-8")) + C.CU17_18
xml = [anexo("Especificación de casos de uso"),
       L.para("La especificación de CU01 a CU16 proviene del informe de Unidad 2 (Equipo Proyecto Aurora, 2026c); CU17 y CU18 se especifican en este informe a partir del comportamiento verificado en el código y en las pruebas.")]
for c in cus:
    xml.append(bold_p("%s. %s" % (c["id"], c["name"])))
    xml.append(L.table([2200, 6344], [["Elemento", "Descripción"]] + [[k, v] for k, v in c["rows"]]))
schema = json.load(open(os.path.join(HERE, "schema_modelos.json"), encoding="utf-8"))
rows = [["Tabla", "Columna", "Tipo", "Nulo", "Clave / restricción"]]
for t, v in schema.items():
    first = True
    for n, typ, pk, nul, fks, *rest in v["cols"]:
        key = "PK" if pk else ("FK → " + ", ".join(fks) if fks else "")
        if rest and rest[0] and not pk: key = (key + "; " if key else "") + "Única"
        rows.append([t if first else "", n, typ, "Sí" if nul else "No", key]); first = False
xml += [anexo("Diccionario de datos"),
        L.para("El diccionario de datos se generó a partir de los modelos SQLAlchemy del repositorio (23-11-2026) y describe las 18 tablas del modelo con sus columnas, tipos, obligatoriedad y claves."),
        R([("tabla", "Diccionario de datos", "dicc", "Fuente: Elaboración propia; generado desde los modelos SQLAlchemy del repositorio (herramientas/schema_modelos.json).", [1900, 2200, 1900, 600, 1944], rows)])]
xml += [anexo("Configuración inicial del triage"), R(C.TRIAGE)]
xml += [anexo("Evidencia de la ejecución de pruebas"), R(C.EVIDENCIA)]
x = L.insert_after_bookmark(x, "_Toc177988529", "".join(xml))
x = L.insert_after_bookmark(x, "_Toc177988530", R(C.MATERIAL))

# Ajustes de citas
rep("(Amazon Web Services, s.f.-b)", "(Amazon Web Services, s.f.)")
rep("los conjuntos de entrenamiento (CBIS-DDSM y CMMD) no contienen mamografías sanas",
    "los conjuntos de entrenamiento (CBIS-DDSM, Lee et al., 2017; CMMD, Cui et al., 2021) no contienen mamografías sanas")

# Normaliza «s.f.» a «s. f.» (APA 7 en español) en todo el documento
x = x.replace("s.f.)", "s. f.)").replace("s.f.-", "s. f.-").replace("(s.f.)", "(s. f.)").replace(", s.f.", ", s. f.")
x = L.set_control_row(x, "XVI. Conclusiones y recomendaciones", "Redactadas en v0.13: cumplimiento por objetivo, gestión, aprendizajes y nueve recomendaciones.", "Revisión del equipo.")
x = L.set_control_row(x, "XVII. Glosario y referencias", "Glosario (23 términos) y referencias APA 7 de todas las citas del informe en v0.13.", "Pendiente: completar Shah et al. (2023); confirmar título de 2026c y fechas de consulta de fuentes web.")
x = L.set_control_row(x, "XVIII. Anexos", "Anexos en v0.13: especificación de CU01–CU18, diccionario de datos (18 tablas), configuración del triage, evidencia de pruebas y material complementario.", "Revisar con el equipo; agregar notas de la revisión del 20-11 si existen.")
x = L.set_control_version(x, "0.13", "23-11-2026")
x, nums = L.renumerar(x)
open(p, "w", encoding="utf-8").write(x)
print("ok", {k[7:]: v for k, v in nums.items() if k[7:] in ("dicc", "triage_par")})
