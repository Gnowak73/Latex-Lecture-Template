# Features And Commands Reference

This file is command-only reference. Setup/workflow context is in `README.md`.

## Setup Commands

- `./scripts/setup_macos.sh`: install dependencies for macOS
- `./scripts/install_nvim_config.sh`: install repo Neovim config into `~/.config/nvim`

## `notes` CLI

Notebook creation:

- `notes init-course <name> --title "<title>" --short <code> [--url <url>]`
- `notes init-topic <name> --title "<title>" --short <code> [--url <url>]`

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
