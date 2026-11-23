# -*- coding: utf-8 -*-
"""Iteración 8: resumen, abstract, introducción, capítulo III (criterios, verificación, RF/RNF, restricciones),
K5 en V y XI, RF09 en XII y presupuesto vigente en XIV (v0.11 -> v0.12)."""
import sys, os, re
from xml.sax.saxutils import escape
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import maestro_lib as L
import cap1_3_contenido as C
root = sys.argv[1]; p = os.path.join(root, "word", "document.xml")
x = open(p, encoding="utf-8").read(); L.init_ids(x)
R = lambda b: L.render(root, b, os.path.dirname(HERE))

def rep(old, new, raw=False):
    global x
    o = old if raw else escape(old); n = new if raw else escape(new)
    assert x.count(o) == 1, (old[:70], x.count(o)); x = x.replace(o, n)

def para_bounds(text):
    i = x.find(escape(text)); assert i > 0 and x.count(escape(text)) == 1, text[:60]
    s = max(x.rfind("<w:p ", 0, i), x.rfind("<w:p>", 0, i)); e = x.find("</w:p>", i) + 6
    return s, e

def insert_after_para(text, xml, drop_next_empty=True):
    global x
    s, e = para_bounds(text); cut = e
    if drop_next_empty:
        m = re.match(r'<w:p><w:pPr><w:pStyle w:val="Prrafo"/></w:pPr></w:p>', x[e:e + 80])
        if m: cut = e + m.end()
    x = x[:e] + xml + x[cut:]

def insert_before_para(text, xml):
    global x
    s, e = para_bounds(text); x = x[:s] + xml + x[s:]

def replace_para(text, xml):
    global x
    s, e = para_bounds(text); x = x[:s] + xml + x[e:]

# Resumen, palabras clave, abstract, keywords e introducción
x = L.insert_after_bookmark(x, "_Toc177988440", R(C.RESUMEN))
insert_after_para("Palabras Claves", L.para(C.KW_ES))
x = L.insert_after_bookmark(x, "_Toc177988441", R(C.ABSTRACT))
insert_after_para("Keywords", L.para(C.KW_EN))
x = L.insert_after_bookmark(x, "_Toc177988443", R(C.INTRO))

# Capítulo III
rep("Las historias HU09–HU12 amplían el conjunto funcional del capítulo. Su prioridad MoSCoW queda pendiente de acuerdo y sus criterios requieren contraste con los requerimientos funcionales, el código y las pruebas. No se declara su implementación ni cumplimiento.",
    "Las historias HU09 a HU12 amplían el conjunto funcional del capítulo; sus prioridades MoSCoW fueron aprobadas y figuran en la tabla de historias de usuario. Sus criterios de aceptación se verifican al final de este apartado.")
rep("Se mantienen como propuestas y no se consideran verificados ni cerrados.", "Su verificación se informa al final de este apartado.")
rep('<w:pStyle w:val="Ttulo3"/></w:pPr><w:r><w:t>Criterios de aceptación propuestos para HU08</w:t>',
    '<w:pStyle w:val="Ttulo4"/></w:pPr><w:r><w:t>Criterios de aceptación de HU08</w:t>', raw=True)
rep('<w:pStyle w:val="Ttulo3"/></w:pPr><w:r><w:t>Historias complementarias HU09–HU12 y criterios propuestos</w:t>',
    '<w:pStyle w:val="Ttulo4"/></w:pPr><w:r><w:t>Criterios de aceptación de HU09 a HU12</w:t>', raw=True)
for t in ("HU09 – Consentimiento informado", "HU10 – Solicitudes y derechos de titulares", "HU11 – Bitácora de auditoría", "HU12 – Revisión profesional"):
    s_, e_ = para_bounds(t); seg = x[s_:e_]; assert '<w:pStyle w:val="Ttulo4"/>' in seg, t
    x = x[:s_] + seg.replace('<w:pStyle w:val="Ttulo4"/>', '<w:pStyle w:val="Ttulo5"/>') + x[e_:]
insert_before_para("Criterios de aceptación de HU08", R(C.CRIT_INTRO))
replace_para("Estado de los criterios: propuestos, pendientes de verificación. No se cierran criterios de aceptación en esta versión.", R(C.VERIF + C.RF))
x = L.insert_after_bookmark(x, "_Toc177988457", R(C.RESTRIC))

# Capítulo V: K5
s_, e_ = para_bounds("Precisión de triage/análisis automatizado")
x = x[:s_] + L.para("• Desempeño del modelo de análisis automatizado (K5): exactitud del resultado automatizado respecto de la validación médica igual o superior a 0,85, calculada por versión del modelo con al menos 30 imágenes evaluables; no constituye desempeño demostrado.") + x[e_:]

# Capítulo XI: correspondencia con el capítulo V
s_, e_ = para_bounds("La correspondencia con las metas del capítulo V es la siguiente")
x = x[:s_] + L.para("La correspondencia con las metas del capítulo V es la siguiente: disponibilidad (K3), tiempo de triage (K1), tiempo de respuesta (K2), desempeño del modelo (K5), satisfacción (K7), cumplimiento de hitos (K10) y protección de datos (K8). Para K5 se adopta la definición que calcula la plataforma: exactitud respecto de la validación médica, con meta de 0,85 y muestra mínima de 30 imágenes evaluables. El criterio de la Unidad 2 (AUC y sensibilidad iguales o superiores a 0,80) se conserva como referencia para evaluar el modelo en su entrenamiento (capítulo X). Las metas de adopción a seis meses y de desviación presupuestaria del capítulo V no tienen un indicador en la plataforma y se miden fuera de ella.") + x[e_:]

# Capítulo XII: RF09 en la matriz de trazabilidad
rep("Derechos de titulares de datos (sin RF asignado)", "Gestión de derechos de titulares de datos")
i = x.find(escape("Gestión de derechos de titulares de datos")); s_ = x.rfind("<w:tr>", 0, i)
row = x[s_:x.find("</w:tr>", i) + 7]; assert row.count(">—</w:t>") >= 1
x = x.replace(row, row.replace(">—</w:t>", ">RF09</w:t>", 1))
rep("La historia HU10 no tiene un requisito funcional asignado en la especificación original, por lo que su incorporación como requisito queda pendiente de formalizar.",
    "La historia HU10 se vincula con el requerimiento RF09, agregado en este informe.")

# Capítulo XIV: presupuesto vigente
rep("primero corresponde a la fase de prototipo académico: su presupuesto estimado y el costo efectivo", "primero corresponde a la fase de prototipo académico: su presupuesto vigente y el costo efectivo")
rep("El presupuesto del prototipo académico se estimó en la Unidad 2 en $47.074.638 para los ocho meses del proyecto, de forma ascendente a partir del presupuesto de la asignatura de Gestión de Proyectos (Equipo Proyecto Aurora, 2026b).",
    "El presupuesto vigente del prototipo académico asciende a $47.074.638 para los ocho meses del proyecto. Fue elaborado en la Unidad 2 de forma ascendente a partir del presupuesto de la asignatura de Gestión de Proyectos (Equipo Proyecto Aurora, 2026b).")
rep("Presupuesto estimado del prototipo por partida", "Presupuesto vigente del prototipo por partida")

# Control de integración
x = L.set_control_row(x, "I. Introducción", "Redactada en v0.12, con resumen, abstract y palabras clave.", "Revisar con el equipo antes de la entrega.")
x = L.set_control_row(x, "III. Levantamiento de requerimientos",
    "Actualizado en v0.12: criterios de HU01–HU07 (formulación inicial), verificación de HU01–HU12 con pruebas, RF01–RF09 (RF08 actualizado, RF09 nuevo), RNF01–RNF05 y restricciones.",
    "Pendiente: confirmar CU18 y los casos de prueba nuevos; HU06/HU07 con verificación parcial de interfaz.")
x = L.set_control_row(x, "V. Objetivos del proyecto",
    "Sección redactada; K5 alineado con la plataforma en v0.12.",
    "Pendiente: matriz de interesados aprobada (no disponible).")
x = L.set_control_row(x, "XIV. Factibilidad económica",
    "Presupuesto vigente confirmado por el usuario (v0.12); costo real de la demostración; flujo de caja verificado.",
    "Pendiente: costo del dominio; licencia comercial de YOLO.")
x = L.set_control_version(x, "0.12", "23-11-2026")
x, nums = L.renumerar(x)
open(p, "w", encoding="utf-8").write(x)
print("ok", {k[7:]: v for k, v in nums.items() if k[7:] in ("crit_hu", "verif", "rf", "rnf")})
