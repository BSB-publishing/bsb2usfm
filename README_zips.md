# ZIP Creation Script

This script automatically creates and maintains ZIP archives for all generated files under each edition's directory (e.g., `bereanbible/` and `majoritybible/`).

## Overview

The `create_zips.py` script:
- Processes `results`, `results_usj`, and `results_usx` directory trees for each edition
- Creates separate ZIP files for each directory (root and subdirectories)
- Only updates ZIPs when source files are newer than the existing archive
- Names ZIPs based on the edition identifier (e.g., "BSB" or "MSB") and file extensions
- Completely regenerates ZIP files when updates are needed (not incremental)</parameter>

## Usage

### Basic Usage

Create or update ZIP files for a specific edition:
```bash
python3 create_zips.py --base-dir bereanbible --identifier BSB
python3 create_zips.py --base-dir majoritybible --identifier MSB
```

### Command-Line Options

- `--base-dir`: Edition directory (e.g., `bereanbible`, `majoritybible`)
- `--identifier`: Edition identifier used in filenames (e.g., `BSB`, `MSB`)
- `-n, --dry-run`: Show what would be done without actually creating files
- `-v, --verbose`: Show detailed information about processing
- `-h, --help`: Show help message

### Examples

```bash
# Create/update ZIPs for BSB
python3 create_zips.py --base-dir bereanbible --identifier BSB

# Create/update ZIPs for MSB
python3 create_zips.py --base-dir majoritybible --identifier MSB

# Dry-run to see what would be updated
python3 create_zips.py --base-dir bereanbible --identifier BSB --dry-run

# Verbose output
python3 create_zips.py --base-dir bereanbible --identifier BSB --verbose
```

## Generated ZIP Files

The script creates ZIP files under each edition's `workspace/` directory.
For example, for BSB (`bereanbible/workspace/`):

### USFM
- `BSB_usfm.zip` - Standard clean text
- `int/BSB_int_usfm.zip` - With interlinear data
- `strongs/BSB_strongs_usfm.zip` - With Strong's numbers
- `strongs_full/BSB_full_strongs_usfm.zip` - Complete Strong's data

### USJ
- `usj/BSB_usj.zip` - Standard clean text
- `usj/int/BSB_int_usj.zip` - With interlinear data
- `usj/strongs/BSB_strongs_usj.zip` - With Strong's numbers
- `usj/strongs_full/BSB_full_strongs_usj.zip` - Complete Strong's data

### USX
- `usx/BSB_usx.zip` - Standard clean text
- `usx/int/BSB_int_usx.zip` - With interlinear data
- `usx/strongs/BSB_strongs_usx.zip` - With Strong's numbers
- `usx/strongs_full/BSB_full_strongs_usx.zip` - Complete Strong's data

The same structure applies to MSB under `majoritybible/workspace/` with
the `MSB` prefix (New Testament only).</parameter>

## How It Works

1. **Directory Scanning**: The script scans each directory for files (excluding existing `.zip` files)

2. **Name Detection**: It analyzes filenames to find:
   - Common prefixes (e.g., "BSB" or "MSB" from filenames like "01GENBSB_int.usfm")
   - Common file extensions (e.g., "usfm", "usj")

3. **Timestamp Comparison**: For each directory, it compares:</parameter>
   - The modification time of the newest file in the directory
   - The modification time of the existing ZIP file (if any)

4. **Conditional Update**: A ZIP is only created/updated if:
   - No ZIP file exists yet, OR
   - At least one source file is newer than the existing ZIP

5. **Complete Regeneration**: When an update is needed, the entire ZIP is recreated from scratch (not patched)

6. **Co-location**: ZIP files are always created in the same directory as their source files

7. **Extension Suffix**: ZIP filenames include the common file extension (e.g., `BSB_usfm.zip`, `BSB_usj.zip`)</parameter>

## Integration

You can integrate this script into your workflow:

### Manual Updates
Run the script whenever you want to ensure ZIPs are up to date:
```bash
python3 create_zips.py
```

### Automated Updates with Makefile

The script is already integrated into the Makefile and runs automatically for each edition after all files are generated. When you run `make all` (or `make bereanbible` / `make majoritybible`), the ZIP files are created/updated as the final step.

### Git Hook
Add to `.git/hooks/pre-commit` to update ZIPs before commits:
```bash
#!/bin/sh
python3 create_zips.py
```

## Notes

- ZIP files are created with DEFLATE compression
- Files are stored in the ZIP with just their filename (no directory path)
- ZIP files are always placed in the same directory as their source files
- ZIP filenames include the file extension suffix (e.g., `_usfm`, `_usj`)
- The script is idempotent - safe to run multiple times
- Only processes directories that exist; missing directories are skipped
- Existing ZIP files are completely overwritten when updates are needed</parameter>

## Requirements

- Python 3.6 or higher
- Standard library only (no external dependencies)