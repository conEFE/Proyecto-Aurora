# -*- coding: utf-8 -*-
"""Iteración 17: registro de revisiones v0.25 -> v0.26 (versiones 2.11.0 y 2.12.0, punto A2, pendientes del equipo).
Uso: python3 iter17_registro.py <dir_registro>"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from registro_lib import *
p = os.path.join(sys.argv[1], "word", "document.xml")
x = open(p, encoding="utf-8").read()
x = set_version(x, "0.26 (25-11-2026)")
x = add_version_rows(x, [
    ["1.7-rc", "25-11-2026", "Informe maestro",
     "Iteración 17: versión 2.11.0 desplegada (rol de jefatura y finanzas, comparador de médicos, ficha del médico, activación por correo) y 2.12.0 terminada sin desplegar (optimización de consultas y servicio de inferencia de respaldo) integradas en VI, X, XI, XII, XIII, XIV, XV, XVI y anexos; ejecución formal de pruebas del 25-11 (340 pruebas, 97%); nueva subsección de optimización con su tabla; CU19 y CU20; tabla email_tokens; modelo lógico, casos de uso, arquitectura e infraestructura regenerados; dos capturas de la 2.11.0. De 67 a 68 tablas y de 26 a 28 figuras.",
     "Respaldo previo: Proyecto_Aurora_Informe_Final_Maestro_v1.6-rc_pre-it17.docx. Script: herramientas/iter17_versiones.py."],
    ["0.26", "25-11-2026", "Registro de revisiones", "Sección 4.22: versiones 2.11.0 y 2.12.0, ejecución de pruebas y mecanismo para los insumos del equipo.", "—"]])
sec = [H("4.22. Iteración 17 – Versiones 2.11.0 y 2.12.0, ejecución de pruebas y pendientes del equipo"),
       P("Fecha: 25-11-2026. El usuario pidió aplicar las correcciones pendientes y dejar el informe listo para que el equipo agregue solo lo que falta. Fuentes: código de la rama claude/bold-maxwell-13fkwp (commit a2c4761, versión 2.12.0, que incluye la 2.11.0 de main), docs/CHANGELOG_SPRINTS.md, docs/ESTADO_AWS.md y docs/inferencia_remota.md."),
       TABLE([1300, 6000, 2924], [
        ["ID", "Descripción", "Estado"],
        ["D-17-01", "Versión 2.11.0, desplegada el 25-11-2026: rol de jefatura y finanzas (VI, X, XVI), CU19 «Comparar desempeño de médicos» y CU20 «Activar cuenta por correo» (catálogo, diagrama y especificación en anexos; CU02 actualizado), comparador de médicos en XI, componente de envío de correos y tabla email_tokens (modelo de 18 a 19 tablas; modelo físico, modelo lógico y diccionario de datos regenerados desde los modelos).", "Aplicada"],
        ["D-17-02", "Punto A2 de la revisión de completitud: ejecución formal del 25-11-2026 sobre la versión 2.12.0 (340 pruebas aprobadas, cobertura 97%, servicios 94,5%; evidencias/pruebas_2026-11-25). Actualizados las Tablas de resultados y de pruebas por archivo, la matriz de casos de prueba (5 casos nuevos: PI-09* a PI-12* y PS-09*), la matriz de trazabilidad, el resumen, el abstract, las conclusiones y el anexo de evidencia.", "Aplicada"],
        ["D-17-03", "Versión 2.12.0 (terminada, sin desplegar): nueva subsección «Optimización de consultas» en XII con la prueba local antes y después (de 23,4 a 94,6 solicitudes/s; p95 de 2.532 ms con 100 usuarios; evidencias/rendimiento_2026-11-25). Se declara expresamente que PC-01 se evalúa en el entorno de demostración y que allí falta medirla.", "Aplicada"],
        ["D-17-04", "Inferencia el día de la defensa: decisión del equipo de usar el equipo con GPU como servicio principal y una instancia en AWS como respaldo. Integrado como servicio de respaldo configurable (2.12.0) en 10.7.1, componentes, infraestructura (fila «planificado»), análisis de impacto, factibilidad, riesgos y recomendaciones. La instancia no está creada al 25-11-2026.", "Aplicada"],
        ["D-17-05", "Figuras de arquitectura e infraestructura cloud regeneradas con la versión 2.11.0 (herramientas/diagramas_it15); dos capturas de la 2.11.0 en el anexo (comparador y ficha de usuario nuevo).", "Aplicada"],
        ["D-17-06", "Mecanismo para los insumos del equipo: trabajo/pendientes_equipo.json (dedicatoria, agradecimientos, referencias, marcas del capítulo II, despliegue de la 2.12.0, PC-01 en el entorno de demostración e instancia de respaldo) y herramientas/completar_pendientes.sh, que los aplica con textos para cada resultado posible, valida el DOCX y exporta el PDF. Guía: trabajo/PENDIENTES_EQUIPO.md.", "Aplicada"],
        ["N-17-01", "Se detectaron dos marcas «[FALTA INFORMACIÓN…]» en el capítulo II (cifras de GLOBOCAN 2024 y plazos GES) que no figuraban en los pendientes consolidados; se agregaron al archivo de insumos del equipo.", "Abierta"],
        ["N-17-02", "Siguen abiertos: A3 (desarrollo del modelo de IA desde la sección 3.8 de U2, que requiere el documento), las correcciones del docente, las etiquetas de versión v2.10.1 a v2.12.0 y la lectura y aceptación de la versión 1.0.", "Abierta"]])]
x = append_section(x, "".join(sec))
open(p, "w", encoding="utf-8").write(x)
print("ok")
