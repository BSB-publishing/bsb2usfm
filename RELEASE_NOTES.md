# Release Notes Template

Use this template when creating a new release on GitHub.

## Version X.X

**Release Date:** YYYY-MM-DD

### Overview

This release contains the complete Berean Standard Bible (BSB) and the Majority Standard Bible (MSB) in USFM, USJ, and USX formats, with multiple variant versions for different use cases.

### What's Included

#### Berean Standard Bible (BSB) - Full Bible (66 books)

**USFM Format** (Universal Standard Format Markers):
- **BSB_usfm.zip** - Standard clean text
- **BSB_int_usfm.zip** - With original language reverse interlinear data
- **BSB_strongs_usfm.zip** - With Strong's numbers
- **BSB_full_strongs_usfm.zip** - Complete Strong's data with placeholders and brackets

**USJ Format** (Unified Scripture JSON):
- **BSB_usj.zip** - Standard clean text
- **BSB_int_usj.zip** - With original language reverse interlinear data
- **BSB_strongs_usj.zip** - With Strong's numbers
- **BSB_full_strongs_usj.zip** - Complete Strong's data with placeholders and brackets

**USX Format** (Unified Scripture XML):
- **BSB_usx.zip** - Standard clean text
- **BSB_int_usx.zip** - With original language reverse interlinear data
- **BSB_strongs_usx.zip** - With Strong's numbers
- **BSB_full_strongs_usx.zip** - Complete Strong's data with placeholders and brackets

#### Majority Standard Bible (MSB) - New Testament (27 books)

**USFM Format**:
- **MSB_usfm.zip** - Standard clean text
- **MSB_int_usfm.zip** - With original language reverse interlinear data
- **MSB_strongs_usfm.zip** - With Strong's numbers
- **MSB_full_strongs_usfm.zip** - Complete Strong's data with placeholders and brackets

**USJ Format**:
- **MSB_usj.zip** - Standard clean text
- **MSB_int_usj.zip** - With original language reverse interlinear data
- **MSB_strongs_usj.zip** - With Strong's numbers
- **MSB_full_strongs_usj.zip** - Complete Strong's data with placeholders and brackets

**USX Format**:
- **MSB_usx.zip** - Standard clean text
- **MSB_int_usx.zip** - With original language reverse interlinear data
- **MSB_strongs_usx.zip** - With Strong's numbers
- **MSB_full_strongs_usx.zip** - Complete Strong's data with placeholders and brackets

### Contents

**BSB** - All 66 books of the Bible:
- Old Testament: 39 books (GEN through MAL)
- New Testament: 27 books (MAT through REV)

**MSB** - New Testament only:
- 27 books (MAT through REV)

### Features

All files include:
- Complete text with verses and chapters
- Section headings
- Cross-references and parallel passage references
- Footnotes
- Poetry formatting
- Red letter markup (Jesus' words)
- Proper character encoding (UTF-8)

### Changes in This Release

<!-- Add specific changes for this release -->
- [Add specific details here]

### File Statistics

- **Total ZIP files:** 24 (12 BSB + 12 MSB)
- **BSB individual files:** 66 books x 4 variants x 3 formats
- **MSB individual files:** 27 books x 4 variants x 3 formats
- **Format versions:** USFM 3.1, USJ (JSON), USX 3.1

### Technical Details

#### USFM Format
- **Version:** USFM 3.1
- **Encoding:** UTF-8
- **Line endings:** Unix (LF)
- **Compatible with:** Paratext, PTXprint, and most Bible translation software

#### USJ Format
- **Specification:** Unified Scripture JSON
- **Encoding:** UTF-8
- **Compatible with:** Modern web apps, JavaScript libraries, JSON parsers

#### USX Format
- **Specification:** USX 3.1
- **Encoding:** UTF-8
- **Compatible with:** Digital Bible Library (DBL), Bible technology platforms

### Installation & Usage

#### For Bible Translation Software (USFM)
1. Download the appropriate USFM ZIP file
2. Extract to your Paratext/translation software projects folder
3. Open the project in your software

#### For Web/App Development (USJ)
1. Download the appropriate USJ ZIP file
2. Extract to your project directory
3. Import and parse the JSON files in your application

#### For Research/Study
- **Standard versions** - Clean, readable text
- **Interlinear versions** - See original language words aligned with English
- **Strong's versions** - Reference Greek/Hebrew word numbers
- **Full versions** - Complete linguistic data

### License

**Public Domain** - Both the Berean Standard Bible and Majority Standard Bible texts are completely free to use:
- Copy and distribute freely
- Modify and adapt as needed
- Use commercially without restriction
- Use in any project (software, publications, apps, etc.)
- Create derivative works

**No restrictions.** No attribution required (though appreciated). No permission needed.

Both texts are dedicated to the public domain. See [UNLICENSE](https://github.com/BSB-publishing/bsb2usfm/blob/main/UNLICENSE) for the formal dedication.

**Note:** The software tools in this repository are MIT licensed, but the Bible texts themselves are completely unrestricted.

### Support

- **Issues:** [GitHub Issues](https://github.com/BSB-publishing/bsb2usfm/issues)
- **Documentation:** See repository README
- **Questions:** Open a discussion on GitHub

### Links

- **Repository:** https://github.com/BSB-publishing/bsb2usfm
- **BSB Website:** https://bereanbible.com
- **MSB Website:** https://majoritybible.com
- **All Releases:** https://github.com/BSB-publishing/bsb2usfm/releases

### Acknowledgments

The Berean Standard Bible and Majority Standard Bible are produced by [Bible Hub](https://biblehub.com) and made freely available to the global community.
