# -*- coding: utf-8 -*-
"""Iteración 12: la corrección del bloqueo bajo carga se desplegó (versión 2.10.1, 24-11-2026). Maestro 1.1-rc -> 1.2-rc.
Uso: python3 iter12_despliegue.py <dir_maestro_descomprimido>"""
import sys, os
p = os.path.join(sys.argv[1], "word", "document.xml")
x = open(p, encoding="utf-8").read()
CAMBIOS = [
    # 12.1.3
    ("La corrección está en el repositorio, pero no se ha desplegado en el entorno de demostración, que sigue en la versión 2.10.0.",
     "La corrección se publicó como versión 2.10.1 y se desplegó en el entorno de demostración el 24-11-2026; el rendimiento bajo carga en ese entorno no se ha medido."),
    # XIII
    ("La versión publicada en el entorno de demostración al cierre de este informe es la 2.10.0.",
     "La versión publicada en el entorno de demostración al cierre de este informe es la 2.10.1, desplegada el 24-11-2026, que corrige el bloqueo bajo carga descrito en el capítulo XII."),
    # Tabla de factibilidad (14.3.1)
    ("prototipo desplegado (versión 2.10.0)", "prototipo desplegado (versión 2.10.1)"),
]
for a, b in CAMBIOS:
    assert x.count(a) == 1, a
    x = x.replace(a, b)
open(p, "w", encoding="utf-8").write(x)
print("ok")
