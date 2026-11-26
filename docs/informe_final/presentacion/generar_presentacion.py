# -*- coding: utf-8 -*-
"""Rellena base.pptx (diapositivas de la presentación de la Unidad 2) con el contenido del informe final."""
import copy
from pptx import Presentation
from pptx.util import Inches
from PIL import Image
from pptx.oxml.ns import qn

prs = Presentation("base.pptx")
SL = list(prs.slides)


def sh(slide, sid):
    for s in slide.shapes:
        if s.shape_id == sid:
            return s
    raise KeyError(sid)


def set_text(shape, paras):
    """Reemplaza el texto conservando el formato: el párrafo i usa como molde el párrafo i del original (o el último)."""
    if isinstance(paras, str):
        paras = [paras]
    txBody = shape.text_frame._txBody
    old = txBody.findall(qn("a:p"))
    for p in old:
        txBody.remove(p)
    for i, t in enumerate(paras):
        tpl = copy.deepcopy(old[min(i, len(old) - 1)])
        runs = tpl.findall(qn("a:r"))
        rpr = copy.deepcopy(runs[0].find(qn("a:rPr"))) if runs and runs[0].find(qn("a:rPr")) is not None else None
        for child in list(tpl):
            if child.tag in (qn("a:r"), qn("a:br"), qn("a:fld")):
                tpl.remove(child)
        r = tpl.makeelement(qn("a:r"), {})
        if rpr is not None:
            r.append(rpr)
        tt = r.makeelement(qn("a:t"), {}); tt.text = t; r.append(tt)
        end = tpl.find(qn("a:endParaRPr"))
        if end is not None:
            end.addprevious(r)
        else:
            tpl.append(r)
        txBody.append(tpl)


def delete(slide, *sids):
    for sid in sids:
        e = sh(slide, sid)._element; e.getparent().remove(e)


def put_image(slide, old_sid, path, mode="fit"):
    """Coloca la imagen en el recuadro de la imagen anterior (ajustada o recortada) y elimina la anterior."""
    old = sh(slide, old_sid)
    L, T, W, H = old.left, old.top, old.width, old.height
    w, h = Image.open(path).size
    if mode == "fit":
        k = min(W / w, H / h); nw, nh = int(w * k), int(h * k)
        pic = slide.shapes.add_picture(path, L + (W - nw) // 2, T + (H - nh) // 2, nw, nh)
    else:
        pic = slide.shapes.add_picture(path, L, T, W, H)
    pic.name = old.name
    old._element.addprevious(pic._element)
    old._element.getparent().remove(old._element)
    return pic


def notes(slide, text):
    slide.notes_slide.notes_text_frame.text = text


def move(slide, sid, left=None, top=None, width=None, height=None):
    s = sh(slide, sid)
    if left is not None: s.left = Inches(left)
    if top is not None: s.top = Inches(top)
    if width is not None: s.width = Inches(width)
    if height is not None: s.height = Inches(height)


# ---------------------------------------------------------------- 1. Portada
s = SL[0]
set_text(sh(s, 174), "Informe final")
notes(s, "(20 s) Presentamos el informe final de Proyecto Aurora: una plataforma web que apoya la detección temprana y la priorización de casos sospechosos de cáncer de mama. Apoya, no reemplaza, el criterio médico.")

# ---------------------------------------------------------------- 2. Problema y diferenciación
s = SL[1]
set_text(sh(s, 2), "Introducción"); set_text(sh(s, 3), "¿Qué problema resolvemos?")
move(s, 13, left=2.08); move(s, 5, left=10.18); move(s, 9, left=18.27)  # edificio, código, tendencia
for sid in (13, 5, 9):  # al frente: si no, el fondo de la tarjeta siguiente los tapa
    e = sh(s, sid)._element; tree = e.getparent(); tree.remove(e); tree.append(e)
set_text(sh(s, 6), "EL PROBLEMA")
set_text(sh(s, 7), ["La gestión inicial del caso reúne antecedentes, imágenes y plazos",
                    "Priorizar exige criterios explícitos y trazables",
                    "Datos de salud sensibles: consentimiento, roles y bitácora"])
set_text(sh(s, 10), "LO QUE YA EXISTE")
set_text(sh(s, 11), ["Transpara, Lunit INSIGHT MMG y ProFound AI: IA autorizada que analiza la mamografía",
                     "Apoyan la lectura del radiólogo",
                     "Requieren PACS, DICOM y licencia comercial"])
set_text(sh(s, 14), "LO QUE APORTA AURORA")
set_text(sh(s, 15), ["Gestiona el caso completo, del registro al reporte firmado",
                     "Reglas clínicas configurables; la IA es un insumo más",
                     "Solo navegador: sin integrarse a HIS, RIS ni PACS"])
set_text(sh(s, 16), "La innovación está en el flujo completo, no en el algoritmo: el médico siempre decide.")
notes(s, "(60 s) El problema combina lo clínico, lo tecnológico, lo organizacional y lo normativo. Ya existen productos de IA autorizados, como Transpara, Lunit o ProFound, pero analizan la imagen y necesitan PACS y DICOM. Aurora se diferencia en el flujo: gestiona el caso completo, prioriza con reglas clínicas configurables por los médicos y usa la IA como un insumo más, sin integraciones previas.")

# ---------------------------------------------------------------- 3. Estado al cierre
s = SL[2]
set_text(sh(s, 3), "¿Dónde llegamos?")
set_text(sh(s, 4), "8 de 8"); set_text(sh(s, 5), "sprints cerrados; el 7 con 11 días de desfase")
set_text(sh(s, 6), "340"); set_text(sh(s, 7), "pruebas automatizadas aprobadas (100%)")
set_text(sh(s, 8), "97%"); set_text(sh(s, 9), "cobertura de código del servidor")
set_text(sh(s, 10), "2.11.0"); set_text(sh(s, 11), "publicada en demo.auroracare.cl")
set_text(sh(s, 14), ["MODELO REAL CONECTADO",
                     "CNN y YOLO en el equipo con GPU, por red privada Tailscale. Prototipo sin validación clínica."])
set_text(sh(s, 17), ["DESPLEGADO EN AWS",
                     "Servidor, base de datos e imágenes cifradas en AWS, con respaldos diarios y alarmas por correo."])
notes(s, "(45 s) Cerramos los ocho sprints; el Sprint 7 tuvo un desfase de 11 días. La suite tiene 340 pruebas, todas aprobadas, con 97% de cobertura. La versión 2.11.0 está publicada en demo.auroracare.cl, en AWS, y el modelo real está conectado desde el equipo con GPU como prototipo, sin validación clínica.")

# ---------------------------------------------------------------- 4. Tecnologías (se conserva el contenido de la U2)
s = SL[3]
notes(s, "(45 s) Las plataformas se eligieron con una matriz ponderada; los pesos salen de una comparación por pares (AHP) con razón de consistencia 0,013. React, FastAPI, PostgreSQL, AWS y la familia YOLO ganan en cuatro de cinco componentes con cualquier esquema de pesos. La metodología fue Scrumban: hitos para la institución y flujo ágil para la incertidumbre de la IA.")

# ---------------------------------------------------------------- 5. Procesos y sustentabilidad
s = SL[4]
set_text(sh(s, 2), "Procesos"); set_text(sh(s, 3), "Procesos de negocio y sustentabilidad")
set_text(sh(s, 15), "Carriles por actor: paciente · personal administrativo · médico · sistema Aurora · jefatura")
set_text(sh(s, 16), "Sustentable: stack abierto, cerca de USD 26 al mes y triage que ajustan los médicos sin programar.")
notes(s, "(45 s) La solución sigue tres procesos BPMN: admisión del caso, triage y priorización, y revisión clínica con reporte firmado. Basta cargar un examen para que el caso se analice y se priorice. Es sustentable porque usa los roles existentes, un stack abierto que mantiene un equipo pequeño, cuesta cerca de USD 26 al mes en demostración y los médicos ajustan el triage sin tocar código.")

# ---------------------------------------------------------------- 6. Arquitectura
s = SL[5]
put_image(s, 5, "/home/user/Proyecto-Aurora/docs/informe_final/figuras/it15_arquitectura.png")
set_text(sh(s, 6), "Capas: usuarios · presentación · lógica · análisis · datos, con operación y seguridad transversales")
set_text(sh(s, 8), ["MONOLITO MODULAR POR CAPAS", "Una API FastAPI con módulos separados; solo la lógica accede a los datos"])
set_text(sh(s, 10), ["LAS HERRAMIENTAS SE COMPLEMENTAN", "React, Caddy, FastAPI, PostgreSQL y S3, con integración continua"])
set_text(sh(s, 12), ["IA DESACOPLADA", "PC con GPU, respaldo en AWS (2.12.0) y, al final, IA simulada marcada"])
notes(s, "(60 s) La arquitectura es por capas, implementada como monolito modular. Una solicitud recorre React, Caddy con TLS, la API FastAPI y PostgreSQL en RDS; las imágenes van cifradas a S3. La integración continua prueba y publica cada versión. El análisis automatizado está detrás de una interfaz de proveedor: hoy consulta el equipo con GPU por Tailscale; la versión 2.12.0 agrega un respaldo en AWS y, si nada responde, usa la IA simulada, siempre marcada.")

# ---------------------------------------------------------------- 7. Componente de IA
s = SL[6]
set_text(sh(s, 2), "Arquitectura"); set_text(sh(s, 3), "Componente de IA")
set_text(sh(s, 4), "0,838"); set_text(sh(s, 5), "AUC con división por paciente")
set_text(sh(s, 6), "0,849"); set_text(sh(s, 7), "sensibilidad con umbral 0,35")
set_text(sh(s, 8), "2 etapas"); set_text(sh(s, 9), "CNN ResNet18 clasifica; YOLO11s marca masas")
set_text(sh(s, 10), "672×1024"); set_text(sh(s, 11), "píxeles de entrada del modelo reentrenado")
set_text(sh(s, 14), ["PROTOTIPO, NO DIAGNÓSTICO",
                     "Sin validación clínica: el médico valida cada resultado y la plataforma lo mide por versión (K5)."])
set_text(sh(s, 17), ["SIEMPRE HAY RESULTADO",
                     "Si el PC con GPU no responde, usa el respaldo en AWS y luego la IA simulada, marcada como tal."])
set_text(sh(s, 19), ["Datos públicos", "CBIS-DDSM y CMMD"])
set_text(sh(s, 20), ["Especificidad", "0,641 con el mismo umbral"])
set_text(sh(s, 21), ["Uso real", "Requiere validación y licencia de YOLO"])
notes(s, "(50 s) El modelo tiene dos etapas: una CNN ResNet18 entrega la probabilidad de malignidad y YOLO11s marca masas. Reentrenado con división por paciente, alcanza un AUC de 0,838 y una sensibilidad de 0,849 con umbral 0,35, en conjuntos públicos. No tiene validación clínica: el médico valida cada resultado y la plataforma mide el desempeño por versión.")

# ---------------------------------------------------------------- 8. Calidad
s = SL[7]
set_text(sh(s, 3), "Pruebas y resultados")
set_text(sh(s, 4), "31 CASOS DE PRUEBA EN 7 TIPOS")
rows = [(8, 7, "4", "pytest: reglas, umbrales y pesos"), (12, 11, "12", "casos, IA, comparador y consultas"),
        (16, 15, "9", "tokens, roles, firma y OWASP ZAP"), (20, 19, "1", "contenedores en GitHub Actions"),
        (24, 23, "1", "de paciente a reporte firmado"), (28, 27, "2", "PC-01 ejecutada; PC-02 pendiente"),
        (32, 31, "2", "revisión con 2 médicos y 1 enfermera")]
for desc, num, n, t in rows:
    set_text(sh(s, num), n); set_text(sh(s, desc), t)
set_text(sh(s, 33), "340/340"); set_text(sh(s, 34), "pruebas automatizadas aprobadas")
set_text(sh(s, 35), "97%"); set_text(sh(s, 36), "cobertura de código (mínimo 70%)")
set_text(sh(s, 37), "0"); set_text(sh(s, 38), "riesgos altos en el escaneo OWASP ZAP")
set_text(sh(s, 39), "100%"); set_text(sh(s, 40), "restauración de un respaldo verificada")
set_text(sh(s, 43), "Prueba de estrés, escaneo activo autenticado y validación clínica del modelo")
set_text(sh(s, 45), ["NORMAS APLICADAS", "ISO/IEC 25010 y 29119, OWASP Top 10, Ley 21.719 por diseño y datos solo ficticios"])
notes(s, "(50 s) El plan de pruebas tiene 31 casos en siete tipos, trazados a los requisitos. Las 340 pruebas automatizadas se aprobaron con 97% de cobertura. Un escaneo OWASP ZAP no encontró riesgos altos y se verificó la restauración completa de un respaldo. Quedan pendientes la prueba de estrés, un escaneo activo autenticado y la validación clínica del modelo.")

# ---------------------------------------------------------------- 9. Rendimiento
s = SL[8]
set_text(sh(s, 2), "Calidad"); set_text(sh(s, 3), "Rendimiento bajo carga")
set_text(sh(s, 4), "4×"); set_text(sh(s, 5), "capacidad por proceso tras optimizar consultas")
set_text(sh(s, 6), "2,53 s"); set_text(sh(s, 7), "p95 con 100 usuarios en local (meta ≤ 3 s)")
set_text(sh(s, 8), "14,98 s"); set_text(sh(s, 9), "p95 con 100 usuarios en AWS, versión 2.10.2")
set_text(sh(s, 10), "SOLICITUDES POR SEGUNDO, UN PROCESO")
delete(s, 11, 12, 13, 14, 19, 20, 27, 28, 29)
base, maxh, maxv = 9.27, 4.9, 94.6
bars = [(15, 16, 24, 20.0, "≈ 20", "AWS 2.10.2"), (17, 18, 25, 23.4, "23,4", "Local 2.11.0"), (21, 22, 26, 94.6, "94,6", "Local 2.12.0")]
for k, (bar, lab, cat, v, vt, ct) in enumerate(bars):
    c = 10.9 + 3.0 * k; h = maxh * v / maxv
    move(s, bar, left=c - 0.8, top=base - h, width=1.6, height=h)
    move(s, lab, left=c - 0.9, top=base - h - 0.6, width=1.8)
    set_text(sh(s, lab), vt)
    move(s, cat, left=c - 1.4, top=base + 0.1, width=2.8)
    set_text(sh(s, cat), ct)
move(s, 23, left=9.4, width=9.4)
move(s, 30, top=10.2)
set_text(sh(s, 30), "AWS: demostración, 24-11. Local: un núcleo, mismos datos, 25-11.")
set_text(sh(s, 32), "DEFECTOS CORREGIDOS")
set_text(sh(s, 33), ["2.10.1", "Bloqueo del pool de conexiones"])
set_text(sh(s, 34), ["2.10.2", "Cola de solicitudes por proceso"])
set_text(sh(s, 35), ["2.12.0", "Listas sin consultas por fila"])
set_text(sh(s, 36), ["Lista de casos", "De 63 a 6 consultas"])
set_text(sh(s, 38), "Errores"); set_text(sh(s, 39), "0")
set_text(sh(s, 41), ["PRÓXIMO PASO", "Desplegar la 2.12.0 y repetir PC-01 en AWS: ahí se decide si se cumple la meta de 3 s."])
notes(s, "(60 s) La prueba de carga fue la más útil: detectó dos bloqueos bajo carga, corregidos en la 2.10.1 y la 2.10.2. En AWS, con un proceso, la meta de 3 segundos se cumple hasta 25 usuarios; con 100 el percentil 95 fue de 15 s, sin errores. Optimizamos las consultas en la 2.12.0 y la capacidad de un proceso se cuadruplicó: en local, con 100 usuarios, el p95 bajó a 2,5 s. Lo honesto es decir que falta repetir la prueba en AWS.")

# ---------------------------------------------------------------- 10. Factibilidad
s = SL[9]
set_text(sh(s, 2), "Factibilidad"); set_text(sh(s, 3), "¿Es factible?")
set_text(sh(s, 6), "TÉCNICA Y OPERATIVA")
set_text(sh(s, 7), ["Stack abierto, desplegado y con 340 pruebas", "Flujo en navegador con los roles existentes",
                    "Condición: meta de rendimiento en AWS e inferencia fuera del PC"])
set_text(sh(s, 10), "ECONÓMICA")
set_text(sh(s, 11), ["VAN de $134,8 millones a una tasa de 14%", "TIR de 45,0% y recuperación en 2,84 años",
                     "Condición: captar al menos 75,2% de los clientes proyectados"])
set_text(sh(s, 14), "LEGAL Y AMBIENTAL")
set_text(sh(s, 15), ["Consentimiento versionado, derechos de titulares y bitácora (Ley 21.719)",
                     "Antes de usar datos reales: acuerdo de tratamiento y calificación como dispositivo médico",
                     "Sin servidores propios ni compra de hardware"])
set_text(sh(s, 16), "Factible para la demostración; para operar con pacientes falta validar la demanda y el marco regulatorio.")
notes(s, "(50 s) Evaluamos cinco dimensiones. Técnica y operativa: el prototipo está desplegado y probado, y funciona con los roles existentes. Económica: VAN de 134,8 millones, TIR de 45% y recuperación en 2,84 años, siempre que se capte al menos el 75% de los clientes proyectados. Legal: consentimiento, derechos de titulares y bitácora; antes de usar datos reales falta el acuerdo de tratamiento y la calificación como dispositivo médico. Ambiental: sin servidores propios ni hardware nuevo.")

# ---------------------------------------------------------------- 11. El prototipo hoy
s = SL[10]
set_text(sh(s, 2), "Resultado")
set_text(sh(s, 4), "Versiones 2.10.2 y 2.11.0 con datos ficticios · «IA SIMULADA» = resultado sin valor clínico")
for sid, img, cap_sid, cap in [(6, "cap_cola.png", 7, "Cola de triage priorizada (CU09)"),
                               (9, "cap_caso.png", 10, "Caso: análisis, validación y nivel explicado"),
                               (12, "cap_dash.png", 13, "Dashboard de indicadores (CU14)"),
                               (15, "cap_comp.png", 16, "Comparador de médicos para jefatura (CU19)")]:
    put_image(s, sid, img, mode="fill"); set_text(sh(s, cap_sid), cap)
notes(s, "(40 s) Así se ve hoy: la cola priorizada por nivel, puntaje y espera; el caso con el análisis, la validación médica y la explicación del nivel; el dashboard de indicadores, y el comparador de médicos para la jefatura, agregado en la 2.11.0. Todo con datos ficticios.")

# ---------------------------------------------------------------- 12. Conclusiones
s = SL[11]
set_text(sh(s, 4), "Aurora es un prototipo funcional, desplegado, probado y declarado con transparencia.")
set_text(sh(s, 7), "Plataformas y metodología elegidas con matrices ponderadas")
set_text(sh(s, 10), "Triage configurable, revisión y firma; la IA es apoyo")
set_text(sh(s, 13), "AUC 0,838 por paciente; sin validación clínica todavía")
set_text(sh(s, 16), "VAN de $134,8 M; el piloto es la prueba clave")
set_text(sh(s, 17), "Próximos pasos: desplegar la 2.12.0, repetir PC-01 en AWS, validar el modelo con médicos y formalizar un piloto.")
notes(s, "(40 s) En síntesis: decisiones con criterio, el médico decide, una IA medida y no prometida, y un proyecto viable si se valida la demanda. Los próximos pasos son desplegar la 2.12.0 y repetir la prueba de carga en AWS, validar el modelo con médicos y formalizar un piloto con una institución de salud.")

notes(SL[12], "(5 s) Gracias. Quedamos atentos a sus preguntas.")
prs.save("Presentacion_Aurora_Informe_Final.pptx")
print("ok")
