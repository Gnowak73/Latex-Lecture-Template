#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
NVIM_DIR="${XDG_CONFIG_HOME:-$HOME/.config}/nvim"

mkdir -p "$NVIM_DIR/lua"
cp "$ROOT_DIR/nvim/lua/figures.lua" "$NVIM_DIR/lua/figures.lua"
cp "$ROOT_DIR/nvim/lua/notes.lua" "$NVIM_DIR/lua/notes.lua"
cp "$ROOT_DIR/nvim/lua/snippets.lua" "$NVIM_DIR/lua/snippets.lua"

if ! rg -q 'require\("figures"\)' "$NVIM_DIR/init.lua" 2>/dev/null; then
  {
    echo ''
    echo 'vim.g.mapleader = " "'
    echo 'require("figures")'
    echo 'require("notes")'
  } >> "$NVIM_DIR/init.lua"
fi

if ! rg -q 'require\("snippets"\)' "$NVIM_DIR/init.lua" 2>/dev/null; then
  echo 'require("snippets")' >> "$NVIM_DIR/init.lua"
fi

echo "Installed Neovim modules to $NVIM_DIR"
