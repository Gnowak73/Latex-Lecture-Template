# LaTeX Notes (Neovim + Inkscape)

This repo is a small notes system for classes and math/physics scratchwork on macOS. The goal is practical: write fast in Neovim, drop in clean Inkscape figures without fuss, and keep everything organized.

Notes live in two buckets:
- `courses/` for course notebooks
- `topics/` for one-off notebooks (homework sets, ideas, short projects)

Each notebook is self-contained (metadata, a `master.tex`, per-lecture/per-chapter files, figures, and local snippets).

From the repo root:

```bash
./scripts/setup_all.sh
```

That bootstraps the Python venv and installs the Neovim modules from this repo into `~/.config/nvim`. You can always run the tool as `./bin/notes ...`.

If you want `notes ...` to work anywhere, add this repo’s `bin/` to your shell `PATH`:

```bash
export PATH="/absolute/path/to/Latex-Lecture-Template/bin:$PATH"
```

Put that line in `~/.zshrc` (zsh, default on macOS) or `~/.bashrc` (bash). If a subcommand is “missing”, you’re likely calling a different `notes` binary; check with:

```bash
which -a notes
```

Create a course notebook and set it active:

```bash
./bin/notes init-course algebra --title "Algebra I" --short ALG1 --template lecture-color
./bin/notes set-current algebra
```

Add a lecture and compile:

```bash
./bin/notes new-lecture --title "Lecture 1"
./bin/notes open-lecture last
./bin/notes compile --current
```

Templates: multiple lecture-note templates (based on Gilles Castel’s layouts) plus `lecture-book` (tufte/masterthesis style). `lecture-book` always uses chapters (`chap_XX.tex` with `\chapter{...}`).

In Neovim (leader is Space):
- `Space+i` creates a new figure (writes a figure environment and opens Inkscape)
- `Space+I` opens a picker to edit an existing figure

The picker requires `choose-gui` (or `choose`) on your PATH. The figure flow also expects `inkscape` and (for auto-export watcher) `fswatch`.

CLI equivalents:
```bash
./bin/notes list-figures
./bin/notes pick-figure
```

Snippets: notebook-local snippets live at `UltiSnips/tex.snippets`. This repo ships a base snippet file in `templates/tex.snippets`, but snippets only work if you install UltiSnips in your Neovim plugin setup (and `vimtex` is strongly recommended).
- `SirVer/ultisnips`

Quick check inside Neovim:

```vim
:echo exists(':UltiSnipsEdit')
```

`2` means UltiSnips is loaded.

In TeX files, `<Tab>` / `<S-Tab>` are handled by UltiSnips for expand/jump.

If you see `E319: No "python3" provider found`, install `pynvim` for your Neovim python and re-run `:checkhealth vim.provider`.

## Commands reference

Full command list is here:

- [FEATURES_AND_COMMANDS.md](/Users/gabe/Github/Latex-Lecture-Template/FEATURES_AND_COMMANDS.md)

## Repo is safe to publish

Personal/local stuff is ignored by `.gitignore`:

- `.venv/`
- `.current_course`
- `courses/`
- `topics/`
Template options:

```bash
notes list-templates
```

Current built-ins:

- `lecture-color` (or `1`)
- `lecture-light` (or `2`)
- `lecture-dynamic` (or `3`)
- `lecture-book` (or `4`)

You can use `--template <name>` with both `notes init-course` and `notes init-topic`.
Each template maps to its own preamble file:

- `lecture-color` -> `templates/preambles/template1.tex`
- `lecture-light` -> `templates/preambles/template2.tex`
- `lecture-dynamic` -> `templates/preambles/template3.tex`
- `lecture-book` -> `templates/preambles/template4.tex`
