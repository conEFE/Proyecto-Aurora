# -*- coding: utf-8 -*-
"""Iteración 7: registro de revisiones v0.14 -> v0.15 (capítulo XV)."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from registro_lib import *
p = os.path.join(sys.argv[1], "word", "document.xml")
x = open(p, encoding="utf-8").read()
x = set_version(x, "0.15 (23-11-2026)")
x = add_version_rows(x, [
    ["0.11", "23-11-2026", "Informe maestro", "Iteración 7: redacción inicial del capítulo XV (carta Gantt con línea base, ejecución, responsables e hitos; estado por fase; entregables por sprint; ajustes; hitos y ruta crítica; matriz de riesgos). Figura 11 y Tablas 50 a 54.", "Respaldo previo: Proyecto_Aurora_Informe_Final_Maestro_v0.10_pre-it7.docx. Figura regenerable con herramientas/gantt_xv.py."],
    ["0.15", "23-11-2026", "Registro de revisiones", "Sección 4.11: decisión D-15-01 y observaciones N-15-01 a N-15-06.", "—"]])
sec = [H("4.11. Iteración 7 – Capítulo XV"),
       P("Fecha: 23-11-2026. El usuario solicitó una carta Gantt con quién hizo qué y cuándo según los sprints, e indicó inventar los tiempos para que calcen. No se inventaron fechas de ejecución: se usaron las fechas declaradas por el equipo en Unidad 2 (Sprints 1 a 6, al 18-10-2026) y las del historial de versiones del repositorio (desde octubre); las actividades sin registro se marcaron como tales. Se informó al usuario el criterio."),
       TABLE([1000, 3400, 5824], [
        ["ID", "Tema", "Criterio aplicado (23-11-2026)"],
        ["D-15-01", "Fechas de ejecución del cronograma", "Solo se registran fechas con respaldo (informe de Unidad 2 o repositorio). Las actividades sin evidencia se informan como «sin registro de ejecución». Cualquier replanificación se presenta como plan y no como ejecución. Si el equipo aporta fechas reales con respaldo, se incorporan."]]),
       TABLE(OBS_W, [
        ["ID", "Capítulo", "Observación", "Acción", "Estado"],
        ["N-15-01", "XV", "Los Sprints 1 a 6 no pueden fecharse con Git: sus commits se consolidaron el 07-10-2026. Se usan las fechas declaradas en Unidad 2.", "Declarado en el capítulo; fuente indicada por fila.", "Informativo"],
        ["N-15-02", "XV", "Sprint 7 cerró el 11-11 (11 días de desfase); Sprint 8 cerró el 16-11 con pendientes (pruebas de carga, DICOM). Inicio del Sprint 8 sin registro propio (se usa la línea base).", "Registrado en la Tabla 50 y en la Figura 11.", "Resuelto en v0.11"],
        ["N-15-03", "XV", "Sin evidencia de: firma de la propuesta de SLA (31-10), acta de decisión sobre el modelo (01-11), validación clínica (16–20-11), capacitación (10–25-11) y piloto (20–30-11). Aceptación del MVP (24-11) pendiente. Relacionado con N-06-04, N-12-04 y N-10-05.", "Confirmar con el equipo; si existen registros, actualizar el capítulo.", "Pendiente"],
        ["N-15-04", "XV", "La autoría de commits no permite atribuir contribuciones individuales (historial consolidado; casi todos los commits figuran con un mismo autor). La responsabilidad se informa según los roles del capítulo VI.", "Declarado en el texto de la Tabla 51.", "Informativo"],
        ["N-15-05", "XV / XIII", "Cambios relevantes posteriores a Unidad 2 (migración a RDS, rediseño visual, aurora-admin) no tienen solicitud de cambio formal registrada en las fuentes revisadas.", "Declarado; registrar SC si el equipo lo requiere.", "Pendiente"],
        ["N-15-06", "XV", "Se agregó el riesgo R18 (dependencia de un equipo personal para la inferencia) sin probabilidad ni impacto valorados.", "Valorar con el equipo.", "Pendiente"]])]
x = append_section(x, "".join(sec))
open(p, "w", encoding="utf-8").write(x)
print("ok")
