#!/bin/bash
# Deployment Readiness Checker for BSB2USFM Web Service
# This script verifies that all components are ready for deployment

set -e

echo "================================================"
echo "BSB2USFM Web Service Deployment Readiness Check"
echo "================================================"
echo ""

ERRORS=0
WARNINGS=0

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

check_pass() {
    echo -e "${GREEN}✓${NC} $1"
}

check_fail() {
    echo -e "${RED}✗${NC} $1"
    ((ERRORS++))
}

check_warn() {
    echo -e "${YELLOW}⚠${NC} $1"
    ((WARNINGS++))
}

# Check 1: Required files exist
echo "Checking required files..."
if [ -f "Dockerfile" ]; then
    check_pass "Dockerfile exists"
else
    check_fail "Dockerfile is missing"
fi

if [ -f "docker-compose.yml" ]; then
    check_pass "docker-compose.yml exists"
else
    check_fail "docker-compose.yml is missing"
fi

if [ -f "webapp.py" ]; then
    check_pass "webapp.py exists"
else
    check_fail "webapp.py is missing"
fi

if [ -f "../requirements.txt" ]; then
    check_pass "requirements.txt exists"
else
    check_fail "requirements.txt is missing"
fi

if [ -f "../bsb2usfm.py" ]; then
    check_pass "bsb2usfm.py exists"
else
    check_fail "bsb2usfm.py is missing"
fi

echo ""

# Check 2: Templates directory
echo "Checking templates..."
if [ -d "templates" ]; then
    if [ -f "templates/index.html" ]; then
        check_pass "templates/index.html exists"
    else
        check_fail "templates/index.html is missing"
    fi
else
    check_fail "templates/ directory is missing"
fi

echo ""

# Check 3: Dependencies in requirements.txt
echo "Checking Python dependencies..."
if [ -f "../requirements.txt" ]; then
    if grep -q "flask" ../requirements.txt; then
        check_pass "flask is in requirements.txt"
    else
        check_fail "flask is missing from requirements.txt"
    fi
    
    if grep -q "gunicorn" ../requirements.txt; then
        check_pass "gunicorn is in requirements.txt"
    else
        check_warn "gunicorn is missing from requirements.txt (recommended for production)"
    fi
    
    if grep -q "usfmtc" ../requirements.txt; then
        check_pass "usfmtc is in requirements.txt"
    else
        check_fail "usfmtc is missing from requirements.txt"
    fi
fi

echo ""

# Check 4: Dockerfile syntax
echo "Checking Dockerfile..."
if [ -f "Dockerfile" ]; then
    if grep -q "FROM python" Dockerfile; then
        check_pass "Dockerfile has Python base image"
    else
        check_fail "Dockerfile missing Python base image"
    fi
    
    if grep -q "EXPOSE" Dockerfile; then
        check_pass "Dockerfile exposes port"
    else
        check_warn "Dockerfile should expose a port"
    fi
    
    if grep -q "CMD" Dockerfile || grep -q "ENTRYPOINT" Dockerfile; then
        check_pass "Dockerfile has CMD or ENTRYPOINT"
    else
        check_fail "Dockerfile missing CMD or ENTRYPOINT"
    fi
    
    # Check for relative parent directory issues
    if grep -q "COPY \.\." Dockerfile; then
        check_fail "Dockerfile uses '../' in COPY (won't work, use build context instead)"
    else
        check_pass "Dockerfile COPY commands are correct"
    fi
fi

echo ""

# Check 5: Render configuration (if exists)
echo "Checking deployment configurations..."
if [ -f "../render/render.yaml" ]; then
    check_pass "render.yaml exists for Render deployment"
    
    if grep -q "runtime: docker" ../render/render.yaml; then
        check_pass "render.yaml configured for Docker runtime"
    else
        check_warn "render.yaml may need 'runtime: docker' setting"
    fi
    
    if grep -q "healthCheckPath" ../render/render.yaml; then
        check_pass "render.yaml has health check configured"
    else
        check_warn "render.yaml should include healthCheckPath"
    fi
else
    check_warn "render.yaml not found (optional for Render deployment)"
fi

echo ""

# Check 6: Docker availability
echo "Checking Docker installation..."
if command -v docker &> /dev/null; then
    check_pass "Docker is installed"
    DOCKER_VERSION=$(docker --version | cut -d ' ' -f3 | cut -d ',' -f1)
    echo "  Docker version: $DOCKER_VERSION"
else
    check_warn "Docker is not installed (needed for local testing)"
fi

if command -v docker-compose &> /dev/null; then
    check_pass "docker-compose is installed"
    COMPOSE_VERSION=$(docker-compose --version | cut -d ' ' -f4 | cut -d ',' -f1)
    echo "  docker-compose version: $COMPOSE_VERSION"
else
    check_warn "docker-compose is not installed (needed for local testing)"
fi

echo ""

# Check 7: Python availability
echo "Checking Python installation..."
if command -v python3 &> /dev/null; then
    check_pass "python3 is installed"
    PYTHON_VERSION=$(python3 --version | cut -d ' ' -f2)
    echo "  Python version: $PYTHON_VERSION"
    
    # Check version is 3.11+
    MAJOR=$(echo $PYTHON_VERSION | cut -d '.' -f1)
    MINOR=$(echo $PYTHON_VERSION | cut -d '.' -f2)
    if [ "$MAJOR" -ge 3 ] && [ "$MINOR" -ge 11 ]; then
        check_pass "Python version is 3.11+"
    else
        check_warn "Python 3.11+ recommended (current: $PYTHON_VERSION)"
    fi
else
    check_warn "python3 is not installed (needed for local development)"
fi

echo ""

# Check 8: Test webapp.py syntax
echo "Checking webapp.py syntax..."
if [ -f "webapp.py" ]; then
    if python3 -m py_compile webapp.py 2>/dev/null; then
        check_pass "webapp.py has valid Python syntax"
    else
        check_fail "webapp.py has syntax errors"
    fi
    
    if grep -q "app = Flask" webapp.py; then
        check_pass "webapp.py creates Flask app"
    else
        check_fail "webapp.py missing Flask app initialization"
    fi
    
    if grep -q "@app.route('/health')" webapp.py; then
        check_pass "webapp.py has health check endpoint"
    else
        check_warn "webapp.py should have /health endpoint for monitoring"
    fi
    
    if grep -q "PORT" webapp.py; then
        check_pass "webapp.py reads PORT from environment"
    else
        check_warn "webapp.py should read PORT from environment variable"
    fi
fi

echo ""

# Check 9: Directory structure
echo "Checking directory structure..."
if [ -d "../results" ]; then
    check_pass "../results directory exists"
else
    check_warn "../results directory doesn't exist (will be created)"
fi

if [ -d "../demo_data" ]; then
    check_pass "../demo_data directory exists"
else
    check_warn "../demo_data directory doesn't exist (optional)"
fi

echo ""

# Check 10: Documentation
echo "Checking documentation..."
if [ -f "DEPLOY_Docker.md" ]; then
    check_pass "DEPLOY_Docker.md exists"
else
    check_warn "DEPLOY_Docker.md not found (deployment guide recommended)"
fi

if [ -f "README-WebService.md" ]; then
    check_pass "README-WebService.md exists"
else
    check_warn "README-WebService.md not found (web service docs recommended)"
fi

if [ -f "DEPLOYMENT_INDEX.md" ]; then
    check_pass "DEPLOYMENT_INDEX.md exists"
else
    check_warn "DEPLOYMENT_INDEX.md not found (deployment index recommended)"
fi

if [ -f "../README_developer.md" ]; then
    check_pass "README_developer.md exists"
else
    check_warn "README_developer.md not found"
fi

echo ""
echo "================================================"
echo "Summary"
echo "================================================"

if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo -e "${GREEN}✓ All checks passed! Ready to deploy.${NC}"
    exit 0
elif [ $ERRORS -eq 0 ]; then
    echo -e "${YELLOW}⚠ $WARNINGS warning(s) found. Review before deploying.${NC}"
    exit 0
else
    echo -e "${RED}✗ $ERRORS error(s) and $WARNINGS warning(s) found.${NC}"
    echo -e "${RED}Please fix errors before deploying.${NC}"
    exit 1
fi