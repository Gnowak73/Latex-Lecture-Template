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

Create a Letter-size cutting proof for a 6x9 classic book:

```bash
notes print-letter --current
# or: notes print-letter --course symon-layout-test
```

This writes `print-letter.pdf` beside `master.pdf`, centered at its true 6x9
size on 8.5x11 Letter paper with a trim box and corner crop marks. Print that
PDF using `Actual Size` or `100%`, never `Fit` or `Scale to page`.

Create and print an A5-folded booklet. The source PDF uses A6 finished pages;
the print PDF places two pages on each side of an A5 landscape sheet in
booklet order and pads the total to a multiple of four pages.

```bash
notes init-course pamphlet \
  --title "Small Pamphlet" \
  --short PAMPHLET \
  --template a5book \
  --author "Your Name"
notes set-current pamphlet
notes new-lecture --title "Introduction"
notes print-a5-booklet --current
```

Print `print-a5-booklet.pdf` at `Actual Size` or `100%`, double-sided, with
`Flip on short edge`, then stack and fold the sheets in half.

Templates: multiple lecture-note templates (based on Gilles Castel’s layouts), `lecture-book` (tufte/masterthesis style), `6x9book` (the 6x9 Addison-Wesley/Symon-style textbook), and `a5book` (the analogous A6 finished page for folding A5 sheets). Book templates always use chapters (`chap_XX.tex` with `\chapter{...}`).

The `6x9book` and `a5book` templates vendor the custom `Symon Schoolbook` Type 1 family into each project. It is an optically lightened, renamed derivative of TeX Gyre Schola with unchanged TeX metrics, so line breaks and the Fourier New Century Schoolbook mathematics remain stable. Rebuild the bundled PFB and OTF files with `fontforge -script scripts/build_symon_schoolbook.py`.

For both classic book sizes, optional book parts are included in this order when present:
half-title, series page, title page, copyright, dedication, preface, contents, chapters, bibliography, answers to odd-numbered problems, index of symbols, index.
The bibliography leaf is omitted when `bibliography.bib` has no BibTeX entries;
after adding an `@book`, `@article`, or other entry, run `notes fix-master` to include it.

Choose the running-head scheme when creating the book. `symon` uses chapter and
section heads; `math` replaces their inner markers with the current numbered
statement (`THM.`, `DEF.`, `LEM.`, and so on).

```bash
notes init-course analysis \
  --title "Mathematical Analysis" \
  --short ANALYSIS \
  --template 6x9book \
  --author "Tom M. Apostol" \
  --affiliation "California Institute of Technology" \
  --edition "First Edition" \
  --printing "First Printing" \
  --printing-date "January 1960" \
  --preface-date "January, 1960" \
  --preface-author "T. M. A." \
  --series "ADDISON-WESLEY SERIES IN MATHEMATICS" \
  --publisher "ADDISON-WESLEY PUBLISHING COMPANY, INC." \
  --publisher-location "Reading, Massachusetts, U.S.A." \
  --publisher-location "London, England" \
  --copyright-years "1957, 1960" \
  --catalog-card "60-5164" \
  --publisher-mark folio-star \
  --printed-line "Printed in the United States of America" \
  --copyright-notice "All rights reserved. This book, or parts there-|of, may not be reproduced in any form with-|out written permission of the publisher." \
  --catalog-label "Library of Congress Catalog Card No." \
  --running-heads math
```

All title and copyright fields are optional. New books use the printed-in-USA
line and rights notice shown above by default; pass an empty `--printed-line`
or `--copyright-notice` to omit either one. The same settings can be changed
later in `info.yaml`, including `running_heads: 'symon'` or
`running_heads: 'math'`, followed by `notes fix-master`.

```bash
notes new-book-part copyright
notes new-book-part dedication
notes new-book-part preface
notes new-book-part answers
notes new-book-part index
notes fix-master
```

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
- `6x9book` (or `5`; legacy name `classic-book` also works)
- `a5book` (or `6`; A6 finished pages on folded A5 sheets)

You can use `--template <name>` with both `notes init-course` and `notes init-topic`.
Each template maps to its own preamble file:

- `lecture-color` -> `templates/preambles/template1.tex`
- `lecture-light` -> `templates/preambles/template2.tex`
- `lecture-dynamic` -> `templates/preambles/template3.tex`
- `lecture-book` -> `templates/preambles/template4.tex`
- `6x9book` -> `templates/preambles/template5.tex`
- `a5book` -> `templates/preambles/a5book.tex` plus the shared classic-book rules

Classic book optional parts:

- `notes new-book-part series`
- `notes new-book-part copyright`
- `notes new-book-part dedication`
- `notes new-book-part preface`
- `notes new-book-part summary`
- `notes new-book-part conclusion`
- `notes new-book-part answers`
- `notes new-book-part symbols`
- `notes new-book-part index`
