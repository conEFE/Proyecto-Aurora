# -*- coding: utf-8 -*-
"""Iteración 15: diagramas y capturas (maestro 1.4-rc -> 1.5-rc).
- III y VIII: BPMN del proceso afectado, proceso de negocio y organigrama de la Unidad 1 (figuras del equipo).
- X: arquitectura y diagrama cloud nuevos (reemplazan las figuras 9 y 10); diseños de la formulación como contraste.
- 10.7.1: diagrama del componente de análisis (redibujado con los datos del código; el de la Unidad 2 decía 512 × 512).
- Anexo: capturas del prototipo 2.10.2 con datos ficticios.
Uso: python3 iter15_figuras.py <dir_desempaquetado_maestro>"""
import sys, os, re, shutil
from xml.sax.saxutils import escape
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import maestro_lib as L

root = sys.argv[1]
BASE = os.path.dirname(HERE)  # docs/informe_final
p = os.path.join(root, "word", "document.xml")
x = open(p, encoding="utf-8").read(); L.init_ids(x)
PARA = re.compile(r"<w:p\b(?:(?!<w:p\b).)*?</w:p>", re.S)
R = lambda blocks: L.render(root, blocks, BASE)

def text_of(px):
    return "".join(re.findall(r"<w:t[^>]*>([^<]*)</w:t>", px))

def find_para(start_text, style=None):
    hits = [m for m in PARA.finditer(x) if text_of(m.group(0)).startswith(escape(start_text))
            and (style is None or ('w:val="%s"' % style) in m.group(0)[:400])]
    assert len(hits) == 1, (start_text, len(hits))
    return hits[0]

def insert_after(m, xml):
    global x
    x = x[:m.end()] + xml + x[m.end():]

def insert_before(m, xml):
    global x
    x = x[:m.start()] + xml + x[m.start():]

def rep(old, new):
    global x
    o, n = escape(old), escape(new); assert x.count(o) == 1, (old[:70], x.count(o)); x = x.replace(o, n)

SRC_U1 = "Fuente: Equipo Proyecto Aurora (2026a), formulación del proyecto (Unidad 1)."
SRC_U2 = "Fuente: Equipo Proyecto Aurora (2026c), informe de la Unidad 2."

# ---------------------------------------------------------------- III: proceso de negocio afectado
insert_after(find_para("La solución busca centralizar la información relevante para facilitar su consulta"), R([
 ("p", "La {F:u1flujo} representa el proceso afectado tal como se formuló en la Unidad 1: los carriles del paciente, el personal administrativo, el personal clínico y la plataforma, desde la entrega de antecedentes hasta el reporte y la actualización de las métricas. El detalle de los procesos implementados se presenta en el capítulo X con tres diagramas BPMN."),
 ("figura", "BPMN del proceso de atención y priorización de pacientes con sospecha de cáncer de mama (formulación)", "u1flujo", SRC_U1, "figuras/u1_flujo_proceso.png"),
]))

# ---------------------------------------------------------------- VIII: organigrama y proceso de negocio
insert_after(find_para("La formulación inicial representaba un cuarto rol de QA a tiempo parcial dentro del organigrama."), R([
 ("p", "La {F:u1org} reproduce el organigrama de la formulación. En la ejecución, la distribución cambió en un punto: el modelo de análisis de imágenes quedó a cargo de Juan Francisco Meneses, junto con la infraestructura, y la integración y la aplicación, de Felipe Campos (capítulo XV); el rol de QA no se incorporó."),
 ("figura", "Estructura organizacional del equipo según la formulación", "u1org", SRC_U1, "figuras/u1_organigrama.png"),
]))
m = find_para("Los procesos de negocio considerados corresponden al proceso objetivo de gestión inicial")
insert_after(m, R([
 ("p", "La {F:u1neg} resume, en una vista general, el proceso de negocio de la formulación: registro, creación del caso y carga de exámenes por el personal administrativo; procesamiento de imágenes y priorización por la plataforma; revisión y registro del resultado por el personal médico; y reportes e indicadores para la gestión."),
 ("figura", "Proceso de negocio de Proyecto Aurora (vista general de la formulación)", "u1neg", SRC_U1, "figuras/u1_proceso_negocio.png"),
]))

# ---------------------------------------------------------------- VII: los diagramas de la formulación sí se reproducen
rep("Por lo anterior, los diagramas de la formulación inicial no se reproducen en este capítulo. La arquitectura de aplicaciones, la topología, la infraestructura y la arquitectura implementada se detallan en el capítulo X, diferenciando lo diseñado de lo desplegado.",
    "Por lo anterior, los diagramas de arquitectura de la formulación se presentan en el capítulo X junto a los de la arquitectura implementada, rotulados como diseño de la formulación, para mostrar la evolución entre lo diseñado y lo desplegado.")

# ---------------------------------------------------------------- X: reemplazo de las figuras 9 y 10
def replace_media(rid_name, png, max_w=7680000, max_h=4400000):
    global x
    shutil.copy(os.path.join(BASE, png), os.path.join(root, "word", "media", rid_name))
    rid = "rIdImg_" + re.sub(r"\W", "_", rid_name)
    i = x.find('r:embed="%s"' % rid); assert i > 0, rid
    s = x.rfind("<w:drawing>", 0, i); e = x.find("</w:drawing>", i)
    seg = x[s:e]
    cx, cy = map(int, re.search(r'<wp:extent cx="(\d+)" cy="(\d+)"/>', seg).groups())
    w, h = Image.open(os.path.join(BASE, png)).size
    k = min(max_w / w, max_h / h); ncx, ncy = int(w * k), int(h * k)
    seg = seg.replace('<wp:extent cx="%d" cy="%d"/>' % (cx, cy), '<wp:extent cx="%d" cy="%d"/>' % (ncx, ncy))
    seg = seg.replace('<a:ext cx="%d" cy="%d"/>' % (cx, cy), '<a:ext cx="%d" cy="%d"/>' % (ncx, ncy))
    x = x[:s] + seg + x[e:]

replace_media("cap10_infraestructura.png", "figuras/it15_cloud.png")
replace_media("cap10_arquitectura.png", "figuras/it15_arquitectura.png")
rep(". Infraestructura desplegada del entorno de demostración", ". Infraestructura cloud desplegada del entorno de demostración (24-11-2026)")
rep("Fuente: Elaboración propia a partir de docs/ESTADO_AWS.md (actualizado al 16-11-2026) y de la configuración de despliegue del repositorio.",
    "Fuente: Elaboración propia a partir de docs/ESTADO_AWS.md (actualizado al 24-11-2026) y de la configuración de despliegue del repositorio.")
def source_after(bm):
    """Párrafo de fuente que sigue a la figura con el marcador bm."""
    i = x.find('w:name="%s"' % bm); assert i > 0, bm
    j = x.find("FiguraoTablaFuente", i)
    return next(m for m in PARA.finditer(x) if m.start() < j < m.end())

m10 = source_after("_Ref_F_arq")
old10 = escape("Fuente: Elaboración propia a partir del código fuente y de la documentación del repositorio (23-11-2026).")
assert old10 in m10.group(0)
x = x[:m10.start()] + m10.group(0).replace(old10, escape("Fuente: Elaboración propia a partir del código fuente y de la documentación del repositorio (24-11-2026, versión 2.10.2).")) + x[m10.end():]

# diseños de la formulación, como contraste (después de la fuente de cada figura)
src9 = source_after("_Ref_F_infra")
insert_after(src9, R([
 ("p", "Como contraste, la {F:u1infra} y la {F:u2infra} reproducen los diseños de infraestructura de la formulación y de la Unidad 2. Ambos ubicaban la solución en la región de São Paulo y contemplaban Cloudflare, Prometheus y Grafana, AWS Backup y copias en otra región; el entorno desplegado usa la región us-east-2 asignada al proyecto de AWS, que no admite recursos ni copias en otras regiones, con Caddy, CloudWatch y volcados diarios a S3. Las diferencias y su justificación se detallan en el capítulo VII y en la Tabla de componentes de infraestructura."),
 ("figura", "Arquitectura de infraestructura de la formulación (diseño, no implementado tal cual)", "u1infra", SRC_U1, "figuras/u1_arq_infraestructura.png"),
 ("figura", "Infraestructura objetivo en AWS de la Unidad 2 (diseño, no implementado tal cual)", "u2infra", SRC_U2, "figuras/u2_infra_objetivo.png"),
]))
src10 = source_after("_Ref_F_arq")
insert_after(src10, R([
 ("p", "La {F:u1apps} muestra la arquitectura de aplicaciones de la formulación. Se mantuvieron las capas y el monolito modular; el análisis de imágenes pasó de un módulo con modelos YOLO a un servicio independiente con una CNN y YOLO, y el monitoreo con Prometheus y Grafana se reemplazó por CloudWatch."),
 ("figura", "Arquitectura de aplicaciones de la formulación (diseño)", "u1apps", SRC_U1, "figuras/u1_arq_aplicaciones.png"),
]))

# ---------------------------------------------------------------- 10.7.1: componente de análisis
insert_after(find_para("El análisis automatizado de imágenes se implementa como un servicio de inferencia independiente, ubicado en backend/inference_service."), R([
 ("p", "La {F:cnn} muestra el recorrido de una imagen por el servicio: el preprocesamiento común y las dos etapas, la clasificación con ResNet18 —con su capa inicial adaptada a un canal y su capa de salida reemplazada— y la localización de masas con YOLO11s. El diagrama de la Unidad 2 indicaba una entrada de 512 × 512 píxeles; se redibujó con los valores del código, que usa 672 × 1024."),
 ("figura", "Componente de análisis automatizado de imágenes (CNN ResNet18 y YOLO11s)", "cnn", "Fuente: Elaboración propia a partir de backend/inference_service (analyzer.py y preprocessing.py), adaptada del diagrama de la Unidad 2 (Equipo Proyecto Aurora, 2026c).", "figuras/it15_cnn.png"),
]))

# ---------------------------------------------------------------- Anexo: capturas
anexo_tpl = find_para("Evidencia de la ejecución de pruebas", "Anexos").group(0)
anexo = anexo_tpl.replace(escape("Evidencia de la ejecución de pruebas"), escape("Capturas del prototipo (versión 2.10.2)"))
anexo = re.sub(r'<w:bookmark(Start|End)[^>]*/>', '', anexo)
SRC_CAP = "Fuente: Captura del prototipo, versión 2.10.2, ejecutado en un entorno local con datos ficticios y el proveedor de IA simulado (24-11-2026)."
CAPS = [
 ("01_ingreso", "Ingreso con RUT y contraseña"),
 ("02_cola", "Cola de triage priorizada por nivel, puntaje y espera (vista del médico)"),
 ("03_caso", "Caso con imágenes, resultado del análisis automatizado marcado como IA SIMULADA, validación médica y explicación del nivel"),
 ("04_casos", "Listado de casos con filtros por nivel, estado y fecha"),
 ("05_paciente", "Ficha de paciente con datos, casos e historia"),
 ("06_dashboard", "Dashboard con indicadores, calidad de las decisiones y desempeño del modelo"),
 ("07_administracion", "Administración: resumen del sistema, equipo y actividad reciente"),
 ("08_parametros", "Parámetros de triage versionados (vista del administrador)"),
]
blocks = [("p", "Las figuras siguientes muestran las pantallas principales de la versión 2.10.2, la misma desplegada en el entorno de demostración, ejecutada en un entorno local con los datos ficticios de los scripts de demostración. Las imágenes del caso son sintéticas y el resultado del análisis proviene del proveedor simulado, identificado en pantalla como «IA SIMULADA»; no corresponden a resultados clínicos.")]
for f, t in CAPS:
    blocks.append(("figura", t, "cap_" + f[3:], SRC_CAP, "figuras/capturas_2.10.2/%s.png" % f))
insert_before(find_para("Material Complementario (Apéndices).", "Ttulo2"), anexo + R(blocks))

# ---------------------------------------------------------------- páginas horizontales para figuras anchas
MAX_W, MAX_H = 7680000, 4400000
def para_span(i):
    s = x.rfind("<w:p>", 0, i); s2 = x.rfind("<w:p ", 0, i); s = max(s, s2)
    return s, x.find("</w:p>", i) + 6

def fit_drawings(a, b):
    """Agranda las figuras entre las posiciones a y b al área útil de una página horizontal."""
    global x
    seg = x[a:b]
    def fix(m):
        d = m.group(0)
        cx, cy = map(int, re.search(r'<wp:extent cx="(\d+)" cy="(\d+)"/>', d).groups())
        k = min(MAX_W / cx, MAX_H / cy); ncx, ncy = int(cx * k), int(cy * k)
        d = d.replace('<wp:extent cx="%d" cy="%d"/>' % (cx, cy), '<wp:extent cx="%d" cy="%d"/>' % (ncx, ncy))
        return d.replace('<a:ext cx="%d" cy="%d"/>' % (cx, cy), '<a:ext cx="%d" cy="%d"/>' % (ncx, ncy))
    seg = re.sub(r"<w:drawing>.*?</w:drawing>", fix, seg, flags=re.S)
    x = x[:a] + seg + x[b:]
    return len(seg) - (b - a)

def landscape(bm_first, bm_last=None):
    """Lleva a una sección horizontal desde la leyenda de bm_first hasta la fuente de bm_last (inclusive)."""
    global x
    bm_last = bm_last or bm_first
    cs, _ = para_span(x.find('w:name="%s"' % bm_first))
    i = x.find('w:name="%s"' % bm_last); assert i > 0 and cs > 0, (bm_first, bm_last)
    _, ce = para_span(i)
    _, fe = para_span(x.find("<w:drawing>", ce))
    ss, se = para_span(x.find("FiguraoTablaFuente", fe)); assert ss == fe, bm_last
    se += fit_drawings(cs, se)
    m = re.compile(r"<w:sectPr\b.*?</w:sectPr>", re.S).search(x, se); orig = m.group(0)
    base = re.sub(r"<w:pgNumType[^>]*/>", "", orig)
    base = re.sub(r"<w:titlePg[^>]*/>", "", base)
    base = re.sub(r"<w:(header|footer)Reference[^>]*/>", "", base)
    land = re.sub(r"<w:type[^>]*/>", "", base)
    land = land.replace('<w:pgSz w:w="12240" w:h="15840" w:code="1"/>', '<w:pgSz w:w="15840" w:h="12240" w:orient="landscape" w:code="1"/>')
    assert 'w:orient="landscape"' in land, (bm_first, "la sección siguiente no es vertical")
    land = land.replace("<w:sectPr>", '<w:sectPr><w:type w:val="nextPage"/>', 1) if "<w:sectPr>" in land else re.sub(r"(<w:sectPr\b[^>]*>)", r'\1<w:type w:val="nextPage"/>', land, count=1)
    rest = re.sub(r"<w:type[^>]*/>", "", base)
    rest = re.sub(r"(<w:sectPr\b[^>]*>)", r'\1<w:type w:val="nextPage"/>', rest, count=1)
    x = x[:m.start()] + rest + x[m.end():]
    x = x[:se] + '<w:p><w:pPr><w:sectPr>%s</w:sectPr></w:pPr></w:p>' % land[land.find(">") + 1:land.rfind("</w:sectPr>")] + x[se:]
    x = x[:cs] + '<w:p><w:pPr><w:sectPr>%s</w:sectPr></w:pPr></w:p>' % orig[orig.find(">") + 1:orig.rfind("</w:sectPr>")] + x[cs:]

# la figura de la formulación queda dentro de la página horizontal de la Figura de arquitectura: solo se agranda
a = x.find('w:name="_Ref_F_u1apps"'); fit_drawings(a, x.find("FiguraoTablaFuente", a))
landscape("_Ref_F_infra", "_Ref_F_u2infra")
landscape("_Ref_F_u1neg")
landscape("_Ref_F_u1flujo")

# capturas altas: limitar el alto para que la leyenda, la figura y la fuente quepan en la misma página vertical
MAX_H_V = 6000000
for k in [c[0][3:] for c in CAPS] + ["cnn"]:
    a = x.find('w:name="_Ref_F_cap_%s"' % k if k != "cnn" else 'w:name="_Ref_F_cnn"'); assert a > 0, k
    b = x.find("FiguraoTablaFuente", a)
    seg = x[a:b]
    cx, cy = map(int, re.search(r'<wp:extent cx="(\d+)" cy="(\d+)"/>', seg).groups())
    if cy > MAX_H_V:
        ncy = MAX_H_V; ncx = int(cx * ncy / cy)
        seg = seg.replace('<wp:extent cx="%d" cy="%d"/>' % (cx, cy), '<wp:extent cx="%d" cy="%d"/>' % (ncx, ncy))
        seg = seg.replace('<a:ext cx="%d" cy="%d"/>' % (cx, cy), '<a:ext cx="%d" cy="%d"/>' % (ncx, ncy))
        x = x[:a] + seg + x[b:]

x, nums = L.renumerar(x)
open(p, "w", encoding="utf-8").write(x)
print("ok; figuras:", sum(1 for k in nums if "_F_" in k))
