#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
TMP_DIR="${TMPDIR:-/tmp}"

LECTURE_NOTES_DIR="$TMP_DIR/gilles_lecture_notes"
MASTERTHESIS_DIR="$TMP_DIR/gilles_masterthesis"
LATEX_SNIPPETS_DIR="$TMP_DIR/gilles_latex_snippets"

clone_or_update() {
  local url="$1"
  local dir="$2"
  if [ -d "$dir/.git" ]; then
    (cd "$dir" && git pull --ff-only >/dev/null)
  else
    git clone --depth 1 "$url" "$dir" >/dev/null
  fi
}

echo "Fetching upstream repos..."
clone_or_update "https://github.com/gillescastel/lecture-notes" "$LECTURE_NOTES_DIR"
clone_or_update "https://github.com/gillescastel/masterthesis" "$MASTERTHESIS_DIR"
clone_or_update "https://github.com/gillescastel/latex-snippets" "$LATEX_SNIPPETS_DIR"

echo "Diff: lecture templates"
diff -u "$LECTURE_NOTES_DIR/algebraic-topology/preamble.tex" "$ROOT_DIR/templates/preambles/template1.tex" >/dev/null
diff -u "$LECTURE_NOTES_DIR/differential-geometry/preamble.tex" "$ROOT_DIR/templates/preambles/template2.tex" >/dev/null
diff -u "$LECTURE_NOTES_DIR/group-theory/preamble.tex" "$ROOT_DIR/templates/preambles/template3.tex" >/dev/null

echo "Diff: book template preamble"
diff -u "$MASTERTHESIS_DIR/thesis/preamble.tex" "$ROOT_DIR/templates/preambles/template4.tex" >/dev/null

echo "Diff: book class/sty"
diff -u "$MASTERTHESIS_DIR/thesis/tuftebook.cls" "$ROOT_DIR/templates/book/tuftebook.cls" >/dev/null
diff -u "$MASTERTHESIS_DIR/thesis/marginfix.sty" "$ROOT_DIR/templates/book/marginfix.sty" >/dev/null

echo "Diff: snippets"
diff -u "$LATEX_SNIPPETS_DIR/tex.snippets" "$ROOT_DIR/templates/tex.snippets" >/dev/null

echo "OK: all checked files match upstream."
