# BSB to USFM Web Interface

A user-friendly web interface for converting Berean Study Bible (BSB) tables to USFM (Unified Standard Format Markers) format.

## Features

- **Easy File Upload**: Drag-and-drop interface for uploading BSB table files
- **Book Selection**: Choose specific books or convert entire Bible
- **Optional Files**: Support for footnote styling and custom book names
- **Real-time Progress**: View conversion progress and logs
- **Download Results**: Get individual USFM files or a complete ZIP package
- **Responsive Design**: Works on desktop, tablet, and mobile devices

## Quick Start

1. **Start the Web Server**:
   ```bash
   python3 run_web.py
   ```

2. **Open Your Browser**: Navigate to http://localhost:5000

3. **Upload Files**: 
   - Required: BSB tables file (CSV/TSV format)
   - Optional: Footnote styling file (TSV)
   - Optional: Book names file (XML)

4. **Configure Options**:
   - Set output file template
   - Select specific books (or leave empty for all books)

5. **Convert**: Click "Convert to USFM" and wait for results

6. **Download**: Get your USFM files as individual downloads or ZIP package

## File Requirements

### Required Files

- **BSB Tables File**: The main data file containing scripture text and metadata
  - Format: CSV or TSV
  - Encoding: UTF-8 recommended
  - Size limit: 16MB

### Optional Files

- **Footnote Styling File**: TSV file with footnote formatting rules
- **Book Names File**: XML file with custom book names and abbreviations

## Configuration Options

### Output Template
- Use `%` as a placeholder for book codes
- Example: `output_%.usfm` becomes `output_GEN.usfm`, `output_MAT.usfm`, etc.

### Book Selection
- **All Books**: Leave selection empty to convert all available books
- **Old Testament**: Click "Old Testament" button for quick selection
- **New Testament**: Click "New Testament" button for quick selection
- **Custom**: Select individual books using checkboxes

## Supported Book Codes

| Code | Book Name | Code | Book Name |
|------|-----------|------|-----------|
| GEN | Genesis | MAT | Matthew |
| EXO | Exodus | MRK | Mark |
| LEV | Leviticus | LUK | Luke |
| NUM | Numbers | JHN | John |
| DEU | Deuteronomy | ACT | Acts |
| JOS | Joshua | ROM | Romans |
| JDG | Judges | 1CO | 1 Corinthians |
| RUT | Ruth | 2CO | 2 Corinthians |
| ... | ... | ... | ... |

*See the web interface for the complete list of available books.*

## API Endpoints

The web interface also provides REST API endpoints:

- `GET /api/books` - Get list of available book codes
- `GET /health` - Health check endpoint

## Directory Structure

```
web/
├── app.py              # Main Flask application
├── templates/          # HTML templates
│   ├── index.html      # Main upload form
│   └── result.html     # Results page
├── static/             # Static assets (CSS, JS, images)
├── uploads/            # Temporary upload storage
└── outputs/            # Generated USFM files
```

## Troubleshooting

### Common Issues

1. **File Upload Fails**
   - Check file format (must be CSV, TSV, or XML)
   - Ensure file size is under 16MB
   - Verify file encoding is UTF-8

2. **Conversion Errors**
   - Review the error log in the results page
   - Check that BSB tables file has required columns
   - Ensure footnote/names files are properly formatted

3. **Download Problems**
   - Files are automatically cleaned up after some time
   - Try refreshing the page and converting again
   - Check browser download settings

### Server Issues

1. **Port Already in Use**
   - Change port in `app.py`: `app.run(port=5001)`
   - Or stop other services using port 5000

2. **Permission Errors**
   - Ensure write permissions for `uploads/` and `outputs/` directories
   - Run with appropriate user permissions

## Security Notes

- Files are stored temporarily and should be cleaned up regularly
- The web interface is designed for local use
- For production deployment, consider:
  - Adding authentication
  - Setting up HTTPS
  - Configuring proper file permissions
  - Adding rate limiting

## Development

### Running in Debug Mode

Edit `app.py` and set `debug=True`:
```python
app.run(debug=True, host='0.0.0.0', port=5000)
```

### Adding New Features

1. Backend: Modify `app.py`
2. Frontend: Update templates in `templates/`
3. Styling: Add CSS to template `<style>` sections or create external files in `static/`

## Dependencies

See `requirements.txt` for complete list:
- Flask (web framework)
- usfmtc (USFM processing library)
- regex (pattern matching)
- werkzeug (file upload handling)

## License

This web interface follows the same license as the main BSB2USFM project.