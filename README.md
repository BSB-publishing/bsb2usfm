# BSB to USFM Converter

A powerful tool to convert Berean Study Bible (BSB) tables to USFM (Unified Standard Format Markers) format, with both command-line and web interfaces.

## Features

- ✅ **Command Line Interface**: Traditional script-based conversion
- 🌐 **Web Interface**: User-friendly browser-based conversion
- 📚 **Selective Conversion**: Choose specific books or convert entire Bible
- 📝 **Footnote Support**: Custom footnote styling with TSV files
- 🏷️ **Custom Book Names**: XML-based book name customization
- 📦 **Batch Download**: Get all USFM files in a convenient ZIP package
- 🔄 **Real-time Progress**: View conversion logs and progress
- 📱 **Responsive Design**: Works on desktop, tablet, and mobile

## Quick Start

### Web Interface (Recommended)

1. **Setup** (first time only):
   ```bash
   chmod +x setup_web.sh
   ./setup_web.sh
   ```

2. **Start the web server**:
   ```bash
   ./run_web.py
   ```

3. **Open your browser** and visit: http://localhost:5000

4. **Configure options** and select books to convert

5. **Download your USFM files** when conversion completes

**Note**: The web interface uses the fixed BSB tables file at `data/bsb_tables.csv` containing the complete Berean Study Bible dataset.

### Command Line Interface

```bash
# Basic conversion (uses fixed BSB data file)
python3 bsb2usfm.py data/bsb_tables.csv -o output_%.usfm

# With optional customization files
python3 bsb2usfm.py data/bsb_tables.csv -o output_%.usfm -f footnotes.tsv -n BookNames.xml

# Convert specific books only
python3 bsb2usfm.py data/bsb_tables.csv -o output_%.usfm -b GEN -b EXO -b MAT
```

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- Virtual environment support

### Automatic Setup

The easiest way to get started:

```bash
git clone <repository-url>
cd bsb2usfm-py
./setup_web.sh
```

### Manual Setup

1. **Create virtual environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Test installation**:
   ```bash
   python3 -c "import usfmtc; print('Installation successful!')"
   ```

## File Requirements

### Fixed Data Source

| File | Description | Format |
|------|-------------|--------|
| **BSB Tables** | Complete Berean Study Bible data (fixed location: `data/bsb_tables.csv`) | TSV |

### Optional Customization Files

| File | Description | Format | Purpose |
|------|-------------|--------|---------|
| **Footnotes** | Footnote styling rules | TSV | Custom footnote formatting |
| **Book Names** | Custom book names/abbreviations | XML | Override default book names |

### File Format Examples

#### BSB Tables (Fixed File: data/bsb_tables.csv)
The BSB tables file contains the complete Berean Study Bible with Hebrew/Greek parsing data:
```tsv
Heb Sort	Greek Sort	BSB Sort	Verse	Language	...	VerseId	Hdg	Crossref	Par	...	 BSB version 	...	footnotes	End text
1	0	1	1	Hebrew	...	Genesis 1:1	<p class=|hdg|>The Creation	...	 In the beginning God created the heavens and the earth. 	...		
```

#### Footnotes (TSV)
```tsv
GEN 1:1	fqa	ft
GEN 1:2	fq	ft	fqa
```

#### Book Names (XML)
```xml
<?xml version="1.0" encoding="utf-8"?>
<books>
  <book code="GEN" long="Genesis" short="Genesis" abbr="Gen"/>
  <book code="EXO" long="Exodus" short="Exodus" abbr="Exo"/>
</books>
```

## Configuration

### Output Template

Use `%` as a placeholder for book codes in the output filename:

- `output_%.usfm` → `output_GEN.usfm`, `output_MAT.usfm`, etc.
- `usfm/%.txt` → `usfm/GEN.txt`, `usfm/MAT.txt`, etc.
- `bible_%.usfm` → `bible_GEN.usfm`, `bible_MAT.usfm`, etc.

### Book Codes

| Code | Book Name | Code | Book Name |
|------|-----------|------|-----------|
| GEN | Genesis | MAT | Matthew |
| EXO | Exodus | MRK | Mark |
| LEV | Leviticus | LUK | Luke |
| NUM | Numbers | JHN | John |
| DEU | Deuteronomy | ACT | Acts |
| ... | ... | ... | ... |

*See the web interface for the complete list of 66 books.*

## Usage Examples

### Web Interface
### Web Interface Examples

1. **Access Data Source**: The complete BSB tables are automatically loaded from `data/bsb_tables.csv`
2. **Add Optional Files**: Upload footnotes or book names for customization if desired
3. **Configure Output**: Set filename template and select books
4. **Convert**: Click "Convert to USFM" and wait for results
5. **Download**: Get individual files or complete ZIP package

### Command Line Examples

```bash
# Convert all books from fixed BSB data
python3 bsb2usfm.py data/bsb_tables.csv -o output/%.usfm

# Convert New Testament only
python3 bsb2usfm.py data/bsb_tables.csv -o nt/%.usfm \
  -b MAT -b MRK -b LUK -b JHN -b ACT -b ROM -b 1CO -b 2CO \
  -b GAL -b EPH -b PHP -b COL -b 1TH -b 2TH -b 1TI -b 2TI \
  -b TIT -b PHM -b HEB -b JAS -b 1PE -b 2PE -b 1JN -b 2JN \
  -b 3JN -b JUD -b REV

# Convert with custom footnotes and book names
python3 bsb2usfm.py data/bsb_tables.csv -o custom/%.usfm \
  -f customization/footnotes.tsv -n customization/BookNames.xml

# Convert specific books with custom output location
python3 bsb2usfm.py data/bsb_tables.csv -o "/path/to/output/%.usfm" \
  -b PSA -b PRO -b ECC
```

## Web Interface Features

### Data Source
- **Fixed BSB Data**: Uses the complete Berean Study Bible tables automatically
- **No Upload Required**: The main data file is always available at `data/bsb_tables.csv`
- **Optional Customization**: Upload footnote styling or book name files if desired
- **Size Limits**: 16MB maximum for optional files

### Book Selection
- **Select All/None**: Quick selection buttons
- **Old Testament**: Select all 39 OT books
- **New Testament**: Select all 27 NT books
- **Individual Selection**: Check/uncheck specific books

### Results & Downloads
- **Progress Logs**: View real-time conversion progress
- **Individual Downloads**: Download specific book files
- **ZIP Package**: Get all files in one download
- **Error Reporting**: Detailed error messages and troubleshooting

## Troubleshooting

### Common Issues

#### Optional File Upload Problems
- **File too large**: Maximum size is 16MB for optional files
- **Wrong format**: Only TSV and XML files are accepted for optional files
- **Encoding issues**: Ensure optional files are UTF-8 encoded

#### Conversion Errors
- **Missing BSB data**: Ensure `data/bsb_tables.csv` exists and is accessible
- **Invalid book codes**: Check that book codes match expected format
- **Memory issues**: Converting all 66 books may require sufficient system memory

#### Web Interface Issues
- **Port in use**: Change port in `web/app.py` or stop other services
- **Permission denied**: Ensure write permissions for `web/uploads/` and `web/outputs/`
- **BSB data not found**: Verify `data/bsb_tables.csv` exists
- **Module not found**: Run `./setup_web.sh` to install dependencies

### Solutions

1. **Check BSB data file**:
   ```bash
   file data/bsb_tables.csv  # Should show text/csv or similar
   ```

2. **Verify BSB data encoding**:
   ```bash
   file -bi data/bsb_tables.csv  # Should include charset=utf-8
   ```

3. **Test Python modules**:
   ```bash
   source venv/bin/activate
   python3 -c "import usfmtc, flask, regex; print('All modules OK')"
   ```

4. **Check permissions**:
   ```bash
   ls -la web/uploads/ web/outputs/
   ```

### Getting Help

1. **Check the logs**: 
   - Web interface: Look at the conversion log in the results page
   - Command line: Error messages are printed to the console

2. **Validate your files**:
   - Ensure `data/bsb_tables.csv` exists and has the correct structure
   - Verify optional customization files are properly formatted

3. **Test with minimal data**:
   - Try converting a single book first: `-b GEN`
   - Start with a few books before attempting the complete Bible

## API Reference

### Command Line Arguments

```
python3 bsb2usfm.py data/bsb_tables.csv [OPTIONS]

Arguments:
  data/bsb_tables.csv   Fixed BSB tables file (complete Berean Study Bible data)

Options:
  -o, --outfile        Output file template with % for book code
  -f, --fnotes         Footnote styling TSV file
  -b, --book           Book code to include (can be repeated)
  -n, --names          BookNames.xml file
  -h, --help           Show help message
```

### Web API Endpoints

- `GET /` - Main configuration form
- `POST /convert` - Process conversion with optional file uploads
- `GET /download/<job_id>` - Download ZIP of all results
- `GET /download_single/<job_id>/<filename>` - Download single file
- `GET /api/books` - Get list of available book codes (JSON)
- `GET /health` - Health check endpoint

## Development

### Project Structure

```
bsb2usfm-py/
├── bsb2usfm.py           # Main conversion script
├── getirefs.py           # Additional utility script
├── run_web.py            # Web server launcher
├── setup_web.sh          # Setup script
├── requirements.txt      # Python dependencies
├── README.md            # This file
├── data/                # BSB data source
│   └── bsb_tables.csv   # Complete BSB tables (fixed file)
├── web/                 # Web interface
│   ├── app.py           # Flask application
│   ├── templates/       # HTML templates
│   │   ├── index.html   # Main form
│   │   └── result.html  # Results page
│   ├── static/         # CSS, JS, images
│   │   └── style.css   # Custom styles
│   ├── uploads/        # Optional file uploads
│   └── outputs/        # Generated USFM files
└── venv/               # Python virtual environment
```

### Running in Development Mode

1. **Activate virtual environment**:
   ```bash
   source venv/bin/activate
   ```

2. **Start with debug mode**:
   ```bash
   cd web
   FLASK_ENV=development python3 app.py
   ```

3. **Run tests**:
   ```bash
   python3 -m pytest  # If tests are available
   ```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## Dependencies

### Core Dependencies
- **usfmtc**: USFM processing library
- **regex**: Advanced pattern matching
- **Flask**: Web framework
- **Werkzeug**: File upload handling

### Full Requirements
See `requirements.txt` for complete list with versions.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- **USFM Technical Committee** for the usfmtc library
- **Flask Team** for the web framework
- **Berean Study Bible** for the original data format
- **Bootstrap** and **Font Awesome** for web interface styling

## Version History

### v1.0.0
- Initial command-line interface
- Basic BSB to USFM conversion
- Support for footnotes and custom book names

### v2.0.0
- Added web interface with fixed BSB data source
- Book selection interface for all 66 books
- Optional file uploads for customization
- ZIP download support
- Real-time progress monitoring
- Responsive design
- Setup automation scripts

---

**Questions or Issues?** Please check the troubleshooting section above or create an issue in the project repository.