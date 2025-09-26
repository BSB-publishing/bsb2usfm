#!/bin/bash

# Getting Started with BSB to USFM Converter
# This script helps you get started with the BSB to USFM converter

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# Function to print colored output
print_title() {
    echo -e "${PURPLE}$1${NC}"
}

print_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_info() {
    echo -e "${YELLOW}[INFO]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Main header
print_header() {
    clear
    echo ""
    echo "################################################################"
    echo "#                                                              #"
    echo "#           BSB to USFM Converter - Getting Started           #"
    echo "#                                                              #"
    echo "################################################################"
    echo ""
    print_title "🚀 Welcome to the BSB to USFM Converter!"
    echo ""
    echo "This interactive guide will help you set up and use the converter."
    echo ""
}

# Check if setup is complete
check_setup() {
    print_step "Checking if setup is complete..."

    if [ ! -d "venv" ]; then
        print_error "Virtual environment not found. Running setup..."
        if [ -f "setup_web.sh" ]; then
            ./setup_web.sh
        else
            print_error "setup_web.sh not found. Please run setup manually."
            exit 1
        fi
    else
        print_success "Virtual environment found"
    fi

    if [ ! -f "web/app.py" ]; then
        print_error "Web application not found. Please ensure all files are present."
        exit 1
    else
        print_success "Web application found"
    fi

    # Check if demo data exists
    if [ ! -d "demo_data" ]; then
        print_info "Demo data not found. Creating demo data..."
        python3 create_demo_data.py
    else
        print_success "Demo data found"
    fi
}

# Show available options
show_options() {
    echo ""
    print_title "📋 What would you like to do?"
    echo ""
    echo "1) 🌐 Start Web Interface (Recommended for beginners)"
    echo "2) 💻 Use Command Line Interface"
    echo "3) 🧪 Run Demo Conversion"
    echo "4) 📚 View Documentation"
    echo "5) 🔧 Run Setup/Diagnostics"
    echo "6) ❌ Exit"
    echo ""
}

# Start web interface
start_web_interface() {
    print_step "Starting web interface..."
    echo ""
    print_success "Web interface will start at: http://localhost:5000"
    print_info "You can use the demo data files in the 'demo_data' folder"
    print_info "Press Ctrl+C to stop the web server when you're done"
    echo ""
    read -p "Press Enter to start the web server..."

    # Start the web server
    ./run_web.py
}

# Command line interface demo
show_cli_usage() {
    print_step "Command Line Interface Usage"
    echo ""
    echo "Basic conversion (using fixed BSB data):"
    echo "  python3 bsb2usfm.py data/bsb_tables.csv -o output_%.usfm"
    echo ""
    echo "With optional customization files:"
    echo "  python3 bsb2usfm.py data/bsb_tables.csv \\"
    echo "    -o output_%.usfm \\"
    echo "    -f footnotes.tsv \\"
    echo "    -n BookNames.xml"
    echo ""
    echo "Convert specific books only:"
    echo "  python3 bsb2usfm.py data/bsb_tables.csv -o output_%.usfm \\"
    echo "    -b GEN -b EXO -b MAT -b JHN"
    echo ""

    read -p "Would you like to try the CLI with the BSB data? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        run_cli_demo
    fi
}

# Run CLI demo
run_cli_demo() {
    print_step "Running CLI demo conversion..."

    if [ ! -f "data/bsb_tables.csv" ]; then
        print_error "BSB tables file not found at data/bsb_tables.csv"
        return 1
    fi

    # Ensure demo customization files exist
    if [ ! -d "demo_data" ]; then
        print_info "Creating demo customization files..."
        python3 create_demo_data.py
    fi

    echo ""
    print_info "Converting sample books from BSB data with optional customization files..."
    echo ""

    # Activate virtual environment and run conversion
    source venv/bin/activate
    python3 bsb2usfm.py data/bsb_tables.csv \
        -o demo_cli_%.usfm \
        -f demo_data/sample_footnotes.tsv \
        -n demo_data/sample_book_names.xml \
        -b GEN -b MAT -b JHN

    echo ""
    print_success "Conversion completed! Generated files:"
    ls -la demo_cli_*.usfm 2>/dev/null || echo "No output files found."
    echo ""

    read -p "Would you like to view a generated USFM file? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        if [ -f "demo_cli_GEN.usfm" ]; then
            echo ""
            print_info "Contents of demo_cli_GEN.usfm:"
            echo "----------------------------------------"
            cat demo_cli_GEN.usfm
            echo ""
            echo "----------------------------------------"
        fi
    fi
}

# Run complete demo
run_demo_conversion() {
    print_step "Running complete demo conversion..."

    # Ensure demo data exists
    if [ ! -d "demo_data" ]; then
        print_info "Creating demo data..."
        python3 create_demo_data.py
    fi

    echo ""
    print_info "The converter uses the complete BSB tables file:"
    echo "  📄 data/bsb_tables.csv - Complete Berean Study Bible data"
    echo ""
    print_info "Optional demo files available:"
    echo "  📝 demo_data/sample_footnotes.tsv - Footnote styling rules"
    echo "  📚 demo_data/sample_book_names.xml - Custom book names"
    echo ""

    print_info "This will convert from the complete BSB dataset (all 66 books available)"
    echo ""

    read -p "Continue with demo conversion? (Y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Nn]$ ]]; then
        # Clean up previous demo files
        rm -f demo_*.usfm

        # Run conversion with the fixed BSB tables file
        source venv/bin/activate
        python3 bsb2usfm.py data/bsb_tables.csv \
            -o demo_%.usfm \
            -f demo_data/sample_footnotes.tsv \
            -n demo_data/sample_book_names.xml \
            -b GEN -b EXO -b MAT -b JHN -b REV

        echo ""
        print_success "Demo conversion completed!"
        echo ""
        print_info "Generated files:"
        ls -la demo_*.usfm
        echo ""

        # Show sample output
        if [ -f "demo_GEN.usfm" ]; then
            echo ""
            print_info "Sample output (Genesis):"
            echo "========================"
            head -15 demo_GEN.usfm
            echo "========================"
            echo ""
        fi
    fi
}

# Show documentation
show_documentation() {
    print_step "Documentation and Help"
    echo ""

    if [ -f "README.md" ]; then
        print_info "Main README.md file contains comprehensive documentation"
    fi

    if [ -f "web/README.md" ]; then
        print_info "Web interface documentation: web/README.md"
    fi

    if [ -f "demo_data/README.md" ]; then
        print_info "Demo data documentation: demo_data/README.md"
    fi

    echo ""
    print_info "Key file formats:"
    echo ""
    echo "  📋 BSB Tables: Complete Berean Study Bible data (fixed file: data/bsb_tables.csv)"
    echo "     - Contains all 66 books with Hebrew/Greek parsing, cross-references, footnotes"
    echo ""
    echo "  📝 Footnotes: Tab-separated values (TSV) with verse references and styles"
    echo "     - Format: VerseRef<tab>Style1<tab>Style2<tab>..."
    echo ""
    echo "  📚 Book Names: XML format with book codes and names"
    echo "     - Format: <book code=\"GEN\" long=\"Genesis\" short=\"Gen\" abbr=\"Gn\"/>"
    echo ""
    echo "  📖 Output: USFM files (Unified Standard Format Markers)"
    echo "     - Standard format for Bible translation software"
    echo ""

    read -p "Would you like to view the main README? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        if command -v less &> /dev/null; then
            less README.md
        elif command -v more &> /dev/null; then
            more README.md
        else
            cat README.md
        fi
    fi
}

# Run diagnostics
run_diagnostics() {
    print_step "Running setup and diagnostics..."
    echo ""

    if [ -f "setup_web.sh" ]; then
        ./setup_web.sh --test
    else
        print_error "setup_web.sh not found"
    fi

    echo ""
    print_step "Checking Python environment..."

    if [ -d "venv" ]; then
        source venv/bin/activate
        echo "Python version: $(python3 --version)"
        echo "Pip version: $(pip --version)"

        print_info "Checking required modules..."
        python3 -c "
import sys
modules = ['flask', 'usfmtc', 'regex']
missing = []
for module in modules:
    try:
        __import__(module)
        print(f'✓ {module}')
    except ImportError:
        print(f'✗ {module}')
        missing.append(module)

if missing:
    print(f'Missing modules: {missing}')
    sys.exit(1)
else:
    print('All required modules are available')
"
    else
        print_error "Virtual environment not found. Run setup first."
    fi

    echo ""
    print_step "File permissions check..."
    chmod +x run_web.py setup_web.sh create_demo_data.py getting_started.sh 2>/dev/null || true

    if [ -d "web" ]; then
        if [ -w "web/uploads" ] && [ -w "web/outputs" ]; then
            print_success "Web directories have correct permissions"
        else
            print_info "Setting web directory permissions..."
            chmod 755 web/uploads web/outputs 2>/dev/null || true
        fi
    fi

    print_success "Diagnostics completed"
}

# Main menu loop
main_loop() {
    while true; do
        show_options
        read -p "Please choose an option (1-6): " choice
        echo ""

        case $choice in
            1)
                start_web_interface
                ;;
            2)
                show_cli_usage
                ;;
            3)
                run_demo_conversion
                ;;
            4)
                show_documentation
                ;;
            5)
                run_diagnostics
                ;;
            6)
                print_success "Thank you for using BSB to USFM Converter!"
                exit 0
                ;;
            *)
                print_error "Invalid option. Please choose 1-6."
                ;;
        esac

        echo ""
        read -p "Press Enter to continue..."
        clear
        print_header
    done
}

# Main execution
main() {
    # Change to script directory
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    cd "$SCRIPT_DIR"

    print_header
    check_setup
    main_loop
}

# Handle script arguments
case "${1:-}" in
    --help|-h)
        echo "BSB to USFM Converter - Getting Started Guide"
        echo ""
        echo "Usage: $0 [OPTIONS]"
        echo ""
        echo "Options:"
        echo "  --help, -h      Show this help message"
        echo "  --web          Start web interface directly"
        echo "  --demo         Run demo conversion"
        echo "  --setup        Run setup and diagnostics"
        echo ""
        echo "Interactive mode (no options):"
        echo "  Provides a menu-driven interface for all features"
        echo ""
        exit 0
        ;;
    --web)
        check_setup
        start_web_interface
        ;;
    --demo)
        check_setup
        run_demo_conversion
        ;;
    --setup)
        run_diagnostics
        ;;
    "")
        main
        ;;
    *)
        print_error "Unknown option: $1"
        echo "Use --help for usage information"
        exit 1
        ;;
esac
