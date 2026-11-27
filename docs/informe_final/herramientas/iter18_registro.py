# -*- coding: utf-8 -*-
"""Iteración 18: registro de revisiones (sección 4.24, registro v0.27).
Uso: python3 iter18_registro.py <dir_registro>"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from registro_lib import *
p = os.path.join(sys.argv[1], "word", "document.xml")
x = open(p, encoding="utf-8").read()
x = set_version(x, "0.27 (27-11-2026)")
x = add_version_rows(x, [["1.8-rc", "27-11-2026", "Informe maestro",
     "Diagrama de casos de uso con la disposición definida por el equipo (fuente editable en draw.io); punto A3: subsección «Desarrollo del modelo» en 10.7.1 con 3 tablas de la Unidad 2; 4 referencias agregadas.",
     "Respaldo previo: Proyecto_Aurora_Informe_Final_Maestro_pre-it18.docx. Scripts: herramientas/casos_uso_drawio.py e iter18_modelo_cu.py."]])
x = append_section(x, "".join([H("4.24. Iteración 18 – Casos de uso y desarrollo del modelo de IA"),
    P("Fecha: 27-11-2026. El equipo entregó el diagrama de casos de uso con la disposición que quiere en el informe (actores a ambos lados del sistema, sin el actor secundario del servicio de inferencia, CU17 a CU20 en amarillo). Se reprodujo con casos_uso_drawio.py, que genera también el archivo figuras/drawio/cap10_casos_uso.drawio para editarlo en draw.io. Se ajustó el párrafo que describía el actor secundario."),
    P("Punto A3: con el informe de la Unidad 2 reenviado por el equipo se agregó en 10.7.1 la subsección «Desarrollo del modelo»: funcionamiento de una CNN, ResNet18 y capas modificadas, conjuntos de datos (Tabla 35), etapas de entrenamiento (Tabla 36) y los siete intentos con la fuga de datos del primero (Tabla 37). Las cifras de la Unidad 2 se presentan como tales; las vigentes siguen siendo las del modelo reentrenado con división por paciente. Referencias agregadas: He et al. (2016), Deng et al. (2009), Paszke et al. (2019) y Zuiderveld (1994). Tablas: de 68 a 71.")]))
open(p, "w", encoding="utf-8").write(x)
print("ok")
