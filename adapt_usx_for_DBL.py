#!/usr/bin/env python3
"""
Fix USX validation errors.

This script addresses common USX validation issues:
1. Converts inline verse markers to milestone format (sid/eid)
2. Fixes <ref> elements inside <para style="r"> sections
3. Pads Strong's numbers to 5 digits (H776 -> H00776, G123 -> G00123)
4. Ensures proper USX 3.0 compliance
"""

import re
import sys
from pathlib import Path


def fix_strongs_numbers(xml_string: str) -> tuple[str, int]:
    """
    Fix Strong's numbers by padding to 5 digits.

    Convert: strong="H776" -> strong="H00776"
    Convert: strong="G123" -> strong="G00123"

    USX requires Strong's IDs in the form H##### or G##### (exactly 5 digits).

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
    count = sum(1 for m in strongs_pattern.finditer(xml_string) if len(m.group(2)) < 5)

    result = strongs_pattern.sub(pad_strong, xml_string)

    return result, count


def fix_ref_elements(xml_string: str) -> tuple[str, int]:
    """
    Fix <ref> elements by converting to plain text.

    Convert: <ref loc="1TI 5:3-16">1 Timothy 5:3–16</ref>
    To: 1 Timothy 5:3–16

    Returns tuple of (modified string, count of fixes).
    """
    # Pattern to match ref elements and capture their text content
    ref_pattern = re.compile(r'<ref\s+loc="[^"]*">([^<]*)</ref>')

    count = len(ref_pattern.findall(xml_string))
    result = ref_pattern.sub(r"\1", xml_string)

    return result, count


def convert_verses_to_milestones(xml_string: str, book_code: str) -> tuple[str, int]:
    """
    Convert inline verse markers to milestone format with sid/eid.

    From: <verse style="v" number="1" />
    To: <verse number="1" style="v" sid="BOOK C:V" /> text <verse eid="BOOK C:V" />

    Returns tuple of (modified string, count of conversions).
    """
    current_chapter = "1"
    conversions = 0

    # First pass: Find all verse markers and track chapter changes
    # Build a list of (position, type, data) tuples

    chapter_pattern = re.compile(r'<chapter\s+number="(\d+)"[^>]*/>')

    # Match both attribute orders for verse markers
    verse_pattern = re.compile(
        r'<verse\s+(?:style="v"\s+number="(\d+)"|number="(\d+)"\s+style="v")\s*/>'
    )

    result = []
    last_end = 0
    last_verse_id = None

    # Find all chapters and verses
    markers = []

    for match in chapter_pattern.finditer(xml_string):
        markers.append(("chapter", match.start(), match.end(), match.group(1)))

    for match in verse_pattern.finditer(xml_string):
        verse_num = match.group(1) or match.group(2)
        markers.append(("verse", match.start(), match.end(), verse_num))

    # Sort by position
    markers.sort(key=lambda x: x[1])

    # Process markers in order
    for marker in markers:
        marker_type, start, end, value = marker

        if marker_type == "chapter":
            # Add end marker for previous verse before chapter
            if last_verse_id:
                result.append(xml_string[last_end:start])
                result.append(f'<verse eid="{last_verse_id}" />')
                last_end = start
                last_verse_id = None
            current_chapter = value

        elif marker_type == "verse":
            verse_num = value
            verse_id = f"{book_code} {current_chapter}:{verse_num}"

            # Add text before this verse
            result.append(xml_string[last_end:start])

            # Add end marker for previous verse
            if last_verse_id:
                result.append(f'<verse eid="{last_verse_id}" />')

            # Add new verse with sid
            result.append(f'<verse number="{verse_num}" style="v" sid="{verse_id}" />')

            last_end = end
            last_verse_id = verse_id
            conversions += 1

    # Add remaining content
    result.append(xml_string[last_end:])

    # Add final end marker before </usx>
    final_result = "".join(result)
    if last_verse_id:
        final_result = final_result.replace(
            "</usx>", f'<verse eid="{last_verse_id}" /></usx>'
        )

    return final_result, conversions


def fix_usx_file(input_path: Path, output_path: Path | None = None) -> dict:
    """
    Fix USX validation issues in a file.

    Args:
        input_path: Path to input USX file
        output_path: Path to output file (default: overwrite input)

    Returns:
        Dictionary with fix statistics
    """
    if output_path is None:
        output_path = input_path

    stats = {"ref_fixes": 0, "verse_conversions": 0, "strongs_fixes": 0, "errors": []}

    # Read the file
    try:
        with open(input_path, "r", encoding="utf-8") as f:
            xml_string = f.read()
    except Exception as e:
        stats["errors"].append(f"Error reading file: {e}")
        return stats

    # Extract book code
    book_match = re.search(r'<book[^>]+code="([^"]+)"', xml_string)
    book_code = book_match.group(1) if book_match else "UNK"

    # Fix 1: Remove <ref> elements
    xml_string, ref_fixes = fix_ref_elements(xml_string)
    stats["ref_fixes"] = ref_fixes

    # Fix 2: Convert inline verse markers to milestone format
    xml_string, verse_conversions = convert_verses_to_milestones(xml_string, book_code)
    stats["verse_conversions"] = verse_conversions

    # Fix 3: Pad Strong's numbers to 5 digits
    xml_string, strongs_fixes = fix_strongs_numbers(xml_string)
    stats["strongs_fixes"] = strongs_fixes

    # Write the result
    try:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(xml_string)
    except Exception as e:
        stats["errors"].append(f"Error writing file: {e}")

    return stats


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Fix USX validation errors")
    parser.add_argument(
        "input",
        type=Path,
        nargs="?",
        default=Path("results_usx"),
        help="Input USX file or directory (default: results_usx)",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="Output file or directory (default: results_usx_for_DBL for directory, overwrite for single file)",
    )
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")

    args = parser.parse_args()

    # Set default output directory when processing the default input directory
    if (
        args.output is None
        and args.input == Path("results_usx")
        and args.input.is_dir()
    ):
        args.output = Path("results_usx_for_DBL")

    if args.input.is_file():
        # Process single file
        print(f"Processing: {args.input}")
        stats = fix_usx_file(args.input, args.output)

        if args.verbose or stats["errors"]:
            print(f"  Ref elements fixed: {stats['ref_fixes']}")
            print(f"  Verse conversions: {stats['verse_conversions']}")
            print(f"  Strong's numbers fixed: {stats['strongs_fixes']}")
            for error in stats["errors"]:
                print(f"  ERROR: {error}")

        if stats["errors"]:
            return 1
        print("Done!")

    elif args.input.is_dir():
        # Process all USX files in directory and subdirectories recursively
        usx_files = list(args.input.rglob("*.usx"))
        if not usx_files:
            print(f"No .usx files found in {args.input}")
            return 1

        total_stats = {
            "files": 0,
            "ref_fixes": 0,
            "verse_conversions": 0,
            "strongs_fixes": 0,
            "errors": [],
        }

        for usx_file in usx_files:
            output_file = None
            if args.output:
                # Mirror the subdirectory structure
                relative_path = usx_file.relative_to(args.input)
                output_file = args.output / relative_path
                output_file.parent.mkdir(parents=True, exist_ok=True)

            if args.verbose:
                # Show relative path for files in subdirectories
                relative_path = usx_file.relative_to(args.input)
                print(f"Processing: {relative_path}")

            stats = fix_usx_file(usx_file, output_file)
            total_stats["files"] += 1
            total_stats["ref_fixes"] += stats["ref_fixes"]
            total_stats["verse_conversions"] += stats["verse_conversions"]
            total_stats["strongs_fixes"] += stats["strongs_fixes"]
            total_stats["errors"].extend(stats["errors"])

        print(f"\nProcessed {total_stats['files']} files")
        print(f"  Total ref elements fixed: {total_stats['ref_fixes']}")
        print(f"  Total verse conversions: {total_stats['verse_conversions']}")
        print(f"  Total Strong's numbers fixed: {total_stats['strongs_fixes']}")

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
