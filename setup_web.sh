#!/bin/bash

# BSB to USFM Web Interface Setup Script
# This script sets up the web interface for the BSB to USFM converter

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo ""
    echo "=================================================="
    echo "  BSB to USFM Web Interface Setup"
    echo "=================================================="
    echo ""
}

# Check if Python 3 is installed
check_python() {
    print_status "Checking Python installation..."

    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2)
        print_success "Python 3 found: $PYTHON_VERSION"
    else
        print_error "Python 3 is not installed. Please install Python 3.8 or higher."
        exit 1
    fi

    # Check Python version (minimum 3.8)
    PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d'.' -f1)
    PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d'.' -f2)

    if [[ $PYTHON_MAJOR -lt 3 ]] || [[ $PYTHON_MAJOR -eq 3 && $PYTHON_MINOR -lt 8 ]]; then
        print_error "Python 3.8 or higher is required. Found: $PYTHON_VERSION"
        exit 1
    fi
}

# Check if pip is installed
check_pip() {
    print_status "Checking pip installation..."

    if command -v pip3 &> /dev/null; then
        print_success "pip3 found"
    elif command -v pip &> /dev/null; then
        print_success "pip found"
    else
        print_error "pip is not installed. Please install pip first."
        exit 1
    fi
}

# Create virtual environment
setup_venv() {
    print_status "Setting up virtual environment..."

    if [ -d "venv" ]; then
        print_warning "Virtual environment already exists. Removing it..."
        rm -rf venv
    fi

    python3 -m venv venv
    print_success "Virtual environment created"

    # Activate virtual environment
    source venv/bin/activate
    print_success "Virtual environment activated"

    # Upgrade pip
    print_status "Upgrading pip..."
    pip install --upgrade pip
}

# Install dependencies
install_dependencies() {
    print_status "Installing Python dependencies..."

    # Make sure we're in the virtual environment
    if [[ "$VIRTUAL_ENV" == "" ]]; then
        print_error "Virtual environment not activated"
        exit 1
    fi

    # Install dependencies
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt
        print_success "Dependencies installed from requirements.txt"
    else
        # Install manually if requirements.txt doesn't exist
        print_warning "requirements.txt not found. Installing dependencies manually..."
        pip install Flask==3.1.2
        pip install usfmtc==0.3.16
        pip install regex
        print_success "Dependencies installed manually"
    fi
}

# Create necessary directories
setup_directories() {
    print_status "Creating necessary directories..."

    # Web directories
    mkdir -p web/uploads
    mkdir -p web/outputs
    mkdir -p web/static
    mkdir -p web/templates

    # Set appropriate permissions
    chmod 755 web/uploads
    chmod 755 web/outputs

    print_success "Directories created with proper permissions"
}

# Check if all required files exist
check_files() {
    print_status "Checking required files..."

    REQUIRED_FILES=(
        "bsb2usfm.py"
        "web/app.py"
        "web/templates/index.html"
        "web/templates/result.html"
        "run_web.py"
    )

    MISSING_FILES=()

    for file in "${REQUIRED_FILES[@]}"; do
        if [ ! -f "$file" ]; then
            MISSING_FILES+=("$file")
        fi
    done

    if [ ${#MISSING_FILES[@]} -gt 0 ]; then
        print_error "Missing required files:"
        for file in "${MISSING_FILES[@]}"; do
            echo "  - $file"
        done
        exit 1
    fi

    print_success "All required files found"
}

# Test the installation
test_installation() {
    print_status "Testing installation..."

    # Test import of main modules
    python3 -c "
import sys
sys.path.append('.')
try:
    import flask
    import usfmtc
    import regex
    print('✓ All Python modules imported successfully')
except ImportError as e:
    print('✗ Import error:', e)
    sys.exit(1)
"

    # Test Flask app loads
    cd web
    python3 -c "
try:
    import app
    print('✓ Flask application loads successfully')
except Exception as e:
    print('✗ Flask app error:', e)
    import sys
    sys.exit(1)
"
    cd ..

    print_success "Installation test passed"
}

# Make scripts executable
setup_permissions() {
    print_status "Setting up script permissions..."

    chmod +x run_web.py
    chmod +x setup_web.sh

    print_success "Script permissions set"
}

# Create a simple systemd service file (optional)
create_service_file() {
    print_status "Creating systemd service file (optional)..."

    SERVICE_FILE="bsb2usfm-web.service"
    CURRENT_DIR=$(pwd)
    USER=$(whoami)

    cat > "$SERVICE_FILE" << EOF
[Unit]
Description=BSB to USFM Web Interface
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$CURRENT_DIR/web
Environment=PATH=$CURRENT_DIR/venv/bin
ExecStart=$CURRENT_DIR/venv/bin/python app.py
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

    print_success "Service file created: $SERVICE_FILE"
    print_status "To install as system service:"
    echo "  sudo cp $SERVICE_FILE /etc/systemd/system/"
    echo "  sudo systemctl daemon-reload"
    echo "  sudo systemctl enable bsb2usfm-web"
    echo "  sudo systemctl start bsb2usfm-web"
}

# Display usage instructions
show_usage() {
    echo ""
    echo "=================================================="
    echo "  Setup Complete!"
    echo "=================================================="
    echo ""
    echo "To start the web interface:"
    echo ""
    echo "  Method 1 (Recommended):"
    echo "    ./run_web.py"
    echo ""
    echo "  Method 2 (Manual):"
    echo "    source venv/bin/activate"
    echo "    cd web"
    echo "    python3 app.py"
    echo ""
    echo "  Method 3 (Background):"
    echo "    nohup ./run_web.py > web.log 2>&1 &"
    echo ""
    echo "Once started, visit: http://localhost:5000"
    echo ""
    echo "Files and directories:"
    echo "  - Upload area: web/uploads/"
    echo "  - Output files: web/outputs/"
    echo "  - Log files: web.log (if using Method 3)"
    echo ""
    echo "Troubleshooting:"
    echo "  - Check web.log for errors"
    echo "  - Ensure port 5000 is not in use"
    echo "  - Verify file permissions in web/ directory"
    echo ""
}

# Main setup function
main() {
    print_header

    # Change to script directory
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    cd "$SCRIPT_DIR"

    print_status "Working directory: $SCRIPT_DIR"

    # Run setup steps
    check_python
    check_pip
    check_files
    setup_directories
    setup_venv
    install_dependencies
    setup_permissions
    test_installation

    # Optional service file
    read -p "Create systemd service file? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        create_service_file
    fi

    print_success "Setup completed successfully!"
    show_usage
}

# Handle script arguments
case "${1:-}" in
    --help|-h)
        echo "BSB to USFM Web Interface Setup Script"
        echo ""
        echo "Usage: $0 [OPTIONS]"
        echo ""
        echo "Options:"
        echo "  --help, -h     Show this help message"
        echo "  --test         Test installation only"
        echo "  --clean        Clean previous installation"
        echo ""
        exit 0
        ;;
    --test)
        print_header
        check_files
        test_installation
        print_success "Test completed successfully!"
        exit 0
        ;;
    --clean)
        print_header
        print_status "Cleaning previous installation..."
        rm -rf venv
        rm -rf web/uploads/*
        rm -rf web/outputs/*
        rm -f bsb2usfm-web.service
        print_success "Cleanup completed!"
        exit 0
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
