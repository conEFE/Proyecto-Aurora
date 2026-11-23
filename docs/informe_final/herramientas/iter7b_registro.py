# -*- coding: utf-8 -*-
"""Iteración 7b: registro de revisiones v0.15 -> v0.16 (hechos declarados por el equipo)."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from registro_lib import *
p = os.path.join(sys.argv[1], "word", "document.xml")
x = open(p, encoding="utf-8").read()
x = set_version(x, "0.16 (23-11-2026)")
x = add_version_rows(x, [
    ["0.11 (rev.)", "23-11-2026", "Informe maestro", "Capítulo XV reconstruido con los hechos declarados por el equipo (entrenamiento del modelo y revisión con profesionales de salud) y capítulo XII actualizado (PB-01). Misma numeración de versión del maestro, contenido revisado.", "Construido desde Proyecto_Aurora_Informe_Final_Maestro_v0.10_pre-it7.docx con iter7_cap15.py e iter7b_declarado.py."],
    ["0.16", "23-11-2026", "Registro de revisiones", "Sección 4.12: hechos declarados D-15-02 y actualización de N-15-03.", "—"]])
sec = [H("4.12. Hechos declarados por el equipo (23-11-2026)"),
       P("El usuario declaró: (1) que Juan Francisco Meneses entrenó el modelo de IA entre septiembre y noviembre de 2026; (2) que el 20-11-2026 el prototipo se presentó a un grupo de dos médicos y una enfermera para que revisaran su funcionamiento y validaran el modelo; y (3) que no hubo capacitación como actividad independiente. No se identifican a los participantes."),
       TABLE([1000, 3400, 5824], [
        ["ID", "Tema", "Registro en el informe"],
        ["D-15-02", "Hechos declarados", "Se incorporan como «declarado por el equipo». La presentación del 20-11 se describe como revisión funcional del prototipo con profesionales de salud, no como validación clínica formal (que requiere protocolo, conjunto de casos y métricas). El entrenamiento se registra del 01-09 al 10-11 (fecha en que los pesos se versionaron en el repositorio)."]]),
       TABLE(OBS_W, [
        ["ID", "Capítulo", "Observación", "Acción", "Estado"],
        ["N-15-03", "XV", "Actualización: la validación con profesionales (hito del 20-11) queda cumplida como revisión funcional declarada, aplicando la alternativa del ajuste A3; la capacitación no se realizó; persisten sin evidencia la firma del SLA, el acta de decisión del modelo y el piloto.", "Capítulos XV y XII actualizados. Si existe un acta o notas de la revisión del 20-11, adjuntarlas como anexo.", "Resuelto parcialmente"],
        ["N-15-07", "XII / XI", "La revisión del 20-11 no incluyó encuesta de satisfacción: K7 sigue sin medición.", "Declarado en las Tablas 33 y 34 del capítulo XII.", "Informativo"]])]
x = append_section(x, "".join(sec))
open(p, "w", encoding="utf-8").write(x)
print("ok")
