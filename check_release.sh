#!/bin/bash
# Check GitHub Release Status and Provide Instructions

set -e

REPO="BSB-publishing/bsb2usfm"
VERSION=$(cat VERSION 2>/dev/null || echo "5.1")
TAG="v${VERSION}"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

print_header() {
    echo ""
    echo -e "${BLUE}============================================================${NC}"
    echo -e "${CYAN}$1${NC}"
    echo -e "${BLUE}============================================================${NC}"
    echo ""
}

print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_header "GitHub Release Status Checker"

print_info "Repository: ${REPO}"
print_info "Version: ${VERSION}"
print_info "Tag: ${TAG}"

echo ""
echo "Checking release status..."
echo ""

# Check if release exists
RELEASE_URL="https://github.com/${REPO}/releases/tag/${TAG}"
ACTIONS_URL="https://github.com/${REPO}/actions"

print_info "Checking URLs:"
echo "  Release: ${RELEASE_URL}"
echo "  Actions: ${ACTIONS_URL}"

echo ""
print_header "Step 1: Check GitHub Actions"

echo "1. Visit: ${ACTIONS_URL}"
echo ""
echo "2. Look for the 'Create Release' workflow run"
echo ""
echo "3. Check the status:"
echo "   ${GREEN}✓ Green checkmark${NC} - Success! Release should be created"
echo "   ${YELLOW}⚙ Yellow circle${NC} - In progress, wait for it to complete"
echo "   ${RED}✗ Red X${NC} - Failed, see steps below to fix"
echo ""

print_header "Step 2: Check Release Page"

echo "Visit: ${RELEASE_URL}"
echo ""
echo "If the release exists, you're done! ✓"
echo ""

print_header "Step 3: If GitHub Actions Failed"

echo "Check the error message in the Actions log."
echo ""
echo "Common issues and fixes:"
echo ""
echo "1. ${YELLOW}Python/dependency errors:${NC}"
echo "   - Already fixed in latest commit"
echo "   - Workflow should work on next run"
echo ""
echo "2. ${YELLOW}Permission errors:${NC}"
echo "   - Go to: Settings → Actions → General"
echo "   - Under 'Workflow permissions', select:"
echo "     'Read and write permissions'"
echo "   - Save and re-run the workflow"
echo ""
echo "3. ${YELLOW}Build errors:${NC}"
echo "   - Check that all source files exist"
echo "   - Verify requirements.txt is complete"
echo ""

print_header "Step 4: Manual Release (Fallback)"

echo "If GitHub Actions continues to fail, create the release manually:"
echo ""
echo "1. Visit: https://github.com/${REPO}/releases/new"
echo ""
echo "2. Fill in:"
echo "   Tag: ${TAG}"
echo "   Title: BSB ${TAG}"
echo ""
echo "3. Upload these 8 ZIP files from workspace/:"
echo ""

if [ -d "workspace" ]; then
    ZIP_COUNT=$(find workspace -name "*.zip" 2>/dev/null | wc -l | tr -d ' ')
    if [ "$ZIP_COUNT" -eq 8 ]; then
        print_success "All 8 ZIP files found in workspace/"
        echo ""
        find workspace -name "*.zip" -exec ls -lh {} \; | awk '{printf "   %-50s %8s\n", $9, $5}'
    else
        print_error "Expected 8 ZIP files, found ${ZIP_COUNT}"
        echo ""
        echo "   Run: make clean && make all"
    fi
else
    print_warning "Workspace directory not found"
    echo ""
    echo "   Run: make all"
fi

echo ""
echo "4. Copy this release description:"
echo ""
echo "${CYAN}─────────────────────────────────────────────────────────${NC}"
cat << 'RELEASE_DESC'
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
RELEASE_DESC
echo "${CYAN}─────────────────────────────────────────────────────────${NC}"

echo ""
echo "5. Click 'Publish release'"
echo ""

print_header "Quick Commands"

echo "Rebuild everything:"
echo "  ${CYAN}make clean && make all${NC}"
echo ""
echo "Verify workspace:"
echo "  ${CYAN}find workspace -name '*.zip' | wc -l${NC}"
echo "  (should output: 8)"
echo ""
echo "Check each ZIP file:"
echo "  ${CYAN}for zip in \$(find workspace -name '*.zip'); do unzip -l \"\$zip\" | grep -E '\.(usfm|usj)\$' | wc -l; done${NC}"
echo "  (each should output: 66)"
echo ""

print_header "Summary"

print_info "Current status:"
echo "  • Tag ${TAG} is pushed to GitHub"
echo "  • GitHub Actions should be running or completed"
echo "  • Check ${ACTIONS_URL}"
echo ""

print_info "Next steps:"
echo "  1. Check GitHub Actions status"
echo "  2. Verify release at ${RELEASE_URL}"
echo "  3. If needed, create release manually using instructions above"
echo ""

print_success "All instructions provided above!"
echo ""
