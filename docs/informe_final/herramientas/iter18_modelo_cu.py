# -*- coding: utf-8 -*-
"""Iteración 18 (27-11-2026): diagrama de casos de uso según el diseño del equipo y punto A3 (desarrollo del modelo
de IA desde la Unidad 2, sección 3.8). Maestro 1.7-rc -> 1.8-rc.
- Figura de casos de uso: herramientas/casos_uso_drawio.py (fuente editable en figuras/drawio/cap10_casos_uso.drawio).
- 10.7.1: subsección «Desarrollo del modelo» (arquitectura, datos, entrenamiento, intentos) con 3 tablas de la U2.
- Referencias: He et al. (2016), Deng et al. (2009), Zuiderveld (1994) y Paszke et al. (2019), tomadas de la U2.
Uso: python3 iter18_modelo_cu.py <dir_desempaquetado_maestro> <png_casos_uso>"""
import os, re, shutil, sys
from xml.sax.saxutils import escape
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import maestro_lib as L

root, png_cu = sys.argv[1], sys.argv[2]
p = os.path.join(root, "word", "document.xml")
x = open(p, encoding="utf-8").read(); L.init_ids(x)
PARA = re.compile(r"<w:p\b(?:(?!<w:p\b).)*?</w:p>", re.S)
text_of = lambda px: "".join(re.findall(r"<w:t[^>]*>([^<]*)</w:t>", px))


def rep(old, new, n=1):
    global x
    o, nn = escape(old), escape(new)
    assert x.count(o) == n, (old[:80], x.count(o))
    x = x.replace(o, nn)


def find_para_unique(text):
    ms = [m for m in PARA.finditer(x) if text_of(m.group(0)) == escape(text)]
    assert len(ms) == 1, (text[:80], len(ms))
    return ms[0]


def replace_image(name, png):
    global x
    shutil.copy(png, os.path.join(root, "word", "media", name))
    w, h = Image.open(png).size
    i = x.find('name="%s"' % name); assert i > 0, name
    s = x.rfind("<w:drawing>", 0, i); e = x.find("</w:drawing>", i)
    d = x[s:e]
    cx, cy = map(int, re.search(r'<wp:extent cx="(\d+)" cy="(\d+)"/>', d).groups())
    ncx, ncy = cx, int(cx * h / w)
    if ncy > cy * 1.15:
        ncy = int(cy * 1.15); ncx = int(ncy * w / h)
    for tag in ("wp:extent", "a:ext"):
        d = d.replace('<%s cx="%d" cy="%d"/>' % (tag, cx, cy), '<%s cx="%d" cy="%d"/>' % (tag, ncx, ncy))
    x = x[:s] + d + x[e:]


# ================================================================ X: casos de uso
replace_image("cap10_casos_uso.png", png_cu)
rep("El diagrama de casos de uso representa cuatro actores principales —personal administrativo, médico, administrador del sistema y jefatura y finanzas— y un actor secundario, el servicio de inferencia.",
    "El diagrama de casos de uso representa cuatro actores: personal administrativo, médico, administrador del sistema y jefatura y finanzas. El análisis de la imagen (CU07) y el cálculo del triage (CU08) los ejecuta la plataforma como parte de la carga de exámenes (CU06), por lo que no tienen un actor humano asociado.")
rep("Fuente: Elaboración propia a partir del catálogo de casos de uso del informe de Unidad 2, actualizado con las funciones implementadas posteriormente (CU17 a CU20, destacados; 25-11-2026).",
    "Fuente: Elaboración propia a partir del catálogo de casos de uso del informe de Unidad 2, actualizado con las funciones implementadas posteriormente (CU17 a CU20, en amarillo; 27-11-2026).")

# ================================================================ 10.7.1: desarrollo del modelo (A3)
ancla = find_para_unique("Las limitaciones declaradas son relevantes para interpretar los resultados: los conjuntos de entrenamiento (CBIS-DDSM, Lee et al., 2017; CMMD, Cui et al., 2021) no contienen mamografías sanas, por lo que el modelo prioriza entre casos con hallazgo; no existe validación externa ni clínica con población chilena; la especificidad implica que una proporción importante de casos benignos queda marcada como sospechosa; y el umbral de 0,35 está fijado en el código del servicio, por lo que su validación por un médico y su conversión en parámetro configurable siguen pendientes. Las métricas corresponden a un prototipo y no constituyen evidencia de desempeño clínico.")
SRC_U2 = "Fuente: Equipo Proyecto Aurora (2026c), informe de la Unidad 2, sección 3.8."
bloques = [
    ("h5", "Desarrollo del modelo."),
    ("p", "Esta sección resume cómo se construyó el clasificador, según lo documentado en la Unidad 2 (Equipo Proyecto Aurora, 2026c). Una red neuronal convolucional (CNN) aprende a reconocer patrones en una imagen deslizando filtros pequeños sobre ella: las primeras capas captan bordes y texturas, las intermedias formas y las profundas rasgos que separan una clase de otra. Los filtros no se programan, sino que se ajustan durante el entrenamiento comparando la predicción con la etiqueta conocida, por lo que el modelo se evalúa por sus resultados."),
    ("p", "El modelo es una ResNet18 preentrenada (He et al., 2016), de 18 capas con pesos y unos 11,7 millones de parámetros, cuyas conexiones residuales permiten entrenar redes profundas sin que el aprendizaje se estanque. Sus filtros vienen ajustados con ImageNet (Deng et al., 2009) y el entrenamiento los adapta a mamografías; esta transferencia de aprendizaje elevó el AUC de 0,70 a 0,79 con los mismos datos. Se modificaron dos capas:"),
    ("b", "Capa inicial: la original espera imágenes a color (3 canales); se reemplazó por una de 1 canal cuyos pesos son el promedio de los tres originales, para conservar lo aprendido."),
    ("b", "Capa de salida: la original elige entre 1.000 categorías; se reemplazó por una capa de abandono (dropout) del 40%, para reducir la memorización, y una neurona cuya salida, con la función sigmoide, es la probabilidad de malignidad."),
    ("p", "El modelo informado en la Unidad 2 se entrenó con 6.601 mamografías completas de dos conjuntos públicos con etiqueta confirmada por patología ({T:it18_datos}). Cada imagen se lee en escala de grises (las de CMMD, en DICOM), se ecualiza con CLAHE (Zuiderveld, 1994), que hace más visibles las estructuras dentro del tejido denso, y se redimensiona; la Unidad 2 usaba 512 × 512 píxeles y la versión integrada en la plataforma usa 672 × 1024. Las imágenes se repartieron en forma estratificada en entrenamiento (70%), validación (10%) y prueba (20%)."),
    ("tabla", "Conjuntos de datos del clasificador CNN", "it18_datos", SRC_U2 + " En CMMD se descartaron 1.458 imágenes de la mama contralateral que no figuran en el registro clínico.",
     [2400, 1700, 1500, 1450, 1450],
     [["Conjunto", "Origen", "Imágenes", "Benignas", "Malignas"],
      ["CBIS-DDSM (Lee et al., 2017)", "Estados Unidos", "2.857", "1.580", "1.277"],
      ["CMMD (Cui et al., 2021)", "China", "3.744", "1.112", "2.632"],
      ["Combinado", "—", "6.601", "2.692", "3.909"]]),
    ("p", "El entrenamiento se realizó en dos etapas para no dañar lo aprendido con ImageNet ({T:it18_etapas}): primero se ajusta solo la capa de salida, que parte con valores al azar, y después se refina toda la red con una tasa de aprendizaje 50 veces menor. Se implementó con PyTorch y torchvision (Paszke et al., 2019) en la tarjeta gráfica del equipo (RTX 3060 portátil, 6 GB), con lotes de 8 imágenes."),
    ("tabla", "Etapas de entrenamiento del clasificador CNN", "it18_etapas", SRC_U2 + " Pérdida: entropía cruzada binaria con ponderación de clases; detención temprana según el AUC de validación.",
     [2200, 3044, 1700, 1600],
     [["Etapa", "Qué se entrena", "Tasa de aprendizaje", "Épocas"],
      ["1. Capa de salida", "Solo la capa final; el resto de la red queda congelado", "0,001", "8"],
      ["2. Ajuste fino", "Toda la red", "0,00002", "Hasta completar 60 en total"]]),
    ("p", "El modelo fue el resultado de siete intentos ({T:it18_intentos}). El primero dio un AUC de 0,988 que resultó falso por fuga de datos: variantes de una misma imagen caían en entrenamiento y prueba. Desde entonces el equipo adoptó un criterio para todo el proyecto: un AUC sobre 0,95 en este problema obliga a revisar la metodología. El paso de recortes de lesiones a mamografía completa fue clave, porque en la práctica clínica se carga la mamografía entera y nadie ha ubicado antes la lesión."),
    ("tabla", "Intentos de entrenamiento del clasificador y aprendizajes", "it18_intentos", SRC_U2,
     [2300, 2300, 1300, 2644],
     [["Intento", "Datos", "AUC en prueba", "Qué se aprendió"],
      ["1. Red propia", "Conjunto de Kaggle, recortes ya aumentados", "0,988 interno; 0,51 externo", "Fuga de datos: el modelo memorizaba"],
      ["2. Red propia desde cero", "CBIS-DDSM, recortes de lesiones", "0,700", "Resultado limpio, pero bajo"],
      ["3. Red propia con aumento de datos", "Igual que el 2", "0,681", "El límite era la capacidad de la red, no la cantidad de datos"],
      ["4. ResNet18 preentrenada", "CBIS-DDSM, recortes, 227 px", "0,788", "La transferencia de aprendizaje funciona"],
      ["5. ResNet18 en dos etapas", "CBIS-DDSM, mamografía completa, 512 px", "0,852", "Mejor resultado, sobre el caso real"],
      ["6. ResNet18 en dos etapas", "CMMD", "0,792", "Referencia por separado"],
      ["7. ResNet18 en dos etapas", "Combinado", "0,843", "Modelo elegido en la Unidad 2"]]),
    ("p", "La Unidad 2 eligió el modelo combinado aunque no tenía el AUC más alto, porque era el más parejo entre clases, su conjunto de prueba era más grande (1.321 imágenes) y aprendió de dos poblaciones y dos tipos de equipo. El umbral de 0,35 se eligió porque, en priorización, un caso maligno no detectado cuesta más que uno benigno marcado. Como próximos pasos planteó reentrenar con división por paciente, ya que la división por imagen podía inflar las métricas, y conectar el modelo a la plataforma como servicio de inferencia. Ambos se cumplieron: las cifras vigentes, con división por paciente, son las informadas antes de esta subsección, y el servicio está integrado mediante el proveedor HTTP descrito en la {T:ia_tab}."),
]
x = x[:ancla.end()] + L.render(root, bloques) + x[ancla.end():]

# ================================================================ Referencias
REFS = [
    ("Deng, J., Dong, W., Socher, R., Li, L.-J., Li, K., & Fei-Fei, L. (2009). ImageNet: A large-scale hierarchical image database. En ",
     "Proceedings of the IEEE Conference on Computer Vision and Pattern Recognition", " (pp. 248–255). https://doi.org/10.1109/CVPR.2009.5206848"),
    ("He, K., Zhang, X., Ren, S., & Sun, J. (2016). Deep residual learning for image recognition. En ",
     "Proceedings of the IEEE Conference on Computer Vision and Pattern Recognition", " (pp. 770–778). https://doi.org/10.1109/CVPR.2016.90"),
    ("Paszke, A., Gross, S., Massa, F., Lerer, A., Bradbury, J., Chanan, G., … Chintala, S. (2019). PyTorch: An imperative style, high-performance deep learning library. En ",
     "Advances in Neural Information Processing Systems", " (Vol. 32)."),
    ("Zuiderveld, K. (1994). Contrast limited adaptive histogram equalization. En P. S. Heckbert (Ed.), ",
     "Graphics gems IV", " (pp. 474–485). Academic Press."),
]
IT = '<w:rPr><w:i/><w:iCs/></w:rPr>'
for a, b, c in REFS:
    refs = [m for m in PARA.finditer(x) if 'w:val="BibliografayReferencias"' in m.group(0)[:200]]
    assert len(refs) > 20, len(refs)
    nxt = next((m for m in refs if text_of(m.group(0)).lower() > escape(a).lower()), None)
    xml = '<w:p><w:pPr><w:pStyle w:val="BibliografayReferencias"/></w:pPr>%s%s%s</w:p>' % (L.run(a), L.run(b, IT), L.run(c))
    pos = nxt.start() if nxt else refs[-1].end()
    x = x[:pos] + xml + x[pos:]

x, nums = L.renumerar(x)
open(p, "w", encoding="utf-8").write(x)
print("ok; tablas", max(v for k, v in nums.items() if "_T_" in k), "figuras", max(v for k, v in nums.items() if "_F_" in k))
