#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
VENDORED="$ROOT_DIR/tools/figure-manager"
VENV_PY="$ROOT_DIR/.venv/bin/python3"
CONFIG_DIR="$ROOT_DIR/config/figure-manager"
DEFAULT_TEMPLATE="$ROOT_DIR/templates/template.svg"

if [ -x "$VENV_PY" ]; then
  PYTHON_BIN="$VENV_PY"
elif command -v python3 >/dev/null 2>&1; then
  PYTHON_BIN="python3"
else
  echo "python3 is required" >&2
  exit 1
fi

mkdir -p "$CONFIG_DIR"
cp "$DEFAULT_TEMPLATE" "$CONFIG_DIR/template.svg"

PYTHONPATH="$VENDORED${PYTHONPATH:+:$PYTHONPATH}" \
INKSCAPE_FIGURES_CONFIG_DIR="$CONFIG_DIR" \
  "$PYTHON_BIN" "$VENDORED/bin/inkscape-figures" "$@"
