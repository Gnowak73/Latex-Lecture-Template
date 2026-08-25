#!/usr/bin/env python3
"""Unified lecture/course manager for this repository."""

from __future__ import annotations

import argparse
import datetime as dt
import os
import re
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COURSES_ROOT = ROOT / "courses"
TOPICS_ROOT = ROOT / "topics"
CURRENT_LINK = ROOT / ".current_course"
DATE_FORMAT = "%a %d %b %Y %H:%M"
SNIPPETS_TEMPLATE = ROOT / "templates" / "tex.snippets"
FIGURE_TEMPLATE = ROOT / "templates" / "template.svg"
PREAMBLES_DIR = ROOT / "templates" / "preambles"
BOOK_TEMPLATE_DIR = ROOT / "templates" / "book"
CLASSIC_FONT_DIR = ROOT / "templates" / "fonts" / "symon-schoolbook"
BOOK_PART_TEMPLATES: dict[str, Path] = {
    "series": BOOK_TEMPLATE_DIR / "series.tex",
    "copyright": BOOK_TEMPLATE_DIR / "copyright.tex",
    "dedication": BOOK_TEMPLATE_DIR / "dedication.tex",
    "preface": BOOK_TEMPLATE_DIR / "preface.tex",
    "summary": BOOK_TEMPLATE_DIR / "summary.tex",
    "conclusion": BOOK_TEMPLATE_DIR / "conclusion.tex",
    "answers": BOOK_TEMPLATE_DIR / "answers.tex",
    "symbols": BOOK_TEMPLATE_DIR / "symbols.tex",
    "index": BOOK_TEMPLATE_DIR / "index.tex",
}

TEMPLATE_PREAMBLES = {
    "lecture-color": PREAMBLES_DIR / "template1.tex",
    "lecture-light": PREAMBLES_DIR / "template2.tex",
    "lecture-dynamic": PREAMBLES_DIR / "template3.tex",
    "lecture-book": PREAMBLES_DIR / "template4.tex",
    "6x9book": PREAMBLES_DIR / "template5.tex",
    "a5book": PREAMBLES_DIR / "a5book.tex",
}

TEMPLATE_ALIASES = {
    "1": "lecture-color",
    "2": "lecture-light",
    "3": "lecture-dynamic",
    "4": "lecture-book",
    "5": "6x9book",
    "6": "a5book",
    "template1": "lecture-color",
    "template2": "lecture-light",
    "template3": "lecture-dynamic",
    "template4": "lecture-book",
    "template5": "6x9book",
    "template6": "a5book",
    "classic-book": "6x9book",
    "6x9-book": "6x9book",
    "a5-book": "a5book",
}

CLASSIC_BOOK_TEMPLATES = {"6x9book", "a5book"}

LETTER_PRINT_TEMPLATE = r"""\documentclass[letterpaper]{article}
\usepackage[margin=0in]{geometry}
\usepackage{pdfpages}
\usepackage{tikz}
\usetikzlibrary{calc}
\pagestyle{empty}

\newcommand{\booktrimmarks}{%
  \thispagestyle{empty}%
  \begin{tikzpicture}[remember picture,overlay,line width=0.2pt,line cap=butt]
    \coordinate (trimnw) at ([xshift=-3in,yshift=4.5in]current page.center);
    \coordinate (trimne) at ([xshift=3in,yshift=4.5in]current page.center);
    \coordinate (trimsw) at ([xshift=-3in,yshift=-4.5in]current page.center);
    \coordinate (trimse) at ([xshift=3in,yshift=-4.5in]current page.center);
    \draw (trimsw) rectangle (trimne);
    \draw ($(trimnw)+(-0.25in,0)$) -- ($(trimnw)+(-0.04in,0)$);
    \draw ($(trimnw)+(0,0.04in)$) -- ($(trimnw)+(0,0.25in)$);
    \draw ($(trimne)+(0.04in,0)$) -- ($(trimne)+(0.25in,0)$);
    \draw ($(trimne)+(0,0.04in)$) -- ($(trimne)+(0,0.25in)$);
    \draw ($(trimsw)+(-0.25in,0)$) -- ($(trimsw)+(-0.04in,0)$);
    \draw ($(trimsw)+(0,-0.04in)$) -- ($(trimsw)+(0,-0.25in)$);
    \draw ($(trimse)+(0.04in,0)$) -- ($(trimse)+(0.25in,0)$);
    \draw ($(trimse)+(0,-0.04in)$) -- ($(trimse)+(0,-0.25in)$);
  \end{tikzpicture}%
}

\begin{document}
\includepdf[
  pages=-,
  noautoscale=true,
  pagecommand={\booktrimmarks}
]{master.pdf}
\end{document}
"""

A5_BOOKLET_PRINT_TEMPLATE = r"""\documentclass[a5paper,landscape]{article}
\usepackage[margin=0pt]{geometry}
\usepackage{pdfpages}
\pagestyle{empty}

\begin{document}
\includepdf[
  pages=-,
  booklet,
  nup=2x1,
  noautoscale=true
]{master.pdf}
\end{document}
"""

MASTER_TEMPLATE = """\\documentclass[a4paper]{{report}}
\\input{{./preamble.tex}}
\\title{{{title}}}
\\author{{Gabriel Nowaskie}}
\\begin{{document}}
    \\maketitle
    \\tableofcontents
    % start lectures
    % end lectures
\\end{{document}}
"""

MASTER_TEMPLATE_BOOK_CHAPTERS = """\\documentclass[working]{{tuftebook}}

\\input{{preamble.tex}}
\\input{{symbols.tex}}
\\title{{{title}}}
\\author{{Gabriel Nowaskie}}
\\date{{{date}}}
\\begin{{document}}
    % Title page (centered; works well with tuftebook's layout).
    \\begin{{titlepage}}
        \\thispagestyle{{empty}}
        \\vspace*{{0.14\\textheight}}
        \\begin{{fullwidth}}
            \\centering
            {{\\LARGE {title}\\par}}
            \\vspace{{1.0em}}
            {{\\large {author}\\par}}
            \\vspace{{0.5em}}
            {{\\large {date}\\par}}
        \\end{{fullwidth}}
        \\vfill
    \\end{{titlepage}}

    % Match upstream masterthesis conventions:
    % roman numbering for frontmatter, plain style; arabic + "normal" style for main matter.
    \\renewcommand{{\\thepage}}{{\\roman{{page}}}}
    \\pagestyle{{plain}}
    \\setcounter{{page}}{{0}}
{frontmatter}
    \\tableofcontents
    \\cleardoublepage
    \\renewcommand{{\\thepage}}{{\\arabic{{page}}}}
    \\setcounter{{page}}{{1}}
    \\pagestyle{{normal}}
    % start chapters
    % end chapters
{backmatter}
    \\printbibliography
\\end{{document}}
"""

MASTER_TEMPLATE_CLASSIC_BOOK_CHAPTERS = """\\documentclass[10pt,twoside,openright]{{book}}

\\input{{preamble.tex}}
% Generated title leaves use the text-area anchors provided by this package.
% Keep this here as well as in template5 so older project preambles still work.
\\usepackage{{tikzpagenodes}}
% Defaults preserve compatibility with preambles created before the page-size
% variants were introduced. Current 6x9book and a5book preambles override them.
\\providecommand{{\\bookhalftitley}}{{1.36in}}
\\providecommand{{\\bookhalftitlewidth}}{{\\textwidth}}
\\providecommand{{\\bookserieslineone}}{{1.44in}}
\\providecommand{{\\bookserieslinetwo}}{{1.64in}}
\\providecommand{{\\booktitley}}{{0.68in}}
\\providecommand{{\\booktitlewidth}}{{\\textwidth}}
\\providecommand{{\\booktitlefontsize}}{{34.5}}
\\providecommand{{\\booktitleleading}}{{38}}
\\providecommand{{\\booktitletracking}}{{110}}
\\providecommand{{\\booktitleruley}}{{1.32in}}
\\providecommand{{\\booktitlerulehalfwidth}}{{2.03in}}
\\providecommand{{\\booktitlebyy}}{{1.78in}}
\\providecommand{{\\booktitleauthory}}{{2.04in}}
\\providecommand{{\\booktitleaffiliationy}}{{2.32in}}
\\providecommand{{\\booktitleeditiony}}{{4.29in}}
\\providecommand{{\\booktitlemarky}}{{5.64in}}
\\providecommand{{\\booktitlepublishery}}{{6.50in}}
\\providecommand{{\\booktitlelocationsy}}{{6.75in}}
\\providecommand{{\\booktitlepublisherwidth}}{{5.20in}}
\\input{{symbols.tex}}
\\title{{{title}}}
\\author{{{author}}}
\\newcommand{{\\bookpublisher}}{{{publisher}}}
\\newcommand{{\\bookaffiliation}}{{{affiliation}}}
\\newcommand{{\\bookedition}}{{{edition}}}
\\newcommand{{\\bookprinting}}{{{printing}}}
\\newcommand{{\\bookprintingdate}}{{{printing_date}}}
\\newcommand{{\\bookprefacedate}}{{{preface_date}}}
\\newcommand{{\\bookprefaceauthor}}{{{preface_author}}}
\\newcommand{{\\bookpublisherlocations}}{{{publisher_locations}}}
\\newcommand{{\\bookcopyrightyears}}{{{copyright_years}}}
\\newcommand{{\\bookcatalogcard}}{{{catalog_card}}}
\\newcommand{{\\bookpublishermark}}{{{publisher_mark}}}
\\newcommand{{\\bookprintedline}}{{{printed_line}}}
\\newcommand{{\\bookcopyrightnotice}}{{{copyright_notice}}}
\\newcommand{{\\bookcataloglabel}}{{{catalog_label}}}
\\symonrunningheads{{{running_heads}}}
\\begin{{document}}
    \\frontmatter
    \\pagestyle{{symonfront}}
    \\hypersetup{{pageanchor=false}}
    \\thispagestyle{{empty}}
    \\begin{{tikzpicture}}[remember picture,overlay]
        \\node[anchor=north,inner sep=0pt,text width=\\bookhalftitlewidth,align=center]
            at ([yshift=-\\bookhalftitley]current page text area.north)
            {{\\fontsize{{\\booktitlefontsize}}{{\\booktitleleading}}\\selectfont
              \\textls[110]{{\\MakeUppercase{{{title}}}}}}};
    \\end{{tikzpicture}}
    \\null
    \\clearpage

{seriespage}
    \\thispagestyle{{empty}}
    \\begin{{tikzpicture}}[remember picture,overlay]
            \\node[anchor=north,inner sep=0pt,text width=\\booktitlewidth,align=center]
                at ([yshift=-\\booktitley]current page text area.north)
                {{\\fontsize{{\\booktitlefontsize}}{{\\booktitleleading}}\\selectfont
                  \\textls[\\booktitletracking]{{\\MakeUppercase{{{title}}}}}}};
            \\draw[line width=0.6pt]
                ([xshift=-\\booktitlerulehalfwidth,yshift=-\\booktitleruley]current page text area.north) --
                ([xshift= \\booktitlerulehalfwidth,yshift=-\\booktitleruley]current page text area.north);
            \\node[anchor=north,inner sep=0pt]
                at ([yshift=-\\booktitlebyy]current page text area.north)
                {{\\fontsize{{9.5}}{{11}}\\selectfont\\itshape by}};
            \\node[anchor=north,inner sep=0pt]
                at ([yshift=-\\booktitleauthory]current page text area.north)
                {{\\fontsize{{10.7}}{{12.8}}\\selectfont\\normalfont\\textls[140]{{\\MakeUppercase{{{author}}}}}}};
            \\ifstrempty{{\\bookaffiliation}}{{}}{{
                \\node[anchor=north,inner sep=0pt]
                    at ([yshift=-\\booktitleaffiliationy]current page text area.north)
                    {{\\fontsize{{9.6}}{{11.5}}\\selectfont\\itshape\\bookaffiliation}};
            }}
            \\ifstrempty{{\\bookedition}}{{}}{{
                \\node[anchor=north,inner sep=0pt]
                    at ([yshift=-\\booktitleeditiony]current page text area.north)
                    {{\\fontsize{{7.5}}{{9.5}}\\selectfont\\normalfont\\MakeUppercase{{\\bookedition}}}};
            }}
            \\ifdefstring{{\\bookpublishermark}}{{none}}{{}}{{
                \\begin{{scope}}[
                    shift={{([yshift=-\\booktitlemarky]current page text area.north)}}
                ]
                    % Original press mark: a guiding star over an open folio.
                    \\fill (0,7pt) -- (2pt,2pt) -- (7pt,0) --
                          (2pt,-2pt) -- (0,-7pt) -- (-2pt,-2pt) --
                          (-7pt,0) -- (-2pt,2pt) -- cycle;
                    \\draw[line width=0.90pt,line cap=round,line join=round]
                          (-16pt,-8pt) .. controls (-10pt,-6pt) and (-5pt,-7pt) ..
                          (0,-12pt) .. controls (5pt,-7pt) and (10pt,-6pt) ..
                          (16pt,-8pt);
                \\end{{scope}}
            }}
            \\ifstrempty{{\\bookpublisher}}{{}}{{
                \\node[anchor=north,inner sep=0pt,text width=\\booktitlepublisherwidth,align=center]
                    at ([yshift=-\\booktitlepublishery]current page text area.north)
                    {{\\fontsize{{10.2}}{{12}}\\selectfont\\normalfont
                      \\textls[85]{{\\MakeUppercase{{\\bookpublisher}}}}}};
            }}
            \\ifstrempty{{\\bookpublisherlocations}}{{}}{{
                \\node[anchor=north,inner sep=0pt,text width=\\booktitlepublisherwidth,align=center]
                    at ([yshift=-\\booktitlelocationsy]current page text area.north)
                    {{\\fontsize{{7.7}}{{11.5}}\\selectfont\\normalfont
                      \\textls[45]{{\\MakeUppercase{{\\bookpublisherlocations}}}}}};
            }}
    \\end{{tikzpicture}}
    \\null
    \\clearpage
    \\hypersetup{{pageanchor=true}}
{frontmatter}
    \\tableofcontents
    \\cleardoublepage
    \\mainmatter
    \\pagestyle{{symonmain}}
    % start chapters
    % end chapters
    \\backmatter
    \\pagestyle{{symonback}}
{conclusion}
{bibliography}
{backmatter}
\\end{{document}}
"""


def is_book_template(template: str) -> bool:
    return template == "lecture-book" or template in CLASSIC_BOOK_TEMPLATES


def is_classic_book_template(template: str) -> bool:
    return template in CLASSIC_BOOK_TEMPLATES


def vendor_classic_book_fonts(path: Path) -> None:
    """Copy the project-local Symon Schoolbook bundle into a classic book."""
    if not CLASSIC_FONT_DIR.exists():
        return
    destination = path / "fonts"
    destination.mkdir(exist_ok=True)
    for source in CLASSIC_FONT_DIR.iterdir():
        if source.is_file():
            shutil.copy2(source, destination / source.name)
            if source.name == "symontoc.tfm":
                shutil.copy2(source, path / source.name)


def symbols_define_list(path: Path) -> bool:
    if not path.exists():
        return False
    try:
        sym_txt = path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return False
    return "\\newcommand{\\listofsymbols}" in sym_txt or "\\def\\listofsymbols" in sym_txt


def bibliography_has_entries(path: Path) -> bool:
    if not path.exists():
        return False
    text = path.read_text(encoding="utf-8", errors="ignore")
    return re.search(r"^\s*@\w+\s*[{(]", text, flags=re.MULTILINE) is not None


def classic_bibliography_block(path: Path) -> str:
    if not bibliography_has_entries(path / "bibliography.bib"):
        return ""
    return (
        "    \\symontitleleaf{Bibliography}\n"
        "    \\addcontentsline{toc}{chapter}{Bibliography}\n"
        "    \\printbibliography[heading=symonbibliography]"
    )


def rewrite_master_for_current_notebook(path: Path):
    info = parse_info_yaml(path)
    title = info.get("title", path.name)
    author = info.get("author", "Gabriel Nowaskie")
    series = info.get("series", "").strip()
    publisher = info.get("publisher", "").strip()
    affiliation = info.get("affiliation", "").strip()
    edition = info.get("edition", "").strip()
    printing = info.get("printing", "").strip()
    printing_date = info.get("printing_date", "").strip()
    preface_date = info.get("preface_date", "").strip()
    preface_author = info.get("preface_author", "").strip() or author
    publisher_locations = info.get("publisher_locations", "").strip().replace(
        "|", r"\enspace\textperiodcentered\enspace{}"
    )
    copyright_years = info.get("copyright_years", "").strip() or "\\the\\year"
    catalog_card = info.get("catalog_card", "").strip()
    publisher_mark = info.get("publisher_mark", "none").strip().lower()
    if publisher_mark == "triad":
        publisher_mark = "folio-star"
    if publisher_mark not in {"none", "folio-star"}:
        publisher_mark = "none"
    printed_line = info.get("printed_line", "").strip()
    copyright_notice = info.get("copyright_notice", "").strip().replace("|", "\\\\")
    catalog_label = info.get("catalog_label", "").strip()
    running_heads = info.get("running_heads", "symon").strip().lower()
    if running_heads not in {"symon", "math"}:
        running_heads = "symon"
    template = normalize_template_name(info.get("template", "lecture-color"))
    structure = notebook_structure(path)
    existing_numbers = [parse_entry_number(p.stem) for p in lecture_files(path)]

    master = path / "master.tex"
    if is_book_template(template):
        # Classic book variants follow the Symon-style order:
        # title matter, preface, contents, chapters, bibliography, answers, symbols, index.
        front_lines: list[str] = []
        back_lines: list[str] = []
        conclusion_lines: list[str] = []
        seriespage = ""

        if is_classic_book_template(template):
            if series:
                seriespage = (
                    "\n"
                    "    \\thispagestyle{empty}\n"
                    "    \\begin{tikzpicture}[remember picture,overlay]\n"
                    "        \\node[anchor=north,inner sep=0pt]\n"
                    "            at ([yshift=-\\bookserieslineone]current page text area.north)\n"
                    "            {\\fontsize{10}{12}\\selectfont This book is in the};\n"
                    "        \\node[anchor=north,inner sep=0pt,text width=\\textwidth,align=center]\n"
                    "            at ([yshift=-\\bookserieslinetwo]current page text area.north)\n"
                    f"            {{\\fontsize{{10}}{{12}}\\selectfont\\textls[75]{{\\MakeUppercase{{{series}}}}}}};\n"
                    "    \\end{tikzpicture}\n"
                    "    \\null\n"
                    "    \\clearpage\n"
                )
            elif (path / "series.tex").exists():
                seriespage = "\n    \\input{series.tex}\n"
            for part in ("copyright", "dedication", "preface", "summary"):
                if (path / f"{part}.tex").exists():
                    front_lines.append(f"    \\input{{{part}.tex}}")
            if (path / "conclusion.tex").exists():
                conclusion_lines.append("    \\input{conclusion.tex}")
            if (path / "answers.tex").exists():
                back_lines.append("    \\input{answers.tex}")
            if symbols_define_list(path / "symbols.tex"):
                back_lines.append("    \\listofsymbols")
            if (path / "index.tex").exists():
                back_lines.append("    \\input{index.tex}")
        else:
            for part in ("copyright", "preface", "summary"):
                if (path / f"{part}.tex").exists():
                    front_lines.append(f"    \\input{{{part}.tex}}")
            if symbols_define_list(path / "symbols.tex"):
                front_lines.append("    \\listofsymbols")
            if (path / "conclusion.tex").exists():
                back_lines.append("    \\input{conclusion.tex}")

        frontmatter = ("\n" + "\n".join(front_lines) + "\n") if front_lines else ""
        conclusion = ("\n" + "\n".join(conclusion_lines) + "\n") if conclusion_lines else ""
        backmatter = ("\n" + "\n".join(back_lines) + "\n") if back_lines else ""

        date = dt.datetime.now().strftime("%B %Y")
        publisherline = (
            f"            {{\\normalsize\\MakeUppercase{{{publisher}}}\\par}}\n"
            if publisher
            else ""
        )
        master_template = (
            MASTER_TEMPLATE_BOOK_CHAPTERS
            if template == "lecture-book"
            else MASTER_TEMPLATE_CLASSIC_BOOK_CHAPTERS
        )
        master.write_text(
            master_template.format(
                title=title,
                author=author,
                publisher=publisher,
                affiliation=affiliation,
                edition=edition,
                printing=printing,
                printing_date=printing_date,
                preface_date=preface_date,
                preface_author=preface_author,
                publisher_locations=publisher_locations,
                copyright_years=copyright_years,
                catalog_card=catalog_card,
                publisher_mark=publisher_mark,
                printed_line=printed_line,
                copyright_notice=copyright_notice,
                catalog_label=catalog_label,
                date=date,
                running_heads=running_heads,
                seriespage=seriespage,
                publisherline=publisherline,
                frontmatter=frontmatter,
                conclusion=conclusion,
                bibliography=classic_bibliography_block(path),
                backmatter=backmatter,
            ),
            encoding="utf-8",
        )
        # Repopulate the chapter list automatically (book notebooks always use chapters).
        if existing_numbers:
            update_master(path, existing_numbers)
    else:
        master.write_text(MASTER_TEMPLATE.format(title=title), encoding="utf-8")
        # Keep behavior consistent with "notes new-lecture": default view is last two entries.
        if existing_numbers:
            include = existing_numbers[-2:] if len(existing_numbers) >= 2 else existing_numbers
            update_master(path, include)


def cmd_fix_master(_args):
    path = current_course_path()
    info = parse_info_yaml(path)
    template = normalize_template_name(info.get("template", "lecture-color"))
    if template == "lecture-book":
        # Keep vendored class/sty in sync with templates/book.
        for fname in ("tuftebook.cls", "marginfix.sty"):
            src = BOOK_TEMPLATE_DIR / fname
            dst = path / fname
            if src.exists():
                shutil.copy2(src, dst)
    elif is_classic_book_template(template):
        vendor_classic_book_fonts(path)
    rewrite_master_for_current_notebook(path)
    print(f"Rewrote master.tex for: {path.name}")


def cmd_new_book_part(args):
    path = current_course_path()
    info = parse_info_yaml(path)
    template = normalize_template_name(info.get("template", "lecture-color"))
    if not is_book_template(template):
        raise SystemExit("new-book-part is only available for book templates")

    part = args.part.strip().lower()
    if part not in BOOK_PART_TEMPLATES:
        raise SystemExit(f"Unknown part '{part}'. Choose one of: {', '.join(BOOK_PART_TEMPLATES.keys())}")

    src = BOOK_PART_TEMPLATES[part]
    if not src.exists():
        raise SystemExit(f"Missing template file: {src}")

    dst_name = "symbols.tex" if part == "symbols" else f"{part}.tex"
    dst = path / dst_name
    if dst.exists() and not args.force:
        raise SystemExit(f"{dst_name} already exists. Re-run with --force to overwrite.")
    shutil.copy2(src, dst)
    rewrite_master_for_current_notebook(path)
    print(dst)

def parse_info_yaml(path: Path) -> dict[str, str]:
    info_path = path / "info.yaml"
    if not info_path.exists():
        return {}
    info: dict[str, str] = {}
    for line in info_path.read_text(encoding="utf-8").splitlines():
        if ":" not in line:
            continue
        key, val = line.split(":", 1)
        info[key.strip()] = val.strip().strip("'").strip('"')
    return info


def notebook_structure(path: Path) -> str:
    info = parse_info_yaml(path)
    structure = info.get("structure", "").strip().lower()
    if structure in ("chapters", "lectures"):
        return structure
    return "lectures"


def entry_prefix(structure: str) -> str:
    return "chap_" if structure == "chapters" else "lec_"


def entry_marker(structure: str) -> str:
    return "chapters" if structure == "chapters" else "lectures"


def parse_entry_number(stem: str) -> int:
    m = re.search(r"_(\d+)$", stem)
    return int(m.group(1)) if m else 0

def notebook_dir(kind: str, name: str) -> Path:
    if kind == "course":
        return COURSES_ROOT / name
    return TOPICS_ROOT / name


def ensure_notebook_exists(kind: str, name: str) -> Path:
    path = notebook_dir(kind, name)
    if not path.is_dir():
        raise SystemExit(f"{kind.capitalize()} does not exist: {name}")
    return path


def find_notebook(name: str) -> Path:
    course_path = COURSES_ROOT / name
    topic_path = TOPICS_ROOT / name
    if course_path.is_dir() and topic_path.is_dir():
        raise SystemExit(f"Ambiguous name '{name}' exists in both courses/ and topics/")
    if course_path.is_dir():
        return course_path
    if topic_path.is_dir():
        return topic_path
    raise SystemExit(f"Notebook does not exist: {name}")


def read_lecture_meta(path: Path):
    line = path.read_text(encoding="utf-8").splitlines()[0] if path.exists() else ""
    m = re.search(r"lecture\{(.*?)\}\{(.*?)\}\{(.*)\}", line)
    if not m:
        m2 = re.search(r"\\chapter\{(.*)\}", line)
        if not m2:
            return None
        return {
            "number": parse_entry_number(path.stem),
            "date": "",
            "title": m2.group(1),
            "file": path,
        }
    return {
        "number": int(m.group(1)),
        "date": m.group(2),
        "title": m.group(3),
        "file": path,
    }


def lecture_files(path: Path):
    structure = notebook_structure(path)
    files = sorted(path.glob(f"{entry_prefix(structure)}*.tex"))
    return files


def update_master(course_path: Path, numbers: list[int]):
    master = course_path / "master.tex"
    text = master.read_text(encoding="utf-8")
    structure = notebook_structure(course_path)
    marker = entry_marker(structure)
    start = text.find(f"% start {marker}")
    end = text.find(f"% end {marker}")
    if start == -1 or end == -1 or end < start:
        raise SystemExit(f"master.tex is missing '% start {marker}'/'% end {marker}' markers")

    start_line_end = text.find("\n", start)
    before = text[: start_line_end + 1]
    after = text[end:]
    prefix = entry_prefix(structure)
    body = "".join(f"    \\input{{{prefix}{n:02d}.tex}}\n" for n in numbers)
    master.write_text(before + body + after, encoding="utf-8")


def parse_range(spec: str, all_numbers: list[int]) -> list[int]:
    if not all_numbers:
        return []
    last = all_numbers[-1]
    prev = all_numbers[-2] if len(all_numbers) >= 2 else last

    lookup = {
        "all": all_numbers,
        "last": [last],
        "prev": [n for n in all_numbers if n < last],
        "prev-last": [prev, last] if prev != last else [last],
    }
    if spec in lookup:
        return lookup[spec]

    if "-" in spec:
        a, b = spec.split("-", 1)
        start = last if a == "last" else prev if a == "prev" else int(a)
        end = last if b == "last" else prev if b == "prev" else int(b)
        lo, hi = (start, end) if start <= end else (end, start)
        return [n for n in all_numbers if lo <= n <= hi]

    return [int(spec)]


def current_course_path() -> Path:
    if CURRENT_LINK.exists() and CURRENT_LINK.is_symlink():
        return CURRENT_LINK.resolve()
    raise SystemExit("No current notebook set. Use: notes set-current <name>")


def selected_preamble_template(name: str) -> Path:
    normalized = normalize_template_name(name)
    preamble = TEMPLATE_PREAMBLES.get(normalized)
    if preamble is None:
        available = ", ".join(sorted(TEMPLATE_PREAMBLES.keys()))
        raise SystemExit(f"Unknown template '{name}'. Available: {available}")
    if not preamble.exists():
        raise SystemExit(f"Template file is missing: {preamble}")
    return preamble


def normalize_template_name(name: str) -> str:
    key = name.strip().lower()
    if key in TEMPLATE_ALIASES:
        return TEMPLATE_ALIASES[key]
    if key in TEMPLATE_PREAMBLES:
        return key
    available = ", ".join(sorted(TEMPLATE_PREAMBLES.keys()))
    raise SystemExit(f"Unknown template '{name}'. Available: {available} (or 1-6)")


def write_notebook_preamble(path: Path, template_name: str):
    normalized = normalize_template_name(template_name)
    src = selected_preamble_template(normalized)
    dst = path / "preamble.tex"
    text = src.read_text(encoding="utf-8")
    if normalized == "a5book":
        text += "\n" + (PREAMBLES_DIR / "template5.tex").read_text(encoding="utf-8")

    # Compatibility: lecture-notes templates define \lesson, while this tool writes \lecture.
    compat = (
        "\n\n% Compatibility for notes_manager.py lecture files.\n"
        "\\providecommand{\\lecture}[3]{\\lesson{#1}{#2}{#3}}\n"
    )

    if "\\providecommand{\\lecture}" not in text:
        text += compat
    dst.write_text(text, encoding="utf-8")


def init_notebook(
    path: Path,
    title: str,
    short: str,
    url: str,
    template: str,
    structure: str,
    author: str = "Gabriel Nowaskie",
    series: str = "",
    publisher: str = "",
    running_heads: str = "symon",
    affiliation: str = "",
    edition: str = "",
    printing: str = "",
    printing_date: str = "",
    preface_date: str = "",
    preface_author: str = "",
    publisher_locations: str = "",
    copyright_years: str = "",
    catalog_card: str = "",
    publisher_mark: str = "none",
    printed_line: str = "",
    copyright_notice: str = "",
    catalog_label: str = "",
):
    template = normalize_template_name(template)
    structure = structure.strip().lower()
    running_heads = running_heads.strip().lower()
    if running_heads not in {"symon", "math"}:
        raise SystemExit("Invalid --running-heads (use 'symon' or 'math')")
    if structure not in ("lectures", "chapters"):
        raise SystemExit("Invalid --structure (use 'lectures' or 'chapters')")

    # Book templates force chapter structure to avoid mixed semantics.
    if is_book_template(template):
        structure = "chapters"
    if is_classic_book_template(template):
        preface_date = preface_date.strip() or dt.datetime.now().strftime("%B, %Y")
        preface_author = preface_author.strip() or author
    path.mkdir(parents=True, exist_ok=True)
    (path / "figures").mkdir(exist_ok=True)
    (path / "UltiSnips").mkdir(exist_ok=True)

    info = (
        f"title: '{title}'\n"
        f"short: '{short}'\n"
        f"url: '{url}'\n"
        f"author: '{author}'\n"
        f"series: '{series}'\n"
        f"publisher: '{publisher}'\n"
        f"affiliation: '{affiliation}'\n"
        f"edition: '{edition}'\n"
        f"printing: '{printing}'\n"
        f"printing_date: '{printing_date}'\n"
        f"preface_date: '{preface_date}'\n"
        f"preface_author: '{preface_author}'\n"
        f"publisher_locations: '{publisher_locations}'\n"
        f"copyright_years: '{copyright_years}'\n"
        f"catalog_card: '{catalog_card}'\n"
        f"publisher_mark: '{publisher_mark}'\n"
        f"printed_line: '{printed_line}'\n"
        f"copyright_notice: '{copyright_notice}'\n"
        f"catalog_label: '{catalog_label}'\n"
        f"running_heads: '{running_heads}'\n"
        f"template: '{template}'\n"
        f"structure: '{structure}'\n"
    )
    (path / "info.yaml").write_text(info, encoding="utf-8")

    master = path / "master.tex"
    if not master.exists():
        if is_book_template(template):
            date = dt.datetime.now().strftime("%B %Y")
            initial_seriespage = ""
            if is_classic_book_template(template) and series:
                initial_seriespage = (
                    "\n"
                    "    \\thispagestyle{empty}\n"
                    "    \\begin{tikzpicture}[remember picture,overlay]\n"
                    "        \\node[anchor=north,inner sep=0pt]\n"
                    "            at ([yshift=-\\bookserieslineone]current page text area.north)\n"
                    "            {\\fontsize{10}{12}\\selectfont This book is in the};\n"
                    "        \\node[anchor=north,inner sep=0pt,text width=\\textwidth,align=center]\n"
                    "            at ([yshift=-\\bookserieslinetwo]current page text area.north)\n"
                    f"            {{\\fontsize{{10}}{{12}}\\selectfont\\textls[75]{{\\MakeUppercase{{{series}}}}}}};\n"
                    "    \\end{tikzpicture}\n"
                    "    \\null\n"
                    "    \\clearpage\n"
                )
            master_template = (
                MASTER_TEMPLATE_BOOK_CHAPTERS
                if template == "lecture-book"
                else MASTER_TEMPLATE_CLASSIC_BOOK_CHAPTERS
            )
            master.write_text(
                master_template.format(
                    title=title,
                    author=author,
                    publisher=publisher,
                    affiliation=affiliation,
                    edition=edition,
                    printing=printing,
                    printing_date=printing_date,
                    preface_date=preface_date,
                    preface_author=preface_author,
                    publisher_locations=publisher_locations.replace(
                        "|", r"\enspace\textperiodcentered\enspace{}"
                    ),
                    copyright_years=copyright_years or "\\the\\year",
                    catalog_card=catalog_card,
                    publisher_mark=publisher_mark,
                    printed_line=printed_line,
                    copyright_notice=copyright_notice.replace("|", "\\\\"),
                    catalog_label=catalog_label,
                    date=date,
                    running_heads=running_heads,
                    seriespage=initial_seriespage,
                    publisherline=(
                        f"            {{\\normalsize\\MakeUppercase{{{publisher}}}\\par}}\n"
                        if publisher
                        else ""
                    ),
                    frontmatter="",
                    conclusion="",
                    bibliography=classic_bibliography_block(path),
                    backmatter="",
                ),
                encoding="utf-8",
            )
        else:
            master.write_text(MASTER_TEMPLATE.format(title=title), encoding="utf-8")

    preamble = path / "preamble.tex"
    if not preamble.exists():
        write_notebook_preamble(path, template)

    if template == "lecture-book":
        # Vendor the class/sty files so the book template compiles without requiring
        # a specific TeX Live installation.
        for fname in ("tuftebook.cls", "marginfix.sty"):
            src = BOOK_TEMPLATE_DIR / fname
            dst = path / fname
            if src.exists() and not dst.exists():
                shutil.copy2(src, dst)
        symbols = path / "symbols.tex"
        if not symbols.exists():
            symbols.write_text("% symbols.tex (optional)\n", encoding="utf-8")
        bib = path / "bibliography.bib"
        if not bib.exists():
            bib.write_text("% bibliography.bib\n", encoding="utf-8")
    elif is_classic_book_template(template):
        vendor_classic_book_fonts(path)
        symbols = path / "symbols.tex"
        if not symbols.exists():
            symbols.write_text("% symbols.tex (optional)\n", encoding="utf-8")
        bib = path / "bibliography.bib"
        if not bib.exists():
            bib.write_text("% bibliography.bib\n", encoding="utf-8")

    course_snippets = path / "UltiSnips" / "tex.snippets"
    if SNIPPETS_TEMPLATE.exists() and not course_snippets.exists():
        shutil.copy2(SNIPPETS_TEMPLATE, course_snippets)

    course_figure_template = path / "figures" / "template.svg"
    if FIGURE_TEMPLATE.exists() and not course_figure_template.exists():
        shutil.copy2(FIGURE_TEMPLATE, course_figure_template)


def cmd_init_course(args):
    path = notebook_dir("course", args.name)
    init_notebook(
        path, args.title, args.short, args.url, args.template, args.structure,
        args.author, args.series, args.publisher, args.running_heads,
        args.affiliation, args.edition, args.printing,
        args.printing_date, args.preface_date, args.preface_author,
        "|".join(args.publisher_locations), args.copyright_years, args.catalog_card,
        args.publisher_mark, args.printed_line, args.copyright_notice,
        args.catalog_label,
    )
    print(f"Initialized course at {path}")


def cmd_list_courses(_args):
    COURSES_ROOT.mkdir(exist_ok=True)
    for p in sorted(COURSES_ROOT.iterdir()):
        if p.is_dir():
            mark = "*" if CURRENT_LINK.exists() and CURRENT_LINK.resolve() == p else " "
            print(f"{mark} {p.name}")


def cmd_init_topic(args):
    path = notebook_dir("topic", args.name)
    init_notebook(
        path, args.title, args.short, args.url, args.template, args.structure,
        args.author, args.series, args.publisher, args.running_heads,
        args.affiliation, args.edition, args.printing,
        args.printing_date, args.preface_date, args.preface_author,
        "|".join(args.publisher_locations), args.copyright_years, args.catalog_card,
        args.publisher_mark, args.printed_line, args.copyright_notice,
        args.catalog_label,
    )
    print(f"Initialized topic at {path}")


def cmd_list_topics(_args):
    TOPICS_ROOT.mkdir(exist_ok=True)
    for p in sorted(TOPICS_ROOT.iterdir()):
        if p.is_dir():
            mark = "*" if CURRENT_LINK.exists() and CURRENT_LINK.resolve() == p else " "
            print(f"{mark} {p.name}")


def cmd_set_current(args):
    path = find_notebook(args.name)
    if CURRENT_LINK.exists() or CURRENT_LINK.is_symlink():
        CURRENT_LINK.unlink()
    CURRENT_LINK.symlink_to(path)
    print(f"Current notebook set to: {path.name}")


def cmd_show_current(_args):
    path = current_course_path()
    print(path.name)


def cmd_new_lecture(args):
    path = current_course_path()
    structure = notebook_structure(path)
    files = lecture_files(path)
    number = parse_entry_number(files[-1].stem) + 1 if files else 1
    fname = path / f"{entry_prefix(structure)}{number:02d}.tex"
    raw_date = dt.datetime.now().strftime(DATE_FORMAT)
    # Normalize capitalization for month/day abbreviations across locales.
    date = " ".join(part.capitalize() if part.isalpha() else part for part in raw_date.split())
    title = args.title or ""
    if structure == "chapters":
        chap_title = title if title else f"Chapter {number}"
        fname.write_text(f"\\chapter{{{chap_title}}}\n", encoding="utf-8")
    else:
        fname.write_text(f"\\lecture{{{number}}}{{{date}}}{{{title}}}\n", encoding="utf-8")

    if number == 1:
        include = [1]
    else:
        include = [number - 1, number]
    update_master(path, include)
    print(fname)


def cmd_list_lectures(_args):
    path = current_course_path()
    for f in lecture_files(path):
        meta = read_lecture_meta(f)
        if meta:
            print(f"{meta['number']:02d}  {meta['date']}  {meta['title']}  {f.name}")


def cmd_open_lecture(args):
    path = current_course_path()
    structure = notebook_structure(path)
    files = lecture_files(path)
    if not files:
        raise SystemExit("No lectures yet. Use: notes new-lecture")

    target: Path
    if args.which == "last":
        target = files[-1]
    else:
        n = int(args.which)
        target = path / f"{entry_prefix(structure)}{n:02d}.tex"
        if not target.exists():
            raise SystemExit(f"Lecture file not found: {target.name}")

    editor = os.environ.get("EDITOR", "nvim")
    subprocess.run([editor, str(target)], check=False)


def cmd_update_view(args):
    path = current_course_path()
    numbers = [parse_entry_number(p.stem) for p in lecture_files(path)]
    chosen = parse_range(args.spec, numbers)
    update_master(path, chosen)
    print(f"Updated master.tex with lectures: {chosen}")


def cmd_compile(args):
    path = current_course_path() if args.current else find_notebook(args.course)
    master = path / "master.tex"
    if not master.exists():
        raise SystemExit(f"Missing {master}")
    subprocess.run(["latexmk", "-pdf", "-f", "-interaction=nonstopmode", str(master)], cwd=path, check=False)


def cmd_print_letter(args):
    path = current_course_path() if args.current else find_notebook(args.course)
    master = path / "master.tex"
    if not master.exists():
        raise SystemExit(f"Missing {master}")

    master_build = subprocess.run(
        ["latexmk", "-pdf", "-interaction=nonstopmode", str(master)],
        cwd=path,
        check=False,
    )
    master_pdf = path / "master.pdf"
    if master_build.returncode != 0 or not master_pdf.exists():
        raise SystemExit("Book compilation failed; print proof was not generated.")

    wrapper = path / "print-letter.tex"
    wrapper.write_text(LETTER_PRINT_TEMPLATE, encoding="utf-8")
    proof_build = subprocess.run(
        ["latexmk", "-pdf", "-interaction=nonstopmode", str(wrapper)],
        cwd=path,
        check=False,
    )
    proof_pdf = path / "print-letter.pdf"
    if proof_build.returncode != 0 or not proof_pdf.exists():
        raise SystemExit("Letter-size print proof compilation failed.")

    print(proof_pdf)
    print("Print at Actual Size / 100%; cut on the 6x9 trim box or crop marks.")


def cmd_print_a5_booklet(args):
    path = current_course_path() if args.current else find_notebook(args.course)
    info = parse_info_yaml(path)
    template = normalize_template_name(info.get("template", "lecture-color"))
    if template != "a5book":
        raise SystemExit(
            "print-a5-booklet requires an a5book project (A6 finished pages)."
        )

    master = path / "master.tex"
    if not master.exists():
        raise SystemExit(f"Missing {master}")

    master_build = subprocess.run(
        ["latexmk", "-pdf", "-interaction=nonstopmode", str(master)],
        cwd=path,
        check=False,
    )
    master_pdf = path / "master.pdf"
    if master_build.returncode != 0 or not master_pdf.exists():
        raise SystemExit("Book compilation failed; A5 booklet was not generated.")

    wrapper = path / "print-a5-booklet.tex"
    wrapper.write_text(A5_BOOKLET_PRINT_TEMPLATE, encoding="utf-8")
    booklet_build = subprocess.run(
        ["latexmk", "-pdf", "-interaction=nonstopmode", str(wrapper)],
        cwd=path,
        check=False,
    )
    booklet_pdf = path / "print-a5-booklet.pdf"
    if booklet_build.returncode != 0 or not booklet_pdf.exists():
        raise SystemExit("A5 booklet imposition failed.")

    print(booklet_pdf)
    print(
        "Print at Actual Size / 100%, double-sided, flip on the short edge; "
        "then fold the A5 sheets in half."
    )


def cmd_list_figures(_args):
    path = current_course_path()
    figdir = path / "figures"
    if not figdir.exists():
        print("No figures directory in current course.")
        return
    svgs = sorted(figdir.glob("*.svg"))
    if not svgs:
        print("No figures found.")
        return
    for f in svgs:
        print(f.stem)


def cmd_open_figures(_args):
    path = current_course_path()
    figdir = path / "figures"
    if not figdir.exists():
        print("No figures directory in current course.")
        return
    if os.uname().sysname == "Darwin":
        subprocess.run(["open", str(figdir)], check=False)
    else:
        subprocess.run(["xdg-open", str(figdir)], check=False)


def cmd_pick_figure(args):
    path = current_course_path()
    figdir = path / "figures"
    if not figdir.exists():
        print("No figures directory in current course.")
        return
    svgs = sorted(figdir.glob("*.svg"))
    if not svgs:
        print("No figures found.")
        return
    names = [f.stem for f in svgs]
    selected = pick_with_ui("Figure", names)
    if not selected:
        print("No figure selected.")
        return
    svg_path = figdir / f"{selected}.svg"
    if os.uname().sysname == "Darwin":
        subprocess.run(["open", "-a", "Inkscape", str(svg_path)], check=False)
    else:
        subprocess.run(["inkscape", str(svg_path)], check=False)


def pick_with_ui(prompt: str, options: list[str]) -> str | None:
    if not options:
        return None
    optionstr = "\n".join(options)

    choose_gui = shutil.which("choose-gui")
    choose_bin = shutil.which("choose")
    picker_bin = choose_gui or choose_bin
    if not picker_bin:
        print("Picker not found. Install with: brew install choose-gui")
        return None

    cmd = [picker_bin]
    result = subprocess.run(cmd, input=optionstr, text=True, capture_output=True)
    if result.returncode != 0:
        print("No selection.")
        return None
    selected = result.stdout.strip()
    return selected if selected else None


def cmd_pick_course(_args):
    COURSES_ROOT.mkdir(exist_ok=True)
    courses = sorted([p.name for p in COURSES_ROOT.iterdir() if p.is_dir()])
    if not courses:
        print("No courses found. Create one with: notes init-course <name> --title \"...\" --short CODE")
        return
    selected = pick_with_ui("Course", courses)
    if selected:
        cmd_set_current(argparse.Namespace(name=selected))
        print(f"Picked course: {selected}")
    else:
        print("No course selected.")


def cmd_pick_topic(_args):
    TOPICS_ROOT.mkdir(exist_ok=True)
    topics = sorted([p.name for p in TOPICS_ROOT.iterdir() if p.is_dir()])
    if not topics:
        print("No topics found. Create one with: notes init-topic <name> --title \"...\" --short CODE")
        return
    selected = pick_with_ui("Topic", topics)
    if selected:
        cmd_set_current(argparse.Namespace(name=selected))
        print(f"Picked topic: {selected}")
    else:
        print("No topic selected.")


def cmd_pick_lecture(args):
    path = current_course_path()
    entries = []
    lookup = {}
    for f in lecture_files(path):
        meta = read_lecture_meta(f)
        if not meta:
            continue
        entry = f"{meta['number']:02d}  {meta['date']}  {meta['title']}"
        entries.append(entry)
        lookup[entry] = meta["number"]
        # Some pickers normalize repeated spaces in selected output.
        lookup[" ".join(entry.split())] = meta["number"]
    if not entries:
        print("No lectures found in current course. Create one with: notes new-lecture --title \"...\"")
        return

    selected = pick_with_ui("Lecture", entries)
    if not selected:
        print("No lecture selected.")
        return
    n = lookup.get(selected) or lookup.get(" ".join(selected.split()))
    if n is None:
        m = re.match(r"^\s*(\d+)\b", selected)
        if m:
            n = int(m.group(1))
    if n is None:
        print(f"Could not resolve selected lecture: {selected}")
        return
    cmd_open_lecture(argparse.Namespace(which=str(n)))
    if args.include:
        cmd_update_view(argparse.Namespace(spec=str(n)))


def cmd_pick_view(_args):
    options = [
        ("Current lecture", "last"),
        ("Last two lectures", "prev-last"),
        ("All lectures", "all"),
        ("Previous lectures", "prev"),
    ]
    labels = [o[0] for o in options]
    selected = pick_with_ui("View", labels)
    if not selected:
        print("No view selected.")
        return
    mapping = {label: spec for label, spec in options}
    cmd_update_view(argparse.Namespace(spec=mapping[selected]))


def cmd_list_templates(_args):
    print("1  lecture-color")
    print("2  lecture-light")
    print("3  lecture-dynamic")
    print("4  lecture-book")
    print("5  6x9book")
    print("6  a5book (A6 pages folded from A5 sheets)")


def build_parser():
    p = argparse.ArgumentParser(prog="notes", description="Unified notes manager")
    sub = p.add_subparsers(dest="cmd", required=True)

    a = sub.add_parser("init-course", help="Create a new course folder")
    a.add_argument("name")
    a.add_argument("--title", required=True)
    a.add_argument("--short", required=True)
    a.add_argument("--url", default="https://")
    a.add_argument("--author", default="Gabriel Nowaskie")
    a.add_argument("--series", default="", help="Optional classic book series name")
    a.add_argument("--publisher", default="", help="Optional classic book publisher/imprint line")
    a.add_argument("--affiliation", default="", help="Optional institution shown below the author")
    a.add_argument("--edition", default="", help="Optional edition line, for example 'Second Edition'")
    a.add_argument("--printing", default="", help="Optional printing line, for example 'Third Printing'")
    a.add_argument("--printing-date", default="", help="Optional date shown after the printing line")
    a.add_argument("--preface-date", default="", help="Preface closing date; defaults to the current month and year")
    a.add_argument("--preface-author", default="", help="Preface closing name or initials; defaults to the author")
    a.add_argument("--publisher-location", dest="publisher_locations", action="append", default=[], help="Publisher location; repeat to separate locations with centered dots")
    a.add_argument("--copyright-years", default="", help="Copyright year or years; defaults to the current year")
    a.add_argument("--catalog-card", default="", help="Optional Library of Congress catalog card number")
    a.add_argument("--publisher-mark", choices=["none", "folio-star"], default="none", help="Optional original star-and-folio publisher mark")
    a.add_argument("--printed-line", default="", help="Optional copyright-page printing/location line")
    a.add_argument("--copyright-notice", default="", help="Optional rights notice; use | for explicit line breaks")
    a.add_argument("--catalog-label", default="", help="Optional label preceding the catalog number")
    a.add_argument("--running-heads", choices=["symon", "math"], default="symon", help="Classic book running heads: Symon chapter/section or Apostol theorem tracking")
    a.add_argument("--structure", default="lectures", choices=["lectures", "chapters"], help="Ignored for book templates (always chapters)")
    a.add_argument(
        "--template",
        default="lecture-color",
        help="Notebook template style (lecture-color|lecture-light|lecture-dynamic|lecture-book|6x9book|a5book or 1-6)",
    )
    a.set_defaults(func=cmd_init_course)

    a = sub.add_parser("list-courses", help="List courses")
    a.set_defaults(func=cmd_list_courses)

    a = sub.add_parser("init-topic", help="Create a new topic folder")
    a.add_argument("name")
    a.add_argument("--title", required=True)
    a.add_argument("--short", required=True)
    a.add_argument("--url", default="https://")
    a.add_argument("--author", default="Gabriel Nowaskie")
    a.add_argument("--series", default="", help="Optional classic book series name")
    a.add_argument("--publisher", default="", help="Optional classic book publisher/imprint line")
    a.add_argument("--affiliation", default="", help="Optional institution shown below the author")
    a.add_argument("--edition", default="", help="Optional edition line, for example 'Second Edition'")
    a.add_argument("--printing", default="", help="Optional printing line, for example 'Third Printing'")
    a.add_argument("--printing-date", default="", help="Optional date shown after the printing line")
    a.add_argument("--preface-date", default="", help="Preface closing date; defaults to the current month and year")
    a.add_argument("--preface-author", default="", help="Preface closing name or initials; defaults to the author")
    a.add_argument("--publisher-location", dest="publisher_locations", action="append", default=[], help="Publisher location; repeat to separate locations with centered dots")
    a.add_argument("--copyright-years", default="", help="Copyright year or years; defaults to the current year")
    a.add_argument("--catalog-card", default="", help="Optional Library of Congress catalog card number")
    a.add_argument("--publisher-mark", choices=["none", "folio-star"], default="none", help="Optional original star-and-folio publisher mark")
    a.add_argument("--printed-line", default="", help="Optional copyright-page printing/location line")
    a.add_argument("--copyright-notice", default="", help="Optional rights notice; use | for explicit line breaks")
    a.add_argument("--catalog-label", default="", help="Optional label preceding the catalog number")
    a.add_argument("--running-heads", choices=["symon", "math"], default="symon", help="Classic book running heads: Symon chapter/section or Apostol theorem tracking")
    a.add_argument("--structure", default="lectures", choices=["lectures", "chapters"], help="Ignored for book templates (always chapters)")
    a.add_argument(
        "--template",
        default="lecture-color",
        help="Notebook template style (lecture-color|lecture-light|lecture-dynamic|lecture-book|6x9book|a5book or 1-6)",
    )
    a.set_defaults(func=cmd_init_topic)

    a = sub.add_parser("list-topics", help="List topics")
    a.set_defaults(func=cmd_list_topics)

    a = sub.add_parser("set-current", help="Set active notebook (course or topic)")
    a.add_argument("name")
    a.set_defaults(func=cmd_set_current)

    a = sub.add_parser("show-current", help="Show active notebook")
    a.set_defaults(func=cmd_show_current)

    a = sub.add_parser("fix-master", help="Regenerate master.tex for the current notebook template")
    a.set_defaults(func=cmd_fix_master)

    book_parts = "|".join(BOOK_PART_TEMPLATES.keys())
    a = sub.add_parser("new-book-part", help=f"Create book front/back-matter files ({book_parts})")
    a.add_argument("part", help=book_parts)
    a.add_argument("--force", action="store_true", help="Overwrite if the file already exists")
    a.set_defaults(func=cmd_new_book_part)

    a = sub.add_parser("new-lecture", help="Create next lecture")
    a.add_argument("--title", default="")
    a.set_defaults(func=cmd_new_lecture)

    a = sub.add_parser("list-lectures", help="List lectures in active course")
    a.set_defaults(func=cmd_list_lectures)

    a = sub.add_parser("open-lecture", help="Open lecture in $EDITOR")
    a.add_argument("which", help="last or lecture number")
    a.set_defaults(func=cmd_open_lecture)

    a = sub.add_parser("update-view", help="Update included lectures in master.tex")
    a.add_argument("spec", help="all|last|prev|prev-last|N|A-B")
    a.set_defaults(func=cmd_update_view)

    a = sub.add_parser("compile", help="Compile course master.tex")
    g = a.add_mutually_exclusive_group(required=True)
    g.add_argument("--current", action="store_true")
    g.add_argument("--course")
    a.set_defaults(func=cmd_compile)

    a = sub.add_parser("print-letter", help="Create a Letter-size 6x9 cutting proof")
    g = a.add_mutually_exclusive_group(required=True)
    g.add_argument("--current", action="store_true")
    g.add_argument("--course")
    a.set_defaults(func=cmd_print_letter)

    a = sub.add_parser(
        "print-a5-booklet",
        help="Impose an a5book project two-up as a folded A5 booklet",
    )
    g = a.add_mutually_exclusive_group(required=True)
    g.add_argument("--current", action="store_true")
    g.add_argument("--course")
    a.set_defaults(func=cmd_print_a5_booklet)

    a = sub.add_parser("list-figures", help="List figure names in current course")
    a.set_defaults(func=cmd_list_figures)

    a = sub.add_parser("open-figures", help="Open current course figures folder")
    a.set_defaults(func=cmd_open_figures)

    a = sub.add_parser("pick-figure", help="Pick a figure in current course and open it in Inkscape")
    a.set_defaults(func=cmd_pick_figure)

    a = sub.add_parser("pick-course", help="Pick and set current course (choose-gui/choose)")
    a.set_defaults(func=cmd_pick_course)

    a = sub.add_parser("pick-topic", help="Pick and set current topic (choose-gui/choose)")
    a.set_defaults(func=cmd_pick_topic)

    a = sub.add_parser("pick-lecture", help="Pick and open lecture in current course")
    a.add_argument("--include", action="store_true", help="Also set master.tex view to selected lecture")
    a.set_defaults(func=cmd_pick_lecture)

    a = sub.add_parser("pick-view", help="Pick lecture include view (last/all/etc)")
    a.set_defaults(func=cmd_pick_view)

    a = sub.add_parser("list-templates", help="List available notebook templates")
    a.set_defaults(func=cmd_list_templates)

    return p


def main():
    COURSES_ROOT.mkdir(exist_ok=True)
    TOPICS_ROOT.mkdir(exist_ok=True)
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
