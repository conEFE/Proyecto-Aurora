# -*- coding: utf-8 -*-
"""Iteración 6: registro de revisiones v0.13 -> v0.14 (capítulo XIV y equipo de inferencia)."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from registro_lib import *
p = os.path.join(sys.argv[1], "word", "document.xml")
x = open(p, encoding="utf-8").read()
x = set_version(x, "0.14 (23-11-2026)")
x = add_version_rows(x, [
    ["0.10", "23-11-2026", "Informe maestro", "Iteración 6: redacción inicial del capítulo XIV (mercado, presupuesto estimado, costo real de la demostración, cotización, flujo de caja, VAN/TIR y sensibilidad recalculados) y actualización de las especificaciones del equipo de inferencia en los capítulos VI y X. Tablas 43 a 49.", "Respaldo previo: Proyecto_Aurora_Informe_Final_Maestro_v0.9_pre-it6.docx."],
    ["0.14", "23-11-2026", "Registro de revisiones", "Sección 4.10: dato aportado por el usuario y observaciones N-14-01 a N-14-07.", "—"]])
sec = [H("4.10. Iteración 6 – Capítulo XIV y equipo de inferencia"),
       P("Fecha: 23-11-2026. El usuario indicó que el costo de la nube ya es conocido y aportó las especificaciones del equipo de inferencia: HP Victus 16 (16-d0xxx), Intel Core i7-11800H (8 núcleos, 16 hilos, 2,3 GHz), 16 GB de RAM, NVIDIA GeForce RTX 3060 Laptop de 6 GB, SSD Micron 3400 de 512 GB (NVMe PCIe 4.0) y SSD Kingston A2000 de 1 TB (NVMe PCIe 3.0). Las especificaciones son coherentes entre sí y con la tarjeta de entrenamiento informada en Unidad 2 («RTX 3060 portátil, 6 GB»). Se incorporaron en las Tablas 8, 26 y 27 y en el apartado 14.2.1. El costo de la nube se tomó de docs/ESTADO_AWS.md y docs/despliegue_aws.md (≈ USD 26 al mes desde el 16-11-2026, con créditos)."),
       TABLE(OBS_W, [
        ["ID", "Capítulo", "Observación", "Acción", "Estado"],
        ["N-14-01", "XIV", "Los cálculos de Unidad 2 (flujo de caja, VAN $134.801.449, TIR 45,0%, recuperación 2,84 años, sensibilidad y umbral de demanda de 75,2%) se reprodujeron con un script y coinciden.", "Presentados como cifras verificadas.", "Resuelto en v0.10"],
        ["N-14-02", "XIV", "Unidad 2 presenta a Nueva Clínica Cordillera como «cliente ancla» y a las cinco clínicas de su red como los clientes del año 1, sin compromiso formal.", "Redactado como supuesto de demanda no validado, sin nombrar a la institución como cliente.", "Resuelto en v0.10"],
        ["N-14-03", "XIV / VI", "No está confirmado que el presupuesto de $47.074.638 sea la versión aprobada; su fuente (Equipo Proyecto Aurora, 2026b) se describe de forma distinta en Unidad 1 y Unidad 2 (relacionado con N-06-09 y N-06-10).", "Presentado como presupuesto estimado (valoración, no gasto efectivo). Confirmar con el equipo.", "Pendiente"],
        ["N-14-04", "XIV / XIII", "La alerta de presupuesto de AWS está configurada en USD 15 mensuales, inferior al costo actual (≈ USD 26).", "Declarado; ajustar la alerta en AWS.", "Pendiente"],
        ["N-14-05", "XIV", "La cotización de equipamiento (Lenovo LOQe con RTX 3050) es una valoración; el equipo usado para el modelo es el HP Victus de un integrante, sin costo de adquisición.", "Aclarado en el texto.", "Resuelto en v0.10"],
        ["N-14-06", "XIV", "La licencia comercial de YOLO (AGPL-3.0) y la infraestructura de inferencia en la nube no están costeadas en el flujo de caja (relacionado con N-09-07).", "Declarado como adquisición no presupuestada que condiciona la fase comercial.", "Pendiente"],
        ["N-14-07", "XIV", "El costo del dominio auroracare.cl (NIC Chile) no está documentado.", "Obtener el valor del equipo si se quiere incluir.", "Pendiente"]])]
x = append_section(x, "".join(sec))
open(p, "w", encoding="utf-8").write(x)
print("ok")
