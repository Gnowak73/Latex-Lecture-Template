#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"

usage() {
  cat <<'EOF'
Usage: scripts/setup_all.sh [--yes] [--system-deps] [--verify-templates]

One-script setup for this repo.

What it does:
- bootstraps the repo python venv + deps
- installs the repo Neovim modules into ~/.config/nvim
- optionally installs external tools (macOS only) via scripts/setup_macos.sh
- optionally verifies templates/snippets against upstream Gilles repos

Flags:
  --yes              non-interactive (assume yes)
  --system-deps      install system deps (macOS/Homebrew only)
  --verify-templates run scripts/verify_upstream_templates.sh
EOF
}

ASSUME_YES=0
INSTALL_SYSTEM_DEPS=0
VERIFY_TEMPLATES=0

while [ $# -gt 0 ]; do
  case "$1" in
    --yes) ASSUME_YES=1 ;;
    --system-deps) INSTALL_SYSTEM_DEPS=1 ;;
    --verify-templates) VERIFY_TEMPLATES=1 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown arg: $1" >&2; usage; exit 2 ;;
  esac
  shift
done

cd "$ROOT_DIR"

say() { printf '%s\n' "$*"; }

confirm() {
  local prompt="$1"
  if [ "$ASSUME_YES" -eq 1 ]; then
    return 0
  fi
  printf "%s [y/N] " "$prompt"
  local ans
  read -r ans || true
  case "${ans:-}" in
    y|Y|yes|YES) return 0 ;;
    *) return 1 ;;
  esac
}

OS="$(uname -s)"

say "Step 1/4: repo bootstrap (venv + python deps)"
"$ROOT_DIR/scripts/bootstrap.sh" --yes --nvim

say "Step 2/4: external tools"
if [ "$INSTALL_SYSTEM_DEPS" -eq 1 ]; then
  if [ "$OS" = "Darwin" ]; then
    "$ROOT_DIR/scripts/setup_macos.sh"
  else
    say "Skipping: --system-deps is only implemented for macOS/Homebrew."
  fi
else
  if [ "$OS" = "Darwin" ]; then
    if confirm "Install external tools via Homebrew (fswatch/choose-gui/inkscape)?"; then
      "$ROOT_DIR/scripts/setup_macos.sh"
    else
      say "Skipping external tools install."
    fi
  else
    say "Not installing external tools automatically on $OS."
  fi
fi

say "Step 3/4: PATH hint"
say "To use repo commands, add this to your shell PATH:"
say "  export PATH=\"$ROOT_DIR/bin:\$PATH\""

say "Step 4/4: verify templates (optional)"
if [ "$VERIFY_TEMPLATES" -eq 1 ]; then
  "$ROOT_DIR/scripts/verify_upstream_templates.sh"
else
  if confirm "Verify templates/snippets match upstream Gilles repos?"; then
    "$ROOT_DIR/scripts/verify_upstream_templates.sh"
  else
    say "Skipping template verification."
  fi
fi

say "All done."
