# BSB2USFM Docker Setup

This document provides instructions for running the BSB to USFM converter using Docker.

## Prerequisites

- Docker installed and running on your system
- Docker Compose (optional, included with Docker Desktop)

## Quick Start

1. **Build the Docker image:**
   ```bash
   ./docker-run.sh build
   ```

2. **Run a conversion:**
   ```bash
   ./docker-run.sh convert data/bsb_tables.csv -o results/%.usfm
   ```

3. **Extract references from generated USFM files:**
   ```bash
   ./docker-run.sh refs results/*.usfm -o results/references.txt
   ```

## Docker Run Script Usage

The `docker-run.sh` script provides convenient commands for Docker operations:

### Available Commands

- `build` - Build the Docker image
- `convert [args]` - Run BSB to USFM conversion
- `refs [args]` - Extract references from USFM files
- `shell` - Start interactive shell in container
- `clean` - Remove container and image
- `logs` - Show container logs
- `help` - Show help message

### Examples

#### Basic Conversion
```bash
./docker-run.sh convert data/bsb_tables.csv -o results/%.usfm
```

#### Convert Specific Books
```bash
./docker-run.sh convert data/bsb_tables.csv -o results/%.usfm -b GEN -b EXO -b MAT
```

#### Extract References
```bash
./docker-run.sh refs results/*.usfm -o results/references.txt
```

#### Interactive Shell
```bash
./docker-run.sh shell
```

## Using Docker Compose

### Basic Usage

1. **Start the container (keeps running for interactive use):**
   ```bash
   docker-compose up -d
   ```

2. **Execute commands in the running container:**
   ```bash
   docker-compose exec bsb2usfm python3 bsb2usfm.py /app/input/bsb_tables.csv -o /app/output/%.usfm
   ```

3. **Stop the container:**
   ```bash
   docker-compose down
   ```

### Profile-based Operations

#### Run conversion job:
```bash
docker-compose --profile convert up bsb2usfm-convert
```

#### Extract references:
```bash
docker-compose --profile refs up bsb2usfm-refs
```

## Manual Docker Commands

### Build Image
```bash
docker build -t bsb2usfm .
```

### Run Conversion
```bash
docker run --rm \
  -v $(pwd)/data:/app/input:ro \
  -v $(pwd)/results:/app/output \
  -v $(pwd)/demo_data:/app/demo_data:ro \
  bsb2usfm python3 bsb2usfm.py /app/input/bsb_tables.csv -o /app/output/%.usfm
```

### Interactive Shell
```bash
docker run -it --rm \
  -v $(pwd)/data:/app/input:ro \
  -v $(pwd)/results:/app/output \
  -v $(pwd)/demo_data:/app/demo_data:ro \
  bsb2usfm /bin/bash
```

## Directory Structure

The Docker setup expects the following directory structure:

```
bsb2usfm/
├── data/           # Input data files (mounted read-only)
├── results/        # Output USFM files (mounted read-write)
├── demo_data/      # Demo/sample files (mounted read-only)
├── Dockerfile
├── docker-compose.yml
├── docker-run.sh   # Convenience script
└── ...
```

## Volume Mounts

- `./data` → `/app/input` (read-only) - Input CSV files
- `./results` → `/app/output` (read-write) - Output USFM files
- `./demo_data` → `/app/demo_data` (read-only) - Demo files

## Environment Variables

The following environment variables are set in the container:

- `PYTHONPATH=/app`
- `PYTHONDONTWRITEBYTECODE=1`
- `PYTHONUNBUFFERED=1`

## Security

- The container runs as a non-root user (`bsb2usfm`, UID 1000)
- Input directories are mounted read-only
- Only the output directory has write permissions

## Troubleshooting

### Permission Issues
If you encounter permission issues with output files:
```bash
# Fix ownership (Linux/macOS)
sudo chown -R $USER:$USER results/

# Or run with specific user ID
docker run --user $(id -u):$(id -g) ...
```

### Container Won't Start
1. Check Docker is running: `docker info`
2. Ensure directories exist: `mkdir -p data results demo_data`
3. Check image exists: `docker images | grep bsb2usfm`

### Build Issues
If build fails:
1. Clean Docker cache: `docker system prune`
2. Rebuild without cache: `docker build --no-cache -t bsb2usfm .`

## Performance Tips

- Use `.dockerignore` to exclude unnecessary files from build context
- Mount only necessary directories
- Use specific tags for production deployments

## Development

For development work:

1. **Start development container:**
   ```bash
   docker-compose up -d
   ```

2. **Enter container for development:**
   ```bash
   docker-compose exec bsb2usfm bash
   ```

3. **Edit code and test immediately:**
   ```bash
   python3 bsb2usfm.py --help
   ```

The source code is copied into the container, so changes require rebuilding the image.

## Integration

### CI/CD Pipeline Example
```bash
# Build and test
docker build -t bsb2usfm .
docker run --rm bsb2usfm python3 -m py_compile bsb2usfm.py

# Run conversion
docker run --rm -v ./data:/app/input:ro -v ./results:/app/output bsb2usfm \
  python3 bsb2usfm.py /app/input/bsb_tables.csv -o /app/output/%.usfm
```

### Batch Processing
```bash
# Process multiple input files
for file in data/*.csv; do
  ./docker-run.sh convert "$file" -o "results/$(basename "$file" .csv)/%.usfm"
done
```
