# My LaTeX Notes Setup (macOS)

This is my personal notes system for classes and random math/CS topics.  
Main goal: keep note-taking fast in Neovim, make figure drawing easy in Inkscape, and keep everything organized without extra overhead.

## What this project does

- organizes notes as `courses/` and `topics/`
- creates lecture files like `lec_01.tex`, `lec_02.tex`, etc.
- keeps a `master.tex` per notebook to compile everything together
- supports multiple built-in layout templates (including Gilles Castel lecture-note styles)
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

## Permanent PATH for `notes`

Temporary (current shell only):

```bash
export PATH="/Users/gabe/Github/Latex-Lecture-Template/bin:$PATH"
```

Permanent on zsh:

```bash
echo 'export PATH="/Users/gabe/Github/Latex-Lecture-Template/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

Permanent on bash:

```bash
echo 'export PATH="/Users/gabe/Github/Latex-Lecture-Template/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

## Quick start

Create a course and set it active:

```bash
notes init-course algebra --title "Algebra I" --short ALG1 --template template1
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
- `Space+I` opens a searchable picker and edits a selected figure in Inkscape

Picker requirement:

- install `choose-gui` (used by figure search on both macOS and Linux)
- picker executable can be either `choose-gui` or `choose`

Troubleshooting:

- if `Space+I` shows `No figures directory`, open a file in a notebook with a `figures/` folder
- if it shows `No .svg figures found`, create a figure first with `Space+i`
- if it shows `Picker not found`, install `choose-gui`

CLI options:

```bash
notes list-figures
notes pick-figure
```

## Neovim config note

The source config is in `nvim/`, and `scripts/install_nvim_config.sh` copies it to `~/.config/nvim`.

### Snippets (UltiSnips)

This repo configures UltiSnips triggers (`Tab` / `Shift-Tab`) and notebook-local snippet loading from `UltiSnips/tex.snippets` (Gilles Castel snippet file is included in `templates/tex.snippets`).

You still need to install the plugins in your Neovim setup:

- `lervag/vimtex`
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

- `template1`
- `template2`
- `template3`
- `template4`

You can use `--template <name>` with both `notes init-course` and `notes init-topic`.
Each template maps to its own preamble file:

- `template1` -> `templates/preambles/template1.tex`
- `template2` -> `templates/preambles/template2.tex`
- `template3` -> `templates/preambles/template3.tex`
- `template4` -> `templates/preambles/template4.tex`
