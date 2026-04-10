#!/usr/bin/env bash
set -euo pipefail

if [ $# -lt 1 ]; then
  echo "Usage: $0 <figure-name> [figure-dir]" >&2
  exit 1
fi

FIG_NAME="$1"
FIG_DIR="${2:-figures}"

SVG_PATH="$FIG_DIR/$FIG_NAME.svg"
PDF_PATH="$FIG_DIR/$FIG_NAME.pdf"

if [ ! -f "$SVG_PATH" ]; then
  cp "$FIG_DIR/template.svg" "$SVG_PATH"
fi

if command -v open >/dev/null 2>&1; then
  open -a Inkscape "$SVG_PATH" || inkscape "$SVG_PATH" &
else
  inkscape "$SVG_PATH" &
fi

fswatch -o "$SVG_PATH" | while read f; do
  inkscape "$SVG_PATH" \
    --export-type=pdf \
    --export-latex \
    --export-filename="$PDF_PATH"
done
