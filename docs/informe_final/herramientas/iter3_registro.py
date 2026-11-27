# -*- coding: utf-8 -*-
"""Iteración 3: registro de revisiones v0.10 -> v0.11 (capítulo X e inspección del servicio de inferencia)."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from registro_lib import *

p = os.path.join(sys.argv[1], "word", "document.xml")
x = open(p, encoding="utf-8").read()
x = set_version(x, "0.11 (23-11-2026)")
x = add_version_rows(x, [
    ["0.7", "23-11-2026", "Informe maestro", "Iteración 3: redacción inicial del capítulo X (BPMN, casos de uso, componentes, modelo lógico y físico, topología, infraestructura, arquitectura y componente de análisis automatizado). Figuras 2 a 10 y Tablas 22 a 27.", "Respaldo previo: Proyecto_Aurora_Informe_Final_Maestro_v0.6_pre-it3.docx. Diagramas regenerables con herramientas/diagramas_cap10.py."],
    ["0.11", "23-11-2026", "Registro de revisiones", "Sección 4.7: observaciones N-10-01 a N-10-09 y evidencia de las observaciones técnicas del componente inference.", "—"]])
sec = [H("4.7. Iteración 3 – Capítulo X e inspección del servicio de inferencia"),
       P("Fecha: 23-11-2026. Fuentes: informe de Unidad 2 (sección III, Figuras 1 a 10, Tablas 15 a 29), código del repositorio (backend/app, backend/alembic, backend/inference_service, deploy/) y documentación (docs/ESTADO_AWS.md, docs/despliegue_aws.md). El modelo de datos se extrajo de los modelos SQLAlchemy con un script (herramientas/schema_modelos.json). Aplicando D-07-01, los diagramas de componentes, topología, infraestructura y arquitectura se elaboraron desde la arquitectura actual."),
       TABLE(OBS_W, [
        ["ID", "Capítulo", "Observación", "Acción", "Estado"],
        ["N-10-01", "X", "Los diagramas de componentes, topología, infraestructura y arquitectura de Unidad 2 representan el diseño objetivo (Cloudflare, sa-east-1, EC2 t3.large, Nginx, Prometheus/Grafana, AWS Backup, Cloudflare R2, inferencia en EC2), distinto de lo desplegado.", "Diagramas nuevos generados desde código y documentación del despliegue (Figuras 6, 8, 9 y 10).", "Resuelto en v0.7"],
        ["N-10-02", "X.10.2", "El diagrama de casos de uso de Unidad 2 marca CU17 «Cambiar contraseña» como planificado (implementado en 2.3.0) y no incluye las funciones de privacidad de 2.4.0.", "Diagrama y catálogo actualizados; se agrega CU18 «Gestionar solicitudes de titulares de datos» (identificador nuevo, a confirmar por el equipo).", "Resuelto en v0.7; confirmar CU18"],
        ["N-10-03", "X.10.4", "Unidad 2 informa 14 tablas; los modelos actuales definen 18 (19 con la tabla de versiones de Alembic). Cierra N-09-04.", "Modelo lógico generado desde el código (Figura 7) y modelo físico (Tabla 24).", "Resuelto en v0.7"],
        ["N-10-04", "X.10.8", "El modelo de IA fue reentrenado después de Unidad 2 (división por paciente, entrada 672 × 1024, YOLO11s agregado). Métricas actuales según README del servicio: AUC 0,838; sensibilidad 0,849; especificidad 0,641; mAP50 YOLO 0,538. Los scripts y datos de entrenamiento no están en el repositorio, por lo que las métricas no son reproducibles.", "Presentadas como métricas declaradas del prototipo, sin carácter clínico. Obtener del equipo el registro de entrenamiento si se requiere acreditarlas.", "Pendiente"],
        ["N-10-05", "X.10.8 / XV", "El umbral 0,35 está fijado como constante en analyzer.py; Unidad 2 lo planteaba como parámetro clínico configurable validado por un médico (ajuste A2). No hay evidencia de validación médica del umbral.", "Declarado como limitación; considerar en el capítulo XV (decisión sobre el modelo, hito del 01-11).", "Pendiente"],
        ["N-10-06", "X", "El servicio de inferencia lee DICOM, pero la plataforma solo admite cargas PNG y JPEG; los reportes incluyen metadatos de tipo DICOM.", "Declarado en el capítulo; coherente con el alcance (sin integración PACS).", "Informativo"],
        ["N-10-07", "X.10.5–10.6", "La infraestructura se describe a partir de docs/ESTADO_AWS.md (16-11-2026), no de una inspección directa de la cuenta de AWS.", "Indicado en el texto. Verificación opcional con acceso a la cuenta.", "Pendiente"],
        ["N-10-08", "X / XIII", "Inconsistencia documental en ESTADO_AWS.md: la tabla de recursos indica «Falta Juan» en Tailscale, mientras los puntos 5 y 6 del plan registran la conexión del equipo con GPU el 11-11-2026.", "Se usa la conexión registrada; aclarar con el equipo.", "Pendiente"],
        ["N-10-09", "Formato", "Los diagramas anchos (BPMN, topología, arquitectura) quedan pequeños en página vertical. El título de plantilla «Diccionario de datos (puede ir como anexo)» conserva la indicación entre paréntesis.", "Evaluar páginas horizontales y ajuste de títulos en la iteración 10 (cierre editorial).", "Pendiente"]]),
       P("Evidencia sobre las observaciones técnicas del componente inference (registradas en la sección 3 como identificación del modelo, contrato de integración, procesamiento de imágenes, persistencia, pruebas del proveedor y validación clínica):"),
       TABLE([2200, 5624, 2400], [
        ["Observación técnica", "Evidencia obtenida por lectura directa del código (23-11-2026)", "Estado"],
        ["Identificación del modelo", "MODEL_VERSION «cnn-resnet18-672x1024+yolo11s-masa-1280» en analyzer.py; pesos cnn_proporcion.pt y yolo_masas.pt versionados en el repositorio (commit 3eaf005, 10-11-2026).", "Resuelto (verificado en código)"],
        ["Contrato de integración", "app.py: POST /predict multipart, GET /health, token Bearer con comparación en tiempo constante, límite 60 MB, códigos 400/401/413/415. providers.py: tiempo máximo configurable, campos obligatorios, rango de confianza 0–100, respaldo simulado.", "Resuelto (verificado en código)"],
        ["Procesamiento de imágenes", "preprocessing.py: escala de grises desde PNG, JPEG o DICOM; CLAHE (2,0; 8×8); 672 × 1024 sin deformación para la CNN; lado mayor 1.280 para YOLO.", "Resuelto (verificado en código)"],
        ["Persistencia y trazabilidad", "Tabla inference_results con versión del modelo, is_simulated, clinically_validated, tiempo de proceso y detecciones; relación 1:1 con la imagen; validación médica en ai_validations.", "Resuelto (verificado en código)"],
        ["Pruebas del proveedor", "test_inference_model.py cubre token, contrato, fallas, respaldo simulado, reanálisis y concordancia del contrato servicio–plataforma.", "Pruebas identificadas; ejecución en iteración 4"],
        ["Validación clínica", "CLINICALLY_VALIDATED = False en el código; métricas solo de conjuntos públicos; sin validación externa ni clínica.", "Sin validación clínica (fuera del alcance acreditable)"]])]
x = append_section(x, "".join(sec))
open(p, "w", encoding="utf-8").write(x)
print("ok")
