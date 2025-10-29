# BSB2USFM Web Service

A web-based interface for the BSB2USFM converter that provides a simple, user-friendly way to convert Berean Standard Bible tables to USFM format with real-time progress updates.

## Features

- 🌐 **Web Interface**: Simple, modern UI accessible from any browser
- 🔄 **Real-time Progress**: Server-Sent Events (SSE) for live conversion progress
- 📊 **Status Monitoring**: Track conversion status and view statistics
- 📁 **Results Display**: Automatic listing of generated USFM files
- 🐳 **Docker Ready**: Fully containerized for easy deployment
- 🚀 **One-Click Operation**: Single button to trigger data updates

## Quick Start

### Using Docker Compose (Recommended)

1. **Start the web service:**
   ```bash
   docker-compose up -d web
   ```

2. **Access the web interface:**
   Open your browser and navigate to: http://localhost:5000

3. **Click "Update Data"** to start the conversion process

4. **Stop the service:**
   ```bash
   docker-compose down
   ```

### Using the Docker Run Script

The `docker-run.sh` script provides convenient commands for managing the web service:

```bash
# Start web service
./docker-run.sh web

# View logs
./docker-run.sh web-logs

# Stop web service
./docker-run.sh web-stop
```

## Web Interface

### Main Features

#### Update Data Button
- Click to trigger the BSB to USFM conversion
- Button shows progress indicator during conversion
- Automatically disabled while conversion is running

#### Status Badge
- **Idle**: No conversion running
- **Running**: Conversion in progress (animated)
- **Completed**: Conversion finished successfully
- **Error**: Conversion failed

#### Progress Log
- Real-time streaming of conversion progress
- Color-coded messages (info, success, warning, error)
- Timestamps for each log entry
- Auto-scrolling to latest messages
- Clear button to reset the log

#### Statistics
- **Files Generated**: Count of USFM files created
- **Duration**: Time taken for the conversion

#### Results Display
- Grid view of all generated USFM files
- File names and sizes
- Automatically shown after successful conversion

## API Endpoints

The web service provides REST API endpoints that can be used programmatically:

### Health Check
```bash
GET /health
```
Returns service health status.

### Trigger Update
```bash
POST /api/update
Content-Type: application/json

{
  "output": "/app/output/%.usfm",
  "books": ["GEN", "EXO"],
  "interlinear": false,
  "strongs": false,
  "placeholders": false,
  "brackets": false
}
```
Triggers a new conversion. All fields are optional.

### Get Status
```bash
GET /api/status
```
Returns current conversion status and results.

### Get Progress History
```bash
GET /api/progress
```
Returns full progress log history.

### Stream Progress (SSE)
```bash
GET /api/progress/stream
```
Server-Sent Events stream for real-time progress updates.

### Get Results
```bash
GET /api/results
```
Returns list of generated USFM files with metadata.

## Architecture

### Components

- **Flask Web Server**: Serves the web interface and API endpoints
- **Background Thread**: Runs the conversion process without blocking
- **Server-Sent Events**: Real-time progress streaming to the browser
- **Thread-Safe State**: Shared state management with locks

### Data Flow

1. User clicks "Update Data" button
2. Browser sends POST to `/api/update`
3. Server starts conversion in background thread
4. Browser connects to `/api/progress/stream` for real-time updates
5. Conversion process logs progress via SSE
6. Upon completion, results are fetched and displayed

## Configuration

### Environment Variables

- `PORT`: Web service port (default: 5000)
- `PYTHONPATH`: Python module path (default: /app)
- `PYTHONUNBUFFERED`: Python output buffering (default: 1)

### Volume Mounts

The web service uses the following volume mounts:

- `./data:/app/input` - Input data files (read-only)
- `./results:/app/output` - Output USFM files (read-write)
- `./demo_data:/app/demo_data` - Demo/sample files (read-only)

## Development

### Running Locally (Without Docker)

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Create required directories:**
   ```bash
   mkdir -p data results demo_data
   ```

3. **Run the web service:**
   ```bash
   python3 webapp.py
   ```

4. **Access at:** http://localhost:5000

### File Structure

```
bsb2usfm/
├── webapp.py              # Flask web application
├── templates/
│   └── index.html        # Web interface template
├── static/               # Static files (CSS, JS)
├── bsb2usfm.py          # Core conversion script
├── Dockerfile            # Docker image definition
├── docker-compose.yml    # Docker Compose configuration
└── requirements.txt      # Python dependencies
```

## Customization

### Conversion Options

You can customize the conversion by modifying the POST request to `/api/update`:

```javascript
fetch('/api/update', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    output: '/app/output/%.usfm',
    books: ['GEN', 'EXO', 'MAT'],  // Specific books
    interlinear: true,              // Enable interlinear format
    strongs: true,                  // Include Strong's numbers
    placeholders: true,             // Include placeholders
    brackets: true                  // Include brackets
  })
});
```

### Styling

The web interface uses embedded CSS in `templates/index.html`. To customize:

1. Edit the `<style>` section in `index.html`
2. Modify colors, fonts, or layout
3. Rebuild the Docker image

### Progress Messages

To modify how progress is logged, edit the `log_progress()` function in `webapp.py`:

```python
def log_progress(message, level='info'):
    """Add a progress message to the queue"""
    # Custom logging logic here
    pass
```

## Troubleshooting

### Port Already in Use

If port 5000 is already in use:

1. **Stop the conflicting service**, or
2. **Change the port** in `docker-compose.yml`:
   ```yaml
   ports:
     - "8080:5000"  # Use port 8080 instead
   ```

### Permission Issues

If you encounter permission errors with output files:

```bash
# Fix ownership (Linux/macOS)
sudo chown -R $USER:$USER results/
```

### Web Service Won't Start

1. **Check if Docker is running:**
   ```bash
   docker info
   ```

2. **Verify image exists:**
   ```bash
   docker images | grep bsb2usfm
   ```

3. **Check logs:**
   ```bash
   docker-compose logs web
   ```

4. **Rebuild the image:**
   ```bash
   docker-compose build web
   docker-compose up -d web
   ```

### Conversion Hangs

If the conversion appears to hang:

1. **Check the logs:**
   ```bash
   ./docker-run.sh web-logs
   ```

2. **Restart the service:**
   ```bash
   docker-compose restart web
   ```

3. **Clear the output directory:**
   ```bash
   rm -rf results/*
   ```

### Progress Not Updating

If progress stops updating in the browser:

1. **Refresh the page** - SSE connections may timeout
2. **Check browser console** for JavaScript errors
3. **Verify network connectivity** to the server
4. **Check server logs** for errors

## Security Considerations

### Production Deployment

For production use, consider:

1. **Enable HTTPS** using a reverse proxy (nginx, Apache)
2. **Add authentication** to restrict access
3. **Set up rate limiting** to prevent abuse
4. **Use environment variables** for sensitive configuration
5. **Run behind a firewall** or VPN
6. **Regular security updates** of dependencies

### Example Nginx Configuration

```nginx
server {
    listen 80;
    server_name bsb2usfm.example.com;

    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        
        # SSE support
        proxy_buffering off;
        proxy_cache off;
        proxy_set_header Connection '';
        proxy_http_version 1.1;
        chunked_transfer_encoding on;
    }
}
```

## Performance

### Optimization Tips

1. **Use SSD storage** for faster file I/O
2. **Allocate sufficient memory** to Docker (at least 2GB)
3. **Mount output directory** on fast storage
4. **Monitor resource usage** with `docker stats`

### Resource Usage

Typical resource requirements:

- **CPU**: 1-2 cores
- **Memory**: 512MB - 1GB
- **Disk**: 100MB + output files
- **Network**: Minimal (downloads BSB tables once)

## Monitoring

### Log Levels

The web service uses the following log levels:

- `info`: General information messages
- `success`: Successful operations
- `warning`: Non-critical issues
- `error`: Critical errors

### Viewing Logs

```bash
# Real-time logs
docker-compose logs -f web

# Last 100 lines
docker-compose logs --tail=100 web

# Since specific time
docker-compose logs --since="2024-01-01T00:00:00" web
```

## Integration

### Webhook Support

To add webhook notifications after conversion, modify `webapp.py`:

```python
def run_conversion(args=None):
    # ... existing code ...
    
    # After successful conversion
    if conversion_state['status'] == 'completed':
        requests.post('https://your-webhook-url.com', json={
            'status': 'completed',
            'files': conversion_state['results']
        })
```

### CI/CD Integration

Example GitHub Actions workflow:

```yaml
name: Convert BSB to USFM
on:
  schedule:
    - cron: '0 0 * * 0'  # Weekly on Sunday

jobs:
  convert:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Start web service
        run: docker-compose up -d web
      - name: Trigger conversion
        run: |
          curl -X POST http://localhost:5000/api/update
          sleep 60  # Wait for completion
      - name: Upload results
        uses: actions/upload-artifact@v3
        with:
          name: usfm-files
          path: results/*.usfm
```

## Support

For issues, questions, or contributions:

- Check the main [README.md](README.md) for general usage
- Review [README-Docker.md](README-Docker.md) for Docker details
- Open an issue on the project repository
- Contact the maintainers

## License

Same as the main BSB2USFM project.