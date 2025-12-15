# Release Notes Template

Use this template when creating a new release on GitHub.

## Version X.X

**Release Date:** YYYY-MM-DD

### Overview

This release contains the complete Berean Standard Bible in both USFM and USJ formats, with multiple variant versions for different use cases.

### 📦 What's Included

#### USFM Format (Universal Standard Format Markers)
Standard format used by Paratext, PTXprint, and most Bible translation software.

- **BSB_usfm.zip** - Standard clean text (66 books)
- **BSB_int_usfm.zip** - With original language reverse interlinear data (66 books)
- **BSB_strongs_usfm.zip** - With Strong's numbers (66 books)
- **BSB_full_strongs_usfm.zip** - Complete Strong's data with placeholders and brackets (66 books)

#### USJ Format (Unified Scripture JSON)
Modern JSON-based format for web applications and digital platforms.

- **BSB_usj.zip** - Standard clean text (66 books)
- **BSB_int_usj.zip** - With original language reverse interlinear data (66 books)
- **BSB_strongs_usj.zip** - With Strong's numbers (66 books)
- **BSB_full_strongs_usj.zip** - Complete Strong's data with placeholders and brackets (66 books)

### 📖 Contents

Each ZIP file contains all 66 books of the Bible:
- **Old Testament:** 39 books (GEN through MAL)
- **New Testament:** 27 books (MAT through REV)

### ✨ Features

All files include:
- ✅ Complete text with verses and chapters
- ✅ Section headings
- ✅ Cross-references
- ✅ Footnotes
- ✅ Poetry formatting
- ✅ Red letter markup (Jesus' words)
- ✅ Proper character encoding (UTF-8)

### 🔄 Changes in This Release

<!-- Add specific changes for this release -->
- Initial release / updates / bug fixes / improvements
- [Add specific details here]

### 📊 File Statistics

- **Total ZIP files:** 8
- **Total individual files:** 528 (66 books × 8 variants)
- **Format versions:** USFM 3.1, USJ (JSON)
- **Total size:** ~XX MB (combined)

### 🛠️ Technical Details

#### USFM Format
- **Version:** USFM 3.1
- **Encoding:** UTF-8
- **Line endings:** Unix (LF)
- **Compatible with:** Paratext, PTXprint, and most Bible translation software

#### USJ Format
- **Specification:** Unified Scripture JSON
- **Encoding:** UTF-8
- **Schema compliant:** Yes
- **Compatible with:** Modern web apps, JavaScript libraries, JSON parsers

### 📥 Installation & Usage

#### For Bible Translation Software (USFM)
1. Download the appropriate USFM ZIP file
2. Extract to your Paratext/translation software projects folder
3. Open the project in your software

#### For Web/App Development (USJ)
1. Download the appropriate USJ ZIP file
2. Extract to your project directory
3. Import and parse the JSON files in your application

```javascript
// Example: Loading a book in JavaScript
const book = require('./GEN.usj');
console.log(book.content);
```

#### For Research/Study
- **Standard versions** - Clean, readable text
- **Interlinear versions** - See original language words aligned with English
- **Strong's versions** - Reference Greek/Hebrew word numbers
- **Full versions** - Complete linguistic data

### 🔒 Verification

SHA256 checksums are provided in `SHA256SUMS.txt` (included with release assets).

To verify a download:
```bash
sha256sum -c SHA256SUMS.txt
```

### 📄 License

**Public Domain** - The Berean Standard Bible text is completely free to use:
- ✅ Copy and distribute freely
- ✅ Modify and adapt as needed
- ✅ Use commercially without restriction
- ✅ Use in any project (software, publications, apps, etc.)
- ✅ Create derivative works

**No restrictions.** No attribution required (though appreciated). No permission needed.

The BSB text is dedicated to the public domain. See [UNLICENSE](https://github.com/BSB-publishing/bsb2usfm/blob/main/UNLICENSE) for the formal dedication.

**Note:** The software tools in this repository are MIT licensed, but the Bible text itself is completely unrestricted.

### 🆘 Support

- **Issues:** [GitHub Issues](https://github.com/YOUR_USERNAME/bsb2usfm/issues)
- **Documentation:** See repository README
- **Questions:** Open a discussion on GitHub

### 🔗 Links

- **Repository:** https://github.com/YOUR_USERNAME/bsb2usfm
- **BSB Website:** https://bereanbible.com
- **All Releases:** https://github.com/YOUR_USERNAME/bsb2usfm/releases

### 🙏 Acknowledgments

The Berean Standard Bible is produced by [Bible Hub](https://biblehub.com) and made freely available to the global community.

---

**Release prepared on:** [Auto-generated]
**Build system:** Automated via GitHub Actions