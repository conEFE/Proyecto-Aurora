# -*- coding: utf-8 -*-
"""Presentación de defensa del informe final (pauta de la comisión) sobre la estética de la presentación de la U2.
Requiere base2.pptx (diapositivas de la U2 ya duplicadas y ordenadas) y las capturas cap_*.png."""
import re
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN

exec(open("lib2.py", encoding="utf-8").read())

FIG = "/home/user/Proyecto-Aurora/docs/informe_final/figuras/"
RED, GRAY, PINK, TXT = RGBColor(0xC0, 0, 0), RGBColor(0xF2, 0xF2, 0xF2), RGBColor(0xFB, 0xED, 0xED), RGBColor(0x53, 0x53, 0x53)


def front(slide, *sids):
    for sid in sids:
        e = sh(slide, sid)._element; t = e.getparent(); t.remove(e); t.append(e)


def card(slide, x, y, w, h, title, lines, strong=False, name="Tarjeta"):
    box = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
    box.name = name
    box.fill.solid(); box.fill.fore_color.rgb = PINK if strong else GRAY
    box.line.fill.background(); box.shadow.inherit = False
    tf = box.text_frame; tf.word_wrap = True; tf.vertical_anchor = MSO_ANCHOR.TOP
    for side in ("left", "right"):
        setattr(tf, "margin_" + side, Inches(0.22))
    tf.margin_top = Inches(0.2); tf.margin_bottom = Inches(0.1)
    p = tf.paragraphs[0]; p.alignment = PP_ALIGN.LEFT; r = p.add_run(); r.text = title
    r.font.bold = True; r.font.size = Pt(28); r.font.color.rgb = RED
    p.space_after = Pt(8)
    for ln in lines:
        q = tf.add_paragraph(); q.space_after = Pt(6); q.alignment = PP_ALIGN.LEFT
        rr = q.add_run(); rr.text = ln; rr.font.size = Pt(23); rr.font.color.rgb = TXT
    return box


def textbox(slide, x, y, w, h, text, size=16, color=TXT, italic=False):
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame; tf.word_wrap = True
    for side in ("left", "right", "top", "bottom"):
        setattr(tf, "margin_" + side, 0)
    r = tf.paragraphs[0].add_run(); r.text = text; r.font.size = Pt(size); r.font.color.rgb = color; r.font.italic = italic
    return tb


def recolor_tag(slide, sid, fill, text):
    e = sh(slide, sid)._element
    xml_cols = e.findall(".//" + qn("a:srgbClr"))
    if len(xml_cols) >= 2:
        xml_cols[0].set("val", fill); xml_cols[1].set("val", text)


# ================================================================ PRINCIPAL
# ---- 0. Portada
s = SL[0]
set_text(sh(s, 174), "Informe final")
notes(s, "(15 s) Presentamos Proyecto Aurora: una plataforma web que apoya la detección temprana y la priorización de casos sospechosos de cáncer de mama. Apoya, no reemplaza, el criterio médico.")

# ---- 1. Identificación del problema
s = SL[1]
set_text(sh(s, 2), "Problema"); set_text(sh(s, 3), "Identificación del problema")
move(s, 13, left=2.08); move(s, 9, left=10.18); move(s, 5, left=18.27); front(s, 13, 9, 5)
set_text(sh(s, 6), "NECESIDAD")
set_text(sh(s, 7), ["La gestión inicial de un caso sospechoso reúne antecedentes, imágenes y plazos",
                    "Priorizar exige criterios explícitos y trazables, separados del diagnóstico",
                    "Son datos de salud sensibles: consentimiento, roles y bitácora"])
set_text(sh(s, 10), "IMPACTO")
set_text(sh(s, 11), ["5.141 casos nuevos y 1.829 muertes al año en Chile (GLOBOCAN 2024)",
                     "Las garantías GES fijan plazos máximos de diagnóstico y tratamiento",
                     "Detectar y priorizar a tiempo cambia el pronóstico"])
set_text(sh(s, 14), "SOLUCIÓN PROPUESTA")
set_text(sh(s, 15), ["Plataforma web que gestiona el caso del registro al reporte firmado",
                     "Triage automático con reglas que configuran los médicos",
                     "IA como insumo: el médico revisa, valida y decide"])
set_text(sh(s, 16), "Aurora ordena y prioriza los casos; la decisión clínica sigue siendo del médico.")
notes(s, "(60 s) La necesidad: la gestión inicial de un caso sospechoso reúne antecedentes, imágenes y plazos, y priorizar exige criterios explícitos y trazables. El impacto: en Chile hay más de cinco mil casos nuevos al año y las garantías GES fijan plazos máximos, por lo que priorizar a tiempo importa. La solución: una plataforma web que gestiona el caso completo, calcula un triage con reglas que configuran los médicos y usa la IA solo como un insumo más.")

# ---- 2. Modelo CANVAS
s = SL[2]
set_text(sh(s, 2), "Modelo de negocio"); set_text(sh(s, 3), "Modelo de negocio CANVAS")
delete(s, *range(4, 17))
W, G, X0, Y0, HT, HB = 4.57, 0.2, 1.5, 2.85, 6.9, 2.75
col = lambda i: X0 + i * (W + G)
half = (HT - G) / 2
card(s, col(0), Y0, W, HT, "SOCIOS CLAVE", ["AWS: infraestructura en la nube", "Institución de referencia y su red de clínicas (sin acuerdo formal)", "Médicos revisores: validan el triage y el modelo", "Datos públicos CBIS-DDSM y CMMD"], strong=True)
card(s, col(1), Y0, W, half, "ACTIVIDADES CLAVE", ["Desarrollo y mantención", "Implementación y soporte", "Validación del modelo"])
card(s, col(1), Y0 + half + G, W, half, "RECURSOS CLAVE", ["Plataforma y modelo propios", "Equipo de tres personas", "Infraestructura en AWS"])
card(s, col(2), Y0, W, HT, "PROPUESTA DE VALOR", ["Gestión del caso completo y priorización configurable", "IA como insumo, validada por el médico imagen por imagen", "Solo navegador: sin integrar HIS, RIS ni PACS", "Trazabilidad y derechos de los titulares (Ley 21.719)"], strong=True)
card(s, col(3), Y0, W, half, "RELACIÓN", ["Soporte L–V 08–20 h con niveles de servicio", "Triage ajustado con los médicos"])
card(s, col(3), Y0 + half + G, W, half, "CANALES", ["Venta directa, partiendo por la red de la institución de referencia", "Servicio web (SaaS)"])
card(s, col(4), Y0, W, HT, "SEGMENTOS", ["Clínicas privadas medianas con imagenología (RM, Valparaíso y Biobío)", "Centros de diagnóstico mamario y oncológicos", "Mercado disponible: 121 instituciones privadas"], strong=True)
wb = (5 * W + 4 * G - G) / 2
card(s, X0, Y0 + HT + G, wb, HB, "ESTRUCTURA DE COSTOS", ["Inversión inicial de $70 M · prototipo de $47,1 M (8 meses)", "Remuneraciones, licencias, nube (≈ USD 26/mes la demostración) y soporte"], strong=True)
card(s, X0 + wb + G, Y0 + HT + G, wb, HB, "FUENTES DE INGRESOS", ["Suscripción de $1.200.000 al mes por establecimiento", "De 5 clientes ($72 M) en el año 1 a 26 ($374,4 M) en el año 5"], strong=True)
textbox(s, X0, Y0 + HT + G + HB + 0.12, 23.66, 0.5, "Elaborado con los datos del informe: mercado, costos y flujo de caja (cap. XIV) y diferenciación (cap. IV). Destacados: los cinco elementos fundamentales.", size=18)
notes(s, "(75 s) Los cinco elementos fundamentales están destacados. Segmentos: clínicas privadas medianas con imagenología, centros de diagnóstico mamario y oncológicos; el mercado disponible son 121 instituciones privadas. Propuesta de valor: gestionar el caso completo con una priorización que configuran los médicos, sin integraciones previas. Socios clave: AWS, la institución de referencia y su red, aún sin acuerdo formal, y médicos revisores. Ingresos: una suscripción de 1,2 millones al mes por establecimiento, de 5 a 26 clientes en cinco años. Costos: una inversión de 70 millones; el prototipo costó 47 millones en ocho meses.")

# ---- 3. Tecnologías seleccionadas
s = SL[3]
set_text(sh(s, 3), "Tecnologías seleccionadas")
set_text(sh(s, 14), "PostgreSQL 16 (Amazon RDS) · imágenes cifradas con Fernet en S3")
set_text(sh(s, 18), "PyTorch: CNN ResNet18 · Ultralytics YOLO11s")
set_text(sh(s, 19), "PROTOTIPO")
set_text(sh(s, 22), "Docker · GitHub Actions · AWS · Caddy · Tailscale")
set_text(sh(s, 23), "EN USO"); recolor_tag(s, 23, "2E8B57", "FFFFFF")
set_text(sh(s, 29), "Servicios: GitHub Team, Figma y Microsoft 365; AWS con plan gratuito y créditos")
notes(s, "(40 s) Interfaz en React con TypeScript; API en FastAPI con SQLAlchemy y Alembic; datos en PostgreSQL sobre Amazon RDS e imágenes cifradas en S3. La IA usa PyTorch con una CNN ResNet18 y YOLO11s, como prototipo. Se despliega con Docker y GitHub Actions en AWS, con Caddy para HTTPS y Tailscale para llegar al equipo con GPU. Todo el software base es de código abierto.")

# ---- 4. Evaluación y selección tecnológica
s = SL[4]
set_text(sh(s, 3), "Evaluación y selección tecnológica")
set_text(sh(s, 4), "CUANTITATIVA: CRITERIOS Y PESOS (AHP)")
set_text(sh(s, 29), ["CUALITATIVA: EL CASO DE LA API",
                     "FastAPI y Django REST empatan con pesos iguales; se eligió FastAPI por su modelo asíncrono, la validación con Pydantic y la documentación automática."])
notes(s, "(50 s) Ejemplo cuantitativo: una matriz ponderada con cinco criterios; los pesos salen de una comparación por pares (AHP) con razón de consistencia 0,013, bajo el límite de 0,10. Cada alternativa se puntuó de 1 a 5 con una escala anclada. Ejemplo cualitativo: en la API, FastAPI y Django REST empatan con pesos iguales; elegimos FastAPI por su modelo asíncrono, la validación con Pydantic y la documentación automática.")

# ---- 5. Casos de uso principales
s = SL[5]
set_text(sh(s, 2), "Casos de uso"); set_text(sh(s, 3), "Casos de uso principales")
put_image(s, 5, FIG + "cap10_casos_uso.png")
set_text(sh(s, 7), ["CUATRO ROLES, MÍNIMO PRIVILEGIO", "Administrativo: pacientes, casos e imágenes", "Médico: triage, revisión, validación y firma",
                    "Administrador: usuarios · Jefatura: indicadores"])
set_text(sh(s, 19), ["RF02 pacientes: CU04 · RF04 exámenes: CU06 · RF05 triage: CU08–CU10",
                     "RF06 reporte firmado: CU12 y CU16 · RF08 IA: CU07 y CU15",
                     "RF07 indicadores: CU14 y CU19 · RF01 acceso: CU01, CU02 y CU20"])
notes(s, "(60 s) Son 20 casos de uso y cuatro actores con mínimo privilegio. La cadena principal responde al problema: cargar un examen (CU06) desencadena el análisis (CU07) y el triage (CU08), y el caso aparece ordenado en la cola (CU09). El médico revisa, valida la IA y firma el reporte. Cada caso de uso se traza a un requerimiento: por ejemplo, RF05 triage con CU08 a CU10 y RF06 reporte firmado con CU12 y CU16.")

# ---- 6. Arquitectura e infraestructura
s = SL[6]
set_text(sh(s, 3), "Arquitectura e infraestructura")
put_image(s, 5, FIG + "it15_cloud.png")
set_text(sh(s, 7), ["AWS · US-EAST-2 (OHIO)", "EC2 con contenedores · RDS PostgreSQL privado y cifrado · S3 cifrado · Route 53 · CloudWatch"])
set_text(sh(s, 8), "COMPONENTES Y CONTINUIDAD")
set_text(sh(s, 11), "Caddy: HTTPS y proxy inverso hacia la API")
set_text(sh(s, 14), "Respaldo diario de la base en S3; restauración probada")
set_text(sh(s, 17), "Chequeo de /health cada minuto con alarma por correo")
set_text(sh(s, 20), "Modelo en PC con GPU por Tailscale; respaldo en AWS (2.12.0)")
notes(s, "(60 s) El usuario entra por HTTPS a demo.auroracare.cl, resuelto por Route 53. Un servidor EC2 ejecuta los contenedores: Caddy termina TLS y sirve el sitio, y la API FastAPI atiende las solicitudes. La base PostgreSQL está en RDS, privada y cifrada; las imágenes van cifradas a S3. Hay respaldo diario de la base con restauración probada y un chequeo de disponibilidad cada minuto con alarma por correo. El modelo corre en un equipo con GPU por Tailscale; la versión 2.12.0 agrega un respaldo en AWS.")

# ---- 7. Factibilidad económica
s = SL[7]
set_text(sh(s, 2), "Factibilidad")
set_text(sh(s, 33), ["Recursos humanos, licencias y operación", "$30.353.000"])
set_text(sh(s, 34), ["Contingencia (25%)", "$9.414.928"])
set_text(sh(s, 35), ["Equipamiento", "$4.866.710"])
set_text(sh(s, 36), ["Infraestructura en la nube", "$2.440.000"])
set_text(sh(s, 39), "$47.074.638")
set_text(sh(s, 41), ["SUPUESTOS", "Inversión inicial de $70 M", "Suscripción de $1.200.000 al mes", "De 5 a 26 clientes en 5 años", "VAN positivo con ≥ 75,2% de los clientes"])
set_text(sh(s, 30), "El flujo acumulado se vuelve positivo en el año 3")
notes(s, "(60 s) El prototipo costó 47 millones en ocho meses, la mayor parte en recursos humanos; la demostración en AWS cuesta cerca de 26 dólares al mes. Para la fase comercial, con una inversión de 70 millones y una suscripción de 1,2 millones mensuales, el VAN es de 134,8 millones a una tasa de 14%, la TIR de 45% y la inversión se recupera en 2,84 años. La variable crítica es la demanda: el VAN sigue positivo mientras se capte al menos el 75% de los clientes proyectados.")

# ---- 8. Demostración: guion
s = SL[8]
set_text(sh(s, 2), "Demostración"); set_text(sh(s, 3), "Demostración del software")
set_text(sh(s, 5), ["PASO 1 · ADMINISTRATIVO", "REGISTRO Y CARGA"])
set_text(sh(s, 6), ["CU01 Iniciar sesión", "CU04 Paciente y consentimiento", "CU05 Crear el caso", "CU06 Cargar mamografías"])
set_text(sh(s, 9), ["PASO 2 · AUTOMÁTICO", "ANÁLISIS Y TRIAGE"])
set_text(sh(s, 10), ["CU07 Análisis con IA (prototipo)", "CU08 Cálculo del nivel", "CU09 Cola priorizada", "CU10 Ajuste del nivel con motivo"])
set_text(sh(s, 13), ["PASO 3 · MÉDICO Y GESTIÓN", "REVISIÓN Y REPORTE"])
set_text(sh(s, 14), ["CU11 Revisión del caso", "CU15 Validación de la IA", "CU16 y CU12 Firma y reporte PDF", "CU14 Dashboard · CU19 Comparador"])
set_text(sh(s, 15), "En vivo en demo.auroracare.cl con datos ficticios; si falla la red, se usan las capturas siguientes")
set_text(sh(s, 16), "Cada paso de la demostración corresponde a un caso de uso y a su requerimiento.")
notes(s, "(30 s + demostración en vivo) Guion: como administrativo, ingresar, registrar un paciente con consentimiento, crear el caso y cargar las mamografías. La plataforma analiza las imágenes y calcula el nivel; el caso aparece en la cola. Como médico, revisar el caso, validar el resultado de la IA, ajustar el nivel si corresponde, firmar y descargar el reporte. Cerrar con el dashboard y el comparador de médicos.")

# ---- 9. Capturas (respaldo de la demostración)
s = SL[9]
set_text(sh(s, 2), "Demostración"); set_text(sh(s, 3), "Pantallas principales")
set_text(sh(s, 4), "Datos ficticios · «IA SIMULADA» = resultado sin valor clínico")
for sid, img, cap_sid, cap in [(6, "cap_cola.png", 7, "CU09 · Cola de triage priorizada"),
                               (9, "cap_caso.png", 10, "CU07, CU08 y CU15 · Caso con análisis y validación"),
                               (12, "cap_dash.png", 13, "CU14 · Dashboard de indicadores"),
                               (15, "cap_comp.png", 16, "CU19 · Comparador de médicos")]:
    put_image(s, sid, img, mode="fill"); set_text(sh(s, cap_sid), cap)
notes(s, "(20 s, o en lugar de la demostración en vivo) Cola priorizada por nivel, puntaje y espera; el caso con el análisis, la validación médica y la explicación del nivel; el dashboard de indicadores, y el comparador de médicos para la jefatura.")

# ---- 10. Conclusiones
s = SL[10]
set_text(sh(s, 4), "Aurora es un prototipo funcional, desplegado, probado y declarado con transparencia.")
set_text(sh(s, 7), "Plataformas y metodología elegidas con matrices ponderadas")
set_text(sh(s, 10), "Triage configurable, revisión y firma; la IA es apoyo")
set_text(sh(s, 13), "AUC 0,838 por paciente; sin validación clínica todavía")
set_text(sh(s, 16), "VAN de $134,8 M; el piloto es la prueba clave")
set_text(sh(s, 17), "Próximos pasos: desplegar la 2.12.0, repetir la prueba de carga en AWS, validar el modelo con médicos y formalizar un piloto.")
notes(s, "(30 s) En síntesis: decisiones con criterio, el médico decide, una IA medida y no prometida, y un proyecto viable si se valida la demanda. Próximos pasos: desplegar la 2.12.0, repetir la prueba de carga en AWS, validar el modelo con médicos y formalizar un piloto.")
notes(SL[11], "(5 s) Gracias. Quedamos atentos a sus preguntas.")

# ================================================================ RESPALDO
s = SL[12]
set_text(sh(s, 2), "Diapositivas de respaldo"); set_text(sh(s, 3), "Para profundizar ante las preguntas de la comisión")
notes(s, "Separador: lo que sigue se muestra solo si la comisión pregunta.")

# ---- Requerimientos
s = SL[13]
set_text(sh(s, 2), "Respaldo"); set_text(sh(s, 3), "Levantamiento y análisis de requerimientos")
set_text(sh(s, 4), "12"); set_text(sh(s, 5), "historias de usuario priorizadas con MoSCoW")
set_text(sh(s, 6), "9"); set_text(sh(s, 7), "requerimientos funcionales")
set_text(sh(s, 8), "5"); set_text(sh(s, 9), "requerimientos no funcionales")
set_text(sh(s, 10), "3"); set_text(sh(s, 11), "instrumentos de levantamiento")
set_text(sh(s, 14), ["INSTRUMENTOS", "Revisión bibliográfica y de soluciones existentes, reuniones del equipo y consultas informales con perfiles clínicos (no son validación formal)."])
set_text(sh(s, 17), ["TRAZABILIDAD", "Cada requisito se vincula con historias, casos de uso y casos de prueba (ISO/IEC/IEEE 29148)."])
set_text(sh(s, 19), ["RF05 · Triage", "Prioriza con criterios configurables"])
set_text(sh(s, 20), ["RNF03 · Rendimiento", "p95 ≤ 3 s en registro y consulta"])
set_text(sh(s, 21), ["RNF05 · Trazabilidad", "Bitácora de acciones sobre los casos"])
notes(s, "Se usaron tres instrumentos: revisión bibliográfica y de soluciones existentes, reuniones del equipo y consultas informales con perfiles clínicos, que no constituyen una validación formal. Resultaron 12 historias de usuario priorizadas con MoSCoW, 9 requerimientos funcionales y 5 no funcionales, con criterios de aceptación y trazabilidad hasta los casos de prueba.")

# ---- Objetivos
s = SL[14]
set_text(sh(s, 2), "Respaldo"); set_text(sh(s, 3), "Objetivos del proyecto")
set_text(sh(s, 4), "7 OBJETIVOS ESPECÍFICOS")
objs = [("Arquitectura", "por capas, monolito modular: cumplido"), ("Acceso por rol", "JWT, 4 roles, bloqueo y límites: cumplido"),
        ("Pacientes y casos", "registro, casos e imágenes cifradas: cumplido"), ("Triage", "reglas configurables y revisión médica: cumplido"),
        ("Reportes", "PDF firmado e indicadores: cumplido"), ("Análisis con IA", "documentado y medido; sin validación clínica"),
        ("Seguridad", "cifrado, bitácora y respaldos: cumplido")]
for k, (lab, desc) in enumerate(objs):
    base_id = 6 + 4 * k
    set_text(sh(s, base_id), lab); set_text(sh(s, base_id + 1), str(k + 1)); set_text(sh(s, base_id + 2), desc)
delete(s, *range(33, 44))
move(s, 44, top=3.0, height=10.05); move(s, 45, top=3.25, height=9.6)
set_text(sh(s, 45), ["OBJETIVO GENERAL",
                     "Desarrollar y evaluar un prototipo funcional de una plataforma web que centralice la gestión inicial de pacientes y casos asociados a sospecha de cáncer de mama, incorpore mecanismos de triage para apoyar la priorización y entregue reportes e indicadores de gestión, con controles de acceso y protección de la información, sin sustituir la evaluación del personal médico.",
                     "Al cierre: cumplido en desarrollo y evaluación técnica; la evaluación clínica queda fuera de lo acreditado."])
for k, para in enumerate(sh(s, 45).text_frame.paragraphs):
    for run in para.runs:
        run.font.size = Pt(30 if k == 0 else 27)
    para.space_after = Pt(14)
notes(s, "El objetivo general se cumplió en desarrollo y evaluación técnica: el prototipo está implementado, desplegado y verificado con 340 pruebas. De los siete específicos, el del análisis con IA se cumplió en su alcance, documentar y evaluar técnicamente, sin atribuir validación clínica.")

# ---- Metodología (contenido de la U2, vigente)
s = SL[15]
set_text(sh(s, 2), "Respaldo")
notes(s, "Comparamos Scrumban, Scrum y Kanban con cuatro criterios ponderados; Scrumban obtiene 4,55. A nivel de proyecto mantenemos línea base, hitos y control de cambios; a nivel de ejecución, sprints de dos semanas con un tablero Kanban y límites de trabajo en curso. Cascada se descartó porque supone requisitos estables, algo que no ocurre con un componente de IA.")

# ---- KPI
s = SL[16]
set_text(sh(s, 2), "Respaldo")
set_text(sh(s, 18), ["Desempeño de la IA *", "exactitud ≥ 0,85 (≥ 30 imágenes)"])
set_text(sh(s, 38), "* K4 requiere un piloto; K5 se mide con la validación médica por imagen")
notes(s, "Once indicadores SMART. La plataforma calcula K1, K2, K5, K6 y K11; K3 se mide con el chequeo de disponibilidad desde el 24-11. K5 se define como la exactitud del modelo frente a la validación médica, con meta de 0,85 y al menos 30 imágenes evaluables. Sin piloto no hay medición clínica real de K4 ni de K7.")

# ---- SLA
s = SL[17]
set_text(sh(s, 2), "Respaldo")
set_text(sh(s, 6), ["Institución", "De referencia, sin acuerdo formal"])
set_text(sh(s, 9), ["Vigencia", "Propuesta para un piloto"])
set_text(sh(s, 22), "Propuesta de diseño, no contractual: la firma con la institución, prevista para el 31-10, no se concretó.")
notes(s, "Tres acuerdos de nivel de servicio propuestos: gestión de casos y triage con criticidad alta, y reportes y métricas con criticidad media, todos con 99% de disponibilidad mensual. Son metas de diseño: no hay un acuerdo firmado con una institución.")

# ---- Plan de pruebas
s = SL[18]
set_text(sh(s, 2), "Respaldo"); set_text(sh(s, 3), "Plan de pruebas y calidad")
set_text(sh(s, 4), "31 CASOS DE PRUEBA EN 7 TIPOS")
for desc, num, n, t in [(8, 7, "4", "pytest: reglas, umbrales y pesos"), (12, 11, "12", "casos, IA, comparador y consultas"),
                        (16, 15, "9", "tokens, roles, firma y OWASP ZAP"), (20, 19, "1", "contenedores en GitHub Actions"),
                        (24, 23, "1", "de paciente a reporte firmado"), (28, 27, "2", "PC-01 ejecutada; PC-02 pendiente"),
                        (32, 31, "2", "revisión con 2 médicos y 1 enfermera")]:
    set_text(sh(s, num), n); set_text(sh(s, desc), t)
set_text(sh(s, 33), "340/340"); set_text(sh(s, 34), "pruebas automatizadas aprobadas")
set_text(sh(s, 35), "97%"); set_text(sh(s, 36), "cobertura de código (mínimo 70%)")
set_text(sh(s, 37), "0"); set_text(sh(s, 38), "riesgos altos en el escaneo OWASP ZAP")
set_text(sh(s, 39), "100%"); set_text(sh(s, 40), "restauración de un respaldo verificada")
set_text(sh(s, 43), "Prueba de estrés, escaneo activo autenticado y validación clínica del modelo")
set_text(sh(s, 45), ["NORMAS APLICADAS", "ISO/IEC 25010 y 29119, OWASP Top 10, Ley 21.719 por diseño y datos solo ficticios"])
notes(s, "El plan tiene 31 casos en siete tipos, trazados a los requisitos. Las 340 pruebas automatizadas se aprobaron con 97% de cobertura; el escaneo OWASP ZAP no encontró riesgos altos y se verificó la restauración de un respaldo. Pendientes: prueba de estrés, escaneo activo autenticado y validación clínica del modelo.")

# ---- Rendimiento
s = SL[19]
set_text(sh(s, 2), "Respaldo"); set_text(sh(s, 3), "Rendimiento bajo carga")
set_text(sh(s, 4), "4×"); set_text(sh(s, 5), "capacidad por proceso tras optimizar consultas")
set_text(sh(s, 6), "2,53 s"); set_text(sh(s, 7), "p95 con 100 usuarios en local (meta ≤ 3 s)")
set_text(sh(s, 8), "14,98 s"); set_text(sh(s, 9), "p95 con 100 usuarios en AWS, versión 2.10.2")
set_text(sh(s, 10), "SOLICITUDES POR SEGUNDO, UN PROCESO")
delete(s, 11, 12, 13, 14, 19, 20, 27, 28, 29)
base_y, maxh, maxv = 9.27, 4.9, 94.6
for k, (bar, lab, cat, v, vt, ct) in enumerate([(15, 16, 24, 20.0, "≈ 20", "AWS 2.10.2"), (17, 18, 25, 23.4, "23,4", "Local 2.11.0"), (21, 22, 26, 94.6, "94,6", "Local 2.12.0")]):
    c = 10.9 + 3.0 * k; h = maxh * v / maxv
    move(s, bar, left=c - 0.8, top=base_y - h, width=1.6, height=h)
    move(s, lab, left=c - 0.9, top=base_y - h - 0.6, width=1.8); set_text(sh(s, lab), vt)
    move(s, cat, left=c - 1.4, top=base_y + 0.1, width=2.8); set_text(sh(s, cat), ct)
move(s, 23, left=9.4, width=9.4); move(s, 30, top=10.2)
set_text(sh(s, 30), "AWS: demostración, 24-11. Local: un núcleo, mismos datos, 25-11.")
set_text(sh(s, 32), "DEFECTOS CORREGIDOS")
set_text(sh(s, 33), ["2.10.1", "Bloqueo del pool de conexiones"])
set_text(sh(s, 34), ["2.10.2", "Cola de solicitudes por proceso"])
set_text(sh(s, 35), ["2.12.0", "Listas sin consultas por fila"])
set_text(sh(s, 36), ["Lista de casos", "De 63 a 6 consultas"])
set_text(sh(s, 38), "Errores"); set_text(sh(s, 39), "0")
set_text(sh(s, 41), ["PRÓXIMO PASO", "Desplegar la 2.12.0 y repetir PC-01 en AWS: ahí se decide si se cumple la meta de 3 s."])
notes(s, "La prueba de carga detectó dos bloqueos, corregidos en la 2.10.1 y la 2.10.2. En AWS, con un proceso, la meta de 3 s se cumple hasta 25 usuarios; con 100, el p95 fue de 15 s sin errores. La 2.12.0 cuadruplicó la capacidad de un proceso en local; falta repetir la prueba en AWS.")

# ---- Implementación y puesta en marcha
s = SL[20]
set_text(sh(s, 2), "Respaldo"); set_text(sh(s, 3), "Plan de implementación y puesta en marcha")
set_text(sh(s, 4), "99%"); set_text(sh(s, 5), "meta mensual: como máximo 7,3 h sin servicio no programado")
set_text(sh(s, 6), "1 min"); set_text(sh(s, 7), "chequeo de /health con alarma por correo")
set_text(sh(s, 8), "≈ 3 s"); set_text(sh(s, 9), "restauración completa de un respaldo, ya probada")
set_text(sh(s, 12), ["DNS Y HTTPS", "Route 53 y Caddy con certificado Let's Encrypt"])
set_text(sh(s, 15), ["APLICACIÓN", "Contenedores Docker; despliegue por Session Manager, sin puerto 22"])
set_text(sh(s, 18), ["BASE DE DATOS", "RDS privada y cifrada; volcado diario a S3"])
set_text(sh(s, 21), ["IMÁGENES", "S3 con cifrado en la aplicación y SSE-KMS"])
set_text(sh(s, 24), ["ALARMAS", "/health sin respuesta o EC2 caída: aviso por correo (SNS)"])
set_text(sh(s, 27), ["PUESTA EN MARCHA", "2.11.0 desplegada el 25-11, con respaldo previo de la base"])
set_text(sh(s, 28), "Para un piloto faltan el acuerdo con la institución, la capacitación de usuarios y un monitor externo a AWS.")
notes(s, "La meta de disponibilidad es 99% mensual. Hoy hay un chequeo de /health cada minuto con alarmas por correo, respaldo diario de la base a S3 y una restauración probada que tardó unos 3 segundos. Cada versión se despliega por Session Manager con un respaldo previo. Para un piloto faltan el acuerdo con la institución, la capacitación de usuarios y un monitor externo.")

# ---- Mantención (contenido de la U2, vigente)
s = SL[21]
set_text(sh(s, 2), "Respaldo")
notes(s, "La mantención controla siete elementos de configuración con versiones semánticas, gestiona los cambios con solicitudes en ocho pasos y clasifica los incidentes en cuatro prioridades, con restablecimiento de los críticos en 4 horas. Todo cambio del triage requiere el visto bueno de un médico.")

# ---- Arquitectura por capas
s = SL[22]
set_text(sh(s, 2), "Respaldo")
put_image(s, 5, FIG + "it15_arquitectura.png")
set_text(sh(s, 6), "Capas: usuarios · presentación · lógica · análisis · datos, con operación y seguridad transversales")
set_text(sh(s, 8), ["MONOLITO MODULAR POR CAPAS", "Una API FastAPI con módulos separados; solo la lógica accede a los datos"])
set_text(sh(s, 10), ["LAS HERRAMIENTAS SE COMPLEMENTAN", "React, Caddy, FastAPI, PostgreSQL y S3, con integración continua"])
set_text(sh(s, 12), ["IA DESACOPLADA", "PC con GPU, respaldo en AWS (2.12.0) y, al final, IA simulada marcada"])
notes(s, "Arquitectura por capas implementada como monolito modular. El análisis automatizado está detrás de una interfaz de proveedor: equipo con GPU, respaldo en AWS y, si nada responde, IA simulada marcada.")

# ---- Componente de IA
s = SL[23]
set_text(sh(s, 2), "Respaldo"); set_text(sh(s, 3), "Componente de IA")
set_text(sh(s, 4), "0,838"); set_text(sh(s, 5), "AUC con división por paciente")
set_text(sh(s, 6), "0,849"); set_text(sh(s, 7), "sensibilidad con umbral 0,35")
set_text(sh(s, 8), "2 etapas"); set_text(sh(s, 9), "CNN ResNet18 clasifica; YOLO11s marca masas")
set_text(sh(s, 10), "672×1024"); set_text(sh(s, 11), "píxeles de entrada del modelo reentrenado")
set_text(sh(s, 14), ["PROTOTIPO, NO DIAGNÓSTICO", "Sin validación clínica: el médico valida cada resultado y la plataforma lo mide por versión (K5)."])
set_text(sh(s, 17), ["SIEMPRE HAY RESULTADO", "Si el PC con GPU no responde, usa el respaldo en AWS y luego la IA simulada, marcada como tal."])
set_text(sh(s, 19), ["Datos públicos", "CBIS-DDSM y CMMD"])
set_text(sh(s, 20), ["Especificidad", "0,641 con el mismo umbral"])
set_text(sh(s, 21), ["Uso real", "Requiere validación y licencia de YOLO"])
notes(s, "CNN ResNet18 más YOLO11s. Reentrenado con división por paciente: AUC 0,838, sensibilidad 0,849 y especificidad 0,641 con umbral 0,35, en conjuntos públicos. Sin validación clínica.")

# ---- Factibilidad en cinco dimensiones
s = SL[24]
set_text(sh(s, 2), "Respaldo"); set_text(sh(s, 3), "Factibilidad en cinco dimensiones")
set_text(sh(s, 6), "TÉCNICA Y OPERATIVA")
set_text(sh(s, 7), ["Stack abierto, desplegado y con 340 pruebas", "Flujo en navegador con los roles existentes", "Condición: meta de rendimiento en AWS e inferencia fuera del PC"])
set_text(sh(s, 10), "ECONÓMICA")
set_text(sh(s, 11), ["VAN de $134,8 millones a una tasa de 14%", "TIR de 45,0% y recuperación en 2,84 años", "Condición: captar al menos 75,2% de los clientes proyectados"])
set_text(sh(s, 14), "LEGAL Y AMBIENTAL")
set_text(sh(s, 15), ["Consentimiento versionado, derechos de titulares y bitácora (Ley 21.719)", "Antes de usar datos reales: acuerdo de tratamiento y calificación como dispositivo médico", "Sin servidores propios ni compra de hardware"])
set_text(sh(s, 16), "Factible para la demostración; para operar con pacientes falta validar la demanda y el marco regulatorio.")
notes(s, "Técnica y operativa, económica, legal y ambiental: factible para la demostración, con condiciones para operar con pacientes.")

prs.save("Presentacion_Aurora_Defensa.pptx")
print("ok", len(prs.slides))
