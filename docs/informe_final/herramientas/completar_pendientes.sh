#!/usr/bin/env bash
# Aplica trabajo/pendientes_equipo.json al maestro, valida el DOCX y exporta el PDF.
# Uso (desde cualquier carpeta):  bash docs/informe_final/herramientas/completar_pendientes.sh [--probar]
#   --probar: aplica en una copia temporal y muestra el resumen, sin tocar el maestro ni el PDF.
# Requiere: python3, zip/unzip, LibreOffice (soffice, con python3-uno) para el PDF.
set -euo pipefail
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"   # docs/informe_final
MAESTRO="$DIR/trabajo/Proyecto_Aurora_Informe_Final_Maestro.docx"
PDF="$DIR/trabajo/Proyecto_Aurora_Informe_Final.pdf"
JSON="$DIR/trabajo/pendientes_equipo.json"
TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT

mkdir "$TMP/m" && (cd "$TMP/m" && unzip -q "$MAESTRO")
python3 "$DIR/herramientas/completar_pendientes.py" "$TMP/m" "$JSON"
(cd "$TMP/m" && zip -XrDqy "$TMP/maestro.docx" . -x '.*' && zip -d "$TMP/maestro.docx" '*/' >/dev/null 2>&1 || true)

VALIDATE="${DOCX_VALIDATE:-/mnt/skills/public/docx/scripts/office/validate.py}"
if [ -f "$VALIDATE" ]; then (cd "$(dirname "$VALIDATE")/.." && python3 office/validate.py "$TMP/maestro.docx" | tail -1); fi

if [ "${1:-}" = "--probar" ]; then echo "Prueba: el maestro no se modificó."; exit 0; fi

STAMP="$(date +%Y%m%d-%H%M%S)"
cp "$MAESTRO" "$DIR/respaldos/Proyecto_Aurora_Informe_Final_Maestro_pre-pendientes_$STAMP.docx"
cp "$TMP/maestro.docx" "$MAESTRO"
python3 "$DIR/herramientas/exportar_pdf.py" "$MAESTRO" "$PDF"
command -v pdfinfo >/dev/null && pdfinfo "$PDF" | grep Pages || true
echo "Listo. Respaldo previo: respaldos/Proyecto_Aurora_Informe_Final_Maestro_pre-pendientes_$STAMP.docx"
echo "Falta: anotar el cambio en el registro de revisiones y en trabajo/ESTADO_ITERACION.md (ver PENDIENTES_EQUIPO.md)."
