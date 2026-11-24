# -*- coding: utf-8 -*-
"""Iteración 11: registro de revisiones v0.19 -> v0.20 (ajustes por plantilla y rúbrica EA5).
Uso: python3 iter11_registro.py <dir_registro> <p95_100_ms>"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from registro_lib import *
p = os.path.join(sys.argv[1], "word", "document.xml")
p95 = sys.argv[2]
x = open(p, encoding="utf-8").read()
x = set_version(x, "0.20 (24-11-2026)")
x = add_version_rows(x, [
    ["1.1-rc", "24-11-2026", "Informe maestro",
     "Iteración 11 (plantilla y rúbrica de defensa EA5): título 10.4.3 literal de la plantilla; «Componente de análisis automatizado de imágenes» pasa a 10.7.1; cinco encabezados vacíos retirados. Nuevos apartados: 4.8 soluciones existentes y diferenciación (Tabla 6); 8.3.1 sustentabilidad; 9.2.1 integración del stack; 12.1.3 prueba de rendimiento local (PC-01, p95 de " + p95 + " ms con 100 usuarios, tras corregir un bloqueo bajo carga detectado por la propia prueba); 14.3.1 síntesis de factibilidad técnica, operativa, económica, legal y ambiental. Actualizados resumen, abstract, XI, XII, XV y XVI; seis referencias y un término de glosario nuevos.",
     "Respaldo previo: Proyecto_Aurora_Informe_Final_Maestro_v1.0-rc_pre-it11.docx. Evidencia: evidencias/rendimiento_2026-11-24/."],
    ["0.20", "24-11-2026", "Registro de revisiones", "Sección 4.16: ajustes por plantilla y rúbrica; revisión de nube frente a historias de usuario.", "—"]])
sec = [H("4.16. Iteración 11 – Ajustes por plantilla institucional y rúbrica de defensa"),
       P("Fecha: 24-11-2026. Insumos: plantilla Plantilla_Informe_Final_TIHI84_Apoquindo.docx y Escala de Apreciación N.º 5 (TIHI84_U3_ES3_EA5.xlsx). El usuario aprobó aplicar los cinco ajustes propuestos el 23-11-2026."),
       TABLE([1300, 3000, 2900, 3024], [
        ["Ajuste", "Indicador de la rúbrica", "Cambio en el maestro", "Evidencia"],
        ["(a)", "Estructura de plantilla", "10.4.3 con su título literal; 10.8 pasa a 10.7.1; encabezados vacíos retirados", "Contraste con la plantilla (95 títulos)"],
        ["(b)", "4. Innovación frente a soluciones existentes", "4.8 con comparación (Tabla 6) y argumento de innovación por integración", "Applied Radiology (2018), Lunit (2021), iCAD (2023), Dembrower et al. (2020), Freeman et al. (2021), Lång et al. (2023)"],
        ["(c)", "5. Evaluación técnica, operativa, económica, legal y ambiental", "14.3.1 con síntesis y cinco dimensiones", "Estudio de factibilidad de la Unidad 2; capítulos IX a XV; Amazon Web Services (s. f.-a)"],
        ["(d)", "2. Herramientas se complementan; 3. Solución sustentable", "9.2.1 con puntos de integración; 8.3.1 con sustentabilidad", "Código: deploy/Caddyfile, backend/app, .github/workflows"],
        ["(e)", "6. Estabilidad y rendimiento", "12.1.3 con PC-01 en entorno local; XI, XII, XV, XVI, resumen y abstract actualizados", "backend/scripts/load_test.py; evidencias/rendimiento_2026-11-24/"]]),
       P("Decisiones y observaciones de esta iteración:"),
       TABLE([1300, 6000, 2924], [
        ["ID", "Descripción", "Estado"],
        ["D-11-01", "La prueba de carga se implementa con un script propio (httpx) en lugar de Locust y se ejecuta en entorno local; no se ejecuta contra el entorno de demostración sin acuerdo del equipo, porque genera tráfico y registros de auditoría.", "Aplicada"],
        ["D-11-02", "La primera ejecución de PC-01 detectó un bloqueo total de la API con 50 usuarios (el middleware pedía una segunda conexión al pool que ocupa el endpoint). Se corrigió en el código (pool auxiliar y ejecución fuera del bucle de eventos, también en la carga de imágenes), con prueba de regresión (suite de 316 pruebas, 0 fallos) y repetición de la serie. Ejecución previa conservada como evidencia (carga_50_usuarios_antes_correccion.json).", "Aplicada en el repositorio"],
        ["N-11-07", "La corrección del bloqueo bajo carga no está desplegada: el entorno de demostración sigue en la versión 2.10.0. Desplegarla es decisión del equipo.", "Abierta"],
        ["N-11-01", "La evidencia de rendimiento es local (4 vCPU, servidor y generador en la misma máquina, sin imágenes ni inferencia). El rendimiento de la instancia t4g.micro no se midió; PC-02 (estrés) no se ejecutó.", "Abierta"],
        ["N-11-02", "La calificación del componente de análisis de imágenes como dispositivo médico ante la autoridad sanitaria no se evaluó. Se buscó una fuente sobre el régimen chileno de control de dispositivos médicos, pero no pudo verificarse desde esta sesión; por eso el informe solo declara la evaluación como requisito previo a un uso clínico.", "Abierta: requiere revisión del equipo"],
        ["N-11-03", "La recomendación de «copias fuera de la región» no es aplicable en el proyecto de AWS (no admite acciones entre regiones); se reemplazó por una copia cifrada fuera de AWS, alternativa que la Unidad 2 ya contemplaba.", "Aplicada"],
        ["N-11-04", "La factibilidad implementativa de la Unidad 2 mencionaba una capacitación del 10 al 25 de noviembre y a la institución de referencia como cliente piloto; en 14.3.1 se redactó según lo declarado (sin capacitación; revisión del 20-11; institución sin compromiso formal).", "Aplicada"],
        ["N-11-05", "La huella ambiental (nube y equipo de inferencia) no se midió; la eficiencia de Graviton es una cifra declarada por el proveedor.", "Abierta"],
        ["N-11-06", "Error de esquema heredado (sombreado de tabla sin atributo w:val) corregido; el maestro vuelve a validar sin errores.", "Aplicada"]]),
       P("Revisión de componentes de nube no adoptados frente a las historias de usuario: ninguno impide cumplir una historia; afectan requerimientos no funcionales, KPI y SLA. El único que incide en el valor de una historia es la inferencia fuera de la nube (HU08 y HU12: con el equipo de inferencia apagado, el resultado es simulado). Detalle y recomendaciones en trabajo/REVISION_NUBE_VS_HU.md.")]
x = append_section(x, "".join(sec))
open(p, "w", encoding="utf-8").write(x)
print("ok")
