# -*- coding: utf-8 -*-
"""Iteración 13: registro de revisiones v0.21 -> v0.22 (rendimiento en AWS y versión 2.10.2).
Uso: python3 iter13_registro.py <dir_registro>"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from registro_lib import *
p = os.path.join(sys.argv[1], "word", "document.xml")
x = open(p, encoding="utf-8").read()
x = set_version(x, "0.22 (24-11-2026)")
x = add_version_rows(x, [
    ["1.3-rc", "24-11-2026", "Informe maestro",
     "Iteración 13: nuevo apartado de XII sobre la prueba de rendimiento en el entorno de demostración (PC-01 con la versión 2.10.2: 100 usuarios, 0 errores, p95 de 14.979 ms, no cumple; la meta se cumple hasta 25 usuarios) y el segundo defecto bajo carga corregido en la 2.10.2. Actualizados resumen, abstract, XI, XII, XIII (versión publicada 2.10.2), 14.3.1 y XVI.",
     "Respaldo previo: Proyecto_Aurora_Informe_Final_Maestro_v1.2-rc_pre-it13.docx. Evidencia: evidencias/rendimiento_aws_2026-11-24/."],
    ["0.22", "24-11-2026", "Registro de revisiones", "Sección 4.18: prueba de rendimiento en AWS y versión 2.10.2.", "—"]])
sec = [H("4.18. Iteración 13 – Prueba de rendimiento en el entorno de demostración"),
       P("Fecha: 24-11-2026. El usuario pidió medir el rendimiento en AWS, eligió hacerlo sobre una copia de la base de datos y luego autorizó desplegar la versión 2.10.2 y repetir la medición."),
       TABLE([1300, 6000, 2924], [
        ["ID", "Descripción", "Estado"],
        ["D-13-01", "La prueba en AWS se hizo con la API apuntada a una copia de la base en un esquema temporal (carga) de la misma RDS, para no escribir en la bitácora de auditoría ni en los datos del entorno (la bitácora no admite borrado). La clave del usuario de prueba se cambió solo en la copia. La copia se eliminó al terminar y se verificó la vuelta a la base real (316 casos). No se creó una instancia de RDS aparte.", "Aplicada"],
        ["D-13-02", "La serie válida se generó desde el propio servidor: el generador externo pasaba por un proxy de salida que limita las conexiones abiertas y no sostuvo 100 usuarios. El uso de CPU del generador fue bajo y las cifras con 10 y 25 usuarios coinciden con las del generador externo.", "Aplicada"],
        ["D-13-03", "Segundo defecto bajo carga (bloqueo entre hilos y conexiones con 100 usuarios en la 2.10.1), reproducido en local y corregido en la 2.10.2 con un límite de solicitudes simultáneas; 321 pruebas aprobadas; desplegada el 24-11-2026 con respaldo previo.", "Aplicada"],
        ["N-12-01", "Cerrada: el rendimiento del entorno de demostración se midió (≈ 20 solicitudes/s; p95 ≤ 3 s hasta 25 usuarios; con 100, p95 de 14.979 ms y 0 errores).", "Cerrada"],
        ["N-13-01", "La meta p95 ≤ 3 s con 100 usuarios no se cumple en el entorno de demostración; requiere más procesos, una instancia mayor u optimizar la lista de casos y las métricas del dashboard. Es una decisión de costo del equipo.", "Abierta"],
        ["N-13-02", "Durante las dos series (02:37–03:00 y 03:30–03:59 UTC), el entorno de demostración atendió con la copia de la base o estuvo bloqueado por el defecto; cualquier dato ingresado en ese lapso quedó en la copia y se eliminó con ella.", "Informativa"],
        ["N-13-03", "Hipótesis no verificada: la baja de rendimiento a lo largo de la serie (de 20,7 a 16,5 solicitudes/s) podría deberse a que las métricas del dashboard se calculan sobre request_metrics, que crece con cada solicitud.", "Abierta"]])]
x = append_section(x, "".join(sec))
open(p, "w", encoding="utf-8").write(x)
print("ok")
