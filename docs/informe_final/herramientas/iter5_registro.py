# -*- coding: utf-8 -*-
"""Iteración 5: registro de revisiones v0.12 -> v0.13 (capítulos XI y XIII)."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from registro_lib import *
p = os.path.join(sys.argv[1], "word", "document.xml")
x = open(p, encoding="utf-8").read()
x = set_version(x, "0.13 (23-11-2026)")
x = add_version_rows(x, [
    ["0.9", "23-11-2026", "Informe maestro", "Iteración 5: redacción inicial de los capítulos XI (KPI con implementación y estado de medición; propuesta de SLA) y XIII (disponibilidad, continuidad y mantención contrastadas con el estado del entorno de demostración). Tablas 28 a 31 y 38 a 42.", "Respaldo previo: Proyecto_Aurora_Informe_Final_Maestro_v0.8_pre-it5.docx."],
    ["0.13", "23-11-2026", "Registro de revisiones", "Sección 4.9: observaciones N-11-01 a N-11-05 y N-13-01 a N-13-05.", "—"]])
sec = [H("4.9. Iteración 5 – Capítulos XI y XIII"),
       P("Fecha: 23-11-2026. Fuentes: informe de Unidad 2 (secciones IV y VI, Tablas 30 a 35 y 42 a 50), código del dashboard (backend/app/services/dashboard_service.py, middleware.py), configuración de despliegue (deploy/docker-compose.prod.yml, .github/workflows) y docs/ESTADO_AWS.md (16-11-2026)."),
       TABLE(OBS_W, [
        ["ID", "Capítulo", "Observación", "Acción", "Estado"],
        ["N-11-01", "V / XI", "Definición inconsistente del indicador de desempeño del modelo: capítulo V «precisión ≥ 90% en piloto»; Unidad 2 K5 «AUC y sensibilidad ≥ 0,80» (óptimo ≥ 0,85); plataforma: exactitud respecto de la validación médica ≥ 0,85 con mínimo de 30 imágenes; el comentario del código indica «≥ 90 %».", "El capítulo XI registra la meta implementada y declara la diferencia. Decidir una definición única y corregir el capítulo V y el comentario del código.", "Pendiente de decisión"],
        ["N-11-02", "XI", "K9 en Unidad 2 es el tiempo de restablecimiento de incidentes P1; la plataforma solo cuenta errores 5xx.", "Declarado en la Tabla 28; medir K9 desde el registro de incidentes.", "Pendiente"],
        ["N-11-03", "V / XI", "Las metas del capítulo V de adopción a seis meses y desviación presupuestaria no tienen KPI en la especificación de Unidad 2.", "Declarado en el capítulo XI; decidir si se agregan indicadores o se ajusta el capítulo V.", "Pendiente de decisión"],
        ["N-11-04", "XI.11.2", "La propuesta de SLA de Unidad 2 identifica a Nueva Clínica Cordillera como cliente y fija la firma al 31-10-2026; no hay evidencia de firma ni de compromiso formal.", "Institución usuaria «por definir»; SLA presentados como propuesta.", "Resuelto en v0.9"],
        ["N-11-05", "XI", "Ningún KPI tiene medición en operación real; los valores del dashboard de demostración se calculan sobre datos ficticios.", "Declarado en el capítulo.", "Informativo"],
        ["N-13-01", "XIII.13.1", "Medidas de disponibilidad planificadas sin implementar: Cloudflare, alarmas de disponibilidad, monitor externo, Multi-AZ, prueba de capacidad; el servicio de inferencia depende de un equipo personal.", "Tabla 38 contrasta planificado y estado; requisitos mínimos para un piloto declarados.", "Pendiente (piloto)"],
        ["N-13-02", "XIII.13.2", "La prueba de restauración de un respaldo figura como pendiente en ESTADO_AWS.md (punto 2, «antes de la defensa»).", "Ejecutar y documentar la restauración; actualizar la Tabla 40.", "Pendiente"],
        ["N-13-03", "XIII.13.2", "Las copias de respaldo en otra región y fuera de AWS (Cloudflare R2) planificadas en Unidad 2 no están implementadas.", "Escenario declarado como no preparado.", "Pendiente (piloto)"],
        ["N-13-04", "XIII.13.3", "El despliegue en el servidor es manual (Session Manager); el despliegue automático con OIDC planificado en Unidad 2 no se implementó.", "Descrito tal como opera.", "Informativo"],
        ["N-13-05", "XIII.13.3", "Incidente real documentado: pérdida temporal de acceso a la consola de AWS (15-11-2026), resuelta el mismo día sin afectar el sitio.", "Incluido como ejemplo de gestión de incidentes.", "Resuelto en v0.9"]])]
x = append_section(x, "".join(sec))
open(p, "w", encoding="utf-8").write(x)
print("ok")
