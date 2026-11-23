# -*- coding: utf-8 -*-
"""Contenido del capítulo X (Detalle de la Arquitectura a implementar). Rutas de figuras relativas a docs/informe_final."""

SRC_U2 = "Fuente: Informe de Unidad 2 del proyecto; reglas contrastadas con el código fuente del repositorio (23-11-2026)."
SRC_GEN = "Fuente: Elaboración propia a partir del código fuente y de la documentación del repositorio (23-11-2026)."

INTRO = [
 ("p", "Este capítulo detalla la arquitectura implementada en el prototipo. Conforme a la decisión del equipo, se documenta la arquitectura actual, que no requiere cambios arquitectónicos para esta entrega. Los procesos y casos de uso provienen de la Unidad 2 y se contrastaron con el código; el modelo de datos se generó directamente desde las definiciones de la base de datos; y los diagramas de componentes, topología, infraestructura y arquitectura se elaboraron a partir del código y de la documentación del despliegue, reemplazando los diagramas de diseño objetivo de la Unidad 2, que incluían componentes no adoptados (Cloudflare, Prometheus, Grafana, AWS Backup y región sa-east-1)."),
]

BPMN = [
 ("p", "Los procesos de negocio se modelan con la notación BPMN 2.0 en tres procesos: admisión del caso clínico, triage y priorización, y revisión clínica con reporte firmado. Cada diagrama utiliza carriles por actor. Las reglas representadas se contrastaron con el código: escalamiento a prioridad Alta por BI-RADS 4 o 5 o por síntoma de alarma, umbrales de puntaje de 60 (Alta) y 30 (Media), firma del reporte con confirmación de contraseña y cierre del caso condicionado a la validación de todas las imágenes con resultado automatizado."),
 ("figura", "BPMN del Proceso 1 – Admisión del caso clínico", "bpmn1", SRC_U2, "figuras/cap10_bpmn_p1_u2.png"),
 ("p", "El proceso inicia cuando el paciente se presenta con una orden de examen o un estudio realizado. El personal administrativo verifica si el paciente existe; si no, lo registra junto con su consentimiento informado, condición sin la cual el sistema no permite continuar. Luego crea el caso, que recibe un código anónimo, registra antecedentes y síntomas, y carga las imágenes, que se validan, cifran y registran con su huella SHA-256. El proceso termina con un evento que activa el Proceso 2."),
 ("figura", "BPMN del Proceso 2 – Triage y priorización", "bpmn2", SRC_U2, "figuras/cap10_bpmn_p2_u2.png"),
 ("p", "El Proceso 2 se inicia con la carga de imágenes o con la modificación de antecedentes. El sistema solicita el análisis de cada imagen al proveedor de inferencia y calcula el triage en dos pasos: primero evalúa reglas de escalamiento directo; si ninguna se cumple, calcula un puntaje ponderado de 0 a 100 con el resultado automatizado, la edad, los antecedentes y el tiempo de espera, y lo compara con los umbrales configurados. Los casos de nivel Alta generan una notificación a los médicos activos y todos los casos pasan a la cola priorizada. Los pesos, umbrales y reglas son parámetros versionados que definen los médicos; su configuración inicial es una propuesta técnica que requiere validación clínica."),
 ("figura", "BPMN del Proceso 3 – Revisión clínica, validación del resultado automatizado y reporte firmado", "bpmn3", SRC_U2, "figuras/cap10_bpmn_p3_u2.png"),
 ("p", "El médico toma el caso de la cola, revisa antecedentes, imágenes y desglose del triage, y puede sobrescribir el nivel indicando un motivo obligatorio, acción que queda en la bitácora de auditoría. Valida el resultado automatizado de cada imagen (concordante, falso positivo, falso negativo o no evaluable) y registra su resultado, con lo que el caso se cierra. Para emitir el reporte firma su conformidad confirmando su contraseña; el PDF incluye la firma, un código de verificación y metadatos de tipo DICOM. El dashboard actualiza luego los indicadores, incluido el desempeño del modelo por versión."),
]

CU = [
 ("p", "El diagrama de casos de uso representa tres actores principales —personal administrativo, médico y administrador del sistema— y un actor secundario, el servicio de inferencia. Los roles aplican el principio de mínimo privilegio: el personal administrativo registra pacientes, casos e imágenes; el médico concentra las funciones clínicas; y el administrador gestiona usuarios y auditoría. Respecto del catálogo de la Unidad 2 (CU01 a CU16), se actualizó CU17 «Cambiar contraseña», que figuraba como planificado y se implementó en la versión 2.3.0, y se incorporó CU18 «Gestionar solicitudes de titulares de datos», correspondiente a las funciones de privacidad de la versión 2.4.0 (HU10)."),
 ("figura", "Diagrama de casos de uso de la plataforma (actualizado)", "cu",
  "Fuente: Elaboración propia a partir del catálogo de casos de uso del informe de Unidad 2, actualizado con las funciones implementadas posteriormente (CU17 y CU18, destacados).", "figuras/cap10_casos_uso.png"),
 ("tabla", "Catálogo de casos de uso", "cu_cat",
  "Fuente: Elaboración propia a partir del informe de Unidad 2 del proyecto, con CU17 y CU18 actualizados. La especificación detallada se incorporará en los anexos.",
  [800, 2600, 2300, 1844, 1000],
  [["ID", "Caso de uso", "Actor(es)", "Relación", "Historia"],
   ["CU01", "Iniciar sesión", "Todos", "Previo a los demás casos", "HU01"],
   ["CU02", "Gestionar usuarios y roles", "Administrador", "—", "HU01"],
   ["CU03", "Consultar bitácora de auditoría", "Administrador", "—", "HU11"],
   ["CU04", "Registrar paciente y consentimiento", "Administrativo, médico", "—", "HU02, HU09"],
   ["CU05", "Crear y gestionar caso clínico", "Administrativo, médico", "—", "HU03"],
   ["CU06", "Cargar exámenes e imágenes", "Administrativo, médico", "«include» CU07", "HU04"],
   ["CU07", "Analizar imagen", "Servicio de inferencia", "«include» CU08", "HU08"],
   ["CU08", "Calcular triage", "Sistema", "—", "HU05"],
   ["CU09", "Consultar cola priorizada", "Administrativo, médico", "—", "HU05"],
   ["CU10", "Sobrescribir nivel de triage", "Médico", "«extend» CU11", "HU05"],
   ["CU11", "Revisar caso y registrar resultado", "Médico", "«include» CU15", "HU03, HU12"],
   ["CU12", "Generar reporte clínico PDF", "Médico", "«extend» CU11; «include» CU16", "HU06"],
   ["CU13", "Configurar parámetros de triage", "Médico", "—", "HU05"],
   ["CU14", "Visualizar dashboard de métricas", "Todos", "—", "HU07"],
   ["CU15", "Validar informe de IA por imagen", "Médico", "Incluido por CU11", "HU12"],
   ["CU16", "Firmar reporte clínico", "Médico", "Incluido por CU12", "HU06"],
   ["CU17", "Cambiar contraseña", "Todos", "—", "HU01"],
   ["CU18", "Gestionar solicitudes de titulares de datos", "Administrativo, médico", "—", "HU10"]]),
 ("p", "La cadena CU06 → CU07 → CU08 → CU09 expresa la relación entre la solución y el problema: la carga de un examen desencadena el análisis y la priorización, de modo que los casos de mayor sospecha llegan antes a la revisión médica. CU10 y CU13 aseguran que el criterio clínico prevalezca sobre el cálculo automático, y CU15 y CU16 dejan constancia del juicio profesional sobre el resultado automatizado y de la conformidad con el reporte. La relación entre casos de uso e historias es indicativa y se consolidará en la matriz de trazabilidad (capítulo XII)."),
]

COMP = [
 ("p", "El diagrama de componentes muestra la organización del software desplegado. El navegador ejecuta la aplicación React; el contenedor web (Caddy) termina TLS, sirve el sitio y reenvía las solicitudes /api al contenedor backend. La API FastAPI agrupa sus módulos en rutas, servicios de negocio, autenticación, motor de triage y auditoría, y accede a recursos externos mediante dos interfaces: almacenamiento (local o S3 cifrado) y proveedor de inferencia (simulado o HTTP, con respaldo simulado). El servicio de inferencia es un componente independiente que expone POST /predict y GET /health."),
 ("figura", "Diagrama de componentes de la arquitectura actual", "comp", SRC_GEN, "figuras/cap10_componentes.png"),
 ("tabla", "Componentes, interfaces y dependencias", "comp_tab", SRC_GEN,
  [2000, 3044, 1700, 1800],
  [["Componente", "Responsabilidad", "Interfaz expuesta", "Depende de"],
   ["Aurora Web (SPA)", "Interfaz por rol; generación de PDF en el navegador.", "Rutas de la aplicación web", "API REST"],
   ["Caddy (contenedor web)", "TLS, sitio estático, proxy inverso y encabezados de seguridad.", "HTTPS 443", "Contenedor backend"],
   ["Rutas REST", "Contrato HTTP de la API (auth, patients, cases, images, triage, reports, dashboard, privacy, admin, inference).", "API REST JSON", "Servicios y autenticación"],
   ["Autenticación y autorización", "Emisión y verificación de JWT; roles consultados en la base de datos; bloqueo por intentos fallidos.", "Dependencia de seguridad de cada ruta", "PostgreSQL"],
   ["Servicios de negocio", "Pacientes, casos, imágenes, revisión, firma, reportes, privacidad e indicadores.", "Funciones de servicio", "Almacenamiento, inferencia, triage, auditoría, PostgreSQL"],
   ["Motor de triage", "Reglas de escalamiento, puntaje ponderado, umbrales y desglose por factor.", "Cálculo de triage", "Configuración versionada en PostgreSQL"],
   ["Auditoría", "Registro de operaciones relevantes en bitácora no modificable.", "Registro de eventos", "PostgreSQL (disparador append-only)"],
   ["Almacenamiento", "Cifrado y almacenamiento de imágenes; implementación local o en S3.", "Interfaz de almacenamiento", "Disco local o Amazon S3"],
   ["Proveedor de inferencia", "Solicitud del análisis; validación del contrato de respuesta; respaldo simulado identificado.", "Interfaz de proveedor", "Servicio de inferencia"],
   ["Servicio de inferencia", "Preprocesamiento y ejecución de la CNN y de YOLO.", "POST /predict; GET /health", "Pesos de los modelos"]]),
]

DATOS = [
 ("p", "La base de datos es relacional (PostgreSQL) y su esquema se gestiona con migraciones versionadas de Alembic. El modelo actual contiene 18 tablas, organizadas en cinco grupos: identidad y acceso, pacientes y privacidad, casos e imágenes, triage, y revisión y reportes. La Unidad 2 informaba 14 tablas; la diferencia corresponde a las funciones incorporadas en las versiones 2.3.0 y 2.4.0 (registro de errores, métricas de solicitudes, textos y eventos de consentimiento, y solicitudes de titulares)."),
]
LOGICO = [
 ("p", "El modelo lógico se generó automáticamente a partir de las definiciones de la base de datos en el código, lo que asegura su correspondencia con la implementación. El caso clínico es la entidad central: se asocia a un paciente y concentra imágenes, resultado de triage, revisión clínica, firma y reportes. Cinco relaciones son uno a uno por restricción de unicidad: caso–resultado de triage, caso–revisión clínica, caso–firma del reporte, imagen–resultado automatizado e imagen–validación médica."),
 ("figura", "Modelo lógico de datos (entidades y relaciones)", "er",
  "Fuente: Elaboración propia; diagrama generado desde los modelos SQLAlchemy del repositorio (23-11-2026).", "figuras/cap10_modelo_logico.png"),
]
FISICO = [
 ("p", "La {T:fisico} resume el modelo físico. Las tablas usan claves primarias enteras y claves foráneas con integridad referencial. Los datos semiestructurados (parámetros y desglose del triage, detalle de auditoría y metadatos del reporte) se almacenan en columnas JSONB. La tabla audit_log está protegida por un disparador que impide su modificación o eliminación (append-only), definido en la migración del Sprint 2."),
 ("tabla", "Modelo físico: tablas, propósito y claves", "fisico",
  "Fuente: Elaboración propia a partir de los modelos SQLAlchemy y de las migraciones Alembic del repositorio (23-11-2026). N.º = número de columnas.",
  [2000, 3344, 700, 2500],
  [["Tabla", "Propósito", "N.º", "Relaciones principales y notas"],
   ["users", "Usuarios, rol, estado y control de intentos de acceso.", "13", "Referenciada como autor o responsable por la mayoría de las tablas."],
   ["audit_log", "Bitácora de operaciones relevantes.", "8", "FK users; detalle JSONB; disparador append-only."],
   ["error_log", "Registro de errores de la aplicación.", "10", "FK users."],
   ["request_metrics", "Métricas de solicitudes (tiempos de respuesta).", "6", "Sin claves foráneas."],
   ["consent_texts", "Versiones del texto de consentimiento informado.", "5", "Referenciada por patients y patient_consent_events."],
   ["patients", "Datos del paciente, consentimiento vigente y bloqueo.", "18", "FK consent_texts, users."],
   ["patient_consent_events", "Historial de otorgamiento y retiro del consentimiento.", "7", "FK patients, consent_texts, users."],
   ["data_subject_requests", "Solicitudes de titulares de datos y su resolución.", "11", "FK patients, users."],
   ["cases", "Caso clínico: código anónimo, estado, síntomas y BI-RADS.", "13", "FK patients, users (creador, médico asignado)."],
   ["images", "Imágenes del caso: metadatos, ruta cifrada y huella SHA-256.", "13", "FK cases, users."],
   ["inference_results", "Resultado del análisis automatizado por imagen.", "11", "FK images (1:1); detecciones JSON; is_simulated; clinically_validated; versión del modelo."],
   ["ai_validations", "Validación médica del resultado automatizado.", "11", "FK images (1:1), inference_results, users."],
   ["notifications", "Notificaciones de casos de prioridad Alta.", "6", "FK users, cases."],
   ["triage_configs", "Parámetros de triage versionados.", "7", "Parámetros JSONB; FK users."],
   ["triage_results", "Puntaje, nivel, desglose y sobrescritura del triage.", "12", "FK cases (1:1), triage_configs (versión), users; desglose JSONB."],
   ["clinical_reviews", "Resultado de la revisión médica del caso.", "11", "FK cases (1:1), users."],
   ["report_signatures", "Firma de conformidad del médico.", "6", "FK cases (1:1), users."],
   ["reports", "Registro de reportes PDF emitidos.", "7", "FK cases, users, report_signatures; metadatos de tipo DICOM en JSONB."]]),
]
DICC = [
 ("p", "El diccionario de datos, con el detalle de columnas, tipos y restricciones de las 18 tablas, se presenta en los anexos (capítulo XVIII), generado a partir de los mismos modelos para mantener su correspondencia con la implementación."),
]

TOPO = [
 ("p", "La {F:topo} presenta la topología de comunicaciones del entorno de demostración. Los usuarios acceden por HTTPS al nombre demo.auroracare.cl, resuelto por Route 53 hacia la dirección IP fija del servidor. El grupo de seguridad del servidor admite solo los puertos 80 y 443; no expone el puerto 22, y la administración se realiza mediante Session Manager. La base de datos RDS es privada y solo acepta conexiones al puerto 5432 desde el grupo de seguridad del servidor. El servidor se comunica con el servicio de inferencia a través de una red privada Tailscale, y el equipo que ejecuta ese servicio restringe su puerto 8080 a direcciones de esa red."),
 ("figura", "Topología de comunicaciones del entorno de demostración", "topo", SRC_GEN, "figuras/cap10_topologia.png"),
 ("tabla", "Flujos de comunicación y protocolos", "flujos", SRC_GEN,
  [2400, 2200, 1500, 2444],
  [["Origen → destino", "Propósito", "Protocolo / puerto", "Protección"],
   ["Navegador → servidor (Caddy)", "Acceso a la aplicación y a la API", "HTTPS 443", "TLS (Let's Encrypt); encabezados de seguridad"],
   ["Caddy → backend", "Reenvío de solicitudes /api", "HTTP 8000 (red interna Docker)", "Sin exposición a Internet"],
   ["Backend → RDS", "Persistencia", "PostgreSQL 5432", "TLS requerido; grupo de seguridad dedicado"],
   ["Backend → S3", "Imágenes y respaldos", "HTTPS 443", "Rol IAM; cifrado Fernet + SSE-KMS"],
   ["Backend → servicio de inferencia", "Análisis de imágenes", "HTTP 8080 sobre Tailscale", "Túnel cifrado; token Bearer; firewall local"],
   ["Contenedores → CloudWatch Logs", "Registros", "HTTPS 443", "Rol IAM"],
   ["Operación → servidor", "Administración", "Session Manager (HTTPS)", "IAM; sin puerto 22"]]),
]

INFRA = [
 ("p", "La infraestructura del entorno de demostración se despliega en un proyecto de AWS con plan gratuito y créditos, en la región us-east-2 asignada a la cuenta. Un servidor EC2 t4g.micro ejecuta los contenedores web y backend con Docker Compose; la base de datos se migró el 16-11-2026 a Amazon RDS PostgreSQL 16; las imágenes y los respaldos se almacenan en un bucket S3 privado y versionado. El servicio de inferencia se ejecuta fuera de AWS, en un equipo con GPU de un integrante, y puede trasladarse a AWS cambiando únicamente la dirección configurada. La información de este apartado proviene de la documentación del repositorio y no de una inspección directa de la cuenta de AWS."),
 ("figura", "Infraestructura desplegada del entorno de demostración", "infra",
  "Fuente: Elaboración propia a partir de docs/ESTADO_AWS.md (actualizado al 16-11-2026) y de la configuración de despliegue del repositorio.", "figuras/cap10_infraestructura.png"),
 ("tabla", "Componentes de infraestructura del entorno de demostración", "infra_tab",
  "Fuente: Elaboración propia a partir de docs/ESTADO_AWS.md (16-11-2026).",
  [2200, 3844, 2500],
  [["Componente", "Configuración documentada", "Función"],
   ["Amazon EC2", "t4g.micro (arm64), Amazon Linux 2023, disco gp3 de 10 GB cifrado, IMDSv2, IP fija", "Ejecución de los contenedores web y backend"],
   ["Amazon RDS", "PostgreSQL 16.15, db.t4g.micro, 20 GB gp3 cifrados, sin acceso público; respaldo automático de 1 día", "Base de datos de la plataforma"],
   ["Amazon S3", "Bucket privado y versionado; imágenes con cifrado Fernet y SSE-KMS; respaldos con retención de 35 días", "Imágenes y respaldos diarios"],
   ["Respaldo", "Volcado diario de la base de datos a S3 (03:15, hora de Chile)", "Recuperación ante pérdida de datos"],
   ["Route 53", "Zona auroracare.cl, delegada desde NIC Chile", "DNS del entorno de demostración"],
   ["Seguridad", "Rol IAM de la instancia, Secrets Manager, grupos de seguridad, Session Manager", "Control de acceso y gestión de secretos"],
   ["CloudWatch Logs", "Grupo de registros de los contenedores, retención de 30 días", "Registro centralizado"],
   ["Equipo con GPU", "Servicio de inferencia en contenedor o proceso local, conectado por Tailscale", "Análisis automatizado (prototipo)"]]),
 ("p", "Esta configuración corresponde a un entorno de demostración con datos ficticios y costo mínimo. Difiere del dimensionamiento previsto en la Unidad 2 para un piloto (instancias de mayor tamaño, región de São Paulo y servicios administrados de respaldo), cuya evaluación económica se presenta en el capítulo XIV. Su disponibilidad, continuidad y mantención se tratan en el capítulo XIII."),
]

ARQ = [
 ("p", "La {F:arq} integra las vistas anteriores en una arquitectura por capas que relaciona los componentes de software con la infraestructura que los ejecuta. Se mantiene la regla de diseño según la cual solo la capa de lógica de negocio accede a los datos, y el servicio de inferencia recibe imágenes y devuelve resultados que el backend almacena y el médico valida."),
 ("figura", "Arquitectura de la solución (software y hardware)", "arq", SRC_GEN, "figuras/cap10_arquitectura.png"),
]

IA = [
 ("p", "El análisis automatizado de imágenes se implementa como un servicio de inferencia independiente, ubicado en backend/inference_service. Su código fue inspeccionado directamente para este informe; las métricas de desempeño provienen de la documentación del servicio y no fueron reproducidas, ya que los scripts y conjuntos de entrenamiento no forman parte del repositorio."),
 ("tabla", "Características del servicio de inferencia", "ia_tab",
  "Fuente: Elaboración propia a partir de backend/inference_service (app.py, analyzer.py, preprocessing.py y README.md) y de backend/app/inference/providers.py, inspeccionados el 23-11-2026.",
  [2300, 6244],
  [["Aspecto", "Descripción verificada en el código"],
   ["Identificación del modelo", "Versión «cnn-resnet18-672x1024+yolo11s-masa-1280»; pesos cnn_proporcion.pt (≈ 45 MB) e yolo_masas.pt (≈ 19 MB) versionados en el repositorio."],
   ["Etapa 1: clasificación", "ResNet18 adaptada a un canal; entrega la probabilidad de malignidad de la mamografía completa; umbral de 0,35 para marcar la imagen como sospechosa."],
   ["Etapa 2: localización", "YOLO11s; entrega cajas de la clase «masa» con confianza mínima de 0,25; no detecta calcificaciones."],
   ["Preprocesamiento", "Lectura en escala de grises (PNG, JPEG o DICOM), ecualización CLAHE, ajuste sin deformación a 672 × 1024 para la CNN y lado mayor de 1.280 píxeles para YOLO."],
   ["Contrato", "POST /predict (archivo multipart) y GET /health; autenticación con token Bearer comparado en tiempo constante; límite de 60 MB; códigos 400, 401, 413 y 415 ante errores."],
   ["Cliente en la plataforma", "Proveedor HTTP con tiempo máximo configurable; valida campos obligatorios y rango de confianza; ante falla usa el proveedor simulado, cuyos resultados quedan marcados como simulados."],
   ["Persistencia", "Tabla inference_results: detección, confianza, detecciones, tiempo de proceso, versión del modelo, marcas is_simulated y clinically_validated y mensaje."],
   ["Validación clínica", "La constante clinically_validated es falsa en el código; la interfaz y el PDF muestran el aviso de modelo prototipo no validado."],
   ["Pruebas", "Pruebas automatizadas del proveedor HTTP (token, contrato, fallas), del respaldo simulado, del reanálisis y del contrato entre servicio y plataforma (test_inference_model.py); su ejecución se reporta en el capítulo XII."]]),
 ("p", "Según la documentación del servicio, la CNN alcanza un AUC de 0,838 en el conjunto de prueba con división por paciente (0,841 en CBIS-DDSM y 0,807 en CMMD) y, con el umbral de 0,35, una sensibilidad de 0,849 y una especificidad de 0,641; YOLO alcanza un mAP50 de 0,538 para masas. Estas cifras difieren de las informadas en la Unidad 2 (AUC 0,843, sensibilidad 0,843 y especificidad 0,664, con división por imagen y entrada de 512 × 512), porque el modelo fue reentrenado con división por paciente, tal como se había planteado como siguiente paso."),
 ("p", "Las limitaciones declaradas son relevantes para interpretar los resultados: los conjuntos de entrenamiento (CBIS-DDSM y CMMD) no contienen mamografías sanas, por lo que el modelo prioriza entre casos con hallazgo; no existe validación externa ni clínica con población chilena; la especificidad implica que una proporción importante de casos benignos queda marcada como sospechosa; y el umbral de 0,35 está fijado en el código del servicio, por lo que su validación por un médico y su conversión en parámetro configurable siguen pendientes. Las métricas corresponden a un prototipo y no constituyen evidencia de desempeño clínico."),
]
