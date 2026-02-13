#!/usr/bin/env python3
"""
Fix USFM validation errors for Paratext compatibility.

This script addresses common USFM validation issues:
1. Converts custom \\ref markers to plain text (LOSSY: link targets removed)
2. Pads Strong's numbers to 5 digits (H776 -> H00776, G123 -> G00123)
3. Removes \\wj markers (words of Jesus) (LOSSY: red-letter distinction lost)
4. Removes empty \\mt1 lines (LOSSY: minor layout change)
5. Removes trailing empty \\ft before \\f*
6. Removes empty \\fqa before \\fv
7. Removes standalone empty \\q1 and \\p lines (LOSSY: visual spacing lost)
8. Converts \\pmo to \\p (LOSSY: paragraph style distinction lost)
9. Converts end-of-book \\mr to \\d (LOSSY: marker semantics changed)
10. Removes \\r parallel passage references (LOSSY: cross-references removed)

See PARATEXT_ADAPTATIONS.md for detailed documentation of all lossy changes.
"""

import re
import shutil
import sys
from pathlib import Path

from usfmtc.reference import bookcodes


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


def fix_ref_markers(usfm_string: str) -> tuple[str, int]:
    """
    LOSSY: Fix \\ref markers by converting to plain text (Display Text only).
    The machine-readable link targets (e.g., JHN 1:1-5) are discarded;
    only the human-readable display text is kept.

    Convert: \\ref Display Text|BOOK C:V\\ref*
    To: Display Text

    Also handles refs without the pipe format:
    Convert: \\ref Display Text\\ref*
    To: Display Text

    Examples:
        \\ref John 1:1-5|JHN 1:1-5\\ref* -> John 1:1-5
        \\ref 2 Corinthians 4:6|2CO 4:6\\ref* -> 2 Corinthians 4:6
        \\ref Genesis 4-9\\ref* -> Genesis 4-9

    Returns tuple of (modified string, count of fixes).
    """
    count = 0

    # Pattern 1: \ref Display Text|BOOK C:V\ref* (with pipe and reference)
    ref_pattern_with_pipe = re.compile(r"\\ref ([^|]+)\|[^\\]+\\ref\*")
    count += len(ref_pattern_with_pipe.findall(usfm_string))
    result = ref_pattern_with_pipe.sub(r"\1", usfm_string)

    # Pattern 2: \ref Display Text\ref* (without pipe, just display text)
    # Use non-greedy match to handle any characters including unicode
    ref_pattern_simple = re.compile(r"\\ref (.+?)\\ref\*")
    count += len(ref_pattern_simple.findall(result))
    result = ref_pattern_simple.sub(r"\1", result)

    # Clean up any orphaned \ref* markers that might remain
    orphan_count = len(re.findall(r"\\ref\*", result))
    if orphan_count:
        count += orphan_count
        result = re.sub(r"\\ref\*", "", result)

    # Handle \ref without closing \ref* (e.g., \ref Romans 4:1–12)
    # These appear before closing parenthesis, end of line, or semicolon
    ref_unclosed = re.compile(r"\\ref ([^\\)\n;]+)")
    unclosed_count = len(ref_unclosed.findall(result))
    if unclosed_count:
        count += unclosed_count
        result = ref_unclosed.sub(r"\1", result)

    return result, count


def remove_wj_markers(usfm_string: str) -> tuple[str, int]:
    """
    LOSSY: Remove \\wj markers (words of Jesus) while keeping their content.
    The red-letter distinction for Jesus' spoken words is lost. This is
    necessary because \\wj markers cause validation issues when they span
    across verse or paragraph boundaries, resulting in
    <unmatched marker="wj*" /> elements in USX output.

    Convert: \\wj text content\\wj* -> text content

    Returns tuple of (modified string, count of removals).
    """
    # Pattern to match \wj ... \wj* with content
    wj_pattern = re.compile(r"\\wj (.*?)\\wj\*", re.DOTALL)

    count = len(wj_pattern.findall(usfm_string))
    result = wj_pattern.sub(r"\1", usfm_string)

    # Also remove any orphaned \wj or \wj* markers
    orphan_open = len(re.findall(r"\\wj(?!\*)", result))
    orphan_close = len(re.findall(r"\\wj\*", result))
    count += orphan_open + orphan_close

    result = re.sub(r"\\wj\*", "", result)
    result = re.sub(r"\\wj(?!\*)", "", result)

    return result, count


def fix_mt_markers(usfm_string: str) -> tuple[str, int]:
    """
    Fix \\mt2 + empty \\mt1 pattern by collapsing to a single \\mt1.

    Every book has \\mt2 BookName followed by an empty \\mt1, which
    Paratext flags as an empty marker error. Simply removing the empty
    \\mt1 leaves only \\mt2, which Paratext rejects because DBL requires
    a major title marker (\\mt or \\mt1) before chapter 1.

    Fix: replace \\mt2 BookName + empty \\mt1 with \\mt1 BookName.

    Returns tuple of (modified string, count of fixes).
    """
    # Match \mt2 line followed by empty \mt1 line
    pattern = re.compile(r"^\\mt2 (.+)\n\\mt1\s*$", re.MULTILINE)
    count = len(pattern.findall(usfm_string))
    result = pattern.sub(r"\\mt1 \1", usfm_string)
    # Also handle any remaining standalone empty \mt1 lines
    leftover = re.compile(r"^\\mt1\s*$\n?", re.MULTILINE)
    count += len(leftover.findall(result))
    result = leftover.sub("", result)
    return result, count


def fix_empty_ft(usfm_string: str) -> tuple[str, int]:
    """
    Remove trailing empty \\ft before \\f*.

    Footnotes sometimes end with an empty \\ft marker like:
        \\fqa to profane \\ft \\f*
    The trailing \\ft has no content and should be removed.

    Returns tuple of (modified string, count of fixes).
    """
    pattern = re.compile(r"\\ft\s*\\f\*")
    count = len(pattern.findall(usfm_string))
    result = pattern.sub(r"\\f*", usfm_string)
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


def remove_empty_para_markers(usfm_string: str) -> tuple[str, int]:
    """
    Remove standalone empty \\q1 and \\p lines.

    These appear as lines with just the marker and no text content,
    acting as visual separators. Paratext flags them as empty markers.

    Returns tuple of (modified string, count of removals).
    """
    pattern = re.compile(r"^\\(q1|p)\s*$\n?", re.MULTILINE)
    count = len(pattern.findall(usfm_string))
    result = pattern.sub("", usfm_string)
    return result, count


def fix_pmo_markers(usfm_string: str) -> tuple[str, int]:
    """
    Convert \\pmo to \\p.

    \\pmo (embedded text opening) causes "Marker cannot occur here"
    errors in certain list contexts in Paratext.

    Returns tuple of (modified string, count of fixes).
    """
    pattern = re.compile(r"\\pmo ")
    count = len(pattern.findall(usfm_string))
    result = pattern.sub(r"\\p ", usfm_string)
    return result, count


def fix_mr_markers(usfm_string: str) -> tuple[str, int]:
    """
    Convert \\mr to \\d at end of book.

    \\mr (major section reference range) at end of book causes
    "Marker cannot occur here" errors. \\d (descriptive title)
    is the appropriate marker for psalm/song attributions like
    "For the choirmaster. With stringed instruments."

    Returns tuple of (modified string, count of fixes).
    """
    pattern = re.compile(r"^\\mr ", re.MULTILINE)
    count = len(pattern.findall(usfm_string))
    result = pattern.sub(r"\\d ", usfm_string)
    return result, count


def remove_r_markers(usfm_string: str) -> tuple[str, int]:
    """
    LOSSY: Remove \\r parallel passage reference lines entirely.
    Cross-reference information (e.g., parallel Gospel accounts) is lost.

    The \\r marker is valid USFM for parallel passage references under
    section headings, but Paratext flags the verse ranges within them as
    "Invalid end range" errors because these references appear at the
    section heading level (before any \\v verse marker) and Paratext's
    reference parser cannot validate them without project-level Scripture
    reference settings being configured.

    Since these are section-level references (not verse-level), there is
    no suitable alternative marker: \\sr is for the section's own range,
    and \\x belongs inside verse text.

    Example removed:
        \\r (John 1:1-5; Hebrews 11:1-3)

    Returns tuple of (modified string, count of removals).
    """
    pattern = re.compile(r"^\\r .*$\n?", re.MULTILINE)
    count = len(pattern.findall(usfm_string))
    result = pattern.sub("", usfm_string)
    return result, count


def to_paratext_filename(usfm_filename: str) -> str | None:
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
    return f"{num}{book}BSB.sfm"


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
        "wj_removals": 0,
        "empty_mt1": 0,
        "empty_ft": 0,
        "empty_fqa": 0,
        "empty_para": 0,
        "pmo_fixes": 0,
        "mr_fixes": 0,
        "r_removals": 0,
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

    # Fix 3: Remove \wj markers (words of Jesus)
    usfm_string, wj_removals = remove_wj_markers(usfm_string)
    stats["wj_removals"] = wj_removals

    # Fix 4: Collapse \mt2 + empty \mt1 into \mt1
    usfm_string, empty_mt1 = fix_mt_markers(usfm_string)
    stats["empty_mt1"] = empty_mt1

    # Fix 5: Remove trailing empty \ft before \f*
    usfm_string, empty_ft = fix_empty_ft(usfm_string)
    stats["empty_ft"] = empty_ft

    # Fix 6: Remove empty \fqa before \fv
    usfm_string, empty_fqa = fix_empty_fqa(usfm_string)
    stats["empty_fqa"] = empty_fqa

    # Fix 7: Remove standalone empty \q1 and \p lines
    usfm_string, empty_para = remove_empty_para_markers(usfm_string)
    stats["empty_para"] = empty_para

    # Fix 8: Convert \pmo to \p
    usfm_string, pmo_fixes = fix_pmo_markers(usfm_string)
    stats["pmo_fixes"] = pmo_fixes

    # Fix 9: Convert \mr to \d
    usfm_string, mr_fixes = fix_mr_markers(usfm_string)
    stats["mr_fixes"] = mr_fixes

    # Fix 10: Remove \r parallel passage references (LOSSY)
    usfm_string, r_removals = remove_r_markers(usfm_string)
    stats["r_removals"] = r_removals

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
            print(f"  WJ markers removed: {stats['wj_removals']}")
            print(f"  Empty \\mt1 removed: {stats['empty_mt1']}")
            print(f"  Empty \\ft removed: {stats['empty_ft']}")
            print(f"  Empty \\fqa removed: {stats['empty_fqa']}")
            print(f"  Empty para markers removed: {stats['empty_para']}")
            print(f"  \\pmo converted to \\p: {stats['pmo_fixes']}")
            print(f"  \\mr converted to \\d: {stats['mr_fixes']}")
            print(f"  \\r references removed: {stats['r_removals']}")
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
            "wj_removals": 0,
            "empty_mt1": 0,
            "empty_ft": 0,
            "empty_fqa": 0,
            "empty_para": 0,
            "pmo_fixes": 0,
            "mr_fixes": 0,
            "r_removals": 0,
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
            total_stats["wj_removals"] += stats["wj_removals"]
            total_stats["empty_mt1"] += stats["empty_mt1"]
            total_stats["empty_ft"] += stats["empty_ft"]
            total_stats["empty_fqa"] += stats["empty_fqa"]
            total_stats["empty_para"] += stats["empty_para"]
            total_stats["pmo_fixes"] += stats["pmo_fixes"]
            total_stats["mr_fixes"] += stats["mr_fixes"]
            total_stats["r_removals"] += stats["r_removals"]
            total_stats["errors"].extend(stats["errors"])

            # Also generate Paratext-named .sfm copy (top-level files only)
            if sfm_dir and output_file and not stats["errors"]:
                relative_path = usfm_file.relative_to(args.input)
                if str(relative_path.parent) == ".":
                    sfm_name = to_paratext_filename(relative_path.name)
                    if sfm_name:
                        sfm_dir.mkdir(parents=True, exist_ok=True)
                        sfm_path = sfm_dir / sfm_name
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
        print(f"  Total WJ markers removed: {total_stats['wj_removals']}")
        print(f"  Total empty \\mt1 removed: {total_stats['empty_mt1']}")
        print(f"  Total empty \\ft removed: {total_stats['empty_ft']}")
        print(f"  Total empty \\fqa removed: {total_stats['empty_fqa']}")
        print(f"  Total empty para markers removed: {total_stats['empty_para']}")
        print(f"  Total \\pmo converted to \\p: {total_stats['pmo_fixes']}")
        print(f"  Total \\mr converted to \\d: {total_stats['mr_fixes']}")
        print(f"  Total \\r references removed: {total_stats['r_removals']}")

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
