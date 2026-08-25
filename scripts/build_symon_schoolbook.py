#!/usr/bin/env fontforge
"""Build the renamed Symon Schoolbook family from TeX Gyre Schola.

Run with:
    fontforge -script scripts/build_symon_schoolbook.py
"""

from pathlib import Path
import shutil
import subprocess

import fontforge
import psMat


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "templates" / "fonts" / "symon-schoolbook"

FACES = (
    ("qcsr.pfb", "Regular", "Regular", -12),
    ("qcsri.pfb", "Italic", "Italic", -12),
    ("qcsb.pfb", "Bold", "Bold", -18),
    ("qcsbi.pfb", "BoldItalic", "Bold Italic", -18),
    ("qcsr.pfb", "TOC", "TOC Light", -18),
)


def kpsewhich(filename: str) -> Path:
    result = subprocess.run(
        ["kpsewhich", filename],
        check=True,
        capture_output=True,
        text=True,
    )
    path = Path(result.stdout.strip())
    if not path.exists():
        raise FileNotFoundError(filename)
    return path


def build_face(source_name: str, suffix: str, weight: str, delta: int) -> None:
    source = kpsewhich(source_name)
    font = fontforge.open(str(source))
    original_widths = {glyph.glyphname: glyph.width for glyph in font.glyphs()}

    font.selection.all()
    font.changeWeight(delta, "LCG", 0, 0, "retain")

    # ChangeWeight adjusts advances with outlines. Restore Schola's proven TeX
    # metrics and recenter each lighter outline inside its original advance.
    for glyph in font.glyphs():
        original_width = original_widths.get(glyph.glyphname)
        if original_width is None:
            continue
        shift = (original_width - glyph.width) / 2
        if shift:
            glyph.transform(psMat.translate(shift, 0))
        glyph.width = original_width

    postscript_name = f"SymonSchoolbook-{suffix}"
    font.fontname = postscript_name
    font.familyname = "Symon Schoolbook"
    font.fullname = f"Symon Schoolbook {weight}"
    font.weight = weight
    font.version = "1.000"
    font.copyright = (
        "Derived from TeX Gyre Schola under the GUST Font License. "
        "Renamed and optically lightened for the Symon classic-book template."
    )

    stem = f"symon-schoolbook-{suffix.lower()}"
    font.generate(str(OUTPUT_DIR / f"{stem}.pfb"))
    font.generate(str(OUTPUT_DIR / f"{stem}.otf"))
    font.close()


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    for face in FACES:
        build_face(*face)
    shutil.copy2(kpsewhich("ec-qcsr.tfm"), OUTPUT_DIR / "symontoc.tfm")


if __name__ == "__main__":
    main()
