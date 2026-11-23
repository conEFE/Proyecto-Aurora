# -*- coding: utf-8 -*-
"""Actualiza el registro de revisiones (v0.8) con el trabajo del capítulo VI."""
import sys, re
from xml.sax.saxutils import escape
p = sys.argv[1] + "/word/document.xml"
x = open(p, encoding="utf-8").read()
RPR = '<w:rPr><w:rFonts w:ascii="Arial" w:hAnsi="Arial"/><w:sz w:val="16"/></w:rPr>'

def rep1(a, b):
    global x
    assert x.count(a) == 1, (a[:80], x.count(a))
    x = x.replace(a, b)

# 1. Encabezado de versión
rep1("Documento de control de observaciones, acciones y estados | Versión 0.6",
     "Documento de control de observaciones, acciones y estados | Versión 0.8 (23-11-2026)")

# 2. Filas U1-07 y U1-08 del registro maestro
def set_row(rid, values):
    """values: dict índice_columna -> texto"""
    global x
    i = x.find("<w:t>%s</w:t>" % rid); assert i > 0
    s = x.rfind("<w:tr>", 0, i); e = x.find("</w:tr>", i) + 7
    row = x[s:e]
    cells = re.findall(r"<w:tc>.*?</w:tc>", row)
    assert len(cells) == 9, (rid, len(cells))
    for k, v in values.items():
        c = cells[k]
        para = re.search(r"<w:p>.*</w:p>", c).group(0)
        newp = "<w:p><w:r>%s<w:t>%s</w:t></w:r></w:p>" % (RPR, escape(v))
        cells[k] = c.replace(para, newp)
    head = row[:row.find("<w:tc>")]
    x = x[:s] + head + "".join(cells) + "</w:tr>" + x[e:]

set_row("U1-07", {5: "Equipo", 6: "En curso",
    7: "Maestro v0.4, cap. VI 6.1 (Tablas 1 y 2): comparación cualitativa y ponderada con referencias (Scrumban 4,55; Scrum 3,80; Kanban 3,50), tomada de Unidad 2. Pendiente revisión del equipo para cerrar."})
set_row("U1-08", {5: "Equipo", 6: "En curso",
    7: "Maestro v0.4, cap. VI 6.2 (Tabla 5, Figura 1) y 6.4. Detalle de sprints incorporado; ruta crítica y estado real se derivan al cap. XV; presupuesto al cap. XIV; se elimina la remisión a un anexo inexistente."})

# 3. Historial de versiones: agregar filas
def vrow(vals):
    return "<w:tr>" + "".join('<w:tc><w:tcPr><w:tcW w:type="dxa" w:w="2045"/></w:tcPr><w:p><w:r>%s<w:t>%s</w:t></w:r></w:p></w:tc>' % (RPR, escape(v)) for v in vals) + "</w:tr>"
i = x.find("4. Historial de versiones del informe"); t_end = x.find("</w:tbl>", i)
new_rows = vrow(["0.3+", "23-11-2026", "Informe maestro", "Incorporación de HU09–HU12 con prioridades aprobadas y redacción inicial de los capítulos IV y V.", "Registro retroactivo: esta iteración no tenía entrada propia en el historial (ver secciones 4.2 y 4.3)."]) + \
    vrow(["0.4", "23-11-2026", "Informe maestro", "Redacción inicial del capítulo VI (6.1–6.4): Scrumban como evolución del enfoque híbrido, comparación ponderada, línea base del cronograma con figura regenerada, roles, matriz RACI actualizada y plan de recursos. Corrección de la tabla «Control de integración» (filas III, VI, VII y VIII).", "Decisiones D-06-01 a D-06-04. Respaldo previo: Proyecto_Aurora_Informe_Final_Maestro_v0.3_pre-capVI.docx."]) + \
    vrow(["0.8", "23-11-2026", "Registro de revisiones", "Sección 4.4 con decisiones y observaciones N-06-01 a N-06-14; actualización de U1-07 y U1-08; encabezado normalizado.", "El cuerpo del registro mencionaba v0.7 y el encabezado v0.6; se adopta v0.8 para esta versión."])
x = x[:t_end] + new_rows + x[t_end:]

# 4. Nueva sección al final
def P(t): return "<w:p><w:r><w:t xml:space=\"preserve\">%s</w:t></w:r></w:p>" % escape(t)
def H(t, lvl): return '<w:p><w:pPr><w:pStyle w:val="Heading%d"/></w:pPr><w:r><w:t>%s</w:t></w:r></w:p>' % (lvl, escape(t))
def LB(t): return '<w:p><w:pPr><w:pStyle w:val="ListBullet"/></w:pPr><w:r><w:t xml:space="preserve">%s</w:t></w:r></w:p>' % escape(t)
def TABLE(widths, rows):
    out = ['<w:tbl><w:tblPr><w:tblStyle w:val="TableGrid"/><w:tblW w:type="dxa" w:w="%d"/><w:tblLayout w:type="fixed"/><w:tblLook w:firstColumn="1" w:firstRow="1" w:lastColumn="0" w:lastRow="0" w:noHBand="0" w:noVBand="1" w:val="04A0"/></w:tblPr><w:tblGrid>%s</w:tblGrid>'
           % (sum(widths), "".join('<w:gridCol w:w="%d"/>' % w for w in widths))]
    for ri, r in enumerate(rows):
        b = "<w:b/>" if ri == 0 else ""
        rpr = '<w:rPr><w:rFonts w:ascii="Arial" w:hAnsi="Arial"/>%s<w:sz w:val="16"/></w:rPr>' % b
        tr = '<w:trPr><w:tblHeader/></w:trPr>' if ri == 0 else ''
        shd = '<w:shd w:val="clear" w:color="auto" w:fill="D9EAF7"/>' if ri == 0 else ''
        out.append("<w:tr>%s%s</w:tr>" % (tr, "".join('<w:tc><w:tcPr><w:tcW w:type="dxa" w:w="%d"/>%s</w:tcPr><w:p><w:r>%s<w:t xml:space="preserve">%s</w:t></w:r></w:p></w:tc>' % (w, shd, rpr, escape(c)) for w, c in zip(widths, r))))
    out.append("</w:tbl>")
    return "".join(out)

sec = []
sec.append(H("4.4. Capítulo VI – Metodología de Trabajo", 3))
sec.append(P("Fecha: 23-11-2026. Fuentes contrastadas: formulación inicial de Unidad 1 (Campos_Meneses_Neira.docx; cap. 6, Figura 3 Cronograma y Figura 4 Matriz RACI), informe de Unidad 2 (Neira_Campos_Meneses.docx; sección «Metodología de trabajo: Scrumban», Tablas 7–11, cap. VII Tablas 51–53 y Figura 11 con corte al 18-10-2026, Tablas 13, 14, 55 y 56) y documentación del repositorio (docs/CHANGELOG_SPRINTS.md, docs/ESTADO_AWS.md, docs/guia_modelo_juan.md e historial de Git). No se recibieron en esta sesión README_CONTINUACION.md, la plantilla institucional, «proyecto de titulo con correcciones.docx» ni «TIHI84_ES2_Informe_Arquitectura_ProyectoAurora_AVANCE.docx»."))
sec.append(P("Antes de redactar se informaron al usuario las contradicciones detectadas. El usuario adoptó las siguientes decisiones:"))
sec.append(TABLE([1000, 3400, 5824], [
    ["ID", "Tema", "Decisión aprobada por el usuario (23-11-2026)"],
    ["D-06-01", "Metodología", "Presentar Scrumban como metodología vigente y como evolución del enfoque híbrido (predictivo + Scrum) de Unidad 1, corrigiendo la afirmación de que los pesos provienen de Unidad 1 y sin declarar métricas de flujo como medidas."],
    ["D-06-02", "Cronograma", "El capítulo VI presenta la línea base planificada (11-04-2026 a 10-12-2026). Estado real, desviaciones, hitos de control posteriores y ruta crítica se tratan en el capítulo XV."],
    ["D-06-03", "Responsable del modelo de IA", "Juan Francisco Meneses desarrolla y entrena el modelo y su servicio de inferencia; Felipe Campos lo integra en el backend (proveedor HTTP, persistencia y validación médica)."],
    ["D-06-04", "Matriz RACI", "Actualizar la RACI con los roles de Unidad 2: «Patrocinador/Cliente» pasa a «Institución de referencia (sin compromiso formal)»; se retira «Validación con Focus Group»; QA a cargo del equipo de desarrollo con Felipe Campos como responsable principal; se deja nota de que es una actualización."]]))
sec.append(P("Observaciones registradas durante el contraste:"))
sec.append(TABLE([900, 1300, 4424, 2400, 1200], [
    ["ID", "Capítulo", "Observación", "Acción", "Estado"],
    ["N-06-01", "VI.6.1", "Unidad 1 adopta enfoque híbrido predictivo + Scrum; Unidad 2 lo cambia a Scrumban sin explicitar la transición.", "Redactado como evolución metodológica (D-06-01).", "Resuelto en v0.4; sujeto a revisión del equipo"],
    ["N-06-02", "VI.6.1", "Unidad 2 (Tabla 10) declara que «los pesos de los criterios se mantienen de la Unidad 1», pero la comparación de Unidad 1 es cualitativa, con siete criterios distintos y sin pesos.", "Se atribuyen criterios y pesos a la revisión de Unidad 2 y se aclara que son juicio del equipo.", "Resuelto en v0.4"],
    ["N-06-03", "VI.6.1 / XV", "Unidad 2 indica medición de métricas de flujo (lead time, cycle time, throughput) desde el 16-10-2026 en GitHub Projects; no se dispone de los registros.", "Presentadas como metas de control, sin resultados. Obtener exportación del tablero si se quieren informar valores.", "Pendiente"],
    ["N-06-04", "VI.6.2 / XV", "No existe Carta Gantt posterior al corte del 18-10-2026. El repositorio documenta cierre del Sprint 7 y primer despliegue en AWS alrededor del 10/11-11-2026 (línea base: 31-10) y Sprint 8 (parte 1) el 10-11-2026. Los commits rotulados sprint-1 a sprint-6 tienen fecha 07-10-2026, por lo que Git no permite fechar el cierre real de cada sprint. Sin evidencia de: firma de propuesta de SLA (31-10), decisión sobre el modelo según criterio AUC/sensibilidad (01-11), capacitación, validación clínica (16–20-11), aceptación del MVP (24-11) ni piloto.", "Obtener del equipo el estado aprobado al 23-11-2026 antes de redactar el capítulo XV. No presentar el corte del 18-10 como estado vigente.", "Pendiente"],
    ["N-06-05", "VI.6.2", "La figura de cronograma de Unidad 1 (y la imagen adjunta en la sesión) presenta las barras de las fases 4 y 5 desplazadas una fila respecto de sus etiquetas.", "Figura regenerada a partir de las fechas de la tabla de Unidad 1 (Figura 1 del maestro).", "Resuelto en v0.4"],
    ["N-06-06", "VI.6.3", "Atribución contradictoria del modelo de IA: tabla de equipo de Unidad 1 (Juan Francisco), RACI de Unidad 1 y Tabla 52 de Unidad 2 (Felipe), repositorio («modelo de Juan»).", "Aplicada D-06-03.", "Resuelto en v0.4"],
    ["N-06-07", "VI.6.3", "RACI de Unidad 1: columna «Patrocinador/Cliente» incompatible con la ausencia de compromiso formal; actividad «Validación con Focus Group» sin respaldo en cronogramas ni registros; «Pruebas del prototipo» A/R a F. Neira, mientras Unidad 2 asigna QA a F. Campos.", "Aplicada D-06-04. Confirmar la matriz con el equipo.", "En curso"],
    ["N-06-08", "VI.6.3 / 6.4", "Unidad 1 contempla apoyo especializado de QA; no hay registro de su incorporación efectiva.", "Redactado como recurso contemplado no registrado. Confirmar con el equipo.", "Pendiente"],
    ["N-06-09", "VI.6.4 / XIV", "El anexo de presupuesto citado en Unidad 1 no existe (el anexo solo contiene la matriz de riesgos). Unidad 2 informa $47.074.638 CLP y una infraestructura de piloto de USD 241,09 al mes en sa-east-1 (t3.large, RDS db.t3.medium); el repositorio documenta para la demostración us-east-2, plan gratuito con créditos, EC2 t4g.micro y RDS db.t4g.micro, con costo estimado ≈ USD 26 al mes (ESTADO_AWS.md, 16-11-2026), y el modelo en un equipo con GPU vía Tailscale.", "El capítulo VI describe recursos por categoría y remite cifras al XIV. Conciliar presupuesto prototipo, piloto y demostración en el XIV con fecha de corte.", "Pendiente"],
    ["N-06-10", "XVII", "Clave bibliográfica del propio informe de Unidad 2 no definida. Además, «Equipo Proyecto Aurora (2026b)» se describe distinto en Unidad 1 («Evaluación 2 de Gestión de Proyectos…») y en Unidad 2 («Informe 4 – Gestión de Proyectos…»).", "En el maestro se cita como «informe de Unidad 2 del proyecto» sin clave inventada. Normalizar en el capítulo XVII.", "Pendiente"],
    ["N-06-11", "Formato", "Las tablas de los capítulos III–V no tienen leyenda numerada; el capítulo VI usa campos SEQ y referencias cruzadas REF, por lo que inicia en Tabla 1. Los índices (TDC, tablas, figuras) no se actualizaron automáticamente.", "Al agregar leyendas en capítulos previos, actualizar campos en Word (Ctrl+A, F9).", "Pendiente"],
    ["N-06-12", "Registro", "Inconsistencias de control: encabezado v0.6 frente a «v0.7» en el cuerpo; identificadores N-03-16 a N-03-21 usados para dos conjuntos de observaciones distintos; filas vacías en la sección 3; dos secciones numeradas «4».", "Encabezado normalizado a v0.8. Renumerar los duplicados (propuesta: segundo conjunto como N-03-22 a N-03-27) requiere aprobación, pues altera referencias históricas.", "Pendiente de aprobación"],
    ["N-06-13", "Maestro – control", "En la tabla «Control de integración» las filas VI–VIII repetían el texto de la fila V («Sección redactada…») y la fila III indicaba prioridades HU09–HU12 por definir.", "Filas corregidas en v0.4.", "Resuelto en v0.4"],
    ["N-06-14", "Continuidad", "Archivos del paquete de continuidad no recibidos en la sesión: README_CONTINUACION.md, plantilla institucional, «proyecto de titulo con correcciones.docx» y «TIHI84_ES2_…_AVANCE.docx».", "Solicitar para contraste de estructura (plantilla) y del capítulo VII en adelante.", "Pendiente"]]))
sec.append(P("Alcance de la verificación: el capítulo VI se redactó con información documental de Unidad 1, Unidad 2 y del repositorio. No se verificaron registros del tablero de GitHub Projects ni actas de ceremonias Scrum/Scrumban; las métricas de flujo y la RACI se presentan como planificación y asignación de responsabilidades, no como desempeño medido."))
sec.append(P("Pendiente: confirmar con el equipo la RACI y la asignación del modelo; obtener estado del cronograma al 23-11-2026 para el capítulo XV; conciliar presupuesto en el capítulo XIV. El próximo capítulo a desarrollar es el VII – Definición de Arquitectura TI."))

k = x.rfind("<w:sectPr")
x = x[:k] + "".join(sec) + x[k:]
open(p, "w", encoding="utf-8").write(x)
print("ok")
