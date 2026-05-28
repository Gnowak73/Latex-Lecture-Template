#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"

usage() {
  cat <<'EOF'
Usage: scripts/bootstrap.sh [--yes] [--nvim]

Safe repo bootstrap:
- creates/updates .venv and installs python deps
- prints missing external deps (inkscape/fswatch/choose-gui/latexmk)
- optionally installs the repo Neovim modules into ~/.config/nvim (--nvim)

Flags:
  --yes   run non-interactively (assumes yes for prompts)
  --nvim  also run scripts/install_nvim_config.sh
EOF
}

ASSUME_YES=0
DO_NVIM=0

while [ $# -gt 0 ]; do
  case "$1" in
    --yes) ASSUME_YES=1 ;;
    --nvim) DO_NVIM=1 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown arg: $1" >&2; usage; exit 2 ;;
  esac
  shift
done

cd "$ROOT_DIR"

if ! command -v python3 >/dev/null 2>&1; then
  echo "Missing dependency: python3" >&2
  exit 1
fi

if [ ! -d "$ROOT_DIR/.venv" ]; then
  python3 -m venv "$ROOT_DIR/.venv"
fi

"$ROOT_DIR/.venv/bin/pip" install --upgrade pip >/dev/null
"$ROOT_DIR/.venv/bin/pip" install -r "$ROOT_DIR/requirements.txt" >/dev/null

missing=()
for cmd in inkscape fswatch latexmk; do
  if ! command -v "$cmd" >/dev/null 2>&1; then
    missing+=("$cmd")
  fi
done

if ! command -v choose-gui >/dev/null 2>&1 && ! command -v choose >/dev/null 2>&1; then
  missing+=("choose-gui(or choose)")
fi

if [ ${#missing[@]} -gt 0 ]; then
  echo "Missing external tools (install manually): ${missing[*]}" >&2
  echo "This script does not install system packages by default for safety." >&2
fi

if [ "$DO_NVIM" -eq 1 ]; then
  if [ "$ASSUME_YES" -eq 1 ]; then
    "$ROOT_DIR/scripts/install_nvim_config.sh"
  else
    printf "Install repo Neovim modules into ~/.config/nvim? [y/N] "
    read -r ans || true
    case "${ans:-}" in
      y|Y|yes|YES) "$ROOT_DIR/scripts/install_nvim_config.sh" ;;
      *) echo "Skipping Neovim install." ;;
    esac
  fi
fi

echo "Bootstrap complete."
