# Handoff — después de la iteración 18 del Informe Final (Proyecto Aurora)

**Fecha:** 27-11-2026 · **Rama:** `claude/bold-maxwell-13fkwp` · **Punto de partida:** maestro **1.8-rc**, registro
**v0.27** (secciones 4.24 y 4.25), PDF de 201 páginas, 71 tablas y 28 figuras. Reemplaza a `HANDOFF_ITERACION_18.md`
(queda como historia). Lee también `trabajo/PENDIENTES_EQUIPO.md` y `trabajo/ESTADO_ITERACION.md`.

## 1. Qué se hizo el 27-11-2026

- **Iteración 18:** diagrama de casos de uso con la disposición que pidió el equipo (`herramientas/casos_uso_drawio.py`)
  y punto **A3** hecho: subsección 10.7.1.1 «Desarrollo del modelo» desde la U2 (3 tablas, 4 referencias).
- **Iteración 18b:** los otros seis diagramas propios del capítulo X rehechos en notación estándar (UML de componentes y
  de despliegue, ER con pata de gallo) con aspecto de draw.io: `herramientas/diagramas_drawio.py` + `drawio_lib.py`.
  **Fuentes editables en `figuras/drawio/*.drawio`.** PNG con `herramientas/svg_a_png.cjs` (Chromium).
  Si el equipo edita un `.drawio`, exportar a PNG en draw.io (escala 2) y reemplazar con `iter18b_diagramas.py`.
- **Instalador local para Windows** (`deploy/instalador-windows/`, Inno Setup): versión **de prueba** con IA simulada
  que remite a demo.auroracare.cl. Workflow `.github/workflows/instalador-windows.yml`: prueba de punta a punta en
  Linux (pwsh + Docker), compila el .exe en Windows y publica en el release `instalador-windows`. **El .exe no se ha
  ejecutado en un Windows real.**
- **Plantilla de AWS para la consola** (`deploy/aws-consola/aurora-aws.yaml`): instala Aurora 2.11.0 en cualquier
  cuenta de AWS con CloudFormation, sin dominio (`<IP>.sslip.io`). Pasa cfn-lint; **no se ha creado en AWS**.
  Publicada en el release `aws-consola`.
- **Manual de instalación** (`docs/manual_instalacion/`): Markdown fuente, Word y PDF (11 páginas); se regenera con
  `python3 docs/manual_instalacion/generar_manual.py`.

## 2. Qué falta

- **Del equipo** (`trabajo/PENDIENTES_EQUIPO.md`): dedicatoria, agradecimientos, Shah et al. (2023), GLOBOCAN y GES
  (capítulo II), referencias 2026b/2026c/OMS/NEMA/ACR. Se cargan con `pendientes_equipo.json` +
  `herramientas/completar_pendientes.sh`. Opcional: desplegar la 2.12.0 y repetir PC-01 en AWS.
- **Probar en real:** el .exe en un PC con Windows y la plantilla en una cuenta de AWS, siguiendo el manual.
- Lectura final y aceptación de la versión 1.0.

## 3. Reglas que no cambian

Ver `HANDOFF_ITERACION_18.md`, secciones 4 a 6 (maestro único con respaldo previo, no inventar evidencia, sin
coautoría de Claude en main, sin `push --force`, una sola región de AWS).
