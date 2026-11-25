# -*- coding: utf-8 -*-
"""Iteración 16: consistencia tras las iteraciones 12 a 15 (maestro 1.5-rc -> 1.6-rc).
(1) afirmaciones desactualizadas; (4) citas de referencias no citadas; (5) glosario; (6) encabezado vacío.
Uso: python3 iter16_consistencia.py <dir_desempaquetado_maestro>"""
import sys, os, re, unicodedata
from xml.sax.saxutils import escape
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import maestro_lib as L

root = sys.argv[1]
p = os.path.join(root, "word", "document.xml")
x = open(p, encoding="utf-8").read(); L.init_ids(x)
PARA = re.compile(r"<w:p\b(?:(?!<w:p\b).)*?</w:p>", re.S)
text_of = lambda px: "".join(re.findall(r"<w:t[^>]*>([^<]*)</w:t>", px))

def rep(old, new, n=1):
    global x
    o, nn = escape(old), escape(new); assert x.count(o) == n, (old[:70], x.count(o)); x = x.replace(o, nn)

def set_cell(px_match, new):
    global x
    px = px_match.group(0); assert px.count("<w:t") == 1, text_of(px)
    x = x[:px_match.start()] + re.sub(r"(<w:t[^>]*>)[^<]*(</w:t>)", lambda m: m.group(1) + escape(new) + m.group(2), px) + x[px_match.end():]

def cell_after(anchor, old, new, within=6):
    """Cambia el primer párrafo de texto exacto `old` dentro de los `within` párrafos que siguen a `anchor` (texto exacto)."""
    ms = list(PARA.finditer(x))
    idx = [i for i, m in enumerate(ms) if text_of(m.group(0)) == escape(anchor)]
    assert len(idx) == 1, (anchor, len(idx))
    for m in ms[idx[0] + 1: idx[0] + 1 + within]:
        if text_of(m.group(0)) == escape(old):
            return set_cell(m, new)
    raise AssertionError((anchor, old))

# ---------------------------------------------------------------- (1) afirmaciones desactualizadas
rep("se consolidará en la matriz de trazabilidad pendiente del capítulo III.",
    "se consolida en la matriz de trazabilidad del capítulo XII.")
rep("Cliente del proveedor verificado en código; funcionamiento del servicio y del modelo pendiente de inspección (capítulo X). Sin validación clínica.",
    "Cliente del proveedor y servicio de inferencia verificados en el código (capítulo X). Sin validación clínica.")
rep("su última corrida en la rama principal (16-11-2026) fue exitosa.",
    "sus corridas en la rama principal fueron exitosas hasta el 24-11-2026 (versión 2.10.2, con 321 pruebas tras las correcciones del capítulo XII).")
cell_after("PS-01, PS-02, PS-04, PS-07", "Parcial: PS-04 no ejecutado",
           "Cubierto: PS-04 ejecutado el 24-11-2026 (escaneo pasivo, sin riesgos altos); escaneo activo no ejecutado")
cell_after("Prueba con 100 usuarios concurrentes", "No ejecutada",
           "Ejecutada el 24-11-2026: con 100 usuarios, p95 de 14,98 s y 0 errores; la meta se cumple hasta 25 usuarios")
rep("Para un piloto se requieren, como mínimo, un monitor externo de disponibilidad, alarmas de errores y latencia, y la ejecución de la prueba de carga en ese entorno.",
    "Para un piloto se requieren, como mínimo, un monitor de disponibilidad externo a AWS y alarmas de errores y de latencia, que complementen el chequeo y las alarmas de disponibilidad instalados el 24-11-2026, y una capacidad que cumpla la meta de rendimiento medida en el capítulo XII.")
rep("(la prueba de carga se ejecutó después, el 24-11-2026, en entorno local)",
    "(la prueba de carga se ejecutó después, el 24-11-2026, en entorno local y en el entorno de demostración)")
rep("Despliegue en AWS (11-11), contenedores e integración continua realizados; escaneo de seguridad no ejecutado; desfase de 11 días",
    "Despliegue en AWS (11-11), contenedores e integración continua realizados; escaneo de seguridad ejecutado después, el 24-11-2026; desfase de 11 días")
rep("Antes de la entrega se recomienda ejecutar la prueba de restauración de un respaldo y el escaneo de seguridad, que no afectan el plazo.",
    "La prueba de restauración de un respaldo y el escaneo de seguridad, recomendados antes de la entrega, se ejecutaron el 24-11-2026 sin afectar el plazo.")
rep("Sprint 8 (2.6.0–2.10.0)", "Sprint 8 (2.6.0–2.10.0; correcciones 2.10.1 y 2.10.2 el 24-11)", n=x.count(escape("Sprint 8 (2.6.0–2.10.0)")))

# Tabla de componentes de infraestructura: fila de monitoreo y fuente al día
i = x.find(escape("Grupo de registros de los contenedores, retención de 30 días")); assert i > 0
s = x.rfind("<w:tr>", 0, i); s2 = x.rfind("<w:tr ", 0, i); s = max(s, s2); e = x.find("</w:tr>", i) + 7
row = x[s:e]
for old, new in [("CloudWatch Logs", "Monitoreo"),
                 ("Grupo de registros de los contenedores, retención de 30 días", "Chequeo de /health cada minuto (CloudWatch Logs /aurora/monitor), alarmas de CloudWatch y aviso por correo (Amazon SNS)"),
                 ("Registro centralizado", "Detección de caídas y medición de disponibilidad")]:
    assert row.count(escape(old)) == 1, old; row = row.replace(">%s<" % escape(old), ">%s<" % escape(new))
x = x[:e] + row + x[e:]
rep("Fuente: Elaboración propia a partir de docs/ESTADO_AWS.md (16-11-2026).", "Fuente: Elaboración propia a partir de docs/ESTADO_AWS.md (24-11-2026).")

# ---------------------------------------------------------------- (4) citas
rep("tiene asignada la región us-east-2 (Ohio), con datos ficticios;", "tiene asignada la región us-east-2 (Ohio; Amazon Web Services, s. f.-b), con datos ficticios;")
for old, new in [("ITIL 4", "ITIL 4 (AXELOS, 2019)"), ("APA 7.ª edición", "APA 7.ª edición (American Psychological Association, 2020)")]:
    ms = [m for m in PARA.finditer(x) if text_of(m.group(0)) == escape(old)]; assert len(ms) == 1, old
    set_cell(ms[0], new)

# ---------------------------------------------------------------- (5) glosario
GLOS = [
 ("AWS", "Amazon Web Services: proveedor de servicios en la nube en el que se despliega el entorno de demostración."),
 ("BPMN", "Modelo y notación de procesos de negocio: notación estándar para representar procesos con actividades, eventos, decisiones y carriles por actor (ISO/IEC 19510)."),
 ("CBIS-DDSM y CMMD", "Conjuntos públicos de mamografías con diagnóstico confirmado por patología, de Estados Unidos y China, usados para entrenar el modelo de análisis."),
 ("CDN", "Red de distribución de contenidos: servidores distribuidos que entregan contenido estático cerca del usuario."),
 ("CLAHE", "Ecualización adaptativa del histograma con contraste limitado: técnica que realza el contraste local de una imagen sin amplificar en exceso el ruido."),
 ("CSP", "Política de seguridad de contenido: encabezado HTTP que restringe los orígenes desde los que el navegador puede cargar scripts, estilos y otros recursos."),
 ("DNS", "Sistema de nombres de dominio: traduce nombres como demo.auroracare.cl a direcciones IP."),
 ("EC2", "Amazon Elastic Compute Cloud: servicio de servidores virtuales de AWS."),
 ("FDA", "Administración de Alimentos y Medicamentos de Estados Unidos: autoridad que autoriza dispositivos médicos, incluido el software de análisis de imágenes."),
 ("GPU", "Unidad de procesamiento gráfico: procesador que acelera el entrenamiento y la ejecución de redes neuronales."),
 ("HTTPS y TLS", "Protocolo HTTP sobre TLS (seguridad de la capa de transporte), que cifra la comunicación entre el navegador y el servidor."),
 ("IAM", "Gestión de identidades y accesos de AWS: define qué identidades pueden realizar qué acciones sobre qué recursos."),
 ("ISO/IEC", "Organización Internacional de Normalización y Comisión Electrotécnica Internacional, que publican normas técnicas conjuntas."),
 ("JSONB", "Tipo de dato de PostgreSQL que almacena documentos JSON en formato binario y permite consultarlos."),
 ("OMS", "Organización Mundial de la Salud."),
 ("OWASP", "Open Worldwide Application Security Project: comunidad que publica guías y herramientas de seguridad de aplicaciones web, como el Top 10 y ZAP."),
 ("p95", "Percentil 95: valor bajo el cual queda el 95% de las mediciones; en este informe, del tiempo de respuesta de la API."),
 ("PK y FK", "Clave primaria y clave foránea: columnas que identifican una fila y que la relacionan con otra tabla."),
 ("QA", "Aseguramiento de la calidad: actividades de prueba y revisión que verifican que el producto cumple sus requisitos."),
 ("RACI", "Matriz que asigna, por actividad, quién la ejecuta (Responsable), quién responde por ella (Aprobador), a quién se consulta y a quién se informa."),
 ("RDS", "Amazon Relational Database Service: servicio administrado de bases de datos relacionales de AWS."),
 ("Route 53", "Servicio de DNS de AWS."),
 ("S3", "Amazon Simple Storage Service: servicio de almacenamiento de objetos de AWS."),
 ("SNS", "Amazon Simple Notification Service: servicio de AWS que envía notificaciones; en este proyecto, avisos de alarma por correo."),
 ("SSE-KMS", "Cifrado en el servidor de Amazon S3 con claves administradas por AWS Key Management Service."),
 ("Tailscale", "Servicio de red privada que conecta, de forma cifrada, el servidor del entorno de demostración con el equipo que ejecuta el servicio de inferencia."),
 ("UML", "Lenguaje unificado de modelado: notación estándar para diagramas de software, como los de casos de uso y de componentes."),
 ("VAN, TIR y PRI", "Valor actual neto, tasa interna de retorno y período de recuperación de la inversión: indicadores de rentabilidad de la evaluación económica."),
 ("ZAP", "Zed Attack Proxy: herramienta de OWASP para analizar la seguridad de aplicaciones web."),
]
def key(s):
    return unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()
existing = [text_of(m.group(0)).split(":")[0] for m in PARA.finditer(x) if 'w:val="Glorario"' in m.group(0)[:300]]
for term, defin in GLOS:
    assert term not in existing, term
    gl = [m for m in PARA.finditer(x) if 'w:val="Glorario"' in m.group(0)[:300]]
    xml = '<w:p><w:pPr><w:pStyle w:val="Glorario"/></w:pPr>%s%s</w:p>' % (L.run(term + ": ", "<w:rPr><w:b/></w:rPr>"), L.run(defin))
    nxt = next((m for m in gl if key(text_of(m.group(0))) > key(term)), None)
    pos = nxt.start() if nxt else gl[-1].end()
    x = x[:pos] + xml + x[pos:]

# ---------------------------------------------------------------- (6) encabezado de nivel 1 vacío antes del índice de tablas
ms = list(PARA.finditer(x))
h = [k for k, m in enumerate(ms) if text_of(m.group(0)) == escape("Índice de Tablas") and 'w:val="Ttulo1"' in m.group(0)]
assert len(h) == 1, len(h)
empties = [m for m in ms[h[0] - 3:h[0]] if 'w:val="Ttulo1"' in m.group(0) and not text_of(m.group(0)).strip()]
assert len(empties) == 1, len(empties)
m = empties[0]
x = x[:m.start()] + m.group(0).replace('<w:pStyle w:val="Ttulo1"/>', "") + x[m.end():]

x, nums = L.renumerar(x)
open(p, "w", encoding="utf-8").write(x)
print("ok; glosario +%d" % len(GLOS))
