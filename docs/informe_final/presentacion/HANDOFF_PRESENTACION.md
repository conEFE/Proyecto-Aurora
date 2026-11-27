# Handoff — Presentación de defensa del Informe Final (Proyecto Aurora)

**Fecha:** 27-11-2026 · **Rama:** `claude/bold-maxwell-13fkwp` · **Archivo vigente:** `Presentacion_Aurora_Informe_Final.pptx`
(28 diapositivas: 16 principales + 12 de respaldo). Lee este documento antes de tocar la presentación.

## 1. Qué se pidió

- Una presentación **del Informe Final** (no de la Unidad 2), de unos **10 minutos**, que abarque todos los temas.
- **Estética:** la de la presentación de la Unidad 2 (`plantilla_u2.pptx`, subida por el usuario): portada INACAP,
  tarjetas grises `F2F2F2`, rosado `FBEDED`, rojo `C00000`, texto `535353`. Solo se usa como guía visual; la
  presentación de la U2 en sí «se verá después» (el usuario no pidió cambiarla).
- Se puede usar **más de una diapositiva por tema** si corresponde.
- **Pauta de la comisión** (texto del usuario). Contenido obligatorio:
  1. Identificación del problema: necesidad detectada, impacto y solución propuesta.
  2. Modelo de negocio CANVAS: sobre todo socios clave, segmentos de clientes, propuesta de valor, fuentes de
     ingresos y estructura de costos.
  3. Tecnologías seleccionadas.
  4. Evaluación y selección tecnológica, con al menos un ejemplo cualitativo y uno cuantitativo.
  5. Casos de uso principales y su relación con los requerimientos.
  6. Arquitectura e infraestructura: diagrama de infraestructura y componentes técnicos.
  7. Factibilidad económica: costos, beneficios y antecedentes de viabilidad.
  8. Demostración del software, ligada a los casos de uso.

  **Diapositivas de respaldo** para las preguntas de la comisión: levantamiento y análisis de requerimientos;
  objetivos general y específicos; justificación de la metodología; KPI y SLA; plan de pruebas y aseguramiento de
  calidad; plan de implementación y puesta en marcha.

## 2. Estructura actual

| # | Tema de la pauta | Diapositiva | Base en la plantilla |
|---|---|---|---|
| 1 | — | Portada («Informe final») | slide1 |
| 2 | Problema | Identificación del problema (necesidad, impacto, solución) | slide25 (3 tarjetas) |
| 3 | Problema | Soluciones existentes y diferenciación (Tabla 6 del informe) | slide22 (tabla) |
| 4 | CANVAS | Modelo de negocio CANVAS (9 bloques dibujados; 5 destacados) | slide25 vaciada |
| 5 | Tecnologías | Tecnologías seleccionadas | slide24 |
| 6 | Evaluación | Cuantitativa (AHP) + cualitativa (FastAPI vs. Django REST) | slide22 |
| 7 | Casos de uso | Diagrama, 4 roles, cadena CU06→CU09, RF por CU | slide30 |
| 8 | Casos de uso | Tabla: caso de uso, qué hace, actor, requerimiento | slide22 (tabla) |
| 9 | Arquitectura | Arquitectura de la solución (por capas) | slide35 |
| 10 | Infraestructura | Infraestructura desplegada en AWS (diagrama cloud) | slide34 |
| 11 | Factibilidad económica | VAN, TIR, recuperación, flujo, costo del prototipo | slide46 |
| 12 | Factibilidad económica | Mercado, clientes proyectados y sensibilidad | slide47 |
| 13 | Demostración | Guion en 3 pasos con sus casos de uso | slide26 |
| 14 | Demostración | Pantallas principales (respaldo si falla la demo en vivo) | slide48 |
| 15–16 | — | Conclusiones · Gracias | slide49 · slide19 |
| 17 | — | Separador «Diapositivas de respaldo» | slide19 |
| 18–28 | Respaldo | Requerimientos · Objetivos · Metodología · KPI · SLA · Plan de pruebas · Rendimiento · Implementación · Mantención · Componente de IA · Factibilidad en 5 dimensiones | slide21, 39, 23, 37, 38, 39, 46, 41, 43, 21, 25 |

Las notas del orador tienen el guion y el tiempo de cada diapositiva: el bloque principal suma ≈ 9 min sin la demo en vivo.

## 3. Cómo se genera (reproducible)

Desde esta carpeta:

```bash
python3 preparar_base.py
python3 generar_presentacion.py
```

- `preparar_base.py`: arma `base.pptx` desde `plantilla_u2.pptx` (duplica, ordena y limpia diapositivas). Usa
  `add_slide.py` y `clean.py` de la skill **pptx** de Claude (se buscan en `~/.claude/skills`).
- `generar_presentacion.py` (+ `lib_presentacion.py`): rellena cada diapositiva por `shape_id`, conservando el formato
  de la plantilla. Helpers: `set_text` (un párrafo por elemento, con el estilo del párrafo original), `put_image`,
  `move`, `delete`, `card` (tarjetas del CANVAS), `reshape_table` (tablas con el estilo de la plantilla), `notes`.
- Imágenes: `../figuras/` (arquitectura, cloud, casos de uso) y `cap_*.png` (capturas recortadas al formato 9,3 × 4,18).
- Validación: `python3 <skill pptx>/scripts/office/validate.py Presentacion_Aurora_Informe_Final.pptx --original plantilla_u2.pptx`.
- Revisión visual: convertir a PDF con `scripts/office/soffice.py` y mirar cada diapositiva (texto cortado, superposiciones,
  fechas partidas en dos líneas). La plantilla es de 26,67 × 15 in: los tamaños en puntos se ven la mitad de grandes
  que en una diapositiva estándar (cuerpo mínimo ≈ 22 pt).
- Para cambiar una diapositiva: editar su bloque en `generar_presentacion.py` (el índice `SL[n]` es la posición en la
  presentación, desde 0) y volver a generar. Para agregar una, duplicar su base en `preparar_base.py` (las copias
  nuevas toman el siguiente número libre, `slide58`…) y agregarla a `ORDER`.

## 4. Decisiones y cuidados

- **Todo dato sale del Informe Final 1.7-rc** (no de la U2). Diferencias ya corregidas respecto de la U2: costo del
  prototipo **$47.074.638** (la U2 decía $48.903.000); 340 pruebas; versión 2.11.0 desplegada; infraestructura real
  (us-east-2, sin Cloudflare ni Multi-AZ); K5 = exactitud ≥ 0,85 con ≥ 30 imágenes; Nueva Clínica Cordillera es
  **institución de referencia sin acuerdo formal** (no cliente); el «equilibrio de 8,0 clientes» de la U2 no está en el
  informe y se reemplazó por la penetración de la Tabla 54.
- **El informe no tiene un CANVAS.** Se armó con sus datos (cap. XIV: mercado, precio, clientes, costos; cap. IV:
  diferenciación). Actividades, recursos, relación y canales son derivados: **el equipo debe revisarlos**. Ofrecer
  agregarlo al informe si la comisión lo espera.
- Rendimiento: se dice abiertamente que la meta de 3 s con 100 usuarios no se cumple en AWS con la 2.10.2 y que la
  2.12.0 la cumple en local; falta repetir PC-01 en AWS. Si se repite antes de la defensa, actualizar la diapositiva 24
  y las conclusiones.
- No inventar datos; no presentar la IA como validada; los roles del equipo son los de la U2 (Francisca Neira jefa de
  proyecto) salvo que el equipo diga otra cosa.

## 5. Pendiente / ideas para seguir

- Revisión del equipo: CANVAS (bloques derivados), roles, guion de la demo y tiempos.
- Si la demo en vivo cuenta dentro de los 10 minutos, recortar el bloque principal (p. ej. fusionar 13 y 14).
- Tras desplegar la 2.12.0 y repetir PC-01 en AWS: actualizar la diapositiva de rendimiento, la cifra de versión y las
  conclusiones (y el informe, con `../trabajo/pendientes_equipo.json`).
- Opcional: video corto de respaldo de la demostración.
- La presentación de la U2 se revisará después (pedido del usuario).

## 6. Historia

- 1.ª versión (26-11): 13 diapositivas temáticas; reemplazada.
- 2.ª versión (26-11): según la pauta, 12 + 13 de respaldo.
- 3.ª versión (26-11, vigente): más de una diapositiva por tema donde corresponde (diferenciación, tabla de casos de
  uso, arquitectura por capas, mercado y sensibilidad): 16 + 12.
