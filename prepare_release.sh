#!/bin/bash
# Release Preparation Script
# This script prepares all files for a GitHub release

set -e  # Exit on error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print colored message
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

print_header() {
    echo ""
    echo "============================================================"
    echo "$1"
    echo "============================================================"
}

# Check if VERSION file exists
if [ ! -f "VERSION" ]; then
    print_error "VERSION file not found!"
    exit 1
fi

# Read version
VERSION=$(cat VERSION | tr -d '[:space:]')
print_header "Preparing Release v${VERSION}"

print_info "Current version: ${VERSION}"

# Confirm with user
read -p "$(echo -e ${YELLOW}Continue with release preparation? [y/N]:${NC} )" -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    print_warning "Release preparation cancelled."
    exit 0
fi

# Step 1: Clean previous builds
print_header "Step 1: Cleaning Previous Builds"
print_info "Removing old workspace files..."
make clean
print_success "Clean complete"

# Step 2: Build all files
print_header "Step 2: Building All Files"
print_info "Generating USFM and USJ files..."
make all
print_success "Build complete"

# Step 3: Verify workspace
print_header "Step 3: Verifying Workspace"

if [ ! -d "workspace" ]; then
    print_error "Workspace directory not found!"
    exit 1
fi

# Count and list ZIP files
USFM_ZIPS=$(find workspace -maxdepth 2 -name "*.zip" -not -path "*/usj/*" -not -path "*/usx/*" | wc -l | tr -d ' ')
USJ_ZIPS=$(find workspace/usj -name "*.zip" 2>/dev/null | wc -l | tr -d ' ')
USX_ZIPS=$(find workspace/usx -name "*.zip" 2>/dev/null | wc -l | tr -d ' ')
TOTAL_ZIPS=$((USFM_ZIPS + USJ_ZIPS + USX_ZIPS))

print_info "Found ${USFM_ZIPS} USFM ZIP files"
print_info "Found ${USJ_ZIPS} USJ ZIP files"
print_info "Found ${USX_ZIPS} USX ZIP files"
print_info "Total: ${TOTAL_ZIPS} ZIP files"

if [ "$TOTAL_ZIPS" -ne 12 ]; then
    print_error "Expected 12 ZIP files, found ${TOTAL_ZIPS}!"
    exit 1
fi

print_success "All ZIP files present"

# List all ZIP files with sizes
print_info "ZIP files in workspace:"
echo ""
find workspace -name "*.zip" -exec ls -lh {} \; | awk '{print "  " $9 " - " $5}'

# Step 4: Verify file contents
print_header "Step 4: Verifying File Contents"

verify_zip() {
    local zip_file=$1
    local expected_count=66
    local actual_count=$(unzip -l "$zip_file" | grep -E '\.(usfm|usj|usx)$' | wc -l | tr -d ' ')

    if [ "$actual_count" -eq "$expected_count" ]; then
        print_success "$(basename $zip_file): ${actual_count} files ✓"
        return 0
    else
        print_error "$(basename $zip_file): Expected ${expected_count}, found ${actual_count}"
        return 1
    fi
}

all_verified=true
for zip_file in $(find workspace -name "*.zip" | sort); do
    if ! verify_zip "$zip_file"; then
        all_verified=false
    fi
done

if [ "$all_verified" = false ]; then
    print_error "Some ZIP files failed verification!"
    exit 1
fi

print_success "All ZIP files verified"

# Step 5: Calculate checksums
print_header "Step 5: Generating Checksums"

CHECKSUM_FILE="workspace/SHA256SUMS.txt"
print_info "Generating SHA256 checksums..."

cd workspace
find . -name "*.zip" -type f -exec sha256sum {} \; | sort > SHA256SUMS.txt
cd ..

print_success "Checksums saved to ${CHECKSUM_FILE}"
echo ""
cat "$CHECKSUM_FILE"

# Step 6: Display summary
print_header "Release Summary"

echo ""
print_info "Version: ${VERSION}"
print_info "Total ZIP files: ${TOTAL_ZIPS}"
print_info "Workspace directory: workspace/"
print_info "Checksums: workspace/SHA256SUMS.txt"
echo ""

# Calculate total size
total_size=$(du -sh workspace | awk '{print $1}')
print_info "Total workspace size: ${total_size}"

# Step 7: Next steps
print_header "Next Steps"

echo ""
echo "To create a GitHub release:"
echo ""
echo "  1. Commit any changes:"
echo "     git add -A"
echo "     git commit -m \"Prepare release v${VERSION}\""
echo ""
echo "  2. Create and push a tag:"
echo "     git tag -a v${VERSION} -m \"Release v${VERSION}\""
echo "     git push origin v${VERSION}"
echo ""
echo "  3. The GitHub Actions workflow will automatically:"
echo "     - Build all files"
echo "     - Create the release"
echo "     - Upload all ZIP files as release assets"
echo ""
echo "  OR manually create a release on GitHub:"
echo "     https://github.com/YOUR_USERNAME/bsb2usfm/releases/new"
echo "     - Tag: v${VERSION}"
echo "     - Upload all ZIP files from workspace/"
echo ""

print_success "Release preparation complete!"
print_info "All files are ready in the workspace/ directory"
