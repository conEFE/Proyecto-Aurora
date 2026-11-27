# -*- coding: utf-8 -*-
"""Iteración 15: registro de revisiones v0.23 -> v0.24 (diagramas y capturas).
Uso: python3 iter15_registro.py <dir_registro>"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from registro_lib import *
p = os.path.join(sys.argv[1], "word", "document.xml")
x = open(p, encoding="utf-8").read()
x = set_version(x, "0.24 (24-11-2026)")
x = add_version_rows(x, [
    ["1.5-rc", "24-11-2026", "Informe maestro",
     "Iteración 15: 15 figuras nuevas (de 11 a 26). Capítulo V: BPMN del proceso afectado (Unidad 1). Capítulo VIII: organigrama y proceso de negocio (Unidad 1). Capítulo X: diagrama cloud y arquitectura por capas nuevos (reemplazan las figuras de infraestructura y arquitectura), diseños de infraestructura y de aplicaciones de las Unidades 1 y 2 como contraste, y diagrama del componente de análisis (CNN y YOLO). Anexo nuevo con 8 capturas de la versión 2.10.2. Capítulo VII: se retira la frase que excluía los diagramas de la formulación.",
     "Respaldo previo: Proyecto_Aurora_Informe_Final_Maestro_v1.4-rc_pre-it15.docx. Fuentes: figuras/ y herramientas/diagramas_it15/."],
    ["0.24", "24-11-2026", "Registro de revisiones", "Sección 4.20: diagramas y capturas.", "—"]])
sec = [H("4.20. Iteración 15 – Diagramas de procesos y arquitectura, y capturas del prototipo"),
       P("Fecha: 24-11-2026. El usuario observó que faltaban diagramas BPMN, el de arquitectura y el cloud, y eligió agregar los procesos de la Unidad 1, rehacer arquitectura y cloud, agregar la CNN y el organigrama, y capturas de la versión 2.10.2."),
       TABLE([1300, 6000, 2924], [
        ["ID", "Descripción", "Estado"],
        ["D-15-03", "Se revierte la decisión de no reproducir los diagramas de la formulación: se incorporan en los capítulos V, VIII y X, rotulados como diseño de la formulación cuando no coinciden con lo implementado (Cloudflare, Prometheus y Grafana, AWS Backup, región de São Paulo).", "Aplicada"],
        ["D-15-04", "Arquitectura por capas y diagrama cloud nuevos, dibujados a partir del código y de docs/ESTADO_AWS.md al 24-11-2026 (incluyen el monitoreo y las alarmas de la iteración 14).", "Aplicada"],
        ["N-15-01", "El diagrama de la CNN de la Unidad 2 indicaba una entrada de 512 × 512 píxeles; el código usa 672 × 1024. Se redibujó con los valores del código (analyzer.py y preprocessing.py) y se agregó la etapa YOLO11s.", "Aplicada"],
        ["N-15-02", "El organigrama de la Unidad 1 asigna el backend y la IA a Felipe Campos y el frontend y la infraestructura a Juan Francisco Meneses; en la ejecución el modelo quedó a cargo de Juan Francisco Meneses. Se aclara en el texto y el rol de QA se mantiene como no incorporado.", "Aplicada"],
        ["N-15-03", "Las capturas se tomaron en un entorno local con la versión 2.10.2, datos ficticios, imágenes sintéticas y el proveedor de IA simulado; las métricas y errores de pruebas de carga previas se limpiaron en esa base local antes de capturar.", "Informativa"]])]
x = append_section(x, "".join(sec))
open(p, "w", encoding="utf-8").write(x)
print("ok")
