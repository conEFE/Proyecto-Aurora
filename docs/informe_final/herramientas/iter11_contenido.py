# -*- coding: utf-8 -*-
"""Contenido de la iteración 11: ajustes por plantilla y rúbrica de defensa (EA5)."""

# --- (b) Capítulo IV: soluciones existentes y diferenciación -------------------------------------------
SOLUCIONES = [
 ("h3", "Soluciones existentes y diferenciación de Proyecto Aurora"),
 ("p", "La aplicación de inteligencia artificial a la mamografía cuenta con productos comerciales consolidados. Transpara, de ScreenPoint Medical, obtuvo en 2018 la autorización 510(k) de la Administración de Alimentos y Medicamentos de Estados Unidos (FDA) para la detección de cáncer de mama en mamografías de tamizaje y cuenta con marcado CE (Applied Radiology, 2018). Lunit INSIGHT MMG obtuvo la misma autorización en 2021, después de contar con marcado CE y aprobación comercial en más de 35 países (Lunit, 2021). ProFound AI, de iCAD, analiza tomosíntesis digital de mama y asigna a cada caso una puntuación de certeza de malignidad que puede utilizarse para ordenar la lista de lectura (iCAD, 2023). Estos productos son sistemas de detección y diagnóstico asistido por computador (CADe/CADx): analizan la imagen, marcan hallazgos y entregan una puntuación por examen, y se integran al flujo de imagenología mediante las estaciones de lectura y el PACS de la institución."),
 ("p", "La evidencia sobre su uso para priorizar o redistribuir la lectura es favorable pero aún acotada. En una simulación retrospectiva con 7.364 mujeres de un centro sueco, el uso de un detector comercial para derivar los exámenes de muy bajo puntaje fuera de la lectura del radiólogo habría reducido la carga de lectura en más de la mitad (Dembrower et al., 2020), y el ensayo aleatorizado MASAI mostró una tasa de detección similar o superior a la doble lectura habitual con 44% menos lecturas de los radiólogos (Lång et al., 2023). En contraste, una revisión sistemática encargada por el Comité Nacional de Tamizaje del Reino Unido concluyó que la calidad metodológica de los estudios disponibles era baja y que la evidencia no permitía aún juzgar la exactitud de la IA en programas de tamizaje (Freeman et al., 2021)."),
 ("p", "La {T:solex} compara estas soluciones con Proyecto Aurora. La comparación no pretende equiparar capacidades: los productos citados son dispositivos médicos autorizados, con validación clínica publicada, mientras que Aurora es un prototipo académico sin validación clínica."),
 ("tabla", "Comparación de Proyecto Aurora con soluciones existentes", "solex",
  "Fuente: Elaboración propia a partir de Applied Radiology (2018), Lunit (2021), iCAD (2023) y de la documentación del repositorio de Proyecto Aurora (23-11-2026).",
  [1700, 2280, 2280, 2284],
  [["Dimensión", "Productos CADe/CADx (Transpara, Lunit INSIGHT MMG, ProFound AI)", "Uso típico en la institución", "Proyecto Aurora"],
   ["Objeto principal", "Análisis de la imagen: hallazgos y puntaje de sospecha por examen", "Apoyo a la lectura del radiólogo", "Gestión del caso: paciente, consentimiento, exámenes, triage, revisión, reporte e indicadores"],
   ["Criterio de priorización", "Puntaje de la imagen", "Ordenar o dividir la lista de lectura", "Reglas clínicas configurables (BI-RADS, síntomas, antecedentes, edad) combinadas con el resultado del modelo como un insumo más"],
   ["Integración requerida", "PACS y estaciones de lectura; formato DICOM", "Proyecto de integración con el proveedor", "Navegador web; no requiere HIS, RIS ni PACS (DICOM pendiente)"],
   ["Condición regulatoria", "Autorización FDA 510(k) y marcado CE", "Uso clínico autorizado", "Prototipo sin autorización sanitaria ni validación clínica; resultados de apoyo"],
   ["Trazabilidad y privacidad", "Según el producto y la integración", "Gestionada por la institución", "Consentimiento versionado, solicitudes de titulares, bitácora de auditoría y evaluación médica separada del resultado automatizado"],
   ["Costo y despliegue", "Licencia comercial", "Contrato con el proveedor", "Stack de código abierto; demostración en la nube por cerca de USD 26 mensuales; suscripción proyectada de $1.200.000 mensuales"]]),
 ("p", "La innovación de Proyecto Aurora no reside en el algoritmo de detección, que reutiliza una familia de modelos conocida (YOLO), sino en la integración: un flujo de trabajo completo para la sospecha de cáncer de mama que une el registro clínico básico, el cumplimiento de privacidad y una priorización explicable y configurable por los médicos, y que admite el resultado de un modelo de IA como información complementaria sin depender de él (el sistema opera con un proveedor desacoplado y con respaldo simulado). Esta combinación apunta a establecimientos medianos sin integración PACS avanzada, para los que un producto CADe supone una barrera de costo e integración. Su valor efectivo frente a esas soluciones debe demostrarse con datos reales en un piloto (capítulo XVI)."),
]

# --- (d) 8.3: sustentabilidad de la solución -----------------------------------------------------------
SUSTENTABILIDAD = [
 ("h4", "Sustentabilidad de la solución"),
 ("p", "La sustentabilidad de la solución se analiza en cuatro dimensiones. En lo operativo, el flujo propuesto reutiliza los roles existentes (personal administrativo, médico y administrador), no exige cambios en los sistemas de la institución y deja la configuración clínica del triage en manos de los médicos, sin modificar código; el costo es el doble registro mientras no exista interoperabilidad. En lo técnico, el stack es de código abierto y ampliamente adoptado, la arquitectura monolítica modular puede mantenerla un equipo pequeño, y la calidad se sostiene con integración continua y pruebas automatizadas (capítulo XII); la prueba de carga ya permitió detectar y corregir un defecto de concurrencia antes de un piloto. En lo económico, la operación de la demostración cuesta cerca de USD 26 mensuales y la evaluación de la fase comercial resulta positiva en el escenario base, condicionada a la captación de clientes (capítulo XIV). En lo organizacional, los procedimientos de cambios, incidentes, respaldo y continuidad del capítulo XIII permiten operar el servicio con responsables definidos."),
 ("p", "Los factores que hoy limitan la sustentabilidad son tres: la dependencia del servicio de inferencia de un equipo personal, la ausencia de un compromiso formal de una institución usuaria y la falta de validación clínica del modelo. Los tres se abordan en las recomendaciones del capítulo XVI."),
]

# --- (d) IX: integración del stack ------------------------------------------------------------------------
INTEGRACION = [
 ("h4", "Integración y complementariedad de las herramientas"),
 ("p", "Las herramientas seleccionadas se complementan a lo largo de una única ruta de solicitud y de un único ciclo de entrega. El navegador carga la aplicación React compilada con Vite, que Caddy sirve como sitio estático y protege con encabezados de seguridad y TLS de Let's Encrypt; el mismo Caddy redirige las rutas /api a la API FastAPI. La API valida los datos con Pydantic, aplica la autorización por rol con JWT y persiste la información con SQLAlchemy en PostgreSQL, cuyo esquema evoluciona únicamente mediante migraciones Alembic. Las imágenes se cifran en la aplicación con Fernet y se guardan en S3 con cifrado SSE-KMS; el análisis automatizado se solicita por HTTP al servicio de inferencia, que corre en el equipo con GPU conectado por Tailscale, y si este no responde la API recurre al proveedor simulado, con su marca visible. El reporte PDF se genera en el navegador con jsPDF a partir de los datos de la API. La {T:integ} resume los puntos de integración."),
 ("tabla", "Puntos de integración entre las herramientas del stack", "integ",
  "Fuente: Elaboración propia a partir del código del repositorio (deploy/Caddyfile, backend/app, .github/workflows) al 24-11-2026.",
  [2100, 2100, 4344],
  [["Origen", "Destino", "Contrato de integración"],
   ["React + TypeScript (navegador)", "API FastAPI", "HTTPS bajo /api; JSON con esquemas Pydantic; token JWT en cada solicitud"],
   ["Caddy", "API y sitio estático", "Proxy inverso, TLS automático, compresión, límite de carga de 64 MB y política de seguridad de contenido"],
   ["API FastAPI", "PostgreSQL (RDS)", "SQLAlchemy 2; esquema controlado por migraciones Alembic reversibles"],
   ["API FastAPI", "Amazon S3", "Imagen cifrada con Fernet; SSE-KMS en el bucket; acceso por rol de instancia, sin llaves en el código"],
   ["API FastAPI", "Servicio de inferencia", "HTTP con token compartido sobre Tailscale; tiempo máximo y respaldo simulado"],
   ["Contenedores", "CloudWatch Logs", "Controlador awslogs; retención de 30 días"],
   ["GitHub Actions", "Repositorio e imágenes", "Análisis estático, pruebas, auditoría de dependencias, construcción, prueba de humo y publicación en GitHub Container Registry"]]),
 ("p", "La consistencia entre capas se apoya en dos decisiones: el contrato de la API se documenta automáticamente con OpenAPI a partir de los mismos esquemas que validan los datos, y todos los componentes se empaquetan como imágenes de contenedor que se ejecutan igual en desarrollo, en la integración continua y en el servidor."),
]

# --- (c) XIV: estudio de factibilidad integral -----------------------------------------------------
FACTIBILIDAD = [
 ("h4", "Síntesis de factibilidad técnica, operativa, económica, legal y ambiental"),
 ("p", "La Unidad 2 evaluó la factibilidad técnica, económica e implementativa del proyecto. Esta síntesis actualiza esa evaluación con el estado al cierre y la amplía a las dimensiones operativa, legal y ambiental ({T:factib}). En cada dimensión se distingue lo verificado de lo que queda condicionado."),
 ("tabla", "Síntesis de factibilidad del proyecto", "factib",
  "Fuente: Elaboración propia a partir del informe de Unidad 2 (estudio de factibilidad) y de los capítulos IX a XV de este informe; Amazon Web Services (s. f.-a) para la eficiencia energética declarada de Graviton.",
  [1300, 4244, 1500, 1500],
  [["Dimensión", "Fundamento", "Resultado", "Condición"],
   ["Técnica", "Stack de código abierto, maduro y documentado; prototipo desplegado (versión 2.10.0); pruebas automatizadas aprobadas con 97% de cobertura; prueba de rendimiento local con p95 bajo la meta de 3 s, tras corregir un bloqueo bajo carga detectado por esa misma prueba; modelo propio conectado con respaldo simulado", "Factible", "Inferencia en equipo personal; DICOM y prueba de restauración pendientes"],
   ["Operativa", "Flujo basado en navegador y en los roles existentes; no requiere HIS, RIS ni PACS; triage configurable por los médicos; revisión funcional con dos médicos y una enfermera el 20-11-2026", "Factible con condiciones", "Doble registro; capacitación planificada y no ejecutada; soporte a cargo del equipo"],
   ["Económica", "Demostración por cerca de USD 26 mensuales cubierta con créditos; fase comercial con VAN de $134.801.449, TIR de 45,0% y recuperación en 2,84 años", "Factible en el escenario base", "Captar al menos el 75,2% de los clientes proyectados"],
   ["Legal", "Consentimiento versionado, derechos de los titulares, bloqueo y exportación, bitácora de solo agregado y cifrado; demostración solo con datos ficticios", "Factible para la demostración", "Transferencia internacional (us-east-2), acuerdo de tratamiento de datos y calificación como dispositivo médico por resolver antes de usar datos reales"],
   ["Ambiental", "Sin servidores propios; instancias Graviton (arm64) de bajo tamaño; registros y reportes digitales; inferencia en un equipo existente, sin compra de hardware", "Impacto bajo", "Huella de la nube y del equipo de inferencia no medida"]]),
 ("p", "Factibilidad técnica. El riesgo técnico principal ya no es la construcción de la plataforma, que está implementada y probada, sino la operación del componente de IA: el servicio de inferencia depende de un equipo personal y el modelo no tiene validación clínica. La arquitectura mitiga el primer punto con el proveedor desacoplado y el respaldo simulado, y el segundo se trata como condición de uso clínico."),
 ("p", "Factibilidad operativa. La plataforma se usa desde un navegador, con los mismos roles que ya existen en un establecimiento, y no exige reemplazar sistemas. La Unidad 2 planificó una capacitación de usuarios entre el 10 y el 25 de noviembre; no se realizó como tal. En su lugar, el 20-11-2026 se presentó el prototipo a dos médicos y una enfermera para revisar su funcionamiento, revisión que no constituye validación clínica. La institución de referencia mantiene su condición, sin compromiso formal (riesgo R12)."),
 ("p", "Factibilidad legal. Los controles exigidos por la Ley N.º 19.628 y por la Ley N.º 21.719, como el consentimiento, los derechos de los titulares, la seguridad y la trazabilidad, están implementados y verificados en código (capítulo XII). Quedan tres condiciones antes de tratar datos reales: decidir la región de alojamiento o documentar la transferencia internacional, formalizar el acuerdo de tratamiento de datos con la institución, y evaluar si el componente de análisis de imágenes debe someterse al control sanitario de dispositivos médicos. Esta última evaluación no se realizó en el proyecto y es un requisito previo a cualquier uso clínico."),
 ("p", "Factibilidad ambiental. El proyecto no instala servidores propios: el entorno de demostración usa instancias pequeñas de AWS con procesadores Graviton, que según el proveedor consumen hasta 60% menos energía que instancias EC2 comparables con el mismo rendimiento (Amazon Web Services, s. f.-a); la cifra es del proveedor y no fue medida en el proyecto. El servicio de inferencia se ejecuta en un equipo ya existente, sin adquisición de hardware, y el uso intensivo de la GPU se limita al procesamiento de imágenes. La gestión digital de casos y reportes evita la impresión de documentos. No se midió la huella de carbono; la herramienta de huella de carbono de AWS y la medición del consumo del equipo de inferencia quedan como mejora para una fase piloto."),
]

# --- (e) XII y XI: prueba de rendimiento local --------------------------------------------------------
def rendimiento(r):
    """r: dict con los resultados por número de usuarios (10, 25, 50, 100)."""
    filas = [["Usuarios virtuales", "Duración", "Solicitudes", "Errores", "Solicitudes/s", "p50 (ms)", "p95 (ms)", "Máx. (ms)"]]
    for u in sorted(r):
        d = r[u]; t = d["total"]
        filas.append([str(u), "%d s" % round(d["duracion_s"]), f"{t['requests']:,}".replace(",", "."), str(t["errors"]),
                      ("%.1f" % t["req_por_s"]).replace(".", ","), ("%.1f" % t["p50_ms"]).replace(".", ","),
                      ("%.1f" % t["p95_ms"]).replace(".", ","), ("%.1f" % t["max_ms"]).replace(".", ",")])
    return filas
