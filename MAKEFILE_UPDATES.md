# Makefile - Multi-Edition Build System

## Overview

The Makefile supports building two Bible editions in parallel:

| Edition | Identifier | Scope | Source URL | Directory |
|---------|-----------|-------|-----------|-----------|
| Berean Standard Bible | BSB | Full Bible (66 books) | https://bereanbible.com/bsb_tables.tsv | `bereanbible/` |
| Majority Standard Bible | MSB | New Testament (27 books) | https://majoritybible.com/msb_nt_tables.tsv | `majoritybible/` |

Each edition is built into its own directory with identical internal structure.

## Architecture

The Makefile uses GNU Make's `define`/`eval`/`foreach` macros to generate per-edition targets from a single template. Edition-specific parameters are defined as variables:

```makefile
EDITIONS = bereanbible majoritybible

bereanbible_URL = https://bereanbible.com/bsb_tables.tsv
bereanbible_ID = BSB
bereanbible_SENTINEL = GEN

majoritybible_URL = https://majoritybible.com/msb_nt_tables.tsv
majoritybible_ID = MSB
majoritybible_SENTINEL = MAT
```

The `SENTINEL` variable defines which book file Make uses to track whether the build step has completed (GEN for full Bible, MAT for NT-only).

## How It Works

### Cache Management

Each edition has its own cached source file at `<edition>/temp/source.tsv`. The cache rule:

1. **Runs on every build** to check for remote updates
2. Uses `curl -z` (time conditional) to only download if remote is newer
3. Downloads to a temporary file first, then replaces the cache only if updated
4. Falls back to a full download if no cached file exists

### Build Dependencies

All output files depend on both `bsb2usfm.py` AND the edition's cached source file:

```
<edition>/results/<SENTINEL>.usfm: bsb2usfm.py <edition>/temp/source.tsv
```

Output files are regenerated if EITHER:
- The Python script is modified, OR
- The remote data file is updated

### Post-Processing

After generating all format variants, each edition runs:
1. `adapt_usx_for_DBL.py` - Adapts USX files for Digital Bible Library
2. `adapt_usfm_for_paratext.py` - Adapts USFM files for Paratext
3. `create_zips.py` - Creates ZIP archives in `<edition>/workspace/`

## Usage

### Build Both Editions
```bash
make all
```

### Build a Single Edition
```bash
make bereanbible        # BSB only
make majoritybible      # MSB only
```

### Force Complete Rebuild
```bash
make force
```
This removes all cached data files and rebuilds everything from scratch.

### Clean Output Files
```bash
make clean
```
Removes all generated files (results, workspace, etc.) for both editions.

### Clean Cache Only
```bash
make clean-cache
```
Removes only the cached data files, forcing a fresh download on next build.

## Makefile Targets

| Command | Description |
|---------|-------------|
| `make all` | Build both editions (default) |
| `make bereanbible` | Build BSB edition only |
| `make majoritybible` | Build MSB edition only |
| `make clean` | Remove generated files for both editions |
| `make clean-cache` | Remove cached source data for both editions |
| `make force` | Clean cache and rebuild all |

## Adding a New Edition

To add a third edition:

1. Define its parameters:
   ```makefile
   new_edition_URL = https://example.com/source.tsv
   new_edition_ID = NEW
   new_edition_SENTINEL = GEN   # or MAT for NT-only
   ```

2. Add it to the EDITIONS list:
   ```makefile
   EDITIONS = bereanbible majoritybible new_edition
   ```

3. Add it to the `.PHONY` target list

The `foreach`/`eval` macros automatically generate all necessary targets.

## Technical Details

### Sentinel Files

Since Make tracks build completion via file timestamps, each build step uses a "sentinel" file - the first book generated:
- **BSB (full Bible)**: `GEN.usfm` (book code 01)
- **MSB (NT-only)**: `MAT.usfm` (book code 40)

Helper functions compute the sentinel filenames for variants:
```makefile
sentinel_int = <bookcode><SENTINEL><ID>_int          # e.g., 01GENBSB_int
sentinel_strongs = <bookcode><SENTINEL><ID>_strongs   # e.g., 40MATMSB_strongs
```

### Remote File Checking

The Makefile uses `curl -z` which performs a conditional GET request:
1. Sends the local file's timestamp to the remote server
2. Server compares with its Last-Modified header
3. If remote is newer: downloads to temporary file, then replaces cache
4. If remote is same/older: no download (cache unchanged)

This means:
- Every `make` checks for updates (minimal network overhead)
- Full download only happens when remote is actually newer
- Timestamp-based rebuilds work correctly

## Requirements

- `curl` must be installed (standard on most Unix-like systems)
- GNU Make (for `define`/`eval`/`foreach` support)
- Internet connection required to check for remote updates
