#!/bin/bash

# BSB to USFM Converter - Quick Start
# This script provides the fastest way to get started

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_header() {
    clear
    echo ""
    echo "🚀 BSB to USFM Converter - Quick Start"
    echo "======================================"
    echo ""
}

print_step() {
    echo -e "${BLUE}▶${NC} $1"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_info() {
    echo -e "${YELLOW}ℹ${NC} $1"
}

main() {
    print_header

    # Get script directory
    cd "$(dirname "${BASH_SOURCE[0]}")"

    print_step "Checking setup..."

    # Quick setup check
    if [ ! -d "venv" ] || [ ! -f "web/app.py" ]; then
        print_info "Running first-time setup..."
        ./setup_web.sh
    else
        print_success "Setup already complete"
    fi

    # Check BSB data
    if [ ! -f "data/bsb_tables.csv" ]; then
        print_info "BSB tables file not found at data/bsb_tables.csv"
        echo "Please ensure the BSB data file is in the correct location."
        exit 1
    fi

    print_success "BSB data file found"
    echo ""

    print_step "Starting web interface..."
    print_info "The web interface will be available at: http://localhost:5000"
    print_info "Press Ctrl+C to stop the server when finished"
    echo ""

    read -p "Press Enter to start the web server..."

    # Start web server
    ./run_web.py
}

# Handle arguments
case "${1:-}" in
    --help|-h)
        echo "BSB to USFM Quick Start"
        echo ""
        echo "Usage: $0"
        echo ""
        echo "This script:"
        echo "  1. Checks if setup is complete (runs setup if needed)"
        echo "  2. Verifies BSB data is available"
        echo "  3. Starts the web interface"
        echo ""
        exit 0
        ;;
    *)
        main
        ;;
esac
