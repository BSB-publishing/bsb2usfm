#!/usr/bin/env python3
"""
Script to create/update zip files for directories in results and results_usj.

For each directory (including root and subdirectories):
- Finds the common prefix in all filenames (or uses "BSB" as fallback)
- Creates a zip file only if at least one file is newer than the existing zip
- Overwrites the existing zip completely if an update is needed
- Places the zip file in workspace directory (workspace/ for USFM, workspace/usj/ for USJ)
"""

import argparse
import os
import re
import zipfile
from pathlib import Path
from typing import List


def get_common_extension(filenames: List[str]) -> str:
    """
    Extract the common file extension from a list of filenames.
    Returns the extension without the dot, or empty string if no common extension.
    """
    if not filenames:
        return ""

    extensions = [
        os.path.splitext(f)[1].lstrip(".") for f in filenames if os.path.splitext(f)[1]
    ]

    if not extensions:
        return ""

    # Check if all extensions are the same
    first_ext = extensions[0]
    if all(ext == first_ext for ext in extensions):
        return first_ext

    return ""


def get_common_prefix(filenames: List[str]) -> str:
    """
    Extract the common prefix from a list of filenames.
    If no meaningful common prefix is found, returns "BSB".
    """
    if not filenames:
        return "BSB"

    # Remove file extensions for comparison
    names = [os.path.splitext(f)[0] for f in filenames]

    if len(names) == 1:
        # Single file - try to extract meaningful part
        name = names[0]
        # Look for patterns like "01GENBSB_int" -> "BSB_int"
        match = re.search(r"BSB[_\w]*", name)
        if match:
            return match.group(0)
        return "BSB"

    # Find common prefix
    prefix = os.path.commonprefix(names)

    # Clean up the prefix - remove trailing numbers, underscores, etc.
    prefix = re.sub(r"[\d_]+$", "", prefix)

    # If the prefix contains "BSB", extract from BSB onwards
    if "BSB" in prefix:
        match = re.search(r"BSB[_\w]*", prefix)
        if match:
            prefix = match.group(0)

    # If prefix is too short or empty, use "BSB"
    if len(prefix) < 3:
        # Try to find BSB in any of the names
        for name in names:
            match = re.search(r"BSB[_\w]*", name)
            if match:
                return match.group(0)
        return "BSB"

    return prefix


def get_newest_file_time(directory: Path) -> float:
    """
    Get the modification time of the newest file in the directory.
    Returns 0 if directory is empty or doesn't exist.
    """
    if not directory.exists():
        return 0

    newest = 0
    for file in directory.iterdir():
        if file.is_file() and not file.name.endswith(".zip"):
            mtime = file.stat().st_mtime
            if mtime > newest:
                newest = mtime

    return newest


def get_zip_time(zip_path: Path) -> float:
    """
    Get the modification time of the zip file.
    Returns 0 if the file doesn't exist.
    """
    if not zip_path.exists():
        return 0
    return zip_path.stat().st_mtime


def create_zip_for_directory(
    directory: Path,
    zip_output_dir: Path,
    dry_run: bool = False,
    verbose: bool = False,
    name_suffix: str = "",
):
    """
    Create or update a zip file for the given directory.
    The zip file will be created in a separate output directory.

    Args:
        directory: The directory to zip
        zip_output_dir: The directory where the zip file should be created
        dry_run: If True, only show what would be done without creating files
        verbose: If True, show more detailed information
        name_suffix: Optional suffix to add to zip filename (before extension)
    """
    if not directory.exists() or not directory.is_dir():
        return

    # Get all files in the directory (excluding zips)
    files = [
        f for f in directory.iterdir() if f.is_file() and not f.name.endswith(".zip")
    ]

    if not files:
        if verbose:
            print(f"  Skipping {directory} - no files found")
        return

    # Get common prefix and extension for naming
    filenames = [f.name for f in files]
    prefix = get_common_prefix(filenames)
    extension = get_common_extension(filenames)

    # Build zip name with extension suffix and optional name suffix
    if extension:
        zip_name = f"{prefix}_{extension}{name_suffix}.zip"
    else:
        zip_name = f"{prefix}{name_suffix}.zip"

    # Ensure the zip output directory exists
    if not dry_run:
        zip_output_dir.mkdir(parents=True, exist_ok=True)

    zip_path = zip_output_dir / zip_name

    # Check if we need to update
    newest_file_time = get_newest_file_time(directory)
    zip_time = get_zip_time(zip_path)

    if newest_file_time <= zip_time:
        if verbose:
            print(f"  Skipping {directory.name} - zip is up to date ({zip_name})")
        return

    # Create the zip file
    if dry_run:
        print(
            f"  [DRY RUN] Would create {zip_path.relative_to(Path.cwd())} with {len(files)} files"
        )
        return

    print(f"  Creating {zip_path.relative_to(Path.cwd())} with {len(files)} files...")

    try:
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
            for file in sorted(files):
                # Add file with just its name (not full path)
                zipf.write(file, file.name)
                if verbose:
                    print(f"    Added: {file.name}")
        print(f"  ✓ Created {zip_name}")
    except Exception as e:
        print(f"  ✗ Error creating {zip_name}: {e}")


def process_branch(
    branch_path: Path,
    zip_base_dir: Path,
    dry_run: bool = False,
    verbose: bool = False,
    name_suffix: str = "",
):
    """
    Process a branch directory (results or results_usj).
    Creates zips for:
    - All files in the root of the branch
    - All files in each subdirectory

    Args:
        branch_path: Path to the branch directory
        zip_base_dir: Base directory for zip output
        dry_run: If True, only show what would be done
        verbose: If True, show more detailed information
        name_suffix: Optional suffix to add to zip filenames
    """
    if not branch_path.exists():
        print(f"Branch {branch_path} does not exist, skipping.")
        return

    print(f"\nProcessing {branch_path.name}...")

    # Process root files in the branch
    root_files = [
        f for f in branch_path.iterdir() if f.is_file() and not f.name.endswith(".zip")
    ]
    if root_files:
        if verbose:
            print(f"  Root directory ({len(root_files)} files):")
        create_zip_for_directory(
            branch_path,
            zip_base_dir,
            dry_run=dry_run,
            verbose=verbose,
            name_suffix=name_suffix,
        )

    # Process subdirectories
    subdirs = [d for d in branch_path.iterdir() if d.is_dir()]
    for subdir in sorted(subdirs):
        if verbose:
            print(f"  Subdirectory: {subdir.name}")
        # Create corresponding subdirectory in zip output
        zip_subdir = zip_base_dir / subdir.name
        create_zip_for_directory(
            subdir,
            zip_subdir,
            dry_run=dry_run,
            verbose=verbose,
            name_suffix=name_suffix,
        )


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Create/update zip files for results and results_usj directories into workspace/",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                    # Create/update all zip files
  %(prog)s --dry-run          # Show what would be done
  %(prog)s --verbose          # Show detailed progress
  %(prog)s -n -v              # Dry run with verbose output
        """,
    )
    parser.add_argument(
        "-n",
        "--dry-run",
        action="store_true",
        help="Show what would be done without creating files",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Show detailed information about processing",
    )

    args = parser.parse_args()

    script_dir = Path(__file__).parent

    # Define source and output directories (source, output, name_suffix)
    branches = [
        (script_dir / "results", script_dir / "workspace", ""),
        (script_dir / "results_usj", script_dir / "workspace" / "usj", ""),
        (script_dir / "results_usx", script_dir / "workspace" / "usx", ""),
        (
            script_dir / "results_usx_for_DBL",
            script_dir / "workspace" / "usx_for_DBL",
            "_for_DBL",
        ),
        (
            script_dir / "results_for_paratext",
            script_dir / "workspace" / "usfm_for_paratext",
            "_for_paratext",
        ),
    ]

    print("=" * 60)
    print("ZIP Creation Script")
    if args.dry_run:
        print("(DRY RUN MODE - no files will be modified)")
    print("=" * 60)

    for source_dir, zip_dir, suffix in branches:
        process_branch(
            source_dir,
            zip_dir,
            dry_run=args.dry_run,
            verbose=args.verbose,
            name_suffix=suffix,
        )

    print("\n" + "=" * 60)
    print("Done!")
    print("=" * 60)


if __name__ == "__main__":
    main()
