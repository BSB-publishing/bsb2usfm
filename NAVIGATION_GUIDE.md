# Navigation Guide

## Documentation Overview

This repository has multiple README files for different audiences:

### For Bible Users (Most People)
**→ [README.md](README.md)** - START HERE
- Quick download links to ZIP files
- Browse individual files
- Choose the right format for your needs
- Simple, non-technical explanations

### For Developers
**→ [README_developer.md](README_developer.md)**
- Complete technical documentation
- How to build/generate files
- Python tool usage
- Docker setup
- Command-line options

### For Understanding File Generation
**→ [README_zips.md](README_zips.md)**
- How ZIP files are created
- Automatic update mechanism
- Script documentation

**→ [QUICK_START_ZIPS.txt](QUICK_START_ZIPS.txt)**
- Quick reference for ZIP script

## Directory Structure

```
bsb2usfm/
│
├── README.md                         # START HERE - User-friendly downloads
├── README_developer.md               # Developer/technical documentation
├── README_zips.md                    # ZIP creation documentation
├── Makefile                          # Multi-edition build automation
├── bsb2usfm.py                      # Main conversion script
├── create_zips.py                    # ZIP creation script
├── adapt_usx_for_DBL.py             # DBL adaptation script
├── adapt_usfm_for_paratext.py       # Paratext adaptation script
│
├── demo_data/                        # Shared sample footnotes and book names
│
├── bereanbible/                      # BSB EDITION (Full Bible - 66 books)
│   ├── temp/                         # Cached source data (gitignored)
│   ├── results/                      # USFM files
│   │   ├── *.usfm                   #   Standard USFM
│   │   ├── int/                     #   Interlinear USFM
│   │   ├── strongs/                 #   Strong's USFM
│   │   └── strongs_full/            #   Complete Strong's USFM
│   ├── results_usj/                  # USJ files (same subdirectory layout)
│   ├── results_usx/                  # USX files (same subdirectory layout)
│   ├── results_usx_for_DBL/         # USX adapted for Digital Bible Library
│   ├── results_for_paratext/        # USFM adapted for Paratext
│   ├── sfm_for_paratext/            # SFM files for Paratext
│   └── workspace/                    # ZIP archives (gitignored)
│
└── majoritybible/                    # MSB EDITION (New Testament - 27 books)
    ├── temp/                         # Cached source data (gitignored)
    ├── results/                      # USFM files (same layout as BSB)
    ├── results_usj/                  # USJ files
    ├── results_usx/                  # USX files
    ├── results_usx_for_DBL/         # USX adapted for Digital Bible Library
    ├── results_for_paratext/        # USFM adapted for Paratext
    ├── sfm_for_paratext/            # SFM files for Paratext
    └── workspace/                    # ZIP archives (gitignored)
```

## Quick Navigation by Task

### "I want to download Bible files"
→ [README.md](README.md) - See the download table or visit [GitHub Releases](../../releases/latest)

### "I want a specific BSB book (e.g., Genesis)"
→ [bereanbible/results/](bereanbible/results/) for USFM, [bereanbible/results_usj/](bereanbible/results_usj/) for USJ
→ Look for GEN.usfm or GEN.usj

### "I want a specific MSB book (e.g., Matthew)"
→ [majoritybible/results/](majoritybible/results/) for USFM, [majoritybible/results_usj/](majoritybible/results_usj/) for USJ
→ Look for MAT.usfm or MAT.usj

### "I want all books in one download"
→ [README.md](README.md) - Download one of the ZIP files from GitHub Releases

### "I want to understand the formats"
→ [README.md](README.md) - See "Which Format Should I Use?"

### "I want to build/generate files myself"
→ [README_developer.md](README_developer.md) - Full developer guide

### "I want to build just one edition"
→ Run `make bereanbible` or `make majoritybible`

### "I want to understand how ZIPs are created"
→ [README_zips.md](README_zips.md) - ZIP creation guide

## Tips

1. **Most users** should start with [README.md](README.md)
2. **Developers** should read [README_developer.md](README_developer.md)
3. **Two editions** are built: BSB (full Bible) and MSB (New Testament)
4. **Each edition** has its own directory with identical internal structure
5. **ZIP files** contain all books for the edition in one archive
6. **`make all`** builds both editions; `make bereanbible` or `make majoritybible` builds one

## External Links

- Berean Bible Website: https://bereanbible.com
- Majority Bible Website: https://majoritybible.com
- USFM Standard: https://ubsicap.github.io/usfm/
- USJ Standard: https://github.com/usfm-bible/tcdocs/blob/main/grammar/usj.rst
