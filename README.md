# My LaTeX Notes Setup (macOS)

This is my personal notes system for classes and random math/CS topics.  
Main goal: keep note-taking fast in Neovim, make figure drawing easy in Inkscape, and keep everything organized without extra overhead.

## What this project does

- organizes notes as `courses/` and `topics/`
- creates lecture files like `lec_01.tex`, `lec_02.tex`, etc.
- keeps a `master.tex` per notebook to compile everything together
- supports Inkscape figures with quick create/edit flow
- includes Neovim keymaps for daily use

## Folder structure per notebook

Each course/topic gets:

- `info.yaml` for metadata
- `master.tex` as the main compiled doc
- `lec_XX.tex` lecture files
- `figures/` for `.svg`, `.pdf`, `.pdf_tex`
- `UltiSnips/tex.snippets`

## Setup on macOS

```bash
cd /Users/gabe/Github/Latex-Lecture-Template
./scripts/setup_macos.sh
export PATH="$PWD/bin:$PATH"
./scripts/install_nvim_config.sh
```

That installs required tools and sets up the Neovim config from this repo.

## Quick start

Create a course and set it active:

```bash
notes init-course algebra --title "Algebra I" --short ALG1
notes set-current algebra
```

Create/open lecture and compile:

```bash
notes new-lecture --title "Lecture 1"
notes open-lecture last
notes compile --current
```

## Figures

In Neovim:

- `Space+i` creates a new figure and opens Inkscape
- `Space+I` lets you pick/edit an existing figure

CLI options:

```bash
notes list-figures
notes pick-figure
```

## Neovim config note

The source config is in `nvim/`, and `scripts/install_nvim_config.sh` copies it to `~/.config/nvim`.

## Commands reference

Full command list is here:

- [FEATURES_AND_COMMANDS.md](/Users/gabe/Github/Latex-Lecture-Template/FEATURES_AND_COMMANDS.md)

## Repo is safe to publish

Personal/local stuff is ignored by `.gitignore`:

- `.venv/`
- `.current_course`
- `courses/`
- `topics/`
