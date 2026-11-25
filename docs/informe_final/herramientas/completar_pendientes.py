# -*- coding: utf-8 -*-
"""Aplica al maestro los insumos del equipo escritos en trabajo/pendientes_equipo.json.

Uso: python3 completar_pendientes.py <dir_desempaquetado_maestro> <pendientes_equipo.json>
Lo normal es no llamarlo directo, sino con completar_pendientes.sh (desempaqueta, aplica, valida y exporta el PDF).

- Solo aplica los campos con contenido. Si un cambio ya estaba aplicado, lo informa y sigue (se puede volver a
  ejecutar con el JSON más completo).
- Los textos que agrega están escritos para cada resultado posible (por ejemplo, PC-01 aprobada o no aprobada).
- Imprime un resumen de lo aplicado, lo omitido y lo que falta.
"""
import json, os, re, sys
from xml.sax.saxutils import escape
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import maestro_lib as L

root, cfg_path = sys.argv[1], sys.argv[2]
p = os.path.join(root, "word", "document.xml")
x = open(p, encoding="utf-8").read(); L.init_ids(x)
cfg = json.load(open(cfg_path, encoding="utf-8"))
PARA = re.compile(r"<w:p\b(?:(?!<w:p\b).)*?</w:p>", re.S)
text_of = lambda px: "".join(re.findall(r"<w:t[^>]*>([^<]*)</w:t>", px))
log = {"aplicado": [], "ya_estaba": [], "falta": []}


def ok(msg): log["aplicado"].append(msg)
def done(msg): log["ya_estaba"].append(msg)
def missing(msg): log["falta"].append(msg)


def has(t): return escape(t) in x


def swap(old, new, what):
    """Reemplaza `old` por `new` una vez; si `old` ya no está pero `new` sí, lo da por aplicado."""
    global x
    o, n = escape(old), escape(new)
    if x.count(o) == 1:
        x = x.replace(o, n); ok(what); return True
    if n in x:
        done(what); return False
    raise SystemExit("No se encontró el texto para «%s»: %s…" % (what, old[:90]))


def fmt_int(v):
    s = str(v).strip().replace(".", "").replace(",", "")
    return "{:,}".format(int(s)).replace(",", ".") if s.isdigit() else str(v)


def fmt_num(v, dec=1):
    """Número con coma decimal y punto de miles, como el resto del informe."""
    f = float(str(v).replace(".", "").replace(",", ".")) if isinstance(v, str) and "," in v else float(v)
    s = ("{:,.%df}" % dec).format(f)
    return s.replace(",", "§").replace(".", ",").replace("§", ".")


def num(v):
    return float(str(v).replace(".", "").replace(",", ".")) if isinstance(v, str) and "," in str(v) else float(v)


# ---------------------------------------------------------------- 1. Dedicatoria y agradecimientos
for heading, key in [("Dedicatoria", "dedicatoria"), ("Agradecimientos", "agradecimientos")]:
    texto = (cfg.get(key) or "").strip()
    ms = list(PARA.finditer(x))
    h = [i for i, m in enumerate(ms) if text_of(m.group(0)) == heading and 'w:val="Ttulo1"' in m.group(0)]
    assert len(h) == 1, heading
    slot = ms[h[0] + 1]
    assert 'DedicatoriayAgradecimientos' in slot.group(0), heading
    if text_of(slot.group(0)).strip():
        done(heading); continue
    if not texto:
        missing(heading + " (página en blanco)"); continue
    tpl = slot.group(0)
    paras = [t.strip() for t in re.split(r"\n\s*\n", texto) if t.strip()]
    xml = "".join(tpl.replace("</w:pPr></w:p>", "</w:pPr>%s</w:p>" % L.run(t.replace("\n", " ")), 1) for t in paras)
    x = x[:slot.start()] + xml + x[slot.end():]
    ok("%s (%d párrafo%s)" % (heading, len(paras), "" if len(paras) == 1 else "s"))

# ---------------------------------------------------------------- 2. Referencias
for start, new in (cfg.get("referencias") or {}).items():
    if start.startswith("_"):
        continue
    new = (new or "").strip()
    ms = [m for m in PARA.finditer(x) if "BibliografayReferencias" in m.group(0)[:300] and text_of(m.group(0)).startswith(escape(start))]
    if not new:
        missing("Referencia «%s»" % start); continue
    if not ms:
        if has(new): done("Referencia «%s»" % start); continue
        raise SystemExit("No se encontró la referencia que comienza con «%s»" % start)
    assert len(ms) == 1, start
    m = ms[0]
    if text_of(m.group(0)) == escape(new):
        done("Referencia «%s»" % start); continue
    ppr = re.search(r"<w:pPr>.*?</w:pPr>", m.group(0), re.S).group(0)
    x = x[:m.start()] + "<w:p>%s%s</w:p>" % (ppr, L.run(new)) + x[m.end():]
    ok("Referencia «%s»" % start)
nueva_cita = ((cfg.get("cita_shah_en_el_texto") or {}).get("nueva") or "").strip()
if nueva_cita:
    n = x.count(escape("Shah et al., 2023"))
    if n:
        x = x.replace(escape("Shah et al., 2023"), escape(nueva_cita)); ok("Cita de Shah et al. en el texto (%d)" % n)
    else:
        done("Cita de Shah et al. en el texto")

# ---------------------------------------------------------------- 2b. Marcas «[FALTA INFORMACIÓN…]» del capítulo II
import unicodedata
fold = lambda t: unicodedata.normalize("NFKD", t).encode("ascii", "ignore").decode().lower()
MARCAS = {
    "globocan": " [FALTA INFORMACIÓN: incorporar referencia bibliográfica completa de la edición GLOBOCAN utilizada y verificar año estadístico de las cifras.]",
    "ges": " [FALTA INFORMACIÓN: incorporar referencia normativa oficial y verificar vigencia de los plazos citados.]",
}
for key, marca in MARCAS.items():
    item = (cfg.get("marcas_capitulo_II") or {}).get(key) or {}
    cita, ref = (item.get("cita") or "").strip().strip("()"), (item.get("referencia") or "").strip()
    frase = item["afirmacion"]; nueva = (item.get("frase_corregida") or "").strip() or frase
    if escape(marca.strip()) not in x:
        done("Marca del capítulo II: %s" % key); continue
    if not (cita and ref):
        missing("Marca del capítulo II: %s (cita y referencia)" % key); continue
    assert x.count(escape(frase)) == 1, frase[:60]
    x = x.replace(escape(frase), escape(nueva[:-1] + " (%s)." % cita if nueva.endswith(".") else nueva + " (%s)" % cita))
    assert x.count(escape(marca)) == 1, key
    x = x.replace(escape(marca), "")
    refs = [m for m in PARA.finditer(x) if "BibliografayReferencias" in m.group(0)[:300]]
    nxt = next((m for m in refs if fold(text_of(m.group(0))) > fold(ref)), None)
    ppr = re.search(r"<w:pPr>.*?</w:pPr>", refs[0].group(0), re.S).group(0)
    xml = "<w:p>%s%s</w:p>" % (ppr, L.run(ref))
    pos = nxt.start() if nxt else refs[-1].end()
    x = x[:pos] + xml + x[pos:]
    ok("Marca del capítulo II: %s (cita «%s» y referencia)" % (key, cita))

# ---------------------------------------------------------------- 3. Despliegue de la 2.12.0
dep = ((cfg.get("despliegue_2_12_0") or {}).get("fecha") or "").strip()
if dep:
    swap("La versión publicada en el entorno de demostración es la 2.11.0, desplegada el 25-11-2026, que agrega el rol de jefatura y finanzas, el comparador de médicos, la especialidad del médico y la activación de cuentas por correo; la precedieron la 2.10.1 y la 2.10.2 (24-11-2026), que corrigen los dos bloqueos bajo carga descritos en el capítulo XII. La versión 2.12.0, con la optimización de consultas y el servicio de inferencia de respaldo, está terminada y probada; su despliegue queda pendiente.",
         "La versión publicada en el entorno de demostración es la 2.12.0, desplegada el %s, que optimiza las consultas de las listas y del dashboard y agrega el servicio de inferencia de respaldo. La precedieron la 2.11.0 (25-11-2026), con el rol de jefatura y finanzas, el comparador de médicos, la especialidad del médico y la activación de cuentas por correo, y la 2.10.1 y la 2.10.2 (24-11-2026), que corrigen los dos bloqueos bajo carga descritos en el capítulo XII." % dep,
         "XIII: versión publicada 2.12.0")
    swap("prototipo desplegado (versión 2.11.0);", "prototipo desplegado (versión 2.12.0);", "XIV: versión desplegada en la factibilidad técnica")
else:
    missing("Fecha de despliegue de la 2.12.0")

# ---------------------------------------------------------------- 4. PC-01 en el entorno de demostración con la 2.12.0
pc = cfg.get("pc01_aws_2_12_0") or {}
filas = [f for f in (pc.get("filas") or []) if str(f.get("p95_ms", "")).strip()]
f100 = [f for f in filas if int(f["usuarios"]) == 100]
if pc.get("fecha") and f100:
    if not dep:
        raise SystemExit("Para registrar PC-01 con la 2.12.0 en el entorno de demostración, complete antes la fecha de despliegue de la 2.12.0.")
    fecha = pc["fecha"].strip(); carpeta = (pc.get("carpeta_evidencia") or "evidencias/rendimiento_aws_%s" % fecha).strip().rstrip("/")
    r = f100[0]; p95 = num(r["p95_ms"]); err = int(num(r["errores"]))
    cumple = p95 <= 3000
    p95_ms, p95_s = fmt_num(p95, 0), fmt_num(p95 / 1000, 2)
    hasta = [int(f["usuarios"]) for f in filas if num(f["p95_ms"]) <= 3000]
    if not has("Prueba de rendimiento en el entorno de demostración con la versión 2.12.0"):
        rows = [["Usuarios virtuales", "Duración", "Solicitudes", "Errores", "Solicitudes/s", "p50 (ms)", "p95 (ms)", "Máx. (ms)"]]
        for f in sorted(filas, key=lambda f: int(f["usuarios"])):
            tab = lambda v: ("%.1f" % num(v)).replace(".", ",")
            rows.append([str(f["usuarios"]), f.get("duracion", ""), fmt_int(f["solicitudes"]), str(int(num(f["errores"]))),
                         tab(f["solicitudes_s"]), tab(f["p50_ms"]), tab(f["p95_ms"]), tab(f["max_ms"])])
        if cumple:
            cierre = ("Con 100 usuarios virtuales el percentil 95 fue de %s ms, dentro de la meta de 3 s, con %d errores. "
                      "En consecuencia, PC-01 se aprueba en el entorno de demostración con la versión 2.12.0. Como en las mediciones anteriores, "
                      "los usuarios virtuales no esperan entre acciones y no se incluyeron la carga de imágenes ni la inferencia." % (p95_ms, err))
        else:
            cierre = ("Con 100 usuarios virtuales el percentil 95 fue de %s ms, sobre la meta de 3 s, con %d errores; la meta se cumple hasta %s usuarios virtuales. "
                      "En consecuencia, PC-01 sigue sin aprobarse en el entorno de demostración: la optimización redujo los tiempos, pero la meta "
                      "exige además más capacidad (procesos de la API o una instancia mayor)." % (p95_ms, err, max(hasta) if hasta else "menos de %d" % min(int(f["usuarios"]) for f in filas)))
        blocks = [
            ("p", "La versión 2.12.0 se desplegó en el entorno de demostración el %s, y el %s se repitió allí PC-01 con el mismo método: copia de la base en un esquema temporal, generador de carga en el propio servidor y el mismo recorrido de consultas. La {T:carga_aws_2120} resume los resultados." % (dep, fecha)),
            ("tabla", "Prueba de rendimiento en el entorno de demostración con la versión 2.12.0", "carga_aws_2120",
             "Fuente: Elaboración propia a partir de la ejecución del %s con la versión 2.12.0 (%s/ de la carpeta del informe)." % (fecha, carpeta),
             [1300, 1000, 1150, 900, 1150, 1000, 1000, 1044], rows),
            ("p", cierre)]
        anchor = escape("y la versión 2.12.0 aún no se despliega ni se mide allí.")
        if anchor in x:
            x = x.replace(anchor, escape("y la versión 2.12.0 se midió allí después de su despliegue."))
        ms = [m for m in PARA.finditer(x) if escape("y la versión 2.12.0 se midió allí después de su despliegue.") in m.group(0)]
        assert len(ms) == 1
        x = x[:ms[0].end()] + L.render(root, blocks, os.path.dirname(HERE)) + x[ms[0].end():]
        ok("XII: PC-01 con la 2.12.0 en el entorno de demostración (%s)" % ("aprobada" if cumple else "no aprobada"))
    else:
        done("XII: PC-01 con la 2.12.0 en el entorno de demostración")
    estado = "aprobado" if cumple else "no aprobado"
    swap("Versión 2.12.0 en local (25-11-2026): p95 2.532 ms con 100 usuarios; falta repetirla en el entorno de demostración",
         "Versión 2.12.0 en local (25-11-2026): p95 2.532 ms con 100 usuarios; en el entorno de demostración (%s): p95 %s ms y %d errores (%s)" % (fecha, p95_ms, err, estado),
         "XII: Tabla de casos de prueba, fila PC-01")
    swap("La versión 2.12.0 obtuvo en local (25-11-2026) un p95 de 2.532 ms con 100 usuarios, por repetir en el entorno de demostración; PC-02 no ejecutada",
         "La versión 2.12.0 obtuvo un p95 de 2.532 ms con 100 usuarios en local (25-11-2026) y de %s ms en el entorno de demostración (%s): %s; PC-02 no ejecutada" % (p95_ms, fecha, "cumple" if cumple else "no cumple"),
         "XII: Tabla de resultados, fila de carga y estrés")
    if cumple:
        swap("Una optimización posterior de las consultas cuadruplicó la capacidad en una medición local y queda por confirmar en ese entorno.",
             "Tras una optimización posterior de las consultas, el entorno de demostración cumplió la meta con 100 usuarios (percentil 95 de %s s)." % p95_s, "Resumen")
        swap("A later query optimization quadrupled capacity in a local measurement and remains to be confirmed in that environment.",
             "After a later query optimization, the demonstration environment met the target with 100 users (95th percentile of %s s)." % p95_s.replace(",", "."), "Abstract")
        swap("con p95 de 2,5 s con 100 usuarios en local, por confirmar en el entorno de demostración;",
             "con p95 de 2,5 s con 100 usuarios en local y de %s s en el entorno de demostración, donde PC-01 se aprueba;" % p95_s, "XIV: factibilidad técnica")
        swap("• Desplegar la versión 2.12.0, cuya optimización de consultas cuadruplicó la capacidad de un proceso en una medición local, y repetir PC-01 en el entorno de demostración; si la meta no se cumple, dimensionar la capacidad (procesos de la API y tamaño de la instancia). Ejecutar además la prueba de estrés",
             "• Ejecutar la prueba de estrés", "XVI: recomendación de rendimiento")
    else:
        swap("Una optimización posterior de las consultas cuadruplicó la capacidad en una medición local y queda por confirmar en ese entorno.",
             "Una optimización posterior de las consultas redujo ese percentil a %s s, aún sobre la meta." % p95_s, "Resumen")
        swap("A later query optimization quadrupled capacity in a local measurement and remains to be confirmed in that environment.",
             "A later query optimization reduced that percentile to %s s, still above the target." % p95_s.replace(",", "."), "Abstract")
        swap("con p95 de 2,5 s con 100 usuarios en local, por confirmar en el entorno de demostración;",
             "con p95 de 2,5 s con 100 usuarios en local y de %s s en el entorno de demostración, aún sobre la meta;" % p95_s, "XIV: factibilidad técnica")
        swap("• Desplegar la versión 2.12.0, cuya optimización de consultas cuadruplicó la capacidad de un proceso en una medición local, y repetir PC-01 en el entorno de demostración; si la meta no se cumple, dimensionar la capacidad (procesos de la API y tamaño de la instancia).",
             "• Dimensionar la capacidad para la meta de rendimiento (procesos de la API y tamaño de la instancia): con la versión 2.12.0, el entorno de demostración obtuvo un percentil 95 de %s s con 100 usuarios. Repetir luego PC-01." % p95_s,
             "XVI: recomendación de rendimiento")
elif pc.get("fecha") or filas:
    missing("PC-01 con la 2.12.0: falta la fecha o la fila de 100 usuarios")
else:
    missing("PC-01 con la 2.12.0 en el entorno de demostración")

# ---------------------------------------------------------------- 5. Instancia de respaldo del modelo
ri = cfg.get("respaldo_inferencia") or {}
fc = (ri.get("fecha_creacion") or "").strip()
if fc:
    probado = bool(ri.get("probado_paso_al_respaldo"))
    swap("Servicio de inferencia de respaldo (planificado)", "Servicio de inferencia de respaldo", "X: fila de la instancia de respaldo")
    swap("Respaldo del análisis automatizado si el equipo con GPU no responde (versión 2.12.0); no creada al 25-11-2026",
         "Respaldo del análisis automatizado si el equipo con GPU no responde (versión 2.12.0); creada el %s%s" % (fc, ", con el paso al respaldo probado" if probado else ""),
         "X: estado de la instancia de respaldo")
    swap("servicio de respaldo configurable (2.12.0) implementados y probados; instancia de respaldo en AWS por crear",
         "servicio de respaldo en AWS (2.12.0) implementados y probados; instancia de respaldo creada el %s%s" % (fc, " y paso al respaldo verificado" if probado else ""),
         "XIII: análisis de impacto, servicio de inferencia")
    swap("servicio de respaldo en AWS configurable (2.12.0), con la instancia por crear",
         "servicio de respaldo en AWS (2.12.0), creado el %s" % fc, "XV: riesgo de dependencia del equipo personal")
    swap("• Crear la instancia de respaldo del servicio de inferencia en AWS prevista en la versión 2.12.0 y, a mediano plazo, trasladar el servicio desde el equipo personal",
         "• A mediano plazo, trasladar el servicio de inferencia desde el equipo personal", "XVI: recomendación del servicio de inferencia")
else:
    missing("Instancia de respaldo del modelo en AWS")

n_marcas = x.count(escape("[FALTA INFORMACIÓN"))
if n_marcas:
    missing("Quedan %d marca(s) «[FALTA INFORMACIÓN…]» en el documento" % n_marcas)
x, nums = L.renumerar(x)
open(p, "w", encoding="utf-8").write(x)
print("\n== Aplicado (%d)" % len(log["aplicado"])); [print("  +", m) for m in log["aplicado"]]
print("== Ya estaba (%d)" % len(log["ya_estaba"])); [print("  =", m) for m in log["ya_estaba"]]
print("== Falta (%d)" % len(log["falta"])); [print("  -", m) for m in log["falta"]]
print("\nQuedan fuera de este script (ver trabajo/PENDIENTES_EQUIPO.md): correcciones del docente, A3 (modelo de IA desde U2) y la lectura final.")
