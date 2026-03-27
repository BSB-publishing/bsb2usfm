# Development Environment Setup

This guide will help you set up your local development environment to build and generate the BSB and MSB files.

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
1. Download BSB source data (cached in `bereanbible/temp/`)
2. Download MSB source data (cached in `majoritybible/temp/`)
3. Generate all USFM, USJ, and USX files for both editions
4. Run post-processing (DBL adaptation, Paratext adaptation)
5. Create all ZIP archives in each edition's `workspace/`

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

### Build All Editions

```bash
make all
```

Generates everything for both editions:
- **BSB (bereanbible/)**: USFM, USJ, USX files (4 variants x 66 books each) + ZIP archives
- **MSB (majoritybible/)**: USFM, USJ, USX files (4 variants x 27 books each) + ZIP archives

### Build a Single Edition

```bash
make bereanbible        # Build BSB edition only
make majoritybible      # Build MSB edition only
```

### Build Specific Formats Manually

**BSB USFM files:**
```bash
python3 bsb2usfm.py --identifier BSB -o bereanbible/results/%.usfm -f demo_data/sample_footnotes.tsv -n demo_data/sample_book_names.xml bereanbible/temp/source.tsv
```

**MSB USFM files:**
```bash
python3 bsb2usfm.py --identifier MSB -o majoritybible/results/%.usfm -f demo_data/sample_footnotes.tsv -n demo_data/sample_book_names.xml majoritybible/temp/source.tsv
```

**With Strong's numbers (BSB example):**
```bash
python3 bsb2usfm.py --identifier BSB -S -o bereanbible/results/strongs/^%BSB_strongs.usfm -f demo_data/sample_footnotes.tsv -n demo_data/sample_book_names.xml bereanbible/temp/source.tsv
```

**With interlinear data (BSB example):**
```bash
python3 bsb2usfm.py --identifier BSB -I -o bereanbible/results/int/^%BSB_int.usfm -f demo_data/sample_footnotes.tsv -n demo_data/sample_book_names.xml bereanbible/temp/source.tsv
```

### Create ZIP Files

After building the individual files:

```bash
python3 create_zips.py --base-dir bereanbible --identifier BSB
python3 create_zips.py --base-dir majoritybible --identifier MSB
```

Or with verbose output:
```bash
python3 create_zips.py --base-dir bereanbible --identifier BSB --verbose
```

Or dry-run to see what would be created:
```bash
python3 create_zips.py --base-dir bereanbible --identifier BSB --dry-run --verbose
```

### Clean Generated Files

**Clean all generated files for both editions:**
```bash
make clean
```

**Clean cached source data for both editions:**
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
├── bsb2usfm.py                     # Main conversion script
├── create_zips.py                   # ZIP creation script
├── adapt_usx_for_DBL.py            # DBL adaptation script
├── adapt_usfm_for_paratext.py      # Paratext adaptation script
├── Makefile                         # Multi-edition build automation
├── requirements.txt                 # Python dependencies
├── VERSION                          # Current version
│
├── demo_data/                       # Shared sample footnotes and book names
│   ├── sample_bsb_tables.tsv
│   ├── sample_book_names.xml
│   └── sample_footnotes.tsv
│
├── bereanbible/                     # BSB edition (Full Bible - 66 books)
│   ├── temp/                        # Cached source data (gitignored)
│   │   └── source.tsv              # Downloaded from bereanbible.com
│   ├── results/                     # Generated USFM files
│   │   ├── *.usfm                  # Standard USFM (66 files)
│   │   ├── int/                    # Interlinear USFM (66 files)
│   │   ├── strongs/                # Strong's USFM (66 files)
│   │   └── strongs_full/           # Complete Strong's (66 files)
│   ├── results_usj/                 # Generated USJ files (same layout)
│   ├── results_usx/                 # Generated USX files (same layout)
│   ├── results_usx_for_DBL/        # USX adapted for Digital Bible Library
│   ├── results_for_paratext/        # USFM adapted for Paratext
│   ├── sfm_for_paratext/            # SFM files for Paratext
│   └── workspace/                   # ZIP archives (gitignored)
│
├── majoritybible/                   # MSB edition (New Testament - 27 books)
│   ├── temp/                        # Cached source data (gitignored)
│   │   └── source.tsv              # Downloaded from majoritybible.com
│   ├── results/                     # Generated USFM files (same layout)
│   ├── results_usj/                 # Generated USJ files
│   ├── results_usx/                 # Generated USX files
│   ├── results_usx_for_DBL/        # USX adapted for Digital Bible Library
│   ├── results_for_paratext/        # USFM adapted for Paratext
│   ├── sfm_for_paratext/            # SFM files for Paratext
│   └── workspace/                   # ZIP archives (gitignored)
│
└── venv/                            # Virtual environment (gitignored)
```

## Makefile Targets

| Command | Description |
|---------|-------------|
| `make all` | Build both editions (default) |
| `make bereanbible` | Build BSB edition only |
| `make majoritybible` | Build MSB edition only |
| `make clean` | Remove generated files for both editions |
| `make clean-cache` | Remove cached source data for both editions |
| `make force` | Clean cache and rebuild all |

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
mkdir -p bereanbible/temp majoritybible/temp
curl -o bereanbible/temp/source.tsv https://bereanbible.com/bsb_tables.tsv
curl -o majoritybible/temp/source.tsv https://majoritybible.com/msb_nt_tables.tsv

# Generate BSB USFM files
python bsb2usfm.py --identifier BSB -o bereanbible/results/%.usfm -f demo_data/sample_footnotes.tsv -n demo_data/sample_book_names.xml bereanbible/temp/source.tsv

# Generate BSB USJ files
python bsb2usfm.py --identifier BSB -o bereanbible/results_usj/%.usj -f demo_data/sample_footnotes.tsv -n demo_data/sample_book_names.xml bereanbible/temp/source.tsv

# Generate MSB USFM files
python bsb2usfm.py --identifier MSB -o majoritybible/results/%.usfm -f demo_data/sample_footnotes.tsv -n demo_data/sample_book_names.xml majoritybible/temp/source.tsv

# Generate MSB USJ files
python bsb2usfm.py --identifier MSB -o majoritybible/results_usj/%.usj -f demo_data/sample_footnotes.tsv -n demo_data/sample_book_names.xml majoritybible/temp/source.tsv

# Create ZIPs
python create_zips.py --base-dir bereanbible --identifier BSB
python create_zips.py --base-dir majoritybible --identifier MSB
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
make all                  # Build both editions
```

### 3. Testing Changes
```bash
# Test specific edition
make bereanbible

# Test ZIP creation (dry-run)
python create_zips.py --base-dir bereanbible --identifier BSB --dry-run --verbose

# Verify output
ls -lh bereanbible/workspace/*.zip
ls -lh majoritybible/workspace/*.zip
```

### 4. Preparing a Release
```bash
# Update version
echo "5.3" > VERSION

# Build everything
make all

# Follow release process (commit, tag, push)
```

## Testing

### Quick Test
```bash
# Generate one BSB book
python bsb2usfm.py --identifier BSB -o test.usfm -b GEN bereanbible/temp/source.tsv

# Verify it worked
ls -lh test.usfm
head test.usfm
```

### Full Verification
```bash
# Build everything
make all

# Count BSB files (should be 66 per variant × 4 variants × 3 formats = 792)
find bereanbible/results bereanbible/results_usj bereanbible/results_usx -name "*.usfm" -o -name "*.usj" -o -name "*.usx" | wc -l

# Count MSB files (should be 27 per variant × 4 variants × 3 formats = 324)
find majoritybible/results majoritybible/results_usj majoritybible/results_usx -name "*.usfm" -o -name "*.usj" -o -name "*.usx" | wc -l

# Count ZIPs per edition
find bereanbible/workspace -name "*.zip" | wc -l
find majoritybible/workspace -name "*.zip" | wc -l
```

## CI/CD with GitHub Actions

The repository includes GitHub Actions workflows that:
- Automatically build on tag push
- Create GitHub releases
- Upload ZIP files as release assets for both editions

See `.github/workflows/release.yml` for details.

## Need Help?

- **Documentation**: See README.md, README_developer.md
- **Issues**: https://github.com/BSB-publishing/bsb2usfm/issues
- **Licensing**: See LICENSING_INFO.md

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

**Version:** 5.2
