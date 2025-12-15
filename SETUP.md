# Development Environment Setup

This guide will help you set up your local development environment to build and generate the BSB files.

## Prerequisites

- **Python 3.x** (3.10 or later recommended)
- **Make** (usually pre-installed on macOS/Linux)
- **Git**
- **curl** (for downloading source data)

## Quick Setup

### 1. Clone the Repository

```bash
git clone https://github.com/BSB-publishing/bsb2usfm.git
cd bsb2usfm
```

### 2. Create Virtual Environment

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows:**
```cmd
python -m venv venv
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Build Everything

```bash
make all
```

This will:
1. Download the BSB source data (cached in `temp/`)
2. Generate all USFM files (in `results/`)
3. Generate all USJ files (in `results_usj/`)
4. Create all ZIP archives (in `workspace/`)

## Detailed Setup

### Python Version

Check your Python version:
```bash
python3 --version
```

You need Python 3.10 or later. If you have an older version:

**macOS (with Homebrew):**
```bash
brew install python@3.14
```

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install python3 python3-venv python3-pip
```

**Windows:**
Download from [python.org](https://www.python.org/downloads/)

### Virtual Environment (Recommended)

A virtual environment keeps dependencies isolated from your system Python.

**Create venv:**
```bash
python3 -m venv venv
```

**Activate venv:**

macOS/Linux:
```bash
source venv/bin/activate
```

Windows (Command Prompt):
```cmd
venv\Scripts\activate.bat
```

Windows (PowerShell):
```powershell
venv\Scripts\Activate.ps1
```

**Verify activation:**
```bash
which python  # macOS/Linux
where python  # Windows
```

Should show a path inside the `venv` directory.

**Deactivate when done:**
```bash
deactivate
```

### Install Required Packages

With your virtual environment activated:

```bash
pip install -r requirements.txt
```

This installs:
- `usfmtc` - USFM to USJ conversion
- `regex` - Enhanced regular expressions
- `lxml` - XML processing
- `flask` - Web service (optional)
- `gunicorn` - Production server (optional)

### Verify Installation

```bash
python -c "import regex, lxml, usfmtc; print('All packages installed!')"
```

## Building Files

### Build All Files

```bash
make all
```

Generates everything:
- USFM files (4 variants × 66 books = 264 files)
- USJ files (4 variants × 66 books = 264 files)
- ZIP archives (8 files in `workspace/`)

### Build Specific Formats

**Only USFM files:**
```bash
python3 bsb2usfm.py -o results/%.usfm -f demo_data/sample_footnotes.tsv -n demo_data/sample_book_names.xml temp/bsb_tables.tsv
```

**Only USJ files:**
```bash
python3 bsb2usfm.py -o results_usj/%.usj -f demo_data/sample_footnotes.tsv -n demo_data/sample_book_names.xml temp/bsb_tables.tsv
```

**With Strong's numbers:**
```bash
python3 bsb2usfm.py -S -o results/strongs/^%BSB_strongs.usfm -f demo_data/sample_footnotes.tsv -n demo_data/sample_book_names.xml temp/bsb_tables.tsv
```

**With interlinear data:**
```bash
python3 bsb2usfm.py -I -o results/int/^%BSB_int.usfm -f demo_data/sample_footnotes.tsv -n demo_data/sample_book_names.xml temp/bsb_tables.tsv
```

### Create ZIP Files

After building the individual files:

```bash
python3 create_zips.py
```

Or with verbose output:
```bash
python3 create_zips.py --verbose
```

Or dry-run to see what would be created:
```bash
python3 create_zips.py --dry-run --verbose
```

### Clean Generated Files

**Clean all generated files:**
```bash
make clean
```

**Clean cached source data:**
```bash
make clean-cache
```

**Clean everything and rebuild:**
```bash
make clean clean-cache all
```

## Directory Structure

```
bsb2usfm/
├── bsb2usfm.py              # Main conversion script
├── create_zips.py           # ZIP creation script
├── Makefile                 # Build automation
├── requirements.txt         # Python dependencies
├── VERSION                  # Current version (5.1)
│
├── temp/                    # Cached source data (gitignored)
│   └── bsb_tables.tsv       # Downloaded BSB data
│
├── results/                 # Generated USFM files
│   ├── *.usfm              # Standard USFM (66 files)
│   ├── int/                # Interlinear USFM (66 files)
│   ├── strongs/            # Strong's USFM (66 files)
│   └── strongs_full/       # Complete Strong's (66 files)
│
├── results_usj/            # Generated USJ files
│   ├── *.usj               # Standard USJ (66 files)
│   ├── int/                # Interlinear USJ (66 files)
│   ├── strongs/            # Strong's USJ (66 files)
│   └── strongs_full/       # Complete Strong's (66 files)
│
├── workspace/              # ZIP archives (gitignored)
│   ├── *.zip               # USFM ZIPs (4 files)
│   └── usj/                # USJ ZIPs (4 files)
│
├── venv/                   # Virtual environment (gitignored)
└── demo_data/              # Sample footnotes and book names
```

## Makefile Targets

| Command | Description |
|---------|-------------|
| `make all` | Build everything (default) |
| `make clean` | Remove generated files |
| `make clean-cache` | Remove cached source data |
| `make force` | Clean cache and rebuild all |
| `make check-remote-updates` | Check for updated source data |

## Troubleshooting

### "No module named 'regex'"

Your Python environment doesn't have the required packages.

**Solution:**
```bash
# Activate venv
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
```

### "venv/bin/python3: No such file or directory"

Your virtual environment is broken or missing.

**Solution:**
```bash
# Remove old venv
rm -rf venv

# Create new venv
python3 -m venv venv

# Activate and install
source venv/bin/activate
pip install -r requirements.txt
```

### "make: command not found"

Make is not installed.

**macOS:**
```bash
xcode-select --install
```

**Ubuntu/Debian:**
```bash
sudo apt install build-essential
```

**Windows:**
- Install via [Chocolatey](https://chocolatey.org/): `choco install make`
- Or use Git Bash (comes with Git for Windows)
- Or run Python scripts directly without Make

### Running Without Make (Windows)

If you can't use Make, run commands directly:

```bash
# Download source data
curl -o temp/bsb_tables.tsv https://bereanbible.com/bsb_tables.tsv

# Generate USFM files
python bsb2usfm.py -o results/%.usfm -f demo_data/sample_footnotes.tsv -n demo_data/sample_book_names.xml temp/bsb_tables.tsv

# Generate USJ files
python bsb2usfm.py -o results_usj/%.usj -f demo_data/sample_footnotes.tsv -n demo_data/sample_book_names.xml temp/bsb_tables.tsv

# Create ZIPs
python create_zips.py
```

### Permission Denied on Scripts

Make scripts executable:

```bash
chmod +x prepare_release.sh check_release.sh
```

### Makefile Uses Wrong Python

The Makefile auto-detects Python. To verify:

```bash
make -n all | grep python
```

Should show `venv/bin/python` if venv exists, otherwise `python3`.

To force a specific Python:
```bash
PYTHON=/path/to/python make all
```

## Development Workflow

### 1. Initial Setup (Once)
```bash
git clone https://github.com/BSB-publishing/bsb2usfm.git
cd bsb2usfm
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Daily Development
```bash
cd bsb2usfm
source venv/bin/activate  # Activate venv
make clean                # Clean old files
make all                  # Build everything
```

### 3. Testing Changes
```bash
# Test specific conversion
python bsb2usfm.py -o test_output/%.usfm temp/bsb_tables.tsv

# Test ZIP creation (dry-run)
python create_zips.py --dry-run --verbose

# Verify output
ls -lh workspace/*.zip
```

### 4. Preparing a Release
```bash
# Update version
echo "5.2" > VERSION

# Run release preparation
./prepare_release.sh

# Follow prompts to commit and tag
```

## Testing

### Quick Test
```bash
# Generate one book
python bsb2usfm.py -o test.usfm -b GEN temp/bsb_tables.tsv

# Verify it worked
ls -lh test.usfm
head test.usfm
```

### Full Verification
```bash
# Build everything
make all

# Count files (should be 264 + 264 = 528)
find results results_usj -name "*.usfm" -o -name "*.usj" | wc -l

# Count ZIPs (should be 8)
find workspace -name "*.zip" | wc -l

# Verify each ZIP has 66 books
for zip in $(find workspace -name "*.zip"); do
  echo "$zip: $(unzip -l "$zip" | grep -E '\.(usfm|usj)$' | wc -l) books"
done
```

## CI/CD with GitHub Actions

The repository includes GitHub Actions workflows that:
- Automatically build on tag push
- Create GitHub releases
- Upload ZIP files as release assets

See `.github/workflows/release.yml` for details.

## Need Help?

- **Documentation**: See README.md, README_developer.md
- **Issues**: https://github.com/BSB-publishing/bsb2usfm/issues
- **Licensing**: See LICENSING_INFO.md
- **Workspace**: See WORKSPACE_STRUCTURE.md

## Platform-Specific Notes

### macOS
- Use Homebrew for Python: `brew install python@3.14`
- Xcode Command Line Tools required for some packages
- Virtual environment recommended

### Linux
- Use system package manager for Python
- May need `python3-venv` package
- Build tools: `sudo apt install build-essential`

### Windows
- Use Git Bash for Unix-like commands
- Or use PowerShell with Windows equivalents
- Make optional (can run scripts directly)
- Consider WSL for better compatibility

---

**Last Updated:** 2024-12-15  
**Version:** 5.1