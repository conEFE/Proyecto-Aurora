# -*- coding: utf-8 -*-
"""Iteración 8: registro de revisiones v0.16 -> v0.17 (capítulos I–V y decisiones del usuario)."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from registro_lib import *
p = os.path.join(sys.argv[1], "word", "document.xml")
x = open(p, encoding="utf-8").read()
x = set_version(x, "0.17 (23-11-2026)")
x = add_version_rows(x, [
    ["0.12", "23-11-2026", "Informe maestro", "Iteración 8: resumen, abstract, palabras clave e introducción; capítulo III con criterios de HU01–HU07, verificación de HU01–HU12, RF01–RF09, RNF01–RNF05 y restricciones; K5 alineado en V y XI; RF09 en XII; presupuesto vigente en XIV. Nuevas Tablas 1 a 4 (renumeración general).", "Respaldo previo: Proyecto_Aurora_Informe_Final_Maestro_v0.11_pre-it8.docx."],
    ["0.17", "23-11-2026", "Registro de revisiones", "Sección 4.13: decisiones D-08-01 a D-08-03, cierres y observaciones N-08-01 a N-08-04.", "—"]])
sec = [H("4.13. Iteración 8 – Capítulos I a V y decisiones pendientes"),
       P("Fecha: 23-11-2026."),
       TABLE([1000, 3400, 5824], [
        ["ID", "Tema", "Decisión aprobada por el usuario (23-11-2026)"],
        ["D-08-01", "Definición de K5", "Se adopta la definición que calcula la plataforma: exactitud del resultado automatizado respecto de la validación médica, meta ≥ 0,85, por versión del modelo, con al menos 30 imágenes evaluables. Aplicado en los capítulos V y XI."],
        ["D-08-02", "RF09", "Se agrega RF09: gestión de solicitudes de titulares de datos (acceso, rectificación, supresión, oposición, portabilidad y bloqueo) con trazabilidad de estado y plazo, vinculado a HU10. Aplicado en los capítulos III y XII."],
        ["D-08-03", "Presupuesto", "El presupuesto de Unidad 2 ($47.074.638) es el presupuesto vigente del prototipo. Aplicado en el capítulo XIV."]]),
       P("Cierres derivados: N-11-01 (definición de K5), N-12-06 (RF para HU10) y N-14-03 (presupuesto vigente) pasan a «Resuelto en v0.12». La matriz de trazabilidad HU–RF/RNF–prueba (N-03-20, segundo conjunto, y N-03-20 de la sección 3) queda resuelta con la Tabla de trazabilidad del capítulo XII y la verificación del capítulo III. Los criterios de aceptación de HU01–HU12 quedan verificados con pruebas automatizadas, salvo HU06 y HU07, con verificación parcial de la interfaz."),
       TABLE(OBS_W, [
        ["ID", "Capítulo", "Observación", "Acción", "Estado"],
        ["N-08-01", "XI / código", "El comentario del código del dashboard indica «exactitud del modelo ≥ 90 %», mientras la constante K5_TARGET es 0,85 (definición adoptada).", "Corregir el comentario en backend/app/services/dashboard_service.py (cambio menor de código, fuera del informe).", "Pendiente"],
        ["N-08-02", "III", "La formulación inicial definía RF08 como preparación de la arquitectura para integrar YOLO; se actualizó a la necesidad funcional de HU08 reformulada.", "Declarado en el capítulo III.", "Resuelto en v0.12"],
        ["N-08-03", "I", "Introducción, resumen y abstract redactados a partir del estado acreditado del proyecto.", "Revisión del equipo antes de la entrega.", "Pendiente de revisión"],
        ["N-08-04", "III / formato", "La tabla de historias de usuario (de una versión anterior) tiene anchos de columna desalineados con su cuadrícula, lo que estrecha las columnas.", "Corregir en la iteración 10 (cierre editorial).", "Pendiente"]])]
x = append_section(x, "".join(sec))
open(p, "w", encoding="utf-8").write(x)
print("ok")
