# BSB2USFM Converter - Developer Documentation

> **Note**: If you're looking to download Bible files, see **[README.md](README.md)** for quick downloads and user-friendly instructions. This document is for developers who want to generate or modify the files.

A Python tool for converting Berean Standard Bible (BSB) tabular data into USFM (Unified Standard Format Markers) format for Bible publishing and translation workflows.

> **Web Service Available**: A web-based interface is available for easy browser-based conversions. See the [Web Service](#web-service) section below or [web_service/DEPLOY_Docker.md](web_service/DEPLOY_Docker.md) for deployment instructions.

## Overview

BSB2USFM converts structured CSV/TSV data containing biblical text, footnotes, cross-references, and formatting information into standardized USFM files that can be used by Bible publishing software such as Paratext, PTXprint, and other Bible translation tools.

## Features

- **URL and local file support**: Download BSB tables from URL or use local files
- **Complete Bible conversion**: Convert entire Bible or specific books
- **Rich formatting support**: Headings, cross-references, footnotes, poetry, lists
- **Custom book names**: Support for custom book naming via XML configuration
- **Footnote styling**: Advanced footnote formatting with custom styling rules
- **Verse references**: Automatic parsing and linking of biblical references
- **USFM 3.1 compliance**: Generates standards-compliant USFM output
- **Docker support**: Containerized execution for consistent environments
- **Web interface**: Browser-based UI with real-time progress updates
- **Cloud deployment**: Ready to deploy on Render, Digital Ocean, Hetzner, and other platforms

## Requirements

- Python 3.11+
- Dependencies: `usfmtc`, `regex`, `lxml`

## Installation

### Local Installation

```bash
git clone <repository-url>
cd bsb2usfm
pip install -r requirements.txt
```

### Docker Installation

```bash
git clone <repository-url>
cd bsb2usfm
chmod +x docker-run.sh
./docker-run.sh build
```

## Usage

### Basic Conversion

Convert BSB tables to USFM format using the default URL source:

```bash
python3 bsb2usfm.py -o results/%.usfm
```

Or specify a local file:

```bash
# Using demo data
python3 bsb2usfm.py demo_data/sample_bsb_tables.tsv -o results/%.usfm

# Or download from URL (downloads from bereanbible.com)
python3 bsb2usfm.py -o results/%.usfm
```

### Convert Specific Books

Convert only specific books using book codes:

```bash
python3 bsb2usfm.py -o results/%.usfm -b GEN -b EXO -b MAT
```

### With Custom Book Names

Use a custom book names XML file:

```bash
python3 bsb2usfm.py -o results/%.usfm -n book_names.xml
```

### With Footnote Styling

Apply custom footnote formatting:

```bash
python3 bsb2usfm.py -o results/%.usfm -f footnotes.tsv
```

### Complete Example

Full conversion with all options (using default URL source):

```bash
python3 bsb2usfm.py -o results/%.usfm \
  -n demo_data/sample_book_names.xml \
  -f demo_data/sample_footnotes.tsv \
  -b GEN -b EXO -b MAT
```

### Advanced Options

#### Interlinear Format

Generate reverse interlinear format with `\rb` entries:

```bash
python3 bsb2usfm.py -o results/%.usfm -I
```

#### Strong's Numbers and other commandline options

- `-S` / `--strongs`: Enable Strong's number processing
- `-P` / `--placeholders`: Enable placeholder processing
- `-B` / `--brackets`: Enable bracket processing

## Web Service

A modern web interface is available for easy browser-based conversions with real-time progress tracking.

### Quick Start with Web Service

```bash
# Start the web service
cd web_service
docker-compose up -d web

# Access at http://localhost:5000
# Click "Update Data" to start conversion
```

### Web Service Features

- 🌐 **Browser-based interface**: No command-line needed
- 🔄 **Real-time progress**: Live streaming of conversion status
- 📊 **Visual feedback**: Progress bars and status indicators
- 📁 **Results display**: Automatic listing of generated files
- 💾 **Download support**: Zip all generated files with one click
- 🚀 **Production ready**: Deploy to Render, Digital Ocean, Hetzner, Fly.io

### Deployment

For production deployment to cloud platforms, see **[web_service/DEPLOY_Docker.md](web_service/DEPLOY_Docker.md)** for comprehensive guides covering:

- **Render.com**: One-click deployment with free tier
- **Digital Ocean**: VPS deployment with full control

See [web_service/README-WebService.md](web_service/README-WebService.md) for detailed web service documentation.

## Docker Usage (CLI)

### Quick Start with Docker

```bash
# Build the image
./docker-run.sh build

# Convert all books using demo data
./docker-run.sh convert demo_data/sample_bsb_tables.tsv -o results/%.usfm

# Convert specific books
./docker-run.sh convert demo_data/sample_bsb_tables.tsv -o results/%.usfm -b GEN -b EXO

# Or download from URL
./docker-run.sh convert -o results/%.usfm -b GEN -b EXO

# Interactive shell
./docker-run.sh shell
```

## Command Line Options

| Option | Description | Example |
|--------|-------------|---------|
| `infile` | Input BSB tables CSV/TSV file or URL (optional, defaults to https://bereanbible.com/bsb_tables.tsv) | `demo_data/sample_bsb_tables.tsv` |
| `-o, --outfile` | Output USFM file template | `results/%.usfm` |
| `-b, --book` | Book codes to include (repeatable) | `-b GEN -b EXO` |
| `-n, --names` | Custom book names XML file | `-n book_names.xml` |
| `-f, --fnotes` | Footnote styling TSV file | `-f footnotes.tsv` |
| `-I, --interlinear` | Output `\rb` entries for reverse interlinear | `-I` |
| `-S, --strongs` | Include Strong's numbers (requires -P and -B for more extensive output) | `-S` |
| `-P, --placeholders` | Include placeholders (requires -S and -B for more extensive output) | `-P` |
| `-B, --brackets` | Include brackets (requires -S and -P for more extensive output) | `-B` |

### Output Template Variables

- `%` - Replaced with book code (e.g., `GEN`, `MAT`)
- `^` - Replaced with book number (e.g., `01`, `40`)

## Input Data Format

### BSB Tables CSV Structure

The input CSV/TSV file should contain the following columns:

- **VerseId**: Bible reference (e.g., "Genesis 1:1")
- **BSB version**: Main verse text
- **Hdg**: Section headings
- **Crossref**: Cross-references
- **Par**: Parallel passages
- **footnotes**: Footnote text
- **pnc**: Punctuation and formatting
- **End text**: Text at verse end

### Book Names XML Format

```xml
<?xml version="1.0" encoding="utf-8"?>
<books>
    <book code="GEN" long="Genesis" short="Genesis" abbr="Gen"/>
    <book code="EXO" long="Exodus" short="Exodus" abbr="Exo"/>
    <!-- ... more books -->
</books>
```

### Footnote Styling TSV Format

```
Genesis 1:1	fq	ft
Genesis 3:16	fqa	ft
```

Format: `Reference [TAB] Style1 [TAB] Style2 [TAB] ...`

## Supported Formatting

### Text Styles

- **Regular text**: Plain verse text
- **Red letter**: Jesus' words (`<span class=|red|>`)
- **Poetry**: Indented lines (`<p class=|indent1|>`, `<p class=|indent2|>`)
- **Headings**: Section headings (`<p class=|hdg|>`)
- **Cross-references**: Reference links (`<span class=|cross|>`)

### Structural Elements

- **Paragraphs**: Regular paragraphs (`<p class=|reg|>`)
- **Lists**: Bulleted lists (`<p class=|list1|>`, `<p class=|list2|>`)
- **Inscriptions**: Special formatting (`<p class=|inscrip|>`)
- **Acrostics**: Hebrew acrostic poems

### Book Structure

Each generated USFM file includes:

- Book identification (`\id`)
- Table of contents entries (`\toc1`, `\toc2`, `\toc3`)
- Book title (`\mt1`, `\mt2`)
- Chapter markers (`\c`)
- Verse markers (`\v`)

## Output Format

Generated USFM files follow the USFM 3.1 standard:

```usfm
\id GEN Autogenerated BSB by bsb2usfm
\h Gen
\toc1 Genesis
\toc2 Genesis
\toc3 GEN
\mt1 Genesis
\c 1
\s1 The Creation
\p
\v 1 In the beginning God created the heavens and the earth.
\v 2 Now the earth was formless and void...
```

## Book Codes

Supported book codes follow standard abbreviations:

**Old Testament**: GEN, EXO, LEV, NUM, DEU, JOS, JDG, RUT, 1SA, 2SA, 1KI, 2KI, 1CH, 2CH, EZR, NEH, EST, JOB, PSA, PRO, ECC, SNG, ISA, JER, LAM, EZK, DAN, HOS, JOL, AMO, OBA, JON, MIC, NAM, HAB, ZEP, HAG, ZEC, MAL

**New Testament**: MAT, MRK, LUK, JHN, ACT, ROM, 1CO, 2CO, GAL, EPH, PHP, COL, 1TH, 2TH, 1TI, 2TI, TIT, PHM, HEB, JAS, 1PE, 2PE, 1JN, 2JN, 3JN, JUD, REV

## Directory Structure

```
bsb2usfm/
├── web_service/       # Web interface (optional)
│   ├── webapp.py     # Flask web application
│   ├── templates/    # HTML templates
│   ├── Dockerfile    # Web service Docker config
│   └── docker-compose.yml
├── results/           # Output USFM files
├── demo_data/         # Sample/demo files
│   ├── sample_bsb_tables.tsv
│   ├── sample_book_names.xml
│   └── sample_footnotes.tsv
├── render/            # Render.com deployment config
│   └── render.yaml
├── bsb2usfm.py       # Main converter script
├── getirefs.py       # Reference extractor
├── requirements.txt   # Python dependencies
├── README.md         # User documentation
└── README_developer.md  # This file
```

## Examples

### Convert Genesis Only

Using default URL source:

```bash
python3 bsb2usfm.py -o gen.usfm -b GEN
```

Or with a local file:

```bash
# Using demo data
python3 bsb2usfm.py demo_data/sample_bsb_tables.tsv -o gen.usfm -b GEN

# Or from URL
python3 bsb2usfm.py -o gen.usfm -b GEN
```

### Convert New Testament

```bash
python3 bsb2usfm.py -o nt_%.usfm \
  -b MAT -b MRK -b LUK -b JHN -b ACT -b ROM -b 1CO -b 2CO \
  -b GAL -b EPH -b PHP -b COL -b 1TH -b 2TH -b 1TI -b 2TI \
  -b TIT -b PHM -b HEB -b JAS -b 1PE -b 2PE -b 1JN -b 2JN \
  -b 3JN -b JUD -b REV
```

### Extract References

Use the companion script to extract verse references:

```bash
python3 getirefs.py results/*.usfm -o references.txt
```

## Troubleshooting

### Common Issues

1. **"not enough values to unpack" error**
   - Ensure book names XML file contains proper long names
   - Check that book titles can be split into two parts

2. **Missing dependencies**
   - Install required packages: `pip install -r requirements.txt`

3. **Encoding issues**
   - Ensure input files are UTF-8 encoded

4. **Empty output files**
   - Check that book codes match between input data and filter options
   - Verify input CSV structure and column mapping

### Docker Issues

1. **Permission errors**
   - Fix ownership: `sudo chown -R $USER:$USER results/`

2. **Build failures**
   - Clean Docker cache: `docker system prune`
   - Rebuild without cache: `./docker-run.sh clean && ./docker-run.sh build`

## Contributing

[Contribution guidelines here]

## Deployment

### Web Service Deployment

For deploying the web service to production environments, see:

- **[web_service/DEPLOY_Docker.md](web_service/DEPLOY_Docker.md)**: Complete deployment guide for Render and Digital Ocean
- **[web_service/README-WebService.md](web_service/README-WebService.md)**: Web service features and API documentation
- **[render/DEPLOYMENT.md](render/DEPLOYMENT.md)**: Render-specific deployment instructions

### Quick Deploy Options

**Render (Easiest)**:
```bash
# Push to GitHub, then connect to Render
# render.yaml is already configured
```

**Digital Ocean Droplet**:
```bash
# SSH to droplet, then:
git clone <repo-url>
cd bsb2usfm/web_service
docker-compose up -d web
```

**Local/VPS Docker**:
```bash
cd web_service
docker-compose up -d web
# Access at http://localhost:5000
```

See [web_service/DEPLOY_Docker.md](web_service/DEPLOY_Docker.md) for step-by-step instructions for each platform.

## Support

For issues or questions:

- **General usage**: See [README.md](README.md)
- **Web service**: See [web_service/README-WebService.md](web_service/README-WebService.md)
- **Deployment**: See [web_service/DEPLOY_Docker.md](web_service/DEPLOY_Docker.md)
- **Bug reports**: Open an issue on the project repository
