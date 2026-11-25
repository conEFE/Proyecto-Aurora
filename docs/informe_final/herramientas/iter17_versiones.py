# -*- coding: utf-8 -*-
"""Iteración 17: versiones 2.11.0 (desplegada) y 2.12.0 (terminada, sin desplegar) y punto A2 (maestro 1.6-rc -> 1.7-rc).
- Rol de jefatura y finanzas, comparador de médicos, ficha del médico y activación por correo (CU19, CU20, email_tokens).
- Ejecución formal de pruebas del 25-11-2026: 340 pruebas (evidencias/pruebas_2026-11-25).
- Optimización de consultas y servicio de inferencia de respaldo (2.12.0; evidencias/rendimiento_2026-11-25).
- Modelo lógico y diagrama de casos de uso regenerados (diagramas_cap10.py); diccionario de datos desde schema_modelos.json.
- Dos capturas de la 2.11.0 en el anexo.
Uso: python3 iter17_versiones.py <dir_desempaquetado_maestro>"""
import json, os, re, sys
from xml.sax.saxutils import escape
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import maestro_lib as L

BASE = os.path.dirname(HERE)  # docs/informe_final
root = sys.argv[1]
p = os.path.join(root, "word", "document.xml")
x = open(p, encoding="utf-8").read(); L.init_ids(x)
PARA = re.compile(r"<w:p\b(?:(?!<w:p\b).)*?</w:p>", re.S)
text_of = lambda px: "".join(re.findall(r"<w:t[^>]*>([^<]*)</w:t>", px))


def rep(old, new, n=1):
    global x
    o, nn = escape(old), escape(new)
    assert x.count(o) == n, (old[:80], x.count(o))
    x = x.replace(o, nn)


def find_para(text, style=None, start=0):
    ms = [m for m in PARA.finditer(x, start) if text_of(m.group(0)) == escape(text)
          and (style is None or 'w:val="%s"' % style in m.group(0)[:400])]
    assert len(ms) >= 1, (text[:80], style)
    return ms[0]


def find_para_unique(text, style=None):
    ms = [m for m in PARA.finditer(x) if text_of(m.group(0)) == escape(text)
          and (style is None or 'w:val="%s"' % style in m.group(0)[:400])]
    assert len(ms) == 1, (text[:80], len(ms))
    return ms[0]


def insert_after(m, xml):
    global x
    x = x[:m.end()] + xml + x[m.end():]


def insert_before(m, xml):
    global x
    x = x[:m.start()] + xml + x[m.start():]


def region(caption_text):
    """(inicio, fin) desde la leyenda de una tabla o figura hasta su párrafo de fuente."""
    ms = [m for m in PARA.finditer(x) if escape(caption_text) in text_of(m.group(0)) and "FiguraoTablaTtulo" in m.group(0)[:400]]
    assert len(ms) == 1, (caption_text, len(ms))
    s = ms[0].start()
    e = x.find("FiguraoTablaFuente", s); e = x.find("</w:p>", e) + 6
    return s, e


def row_span(first_cell, caption_text, nth=0):
    """Fila (<w:tr>) de la tabla `caption_text` cuya primera celda dice `first_cell`."""
    s, e = region(caption_text)
    for tr in re.finditer(r"<w:tr\b.*?</w:tr>", x[s:e], re.S):
        cells = re.findall(r"<w:tc\b.*?</w:tc>", tr.group(0), re.S)
        if cells and text_of(cells[0]) == escape(first_cell):
            if nth == 0:
                return s + tr.start(), s + tr.end()
            nth -= 1
    raise AssertionError((caption_text, first_cell))


def _fill_cell(tc, value):
    ts = list(re.finditer(r"(<w:t(?: [^>]*)?>)[^<]*(</w:t>)", tc))
    assert ts, tc[:200]
    out, pos = [], 0
    for i, t in enumerate(ts):
        out.append(tc[pos:t.start()])
        out.append('<w:t xml:space="preserve">%s</w:t>' % (escape(value) if i == 0 else ""))
        pos = t.end()
    out.append(tc[pos:])
    return "".join(out)


def clone_row(span, values):
    tr = x[span[0]:span[1]]
    cells = re.findall(r"<w:tc\b.*?</w:tc>", tr, re.S)
    assert len(cells) == len(values), (len(cells), values)
    new = tr
    for tc, v in zip(cells, values):
        new = new.replace(tc, _fill_cell(tc, v), 1)
    return new


def add_rows_after(first_cell, caption_text, rows):
    global x
    s, e = row_span(first_cell, caption_text)
    xml = "".join(clone_row((s, e), r) for r in rows)
    x = x[:e] + xml + x[e:]


def set_row_cell(first_cell, caption_text, idx, value, nth=0):
    global x
    s, e = row_span(first_cell, caption_text, nth)
    tr = x[s:e]
    cells = re.findall(r"<w:tc\b.*?</w:tc>", tr, re.S)
    tr2 = tr.replace(cells[idx], _fill_cell(cells[idx], value), 1)
    x = x[:s] + tr2 + x[e:]


def row_cell_text(first_cell, caption_text, idx):
    s, e = row_span(first_cell, caption_text)
    cells = re.findall(r"<w:tc\b.*?</w:tc>", x[s:e], re.S)
    return text_of(cells[idx])


def append_to_cell(first_cell, caption_text, idx, suffix):
    old = row_cell_text(first_cell, caption_text, idx).replace("&amp;", "&")
    set_row_cell(first_cell, caption_text, idx, old + suffix)


def replace_image(name, png):
    """Reemplaza la imagen `name` de word/media y ajusta el alto del dibujo a la nueva proporción."""
    global x
    from PIL import Image
    import shutil
    shutil.copy(png, os.path.join(root, "word", "media", name))
    w, h = Image.open(png).size
    i = x.find('name="%s"' % name); assert i > 0, name
    s = x.rfind("<w:drawing>", 0, i); e = x.find("</w:drawing>", i)
    d = x[s:e]
    cx, cy = map(int, re.search(r'<wp:extent cx="(\d+)" cy="(\d+)"/>', d).groups())
    ncy = int(cx * h / w); ncx = cx
    if ncy > cy * 1.15:  # no crecer más que el espacio que ya ocupaba: se reduce el ancho
        ncy = int(cy * 1.15); ncx = int(ncy * w / h)
    d2 = d.replace('<wp:extent cx="%d" cy="%d"/>' % (cx, cy), '<wp:extent cx="%d" cy="%d"/>' % (ncx, ncy))
    d2 = d2.replace('<a:ext cx="%d" cy="%d"/>' % (cx, cy), '<a:ext cx="%d" cy="%d"/>' % (ncx, ncy))
    x = x[:s] + d2 + x[e:]


R = lambda blocks: L.render(root, blocks, BASE)

# ================================================================ Resumen y abstract
rep("La suite de 314 pruebas automatizadas se ejecutó sin fallas, con una cobertura de código de 97%",
    "La suite de 340 pruebas automatizadas se ejecutó sin fallas, con una cobertura de código de 97%")
rep("con 100 usuarios, el entorno de demostración respondió sin errores, pero con un percentil 95 de 15 s, por lo que la meta exige más capacidad.",
    "con 100 usuarios, el entorno de demostración respondió sin errores, pero con un percentil 95 de 15 s. Una optimización posterior de las consultas cuadruplicó la capacidad en una medición local y queda por confirmar en ese entorno.")
rep("The suite of 314 automated tests ran without failures, with 97% code coverage",
    "The suite of 340 automated tests ran without failures, with 97% code coverage")
rep("with 100 users, the demonstration environment answered without errors but with a 95th percentile of 15 s, so the target requires more capacity.",
    "with 100 users, the demonstration environment answered without errors but with a 95th percentile of 15 s. A later query optimization quadrupled capacity in a local measurement and remains to be confirmed in that environment.")

# ================================================================ VI: registro de interesados
insert_after(find_para_unique("• Administrador del sistema: administra usuarios, roles y parámetros de configuración autorizados."),
             L.bullet("Jefatura y finanzas: consulta indicadores agregados de gestión y el desempeño operativo de los médicos, sin acceso a datos clínicos (rol incorporado en la versión 2.11.0)."))

# ================================================================ X: casos de uso
rep("El diagrama de casos de uso representa tres actores principales —personal administrativo, médico y administrador del sistema— y un actor secundario, el servicio de inferencia. Los roles aplican el principio de mínimo privilegio: el personal administrativo registra pacientes, casos e imágenes; el médico concentra las funciones clínicas; y el administrador gestiona usuarios y auditoría.",
    "El diagrama de casos de uso representa cuatro actores principales —personal administrativo, médico, administrador del sistema y jefatura y finanzas— y un actor secundario, el servicio de inferencia. Los roles aplican el principio de mínimo privilegio: el personal administrativo registra pacientes, casos e imágenes; el médico concentra las funciones clínicas; el administrador gestiona usuarios y auditoría; y la jefatura consulta indicadores agregados, sin acceso a pacientes ni a casos.")
rep("correspondiente a las funciones de privacidad de la versión 2.4.0 (HU10).",
    "correspondiente a las funciones de privacidad de la versión 2.4.0 (HU10). La versión 2.11.0 agregó el rol de jefatura y finanzas y dos casos de uso: CU19 «Comparar desempeño de médicos» y CU20 «Activar cuenta por correo», que reemplaza la entrega de una contraseña temporal por un enlace de un solo uso enviado al correo del usuario.")
rep("Fuente: Elaboración propia a partir del catálogo de casos de uso del informe de Unidad 2, actualizado con las funciones implementadas posteriormente (CU17 y CU18, destacados).",
    "Fuente: Elaboración propia a partir del catálogo de casos de uso del informe de Unidad 2, actualizado con las funciones implementadas posteriormente (CU17 a CU20, destacados; 25-11-2026).")
replace_image("cap10_casos_uso.png", os.path.join(BASE, "figuras", "cap10_casos_uso.png"))
# Tabla 29: catálogo
add_rows_after("CU18", "Catálogo de casos de uso", [
    ["CU19", "Comparar desempeño de médicos", "Jefatura y finanzas, administrador", "—", "HU07"],
    ["CU20", "Activar cuenta por correo", "Todos", "Extiende CU02", "HU01"]])
rep("Fuente: Elaboración propia a partir del informe de Unidad 2 del proyecto, con CU17 y CU18 actualizados. La especificación detallada se incorporará en los anexos.",
    "Fuente: Elaboración propia a partir del informe de Unidad 2 del proyecto, con CU17 y CU18 actualizados y CU19 y CU20 agregados (versión 2.11.0). La especificación detallada está en los anexos.")

# Tabla 30: componentes
set_row_cell("Proveedor de inferencia", "Componentes, interfaces y dependencias", 1,
             "Solicitud del análisis; validación del contrato de respuesta; servicio de respaldo configurable y respaldo simulado identificado.")
add_rows_after("Auditoría", "Componentes, interfaces y dependencias", [
    ["Envío de correos", "Enlaces de activación de cuentas, de un solo uso y con vencimiento; modo de consola o SMTP.", "Servicio de correo", "Servidor SMTP (configurable)"]])

# ================================================================ X: modelo de datos
rep("El modelo actual contiene 18 tablas, organizadas en cinco grupos: identidad y acceso, pacientes y privacidad, casos e imágenes, triage, y revisión y reportes. La Unidad 2 informaba 14 tablas; la diferencia corresponde a las funciones incorporadas en las versiones 2.3.0 y 2.4.0 (registro de errores, métricas de solicitudes, textos y eventos de consentimiento, y solicitudes de titulares).",
    "El modelo actual contiene 19 tablas, organizadas en cinco grupos: identidad y acceso, pacientes y privacidad, casos e imágenes, triage, y revisión y reportes. La Unidad 2 informaba 14 tablas; la diferencia corresponde a las funciones incorporadas en las versiones 2.3.0, 2.4.0 y 2.11.0 (registro de errores, métricas de solicitudes, textos y eventos de consentimiento, solicitudes de titulares y tokens de activación de cuentas).")
rep("Fuente: Elaboración propia; diagrama generado desde los modelos SQLAlchemy del repositorio (23-11-2026).",
    "Fuente: Elaboración propia; diagrama generado desde los modelos SQLAlchemy del repositorio (25-11-2026, versión 2.12.0).")
replace_image("cap10_modelo_logico.png", os.path.join(BASE, "figuras", "cap10_modelo_logico.png"))
set_row_cell("users", "Modelo físico: tablas, propósito y claves", 1,
             "Usuarios: nombre y apellidos, rol, especialidad del médico, verificación del correo, estado y control de intentos de acceso.")
set_row_cell("users", "Modelo físico: tablas, propósito y claves", 2, "17")
add_rows_after("users", "Modelo físico: tablas, propósito y claves", [
    ["email_tokens", "Enlaces de un solo uso enviados por correo (activación de cuentas); solo se guarda su hash SHA-256.", "7",
     "FK users (borrado en cascada); hash único; vencimiento de 48 horas."]])
rep("Fuente: Elaboración propia a partir de los modelos SQLAlchemy y de las migraciones Alembic del repositorio (23-11-2026). N.º = número de columnas.",
    "Fuente: Elaboración propia a partir de los modelos SQLAlchemy y de las migraciones Alembic del repositorio (25-11-2026). N.º = número de columnas.")
rep("El diccionario de datos, con el detalle de columnas, tipos y restricciones de las 18 tablas,",
    "El diccionario de datos, con el detalle de columnas, tipos y restricciones de las 19 tablas,")

# ================================================================ X: infraestructura
add_rows_after("Equipo con GPU", "Componentes de infraestructura", [
    ["Servicio de inferencia de respaldo (planificado)",
     "Instancia EC2 t4g.small (2 GB) en la misma VPC, sin IP pública ni puertos abiertos a internet, encendida solo para demostraciones; misma imagen del servicio, en CPU (≈ 900 MB de RAM y ≈ 1 s por imagen, medido en local)",
     "Respaldo del análisis automatizado si el equipo con GPU no responde (versión 2.12.0); no creada al 25-11-2026"]])
rep("Fuente: Elaboración propia a partir de docs/ESTADO_AWS.md (24-11-2026).", "Fuente: Elaboración propia a partir de docs/ESTADO_AWS.md y docs/inferencia_remota.md (25-11-2026).")

# ================================================================ X (10.7.1): cliente del servicio de inferencia
rep("Proveedor HTTP con tiempo máximo configurable; valida campos obligatorios y rango de confianza; ante falla usa el proveedor simulado, cuyos resultados quedan marcados como simulados.",
    "Proveedor HTTP con tiempo máximo configurable y espera de conexión corta (5 s); valida campos obligatorios y rango de confianza; ante falla usa el servicio de respaldo, si está configurado (versión 2.12.0), y si tampoco responde, el proveedor simulado, cuyos resultados quedan marcados como simulados.")

# ================================================================ X: figuras de infraestructura cloud y de arquitectura (diagramas_it15, 2.11.0)
replace_image("cap10_infraestructura.png", os.path.join(BASE, "figuras", "it15_cloud.png"))
replace_image("cap10_arquitectura.png", os.path.join(BASE, "figuras", "it15_arquitectura.png"))
rep("Infraestructura cloud desplegada del entorno de demostración (24-11-2026)", "Infraestructura cloud desplegada del entorno de demostración (25-11-2026)")
rep("Fuente: Elaboración propia a partir de docs/ESTADO_AWS.md (actualizado al 24-11-2026) y de la configuración de despliegue del repositorio.",
    "Fuente: Elaboración propia a partir de docs/ESTADO_AWS.md (actualizado al 25-11-2026) y de la configuración de despliegue del repositorio.")
rep("Fuente: Elaboración propia a partir del código fuente y de la documentación del repositorio (24-11-2026, versión 2.10.2).",
    "Fuente: Elaboración propia a partir del código fuente y de la documentación del repositorio (25-11-2026, versión 2.11.0).")

# ================================================================ XI: comparador de médicos (después de la Tabla 36)
s, e = region("Umbrales, frecuencia y responsables de los indicadores")
insert_after(list(PARA.finditer(x, e - 10))[0], R([
    ("p", "Desde la versión 2.11.0, desplegada el 25-11-2026, los indicadores de gestión se complementan con un comparador de médicos para el rol de jefatura y finanzas. Para cada médico y para el promedio del equipo muestra, en un período y por especialidad, las revisiones realizadas y su promedio semanal, los reportes firmados, los casos cerrados, el tiempo medio y el percentil 95 desde el triage hasta la revisión, la carga actual de casos abiertos y de casos de nivel Alta atrasados, los ajustes de triage y la concordancia con el análisis automatizado y con el nivel de triage. No expone datos de pacientes y no evalúa la calidad clínica de un diagnóstico: sirve para planificar la carga del equipo; su pantalla se muestra en los anexos."),
]))
# ================================================================ XII: matriz de casos de prueba (Tabla 40)
rep("Para cada caso se indica la prueba automatizada que lo implementa y su resultado en la ejecución del 23-11-2026.",
    "Para cada caso se indica la prueba automatizada que lo implementa y su resultado en la ejecución del 25-11-2026.")
add_rows_after("PS-08*", "Matriz de casos de prueba y resultado", [
    ["PI-09*", "RF01", "Activación de la cuenta con enlace de un solo uso; enlace vencido, reenviado o inválido",
     "test_jefatura_activacion :: test_activation_link_sets_password_and_verifies_email; test_expired_and_resent_links; test_invalid_token_is_rejected", "Aprobado"],
    ["PS-09*", "RF01", "Rol de jefatura sin acceso a datos clínicos; comparador solo para jefatura y administrador",
     "test_jefatura_activacion :: test_jefatura_has_no_clinical_access; test_compare_doctors_permissions", "Aprobado"],
    ["PI-10*", "RF07", "Comparador de médicos: conteos por médico y promedio del equipo",
     "test_jefatura_activacion :: test_compare_doctors_counts_activity", "Aprobado"],
    ["PI-11*", "RF08", "Servicio de inferencia de respaldo antes del proveedor simulado",
     "test_inference_model :: test_backup_service_is_used_before_simulated; test_simulated_only_when_primary_and_backup_fail; test_status_reports_source_with_backup", "Aprobado"],
    ["PI-12*", "RNF03", "Consultas por solicitud constantes en las listas de casos, pacientes y cola",
     "test_query_counts :: test_list_endpoints_do_not_query_per_row", "Aprobado"]])
set_row_cell("PC-01", "Matriz de casos de prueba y resultado", 4,
             "Ejecutado el 24-11-2026: local, p95 3.974 ms y 59 errores; entorno de demostración (2.10.2), p95 14.979 ms y 0 errores (no aprobado). Versión 2.12.0 en local (25-11-2026): p95 2.532 ms con 100 usuarios; falta repetirla en el entorno de demostración")
rep("Fuente: Elaboración propia a partir de la ejecución de la suite de pruebas del 23-11-2026 (evidencias/pruebas_2026-11-23). (*) Caso agregado en este informe.",
    "Fuente: Elaboración propia a partir de la ejecución de la suite de pruebas del 25-11-2026 (evidencias/pruebas_2026-11-25). (*) Caso agregado en este informe.")

# ================================================================ XII: resultados de la ejecución (Tablas 41 y 42)
rep("La suite automatizada del backend se ejecutó el 23-11-2026 sobre el commit 53ee1b1, que contiene el mismo código de aplicación que la rama principal en el commit c318a45, en un entorno Linux con Python 3.13 y PostgreSQL 16, con una base de datos aislada creada mediante las migraciones. La integración continua del repositorio ejecuta la misma suite con Python 3.12; sus corridas en la rama principal fueron exitosas hasta el 24-11-2026 (versión 2.10.2, con 321 pruebas tras las correcciones del capítulo XII).",
    "La suite automatizada del backend se ejecutó el 25-11-2026 sobre el commit a2c4761, versión 2.12.0, que contiene la 2.11.0 desplegada en el entorno de demostración más la optimización de consultas y el servicio de inferencia de respaldo descritos en este capítulo, en un entorno Linux con Python 3.13 y PostgreSQL 16, con una base de datos aislada creada mediante las migraciones. La integración continua del repositorio ejecuta la misma suite con Python 3.12. La ejecución anterior, del 23-11-2026 (314 pruebas, versión 2.10.0), se conserva como evidencia histórica; las 26 pruebas agregadas desde entonces cubren las dos correcciones bajo carga, las funciones de la 2.11.0 y las de la 2.12.0.")
for old, new in [("Resultado al 23-11-2026", "Resultado al 25-11-2026"),
                 ("314 de 314 aprobadas (100%); 0 errores; 0 omitidas", "340 de 340 aprobadas (100%); 0 errores; 0 omitidas"),
                 ("97% (3.348 sentencias; 85 sin cubrir)", "97% (3.817 sentencias; 127 sin cubrir)"),
                 ("96,1% (1.558 sentencias; 61 sin cubrir)", "94,5% (1.812 sentencias; 100 sin cubrir)")]:
    s, e = region("Resultados de la ejecución de pruebas")
    seg = x[s:e]; assert seg.count(">%s<" % escape(old)) == 1, old
    x = x[:s] + seg.replace(">%s<" % escape(old), ">%s<" % escape(new)) + x[e:]
set_row_cell("Carga y estrés (PC-01, PC-02)", "Resultados de la ejecución de pruebas", 1,
             "PC-01 ejecutada el 24-11-2026: no cumple con 100 usuarios (p95 3.974 ms en local y 14.979 ms en el entorno de demostración); la meta se cumple hasta 50 usuarios en local y 25 en el entorno de demostración. La versión 2.12.0 obtuvo en local (25-11-2026) un p95 de 2.532 ms con 100 usuarios, por repetir en el entorno de demostración; PC-02 no ejecutada")
n41 = x.count(escape("Fuente: Elaboración propia a partir de la ejecución de la suite de pruebas del 23-11-2026 (evidencias/pruebas_2026-11-23)."))
assert n41 == 3, n41  # Tablas 41, 42 y matriz de trazabilidad
rep("Fuente: Elaboración propia a partir de la ejecución de la suite de pruebas del 23-11-2026 (evidencias/pruebas_2026-11-23).",
    "Fuente: Elaboración propia a partir de la ejecución de la suite de pruebas del 25-11-2026 (evidencias/pruebas_2026-11-25).", n=3)
set_row_cell("test_inference_model.py", "Pruebas automatizadas por archivo", 1, "24")
set_row_cell("test_inference_model.py", "Pruebas automatizadas por archivo", 2,
             "Proveedor HTTP, respaldo simulado, servicio de respaldo, reanálisis y contrato con el servicio")
add_rows_after("test_migrations.py", "Pruebas automatizadas por archivo", [
    ["test_jefatura_activacion.py", "11", "Rol de jefatura, ficha y especialidad del médico, activación por correo y comparador de médicos"],
    ["test_middleware_pool.py", "2", "Pool auxiliar de conexiones para las métricas (corrección del bloqueo bajo carga, 2.10.1)"],
    ["test_concurrency_limit.py", "5", "Límite de solicitudes simultáneas y cola de espera (corrección del bloqueo bajo carga, 2.10.2)"],
    ["test_query_counts.py", "3", "Consultas por solicitud constantes en las listas (optimización, 2.12.0)"]])
set_row_cell("Total", "Pruebas automatizadas por archivo", 1, "340")

# ================================================================ XII: optimización de consultas (después de la prueba en el entorno de demostración)
opt = R([
    ("h4", "Optimización de consultas (versión 2.12.0)"),
    ("p", "La prueba en el entorno de demostración identificó la lista de casos y las métricas del dashboard como los endpoints más lentos. El análisis del código mostró que las listas hacían consultas a la base de datos fila por fila: la lista de casos consultaba por separado, para cada caso, su paciente, la cantidad de imágenes y el nivel vigente (63 consultas por página); la lista de pacientes recargaba cada paciente y su texto de consentimiento después de registrar la consulta en la bitácora (54 consultas); y la cola de triage leía el paciente de cada fila (34 consultas). Las métricas del dashboard, además, traían a la aplicación todas las duraciones registradas para calcular el percentil 95. La versión 2.12.0 carga esos datos en consultas agrupadas (6, 6 y 3 consultas, sin importar el número de filas) y calcula el percentil en PostgreSQL con el mismo método del rango más cercano; una prueba automatizada (PI-12*) verifica que el número de consultas no crezca con las filas."),
    ("p", "El efecto se midió el 25-11-2026 en un entorno local con la API en un solo proceso fijado a un núcleo, para acercarse a la capacidad del servidor de demostración, 250 pacientes y 283 casos ficticios y 60.000 registros de métricas. La {T:opt2120} resume los resultados con el mismo script de PC-01."),
    ("tabla", "Prueba de rendimiento local antes y después de la optimización de consultas", "opt2120",
     "Fuente: Elaboración propia a partir de la ejecución del 25-11-2026 (evidencias/rendimiento_2026-11-25/ de la carpeta del informe).",
     [1500, 1200, 1300, 1400, 1100, 1100, 944],
     [["Versión", "Usuarios", "Solicitudes", "Solicitudes/s", "p50 (ms)", "p95 (ms)", "Errores"],
      ["2.11.0", "50", "1.502", "23,4", "1.074,5", "7.050,1", "0"],
      ["2.12.0", "50", "5.724", "94,6", "389,6", "1.142,3", "0"],
      ["2.12.0", "100", "6.069", "99,0", "694,8", "2.531,7", "0"]]),
    ("p", "La capacidad de un proceso aumentó unas cuatro veces y, en este entorno, el percentil 95 con 100 usuarios virtuales quedó bajo la meta de 3 s, sin errores. Estas cifras no se comparan con las de la {T:carga}, medidas sin limitar los núcleos de la API. La versión 2.11.0 en este entorno (23,4 solicitudes por segundo) se comportó de forma parecida al entorno de demostración (unas 20), lo que sugiere que la mejora podría trasladarse; sin embargo, PC-01 se aprueba o se rechaza en el entorno de demostración, y la versión 2.12.0 aún no se despliega ni se mide allí."),
])
insert_before(find_para_unique("Escaneo de seguridad y prueba de restauración", "Ttulo4"), opt)

# ================================================================ XII: matriz de trazabilidad (Tabla 46)
T46 = "Matriz de trazabilidad: requisito, historia, caso de uso, prueba y evidencia"
append_to_cell("RF01", T46, 3, ", CU20")
append_to_cell("RF01", T46, 4, ", PI-09*, PS-09*")
append_to_cell("RF07", T46, 3, ", CU19")
append_to_cell("RF07", T46, 4, ", PI-10*")
append_to_cell("RF08", T46, 4, ", PI-11*")
append_to_cell("RNF03", T46, 4, ", PI-12*")

# ================================================================ XIII: continuidad y versiones
def caption_of(text):
    """Título (sin «Tabla N. ») de la tabla que contiene el texto."""
    i = x.find(escape(text)); assert i > 0, text
    c = x.rfind("FiguraoTablaTtulo", 0, i)
    cs = max(x.rfind("<w:p>", 0, c), x.rfind("<w:p ", 0, c))
    return re.sub(r"^Tabla \S+\. ", "", text_of(x[cs:x.find("</w:p>", c) + 6]))


CAP_INF = caption_of("Indisponibilidad del servicio de inferencia")
set_row_cell("Indisponibilidad del servicio de inferencia", CAP_INF, 1,
             "Usar el servicio de respaldo en AWS, si está encendido, y si no, el proveedor simulado identificado; reanalizar al restablecerse")
set_row_cell("Indisponibilidad del servicio de inferencia", CAP_INF, 3,
             "Respaldo simulado, reanálisis y servicio de respaldo configurable (2.12.0) implementados y probados; instancia de respaldo en AWS por crear")
rep("La versión publicada en el entorno de demostración al cierre de este informe es la 2.10.2, desplegada el 24-11-2026, que corrige los dos bloqueos bajo carga descritos en el capítulo XII.",
    "La versión publicada en el entorno de demostración es la 2.11.0, desplegada el 25-11-2026, que agrega el rol de jefatura y finanzas, el comparador de médicos, la especialidad del médico y la activación de cuentas por correo; la precedieron la 2.10.1 y la 2.10.2 (24-11-2026), que corrigen los dos bloqueos bajo carga descritos en el capítulo XII. La versión 2.12.0, con la optimización de consultas y el servicio de inferencia de respaldo, está terminada y probada; su despliegue queda pendiente.")

# ================================================================ XIV: factibilidad
rep("prototipo desplegado (versión 2.10.2); pruebas automatizadas aprobadas con 97% de cobertura; pruebas de carga con p95 bajo 3 s hasta 50 usuarios virtuales en local y 25 en el entorno de demostración, tras corregir dos bloqueos bajo carga detectados por esas mismas pruebas; modelo propio conectado con respaldo simulado",
    "prototipo desplegado (versión 2.11.0); 340 pruebas automatizadas aprobadas con 97% de cobertura; pruebas de carga con p95 bajo 3 s hasta 50 usuarios virtuales en local y 25 en el entorno de demostración, tras corregir dos bloqueos bajo carga detectados por esas mismas pruebas, y optimización de consultas (2.12.0) con p95 de 2,5 s con 100 usuarios en local, por confirmar en el entorno de demostración; modelo propio conectado, con servicio de respaldo configurable y respaldo simulado")
rep("La arquitectura mitiga el primer punto con el proveedor desacoplado y el respaldo simulado,",
    "La arquitectura mitiga el primer punto con el proveedor desacoplado, un servicio de respaldo en AWS configurable desde la versión 2.12.0 y el respaldo simulado,")

# ================================================================ XV: cronograma y riesgos
nS8 = x.count(escape("Sprint 8 (2.6.0–2.10.0; correcciones 2.10.1 y 2.10.2 el 24-11)"))
rep("Sprint 8 (2.6.0–2.10.0; correcciones 2.10.1 y 2.10.2 el 24-11)",
    "Sprint 8 (2.6.0–2.10.0; correcciones 2.10.1 y 2.10.2 el 24-11; 2.11.0 y 2.12.0 el 25-11)", n=nS8)
rep("Respaldo simulado identificado y reanálisis; traslado a la nube documentado",
    "Respaldo simulado identificado y reanálisis; servicio de respaldo en AWS configurable (2.12.0), con la instancia por crear")

# ================================================================ XVI: conclusiones y recomendaciones
rep("verificado mediante 314 pruebas automatizadas aprobadas.", "verificado mediante 340 pruebas automatizadas aprobadas.")
rep("bloqueo por intentos fallidos y límite de solicitudes; estos controles están cubiertos por pruebas automatizadas.",
    "bloqueo por intentos fallidos y límite de solicitudes; desde la versión 2.11.0 incluye un rol de jefatura sin acceso a datos clínicos y la activación de cuentas con enlaces de un solo uso. Estos controles están cubiertos por pruebas automatizadas.")
rep("la plataforma emite reportes con firma del médico y calcula indicadores en el dashboard.",
    "la plataforma emite reportes con firma del médico, calcula indicadores en el dashboard y, desde la versión 2.11.0, ofrece a la jefatura un comparador de médicos.")
rep("• Dimensionar la capacidad para la meta de rendimiento —el entorno de demostración atiende unas 20 solicitudes por segundo con un proceso— (procesos de la API, tamaño de la instancia y costo de la lista de casos y de las métricas del dashboard), repetir PC-01 en el entorno resultante, ejecutar la prueba de estrés y un escaneo de seguridad activo y autenticado de la API, y registrar sus resultados antes de un piloto.",
    "• Desplegar la versión 2.12.0, cuya optimización de consultas cuadruplicó la capacidad de un proceso en una medición local, y repetir PC-01 en el entorno de demostración; si la meta no se cumple, dimensionar la capacidad (procesos de la API y tamaño de la instancia). Ejecutar además la prueba de estrés y un escaneo de seguridad activo y autenticado de la API, y registrar sus resultados antes de un piloto.")
rep("• Trasladar el servicio de inferencia desde el equipo personal a una infraestructura administrada,",
    "• Crear la instancia de respaldo del servicio de inferencia en AWS prevista en la versión 2.12.0 y, a mediano plazo, trasladar el servicio desde el equipo personal a una infraestructura administrada,")

# ================================================================ XVIII: casos de uso, diccionario, evidencia y capturas
rep("CU17 y CU18 se especifican en este informe a partir del comportamiento verificado en el código y en las pruebas.",
    "CU17 a CU20 se especifican en este informe a partir del comportamiento verificado en el código y en las pruebas.")
rep("1. El administrador crea un usuario con RUT, correo, nombre y rol (Administrativo, Médico o Administrador). 2. El sistema valida unicidad del RUT y del correo. 3. El sistema registra el alta en la auditoría.",
    "1. El administrador crea un usuario con RUT, correo, nombre, apellidos y rol (Administrativo, Médico, Jefatura y finanzas o Administrador) y, para el médico, su especialidad. 2. El sistema valida el dígito verificador y la unicidad del RUT y del correo. 3. El sistema envía al correo un enlace de activación (CU20) o, a elección del administrador, asigna una contraseña temporal. 4. El sistema registra el alta en la auditoría.")
rep("1a. Cambio de rol o desactivación de un usuario existente, con registro en la auditoría. 2a. RUT o correo duplicado: se rechaza.",
    "1a. Cambio de rol, de nombre o de especialidad, o desactivación de un usuario existente, con registro en la auditoría. 1b. Médico sin especialidad: se rechaza. 2a. RUT o correo duplicado: se rechaza. 3a. Reenvío del enlace de activación: invalida los anteriores.")
CU_NEW = [
    ("CU19. Comparar desempeño de médicos", [
        ["Actor(es)", "Jefatura y finanzas, Administrador"],
        ["Precondición", "Sesión activa con rol Jefatura y finanzas o Administrador."],
        ["Flujo principal", "1. El usuario elige el período y, opcionalmente, una especialidad. 2. El sistema calcula por médico y para el promedio del equipo las revisiones y su promedio semanal, los reportes firmados, los casos cerrados, el tiempo medio y el percentil 95 hasta la revisión, los casos abiertos asignados, los casos Alta atrasados, los ajustes de triage y la concordancia con el análisis automatizado y con el triage. 3. El usuario compara hasta cuatro médicos lado a lado y puede exportar la tabla en formato CSV."],
        ["Flujos alternativos", "2a. Sin actividad en el período: los indicadores se muestran vacíos. 2b. Otro rol solicita el comparador: se rechaza (403)."],
        ["Postcondición", "Consulta sin datos de pacientes; no modifica información."],
        ["Requisito", "RF07"]]),
    ("CU20. Activar cuenta por correo", [
        ["Actor(es)", "Todos (usuario nuevo); Administrador (reenvío)"],
        ["Precondición", "Cuenta creada por el administrador con envío de enlace (CU02)."],
        ["Flujo principal", "1. El usuario abre el enlace recibido en su correo. 2. El sistema verifica que el enlace exista, no haya vencido (48 horas) y no se haya usado. 3. El usuario define su contraseña según la política. 4. El sistema marca el correo como verificado, invalida el enlace y registra la activación en la auditoría."],
        ["Flujos alternativos", "2a. Enlace vencido, usado o inválido: se rechaza y el usuario debe pedir uno nuevo. 2b. El administrador reenvía el enlace: los anteriores dejan de ser válidos. 3a. Contraseña que no cumple la política: se rechaza con mensaje."],
        ["Postcondición", "Cuenta activa con correo verificado; del enlace solo se conserva su hash."],
        ["Requisito", "RF01, RNF01"]]),
]
m18 = find_para_unique("CU18. Gestionar solicitudes de titulares de datos")
bold_tpl = m18.group(0)
tbl_end = x.find("</w:tbl>", m18.end()) + 8
xml = []
for title, rows in CU_NEW:
    xml.append(bold_tpl.replace(escape("CU18. Gestionar solicitudes de titulares de datos"), escape(title)))
    xml.append(L.table([2200, 6344], [["Elemento", "Descripción"]] + rows))
x = x[:tbl_end] + "".join(xml) + x[tbl_end:]

rep("El diccionario de datos se generó a partir de los modelos SQLAlchemy del repositorio (23-11-2026) y describe las 18 tablas del modelo con sus columnas, tipos, obligatoriedad y claves.",
    "El diccionario de datos se generó a partir de los modelos SQLAlchemy del repositorio (25-11-2026, versión 2.12.0) y describe las 19 tablas del modelo con sus columnas, tipos, obligatoriedad y claves.")
schema = json.load(open(os.path.join(HERE, "schema_modelos.json"), encoding="utf-8"))
rows = [["Tabla", "Columna", "Tipo", "Nulo", "Clave / restricción"]]
for t, v in schema.items():
    first = True
    for n, typ, pk, nul, fks, *rest in v["cols"]:
        key = "PK" if pk else ("FK → " + ", ".join(fks) if fks else "")
        if rest and rest[0] and not pk: key = (key + "; " if key else "") + "Única"
        rows.append([t if first else "", n, typ, "Sí" if nul else "No", key]); first = False
s, e = region("Diccionario de datos")
ts = x.find("<w:tbl>", s); te = x.find("</w:tbl>", ts) + 8; assert s < ts < te < e
x = x[:ts] + L.table([1900, 2200, 1900, 600, 1944], rows) + x[te:]

rep("La evidencia de la ejecución de pruebas del 23-11-2026 se conserva en el repositorio del proyecto, en la carpeta docs/informe_final/evidencias/pruebas_2026-11-23: el informe JUnit con el resultado de cada una de las 314 pruebas y el resumen de cobertura por archivo.",
    "La evidencia de la ejecución de pruebas del 25-11-2026 se conserva en el repositorio del proyecto, en la carpeta docs/informe_final/evidencias/pruebas_2026-11-25: el informe JUnit con el resultado de cada una de las 340 pruebas y el resumen de cobertura por archivo. La ejecución anterior, del 23-11-2026 (314 pruebas), se conserva en evidencias/pruebas_2026-11-23, y las mediciones de rendimiento en evidencias/rendimiento_2026-11-24, rendimiento_aws_2026-11-24 y rendimiento_2026-11-25.")

rep("Capturas del prototipo (versión 2.10.2)", "Capturas del prototipo (versiones 2.10.2 y 2.11.0)")
rep("Las figuras siguientes muestran las pantallas principales de la versión 2.10.2, la misma desplegada en el entorno de demostración,",
    "Las figuras siguientes muestran las pantallas principales de la versión 2.10.2, desplegada en el entorno de demostración el 24-11-2026,")
SRC_211 = "Fuente: Captura del prototipo, versión 2.11.0, ejecutado en un entorno local con datos ficticios (25-11-2026)."
last = x.rfind(escape("Fuente: Captura del prototipo, versión 2.10.2, ejecutado en un entorno local con datos ficticios y el proveedor de IA simulado (24-11-2026)."))
assert last > 0
m_last = [m for m in PARA.finditer(x) if m.start() <= last < m.end()][0]
insert_after(m_last, R([
    ("p", "Las dos figuras siguientes corresponden a funciones de la versión 2.11.0, desplegada en el entorno de demostración el 25-11-2026, capturadas en el mismo entorno local con datos ficticios: el comparador de médicos, con la vista del rol de jefatura y finanzas, y la ficha de un usuario nuevo, con su especialidad y el envío del enlace de activación."),
    ("figura", "Comparador de médicos: comparación lado a lado y tabla de todos los médicos con el promedio del equipo (vista de jefatura y finanzas)", "cap_comparador", SRC_211, "figuras/capturas_2.11.0/09_comparador.png"),
    ("figura", "Ficha de un usuario nuevo: rol, especialidad, RUT, correo y acceso inicial por enlace de activación (vista del administrador)", "cap_nuevo_usuario", SRC_211, "figuras/capturas_2.11.0/10_nuevo_usuario.png"),
]))
MAX_H_V = 6000000
for k in ["cap_comparador", "cap_nuevo_usuario"]:
    a = x.find('w:name="_Ref_F_%s"' % k); assert a > 0, k
    b = x.find("FiguraoTablaFuente", a); seg = x[a:b]
    cx, cy = map(int, re.search(r'<wp:extent cx="(\d+)" cy="(\d+)"/>', seg).groups())
    if cy > MAX_H_V:
        ncy = MAX_H_V; ncx = int(cx * ncy / cy)
        seg = seg.replace('<wp:extent cx="%d" cy="%d"/>' % (cx, cy), '<wp:extent cx="%d" cy="%d"/>' % (ncx, ncy))
        seg = seg.replace('<a:ext cx="%d" cy="%d"/>' % (cx, cy), '<a:ext cx="%d" cy="%d"/>' % (ncx, ncy))
        x = x[:a] + seg + x[b:]

x, nums = L.renumerar(x)
open(p, "w", encoding="utf-8").write(x)
print("ok; tablas", max(v for k, v in nums.items() if "_T_" in k), "figuras", max(v for k, v in nums.items() if "_F_" in k))
