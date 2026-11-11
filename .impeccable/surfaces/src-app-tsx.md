---
version: 1
slug: "src-app-tsx"
primary_target: "src/App.tsx"
related_targets: ["src/components"]
---

# App Aurora (shell y todas las pantallas)

Modo: Operate. Usuarios: administrativo, médico y admin de APS en escritorio o notebook. Tarea: registrar casos, priorizar, revisar, validar la IA y firmar. Restricciones: WCAG 2.1 AA, densidad de datos alta, nada de marketing ni de rosa infantil. Tema oscuro morado/negro y tema claro rosado/blanco.

## Direction contract

THESIS: Cada caso se lee como una orden de mamografía: un diagrama bilateral D/I preciso y un solo timbre de prioridad. Rechaza el tablero de tarjetas KPI con gradientes y la grilla de tarjetas idénticas.

OWN-WORLD: Oscuro: suelo berenjena #140E1C, superficie #1C1426, regla fina #342844, tinta #F3EEF8, violeta texto #B79BFF y acción #7C3AED. Claro: blanco, superficie rubor #FDF2F6, regla #F3D3E0, tinta ciruela #2A1622, rosa clínico #BE185D. Timbres ALTA/MEDIA/BAJA con anillo de grosor fijo por nivel. Reglas finas, sin sombras salvo diálogos y menús. Atkinson Hyperlegible Next, base de 15 px.

STORY: El administrativo registra sin dudar; el médico ve primero los casos ALTA, entiende por qué cada caso tiene su nivel, corrige con motivo y avanza al siguiente.

FIRST VIEWPORT: Barra lateral fija de 232 px con marca y secciones (contador ALTA en la cola). Centro: título, filtros y tabla densa con el código AUR como titular, timbre de nivel, barra de puntaje en escala fija, estado y espera. El detalle del caso lleva la lámina bilateral D/I con las imágenes de cada lado; la acción primaria está bajo la lámina.

FORM: Orden de mamografía, candidato 7 de 7; seed: ea39d65687947ba7. Raises: escala fija única (atlas), código como titular (Factory), reglas sin relleno (densidad japonesa), profundidad solo con rango real (acetato), siguiente caso a una acción (feed), jerarquía por escala (espécimen).

FINISH: unreviewed and undocumented is unfinished; this build ends with the finish review, the verdict, DESIGN.md, and every shipping raster carrying its provenance
