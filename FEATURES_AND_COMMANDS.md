# Features And Commands Reference

This file is command-only reference. Setup/workflow context is in `README.md`.

## Setup Commands

- `./scripts/setup_macos.sh`: install dependencies for macOS
- `./scripts/install_nvim_config.sh`: install repo Neovim config into `~/.config/nvim`

## `notes` CLI

Notebook creation:

- `notes init-course <name> --title "<title>" --short <code> [--url <url>] [--template <name>]`
- `notes init-topic <name> --title "<title>" --short <code> [--url <url>] [--template <name>]`
- `notes list-templates`

Notebook listing/selection:

- `notes list-courses`
- `notes list-topics`
- `notes set-current <name>`
- `notes show-current`
- `notes pick-course`
- `notes pick-topic`

Lecture management:

- `notes new-lecture [--title "<title>"]`
- `notes list-lectures`
- `notes open-lecture <last|N>`
- `notes pick-lecture`
- `notes pick-lecture --include`
- `notes update-view <all|last|prev|prev-last|N|A-B>`
- `notes pick-view`
- `notes compile --current`
- `notes compile --course <name>`

Template defaults:

- new notebooks use `\documentclass[a4paper]{report}`
- each notebook gets a local `preamble.tex` at creation time
- available templates:
  - `lecture-color` (or `1`)
  - `lecture-light` (or `2`)
  - `lecture-dynamic` (or `3`)
  - `lecture-book` (or `4`)
  - `classic-book` (or `5`)
- file mapping:
  - `lecture-color` -> `templates/preambles/template1.tex`
  - `lecture-light` -> `templates/preambles/template2.tex`
  - `lecture-dynamic` -> `templates/preambles/template3.tex`
  - `lecture-book` -> `templates/preambles/template4.tex`
  - `classic-book` -> `templates/preambles/template5.tex`
- book parts:
  - `notes new-book-part series`
  - `notes new-book-part copyright`
  - `notes new-book-part preface`
  - `notes new-book-part summary`
  - `notes new-book-part conclusion`
  - `notes new-book-part answers`
  - `notes new-book-part symbols`
  - `notes new-book-part index`
- `classic-book` order:
  - half-title, optional series page, title page, copyright, preface, contents, chapters, bibliography, answers, list of symbols, index

Figure management:

- `notes list-figures`
- `notes open-figures`
- `notes pick-figure`

## `inkfig` CLI

- `inkfig create "<title>" <figures_dir>`
- `inkfig edit <figures_dir>`
- `inkfig watch`

## Figure Script

- `scripts/create_figure.sh <figure-name> [figure-dir]`

## Neovim Keymaps

- `Space+i`: create figure, open Inkscape, start per-figure watcher
- `Space+I`: search/pick `.svg` figure in current notebook and open it in Inkscape
- `Space+c+n`: init course
- `Space+c+s`: set current notebook
- `Space+l+n`: new lecture
- `Space+l+o`: open latest lecture

Figure picker dependency:

- install `choose-gui`; executable can be `choose-gui` or `choose`

Snippet dependencies:

- install `lervag/vimtex` and `SirVer/ultisnips`
- verify in Neovim with `:echo exists(':UltiSnipsEdit')` (expect `2`)
