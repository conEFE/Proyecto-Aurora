# -*- coding: utf-8 -*-
"""Iteración 10: registro de revisiones v0.18 -> v0.19 (cierre editorial y pendientes consolidados)."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from registro_lib import *
p = os.path.join(sys.argv[1], "word", "document.xml")
x = open(p, encoding="utf-8").read()
x = set_version(x, "0.19 (23-11-2026)")
x = add_version_rows(x, [
    ["1.0-rc", "23-11-2026", "Informe maestro", "Iteración 10 (cierre editorial): siete figuras anchas en páginas horizontales; índice de figuras con la secuencia «Figura»; tabla de historias con leyenda, anchos y letra uniformes; fecha de portada «Diciembre, 2026»; retiro de la sección interna «Control de integración»; limpieza de encabezados vacíos y de la nota de plantilla del diccionario; actualización de campos al abrir en Word. PDF exportado con tabla de contenido e índices actualizados (160 páginas).", "Respaldo previo: Proyecto_Aurora_Informe_Final_Maestro_v0.13_pre-it10.docx. PDF: trabajo/Proyecto_Aurora_Informe_Final.pdf."],
    ["0.19", "23-11-2026", "Registro de revisiones", "Sección 4.15: cierre editorial y pendientes consolidados para la versión final.", "—"]])
sec = [H("4.15. Iteración 10 – Cierre editorial y pendientes para la versión final"),
       P("Fecha: 23-11-2026. El maestro queda como versión candidata 1.0. La sección interna «Control de integración del informe» se retiró del documento académico; su función la cumplen este registro y el archivo de estado. Al abrir el documento en Word se solicitará actualizar los campos (tabla de contenido, índices y referencias cruzadas); el PDF entregado ya los incluye actualizados."),
       P("Pendientes consolidados antes de la entrega (requieren al equipo):"),
       TABLE([1200, 5824, 3200], [
        ["Referencia", "Pendiente", "Responsable sugerido"],
        ["Dedicatoria y agradecimientos", "Redactar los textos personales del equipo (páginas preliminares vacías).", "Equipo"],
        ["N-17-01", "Completar o reemplazar la cita «Shah et al., 2023» del capítulo IV.", "Francisca Neira"],
        ["N-17-02, N-17-04", "Confirmar el título del informe de Unidad 2 (2026c) y la descripción de 2026b.", "Francisca Neira"],
        ["N-17-03", "Verificar fechas de OMS 2026, NEMA 2026 y ACR 2025.", "Francisca Neira"],
        ["N-15-03", "Adjuntar notas o acta de la revisión del 20-11 con profesionales de salud, si existen.", "Equipo"],
        ["N-13-02, N-12-02", "Ejecutar la prueba de restauración de un respaldo y el escaneo OWASP ZAP; actualizar los capítulos XII y XIII con sus resultados.", "Juan Francisco Meneses / Felipe Campos"],
        ["N-14-04", "Ajustar la alerta de presupuesto de AWS al costo real.", "Felipe Campos"],
        ["N-08-01", "Corregir el comentario «≥ 90 %» del código del dashboard (K5 = 0,85).", "Felipe Campos"],
        ["N-10-02, N-12-09", "Confirmar los identificadores nuevos CU18 y PI-06 a PS-08.", "Equipo"],
        ["N-07-04", "Contrastar la estructura con la plantilla institucional original (no disponible en esta sesión).", "Francisca Neira"],
        ["Revisión general", "Lectura completa del informe por el equipo y aceptación de la versión 1.0.", "Equipo"]])]
x = append_section(x, "".join(sec))
open(p, "w", encoding="utf-8").write(x)
print("ok")
