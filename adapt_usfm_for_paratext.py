#!/usr/bin/env python3
"""
Fix USFM validation errors for Paratext compatibility.

This script addresses USFM validation issues specific to Paratext's
current (USFM-3.0-era) basic checks:
1. Converts custom \\ref markers to \\xt (cross-reference text)
2. Pads Strong's numbers to 5 digits (H776 -> H00776, G123 -> G00123)
3. Splits \\wj markers (words of Jesus) at verse boundaries
4. Adds the USFM 3 "+" nesting prefix to \\w markers nested inside \\wj
5. Removes empty \\fqa before \\fv (in USFM 3.1, \\fv is a character
   style valid inside or outside \\fqa; this is a 3.0-only requirement)

These are all workarounds for Paratext not yet fully supporting USFM
3.1 and are expected to become unnecessary once Paratext 9.6 ships.

General-purpose cleanups that aren't version-dependent (non-biblical
\\xt refs, empty \\ft, \\mt2/\\mt1 collapse, empty para markers, \\mr ->
\\d, invalid \\r lines) now happen upstream in bsb2usfm.py itself (via
usx_cleanup.py, applied to the USX tree before serialization) so every
output variant and format — USX, USJ, and USFM alike — gets them, not
just the Paratext .sfm deliverable. \\pmo is emitted as \\lf directly in
bsb2usfm.py, since there was no remaining legitimate use of \\pmo.

See PARATEXT_ADAPTATIONS.md for detailed documentation.
"""

import re
import shutil
import sys
from pathlib import Path

from typing import cast

from usfmtc.reference import bookcodes as _bookcodes

# usfmtc infers this as dict[LiteralString, str] since it's built from a
# literal string constant; cast to plain str keys since we look up
# runtime-derived book codes (e.g. from filenames), not string literals.
bookcodes = cast("dict[str, str]", _bookcodes)


def fix_strongs_numbers(usfm_string: str) -> tuple[str, int]:
    """
    Fix Strong's numbers by padding to 5 digits.

    Convert: strong="H776" -> strong="H00776"
    Convert: strong="G123" -> strong="G00123"

    Returns tuple of (modified string, count of fixes).
    """

    def pad_strong(match: re.Match) -> str:
        prefix = match.group(1)  # H or G
        number = match.group(2)  # The digits
        padded = number.zfill(5)  # Pad to 5 digits
        return f'strong="{prefix}{padded}"'

    # Pattern to match strong="H###" or strong="G###" with any number of digits
    strongs_pattern = re.compile(r'strong="([HG])(\d+)"')

    # Count only those that need fixing (less than 5 digits)
    count = sum(1 for m in strongs_pattern.finditer(usfm_string) if len(m.group(2)) < 5)

    result = strongs_pattern.sub(pad_strong, usfm_string)

    return result, count


def _ref_to_xt(text: str) -> tuple[str, int]:
    """Convert \\ref markers to \\xt markers, preserving cross-reference semantics.

    Convert: \\ref Display Text|BOOK C:V\\ref* -> \\xt Display Text\\xt*
    Convert: \\ref Display Text\\ref* -> \\xt Display Text\\xt*

    Returns tuple of (modified string, count of conversions).

    Note: non-biblical references (Jasher, Enoch) are already converted
    to plain text upstream in bsb2usfm.py (usx_cleanup.fix_nonbiblical_xt)
    before this script runs.
    """
    count = 0

    # Pattern 1: \ref Display Text|BOOK C:V\ref* (with pipe and reference)
    ref_with_pipe = re.compile(r"\\ref ([^|]+)\|[^\\]+\\ref\*")
    count += len(ref_with_pipe.findall(text))
    text = ref_with_pipe.sub(r"\\xt \1\\xt*", text)

    # Pattern 2: \ref Display Text\ref* (without pipe)
    ref_simple = re.compile(r"\\ref (.+?)\\ref\*")
    count += len(ref_simple.findall(text))
    text = ref_simple.sub(r"\\xt \1\\xt*", text)

    # Handle \ref without closing \ref*
    ref_unclosed = re.compile(r"\\ref ([^\\)\n;]+)")
    count += len(ref_unclosed.findall(text))
    text = ref_unclosed.sub(r"\\xt \1\\xt*", text)

    # Clean up any orphaned \ref* markers
    orphan_count = len(re.findall(r"\\ref\*", text))
    if orphan_count:
        count += orphan_count
        text = re.sub(r"\\ref\*", "", text)

    return text, count


def _ref_to_plain(text: str) -> tuple[str, int]:
    """Convert \\ref markers to plain text (display text only).

    Returns tuple of (modified string, count of conversions).
    """
    count = 0

    ref_with_pipe = re.compile(r"\\ref ([^|]+)\|[^\\]+\\ref\*")
    count += len(ref_with_pipe.findall(text))
    text = ref_with_pipe.sub(r"\1", text)

    ref_simple = re.compile(r"\\ref (.+?)\\ref\*")
    count += len(ref_simple.findall(text))
    text = ref_simple.sub(r"\1", text)

    orphan_count = len(re.findall(r"\\ref\*", text))
    if orphan_count:
        count += orphan_count
        text = re.sub(r"\\ref\*", "", text)

    ref_unclosed = re.compile(r"\\ref ([^\\)\n;]+)")
    count += len(ref_unclosed.findall(text))
    text = ref_unclosed.sub(r"\1", text)

    return text, count


def fix_ref_markers(usfm_string: str) -> tuple[str, int]:
    """
    Fix \\ref markers: convert to \\xt inside footnotes, plain text elsewhere.

    Inside footnotes (\\f ... \\f*), \\ref is converted to \\xt (cross-reference
    text), preserving the semantic information that this is a scripture reference.
    Outside footnotes (e.g., in \\r lines), \\ref is converted to plain text
    since those lines are removed separately.

    Examples:
        In footnote: \\ref John 1:1-5|JHN 1:1-5\\ref* -> \\xt John 1:1-5\\xt*
        Elsewhere:   \\ref John 1:1-5|JHN 1:1-5\\ref* -> John 1:1-5

    Returns tuple of (modified string, count of fixes).
    """
    count = 0

    # Process footnotes first: convert \ref to \xt inside \f...\f*
    def convert_footnote_refs(match: re.Match) -> str:
        nonlocal count
        footnote_text = match.group(0)
        if "\\ref " not in footnote_text:
            return footnote_text
        result, c = _ref_to_xt(footnote_text)
        count += c
        return result

    footnote_pattern = re.compile(r"\\f \+.*?\\f\*")
    result = footnote_pattern.sub(convert_footnote_refs, usfm_string)

    # Convert remaining \ref outside footnotes to plain text
    remaining, c = _ref_to_plain(result)
    count += c

    # Clean up spacing artifacts from \ref removal (e.g., "( Matthew" -> "(Matthew")
    remaining = re.sub(r"\(\s+", "(", remaining)

    return remaining, count


def split_wj_markers(usfm_string: str) -> tuple[str, int]:
    """
    Split \\wj markers (words of Jesus) at verse boundaries so each verse
    has its own properly-contained \\wj ...\\wj* span.

    The original USFM has \\wj spans that may wrap multiple verses:
        \\wj text \\v 5 more text \\v 6 final text\\wj*
    This causes validation errors in Paratext. We split into:
        \\wj text\\wj* \\v 5 \\wj more text\\wj* \\v 6 \\wj final text\\wj*

    Returns tuple of (modified string, count of splits performed).
    """
    split_count = 0

    def split_span(match: re.Match) -> str:
        nonlocal split_count
        content = match.group(1)

        # If no verse markers inside, the span is already valid
        if "\\v " not in content:
            return match.group(0)

        # Split content at \v markers, keeping the \v markers
        parts = re.split(r"(\\v \d+)", content)

        result_parts = []
        in_text = False
        is_first_text = True
        for part in parts:
            if re.match(r"\\v \d+$", part):
                # This is a verse marker — close wj before it, reopen after
                if in_text:
                    result_parts.append("\\wj*")
                    split_count += 1
                result_parts.append(part)
                in_text = False
            else:
                # This is text content
                has_content = part.strip()
                if has_content:
                    if not in_text:
                        if is_first_text and not result_parts:
                            # First text segment with no preceding verse: preserve original \wj opening
                            result_parts.append("\\wj ")
                            result_parts.append(part.lstrip(" "))
                        else:
                            # After a verse marker: add space then open \wj
                            result_parts.append(" \\wj ")
                            result_parts.append(part.lstrip(" "))
                    else:
                        result_parts.append(part)
                    in_text = True
                    is_first_text = False
                else:
                    # Preserve whitespace/newlines between markers
                    result_parts.append(part)

        if in_text:
            result_parts.append("\\wj*")

        return "".join(result_parts)

    wj_pattern = re.compile(r"\\wj (.*?)\\wj\*", re.DOTALL)
    result = wj_pattern.sub(split_span, usfm_string)

    return result, split_count


def fix_wj_nested_w_markers(usfm_string: str) -> tuple[str, int]:
    """
    Add the USFM 3 "+" nesting prefix to \\w markers that fall inside an
    open \\wj (words of Jesus) span: \\w text|strong="G00863"\\w* becomes
    \\+w text|strong="G00863"\\+w*.

    Per the USFM 3 character-marker-nesting rule, a character-level marker
    nested inside another already-open character-level marker must use a
    "+" prefix on both its opening and closing forms. bsb2usfm.py's
    Strong's-number \\w wrapping always emits the plain form regardless of
    \\wj nesting, which is ambiguous wherever a \\wj span closes and reopens
    close together (e.g. quote/attribution mid-verse, or a \\wj split across
    a verse boundary) — Paratext's Basic Checks occasionally can't resolve
    the ambiguity and reports the \\wj* as unmatched.

    Must run after split_wj_markers(), which guarantees no \\wj span
    crosses a verse boundary, so each \\wj ... \\wj* span here is
    self-contained.

    Returns tuple of (modified string, count of \\w markers converted).
    """
    count = 0
    w_pattern = re.compile(r"\\w (.*?)\\w\*", re.DOTALL)

    def fix_w(match: re.Match) -> str:
        nonlocal count
        count += 1
        return f"\\+w {match.group(1)}\\+w*"

    def fix_wj_span(match: re.Match) -> str:
        content = w_pattern.sub(fix_w, match.group(1))
        return f"\\wj {content}\\wj*"

    wj_pattern = re.compile(r"\\wj (.*?)\\wj\*", re.DOTALL)
    result = wj_pattern.sub(fix_wj_span, usfm_string)

    return result, count


def fix_empty_fqa(usfm_string: str) -> tuple[str, int]:
    """
    Remove empty \\fqa before \\fv.

    Some footnotes have \\fqa immediately followed by \\fv with no text:
        \\fqa \\fv 21\\fv*But this kind...
    The empty \\fqa should be removed.

    Returns tuple of (modified string, count of fixes).
    """
    pattern = re.compile(r"\\fqa\s*(?=\\fv)")
    count = len(pattern.findall(usfm_string))
    result = pattern.sub("", usfm_string)
    return result, count


def to_paratext_filename(usfm_filename: str, identifier: str = "BSB") -> str | None:
    """
    Convert a USFM filename to Paratext naming convention with .sfm extension.

    Convert: GEN.usfm -> 01GENBSB.sfm
    Convert: 01GENBSB_strongs.usfm -> 01GENBSB_strongs.sfm

    For plain files (e.g., GEN.usfm), the book code is extracted from the
    stem and mapped to its Paratext sort number using usfmtc.reference.bookcodes.

    Returns None if the book code cannot be mapped.
    """
    stem = Path(usfm_filename).stem
    # If it already has a numeric prefix (e.g., 01GENBSB_strongs), just change extension
    if stem[:2].isdigit():
        return stem + ".sfm"
    # Plain filename like GEN.usfm — extract book code and add prefix
    book = stem.upper()
    num = bookcodes.get(book)
    if num is None:
        return None
    return f"{num}{book}{identifier}.sfm"


def fix_usfm_file(input_path: Path, output_path: Path | None = None) -> dict:
    """
    Fix USFM validation issues in a file.

    Args:
        input_path: Path to input USFM file
        output_path: Path to output file (default: overwrite input)

    Returns:
        Dictionary with fix statistics
    """
    if output_path is None:
        output_path = input_path

    stats = {
        "ref_fixes": 0,
        "strongs_fixes": 0,
        "wj_splits": 0,
        "wj_nested_w": 0,
        "empty_fqa": 0,
        "errors": [],
    }

    # Read the file
    try:
        with open(input_path, "r", encoding="utf-8") as f:
            usfm_string = f.read()
    except Exception as e:
        stats["errors"].append(f"Error reading file: {e}")
        return stats

    # Fix 1: Remove \ref markers, converting to plain text
    usfm_string, ref_fixes = fix_ref_markers(usfm_string)
    stats["ref_fixes"] = ref_fixes

    # Fix 2: Pad Strong's numbers to 5 digits
    usfm_string, strongs_fixes = fix_strongs_numbers(usfm_string)
    stats["strongs_fixes"] = strongs_fixes

    # Fix 3: Split \wj markers at verse boundaries
    usfm_string, wj_splits = split_wj_markers(usfm_string)
    stats["wj_splits"] = wj_splits

    # Fix 3b: Add "+" nesting prefix to \w markers nested inside \wj
    usfm_string, wj_nested_w = fix_wj_nested_w_markers(usfm_string)
    stats["wj_nested_w"] = wj_nested_w

    # Fix 4: Remove empty \fqa before \fv
    usfm_string, empty_fqa = fix_empty_fqa(usfm_string)
    stats["empty_fqa"] = empty_fqa

    # Write the result
    try:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(usfm_string)
    except Exception as e:
        stats["errors"].append(f"Error writing file: {e}")

    return stats


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Fix USFM validation errors for Paratext"
    )
    parser.add_argument(
        "input",
        type=Path,
        nargs="?",
        default=Path("results"),
        help="Input USFM file or directory (default: results)",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="Output file or directory (default: results_for_paratext for directory, overwrite for single file)",
    )
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    parser.add_argument("--identifier", default="BSB", help="Edition identifier for Paratext filenames (default: BSB)")

    args = parser.parse_args()

    # Set default output directory when processing the default input directory
    if args.output is None and args.input == Path("results") and args.input.is_dir():
        args.output = Path("results_for_paratext")

    if args.input.is_file():
        # Process single file
        print(f"Processing: {args.input}")
        stats = fix_usfm_file(args.input, args.output)

        if args.verbose or stats["errors"]:
            print(f"  Ref markers fixed: {stats['ref_fixes']}")
            print(f"  Strong's numbers fixed: {stats['strongs_fixes']}")
            print(f"  WJ markers split: {stats['wj_splits']}")
            print(f"  WJ nested \\w markers fixed: {stats['wj_nested_w']}")
            print(f"  Empty \\fqa removed: {stats['empty_fqa']}")
            for error in stats["errors"]:
                print(f"  ERROR: {error}")

        if stats["errors"]:
            return 1
        print("Done!")

    elif args.input.is_dir():
        # Process all USFM files in directory and subdirectories recursively
        usfm_files = list(args.input.rglob("*.usfm"))
        if not usfm_files:
            print(f"No .usfm files found in {args.input}")
            return 1

        # Paratext .sfm output directory (sibling of output directory)
        sfm_dir = None
        if args.output:
            sfm_dir = args.output.parent / "sfm_for_paratext"

        total_stats = {
            "files": 0,
            "sfm_files": 0,
            "ref_fixes": 0,
            "strongs_fixes": 0,
            "wj_splits": 0,
            "wj_nested_w": 0,
            "empty_fqa": 0,
            "errors": [],
        }

        for usfm_file in usfm_files:
            output_file = None
            if args.output:
                # Mirror the subdirectory structure
                relative_path = usfm_file.relative_to(args.input)
                output_file = args.output / relative_path
                output_file.parent.mkdir(parents=True, exist_ok=True)

            if args.verbose:
                # Show relative path for files in subdirectories
                relative_path = usfm_file.relative_to(args.input)
                print(f"Processing: {relative_path}")

            stats = fix_usfm_file(usfm_file, output_file)
            total_stats["files"] += 1
            total_stats["ref_fixes"] += stats["ref_fixes"]
            total_stats["strongs_fixes"] += stats["strongs_fixes"]
            total_stats["wj_splits"] += stats["wj_splits"]
            total_stats["wj_nested_w"] += stats["wj_nested_w"]
            total_stats["empty_fqa"] += stats["empty_fqa"]
            total_stats["errors"].extend(stats["errors"])

            # Also generate Paratext-named .sfm copy, mirroring subdirectories
            # (e.g. strongs/, strongs_full/) alongside top-level files.
            if sfm_dir and output_file and not stats["errors"]:
                relative_path = usfm_file.relative_to(args.input)
                sfm_source_name = relative_path.name
                # The Paratext strongs/ .sfm deliverable uses plain book
                # filenames (no "_strongs" suffix) so it can drop into a
                # Paratext project alongside the base edition without a
                # book-code collision. Other "_strongs"-suffixed outputs
                # (results/strongs, results_usj/strongs, etc.) keep the
                # suffix since they coexist with non-strongs siblings there.
                if relative_path.parent.name == "strongs":
                    stem = Path(sfm_source_name).stem
                    if stem.endswith("_strongs"):
                        sfm_source_name = stem[: -len("_strongs")] + relative_path.suffix
                sfm_name = to_paratext_filename(sfm_source_name, args.identifier)
                if sfm_name:
                    sfm_subdir = sfm_dir / relative_path.parent
                    sfm_subdir.mkdir(parents=True, exist_ok=True)
                    sfm_path = sfm_subdir / sfm_name
                    try:
                        shutil.copy2(output_file, sfm_path)
                        total_stats["sfm_files"] += 1
                    except Exception as e:
                        total_stats["errors"].append(
                            f"Error copying to {sfm_path}: {e}"
                        )

        print(f"\nProcessed {total_stats['files']} files")
        if total_stats["sfm_files"]:
            print(f"  Paratext .sfm files generated: {total_stats['sfm_files']}")
        print(f"  Total ref markers fixed: {total_stats['ref_fixes']}")
        print(f"  Total Strong's numbers fixed: {total_stats['strongs_fixes']}")
        print(f"  Total WJ markers split: {total_stats['wj_splits']}")
        print(f"  Total WJ nested \\w markers fixed: {total_stats['wj_nested_w']}")
        print(f"  Total empty \\fqa removed: {total_stats['empty_fqa']}")

        if total_stats["errors"]:
            print(f"\nErrors ({len(total_stats['errors'])}):")
            for error in total_stats["errors"]:
                print(f"  - {error}")
            return 1

        print("Done!")
    else:
        print(f"Error: {args.input} is not a file or directory")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
