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

MASTER_TEMPLATE = """\\documentclass[a4paper]{{article}}
\\input{{../../templates/preamble.tex}}
\\title{{{title}}}
\\begin{{document}}
    \\maketitle
    \\tableofcontents
    % start lectures
    % end lectures
\\end{{document}}
"""


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
        return None
    return {
        "number": int(m.group(1)),
        "date": m.group(2),
        "title": m.group(3),
        "file": path,
    }


def lecture_files(path: Path):
    files = sorted(path.glob("lec_*.tex"))
    return files


def update_master(course_path: Path, numbers: list[int]):
    master = course_path / "master.tex"
    text = master.read_text(encoding="utf-8")
    start = text.find("% start lectures")
    end = text.find("% end lectures")
    if start == -1 or end == -1 or end < start:
        raise SystemExit("master.tex is missing '% start lectures'/'% end lectures' markers")

    start_line_end = text.find("\n", start)
    before = text[: start_line_end + 1]
    after = text[end:]
    body = "".join(f"    \\input{{lec_{n:02d}.tex}}\n" for n in numbers)
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
    raise SystemExit("No current course set. Use: notes set-current <course-name>")


def init_notebook(path: Path, title: str, short: str, url: str):
    path.mkdir(parents=True, exist_ok=True)
    (path / "figures").mkdir(exist_ok=True)
    (path / "UltiSnips").mkdir(exist_ok=True)

    info = (
        f"title: '{title}'\n"
        f"short: '{short}'\n"
        f"url: '{url}'\n"
    )
    (path / "info.yaml").write_text(info, encoding="utf-8")

    master = path / "master.tex"
    if not master.exists():
        master.write_text(MASTER_TEMPLATE.format(title=title), encoding="utf-8")

    course_snippets = path / "UltiSnips" / "tex.snippets"
    if SNIPPETS_TEMPLATE.exists() and not course_snippets.exists():
        shutil.copy2(SNIPPETS_TEMPLATE, course_snippets)

    course_figure_template = path / "figures" / "template.svg"
    if FIGURE_TEMPLATE.exists() and not course_figure_template.exists():
        shutil.copy2(FIGURE_TEMPLATE, course_figure_template)


def cmd_init_course(args):
    path = notebook_dir("course", args.name)
    init_notebook(path, args.title, args.short, args.url)
    print(f"Initialized course at {path}")


def cmd_list_courses(_args):
    COURSES_ROOT.mkdir(exist_ok=True)
    for p in sorted(COURSES_ROOT.iterdir()):
        if p.is_dir():
            mark = "*" if CURRENT_LINK.exists() and CURRENT_LINK.resolve() == p else " "
            print(f"{mark} {p.name}")


def cmd_init_topic(args):
    path = notebook_dir("topic", args.name)
    init_notebook(path, args.title, args.short, args.url)
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
    files = lecture_files(path)
    number = int(files[-1].stem.split("_")[1]) + 1 if files else 1
    fname = path / f"lec_{number:02d}.tex"
    date = dt.datetime.now().strftime(DATE_FORMAT)
    title = args.title or ""
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
    files = lecture_files(path)
    if not files:
        raise SystemExit("No lectures yet. Use: notes new-lecture")

    target: Path
    if args.which == "last":
        target = files[-1]
    else:
        n = int(args.which)
        target = path / f"lec_{n:02d}.tex"
        if not target.exists():
            raise SystemExit(f"Lecture file not found: {target.name}")

    editor = os.environ.get("EDITOR", "nvim")
    subprocess.run([editor, str(target)], check=False)


def cmd_update_view(args):
    path = current_course_path()
    numbers = [int(p.stem.split("_")[1]) for p in lecture_files(path)]
    chosen = parse_range(args.spec, numbers)
    update_master(path, chosen)
    print(f"Updated master.tex with lectures: {chosen}")


def cmd_compile(args):
    path = current_course_path() if args.current else find_notebook(args.course)
    master = path / "master.tex"
    if not master.exists():
        raise SystemExit(f"Missing {master}")
    subprocess.run(["latexmk", "-f", "-interaction=nonstopmode", str(master)], cwd=path, check=False)


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
    if not entries:
        print("No lectures found in current course. Create one with: notes new-lecture --title \"...\"")
        return

    selected = pick_with_ui("Lecture", entries)
    if not selected:
        print("No lecture selected.")
        return
    n = lookup.get(selected)
    if n is None:
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


def build_parser():
    p = argparse.ArgumentParser(prog="notes", description="Unified notes manager")
    sub = p.add_subparsers(dest="cmd", required=True)

    a = sub.add_parser("init-course", help="Create a new course folder")
    a.add_argument("name")
    a.add_argument("--title", required=True)
    a.add_argument("--short", required=True)
    a.add_argument("--url", default="https://")
    a.set_defaults(func=cmd_init_course)

    a = sub.add_parser("list-courses", help="List courses")
    a.set_defaults(func=cmd_list_courses)

    a = sub.add_parser("init-topic", help="Create a new topic folder")
    a.add_argument("name")
    a.add_argument("--title", required=True)
    a.add_argument("--short", required=True)
    a.add_argument("--url", default="https://")
    a.set_defaults(func=cmd_init_topic)

    a = sub.add_parser("list-topics", help="List topics")
    a.set_defaults(func=cmd_list_topics)

    a = sub.add_parser("set-current", help="Set active course")
    a.add_argument("name")
    a.set_defaults(func=cmd_set_current)

    a = sub.add_parser("show-current", help="Show active course")
    a.set_defaults(func=cmd_show_current)

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

    return p


def main():
    COURSES_ROOT.mkdir(exist_ok=True)
    TOPICS_ROOT.mkdir(exist_ok=True)
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
