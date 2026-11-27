# -*- coding: utf-8 -*-
"""Iteración 2: registro de revisiones v0.9 -> v0.10 (capítulo IX y decisión D-07-01)."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from registro_lib import *

p = os.path.join(sys.argv[1], "word", "document.xml")
x = open(p, encoding="utf-8").read()
x = set_version(x, "0.10 (23-11-2026)")
x = add_version_rows(x, [
    ["0.6", "23-11-2026", "Informe maestro", "Iteración 2: redacción inicial del capítulo IX (criterios, AHP, escala, análisis cualitativo, matriz ponderada, sensibilidad, versiones reales y servicios TI). Tablas 14 a 21.", "Respaldo previo: Proyecto_Aurora_Informe_Final_Maestro_v0.5_pre-it2.docx."],
    ["0.10", "23-11-2026", "Registro de revisiones", "Sección 4.6: decisión D-07-01 y observaciones N-09-01 a N-09-08.", "—"]])
sec = [H("4.6. Iteración 2 – Capítulo IX y decisión sobre la arquitectura"),
       P("Fecha: 23-11-2026."),
       TABLE([1000, 3400, 5824], [
        ["ID", "Tema", "Decisión aprobada por el usuario (23-11-2026)"],
        ["D-07-01", "Arquitectura a documentar", "El informe documenta la arquitectura actual implementada, que no requiere cambios arquitectónicos. Las mejoras menores futuras quedan fuera del alcance de esta entrega. Los diagramas del capítulo X se elaborarán a partir de la arquitectura actual y no de los diagramas de Unidad 1."]]),
       P("Fuentes de la iteración 2: informe de Unidad 2 (sección II, Tablas 1 a 6 y 12 a 14) y archivos del repositorio (backend/requirements.txt, backend/requirements-dev.txt, backend/inference_service/requirements.txt, package.json, backend/Dockerfile, .github/workflows, deploy/docker-compose.prod.yml, docs/ESTADO_AWS.md). Los pesos AHP, la consistencia y los totales se recalcularon con un script."),
       TABLE(OBS_W, [
        ["ID", "Capítulo", "Observación", "Acción", "Estado"],
        ["N-09-01", "IX.9.2", "La Tabla 12 de Unidad 2 tiene versiones desactualizadas: FastAPI 0.115 (actual 0.135.4), python-jose (reemplazado por PyJWT 2.15.1), Pillow 11.0 (13.0.0), jsPDF 3.0 (4.2); no incluye React Router 7, boto3, moto ni el servicio de inferencia con PyTorch 2.6.0, Ultralytics 8.4.173 y pydicom 3.0.2.", "Tabla 20 con versiones verificadas en archivos de dependencias al 23-11-2026.", "Resuelto en v0.6"],
        ["N-09-02", "IX.9.1", "Recálculo AHP: pesos 32,6/24,7/14,2/14,2/14,2, λmáx 5,058, RC 0,013 y totales con pesos adoptados coinciden con Unidad 2. Con pesos AHP hay diferencias de redondeo de 0,01 (Angular 4,12 frente a 4,11; Django 4,51 frente a 4,50).", "Tablas 15, 18 y 19 con valores recalculados.", "Resuelto en v0.6"],
        ["N-09-03", "IX / XII", "Unidad 2 cita 206 pruebas aprobadas y 96% de cobertura (versión 2.2.0); el dato no corresponde a la versión actual.", "No se traslada al capítulo IX; la suite se ejecutará en la iteración 4.", "Pendiente"],
        ["N-09-04", "IX / X", "Unidad 2 indica 14 tablas en la base de datos; los modelos actuales declaran 18 tablas (__tablename__) y la documentación de la migración a RDS menciona 19 tablas copiadas.", "Verificar en el capítulo X (modelo de datos) con las migraciones.", "Pendiente"],
        ["N-09-05", "IX.9.2", "Locust, Prometheus y Grafana figuraban como planificados en Unidad 2 y no se encuentran implementados; Cloudflare no fue adoptado; el flujo OWASP ZAP está configurado a pedido, sin resultados revisados.", "Declarado con su estado en las Tablas 20 y 21.", "Resuelto en v0.6; resultados ZAP pendientes (cap. XII)"],
        ["N-09-06", "IX / XIII", "La evaluación de Unidad 2 consideró la región de São Paulo; el entorno de demostración usa us-east-2 por asignación de la cuenta, con datos ficticios. Para datos reales falta decidir región y condiciones de tratamiento.", "Declarado en 9.1.5; decisión pendiente del equipo.", "Pendiente"],
        ["N-09-07", "IX / XIV", "La licencia AGPL-3.0 de YOLO exige licencia comercial para un servicio SaaS cerrado.", "Considerar en factibilidad económica (cap. XIV) y recomendaciones.", "Pendiente"],
        ["N-09-08", "IX / XVII", "Los porcentajes de adopción de Stack Overflow (2024) citados por Unidad 2 no se verificaron contra la fuente.", "Se redactó una afirmación comparativa sin porcentajes; verificar la fuente al normalizar referencias.", "Pendiente"]])]
x = append_section(x, "".join(sec))
open(p, "w", encoding="utf-8").write(x)
print("ok")
