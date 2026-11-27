# -*- coding: utf-8 -*-
"""Iteración 8: resumen, abstract, introducción y complementos del capítulo III."""

RESUMEN = [
 ("p", "Proyecto Aurora es un prototipo de plataforma web de apoyo a la gestión y priorización (triage) de casos asociados a sospecha de cáncer de mama, concebido como herramienta de apoyo que no reemplaza el criterio médico. La plataforma permite registrar pacientes con consentimiento informado versionado, crear y seguir casos clínicos, cargar imágenes mamarias almacenadas de forma cifrada, priorizar los casos mediante reglas y un puntaje ponderado con parámetros configurables, registrar la revisión y la firma del profesional médico, emitir reportes y consultar indicadores de gestión, con control de acceso por rol, bitácora de auditoría y gestión de derechos de los titulares de datos. Incorpora además, como prototipo, un servicio de análisis automatizado de mamografías basado en un clasificador de red neuronal convolucional y un detector YOLO, sin validación clínica."),
 ("p", "El proyecto se gestionó con un enfoque de planificación predictiva por hitos y ejecución en ocho sprints con Scrumban. La solución utiliza una arquitectura por capas implementada como monolito modular (React, FastAPI y PostgreSQL), con el servicio de análisis desacoplado mediante una interfaz de proveedor, y se desplegó en un entorno de demostración en AWS. La suite de 314 pruebas automatizadas se ejecutó sin fallas, con una cobertura de código de 97%, y el prototipo fue revisado por dos médicos y una enfermera. Quedan pendientes las pruebas de carga y de seguridad dinámica, la validación clínica formal del modelo y un piloto con una institución de salud."),
]
KW_ES = "Cáncer de mama; triage; priorización de casos; plataforma web; inteligencia artificial; apoyo a la decisión clínica; protección de datos de salud."

ABSTRACT = [
 ("p", "Proyecto Aurora is a web platform prototype that supports the management and prioritization (triage) of suspected breast cancer cases. It is designed as a support tool and does not replace medical judgment. The platform registers patients with versioned informed consent, creates and tracks clinical cases, stores breast images in encrypted form, prioritizes cases through rules and a weighted score with configurable parameters, records the physician's review and signature, issues reports and displays management indicators, with role-based access control, an audit log and data subject rights management. It also includes, as a prototype, an automated mammography analysis service based on a convolutional neural network classifier and a YOLO detector, without clinical validation."),
 ("p", "The project combined milestone-based predictive planning with execution in eight Scrumban sprints. The solution follows a layered architecture implemented as a modular monolith (React, FastAPI and PostgreSQL), with the analysis service decoupled through a provider interface, and was deployed to a demonstration environment on AWS. The suite of 314 automated tests ran without failures, with 97% code coverage, and the prototype was reviewed by two physicians and one nurse. Load and dynamic security testing, a formal clinical validation of the model and a pilot with a healthcare institution remain pending."),
]
KW_EN = "Breast cancer; triage; case prioritization; web platform; artificial intelligence; clinical decision support; health data protection."

INTRO = [
 ("p", "El cáncer de mama es el cáncer más frecuente en mujeres en Chile, y su pronóstico depende en gran medida de la oportunidad con que se diagnostica y trata. Cuando los exámenes se revisan por orden de llegada, los casos de mayor sospecha pueden esperar lo mismo que los de menor riesgo. Proyecto Aurora aborda este problema mediante una plataforma web que centraliza la información de pacientes, casos e imágenes y propone un orden de revisión según criterios explícitos y parametrizables, manteniendo la decisión clínica en el profesional de salud."),
 ("p", "El proyecto fue desarrollado por un equipo de tres integrantes: Francisca Neira, a cargo de la gestión del proyecto y la documentación; Felipe Campos, responsable del backend, la base de datos y la integración del análisis automatizado; y Juan Francisco Meneses, responsable del frontend, la infraestructura y el modelo de análisis de imágenes. Nueva Clínica Cordillera se consideró como institución de referencia para contextualizar el escenario de uso, sin que exista un compromiso formal con ella."),
 ("p", "El resultado es un prototipo funcional desplegado en un entorno de demostración con datos ficticios. Este informe documenta su formulación, diseño, implementación y evaluación, distinguiendo en cada capítulo lo planificado, lo documentado, lo verificado en el código y lo probado. Ninguna afirmación del informe debe entenderse como validación clínica del prototipo o del modelo de análisis automatizado, que no se encuentra acreditada."),
 ("p", "El informe se organiza conforme a la plantilla institucional. Los capítulos II a V presentan el problema, los requerimientos, el marco teórico y los objetivos; el capítulo VI describe la metodología, el cronograma, el equipo y los recursos; los capítulos VII a X detallan la arquitectura empresarial y tecnológica, las tecnologías seleccionadas y la arquitectura implementada; los capítulos XI a XIII tratan los indicadores y niveles de servicio, el plan de pruebas y el plan de implementación; el capítulo XIV analiza la factibilidad económica y el XV los ajustes del cronograma. Finalmente, el capítulo XVI presenta las conclusiones y recomendaciones, y los capítulos XVII y XVIII contienen las referencias y los anexos."),
]

SRC_U1 = "Fuente: Formulación inicial del proyecto (Equipo Proyecto Aurora, 2026a); HU08–HU12 según la reformulación aprobada en este informe."

CRIT_INTRO = [
 ("h4", "Criterios de aceptación de HU01 a HU07"),
 ("p", "Los criterios de aceptación de HU01 a HU07 corresponden a los definidos en la especificación de la formulación inicial ({T:crit_hu})."),
 ("tabla", "Criterios de aceptación de HU01 a HU07", "crit_hu", "Fuente: Formulación inicial del proyecto (Equipo Proyecto Aurora, 2026a).",
  [900, 7644],
  [["Historia", "Criterios de aceptación"],
   ["HU01", "El sistema permite autenticarse mediante credenciales; identifica el rol del usuario; contempla los roles médico, personal administrativo y administrador del sistema; y condiciona el acceso a las funcionalidades según el rol."],
   ["HU02", "El sistema permite registrar pacientes, consultar y modificar sus antecedentes clínicos básicos, y la información queda asociada al paciente correspondiente."],
   ["HU03", "El sistema permite crear un caso clínico asociado a un paciente y consultar y gestionar la información del caso."],
   ["HU04", "El sistema permite cargar exámenes e imágenes, que quedan asociados al caso correspondiente, y el usuario autorizado puede consultarlos."],
   ["HU05", "El sistema aplica criterios clínicos predefinidos, prioriza los casos automáticamente y el usuario clínico puede visualizar la priorización resultante."],
   ["HU06", "El sistema genera un reporte en formato PDF a partir de la información registrada, correspondiente al caso seleccionado."],
   ["HU07", "El sistema dispone de un dashboard con métricas de atención, visibles para los perfiles clínicos y administrativos autorizados."]]),
]

VERIF = [
 ("h4", "Verificación de los criterios de aceptación"),
 ("p", "Los criterios de aceptación de HU01 a HU12 se contrastaron con el código y con la suite de pruebas automatizadas ejecutada el 23-11-2026 (capítulo XII). La {T:verif} resume la evidencia y el estado de cada historia. Un criterio se considera verificado cuando existe una prueba automatizada aprobada que comprueba el comportamiento descrito; los aspectos de la interfaz que no cuentan con pruebas automatizadas se informan como verificación parcial."),
 ("tabla", "Verificación de los criterios de aceptación de HU01 a HU12", "verif",
  "Fuente: Elaboración propia a partir de la ejecución de pruebas del 23-11-2026 (Tablas de casos de prueba y de trazabilidad del capítulo XII).",
  [800, 3644, 2300, 1800],
  [["Historia", "Evidencia", "Casos de prueba", "Estado"],
   ["HU01", "Autenticación con JWT, roles leídos desde la base de datos, rechazo de tokens manipulados o expirados, restricción por rol, bloqueo por intentos fallidos", "PS-01, PS-02, PS-07", "Verificada"],
   ["HU02", "Registro y edición de pacientes con RUT validado y auditoría", "PU-04, PS-03", "Verificada"],
   ["HU03", "Creación del caso asociado al paciente, estados y transiciones, caso cerrado no editable", "PI-01, PI-02, PE-01", "Verificada"],
   ["HU04", "Carga de imágenes PNG/JPEG asociadas al caso, cifradas, con control de acceso para su consulta", "PI-03, PS-02", "Verificada"],
   ["HU05", "Reglas de escalamiento, puntaje ponderado, umbrales, cola priorizada y sobrescritura con motivo", "PU-01, PU-02, PU-03, PE-01", "Verificada"],
   ["HU06", "Reporte registrado solo con firma del médico; firma verificable; la generación del PDF ocurre en el navegador", "PS-05, PS-06, PE-01", "Verificada parcialmente (PDF sin prueba automatizada)"],
   ["HU07", "Métricas del dashboard calculadas por la API y accesibles por rol", "PI-05, PE-01", "Verificada parcialmente (interfaz sin prueba automatizada)"],
   ["HU08", "Resultado del análisis asociado a la imagen y al caso; marca de resultado simulado; contrato del servicio; respaldo simulado", "PI-03, PI-07", "Verificada; presentación como información complementaria verificada en documentación"],
   ["HU09", "Consentimiento obligatorio con versión del texto, eventos de otorgamiento y retiro, consulta según permisos", "PI-06, PI-01", "Verificada"],
   ["HU10", "Registro, consulta y gestión de solicitudes de titulares con plazos, bloqueo y exportación de datos", "PI-06", "Verificada; cumplimiento legal no certificado"],
   ["HU11", "Consulta de la bitácora solo por administrador, con filtros; registro no modificable", "PS-03, PS-08", "Verificada"],
   ["HU12", "Validación médica por imagen, evaluación del triage al cierre, cierre bloqueado sin validación, métricas de concordancia", "PI-04, PI-05", "Verificada"]]),
 ("p", "La verificación acredita el comportamiento funcional del prototipo en un entorno de pruebas con datos ficticios. No acredita desempeño clínico del análisis automatizado ni cumplimiento normativo, que requieren evaluaciones independientes."),
]

RF = [
 ("h4", "Requerimientos funcionales"),
 ("p", "La {T:rf} presenta los requerimientos funcionales. RF01 a RF07 provienen de la formulación inicial; RF08 se actualizó para corresponder a la reformulación aprobada de HU08 y a la validación médica incorporada en la Unidad 2; y RF09 se agrega en este informe para la gestión de derechos de los titulares de datos (HU10)."),
 ("tabla", "Requerimientos funcionales", "rf", SRC_U1 + " RF09 agregado en este informe.",
  [800, 6044, 1700],
  [["ID", "Requerimiento", "Historias"],
   ["RF01", "El sistema debe permitir la autenticación de usuarios con roles diferenciados (médico, personal administrativo y administrador del sistema) y controlar el acceso según el rol.", "HU01"],
   ["RF02", "El sistema debe permitir el registro y la gestión de pacientes, sus antecedentes clínicos básicos y su consentimiento informado.", "HU02, HU09"],
   ["RF03", "El sistema debe permitir la creación y gestión de casos clínicos asociados a un paciente y el registro de su resultado.", "HU03, HU12"],
   ["RF04", "El sistema debe permitir la carga y consulta de exámenes e imágenes asociados a un caso.", "HU04"],
   ["RF05", "El sistema debe contar con un módulo de triage que priorice automáticamente los casos según criterios clínicos predefinidos y configurables.", "HU05"],
   ["RF06", "El sistema debe generar reportes clínicos en formato PDF a partir de la información registrada, con la conformidad del médico revisor.", "HU06"],
   ["RF07", "El sistema debe desplegar un dashboard con métricas de atención para los perfiles autorizados.", "HU07"],
   ["RF08", "El sistema debe poner a disposición del profesional médico los resultados del análisis automatizado de las imágenes, identificando los resultados simulados, y permitir registrar su evaluación profesional.", "HU08, HU12"],
   ["RF09", "El sistema debe permitir registrar y gestionar las solicitudes de los titulares de datos (acceso, rectificación, supresión, oposición, portabilidad y bloqueo), con trazabilidad de su estado y plazo de respuesta.", "HU10"]]),
 ("p", "En la formulación inicial, RF08 establecía que la arquitectura debía estar preparada para integrar en iteraciones futuras un modelo de IA. La reformulación expresa la necesidad funcional del profesional médico, consistente con la HU08 aprobada, sin prescribir la tecnología que la implementa."),
 ("h4", "Requerimientos no funcionales"),
 ("tabla", "Requerimientos no funcionales", "rnf", "Fuente: Formulación inicial del proyecto (Equipo Proyecto Aurora, 2026a); métrica de RNF03 según el informe de Unidad 2.",
  [800, 1500, 4744, 1500],
  [["ID", "Categoría", "Requerimiento", "Historias"],
   ["RNF01", "Seguridad", "El sistema debe garantizar la seguridad y confidencialidad de los datos clínicos, considerando su carácter de dato sensible.", "HU01–HU12"],
   ["RNF02", "Escalabilidad", "El sistema debe ser modular y escalable, permitiendo incorporar nuevas funcionalidades sin afectar el funcionamiento existente.", "HU01–HU12"],
   ["RNF03", "Rendimiento", "El sistema debe mantener tiempos de respuesta aceptables en el registro y consulta de casos (percentil 95 igual o inferior a 3 segundos).", "HU02–HU07"],
   ["RNF04", "Disponibilidad", "El sistema debe estar disponible mediante infraestructura cloud, considerando redundancia básica de almacenamiento.", "HU01–HU12"],
   ["RNF05", "Trazabilidad", "El sistema debe registrar la trazabilidad de las acciones realizadas sobre los casos clínicos y los datos de pacientes (auditoría).", "HU02–HU12"]]),
]

RESTRIC = [
 ("p", "La solución se desarrolla bajo las siguientes restricciones:"),
 ("b", "Plazo académico fijo: el proyecto debe completarse entre el 11-04-2026 y el 10-12-2026."),
 ("b", "Equipo de tres integrantes, sin apoyo permanente de aseguramiento de calidad."),
 ("b", "Presupuesto acotado: herramientas de código abierto y servicios cloud cubiertos por créditos de un plan gratuito para el entorno de demostración."),
 ("b", "Uso exclusivo de datos ficticios y RUT de prueba: no se tratan datos reales de pacientes en ningún ambiente."),
 ("b", "Marco normativo de protección de datos de salud (Leyes 19.628, 21.719 y 20.584): consentimiento informado, confidencialidad, control de acceso y registro de operaciones."),
 ("b", "El análisis automatizado de imágenes es un prototipo sin validación clínica: sus resultados son información complementaria y nunca un diagnóstico, y los resultados simulados deben identificarse como tales."),
 ("b", "Sin integración con sistemas HIS, RIS o PACS de una institución, ni compromiso formal de una institución de salud para validación clínica o piloto."),
 ("b", "Región de AWS asignada por la cuenta del proyecto (us-east-2) para el entorno de demostración."),
]
