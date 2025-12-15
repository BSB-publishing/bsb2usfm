# Berean Standard Bible - USFM & USJ Files

[![License: Public Domain](https://img.shields.io/badge/License-Public%20Domain-brightgreen.svg)](UNLICENSE)
[![Bible Version](https://img.shields.io/badge/BSB-v5.1-blue.svg)](https://github.com/BSB-publishing/bsb2usfm/releases)

Welcome! This repository provides the **Berean Standard Bible (BSB)** in multiple digital formats for Bible software, apps, and translation projects.

> **📄 License:** The BSB text is in the **Public Domain** - completely free to use, modify, and distribute for any purpose. See [LICENSE](LICENSE) and [UNLICENSE](UNLICENSE) for details.

## 🚀 GitHub Releases

**Current Version: 5.1**

The recommended way to download the complete BSB dataset is through our **[GitHub Releases](../../releases/latest)**. Each release includes all ZIP files in both USFM and USJ formats.

### Release Assets

Each GitHub release (version 5.1 and later) includes 8 ZIP files:

**USFM Format:**
- `BSB_usfm.zip` - Standard clean text
- `BSB_int_usfm.zip` - With interlinear data
- `BSB_strongs_usfm.zip` - With Strong's numbers
- `BSB_full_strongs_usfm.zip` - Complete Strong's data

**USJ Format:**
- `BSB_usj.zip` - Standard clean text
- `BSB_int_usj.zip` - With interlinear data
- `BSB_strongs_usj.zip` - With Strong's numbers
- `BSB_full_strongs_usj.zip` - Complete Strong's data

All release files are automatically generated and stored in the `/workspace` directory during the build process.

## 📦 Quick Downloads (Alternative)

Choose the format you need and download the ZIP file:

### USFM Format (Universal Standard Format Markers)
Standard format used by Paratext, PTXprint, and most Bible translation software.

| Version | Description | GitHub Release |
|---------|-------------|----------------|
| **Standard** | Clean Bible text | `BSB_usfm.zip` |
| **Interlinear** | With original language reverse interlinear | `BSB_int_usfm.zip` |
| **Strong's** | With Strong's numbers | `BSB_strongs_usfm.zip` |
| **Strong's Full** | With Strong's numbers, placeholders, and brackets | `BSB_full_strongs_usfm.zip` |

### USJ Format (Unified Scripture JSON)
Modern JSON-based format for web applications and digital platforms.

| Version | Description | GitHub Release |
|---------|-------------|----------------|
| **Standard** | Clean Bible text | `BSB_usj.zip` |
| **Interlinear** | With original language reverse interlinear | `BSB_int_usj.zip` |
| **Strong's** | With Strong's numbers | `BSB_strongs_usj.zip` |
| **Strong's Full** | With Strong's numbers, placeholders, and brackets | `BSB_full_strongs_usj.zip` |

## 📂 Browse Individual Files

Don't want to download a ZIP? Browse and download individual book files:

### USFM Files
- **Standard**: [`results/`](results/) - Individual `.usfm` files (GEN.usfm, EXO.usfm, etc.)
- **Interlinear**: [`results/int/`](results/int/) - With reverse interlinear data
- **Strong's**: [`results/strongs/`](results/strongs/) - With Strong's numbers
- **Strong's Full**: [`results/strongs_full/`](results/strongs_full/) - Complete Strong's data

### USJ Files
- **Standard**: [`results_usj/`](results_usj/) - Individual `.usj` files (GEN.usj, EXO.usj, etc.)
- **Interlinear**: [`results_usj/int/`](results_usj/int/) - With reverse interlinear data
- **Strong's**: [`results_usj/strongs/`](results_usj/strongs/) - With Strong's numbers
- **Strong's Full**: [`results_usj/strongs_full/`](results_usj/strongs_full/) - Complete Strong's data

## 📖 Book Codes Reference

Each file is named with a standard 3-letter book code:

**Old Testament**: GEN, EXO, LEV, NUM, DEU, JOS, JDG, RUT, 1SA, 2SA, 1KI, 2KI, 1CH, 2CH, EZR, NEH, EST, JOB, PSA, PRO, ECC, SNG, ISA, JER, LAM, EZK, DAN, HOS, JOL, AMO, OBA, JON, MIC, NAM, HAB, ZEP, HAG, ZEC, MAL

**New Testament**: MAT, MRK, LUK, JHN, ACT, ROM, 1CO, 2CO, GAL, EPH, PHP, COL, 1TH, 2TH, 1TI, 2TI, TIT, PHM, HEB, JAS, 1PE, 2PE, 1JN, 2JN, 3JN, JUD, REV

## ❓ Which Format Should I Use?

### Choose USFM if you're using:
- ✅ Paratext
- ✅ PTXprint
- ✅ Bible translation software
- ✅ Traditional Bible publishing tools

### Choose USJ if you're:
- ✅ Building a web application
- ✅ Creating a Bible app
- ✅ Working with JSON data
- ✅ Developing modern digital tools

### Which version?

| If you need... | Choose... |
|----------------|-----------|
| Just the Bible text | **Standard** |
| Original language alignment | **Interlinear** |
| Greek/Hebrew word references | **Strong's** |
| Complete linguistic data | **Strong's Full** |

## 📋 What's Included

All files contain the complete Berean Standard Bible:
- ✅ All 66 books (39 Old Testament + 27 New Testament)
- ✅ Complete text with verses and chapters
- ✅ Section headings
- ✅ Cross-references
- ✅ Footnotes
- ✅ Poetry formatting
- ✅ Red letter (Jesus' words) markup

## 🔄 Updates

These files are automatically generated and kept up-to-date. The ZIP files are regenerated whenever the source files change.

## 📄 License & Copyright

### Bible Text - Public Domain

The **Berean Standard Bible text** is in the **Public Domain** and completely free of copyright restrictions. You are free to:
- ✅ Copy and distribute freely
- ✅ Modify and adapt as needed
- ✅ Use commercially without restriction
- ✅ Use in any project (software, publications, apps, etc.)
- ✅ Create derivative works

**No attribution required** (though appreciated).  
**No permission needed** to use in any context.

See [UNLICENSE](UNLICENSE) for the formal public domain dedication.

### Software Tools - MIT License

The conversion software and build tools in this repository are licensed under the [MIT License](LICENSE). This only applies to the Python scripts and tooling, not the Bible text itself.

### Summary

| Content | License | Use Freely? |
|---------|---------|-------------|
| **BSB Bible Text** | Public Domain | ✅ Yes - No restrictions |
| **Software Tools** | MIT | ✅ Yes - With attribution |

## 💻 For Developers

### Build Process & Workspace

The build system generates all ZIP files into the `/workspace` directory:
- **`/workspace/`** - Contains USFM ZIP files
- **`/workspace/usj/`** - Contains USJ ZIP files

The workspace directory is excluded from version control (via `.gitignore`) but all ZIP files from this directory are included in each GitHub release.

### Version Management

The current release version is tracked in the `VERSION` file at the root of the repository. Update this file when preparing a new release.

**Current Version:** 5.1

### Documentation

If you want to generate these files yourself or contribute to the conversion process, see:
- **[Developer Documentation](README_developer.md)** - Complete technical documentation
- **[ZIP Creation Guide](README_zips.md)** - How the ZIP files are generated
- **[Quick Start for Zips](QUICK_START_ZIPS.txt)** - Quick reference guide

The conversion tool is written in Python and can generate files in various formats with different options.

### Creating a Release

1. Update the `VERSION` file with the new version number
2. Run `make all` to generate all files and ZIP archives
3. All ZIP files in `/workspace/` and `/workspace/usj/` should be uploaded as release assets
4. Create a GitHub release tagged with the version number (e.g., `v5.1`)

## 🆘 Need Help?

- **Questions about formats?** Check the format-specific documentation in each directory
- **Problems with files?** Open an issue on GitHub
- **Want to contribute?** See [README_developer.md](README_developer.md)

## 🌟 About the Berean Standard Bible

The Berean Standard Bible (BSB) is a completely new translation based on the best available manuscripts and sources. It aims to be a trustworthy translation that is optimized for word-study and is committed to textual accuracy.

For more information about the BSB project, visit [bereanbible.com](https://bereanbible.com).

---

**Last Updated**: Auto-generated with each commit
**Total Files**: 528 Bible files + 8 ZIP archives
**Formats**: USFM 3.1 & USJ (JSON)
