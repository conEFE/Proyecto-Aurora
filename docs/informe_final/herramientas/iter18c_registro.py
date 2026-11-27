# -*- coding: utf-8 -*-
"""Iteración 18c: registro de revisiones (sección 4.26). Uso: python3 iter18c_registro.py <dir_registro>"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from registro_lib import *
p = os.path.join(sys.argv[1], "word", "document.xml")
x = open(p, encoding="utf-8").read()
x = add_version_rows(x, [["1.8-rc (18c)", "27-11-2026", "Informe maestro",
     "Se retiran las figuras de diseño de U1 y U2 (infraestructura y arquitectura de aplicaciones), que mostraban Cloudflare, São Paulo, Prometheus, Grafana y AWS Backup; las diferencias quedan en el texto. Celda de DNS del piloto aclarada. Figuras: de 28 a 25.",
     "Respaldo previo: Proyecto_Aurora_Informe_Final_Maestro_pre-it18c.docx. Script: herramientas/iter18c_sin_disenos.py."]])
x = append_section(x, "".join([H("4.26. Iteración 18c – Sin diagramas de diseño no adoptados"),
    P("Fecha: 27-11-2026. El equipo observó que el informe seguía mostrando Cloudflare. Aparecía en las figuras de diseño de la formulación y de la Unidad 2, rotuladas como «diseño, no implementado tal cual», que se confundían con la infraestructura real. Se retiraron las tres figuras de diseño y se reescribieron los párrafos que las citaban; el informe muestra solo la infraestructura y la arquitectura desplegadas. En la tabla de costos se aclaró que la columna del piloto es la estimación de la Unidad 2. La presentación de defensa se regeneró con los diagramas nuevos.")]))
open(p, "w", encoding="utf-8").write(x)
print("ok")
