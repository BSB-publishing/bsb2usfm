#!/bin/bash
# Manual GitHub Release Creation Script

set -e

VERSION=$(cat VERSION)
REPO="BSB-publishing/bsb2usfm"

echo "Creating release v${VERSION} manually..."

# Ensure all ZIP files exist
if [ ! -d "workspace" ]; then
    echo "Error: workspace directory not found. Run 'make all' first."
    exit 1
fi

ZIP_COUNT=$(find workspace -name "*.zip" | wc -l | tr -d ' ')
if [ "$ZIP_COUNT" -ne 12 ]; then
    echo "Error: Expected 12 ZIP files, found ${ZIP_COUNT}"
    exit 1
fi

echo "✓ Found ${ZIP_COUNT} ZIP files"
echo ""
echo "To create the release manually:"
echo ""
echo "1. Go to: https://github.com/${REPO}/releases/new"
echo ""
echo "2. Fill in:"
echo "   - Tag: v${VERSION} (should already exist)"
echo "   - Title: BSB v${VERSION}"
echo ""
echo "3. Copy this release description:"
echo ""
cat << 'RELEASE_NOTES'
# Berean Standard Bible v5.1

This release contains the complete Berean Standard Bible in both USFM and USJ formats.

## 📦 What's Included

### USFM Format (Universal Standard Format Markers)
- **BSB_usfm.zip** - Standard clean text
- **BSB_int_usfm.zip** - With interlinear data
- **BSB_strongs_usfm.zip** - With Strong's numbers
- **BSB_full_strongs_usfm.zip** - Complete Strong's data

### USJ Format (Unified Scripture JSON)
- **BSB_usj.zip** - Standard clean text
- **BSB_int_usj.zip** - With interlinear data
- **BSB_strongs_usj.zip** - With Strong's numbers
- **BSB_full_strongs_usj.zip** - Complete Strong's data

### USX Format (Unified Scripture XML)
- **BSB_usx.zip** - Standard clean text
- **BSB_int_usx.zip** - With interlinear data
- **BSB_strongs_usx.zip** - With Strong's numbers
- **BSB_full_strongs_usx.zip** - Complete Strong's data

## 📖 Contents

Each ZIP file contains all 66 books of the Bible (39 OT + 27 NT) with:
- Complete text with verses and chapters
- Section headings
- Cross-references
- Footnotes
- Poetry formatting
- Red letter (Jesus' words) markup

## 🆕 What's New in v5.1

- New workspace-based build system
- Automated GitHub release workflow
- Version tracking via VERSION file
- All ZIP files organized in unified structure

## 📄 License

Public Domain - Free to use for any purpose.

## 🔗 More Information

Visit the [repository](https://github.com/BSB-publishing/bsb2usfm) for more details.
RELEASE_NOTES

echo ""
echo "4. Upload these 12 ZIP files as release assets:"
echo ""
find workspace -name "*.zip" -exec ls -lh {} \; | awk '{printf "   - %s (%s)\n", $9, $5}'
echo ""
echo "5. Click 'Publish release'"
echo ""
