# Multi-Source Adaptation - Implementation Notes

## Status: IMPLEMENTED

The multi-edition build system is now fully operational. This document describes the architecture and key implementation decisions.

## Architecture

### Edition Definitions

Two editions are defined in the Makefile:

| Edition | Identifier | Scope | Source URL | Sentinel |
|---------|-----------|-------|-----------|----------|
| `bereanbible` | BSB | Full Bible (66 books) | https://bereanbible.com/bsb_tables.tsv | GEN |
| `majoritybible` | MSB | New Testament (27 books) | https://majoritybible.com/msb_nt_tables.tsv | MAT |

### Data Flow

1. **Source**: Per-edition TSV file downloaded from respective URLs
2. **Cache**: Downloaded to `<edition>/temp/source.tsv` (with timestamp checking)
3. **Converter**: `bsb2usfm.py --identifier <ID>` reads TSV and generates multiple output formats
4. **Post-processing**: Adaptation scripts for DBL and Paratext
5. **Packaging**: `create_zips.py --base-dir <edition> --identifier <ID>` creates distribution archives

### Output Structure (per edition)

```
<edition>/
  temp/                       # Cached source TSV
  results/                    # Basic USFM files (%.usfm)
    int/                      # Interlinear versions
    strongs/                  # Strong's numbers
    strongs_full/             # Full Strong's with placeholders
  results_usj/                # Same structure for USJ format
  results_usx/                # Same structure for USX format
  results_usx_for_DBL/        # Adapted for Digital Bible Library
  results_for_paratext/       # Adapted for Paratext
  sfm_for_paratext/           # SFM files for Paratext
  workspace/                  # ZIP archives for distribution
```

## Key Implementation Decisions

### Approach: Parameterized Makefile with Pattern Rules

The Makefile uses GNU Make's `define`/`eval`/`foreach` macros to generate per-edition targets from a single template. This keeps the build logic DRY while maintaining Make as the orchestrator.

### Dynamic Column Detection

The BSB and MSB source TSV files have different column names:
- BSB uses ` BSB version ` and `WLC / Nestle Base TR RP WH NE NA SBL`
- MSB uses ` MSB version ` and `MT Greek`

The converter (`bsb2usfm.py`) dynamically detects these columns from the header row rather than hardcoding column names. The `addheadline()` method scans for:
- Any column ending with `version` → used as the version text column
- Any column starting with `WLC / Nestle` or equal to `MT Greek` → used as the interlinear column

### Sentinel Files

Make tracks build completion via file timestamps. Each edition uses a different "sentinel" book:
- BSB: `GEN` (book code 01) - first book of the full Bible
- MSB: `MAT` (book code 40) - first book of the New Testament

Helper functions compute variant sentinel filenames (e.g., `01GENBSB_int`, `40MATMSB_strongs`).

### Shared Demo Data

Both editions reuse the same `demo_data/sample_footnotes.tsv` and `demo_data/sample_book_names.xml` files. Edition-specific demo data files can be added later if needed.

### Identifier Parameterization

The `--identifier` parameter was added to:
- `bsb2usfm.py` - Controls the identifier in `\id` lines and output filenames
- `adapt_usfm_for_paratext.py` - Controls the identifier suffix in Paratext filenames
- `create_zips.py` - Controls ZIP naming via `--base-dir` and `--identifier`

## Scripts Modified

| Script | Changes |
|--------|---------|
| `bsb2usfm.py` | Added `--identifier` param, dynamic column detection |
| `adapt_usfm_for_paratext.py` | Added `--identifier` param |
| `create_zips.py` | Added `--base-dir` and `--identifier` params |
| `adapt_usx_for_DBL.py` | Already parameterized (accepts input path and `-o`) |
| `Makefile` | Complete rewrite with `define`/`eval`/`foreach` macros |

## Adding a New Edition

1. Add edition variables to the Makefile:
   ```makefile
   newedition_URL = https://example.com/source.tsv
   newedition_ID = NEW
   newedition_SENTINEL = GEN   # or MAT for NT-only
   ```

2. Add to the EDITIONS list and .PHONY:
   ```makefile
   EDITIONS = bereanbible majoritybible newedition
   .PHONY: all clean clean-cache force bereanbible majoritybible newedition
   ```

3. The `foreach`/`eval` macros automatically generate all build targets.
