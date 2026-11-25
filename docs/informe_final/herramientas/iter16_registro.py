# -*- coding: utf-8 -*-
"""Iteración 16: registro de revisiones v0.24 -> v0.25 (consistencia, citas, glosario y formato).
Uso: python3 iter16_registro.py <dir_registro>"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from registro_lib import *
p = os.path.join(sys.argv[1], "word", "document.xml")
x = open(p, encoding="utf-8").read()
x = set_version(x, "0.25 (25-11-2026)")
x = add_version_rows(x, [
    ["1.6-rc", "25-11-2026", "Informe maestro",
     "Iteración 16: 11 afirmaciones desactualizadas corregidas (VI, IX, X, XII, XIII y XV) según las iteraciones 12 a 15; fila de monitoreo en la tabla de componentes de infraestructura; citas de AWS (s. f.-b), AXELOS (2019) y APA (2020), que figuraban en la lista sin cita; 29 términos nuevos en el glosario (de 24 a 53); encabezado vacío retirado de la tabla de contenido.",
     "Respaldo previo: Proyecto_Aurora_Informe_Final_Maestro_v1.5-rc_pre-it16.docx. Base: trabajo/REVISION_COMPLETITUD_1.5.md (puntos A1, A4, A5 y A6)."],
    ["0.25", "25-11-2026", "Registro de revisiones", "Sección 4.21: consistencia, citas, glosario y formato.", "—"]])
sec = [H("4.21. Iteración 16 – Consistencia, citas, glosario y formato"),
       P("Fecha: 25-11-2026. El usuario aprobó corregir los puntos A1, A4, A5 y A6 de la revisión de completitud del maestro 1.5-rc (trabajo/REVISION_COMPLETITUD_1.5.md)."),
       TABLE([1300, 6000, 2924], [
        ["ID", "Descripción", "Estado"],
        ["D-16-01", "Afirmaciones desactualizadas corregidas: matriz de trazabilidad (PS-04 ejecutado), tabla de disponibilidad (prueba con 100 usuarios ejecutada), brechas para un piloto, última corrida de la integración continua, desviaciones, ajuste A1 y ruta crítica del capítulo XV, referencias internas en VI y IX, y versiones del Sprint 8.", "Aplicada"],
        ["D-16-02", "Citas agregadas para tres referencias que no se citaban: regiones de AWS en IX; ITIL 4 y APA en la tabla de normas de XII. La cita «OMS, 2021» se mantiene: la sigla se presentó con el nombre completo en la primera cita del capítulo IV.", "Aplicada"],
        ["D-16-03", "Glosario ampliado con 29 siglas y términos de uso frecuente (servicios de AWS, notaciones, seguridad, conjuntos de datos y evaluación económica).", "Aplicada"],
        ["N-16-01", "Los índices de tablas y de figuras del DOCX muestran su texto provisional hasta que Word actualiza los campos (el documento pide hacerlo al abrir); el PDF los trae generados.", "Informativa"],
        ["N-16-02", "Siguen abiertos de la misma revisión: A2 (repetir la ejecución de pruebas con 321) y A3 (detalle del desarrollo del modelo de IA), además de los insumos del equipo (sección B).", "Abierta"]])]
x = append_section(x, "".join(sec))
open(p, "w", encoding="utf-8").write(x)
print("ok")
