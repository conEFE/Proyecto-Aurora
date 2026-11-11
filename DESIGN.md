---
name: Aurora
description: Plataforma de apoyo al triage de casos sospechosos de cáncer de mama; cada caso se lee como una orden de mamografía.
colors:
  background: "hsl(0 0% 100%)"
  foreground: "hsl(324 31% 12%)"
  primary: "hsl(333 78% 42%)"
  brand: "hsl(333 78% 40%)"
  muted: "hsl(333 76% 97%)"
  muted-foreground: "hsl(323 17% 36%)"
  accent: "hsl(334 80% 95%)"
  border: "hsl(335 60% 89%)"
  input: "hsl(335 45% 82%)"
  destructive: "hsl(0 64% 44%)"
  alta: "hsl(4 74% 46%)"
  media: "hsl(26 90% 35%)"
  baja: "hsl(142 72% 27%)"
  sim: "hsl(23 83% 30%)"
  sim-bg: "hsl(48 96% 89%)"
  info: "hsl(221 70% 42%)"
  background-dark: "hsl(268 33% 8%)"
  card-dark: "hsl(267 31% 11%)"
  sidebar-dark: "hsl(267 32% 10%)"
  foreground-dark: "hsl(270 47% 95%)"
  primary-dark: "hsl(262 83% 58%)"
  brand-dark: "hsl(256 100% 80%)"
  muted-dark: "hsl(266 31% 14%)"
  muted-foreground-dark: "hsl(267 23% 72%)"
  accent-dark: "hsl(266 30% 18%)"
  border-dark: "hsl(266 26% 21%)"
  input-dark: "hsl(266 24% 28%)"
  destructive-dark: "hsl(0 91% 71%)"
  alta-dark: "hsl(359 100% 71%)"
  media-dark: "hsl(38 91% 55%)"
  baja-dark: "hsl(151 65% 54%)"
  sim-dark: "hsl(45 97% 64%)"
  sim-bg-dark: "hsl(45 97% 64% / 0.12)"
  info-dark: "hsl(213 94% 72%)"
  viewer: "hsl(268 33% 6%)"
typography:
  display:
    fontFamily: "Atkinson Hyperlegible Next Variable, system-ui, sans-serif"
    fontSize: "2.25rem"
    fontWeight: 800
    lineHeight: "2.6rem"
    letterSpacing: "-0.025em"
    fontFeature: "'tnum' 1"
  headline:
    fontFamily: "Atkinson Hyperlegible Next Variable, system-ui, sans-serif"
    fontSize: "1.75rem"
    fontWeight: 800
    lineHeight: "2.1rem"
    letterSpacing: "-0.015em"
  title:
    fontFamily: "Atkinson Hyperlegible Next Variable, system-ui, sans-serif"
    fontSize: "1rem"
    fontWeight: 700
    lineHeight: "1.5rem"
  title-dialog:
    fontFamily: "Atkinson Hyperlegible Next Variable, system-ui, sans-serif"
    fontSize: "1.125rem"
    fontWeight: 700
    lineHeight: "1.6rem"
  body:
    fontFamily: "Atkinson Hyperlegible Next Variable, system-ui, sans-serif"
    fontSize: "0.9375rem"
    fontWeight: 400
    lineHeight: "1.4rem"
    fontFeature: "'tnum' 1"
  label:
    fontFamily: "Atkinson Hyperlegible Next Variable, system-ui, sans-serif"
    fontSize: "0.8125rem"
    fontWeight: 600
    lineHeight: "1.15rem"
  stamp:
    fontFamily: "Atkinson Hyperlegible Next Variable, system-ui, sans-serif"
    fontSize: "0.8125rem"
    fontWeight: 800
    lineHeight: "1.15rem"
    letterSpacing: "0.025em"
rounded:
  md: "6px"
  lg: "8px"
  xl: "12px"
  2xl: "16px"
  full: "9999px"
spacing:
  "1.5": "6px"
  "2": "8px"
  "3": "12px"
  "4": "16px"
  "5": "20px"
  "6": "24px"
components:
  button-primary:
    backgroundColor: "{colors.primary}"
    textColor: "{colors.background}"
    typography: "{typography.body}"
    rounded: "{rounded.lg}"
    padding: "0 16px"
    height: "40px"
  button-primary-dark:
    backgroundColor: "{colors.primary-dark}"
    textColor: "{colors.background}"
    rounded: "{rounded.lg}"
    padding: "0 16px"
    height: "40px"
  button-secondary:
    backgroundColor: "{colors.background}"
    textColor: "{colors.foreground}"
    rounded: "{rounded.lg}"
    padding: "0 16px"
    height: "40px"
  button-ghost:
    textColor: "{colors.muted-foreground}"
    rounded: "{rounded.lg}"
    padding: "0 16px"
    height: "40px"
  button-ghost-hover:
    backgroundColor: "{colors.accent}"
    textColor: "{colors.foreground}"
  button-danger:
    backgroundColor: "{colors.destructive}"
    textColor: "{colors.background}"
    rounded: "{rounded.lg}"
    padding: "0 16px"
    height: "40px"
  input:
    backgroundColor: "{colors.background}"
    textColor: "{colors.foreground}"
    typography: "{typography.body}"
    rounded: "{rounded.lg}"
    padding: "0 12px"
    height: "40px"
  card:
    backgroundColor: "{colors.background}"
    rounded: "{rounded.xl}"
    padding: "24px"
  card-dark:
    backgroundColor: "{colors.card-dark}"
    rounded: "{rounded.xl}"
    padding: "24px"
  nav-item:
    textColor: "{colors.muted-foreground}"
    rounded: "{rounded.lg}"
    padding: "0 12px"
    height: "40px"
  nav-item-active:
    backgroundColor: "{colors.background}"
    textColor: "{colors.foreground}"
    rounded: "{rounded.lg}"
  sidebar:
    backgroundColor: "{colors.muted}"
    width: "232px"
  sidebar-dark:
    backgroundColor: "{colors.sidebar-dark}"
    width: "232px"
  level-stamp-alta:
    textColor: "{colors.alta}"
    typography: "{typography.stamp}"
  level-stamp-media:
    textColor: "{colors.media}"
    typography: "{typography.stamp}"
  level-stamp-baja:
    textColor: "{colors.baja}"
    typography: "{typography.stamp}"
  sim-badge:
    backgroundColor: "{colors.sim-bg}"
    textColor: "{colors.sim}"
    typography: "{typography.stamp}"
    rounded: "{rounded.md}"
    padding: "2px 8px"
  sim-badge-dark:
    backgroundColor: "{colors.sim-bg-dark}"
    textColor: "{colors.sim-dark}"
    rounded: "{rounded.md}"
    padding: "2px 8px"
  score-bar:
    backgroundColor: "{colors.muted}"
    rounded: "{rounded.full}"
    width: "96px"
    height: "6px"
  dialog:
    backgroundColor: "{colors.background}"
    textColor: "{colors.foreground}"
    rounded: "{rounded.2xl}"
    padding: "20px 24px"
  image-viewer:
    backgroundColor: "{colors.viewer}"
    rounded: "{rounded.md}"
---

# Design System: Aurora

## Overview

**Creative North Star: "La Orden de Mamografía"**

Aurora se lee como el formulario clínico que ordena un examen: un diagrama bilateral Derecha/Izquierda preciso, un código de caso que funciona como titular y un solo timbre de prioridad por caso. La interfaz es una herramienta de trabajo para administrativos y médicos de APS que pasan horas frente a ella: densa en datos, legible a 15 px de base, estructurada con reglas finas en lugar de rellenos y tarjetas apiladas.

El sistema vive en dos temas con identidad propia, no en un tema y su inverso. El tema claro es blanco con superficies de rubor y un rosa clínico profundo como única voz de acción; el tema oscuro es un suelo berenjena casi negro con superficies moradas y un violeta como acción. En ambos, los tres niveles de triage (ALTA, MEDIA, BAJA) usan una escala única y fija: el color dice el nivel y el grosor del anillo dice la urgencia, de modo que el nivel se distingue también sin color. La profundidad se reserva para lo que de verdad flota (diálogos, menús, tooltips); todo lo demás es plano y se separa con una regla.

Rechazos confirmados en el contrato de dirección y visibles en la construcción: nada de tablero de tarjetas KPI con gradientes, nada de grilla de tarjetas idénticas, nada de rosa infantil ni tono de marketing.

**Key Characteristics:**
- Código del caso (AUR-AAAA-NNNNNN) como titular, en peso 800 con cifras tabulares.
- Timbre de nivel: anillo cuyo grosor sube con la urgencia (1.5 / 2.5 / 3.5 px) más el nombre del nivel.
- Lámina bilateral D/I como firma visual del detalle del caso.
- Reglas finas de 1 px como estructura; sin sombras en superficies en reposo.
- Una sola familia tipográfica (Atkinson Hyperlegible Next) con jerarquía por escala y peso.
- Badge «IA SIMULADA» obligatorio y visible en todo resultado del proveedor simulado.

## Colors

Dos paletas hermanas con la misma estructura de roles: rubor y rosa clínico en claro, berenjena y violeta en oscuro, más una escala clínica de tres niveles que nunca cambia de significado.

### Primary
- **Rosa Clínico** (primary, hsl(333 78% 42%)): relleno del botón primario, foco (ring), casillas y radios. Una sola acción primaria por zona.
- **Rosa de Marca** (brand, hsl(333 78% 40%)): icono de la sección activa, borde de foco de campos, cursor de texto, miniatura seleccionada y diagrama activo de la lámina.
- **Violeta Acción** (primary-dark, hsl(262 83% 58%)): el mismo rol que Rosa Clínico en tema oscuro.
- **Violeta Texto** (brand-dark, hsl(256 100% 80%)): rol de brand en tema oscuro; también es el color del anillo de foco, porque tiene contraste sobre berenjena.

### Tertiary (escala clínica)
- **Rojo ALTA** (alta / alta-dark): timbre ALTA, contador ALTA de la barra lateral, veredictos de falso positivo o negativo.
- **Ámbar MEDIA** (media / media-dark): timbre MEDIA, estado «En revisión», miniatura «por validar».
- **Verde BAJA** (baja / baja-dark): timbre BAJA, estado «Cerrado», mensajes de éxito, veredicto concordante.
- **Azul Informativo** (info / info-dark): estado «Priorizado» y la marca de nivel ajustado por un médico.
- **Ocre Simulado** (sim sobre sim-bg; sim-dark sobre sim-bg-dark): exclusivo del badge «IA SIMULADA» y de la leyenda «Resultado ficticio».

### Neutral
- **Blanco** (background): fondo de página, tarjetas, popovers y campos en tema claro.
- **Tinta Ciruela** (foreground, hsl(324 31% 12%)): texto principal en claro.
- **Rubor** (muted, hsl(333 76% 97%)): barra lateral, pista de la barra de puntaje, grupo segmentado de filtros.
- **Rubor Acento** (accent): hover de filas, botones fantasma y navegación.
- **Ciruela Tenue** (muted-foreground): texto secundario, encabezados de tabla, navegación inactiva.
- **Regla Rubor** (border, hsl(335 60% 89%)): toda regla de 1 px.
- **Trazo de Campo** (input): borde de campos y botones secundarios, un paso más oscuro que la regla.
- **Suelo Berenjena** (background-dark, hsl(268 33% 8%)), **Superficie Berenjena** (card-dark), **Lateral Berenjena** (sidebar-dark), **Tinta Lavanda** (foreground-dark), **Lavanda Tenue** (muted-foreground-dark), **Regla Morada** (border-dark), **Trazo Morado** (input-dark), **Acento Morado** (accent-dark): los mismos roles en oscuro.
- **Negatoscopio** (viewer, hsl(268 33% 6%)): fondo del visor de imágenes y de las miniaturas, oscuro en ambos temas, como un negatoscopio.

### Named Rules
**The One Scale Rule.** ALTA, MEDIA y BAJA tienen un único color y un único grosor de anillo en toda la aplicación (tabla, filtros, barra lateral, detalle, gráficos). Esos colores no se usan para nada que no sea nivel o su equivalente semántico (alerta, revisión, cierre).

**The Simulated Ochre Rule.** El ocre de «IA SIMULADA» pertenece solo a lo simulado. Ningún otro componente lo toma prestado, y ningún resultado simulado aparece sin él.

**The Two Worlds Rule.** Cada token tiene un valor propio en claro y en oscuro; el oscuro no se obtiene invirtiendo el claro. Todo color nuevo se define en ambos `:root` y `.dark` de `src/index.css`.

## Typography

**Display Font:** Atkinson Hyperlegible Next Variable (con system-ui, sans-serif), autoalojada vía @fontsource-variable.
**Body Font:** la misma familia.

**Character:** una sola familia diseñada para legibilidad de baja visión; la jerarquía sale de la escala y del peso, no de una segunda fuente. Cifras tabulares activadas en todo el documento para que códigos, RUT, puntajes y fechas alineen en columna.

### Hierarchy
- **Display** (800, 2.25rem / 2.6rem, -0.025em): código del caso en el detalle y título de inicio de sesión.
- **Headline** (800, 1.75rem / 2.1rem, -0.015em): título de cada página.
- **Title** (700, 1rem / 1.5rem): títulos de sección dentro de tarjetas y estados vacíos; los diálogos usan 1.125rem.
- **Body** (400, 0.9375rem / 1.4rem): texto base de 15 px; celdas de tabla, campos, botones (600) y navegación.
- **Label** (600, 0.8125rem / 1.15rem): encabezados de tabla, rótulos de dato y ayudas; 13 px es el mínimo de la escala.
- **Stamp** (800, 0.8125rem, +0.025em, mayúsculas por contenido): nombre del nivel en el timbre y texto del badge «IA SIMULADA».

### Named Rules
**The 13 px Floor Rule.** Ningún texto baja de 0.8125rem; la escala de Tailwind está redefinida para que `xs` ya sea 13 px.

**The Code-as-Headline Rule.** El identificador AUR del caso es el titular, en peso 800 y cifras tabulares, tanto en el detalle como en la columna principal de las tablas.

## Layout

Barra lateral fija de 232 px a la altura de la ventana desde `lg` (1024 px); bajo ese ancho se convierte en una franja superior con navegación horizontal desplazable. El área de trabajo usa un relleno de 24 px (32 px desde `lg`) y un ancho máximo de 1440 px. Las vistas de casos combinan lista y detalle en dos columnas. El ritmo se construye sobre 8, 12, 16 y 24 px; las tarjetas llevan 24 px de relleno interno y la lámina bilateral 20 px. Las tablas son densas: filas de alrededor de 44 px, celdas de 12 px de relleno lateral y una regla inferior por fila, sin rayado alterno.

## Elevation & Depth

Sistema plano con profundidad por rango. Las superficies en reposo (tarjetas, tablas, barra lateral, lámina) no tienen sombra: se separan del fondo por una regla de 1 px y, en oscuro, por un escalón tonal (suelo, superficie, lateral). La sombra existe solo para lo que flota sobre el contenido.

### Shadow Vocabulary
- **Overlay** (`box-shadow: 0 18px 48px -12px hsl(var(--shadow) / 0.45), 0 2px 6px hsl(var(--shadow) / 0.18)`): diálogos, menú de notificaciones y tooltip de gráficos. El tono de sombra es ciruela en claro y casi negro en oscuro.
- **Velo de diálogo** (fondo `hsl(var(--shadow) / 0.55)`): oscurece la página detrás de un diálogo.

### Named Rules
**The Acetate Rule.** La sombra indica rango real: si un elemento no se superpone a otro contenido, no lleva sombra.

## Shapes

Esquinas suaves y consistentes por tamaño de objeto: 6 px para chips, badges, segmentos de filtro y miniaturas; 8 px para botones, campos, ítems de navegación y avisos; 12 px para tarjetas, la lámina y menús; 16 px solo para diálogos. Lo circular se reserva para señales: puntos de estado de 8 px, anillos de timbre y la barra de puntaje. Los bordes son siempre de 1 px, salvo el anillo de nivel, cuyo grosor es significado. El diagrama de mama es un dibujo lineal (contorno de 1.5 px, anillo interior punteado, marcas horarias 12/3/6/9 y cola axilar), nunca relleno salvo un velo del 6 % cuando el lado está activo.

## Components

### Buttons
Directos y sobrios; un solo relleno de color por zona.
- **Shape:** esquinas suaves (8 px), alto fijo de 40 px, 16 px de relleno lateral, texto de 15 px en 600.
- **Primary:** relleno primary (rosa o violeta según tema) con texto blanco; hover al 90 %, activo al 80 %; deshabilitado pasa a muted con texto tenue.
- **Secondary:** borde input, fondo de tarjeta, hover en accent.
- **Ghost:** solo texto tenue; hover sube a foreground sobre accent.
- **Danger:** relleno destructive; solo para acciones irreversibles.
- **Icon:** 36 × 36 px, mismo trato que ghost.
- **Focus:** contorno de 2 px en ring con 2 px de separación, global para todo elemento enfocable.

### Chips
- **Filtro segmentado:** grupo sobre muted con 4 px de relleno; cada segmento de 32 px de alto y 6 px de esquina; el seleccionado se eleva a superficie de tarjeta con un anillo de 1 px en border y texto en 700. Los filtros de nivel llevan su anillo de timbre.
- **Veredicto de IA:** borde, fondo al 10 % y texto del color semántico (baja para concordante, alta para falso positivo o negativo, neutro para no evaluable).

### Cards / Containers
- **Corner Style:** 12 px.
- **Background:** card (blanco en claro, superficie berenjena en oscuro).
- **Shadow Strategy:** ninguna (ver Elevation & Depth).
- **Border:** regla de 1 px en border.
- **Internal Padding:** 24 px; las secciones internas se dividen con reglas, no con tarjetas anidadas.

### Inputs / Fields
- **Style:** 40 px de alto, 12 px de relleno lateral, borde input, fondo background, esquinas de 8 px; rótulo encima en 15 px y 500, ayuda debajo en 13 px.
- **Focus:** borde en brand y halo de 2 px en ring al 40 %; hover lleva el borde a brand al 50 %.
- **Error / Disabled:** `aria-invalid` cambia el borde a destructive; deshabilitado al 60 % de opacidad. Los errores se anuncian con `role="alert"` en un aviso con fondo destructive al 10 %.

### Navigation
- **Barra lateral:** fondo sidebar, marca oficial arriba (símbolo PNG con transparencia, una versión por tema), ítems de 40 px con icono lineal de 18 px. Inactivo en texto tenue; activo sube a superficie de tarjeta con anillo de 1 px, texto en 700 e icono en brand. «Cola de triage» muestra el contador ALTA con su anillo. Pie con usuario, rol, campana (médico), tema y salida.

### Timbre de nivel (firma)
Anillo vacío de 14 px (20 px en tamaño grande) en el color del nivel, con borde de 1.5 px para BAJA, 2.5 px para MEDIA y 3.5 px para ALTA, seguido del nombre del nivel en Stamp. Incluye texto para lectores de pantalla. Sin nivel se muestra «Sin triage» en texto tenue.

### Barra de puntaje
Pista de 96 × 6 px sobre muted, relleno en el color del nivel sobre la escala fija 0–100 y el número en 600 con cifras tabulares. La escala nunca se reajusta al máximo observado.

### Badge «IA SIMULADA»
Texto Stamp en sim sobre sim-bg, borde sim al 50 %, esquinas de 6 px, sin salto de línea. Acompaña a todo resultado del proveedor simulado.

### Lámina bilateral D/I (firma)
Contenedor de 12 px con regla y 20 px de relleno, dividido en dos columnas por una regla vertical: Derecha a la izquierda y Izquierda a la derecha, como en la orden. Cada lado lleva el diagrama de mama (activo en brand, inactivo en muted-foreground al 45 %), el nombre del lado y su leyenda, y debajo sus miniaturas 4:5 sobre Negatoscopio. La miniatura seleccionada lleva anillo de 2 px en brand. La acción primaria del caso va bajo la lámina.

### Diálogo
Radix: foco atrapado, Esc para cerrar. Superficie popover, esquinas de 16 px, sombra Overlay, cabecera y pie separados por reglas, aparición por fundido de 160 ms.

## Do's and Don'ts

### Do:
- **Do** usar la escala ALTA/MEDIA/BAJA con sus anillos de 3.5 / 2.5 / 1.5 px en todo lugar donde aparezca un nivel.
- **Do** separar superficies con reglas de 1 px en border y reservar shadow-overlay para diálogos, menús y tooltips.
- **Do** definir cada color nuevo como token HSL en ambos temas (`:root` y `.dark`) y consumirlo vía Tailwind.
- **Do** poner el código AUR como titular del caso, en 800 con cifras tabulares.
- **Do** mostrar el badge «IA SIMULADA» junto a todo resultado simulado.
- **Do** mantener los textos en 13 px como mínimo y la base en 15 px.

### Don't:
- **Don't** construir tableros de tarjetas KPI con gradientes ni grillas de tarjetas idénticas.
- **Don't** usar rosa infantil ni tono de marketing; el rosa del tema claro es clínico y profundo (primary).
- **Don't** poner sombra a tarjetas, tablas o la lámina en reposo.
- **Don't** usar los colores de nivel ni el ocre simulado como decoración.
- **Don't** agregar una segunda familia tipográfica; la jerarquía es por escala y peso.
