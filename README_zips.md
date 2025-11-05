# ZIP Creation Script

This script automatically creates and maintains ZIP archives for all files in the `results` and `results_usj` directories.

## Overview

The `create_zips.py` script:
- Processes both `results` and `results_usj` directory trees
- Creates separate ZIP files for each directory (root and subdirectories)
- Only updates ZIPs when source files are newer than the existing archive
- Names ZIPs based on common prefixes in filenames (defaults to "BSB") and file extensions
- Completely regenerates ZIP files when updates are needed (not incremental)</parameter>

## Usage

### Basic Usage

Create or update all ZIP files:
```bash
python3 create_zips.py
```

or simply:
```bash
./create_zips.py
```

### Command-Line Options

- `-n, --dry-run`: Show what would be done without actually creating files
- `-v, --verbose`: Show detailed information about processing
- `-h, --help`: Show help message

### Examples

```bash
# Normal operation - create/update ZIPs as needed
python3 create_zips.py

# See what would be updated without making changes
python3 create_zips.py --dry-run

# Get detailed output including all files being added
python3 create_zips.py --verbose

# Combine dry-run and verbose for maximum information
python3 create_zips.py -n -v
```

## Generated ZIP Files

The script creates the following ZIP files:

### In `results/`:
- `results/BSB_usfm.zip` - All `.usfm` files in the root directory
- `results/int/BSB_int_usfm.zip` - All files in the `int/` subdirectory
- `results/strongs/BSB_strongs_usfm.zip` - All files in the `strongs/` subdirectory
- `results/strongs_full/BSB_full_strongs_usfm.zip` - All files in the `strongs_full/` subdirectory

### In `results_usj/`:
- `results_usj/BSB_usj.zip` - All `.usj` files in the root directory
- `results_usj/int/BSB_int_usj.zip` - All files in the `int/` subdirectory
- `results_usj/strongs/BSB_strongs_usj.zip` - All files in the `strongs/` subdirectory
- `results_usj/strongs_full/BSB_full_strongs_usj.zip` - All files in the `strongs_full/` subdirectory</parameter>

## How It Works

1. **Directory Scanning**: The script scans each directory for files (excluding existing `.zip` files)

2. **Name Detection**: It analyzes filenames to find:
   - Common prefixes (e.g., "BSB" from "01GENBSB_int.usfm")
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

The script is already integrated into the Makefile and will run automatically after all files are generated:

```makefile
all: [dependencies...]
	$(PYTHON) create_zips.py
```

You can also add custom targets:
```makefile
zips:
	python3 create_zips.py

clean-zips:
	find results results_usj -name "*.zip" -type f -delete
```

When you run `make all`, the ZIP files will be automatically created/updated as the final step.

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