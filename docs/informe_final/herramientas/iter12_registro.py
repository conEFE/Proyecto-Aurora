# -*- coding: utf-8 -*-
"""Iteración 12: registro de revisiones v0.20 -> v0.21 (despliegue de la versión 2.10.1).
Uso: python3 iter12_registro.py <dir_registro>"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from registro_lib import *
p = os.path.join(sys.argv[1], "word", "document.xml")
x = open(p, encoding="utf-8").read()
x = set_version(x, "0.21 (24-11-2026)")
x = add_version_rows(x, [
    ["1.2-rc", "24-11-2026", "Informe maestro",
     "Iteración 12: la corrección del bloqueo bajo carga se desplegó como versión 2.10.1. Actualizados 12.1.3, XIII (versión publicada) y la síntesis de factibilidad técnica de 14.3.1.",
     "Respaldo previo: Proyecto_Aurora_Informe_Final_Maestro_v1.1-rc_pre-it12.docx. Evidencia: docs/ESTADO_AWS.md (24-11-2026)."],
    ["0.21", "24-11-2026", "Registro de revisiones", "Sección 4.17: despliegue de la versión 2.10.1; cierre de N-11-07.", "—"]])
sec = [H("4.17. Iteración 12 – Despliegue de la corrección del bloqueo bajo carga"),
       P("Fecha: 24-11-2026. El usuario decidió desplegar la corrección (decisión 1 del traspaso de la iteración 11)."),
       TABLE([1300, 6000, 2924], [
        ["ID", "Descripción", "Estado"],
        ["D-12-01", "La corrección se incorporó a la rama principal como versión 2.10.1 (commit eecc255; 316 pruebas aprobadas, análisis estático y verificación de tipos sin errores), se publicaron sus imágenes y se desplegó en el entorno de demostración por Session Manager, con respaldo previo de la base de datos (backups/aurora-20261124T022416Z.sql.gz). Sin migraciones. Verificación posterior: sitio y /api/health responden 200 y el inicio de sesión responde.", "Aplicada"],
        ["N-11-07", "Cerrada: el entorno de demostración ejecuta la versión 2.10.1 desde el 24-11-2026.", "Cerrada"],
        ["N-12-01", "El rendimiento bajo carga del entorno de demostración (t4g.micro) sigue sin medirse; la evidencia de PC-01 continúa siendo local (N-11-01).", "Abierta"],
        ["N-12-02", "La versión 2.10.1 no tiene etiqueta de versión en GitHub (las etiquetas se suben desde un PC del equipo, no desde la sesión en la nube); sus imágenes se identifican por el commit (sha-eecc255…).", "Abierta: etiqueta v2.10.1 opcional"]])]
x = append_section(x, "".join(sec))
open(p, "w", encoding="utf-8").write(x)
print("ok")
