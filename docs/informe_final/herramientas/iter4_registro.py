# -*- coding: utf-8 -*-
"""Iteración 4: registro de revisiones v0.11 -> v0.12 (capítulo XII, ejecución de pruebas)."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from registro_lib import *
p = os.path.join(sys.argv[1], "word", "document.xml")
x = open(p, encoding="utf-8").read()
x = set_version(x, "0.12 (23-11-2026)")
x = add_version_rows(x, [
    ["0.8", "23-11-2026", "Informe maestro", "Iteración 4: redacción inicial del capítulo XII (plan de pruebas, matriz de casos con prueba automatizada y resultado, resultados de la ejecución propia, pruebas por archivo, matriz de trazabilidad y normas). Tablas 28 a 33.", "Respaldo previo: Proyecto_Aurora_Informe_Final_Maestro_v0.7_pre-it4.docx. Evidencia: evidencias/pruebas_2026-11-23."],
    ["0.12", "23-11-2026", "Registro de revisiones", "Sección 4.8: observaciones N-12-01 a N-12-09.", "—"]])
sec = [H("4.8. Iteración 4 – Capítulo XII y ejecución de pruebas"),
       P("Fecha: 23-11-2026. Ejecución propia de la suite del backend sobre el commit 53ee1b1 (código de aplicación igual a main en c318a45): Python 3.13.18, PostgreSQL 16 local, base aislada creada con Alembic. Resultado: 314 pruebas aprobadas, 0 fallidas, 0 errores, 0 omitidas; cobertura 97% (app/services 96,1%). Análisis estático: ruff, ESLint y TypeScript sin errores. Integración continua: última corrida en main (run 61, 16-11-2026) exitosa; el flujo OWASP ZAP no registra corridas. Evidencia guardada en docs/informe_final/evidencias/pruebas_2026-11-23 (JUnit y cobertura por archivo)."),
       TABLE(OBS_W, [
        ["ID", "Capítulo", "Observación", "Acción", "Estado"],
        ["N-12-01", "XII", "Los resultados de pruebas citados en las fuentes estaban desactualizados (Unidad 2: 206 pruebas, v2.2.0; resultados_tests.md: 270 pruebas, v2.5.0). Ejecución propia: 314/314, cobertura 97%. Cierra N-09-03.", "Resultados de la ejecución propia en las Tablas 30 y 31.", "Resuelto en v0.8"],
        ["N-12-02", "XII / XI", "El escaneo dinámico OWASP ZAP (PS-04) nunca se ejecutó: el flujo zap.yml tiene 0 corridas en GitHub Actions.", "Declarado como no ejecutado. Ejecutar el flujo y registrar hallazgos si se quiere evidencia.", "Pendiente"],
        ["N-12-03", "XII / XI", "Las pruebas de carga y estrés (PC-01, PC-02) no se ejecutaron: Locust no está implementado. Los KPI de rendimiento y disponibilidad no tienen medición.", "Declarado; considerar en los capítulos XI y XV.", "Pendiente"],
        ["N-12-04", "XII / XV", "Las pruebas alfa (PA-01) y beta (PB-01) no tienen evidencia registrada (relacionado con N-06-04: validación clínica y piloto).", "Solicitar al equipo evidencia si existe; en caso contrario se mantienen como no ejecutadas.", "Pendiente"],
        ["N-12-05", "XII", "No existen pruebas automatizadas de la interfaz web; la generación del PDF en el navegador no está cubierta por pruebas.", "Declarado en la matriz de trazabilidad.", "Informativo"],
        ["N-12-06", "III / XII", "HU10 (derechos de titulares) no tiene un requisito funcional asignado en RF01–RF08.", "Proponer RF09 «Gestión de derechos de titulares de datos» en la revisión del capítulo III (iteración 8); requiere aprobación.", "Pendiente de aprobación"],
        ["N-12-07", "XII", "La ejecución propia usó Python 3.13; el CI y el contenedor usan Python 3.12.", "Declarado en el texto; el CI con 3.12 está en verde.", "Informativo"],
        ["N-12-08", "XII.12.2", "La fecha de entrada en vigencia de la Ley 21.719 (citada por Unidad 2: 01-12-2026, con proyecto de postergación a diciembre de 2027) debe confirmarse a la fecha de entrega.", "Texto redactado sin fijar la fecha; verificar en el capítulo XVII.", "Pendiente"],
        ["N-12-09", "XII.12.1", "Se agregaron los casos PI-06, PI-07, PI-08, PS-07 y PS-08 (marcados con asterisco) para cubrir funciones incorporadas después de Unidad 2.", "Identificadores nuevos a confirmar por el equipo.", "Resuelto en v0.8; confirmar"]]),
       P("Efecto sobre observaciones anteriores: la observación técnica «Pruebas del proveedor» del componente inference queda resuelta (test_inference_model.py, 19 pruebas aprobadas). Los criterios de aceptación de HU01–HU12 cuentan ahora con evidencia de pruebas automatizadas según la Tabla 32 del maestro; su cierre formal se revisará en la iteración 8.")]
x = append_section(x, "".join(sec))
open(p, "w", encoding="utf-8").write(x)
print("ok")
