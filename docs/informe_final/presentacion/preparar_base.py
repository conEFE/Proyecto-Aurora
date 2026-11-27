# -*- coding: utf-8 -*-
"""Arma base.pptx desde plantilla_u2.pptx: duplica las diapositivas que se usan dos veces, fija el orden de las 28
diapositivas de la presentación del informe final y elimina las que sobran. Después: python3 generar_presentacion.py

Uso (desde esta carpeta):  python3 preparar_base.py [<carpeta de la skill pptx>]
Necesita los scripts add_slide.py y clean.py de la skill pptx de Claude (por defecto se buscan en ~/.claude/skills).
"""
import glob, os, re, shutil, subprocess, sys, zipfile

skill = sys.argv[1] if len(sys.argv) > 1 else (glob.glob(os.path.expanduser("~/.claude/skills/**/pptx/scripts/add_slide.py"), recursive=True) or [""])[0].rsplit("/scripts/", 1)[0]
assert skill and os.path.exists(os.path.join(skill, "scripts", "add_slide.py")), "No encuentro la skill pptx; pase su carpeta como argumento"
UN = "_base_tmp"
shutil.rmtree(UN, ignore_errors=True)
zipfile.ZipFile("plantilla_u2.pptx").extractall(UN)

# Diapositivas de la plantilla (nombre de archivo -> contenido en la U2):
# slide1 portada · slide25 factibilidad (3 tarjetas) · slide22 matriz de tecnologías · slide24 herramientas · slide30 casos de uso
# slide35 arquitectura · slide34 infraestructura · slide46 factibilidad económica · slide47 demanda · slide26 procesos (3 cajas)
# slide48 prototipo · slide49 conclusiones · slide19 cierre · slide21 «¿dónde estamos?» · slide39 plan de pruebas
# slide23 Scrumban · slide37 KPI · slide38 SLA · slide41 disponibilidad · slide43 mantención
for src in ["slide25", "slide25", "slide22", "slide22", "slide46", "slide19", "slide39", "slide21"]:
    subprocess.run([sys.executable, os.path.join(skill, "scripts", "add_slide.py"), UN + "/", src + ".xml"], check=True, stdout=subprocess.DEVNULL)
# Copias creadas, en orden: slide50 y slide51 (de 25), slide52 y slide53 (de 22), slide54 (de 46), slide55 (de 19), slide56 (de 39), slide57 (de 21)
ORDER = ["slide1", "slide50", "slide52", "slide51", "slide24", "slide22", "slide30", "slide53", "slide35", "slide34", "slide46", "slide47",
         "slide26", "slide48", "slide49", "slide19",                                     # principales (16)
         "slide55", "slide21", "slide56", "slide23", "slide37", "slide38", "slide39", "slide54", "slide41", "slide43", "slide57", "slide25"]  # respaldo (12)

rels = open(UN + "/ppt/_rels/presentation.xml.rels", encoding="utf-8").read()
f2r = {}
for m in re.finditer(r"<Relationship [^>]*>", rels):
    t = m.group(0); r = re.search(r'Id="(rId\d+)"', t); g = re.search(r'Target="slides/(slide\d+)\.xml"', t)
    if r and g:
        f2r[g.group(1)] = r.group(1)
p = UN + "/ppt/presentation.xml"; x = open(p, encoding="utf-8").read()
ids = dict((r, i) for i, r in re.findall(r'<p:sldId id="(\d+)" r:id="(rId\d+)"/>', x))
new = "<p:sldIdLst>" + "".join('<p:sldId id="%s" r:id="%s"/>' % (ids[f2r[f]], f2r[f]) for f in ORDER) + "</p:sldIdLst>"
x = re.sub(r"<p:sldIdLst>.*?</p:sldIdLst>", new, x, flags=re.S); open(p, "w", encoding="utf-8").write(x)
subprocess.run([sys.executable, os.path.join(skill, "scripts", "clean.py"), UN + "/"], check=True, stdout=subprocess.DEVNULL)
if os.path.exists("base.pptx"):
    os.remove("base.pptx")
subprocess.run("cd %s && zip -XrDqy ../base.pptx ." % UN, shell=True, check=True)
shutil.rmtree(UN)
print("base.pptx con %d diapositivas" % len(ORDER))
