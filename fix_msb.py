#!/usr/bin/env python3
"""MSB post-build fix-ups.

Stand-alone helper to apply MSB-specific corrections to a freshly-built
``majoritybible/`` tree. Run manually after ``make all`` (or after
``make majoritybible``); the apostrophe normalisation is intentionally
not wired into the Makefile, because it addresses an MSB upstream
source issue that doesn't affect BSB.

``write_vrs()`` alone (no text mutation) *is* wired into the Makefile
via ``--vrs-only``, so ``majoritybible/msb.vrs`` is regenerated on
every build and copied into ``majoritybible/sfm_for_paratext/``.

Fix-ups applied (in order):

  1. normalise_apostrophes()
     Replace ASCII apostrophe U+0027 with curly closing apostrophe
     U+2019 inside every MSB text file. The MSB source TSV has a small
     number of stray ASCII apostrophes (3 known cases at the time of
     writing) that trip Paratext's Quotations check; this normaliser
     is a blanket pass that is a no-op everywhere else.

  2. write_vrs()
     Scan the produced USFM and emit ``majoritybible/msb.vrs`` — a
     Paratext versification file that reflects Majority Text
     versification (differs from Critical Text in a handful of places).
     Load in Paratext via Project > Project Properties > Versification.
"""

import re
import sys
from pathlib import Path

MSB_ROOT = Path("majoritybible")
SKIP_DIRS = {"workspace", "temp"}
TEXT_SUFFIXES = {".usfm", ".usj", ".usx", ".sfm"}

# Canonical book order per Paratext / UBS
BOOK_ORDER = [
    "GEN", "EXO", "LEV", "NUM", "DEU", "JOS", "JDG", "RUT",
    "1SA", "2SA", "1KI", "2KI", "1CH", "2CH", "EZR", "NEH",
    "EST", "JOB", "PSA", "PRO", "ECC", "SNG", "ISA", "JER",
    "LAM", "EZK", "DAN", "HOS", "JOL", "AMO", "OBA", "JON",
    "MIC", "NAM", "HAB", "ZEP", "HAG", "ZEC", "MAL",
    "MAT", "MRK", "LUK", "JHN", "ACT", "ROM",
    "1CO", "2CO", "GAL", "EPH", "PHP", "COL",
    "1TH", "2TH", "1TI", "2TI", "TIT", "PHM",
    "HEB", "JAS", "1PE", "2PE", "1JN", "2JN", "3JN", "JUD", "REV",
]


def iter_text_files(root: Path):
    for path in root.rglob("*"):
        if not path.is_file() or path.suffix not in TEXT_SUFFIXES:
            continue
        if path.relative_to(root).parts[0] in SKIP_DIRS:
            continue
        yield path


def normalise_apostrophes(root: Path) -> int:
    """Replace ASCII U+0027 with curly U+2019 across every text file.

    Returns the total number of substitutions made.
    """
    changes = 0
    files_changed = 0
    for path in iter_text_files(root):
        content = path.read_text(encoding="utf-8")
        if "'" not in content:
            continue
        n = content.count("'")
        path.write_text(content.replace("'", "’"), encoding="utf-8")
        changes += n
        files_changed += 1
    print(f"  apostrophes: {changes} substitution(s) in {files_changed} file(s)")
    return changes


def _chapter_verse_counts(path: Path) -> dict[int, int]:
    counts: dict[int, int] = {}
    current = None
    for line in path.read_text(encoding="utf-8").splitlines():
        m = re.match(r"^\\c\s+(\d+)", line)
        if m:
            current = int(m.group(1))
            counts.setdefault(current, 0)
            continue
        if current is None:
            continue
        for vm in re.finditer(r"\\v\s+(\d+)", line):
            v = int(vm.group(1))
            if v > counts[current]:
                counts[current] = v
    return counts


def write_vrs(root: Path) -> Path:
    """Generate majoritybible/msb.vrs from the built USFM tree."""
    usfm_dir = root / "results"
    if not usfm_dir.is_dir():
        raise FileNotFoundError(
            f"{usfm_dir}/ not found — run 'make majoritybible' first"
        )

    lines: list[str] = [
        "# Paratext versification for the Majority Standard Bible (MSB).",
        "# Auto-generated from majoritybible/results/*.usfm by fix_msb.py.",
        "#",
        "# Reflects Majority Text versification, which differs from the Critical",
        "# Text in a handful of places. Most notable differences:",
        "#   - The Pauline doxology is at Rom 14:24-26 (not Rom 16:25-27)",
        "#   - Empty verses for MT omissions: Luk 17:36, Act 8:37, Act 15:34, Act 24:7",
        "#   - 3JN ends at v.14 (no v.15); Rev 12 ends at v.17 (no v.18)",
        "#",
        "# Load in Paratext via:  Project > Project Properties > Versification",
        "",
    ]

    for code in BOOK_ORDER:
        path = usfm_dir / f"{code}.usfm"
        if not path.exists():
            continue
        counts = _chapter_verse_counts(path)
        if not counts:
            continue
        parts = [f"{c}:{counts[c]}" for c in sorted(counts)]
        lines.append(f"{code} " + " ".join(parts))

    lines += [
        "",
        "# Verse range mapping vs the 'Original' (CT) versification.",
        "# The Pauline doxology appears here in Rom 14, not Rom 16.",
        "ROM 14:24 = ROM 16:25",
        "ROM 14:25 = ROM 16:26",
        "ROM 14:26 = ROM 16:27",
        "",
    ]

    out = root / "msb.vrs"
    out.write_text("\n".join(lines), encoding="utf-8")
    print(f"  versification: wrote {out}")
    return out


def main() -> int:
    vrs_only = "--vrs-only" in sys.argv[1:]

    if not MSB_ROOT.is_dir():
        print(f"error: {MSB_ROOT}/ not found", file=sys.stderr)
        return 1
    print(f"Applying MSB fix-ups under {MSB_ROOT}/ ...")
    if not vrs_only:
        normalise_apostrophes(MSB_ROOT)
    write_vrs(MSB_ROOT)
    print("Done.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
