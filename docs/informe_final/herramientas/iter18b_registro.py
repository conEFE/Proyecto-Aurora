# -*- coding: utf-8 -*-
"""Iteración 18b: registro de revisiones (sección 4.25). Uso: python3 iter18b_registro.py <dir_registro>"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from registro_lib import *
p = os.path.join(sys.argv[1], "word", "document.xml")
x = open(p, encoding="utf-8").read()
x = add_version_rows(x, [["1.8-rc (18b)", "27-11-2026", "Informe maestro",
     "Diagramas de componentes, modelo lógico, topología, infraestructura, arquitectura y análisis automatizado rehechos en notación estándar (UML, ER) con fuente editable en draw.io.",
     "Respaldo previo: Proyecto_Aurora_Informe_Final_Maestro_pre-it18b.docx. Scripts: herramientas/diagramas_drawio.py, drawio_lib.py e iter18b_diagramas.py."]])
x = append_section(x, "".join([H("4.25. Iteración 18b – Diagramas en notación estándar"),
    P("Fecha: 27-11-2026. A pedido del equipo, los seis diagramas propios del capítulo X se rehicieron con la notación y el aspecto de draw.io, como los de la Unidad 2: componentes en UML (estereotipos, interfaces provistas), modelo lógico entidad–relación con pata de gallo y todas las columnas, topología e infraestructura como diagramas de despliegue UML, arquitectura por capas y componente de análisis. Se retiraron los títulos y textos largos dentro de las imágenes; el contenido no cambió. Las fuentes editables quedan en figuras/drawio/.")]))
open(p, "w", encoding="utf-8").write(x)
print("ok")
