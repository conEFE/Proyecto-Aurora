# -*- coding: utf-8 -*-
"""Iteración 11: ajustes por plantilla y rúbrica de defensa EA5 (maestro 1.0-rc -> 1.1-rc).
(a) títulos de plantilla; (b) soluciones existentes (IV); (c) factibilidad integral (XIV);
(d) integración del stack (IX) y sustentabilidad (8.3); (e) prueba de rendimiento local (XI, XII, resumen, XV, XVI).
Uso: python3 iter11_rubrica.py <dir_desempaquetado_maestro> <dir_evidencia_rendimiento>"""
import sys, os, re, json, glob
from xml.sax.saxutils import escape
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import maestro_lib as L
import iter11_contenido as C

root, evid = sys.argv[1], sys.argv[2]
p = os.path.join(root, "word", "document.xml")
x = open(p, encoding="utf-8").read(); L.init_ids(x)
base = os.path.dirname(HERE)
R = lambda b: L.render(root, b, base)
PARA = re.compile(r"<w:p\b(?:(?!<w:p\b).)*?</w:p>", re.S)

def text_of(px):
    return "".join(re.findall(r"<w:t[^>]*>([^<]*)</w:t>", px))

def find_para(start_text, style=None, last=False, exact=False):
    hits = []
    for m in PARA.finditer(x):
        t = text_of(m.group(0))
        if (t == escape(start_text)) if exact else t.startswith(escape(start_text)):
            if style is None or ('w:val="%s"' % style) in m.group(0)[:400]:
                hits.append(m)
    assert hits, start_text
    if not last:
        assert len(hits) == 1, (start_text, len(hits))
    return hits[-1]

def insert_before(m, xml):
    global x
    x = x[:m.start()] + xml + x[m.start():]

def insert_after(m, xml):
    global x
    x = x[:m.end()] + xml + x[m.end():]

def set_text(m, new):
    """Reemplaza el texto de un párrafo conservando pPr y el formato del primer run."""
    global x
    px = m.group(0)
    ppr = re.search(r"<w:pPr>.*?</w:pPr>|<w:pPr/>", px, re.S)
    rpr = re.search(r"<w:r\b[^>]*>(<w:rPr>.*?</w:rPr>)", px, re.S)
    head = px[:px.find(">") + 1]
    new_px = head + (ppr.group(0) if ppr else "") + L.run(new, rpr.group(1) if rpr else "") + "</w:p>"
    x = x[:m.start()] + new_px + x[m.end():]

def cell(old, new, nth=None):
    """Cambia el texto de una celda/párrafo identificado por su texto exacto (único, o el n-ésimo)."""
    ms = [m for m in PARA.finditer(x) if text_of(m.group(0)) == escape(old)]
    if nth is None:
        assert len(ms) == 1, (old, len(ms)); m = ms[0]
    else:
        m = ms[nth]
    set_text(m, new)

def rep(old, new):
    global x
    o, n = escape(old), escape(new); assert x.count(o) == 1, (old[:70], x.count(o)); x = x.replace(o, n)

# ---------------------------------------------------------------- (a) títulos de plantilla
m = find_para("Diccionario de datos.", "Ttulo4", exact=True)
x = x[:m.start()] + m.group(0).replace("<w:t>Diccionario de datos.</w:t>", "<w:t>Diccionario de datos (puede ir como anexo).</w:t>") + x[m.end():]
m = find_para("Componente de análisis automatizado de imágenes.", "Ttulo3")
x = x[:m.start()] + m.group(0).replace('<w:pStyle w:val="Ttulo3"/>', '<w:pStyle w:val="Ttulo4"/>', 1) + x[m.end():]
# encabezados vacíos sin numeración heredados de la plantilla (aparecían en blanco en la tabla de contenido)
n_empty = len(re.findall(r'<w:p [^>]*><w:pPr><w:pStyle w:val="Ttulo3"/><w:numPr><w:ilvl w:val="0"/><w:numId w:val="0"/></w:numPr><w:ind w:left="1080"/></w:pPr></w:p>', x))
x = re.sub(r'<w:p [^>]*><w:pPr><w:pStyle w:val="Ttulo3"/><w:numPr><w:ilvl w:val="0"/><w:numId w:val="0"/></w:numPr><w:ind w:left="1080"/></w:pPr></w:p>', "<w:p/>", x)

# ---------------------------------------------------------------- (b) IV soluciones existentes
insert_before(find_para("Relación del marco teórico con Proyecto Aurora", "Ttulo3"), R(C.SOLUCIONES))

# ---------------------------------------------------------------- (d) 8.3 y IX
insert_after(find_para("Proyecto Aurora no reemplaza la evaluación ni la decisión clínica del personal médico."), R(C.SUSTENTABILIDAD))
insert_after(find_para("El equipamiento de hardware del equipo se describe en el apartado"), R(C.INTEGRACION))

# ---------------------------------------------------------------- (c) XIV factibilidad integral
insert_after(find_para("La variable crítica es la demanda"), R(C.FACTIBILIDAD))

# ---------------------------------------------------------------- (e) rendimiento local
res = {}
for f in glob.glob(os.path.join(evid, "carga_*.json")):
    if "antes" in os.path.basename(f):  # ejecución previa a la corrección: se documenta aparte
        continue
    d = json.load(open(f, encoding="utf-8")); res[d["usuarios_virtuales"]] = d
assert 100 in res and 10 in res, sorted(res)
r100 = res[100]; t100 = r100["total"]
fmt = lambda v: f"{round(v):,}".replace(",", ".") if v >= 100 else ("%.1f" % v).replace(".", ",")
p95_100 = t100["p95_ms"]; ok100 = p95_100 <= 3000 and t100["errors"] == 0
peor = max(r100["endpoints"].items(), key=lambda kv: kv[1]["p95_ms"])

RENDIMIENTO = [
 ("h4", "Prueba de rendimiento en entorno local"),
 ("p", "Para obtener una primera evidencia del requerimiento RNF03, el 24-11-2026 se ejecutó el caso PC-01 en un entorno local, con un script de carga incorporado al repositorio (backend/scripts/load_test.py) en lugar de Locust. El entorno fue un contenedor Linux de 4 vCPU y 15 GB de RAM, con PostgreSQL 16.15 local, la API con dos procesos de uvicorn (igual que la imagen de producción), el proveedor de inferencia simulado y 130 pacientes y 147 casos ficticios. Cada usuario virtual inicia sesión como médico y repite sin pausa las consultas más frecuentes: lista de casos, cola de triage, lista de pacientes, detalle de un caso, notificaciones y métricas del dashboard. La {T:carga} resume los resultados."),
 ("p", "La primera ejecución detectó un defecto. Con 50 usuarios virtuales la API dejó de responder: todas las solicitudes agotaron el tiempo de espera de 30 s y el servicio no se recuperó. La causa estaba en el middleware que registra la duración de cada solicitud: pedía una segunda conexión al mismo pool de la base de datos que ocupa el endpoint, que retiene la suya hasta enviar la respuesta; con más de 15 solicitudes simultáneas por proceso, todas retenían una conexión y esperaban otra. Se corrigió con un pool auxiliar para esas escrituras y su ejecución fuera del bucle de eventos (la carga de imágenes recibió el mismo tratamiento), se agregó una prueba de regresión —la suite queda en 316 pruebas, todas aprobadas el 24-11-2026— y la serie completa se repitió con el código corregido. La corrección está en el repositorio, pero no se ha desplegado en el entorno de demostración, que sigue en la versión 2.10.0."),
 ("tabla", "Resultados de la prueba de rendimiento en entorno local", "carga",
  "Fuente: Elaboración propia a partir de la ejecución del 24-11-2026 con el código corregido (evidencias/rendimiento_2026-11-24/ de la carpeta del informe).",
  [1300, 950, 1100, 850, 1100, 1050, 1050, 1094], C.rendimiento(res)),
 ("p", ("Con 100 usuarios virtuales durante %d minutos, el percentil 95 fue de %s ms, %s la meta de 3 s, con %d errores. "
        "El endpoint más lento fue %s, con un p95 de %s ms. El inicio de sesión, medido aparte por su límite de intentos, tuvo una mediana cercana a %s ms, explicada por el costo deliberado de bcrypt. ")
       % (round(r100["duracion_s"] / 60), fmt(p95_100), "bajo" if p95_100 <= 3000 else "sobre", t100["errors"],
          peor[0].replace("GET ", ""), fmt(peor[1]["p95_ms"]), fmt(r100["login"]["p50_ms"]))
      + ("Con 50 usuarios el p95 fue de %s ms, con %d errores. " % (fmt(res[50]["total"]["p95_ms"]), res[50]["total"]["errors"]))
      + ("En consecuencia, PC-01 no se aprueba: en este entorno la meta se cumple hasta 50 usuarios virtuales. Con 100, el servicio no se bloqueó, pero se saturó: el rendimiento bajó a %s solicitudes por segundo y los errores correspondieron a esperas de más de 30 s por una conexión libre a la base de datos. " % (fmt(t100["req_por_s"])) if not ok100 else "")
      + "Como los usuarios virtuales no esperan entre acciones, la carga es más intensa que la de igual número de usuarios clínicos reales, por lo que el resultado no se traduce directamente en un número de usuarios soportados."),
 ("p", "Esta evidencia tiene alcance limitado: el servidor y el generador de carga compartieron la máquina, no se incluyeron la carga de imágenes ni la inferencia, y el entorno local tiene más capacidad que la instancia t4g.micro del entorno de demostración, cuyo rendimiento no se midió. La prueba de estrés PC-02 no se ejecutó."),
]
insert_before(find_para("Matriz de trazabilidad", "Ttulo4"), R(RENDIMIENTO))

def row_after(first, second):
    ms = list(PARA.finditer(x))
    for i in range(len(ms) - 1):
        if text_of(ms[i].group(0)) == first and text_of(ms[i + 1].group(0)) == second:
            return ms, i
    raise AssertionError((first, second))
estado_pc01 = "Ejecutado el 24-11-2026 en entorno local: p95 %s ms, %d errores (%s)" % (fmt(p95_100), t100["errors"], "aprobado" if ok100 else "no aprobado")
ms, i = row_after("Pruebas de carga", "Locust")
assert text_of(ms[i + 3].group(0)) == "Planificado; no implementado"
set_text(ms[i + 3], "Implementado (24-11-2026); ejecutado solo en entorno local")
ms, i = row_after("Pruebas de carga", "Locust")
set_text(ms[i + 1], "Script de carga propio (backend/scripts/load_test.py); Locust no adoptado")
cell("Sin medición real ni prueba de carga", "Sin medición en el entorno de demostración; prueba local: p95 de %s ms con 50 usuarios y %s ms con 100" % (fmt(res[50]["total"]["p95_ms"]), fmt(p95_100)))
ms, i = row_after("PC-01", "RNF03")
assert text_of(ms[i + 3].group(0)) == "Locust (no implementado)" and text_of(ms[i + 4].group(0)) == "No ejecutado"
set_text(ms[i + 4], estado_pc01)
ms, i = row_after("PC-01", "RNF03")
set_text(ms[i + 3], "backend/scripts/load_test.py (entorno local)")
ms, i = row_after("PC-02", "RNF02, RNF04")
assert text_of(ms[i + 3].group(0)) == "Locust (no implementado)"
set_text(ms[i + 3], "No implementada")
cell("No ejecutadas: herramienta no implementada", "PC-01 ejecutada el 24-11-2026 en entorno local: p95 %s ms con 100 usuarios (no cumple; sí con 50); PC-02 no ejecutada" % fmt(p95_100))
cell("Sin evidencia: PC-01 no ejecutado", "Evidencia parcial: PC-01 en entorno local cumple con 50 usuarios y no con 100; sin medición en el entorno de demostración")
rep("No acreditan rendimiento bajo carga, disponibilidad del servicio, resistencia a ataques dinámicos, usabilidad ni desempeño clínico, cuyas pruebas no se han ejecutado. En consecuencia, los indicadores de rendimiento y disponibilidad del capítulo XI no cuentan aún con medición.",
    "El rendimiento bajo carga solo se midió en un entorno local (apartado siguiente); no se acreditan la disponibilidad del servicio, la resistencia a ataques dinámicos, la usabilidad ni el desempeño clínico, cuyas pruebas no se han ejecutado. En consecuencia, los indicadores de rendimiento y disponibilidad del capítulo XI no cuentan aún con medición en el entorno de demostración.")
rep("Quedan pendientes las pruebas de carga y de seguridad dinámica, la validación clínica formal del modelo y un piloto con una institución de salud.",
    "Una prueba de carga local cumplió la meta de tiempo de respuesta hasta 50 usuarios virtuales (percentil 95 de " + fmt(res[50]["total"]["p95_ms"]) + " ms) y la superó con 100 (%s ms). Quedan pendientes la prueba de carga en el entorno de demostración, el escaneo dinámico de seguridad, la validación clínica formal del modelo y un piloto con una institución de salud." % fmt(p95_100))
rep("Load and dynamic security testing, a formal clinical validation of the model and a pilot with a healthcare institution remain pending.",
    "A local load test met the response-time target up to 50 virtual users (95th percentile of " + ("%.0f" % res[50]["total"]["p95_ms"]) + " ms) and exceeded it with 100 (%s ms). Load testing in the demonstration environment, dynamic security scanning, a formal clinical validation of the model and a pilot with a healthcare institution remain pending." % ("%.0f" % p95_100 if p95_100 >= 100 else ("%.1f" % p95_100)))
rep("con pruebas de carga y carga de imágenes DICOM pendientes;", "con pruebas de carga y carga de imágenes DICOM pendientes (la prueba de carga se ejecutó después, el 24-11-2026, en entorno local);")
rep("• Ejecutar las pruebas de carga y estrés y el escaneo dinámico de seguridad, y registrar sus resultados antes de un piloto.",
    "• Dimensionar la capacidad para la meta de rendimiento (procesos de la API, tamaño del pool de conexiones y de la instancia), repetir la prueba de carga en el entorno de demostración, ejecutar la prueba de estrés y el escaneo dinámico de seguridad, y registrar sus resultados antes de un piloto.")
rep("y la ejecución de la prueba de carga.", "y la ejecución de la prueba de carga en ese entorno.")

# copia de respaldo: el proyecto de AWS no permite acciones entre regiones; la alternativa es una copia fuera de AWS
rep("la prueba de restauración de respaldos y la copia de respaldo fuera de la región.",
    "la prueba de restauración de respaldos y una copia de respaldo fuera de AWS (el proyecto de AWS no permite copias entre regiones).")
rep("• Probar y documentar la restauración de respaldos, incorporar copias fuera de la región y configurar monitoreo externo de disponibilidad y alarmas.",
    "• Probar y documentar la restauración de respaldos, incorporar una copia cifrada fuera de AWS (el proyecto de AWS no permite copias entre regiones) y configurar monitoreo externo de disponibilidad y alarmas.")

# ---------------------------------------------------------------- referencias nuevas (orden alfabético)
def styled(style, runs):
    return '<w:p><w:pPr><w:pStyle w:val="%s"/></w:pPr>%s</w:p>' % (style, "".join(runs))
def ref_par(text):
    return styled("BibliografayReferencias", [L.run(part, "<w:rPr><w:i/></w:rPr>" if k % 2 else "") for k, part in enumerate(text.split("*")) if part])

rep("Amazon Web Services. (s. f.). ", "Amazon Web Services. (s. f.-b). ")
NUEVAS = [
 "Amazon Web Services. (s. f.-a). *AWS Graviton sustainability*. https://aws.amazon.com/ec2/graviton/graviton-sustainability/",
 "Applied Radiology. (2018). *ScreenPoint Medical receives FDA clearance for screening mammography AI software*. https://www.appliedradiology.com/news/screenpoint-medical-receives-fda-clearance-for-screening-mammography-ai-software",
 "Dembrower, K., Wåhlin, E., Liu, Y., Salim, M., Smith, K., Lindholm, P., Eklund, M., & Strand, F. (2020). Effect of artificial intelligence-based triaging of breast cancer screening mammograms on cancer detection and radiologist workload: A retrospective simulation study. *The Lancet Digital Health, 2*(9), e468–e474. https://doi.org/10.1016/S2589-7500(20)30185-0",
 "Freeman, K., Geppert, J., Stinton, C., Todkill, D., Johnson, S., Clarke, A., & Taylor-Phillips, S. (2021). Use of artificial intelligence for image analysis in breast cancer screening programmes: Systematic review of test accuracy. *BMJ, 374*, n1872. https://doi.org/10.1136/bmj.n1872",
 "iCAD. (2023). *ProFound AI* [Ficha de producto DMM252 Rev. 1]. https://www.icadmed.com/wp-content/uploads/2023/11/DMM252_ProFound_AI_Rev_1.pdf",
 "Lunit. (2021, 18 de noviembre). *Lunit's AI software for breast cancer detection, Lunit INSIGHT MMG, wins FDA clearance* [Comunicado de prensa]. https://www.lunit.io/en/news/lunits-ai-software-for-breast-cancer-detection-lunit-insight-mmg-wins-fda-clearance",
]
def key(s):
    import unicodedata
    return unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()
for ref in NUEVAS:
    plain = ref.replace("*", "")
    refs = [m for m in PARA.finditer(x) if 'w:val="BibliografayReferencias"' in m.group(0)[:300]]
    nxt = next((m for m in refs if key(text_of(m.group(0))) > key(escape(plain))), None)
    if nxt is None:
        insert_after(refs[-1], ref_par(ref))
    else:
        insert_before(nxt, ref_par(ref))

# ---------------------------------------------------------------- glosario
gl = [m for m in PARA.finditer(x) if 'w:val="Glorario"' in m.group(0)[:300]]
nuevo = ("CADe/CADx", "Detección o diagnóstico asistido por computador: software que analiza imágenes médicas para marcar hallazgos o estimar su probabilidad de malignidad.")
nxt = next(m for m in gl if key(text_of(m.group(0))) > key(nuevo[0]))
insert_before(nxt, styled("Glorario", [L.run(nuevo[0] + ": ", "<w:rPr><w:b/></w:rPr>"), L.run(nuevo[1])]))

# sombreado sin atributo obligatorio w:val (error de esquema heredado de la iteración 10)
x = x.replace('<w:shd w:fill="D9EAF7"/>', '<w:shd w:val="clear" w:color="auto" w:fill="D9EAF7"/>')
x, nums = L.renumerar(x)
open(p, "w", encoding="utf-8").write(x)
print("ok", len(nums), "encabezados vacíos retirados:", n_empty)
