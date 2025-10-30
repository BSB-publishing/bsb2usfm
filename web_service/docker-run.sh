#!/bin/bash

# BSB2USFM Docker Run Script
# This script provides easy commands to run the BSB to USFM converter in Docker

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
IMAGE_NAME="bsb2usfm"
CONTAINER_NAME="bsb2usfm_converter"

# Helper functions
print_usage() {
    echo -e "${BLUE}BSB2USFM Docker Runner${NC}"
    echo ""
    echo "Usage: $0 [COMMAND] [OPTIONS]"
    echo ""
    echo "Commands:"
    echo "  web                  Start web service (accessible at http://localhost:5000)"
    echo "  web-stop             Stop web service"
    echo "  web-logs             Show web service logs"
    echo "  build                Build the Docker image"
    echo "  convert [args]       Run conversion with optional arguments"
    echo "  refs [args]          Extract references from USFM files"
    echo "  shell                Start interactive shell in container"
    echo "  clean                Remove container and image"
    echo "  logs                 Show container logs"
    echo "  help                 Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 web                    # Start web interface"
    echo "  $0 web-stop               # Stop web interface"
    echo "  $0 build"
    echo "  $0 convert data/bsb_tables.csv -o results/%.usfm"
    echo "  $0 convert data/bsb_tables.csv -o results/%.usfm -b GEN -b EXO"
    echo "  $0 refs results/*.usfm -o results/references.txt"
    echo "  $0 shell"
}

print_info() {
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

# Check if Docker is running
check_docker() {
    if ! docker info >/dev/null 2>&1; then
        print_error "Docker is not running or not accessible"
        exit 1
    fi
}

# Build the Docker image
build_image() {
    print_info "Building Docker image: $IMAGE_NAME"
    docker build -t $IMAGE_NAME .
    print_success "Image built successfully"
}

# Check if image exists
image_exists() {
    docker image inspect $IMAGE_NAME >/dev/null 2>&1
}

# Check if container is running
container_running() {
    docker ps --filter "name=$CONTAINER_NAME" --filter "status=running" | grep -q $CONTAINER_NAME
}

# Stop and remove container if it exists
cleanup_container() {
    if docker ps -a --filter "name=$CONTAINER_NAME" | grep -q $CONTAINER_NAME; then
        print_info "Stopping and removing existing container"
        docker stop $CONTAINER_NAME >/dev/null 2>&1 || true
        docker rm $CONTAINER_NAME >/dev/null 2>&1 || true
    fi
}

# Ensure directories exist
ensure_directories() {
    mkdir -p data results demo_data
    print_info "Ensured data directories exist: data/, results/, demo_data/"
}

# Start web service
start_web() {
    ensure_directories

    if ! image_exists; then
        print_warning "Image not found. Building it first..."
        build_image
    fi

    # Check if web service is already running
    if docker ps --filter "name=bsb2usfm_web" --filter "status=running" | grep -q bsb2usfm_web; then
        print_warning "Web service is already running"
        print_info "Access it at http://localhost:5000"
        return
    fi

    print_info "Starting web service..."
    docker-compose up -d web

    print_success "Web service started successfully!"
    echo ""
    print_info "Access the web interface at: ${GREEN}http://localhost:5000${NC}"
    print_info "View logs with: $0 web-logs"
    print_info "Stop with: $0 web-stop"
}

# Stop web service
stop_web() {
    print_info "Stopping web service..."
    docker-compose down
    print_success "Web service stopped"
}

# Show web service logs
web_logs() {
    docker-compose logs -f web
}

# Run conversion
run_conversion() {
    ensure_directories

    if [ $# -eq 0 ]; then
        print_error "No arguments provided for conversion"
        echo "Usage: $0 convert <input_file> [options]"
        echo "Example: $0 convert data/bsb_tables.csv -o results/%.usfm"
        exit 1
    fi

    print_info "Running BSB to USFM conversion"
    docker run --rm \
        -v "$(pwd)/data:/app/input:ro" \
        -v "$(pwd)/results:/app/output" \
        -v "$(pwd)/demo_data:/app/demo_data:ro" \
        $IMAGE_NAME python3 bsb2usfm.py "$@"

    print_success "Conversion completed"
}

# Extract references
run_refs() {
    ensure_directories

    if [ $# -eq 0 ]; then
        print_error "No arguments provided for reference extraction"
        echo "Usage: $0 refs <usfm_files> [options]"
        echo "Example: $0 refs results/*.usfm -o results/references.txt"
        exit 1
    fi

    print_info "Extracting references from USFM files"
    docker run --rm \
        -v "$(pwd)/results:/app/input:ro" \
        -v "$(pwd)/results:/app/output" \
        $IMAGE_NAME python3 getirefs.py "$@"

    print_success "Reference extraction completed"
}

# Start interactive shell
start_shell() {
    ensure_directories
    cleanup_container

    print_info "Starting interactive shell"
    docker run -it --rm \
        --name $CONTAINER_NAME \
        -v "$(pwd)/data:/app/input:ro" \
        -v "$(pwd)/results:/app/output" \
        -v "$(pwd)/demo_data:/app/demo_data:ro" \
        $IMAGE_NAME /bin/bash
}

# Show logs
show_logs() {
    if container_running; then
        docker logs $CONTAINER_NAME
    else
        print_warning "Container is not running"
    fi
}

# Clean up
clean() {
    print_info "Cleaning up Docker resources"
    cleanup_container

    if image_exists; then
        docker rmi $IMAGE_NAME
        print_success "Image removed"
    else
        print_warning "Image not found"
    fi
}

# Main script logic
check_docker

if [ $# -eq 0 ]; then
    print_usage
    exit 0
fi

case "$1" in
    web)
        start_web
        ;;
    web-stop)
        stop_web
        ;;
    web-logs)
        web_logs
        ;;
    build)
        build_image
        ;;
    convert)
        if ! image_exists; then
            print_warning "Image not found. Building it first..."
            build_image
        fi
        shift
        run_conversion "$@"
        ;;
    refs)
        if ! image_exists; then
            print_warning "Image not found. Building it first..."
            build_image
        fi
        shift
        run_refs "$@"
        ;;
    shell)
        if ! image_exists; then
            print_warning "Image not found. Building it first..."
            build_image
        fi
        start_shell
        ;;
    logs)
        show_logs
        ;;
    clean)
        clean
        ;;
    help|--help|-h)
        print_usage
        ;;
    *)
        print_error "Unknown command: $1"
        print_usage
        exit 1
        ;;
esac
