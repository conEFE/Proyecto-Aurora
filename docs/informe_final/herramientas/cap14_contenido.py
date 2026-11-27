# -*- coding: utf-8 -*-
"""Contenido del capítulo XIV (Factibilidad Económica) y datos del equipo de inferencia."""

PC_INFERENCIA = ("Equipo portátil HP Victus 16 (16-d0xxx) de un integrante: Intel Core i7-11800H (8 núcleos, 16 hilos, 2,3 GHz), "
                 "16 GB de RAM, NVIDIA GeForce RTX 3060 Laptop con 6 GB de VRAM, SSD NVMe de 512 GB (PCIe 4.0) y de 1 TB (PCIe 3.0)")

SRC_U2 = "Fuente: Informe de Unidad 2 del proyecto (cifras al 18-10-2026); valores recalculados y verificados para este informe."
SRC_DEMO = "Fuente: Elaboración propia a partir de docs/ESTADO_AWS.md y docs/despliegue_aws.md (16-11-2026); precios de lista de AWS para us-east-2 según esa documentación."

INTRO = [
 ("p", "La factibilidad económica se analiza en dos planos. El primero corresponde a la fase de prototipo académico: su presupuesto estimado y el costo efectivo del entorno de demostración. El segundo corresponde a una eventual fase comercial, evaluada en la Unidad 2 con el método de preparación y evaluación de proyectos de Sapag Chain et al. (2014): estimación de la demanda, inversiones y costos, flujo de caja económico, indicadores de rentabilidad y sensibilidad. Las cifras de la Unidad 2 tienen fecha de corte 18-10-2026 y fueron recalculadas para este informe; las del entorno de demostración provienen de la documentación del repositorio al 16-11-2026."),
]

MERCADO = [
 ("p", "Según GLOBOCAN 2024, en Chile se diagnosticaron 5.141 casos nuevos de cáncer de mama, el más frecuente en mujeres (18,5% de sus cánceres), con 1.829 muertes y 20.209 casos prevalentes a cinco años (International Agency for Research on Cancer, 2026). Cada caso supone al menos una mamografía diagnóstica, a las que se suman las de tamizaje, que concentran la mayor parte del volumen de lectura de un establecimiento. Esta carga de lectura es la que Aurora busca ordenar."),
 ("p", "Los segmentos considerados son clínicas privadas medianas con unidad de imagenología propia en las regiones Metropolitana, de Valparaíso y del Biobío, centros de diagnóstico mamario y centros oncológicos. Como mercado disponible se consideran las 121 instituciones privadas de atención cerrada del país (Clínicas de Chile A.G., 2025). El modelo de negocio es una suscripción mensual de $1.200.000 por establecimiento. El precio se fundamenta en el valor de ordenar la carga de lectura: en el ensayo aleatorizado MASAI, la lectura apoyada por IA detectó 6,1 cánceres por cada 1.000 mujeres, frente a 5,1 con la doble lectura habitual, y redujo en 44% las lecturas de los radiólogos (Lång et al., 2023). Aurora no reemplaza la lectura sino que prioriza la cola, por lo que su beneficio efectivo deberá medirse en un piloto (indicador K4)."),
 ("p", "La proyección de la Unidad 2 supone una entrada al mercado a través de la institución de referencia y de las demás clínicas de su red, que equivaldrían a los cinco clientes del año 1, y un crecimiento posterior con clínicas medianas de las tres regiones. Dado que no existe compromiso formal de ninguna institución, la {T:demanda} constituye un supuesto de demanda no validado."),
 ("tabla", "Proyección de clientes e ingresos de la fase comercial", "demanda", SRC_U2,
  [1500, 1800, 2944, 2300],
  [["Año", "Clientes", "Penetración del mercado disponible", "Ingresos (CLP)"],
   ["1", "5", "4,1%", "72.000.000"],
   ["2", "10", "8,3%", "144.000.000"],
   ["3", "18", "14,9%", "259.200.000"],
   ["4", "22", "18,2%", "316.800.000"],
   ["5", "26", "21,5%", "374.400.000"]]),
]

RECURSOS = [
 ("p", "El presupuesto del prototipo académico se estimó en la Unidad 2 en $47.074.638 para los ocho meses del proyecto, de forma ascendente a partir del presupuesto de la asignatura de Gestión de Proyectos (Equipo Proyecto Aurora, 2026b). Corresponde a una valoración de los recursos del proyecto a precios de mercado y no a un registro de gastos efectivos: los recursos humanos se valorizan según remuneraciones de referencia, el equipamiento según cotizaciones y la infraestructura según el costo estimado de un piloto. El licenciamiento del software base es nulo porque el stack es de código abierto."),
 ("tabla", "Presupuesto estimado del prototipo por partida", "presup", SRC_U2,
  [2300, 1500, 4744],
  [["Partida", "Monto (CLP)", "Base de cálculo"],
   ["Recursos humanos, licencias y operación", "30.353.000", "Remuneración mensual por rol × meses de participación ($21.900.000); licencias de GitHub Team, Figma y Microsoft 365 ($1.203.000); arriendo de oficina, internet, servicios, movilidad e insumos ($7.250.000)"],
   ["Equipamiento", "4.866.710", "Cotización de tres estaciones de trabajo, monitores, disco de respaldo, router y UPS ($3.636.710) y mobiliario ($1.230.000)"],
   ["Infraestructura cloud", "2.440.000", "Aproximadamente 10 meses de operación de un piloto a $237.256 mensuales"],
   ["Contingencia (25%)", "9.414.928", "25% de la suma de las partidas anteriores"],
   ["Total", "47.074.638", ""]]),
 ("p", "La partida de infraestructura cloud se basó en el dimensionamiento de un piloto en la región de São Paulo (EC2 t3.large, RDS db.t3.medium, 100 GB de imágenes y copias en otra región), con un costo estimado de USD 241,09 mensuales. El entorno de demostración efectivamente desplegado utiliza recursos de menor tamaño en la región us-east-2, con un costo aproximado de USD 26 mensuales ({T:nube}), cubierto con créditos del plan gratuito de AWS, por lo que no ha implicado desembolso directo."),
 ("tabla", "Costo mensual de la infraestructura: piloto estimado y demostración desplegada", "nube", SRC_DEMO + " Piloto: informe de Unidad 2.",
  [2400, 2944, 1600, 1600],
  [["Componente", "Demostración desplegada (us-east-2)", "Demostración USD/mes", "Piloto estimado USD/mes"],
   ["Cómputo", "EC2 t4g.micro, disco gp3 de 10 GB e IPv4 fija", "≈ 10,5", "102,67"],
   ["Base de datos", "RDS PostgreSQL db.t4g.micro, 20 GB", "≈ 15", "121,18"],
   ["Almacenamiento y operación", "S3, clave aws/s3, CloudWatch Logs, Secrets Manager", "≈ 1,4", "17,24"],
   ["DNS", "Zona de Route 53", "≈ 0,5", "0 (Cloudflare)"],
   ["Inferencia", "Equipo propio de un integrante, conectado por Tailscale", "0", "Incluida en cómputo"],
   ["Total", "", "≈ 26–27", "241,09"]]),
 ("p", "El proyecto de AWS dispone de créditos por USD 180 (USD 100 iniciales y USD 80 por actividades), con un saldo de USD 177,53 al 16-11-2026 y vigencia hasta el 10-05-2027. Con el costo actual, el consumo hasta esa fecha se estima en cerca de USD 150, por lo que los créditos cubren la operación del entorno de demostración durante su vigencia. La alerta de presupuesto configurada en USD 15 mensuales es inferior al costo actual y debe ajustarse. Si el servicio de inferencia se trasladara a AWS, la documentación del proyecto estima un costo de cerca de USD 28 mensuales con una instancia t4g.medium y ejecución en CPU."),
 ("p", "El servicio de inferencia se ejecuta en un equipo de un integrante, sin costo de adquisición para el proyecto: " + PC_INFERENCIA[0].lower() + PC_INFERENCIA[1:] + ". Este equipo también se utilizó para entrenar el modelo, según la Unidad 2. Su uso como servidor de inferencia introduce una dependencia de disponibilidad que no es adecuada para un piloto con datos reales (capítulo XIII)."),
]

ADQUIS = [
 ("p", "La {T:equipos} presenta la cotización de equipamiento utilizada en el presupuesto, realizada en octubre de 2026 con precios con IVA. Corresponde a una valoración para tres estaciones de trabajo equivalentes; el equipo efectivamente utilizado para el modelo de IA es el descrito en el apartado anterior, de propiedad de un integrante."),
 ("tabla", "Cotización de equipamiento", "equipos",
  "Fuente: Informe de Unidad 2 del proyecto, con precios consultados el 18-10-2026 en PC Factory y Notebookstore.",
  [1800, 2944, 600, 1600, 1600],
  [["Componente", "Modelo cotizado", "Cant.", "Precio unitario (CLP)", "Total (CLP)"],
   ["Notebook de desarrollo", "Lenovo LOQe Gen 10, AMD Ryzen 7 7735HS, 16 GB RAM, SSD 512 GB, RTX 3050", "3", "948.490", "2.845.470"],
   ["Monitor", "ASUS VY249HGR 24\" IPS Full HD", "3", "103.090", "309.270"],
   ["Disco de respaldo", "Kingston XS1000 SSD externo 2 TB", "1", "309.290", "309.290"],
   ["Router", "TP-Link ER605", "1", "48.990", "48.990"],
   ["UPS", "APC Easy-UPS 1000 VA", "1", "123.690", "123.690"],
   ["Total", "", "", "", "3.636.710"]]),
 ("p", "Para una eventual fase comercial deben considerarse además adquisiciones no presupuestadas en la Unidad 2: la licencia comercial de Ultralytics YOLO, exigida por su licencia AGPL-3.0 para un servicio SaaS cerrado (o el reemplazo del detector por una alternativa con licencia permisiva), y la infraestructura de inferencia con GPU o CPU en la nube."),
]

FLUJO = [
 ("p", "La {T:supuestos} resume los supuestos del flujo de caja de la fase comercial, tomados de la Unidad 2, y la {T:flujo} presenta el flujo resultante. Los cálculos se reprodujeron para este informe y coinciden con los de la Unidad 2."),
 ("tabla", "Supuestos del flujo de caja", "supuestos", SRC_U2,
  [2200, 2600, 3744],
  [["Supuesto", "Valor", "Fundamento"],
   ["Inversión inicial", "$70.000.000", "Equipo Proyecto Aurora (2026b)"],
   ["Activos depreciables", "$33.300.000; depreciación lineal de $7.525.000 anuales", "Estaciones de trabajo, servidores y licencias, equipamiento de oficina, desarrollo del MVP y seguridad, según vidas útiles del SII; el resto corresponde a capital de trabajo, imprevistos y trámites legales"],
   ["Valor de desecho", "$8.000.000 en el año 5", "Valor comercial estimado de los activos"],
   ["Tasa de descuento", "14%", "Costo promedio ponderado de capital: 70% capital propio y 30% crédito bancario"],
   ["Impuesto a la renta", "27%", "Régimen general de primera categoría; pérdidas imputadas a años siguientes"],
   ["Costos operacionales", "De $108 a $174 millones anuales", "Equipo Proyecto Aurora (2026b)"]]),
 ("tabla", "Flujo de caja económico de la fase comercial (CLP)", "flujo", SRC_U2,
  [1544, 1100, 1180, 1180, 1180, 1180, 1180],
  [["Concepto", "Año 0", "Año 1", "Año 2", "Año 3", "Año 4", "Año 5"],
   ["Ingresos", "—", "72.000.000", "144.000.000", "259.200.000", "316.800.000", "374.400.000"],
   ["Costos operacionales", "—", "−108.000.000", "−120.000.000", "−138.000.000", "−156.000.000", "−174.000.000"],
   ["Depreciación", "—", "−7.525.000", "−7.525.000", "−7.525.000", "−7.525.000", "−7.525.000"],
   ["Utilidad antes de impuestos", "—", "−43.525.000", "16.475.000", "113.675.000", "153.275.000", "192.875.000"],
   ["Impuesto (27%)", "—", "0", "0", "−23.388.750", "−41.384.250", "−52.076.250"],
   ["Utilidad neta", "—", "−43.525.000", "16.475.000", "90.286.250", "111.890.750", "140.798.750"],
   ["(+) Depreciación", "—", "7.525.000", "7.525.000", "7.525.000", "7.525.000", "7.525.000"],
   ["(−) Inversión", "−70.000.000", "—", "—", "—", "—", "—"],
   ["(+) Valor de desecho", "—", "—", "—", "—", "—", "8.000.000"],
   ["Flujo neto", "−70.000.000", "−36.000.000", "24.000.000", "97.811.250", "119.415.750", "156.323.750"],
   ["Flujo acumulado", "−70.000.000", "−106.000.000", "−82.000.000", "15.811.250", "135.227.000", "291.550.750"]]),
 ("p", "Con una tasa de descuento de 14%, el valor actual neto (VAN) es de $134.801.449, la tasa interna de retorno (TIR) es de 45,0% y el período de recuperación es de 2,84 años. La {T:sens_ec} muestra la sensibilidad ante cambios en las variables críticas."),
 ("tabla", "Sensibilidad de los indicadores de rentabilidad", "sens_ec", SRC_U2,
  [3344, 2000, 1600, 1600],
  [["Escenario", "VAN (CLP)", "TIR", "Recuperación"],
   ["Base", "134.801.449", "45,0%", "2,84 años"],
   ["Precio +20% ($1.440.000)", "242.627.165", "66,7%", "2,34 años"],
   ["Precio −20% ($960.000)", "26.375.349", "20,6%", "3,74 años"],
   ["Costos operacionales +20%", "65.418.521", "28,6%", "3,39 años"],
   ["Clientes −30% (4, 7, 13, 15 y 18)", "−24.256.743", "7,4%", "4,46 años"],
   ["Tasa de descuento 12%", "151.203.074", "45,0%", "2,84 años"],
   ["Tasa de descuento 18%", "106.182.765", "45,0%", "2,84 años"]]),
 ("p", "La variable crítica es la demanda: el VAN se mantiene positivo mientras se capte al menos el 75,2% de los clientes proyectados, y con 30% menos clientes el proyecto deja de ser conveniente. Considerando que la demanda del año 1 descansa en instituciones sin compromiso formal, que no existe validación clínica del componente de IA y que la licencia comercial del detector no está costeada, los indicadores deben interpretarse como un escenario de planificación condicionado a la validación de la demanda en un piloto, y no como una proyección comprometida."),
]
