# -*- coding: utf-8 -*-
"""Iteración 1: registro de revisiones v0.8 -> v0.9 (capítulos VII y VIII)."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from registro_lib import *

p = os.path.join(sys.argv[1], "word", "document.xml")
x = open(p, encoding="utf-8").read()
x = set_version(x, "0.9 (23-11-2026)")
x = add_version_rows(x, [
    ["0.5", "23-11-2026", "Informe maestro", "Iteración 1: redacción inicial de los capítulos VII (tipo de arquitectura, capas con nivel de evidencia, decisiones de arquitectura, evolución respecto de Unidad 1) y VIII (organización, procesos de negocio, relación con la solución). Tablas 10 a 13.", "Respaldo previo: Proyecto_Aurora_Informe_Final_Maestro_v0.4_pre-it1.docx."],
    ["0.9", "23-11-2026", "Registro de revisiones", "Sección 4.5 con observaciones N-07-01 a N-07-06.", "—"]])
sec = [H("4.5. Iteración 1 – Capítulos VII y VIII"),
       P("Fecha: 23-11-2026. Fuentes: formulación de Unidad 1 (cap. 7 y 8; Figuras 5 a 8), informe de Unidad 2 (arquitectura N-tier y monolito modular) y revisión de la estructura del repositorio (backend/app, backend/inference_service, deploy/Caddyfile, deploy/docker-compose.prod.yml, docs/despliegue_aws.md). La plantilla institucional no estaba disponible: la subdivisión de VII (7.1) y VIII (8.1 a 8.3) sigue la de Unidad 1."),
       TABLE(OBS_W, [
        ["ID", "Capítulo", "Observación", "Acción", "Estado"],
        ["N-07-01", "VII", "Los diagramas de arquitectura de Unidad 1 incluyen Grafana, Prometheus, comunicación gRPC, Cloudflare, imágenes DICOM en S3 y región sa-east-1. En el repositorio no se identifican Grafana, Prometheus, gRPC ni Cloudflare; la carga admite PNG y JPEG; TLS lo gestiona Caddy (Let's Encrypt) y el entorno de demostración está en us-east-2.", "No se reproducen los diagramas de Unidad 1; la diferencia se declara como evolución y los diagramas vigentes se elaborarán en el capítulo X.", "Resuelto en v0.5"],
        ["N-07-02", "VIII", "El organigrama de Unidad 1 incluye un cuarto rol «QA Tester (part-time)» sin registro de incorporación (relacionado con N-06-08).", "Presentado como rol contemplado «No asignado» (Tabla 12).", "En curso; confirmar con el equipo"],
        ["N-07-03", "VIII", "El diagrama de procesos de Unidad 1 ubica la revisión de antecedentes y el «registro de resultado/diagnóstico» en el carril del sistema.", "Revisión y evaluación asignadas al profesional médico; se aclara que la plataforma no emite diagnósticos (Tabla 13).", "Resuelto en v0.5"],
        ["N-07-04", "VII, VIII", "No se dispone de la plantilla institucional para confirmar los apartados exigidos en VII y VIII.", "Contrastar cuando se reciba la plantilla.", "Pendiente"],
        ["N-07-05", "VIII", "Unidad 2 indica que la plataforma no requiere integración con RIS/PACS. Consecuencia no declarada antes: posible doble registro de antecedentes e imágenes respecto de los sistemas de la institución.", "Declarada como limitación en 8.3.", "Resuelto en v0.5"],
        ["N-07-06", "VII, X", "El servicio de inferencia (backend/inference_service, FastAPI) existe en el repositorio, pero su funcionamiento, modelo y pruebas no se han inspeccionado (relacionado con N-03-16 a N-03-21).", "Inspección programada en la iteración 3.", "Pendiente"]]),
       P("Nivel de evidencia: la estructura de capas y módulos se verificó por inspección de la organización del código fuente; no se ejecutaron pruebas en esta iteración. Las afirmaciones sobre el entorno desplegado provienen de la documentación del repositorio.")]
x = append_section(x, "".join(sec))
open(p, "w", encoding="utf-8").write(x)
print("ok")
