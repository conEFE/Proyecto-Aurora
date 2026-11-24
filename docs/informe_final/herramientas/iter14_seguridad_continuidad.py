# -*- coding: utf-8 -*-
"""Iteración 14: escaneo OWASP ZAP, prueba de restauración y monitoreo de disponibilidad (maestro 1.3-rc -> 1.4-rc).
Uso: python3 iter14_seguridad_continuidad.py <dir_desempaquetado_maestro>"""
import sys, os, re
from xml.sax.saxutils import escape
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import maestro_lib as L

root = sys.argv[1]
p = os.path.join(root, "word", "document.xml")
x = open(p, encoding="utf-8").read(); L.init_ids(x)
PARA = re.compile(r"<w:p\b(?:(?!<w:p\b).)*?</w:p>", re.S)

def text_of(px):
    return "".join(re.findall(r"<w:t[^>]*>([^<]*)</w:t>", px))

def find_para(start_text):
    hits = [m for m in PARA.finditer(x) if text_of(m.group(0)).startswith(escape(start_text))]
    assert len(hits) == 1, (start_text, len(hits))
    return hits[0]

def rep(old, new):
    global x
    o, n = escape(old), escape(new); assert x.count(o) == 1, (old[:70], x.count(o)); x = x.replace(o, n)

def cell_after(anchor, old, new):
    """Cambia el primer párrafo con texto exacto `old` que sigue al párrafo que comienza con `anchor`."""
    global x
    a = find_para(anchor)
    for m in PARA.finditer(x, a.end()):
        if text_of(m.group(0)) == escape(old):
            px = m.group(0); assert px.count("<w:t") == 1, old
            x = x[:m.start()] + re.sub(r"(<w:t[^>]*>)[^<]*(</w:t>)", lambda mm: mm.group(1) + escape(new) + mm.group(2), px) + x[m.end():]
            return
    raise AssertionError(old)

# ---------------------------------------------------------------- resumen y abstract
rep("Quedan pendientes el escaneo dinámico de seguridad, la validación clínica formal del modelo y un piloto con una institución de salud.",
    "Un escaneo pasivo de seguridad no encontró riesgos altos y la restauración de un respaldo se verificó completa. Quedan pendientes la validación clínica formal del modelo y un piloto con una institución de salud.")
rep("Dynamic security scanning, a formal clinical validation of the model and a pilot with a healthcare institution remain pending.",
    "A passive security scan found no high-risk issues and a backup restore was verified complete. A formal clinical validation of the model and a pilot with a healthcare institution remain pending.")

# ---------------------------------------------------------------- XI (K3)
rep("Endpoint /health disponible; sin monitor externo",
    "Chequeo de /health cada minuto desde el servidor (CloudWatch) con alarma por correo, desde el 24-11-2026")
cell_after("Chequeo de /health cada minuto desde el servidor (CloudWatch)", "Sin medición",
           "Medición iniciada el 24-11-2026; aún sin un mes completo")

# ---------------------------------------------------------------- XII
cell_after("OWASP ZAP (flujo zap.yml a pedido)", "No ejecutado",
           "Ejecutado el 24-11-2026: 0 altas, 1 media y 3 bajas (aprobado)")
rep("No ejecutado: el flujo ZAP no registra corridas",
    "Ejecutado el 24-11-2026 (ZAP 2.17.0, análisis pasivo en el CI): 0 altas; 1 media y 3 bajas de encabezados, 2 corregidas")
rep("no se acreditan la disponibilidad del servicio, la resistencia a ataques dinámicos, la usabilidad ni el desempeño clínico, cuyas pruebas no se han ejecutado. En consecuencia, el indicador de disponibilidad del capítulo XI no cuenta aún con medición en el entorno de demostración.",
    "no se acreditan la resistencia a ataques activos, la usabilidad ni el desempeño clínico, cuyas pruebas no se han ejecutado. La disponibilidad se monitorea desde el 24-11-2026, pero aún sin un período suficiente para el indicador mensual del capítulo XI.")
rep("control de acceso por rol verificado contra la base de datos; escaneo dinámico pendiente.",
    "control de acceso por rol verificado contra la base de datos; escaneo pasivo OWASP ZAP sin hallazgos de riesgo alto (24-11-2026).")

SEG = [
 ("h4", "Escaneo de seguridad y prueba de restauración"),
 ("p", "El 24-11-2026 se ejecutó el caso PS-04 con el flujo de OWASP ZAP del repositorio (ZAP 2.17.0, análisis base: exploración de un minuto y análisis pasivo, sin ataques). El objetivo fue el sistema completo —proxy inverso, sitio y API— levantado con contenedores dentro de la integración continua, con secretos desechables y sin datos, usando la misma configuración y las mismas imágenes que el entorno de demostración. La exploración cubrió el sitio estático; la API autenticada no quedó cubierta, porque la aplicación es de una sola página y la API exige un token. La {T:zap} resume los hallazgos: ninguno de riesgo alto, por lo que PS-04 se aprueba."),
 ("tabla", "Hallazgos del escaneo OWASP ZAP y decisión adoptada", "zap",
  "Fuente: Elaboración propia a partir del informe de ZAP del 24-11-2026 (evidencias/zap_2026-11-24/ de la carpeta del informe).",
  [1100, 3300, 4144],
  [["Riesgo", "Hallazgo", "Decisión"],
   ["Medio", "Política de seguridad de contenido con style-src 'unsafe-inline'", "Riesgo aceptado: la página de inicio inserta estilos propios; script-src 'self' sigue bloqueando scripts en línea"],
   ["Bajo", "Falta Cross-Origin-Opener-Policy", "Corregido el mismo día (same-origin)"],
   ["Bajo", "Falta Cross-Origin-Resource-Policy", "Corregido el mismo día (same-origin)"],
   ["Bajo", "Falta Cross-Origin-Embedder-Policy", "Riesgo aceptado: solo se requiere para el aislamiento entre orígenes, que la aplicación no usa"]]),
 ("p", "Las dos correcciones se desplegaron el mismo día y se verificó que el sitio cargara sin errores. Quedan pendientes un escaneo autenticado de la API y un escaneo activo en un entorno de pruebas."),
 ("p", "Ese mismo día se probó la restauración de un respaldo, pendiente hasta entonces. El volcado diario automático de las 06:15 UTC se descargó desde S3 en el servidor, se verificó su integridad (compresión válida, marca de volcado completo y 19 tablas) y se restauró en un esquema temporal de la misma base de datos, sin interrumpir el servicio. Las 19 tablas restauradas coincidieron en número de filas con la base en uso —entre ellas 316 casos, 275 pacientes y 3.407 eventos de la bitácora—, al igual que la versión de las migraciones y el trigger que impide modificar la bitácora. La descarga, la verificación y la carga tomaron unos 3 s. Las 258 imágenes registradas tenían su archivo en S3, y cinco elegidas al azar se descifraron con su huella SHA-256 correcta. El esquema temporal se eliminó al terminar. La prueba no incluyó la recuperación del servidor completo ni de versiones anteriores de las imágenes."),
]
m = find_para("En consecuencia, la meta de rendimiento exige más capacidad que la del entorno de demostración actual")
x = x[:m.end()] + L.render(root, SEG, os.path.dirname(HERE)) + x[m.end():]

# ---------------------------------------------------------------- XIII
rep("Registros en CloudWatch y alertas de presupuesto; sin alarmas de disponibilidad ni monitor externo",
    "Registros en CloudWatch, alertas de presupuesto y, desde el 24-11-2026, chequeo de /health cada minuto desde el propio servidor, con alarmas por correo ante falta de respuesta o falla de la instancia; sin tablero ni monitor externo a AWS")
rep("no cuentan con evidencia de implementación; la prueba de restauración de un respaldo figura como pendiente en la documentación del proyecto.",
    "no cuentan con evidencia de implementación. La restauración de un respaldo se probó el 24-11-2026: el volcado diario se restauró completo y coincidió con la base en uso (capítulo XII).")
rep("Volcados diarios disponibles; restauración no probada",
    "Volcados diarios disponibles; restauración probada el 24-11-2026 (unos 3 s; 19 tablas coincidentes)")

# ---------------------------------------------------------------- XIV, XV, XVI
rep("DICOM y prueba de restauración pendientes", "DICOM pendiente")
rep("Respaldo de RDS y volcados diarios; restauración no probada",
    "Respaldo de RDS y volcados diarios; restauración probada el 24-11-2026")
rep("Control de acceso, cifrado, bitácora y rotación de credenciales probados; escaneo dinámico no ejecutado",
    "Control de acceso, cifrado, bitácora y rotación de credenciales probados; escaneo pasivo sin riesgos altos; escaneo activo no ejecutado")
rep("Quedan pendientes el escaneo dinámico de seguridad, la prueba de restauración de respaldos y una copia de respaldo fuera de AWS (el proyecto de AWS no permite copias entre regiones).",
    "Se ejecutaron un escaneo pasivo de seguridad, sin hallazgos de riesgo alto, y una prueba de restauración de respaldos, que resultó completa. Queda pendiente una copia de respaldo fuera de AWS (el proyecto de AWS no permite copias entre regiones).")
rep("ejecutar la prueba de estrés y el escaneo dinámico de seguridad, y registrar sus resultados antes de un piloto.",
    "ejecutar la prueba de estrés y un escaneo de seguridad activo y autenticado de la API, y registrar sus resultados antes de un piloto.")
rep("Probar y documentar la restauración de respaldos, incorporar una copia cifrada fuera de AWS (el proyecto de AWS no permite copias entre regiones) y configurar monitoreo externo de disponibilidad y alarmas.",
    "Repetir periódicamente la prueba de restauración, incorporar una copia cifrada fuera de AWS (el proyecto de AWS no permite copias entre regiones) y complementar el monitoreo desde el servidor con uno externo e independiente de AWS.")

x, nums = L.renumerar(x)
open(p, "w", encoding="utf-8").write(x)
print("ok", len(nums), "tabla zap:", nums.get("_Ref_T_zap"))
