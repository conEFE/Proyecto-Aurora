# -*- coding: utf-8 -*-
"""Iteración 17b: registro de revisiones (sección 4.23, sin cambio de versión del registro).
Uso: python3 iter17b_registro.py <dir_registro>"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from registro_lib import *
p = os.path.join(sys.argv[1], "word", "document.xml")
x = open(p, encoding="utf-8").read()
x = add_version_rows(x, [["1.7-rc (17b)", "26-11-2026", "Informe maestro",
     "Diagramas de componentes y de topología regenerados con la 2.11.0/2.12.0; texto de la Figura 9 y fuentes de la Figura 9, la Tabla 30 y la Figura 11 actualizados.",
     "Respaldo previo: Proyecto_Aurora_Informe_Final_Maestro_v1.7-rc_pre-it17b.docx. Script: herramientas/iter17b_figuras.py."]])
x = append_section(x, "".join([H("4.23. Iteración 17b – Diagramas de componentes y de topología"),
    P("Fecha: 26-11-2026. Revisión de las 28 figuras pedida por el usuario. Dos diagramas propios no reflejaban la iteración 17: el de componentes (sin envío de correos, con 18 tablas y sin el servicio de respaldo) y el de topología (usuarios sin el rol de jefatura). Se regeneraron con diagramas_cap10.py; el servicio de respaldo se dibuja con borde punteado como planificado."),
    P("Sin cambios: figuras de la formulación y de la Unidad 2 (se presentan como diseño), BPMN, componente de análisis y capturas de la 2.10.2 (rotuladas con su versión). La carta Gantt de ejecución mantiene su corte del 23-11-2026 a la espera de la decisión del equipo.")]))
open(p, "w", encoding="utf-8").write(x)
print("ok")
