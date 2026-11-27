# -*- coding: utf-8 -*-
"""Iteración 6: capítulo XIV y actualización del equipo de inferencia en VI y X (v0.9 -> v0.10)."""
import sys, os, re
from xml.sax.saxutils import escape
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import maestro_lib as L
import cap14_contenido as C
root = sys.argv[1]; p = os.path.join(root, "word", "document.xml")
x = open(p, encoding="utf-8").read(); L.init_ids(x)

def rep(old, new):
    global x
    o, n = escape(old), escape(new)
    assert x.count(o) == 1, (old[:60], x.count(o))
    x = x.replace(o, n)

# VI, Tabla 8 (recursos tecnológicos): equipo de procesamiento para IA
rep("Equipo con unidad de procesamiento gráfico (GPU)",
    "HP Victus 16 de un integrante: Intel Core i7-11800H, 16 GB RAM, NVIDIA RTX 3060 Laptop (6 GB), SSD NVMe de 512 GB y 1 TB")
# X, Tabla 26 (infraestructura): fila del equipo con GPU
rep("Servicio de inferencia en contenedor o proceso local, conectado por Tailscale",
    "HP Victus 16 (Intel Core i7-11800H, 16 GB RAM, NVIDIA RTX 3060 Laptop de 6 GB, SSD NVMe de 512 GB y 1 TB); servicio de inferencia en contenedor o proceso local, conectado por Tailscale")
# X, Tabla 27 (servicio de inferencia): nueva fila de hardware tras «Identificación del modelo»
t = "<w:t xml:space=\"preserve\">Identificación del modelo</w:t>"
assert x.count(t) == 1
i = x.find(t); s = x.rfind("<w:tr>", 0, i); e = x.find("</w:tr>", i) + 7
row = x[s:e]
cells = re.findall(r'<w:t xml:space="preserve">([^<]*)</w:t>', row)
new = row.replace(cells[0], "Hardware de ejecución", 1).replace(escape(cells[1]) if escape(cells[1]) in row else cells[1],
    escape("GPU NVIDIA RTX 3060 Laptop (6 GB) en un HP Victus 16 con Intel Core i7-11800H y 16 GB de RAM; el servicio usa la GPU si está disponible (cuda:0) o CPU en su defecto. Según su documentación, el análisis toma alrededor de un segundo por imagen con GPU."), 1)
x = x[:e] + new + x[e:]

for bm, blocks in [("_Toc177988513", C.INTRO), ("_Toc177988514", C.MERCADO),
                   ("_Toc177988515", [("p", "Los costos se presentan en dos apartados: los recursos del prototipo, incluido el costo de la infraestructura, y las adquisiciones de equipamiento y licencias.")]),
                   ("_Toc177988516", C.RECURSOS), ("_Toc177988517", C.ADQUIS), ("_Toc177988518", C.FLUJO)]:
    x = L.insert_after_bookmark(x, bm, L.render(root, blocks, os.path.dirname(HERE)))
x = L.set_control_row(x, "XIV. Factibilidad económica",
    "Redacción inicial en v0.10: mercado y demanda (supuesto no validado), presupuesto estimado del prototipo, costo real de la demostración (≈ USD 26/mes con créditos), cotización de equipos, flujo de caja, VAN/TIR y sensibilidad recalculados.",
    "Pendiente: confirmar que el presupuesto de Unidad 2 es la versión aprobada y su fuente (2026b); costo del dominio; licencia comercial de YOLO.")
x = L.set_control_version(x, "0.10", "23-11-2026")
x, nums = L.renumerar(x)
open(p, "w", encoding="utf-8").write(x)
print("ok", {k[7:]: v for k, v in nums.items() if k.startswith("_Ref_T_") and k[7:] in ("demanda","presup","nube","equipos","supuestos","flujo","sens_ec")})
