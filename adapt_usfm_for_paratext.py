#!/usr/bin/env python3
"""
Fix USFM validation errors for Paratext compatibility.

This script addresses common USFM validation issues:
1. Converts custom \\ref markers to plain text
2. Pads Strong's numbers to 5 digits (H776 -> H00776, G123 -> G00123)
3. Removes \\wj markers (words of Jesus) that cause issues when spanning verses
"""

import re
import sys
from pathlib import Path


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
    Fix \\ref markers by converting to plain text (Display Text only).

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
    Remove \\wj markers (words of Jesus) while keeping their content.

    These markers cause validation issues when they span across verse
    or paragraph boundaries, resulting in <unmatched marker="wj*" />
    elements in USX output.

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

    stats = {"ref_fixes": 0, "strongs_fixes": 0, "wj_removals": 0, "errors": []}

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

        total_stats = {
            "files": 0,
            "ref_fixes": 0,
            "strongs_fixes": 0,
            "wj_removals": 0,
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
            total_stats["errors"].extend(stats["errors"])

        print(f"\nProcessed {total_stats['files']} files")
        print(f"  Total ref markers fixed: {total_stats['ref_fixes']}")
        print(f"  Total Strong's numbers fixed: {total_stats['strongs_fixes']}")
        print(f"  Total WJ markers removed: {total_stats['wj_removals']}")

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
