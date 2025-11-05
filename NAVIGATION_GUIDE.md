# Navigation Guide

## 📚 Documentation Overview

This repository has multiple README files for different audiences:

### For Bible Users (Most People)
**→ [README.md](README.md)** ⭐ START HERE
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

## 📂 Directory Structure

```
bsb2usfm/
│
├── README.md ⭐                    # START HERE - User-friendly downloads
├── README_developer.md            # Developer/technical documentation
├── README_zips.md                 # ZIP creation documentation
│
├── results/                       # USFM FORMAT FILES
│   ├── BSB_usfm.zip              # → Download: Standard USFM
│   ├── *.usfm                    # → Individual book files
│   │
│   ├── int/
│   │   ├── BSB_int_usfm.zip      # → Download: Interlinear USFM
│   │   └── *.usfm                # → Individual interlinear files
│   │
│   ├── strongs/
│   │   ├── BSB_strongs_usfm.zip  # → Download: Strong's USFM
│   │   └── *.usfm                # → Individual Strong's files
│   │
│   └── strongs_full/
│       ├── BSB_full_strongs_usfm.zip  # → Download: Full Strong's USFM
│       └── *.usfm                     # → Individual full files
│
└── results_usj/                   # USJ FORMAT FILES (JSON)
    ├── BSB_usj.zip               # → Download: Standard USJ
    ├── *.usj                     # → Individual book files
    │
    ├── int/
    │   ├── BSB_int_usj.zip       # → Download: Interlinear USJ
    │   └── *.usj                 # → Individual interlinear files
    │
    ├── strongs/
    │   ├── BSB_strongs_usj.zip   # → Download: Strong's USJ
    │   └── *.usj                 # → Individual Strong's files
    │
    └── strongs_full/
        ├── BSB_full_strongs_usj.zip  # → Download: Full Strong's USJ
        └── *.usj                      # → Individual full files
```

## 🎯 Quick Navigation by Task

### "I want to download Bible files"
→ [README.md](README.md) - See the download table

### "I want a specific book (e.g., Genesis)"
→ [results/](results/) for USFM or [results_usj/](results_usj/) for USJ
→ Look for GEN.usfm or GEN.usj

### "I want all books in one download"
→ [README.md](README.md) - Download one of the ZIP files

### "I want to understand the formats"
→ [README.md](README.md) - See "Which Format Should I Use?"

### "I want to build/generate files myself"
→ [README_developer.md](README_developer.md) - Full developer guide

### "I want to understand how ZIPs are created"
→ [README_zips.md](README_zips.md) - ZIP creation guide

## 💡 Tips

1. **Most users** should start with [README.md](README.md)
2. **Developers** should read [README_developer.md](README_developer.md)
3. **Each directory** contains a specific version of the Bible
4. **ZIP files** contain all 66 books in one archive
5. **Individual files** can be downloaded from the folders

## 🔗 External Links

- Berean Bible Website: https://bereanbible.com
- USFM Standard: https://ubsicap.github.io/usfm/
- USJ Standard: https://github.com/usfm-bible/tcdocs/blob/main/grammar/usj.rst
