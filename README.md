# Berean Standard Bible & Majority Standard Bible - USFM, USJ & USX Files

[![License: Public Domain](https://img.shields.io/badge/License-Public%20Domain-brightgreen.svg)](UNLICENSE)
[![Bible Version](https://img.shields.io/badge/BSB-v5.1-blue.svg)](https://github.com/BSB-publishing/bsb2usfm/releases)

Welcome! This repository provides the **Berean Standard Bible (BSB)** and the **Majority Standard Bible (MSB)** in multiple digital formats for Bible software, apps, and translation projects.

> **📄 License:** The Bible text is in the **Public Domain** - completely free to use, modify, and distribute for any purpose. See [LICENSE](LICENSE) and [UNLICENSE](UNLICENSE) for details.

## Editions

This repository builds two editions:

| Edition | Identifier | Scope | Source |
|---------|-----------|-------|--------|
| **Berean Standard Bible** | BSB | Full Bible (66 books) | [bereanbible.com](https://bereanbible.com) |
| **Majority Standard Bible** | MSB | New Testament (27 books) | [majoritybible.com](https://majoritybible.com) |

Each edition is built into its own directory (`bereanbible/` or `majoritybible/`) with identical internal structure.

## 🚀 GitHub Releases

**Current Version: 5.1**

The recommended way to download the complete dataset is through our **[GitHub Releases](../../releases/latest)**. Each release includes ZIP files for both editions in USFM, USJ, and USX formats.

### Release Assets (per edition)

Each edition includes ZIP files in 3 formats × 4 variants:

**USFM Format:**
- `BSB_usfm.zip` / `MSB_usfm.zip` - Standard clean text
- `BSB_int_usfm.zip` / `MSB_int_usfm.zip` - With interlinear data
- `BSB_strongs_usfm.zip` / `MSB_strongs_usfm.zip` - With Strong's numbers
- `BSB_full_strongs_usfm.zip` / `MSB_full_strongs_usfm.zip` - Complete Strong's data

**USJ Format:**
- `BSB_usj.zip` / `MSB_usj.zip` - Standard clean text
- `BSB_int_usj.zip` / `MSB_int_usj.zip` - With interlinear data
- `BSB_strongs_usj.zip` / `MSB_strongs_usj.zip` - With Strong's numbers
- `BSB_full_strongs_usj.zip` / `MSB_full_strongs_usj.zip` - Complete Strong's data

**USX Format:**
- `BSB_usx.zip` / `MSB_usx.zip` - Standard clean text
- *(plus interlinear, strongs, and strongs_full variants)*

All release files are automatically generated and stored in each edition's `workspace/` directory during the build process.

## 📖 Book Codes Reference

Each file is named with a standard 3-letter book code:

**Old Testament** (BSB only): GEN, EXO, LEV, NUM, DEU, JOS, JDG, RUT, 1SA, 2SA, 1KI, 2KI, 1CH, 2CH, EZR, NEH, EST, JOB, PSA, PRO, ECC, SNG, ISA, JER, LAM, EZK, DAN, HOS, JOL, AMO, OBA, JON, MIC, NAM, HAB, ZEP, HAG, ZEC, MAL

**New Testament** (BSB and MSB): MAT, MRK, LUK, JHN, ACT, ROM, 1CO, 2CO, GAL, EPH, PHP, COL, 1TH, 2TH, 1TI, 2TI, TIT, PHM, HEB, JAS, 1PE, 2PE, 1JN, 2JN, 3JN, JUD, REV

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

**BSB** files contain the complete Berean Standard Bible:
- ✅ All 66 books (39 Old Testament + 27 New Testament)

**MSB** files contain the Majority Standard Bible New Testament:
- ✅ All 27 New Testament books

Both editions include:
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

The **Berean Standard Bible** and **Majority Standard Bible** text is in the **Public Domain** and completely free of copyright restrictions. You are free to:
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
| **Bible Text** | Public Domain | ✅ Yes - No restrictions |
| **Software Tools** | MIT | ✅ Yes - With attribution |

## 💻 For Developers

### Build Process & Workspace

The build system generates all files into edition-specific directories:
- **`bereanbible/workspace/`** - BSB ZIP files (USFM, USJ, USX variants)
- **`majoritybible/workspace/`** - MSB ZIP files (USFM, USJ, USX variants)

The workspace directories are excluded from version control (via `.gitignore`) but all ZIP files are included in each GitHub release.

### Version Management

The current release version is tracked in the `VERSION` file at the root of the repository. Update this file when preparing a new release.

**Current Version:** 5.1

### Documentation

If you want to generate these files yourself or contribute to the conversion process, see:
- **[Developer Documentation](README_developer.md)** - Complete technical documentation
- **[ZIP Creation Guide](README_zips.md)** - How the ZIP files are generated
- **[Setup Guide](SETUP.md)** - Development environment setup

The conversion tool is written in Python and can generate files in various formats with different options.

### Creating a Release

1. Update the `VERSION` file with the new version number
2. Run `make all` to generate all files and ZIP archives for both editions
3. All ZIP files in `bereanbible/workspace/` and `majoritybible/workspace/` should be uploaded as release assets
4. Create a GitHub release tagged with the version number (e.g., `v5.1`)

## 🆘 Need Help?

- **Questions about formats?** Check the format-specific documentation in each directory
- **Problems with files?** Open an issue on GitHub
- **Want to contribute?** See [README_developer.md](README_developer.md)

For more information about the BSB project, visit [bereanbible.com](https://bereanbible.com).

---

**Last Updated**: Auto-generated with each commit
**Formats**: USFM 3.1, USJ (JSON), USX (XML)
