# -*- coding: utf-8 -*-
"""Iteración 13: prueba de rendimiento en el entorno de demostración (AWS) y versión 2.10.2 (maestro 1.2-rc -> 1.3-rc).
Uso: python3 iter13_rendimiento_aws.py <dir_desempaquetado_maestro>"""
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

# ---------------------------------------------------------------- resumen y abstract
rep("Una prueba de carga local cumplió la meta de tiempo de respuesta hasta 50 usuarios virtuales (percentil 95 de 1.592 ms) y la superó con 100 (3.974 ms). Quedan pendientes la prueba de carga en el entorno de demostración, el escaneo dinámico de seguridad,",
    "Las pruebas de carga cumplieron la meta de tiempo de respuesta hasta 50 usuarios virtuales en un entorno local (percentil 95 de 1.592 ms) y hasta 25 en el entorno de demostración (2.308 ms); con 100 usuarios, el entorno de demostración respondió sin errores, pero con un percentil 95 de 15 s, por lo que la meta exige más capacidad. Quedan pendientes el escaneo dinámico de seguridad,")
rep("A local load test met the response-time target up to 50 virtual users (95th percentile of 1592 ms) and exceeded it with 100 (3974 ms). Load testing in the demonstration environment, dynamic security scanning,",
    "Load tests met the response-time target up to 50 virtual users in a local environment (95th percentile of 1592 ms) and up to 25 in the demonstration environment (2308 ms); with 100 users, the demonstration environment answered without errors but with a 95th percentile of 15 s, so the target requires more capacity. Dynamic security scanning,")

# ---------------------------------------------------------------- XI (indicador p95)
rep("Sin medición en el entorno de demostración; prueba local: p95 de 1.592 ms con 50 usuarios y 3.974 ms con 100",
    "Entorno de demostración: p95 de 2.308 ms con 25 usuarios y 14.979 ms con 100 (0 errores); prueba local: 1.592 ms con 50 usuarios y 3.974 ms con 100")

# ---------------------------------------------------------------- XII
rep("Ejecutado el 24-11-2026 en entorno local: p95 3.974 ms, 59 errores (no aprobado)",
    "Ejecutado el 24-11-2026: local, p95 3.974 ms y 59 errores; entorno de demostración (2.10.2), p95 14.979 ms y 0 errores (no aprobado)")
rep("PC-01 ejecutada el 24-11-2026 en entorno local: p95 3.974 ms con 100 usuarios (no cumple; sí con 50); PC-02 no ejecutada",
    "PC-01 ejecutada el 24-11-2026: no cumple con 100 usuarios (p95 3.974 ms en local y 14.979 ms en el entorno de demostración); la meta se cumple hasta 50 usuarios en local y 25 en el entorno de demostración; PC-02 no ejecutada")
rep("El rendimiento bajo carga solo se midió en un entorno local (apartado siguiente);",
    "El rendimiento bajo carga se midió en un entorno local y en el entorno de demostración (apartados siguientes);")
rep("En consecuencia, los indicadores de rendimiento y disponibilidad del capítulo XI no cuentan aún con medición en el entorno de demostración.",
    "En consecuencia, el indicador de disponibilidad del capítulo XI no cuenta aún con medición en el entorno de demostración.")
rep("La corrección se publicó como versión 2.10.1 y se desplegó en el entorno de demostración el 24-11-2026; el rendimiento bajo carga en ese entorno no se ha medido.",
    "La corrección se publicó como versión 2.10.1 y se desplegó en el entorno de demostración el 24-11-2026; la medición en ese entorno se presenta en el apartado siguiente.")
rep("y el entorno local tiene más capacidad que la instancia t4g.micro del entorno de demostración, cuyo rendimiento no se midió. La prueba de estrés PC-02 no se ejecutó.",
    "y el entorno local tiene más capacidad que el entorno de demostración, cuya medición se presenta a continuación. La prueba de estrés PC-02 no se ejecutó.")
rep("Evidencia parcial: PC-01 en entorno local cumple con 50 usuarios y no con 100; sin medición en el entorno de demostración",
    "Evidencia: PC-01 no cumple con 100 usuarios (p95 3.974 ms en local y 14.979 ms en el entorno de demostración); cumple hasta 50 usuarios en local y 25 en el entorno de demostración")

AWS = [
 ("h4", "Prueba de rendimiento en el entorno de demostración"),
 ("p", "El 24-11-2026 se repitió PC-01 en el entorno de demostración, con el mismo script y el mismo recorrido de consultas. El servidor es una instancia EC2 t4g.micro (2 vCPU y 1 GB de RAM), con la API en un solo proceso de uvicorn, y la base de datos está en RDS db.t4g.micro. Para no alterar los datos ni la bitácora de auditoría del entorno, durante la prueba la API se apuntó a una copia de la base en un esquema temporal de la misma instancia de RDS (316 casos y 275 pacientes ficticios), que se eliminó al terminar. El generador de carga se ejecutó en el propio servidor, contra la dirección pública del sitio, con TLS y el proxy inverso incluidos, y ocupó una fracción menor de la CPU. La {T:carga_aws} resume los resultados."),
 ("tabla", "Resultados de la prueba de rendimiento en el entorno de demostración", "carga_aws",
  "Fuente: Elaboración propia a partir de la ejecución del 24-11-2026 con la versión 2.10.2 (evidencias/rendimiento_aws_2026-11-24/ de la carpeta del informe).",
  [1068] * 8,
  [["Usuarios virtuales", "Duración", "Solicitudes", "Errores", "Solicitudes/s", "p50 (ms)", "p95 (ms)", "Máx. (ms)"],
   ["10", "60 s", "1.251", "0", "20,7", "451,4", "922,6", "1337,9"],
   ["25", "61 s", "1.259", "0", "20,7", "1123,3", "2308,2", "3115,0"],
   ["50", "64 s", "1.233", "0", "19,4", "2124,8", "6132,4", "7408,9"],
   ["100", "912 s", "15.013", "0", "16,5", "4454,6", "14978,7", "18489,0"]]),
 ("p", "La capacidad del entorno es de unas 20 solicitudes por segundo, limitada por el único proceso de la API, que ocupó un núcleo completo durante toda la prueba. Con 10 y 25 usuarios virtuales el percentil 95 fue de 923 y 2.308 ms, dentro de la meta; con 50, de 6.132 ms. Con 100 usuarios durante 15 minutos, la API atendió 15.013 solicitudes sin errores ni interrupciones —el endpoint de salud respondió en todo momento—, pero con un percentil 95 de 14.979 ms. Por lo tanto, PC-01 tampoco se aprueba en este entorno, donde la meta se cumple hasta 25 usuarios virtuales. Los endpoints más lentos fueron la lista de casos y las métricas del dashboard, con un percentil 95 cercano a 16 s."),
 ("p", "Esta prueba detectó un segundo defecto. En una primera serie con la versión 2.10.1, ejecutada desde un generador externo que retuvo y cortó conexiones con 100 usuarios, la API dejó de responder por completo, incluso después de terminada la carga. La causa era que, con más solicitudes simultáneas que conexiones en el pool de la base de datos, una solicitud ya autenticada retenía su conexión mientras esperaba un hilo para ejecutar el endpoint, y los hilos estaban ocupados esperando conexiones; solo el tiempo de espera del pool, de 30 s, deshacía el ciclo. El defecto se reprodujo en local y se corrigió en la versión 2.10.2 con un límite de solicitudes simultáneas por proceso, inferior al tamaño del pool: las demás esperan en cola sin ocupar hilos ni conexiones y, si la espera supera 20 s, reciben una respuesta de servicio ocupado; el endpoint de salud queda fuera de ese límite. Se agregaron pruebas de regresión —la suite queda en 321 pruebas aprobadas— y la versión se desplegó el mismo día, antes de la serie de la {T:carga_aws}."),
 ("p", "En consecuencia, la meta de rendimiento exige más capacidad que la del entorno de demostración actual: más procesos de la API, con la memoria que ello requiere, una instancia mayor o la optimización de las consultas más costosas. Como en la prueba local, los usuarios virtuales no esperan entre acciones, y no se incluyeron la carga de imágenes ni la inferencia."),
]
m = find_para("Esta evidencia tiene alcance limitado: el servidor y el generador de carga compartieron la máquina")
x = x[:m.end()] + L.render(root, AWS, os.path.dirname(HERE)) + x[m.end():]

# ---------------------------------------------------------------- XIII, XIV, XVI
rep("es la 2.10.1, desplegada el 24-11-2026, que corrige el bloqueo bajo carga descrito en el capítulo XII.",
    "es la 2.10.2, desplegada el 24-11-2026, que corrige los dos bloqueos bajo carga descritos en el capítulo XII.")
rep("prototipo desplegado (versión 2.10.1); pruebas automatizadas aprobadas con 97% de cobertura; prueba de carga local con p95 bajo 3 s hasta 50 usuarios virtuales, tras corregir un bloqueo bajo carga detectado por esa misma prueba;",
    "prototipo desplegado (versión 2.10.2); pruebas automatizadas aprobadas con 97% de cobertura; pruebas de carga con p95 bajo 3 s hasta 50 usuarios virtuales en local y 25 en el entorno de demostración, tras corregir dos bloqueos bajo carga detectados por esas mismas pruebas;")
rep("Inferencia en equipo personal; meta de rendimiento no cumplida con 100 usuarios;",
    "Inferencia en equipo personal; meta de rendimiento no cumplida con 100 usuarios (el entorno de demostración atiende unas 20 solicitudes por segundo);")
rep("Dimensionar la capacidad para la meta de rendimiento (procesos de la API, tamaño del pool de conexiones y de la instancia), repetir la prueba de carga en el entorno de demostración, ejecutar la prueba de estrés",
    "Dimensionar la capacidad para la meta de rendimiento —el entorno de demostración atiende unas 20 solicitudes por segundo con un proceso— (procesos de la API, tamaño de la instancia y costo de la lista de casos y de las métricas del dashboard), repetir PC-01 en el entorno resultante, ejecutar la prueba de estrés")

x, nums = L.renumerar(x)
open(p, "w", encoding="utf-8").write(x)
print("ok", len(nums), "tabla nueva:", nums.get("_Ref_T_carga_aws"))
