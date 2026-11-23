# -*- coding: utf-8 -*-
"""Iteración 9: registro de revisiones v0.17 -> v0.18 (capítulos XVI, XVII y XVIII)."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from registro_lib import *
p = os.path.join(sys.argv[1], "word", "document.xml")
x = open(p, encoding="utf-8").read()
x = set_version(x, "0.18 (23-11-2026)")
x = add_version_rows(x, [
    ["0.13", "23-11-2026", "Informe maestro", "Iteración 9: conclusiones y recomendaciones; glosario (23 términos) y referencias APA 7 (56 entradas); anexos 1 a 4 (especificación de CU01–CU18, diccionario de datos, configuración del triage, evidencia de pruebas) y material complementario; normalización de «s. f.»; citas de CBIS-DDSM y CMMD en el capítulo X.", "Respaldo previo: Proyecto_Aurora_Informe_Final_Maestro_v0.12_pre-it9.docx."],
    ["0.18", "23-11-2026", "Registro de revisiones", "Sección 4.14: observaciones N-17-01 a N-17-05.", "—"]])
sec = [H("4.14. Iteración 9 – Capítulos XVI, XVII y XVIII"),
       P("Fecha: 23-11-2026. Se contrastaron todas las citas del texto con la lista de referencias mediante un script. Las referencias provienen de la bibliografía de Unidad 2; las del capítulo IV (OMS 2021, FDA, HL7 FHIR, DICOM, BI-RADS) se identificaron por búsqueda en las fuentes oficiales. Los parámetros del triage del anexo 3 se verificaron contra el código. La especificación de CU01–CU16 proviene de Unidad 2; CU17 y CU18 se especificaron a partir del código y las pruebas."),
       TABLE(OBS_W, [
        ["ID", "Capítulo", "Observación", "Acción", "Estado"],
        ["N-17-01", "IV / XVII", "La cita «Shah et al., 2023» del capítulo IV no pudo identificarse: no figura en las fuentes del proyecto ni se encontró por búsqueda.", "Entrada marcada con [FALTA INFORMACIÓN]. Completar con los datos de la fuente o reemplazar la cita.", "Pendiente"],
        ["N-17-02", "XVII", "El título exacto del informe de Unidad 2 (Equipo Proyecto Aurora, 2026c) no pudo extraerse de la portada.", "Confirmar título; las fuentes que dicen «informe de Unidad 2 del proyecto» corresponden a esta referencia.", "Pendiente"],
        ["N-17-03", "IV / XVII", "Las fechas de las fuentes web citadas con año de consulta (OMS 2026, NEMA 2026, ACR 2025) deben verificarse.", "Verificar fechas de publicación o usar «s. f.» con fecha de consulta.", "Pendiente"],
        ["N-17-04", "XVII", "Equipo Proyecto Aurora (2026b) se describe en Unidad 1 como «Evaluación 2 de Gestión de Proyectos» y en Unidad 2 como «Informe 4 – Gestión de Proyectos» (N-06-10).", "Se usó la descripción de Unidad 2; confirmar.", "Pendiente"],
        ["N-17-05", "XVII", "Se normalizó «s.f.» a «s. f.» (APA 7 en español) en todo el informe, y la cita de AWS pasó de «s.f.-b» a «s. f.» por quedar una sola entrada.", "Aplicado.", "Resuelto en v0.13"]])]
x = append_section(x, "".join(sec))
open(p, "w", encoding="utf-8").write(x)
print("ok")
