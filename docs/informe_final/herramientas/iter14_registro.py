# -*- coding: utf-8 -*-
"""Iteración 14: registro de revisiones v0.22 -> v0.23 (ZAP, restauración y monitoreo).
Uso: python3 iter14_registro.py <dir_registro>"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from registro_lib import *
p = os.path.join(sys.argv[1], "word", "document.xml")
x = open(p, encoding="utf-8").read()
x = set_version(x, "0.23 (24-11-2026)")
x = add_version_rows(x, [
    ["1.4-rc", "24-11-2026", "Informe maestro",
     "Iteración 14: nuevo apartado de XII sobre el escaneo OWASP ZAP (PS-04 aprobado: 0 altas) y la prueba de restauración (completa). Actualizados resumen, abstract, XI (K3 con monitoreo desde el 24-11), XII, XIII (monitoreo y continuidad), 14.3.1, XV y XVI.",
     "Respaldo previo: Proyecto_Aurora_Informe_Final_Maestro_v1.3-rc_pre-it14.docx. Evidencia: evidencias/zap_2026-11-24/ y evidencias/restauracion_2026-11-24/."],
    ["0.23", "24-11-2026", "Registro de revisiones", "Sección 4.19: escaneo de seguridad, restauración y monitoreo.", "—"]])
sec = [H("4.19. Iteración 14 – Escaneo de seguridad, restauración y monitoreo"),
       P("Fecha: 24-11-2026. El usuario eligió ejecutar la prueba de restauración, el escaneo ZAP y el monitoreo con alarmas, y aprobó usar su correo para las alertas."),
       TABLE([1300, 6000, 2924], [
        ["ID", "Descripción", "Estado"],
        ["D-14-01", "Escaneo ZAP baseline con el flujo del repositorio, sobre el sistema levantado dentro del CI (no sobre el entorno de demostración): 0 altas, 1 media y 3 bajas. Se corrigieron dos bajas (COOP y CORP en el Caddyfile, desplegado el 24-11) y se aceptaron la media (style-src 'unsafe-inline') y una baja (sin COEP).", "Aplicada"],
        ["D-14-02", "Prueba de restauración del volcado diario en un esquema temporal de la misma RDS: 19 tablas coincidentes, 258 imágenes con archivo en S3 y 5 descifradas con hash correcto; unos 3 s.", "Aplicada"],
        ["D-14-03", "Monitoreo: chequeo de /health cada minuto desde el servidor hacia CloudWatch Logs, filtro de métrica y alarmas por correo (SNS) ante falta de respuesta o falla de la instancia, todo en us-east-2. El chequeo de salud de Route 53 se descartó porque sus métricas solo existen en us-east-1, donde la política del proyecto de AWS bloquea SNS. Aviso probado: la alarma pasó por ALARM durante la instalación y volvió a OK a las 13:36 UTC.", "Aplicada"],
        ["N-14-01", "El monitoreo corre en el mismo servidor: detecta la caída de la API, de Caddy o de la instancia (por falta de chequeos), pero no una falla de DNS o de red vista desde Internet. Un monitor externo a AWS queda como recomendación.", "Abierta"],
        ["N-14-02", "El escaneo no cubrió la API autenticada ni incluyó ataques (escaneo activo).", "Abierta"],
        ["N-14-03", "K3 cuenta con medición desde el 24-11-2026; el indicador mensual requiere un mes de datos.", "Abierta"]])]
x = append_section(x, "".join(sec))
open(p, "w", encoding="utf-8").write(x)
print("ok")
