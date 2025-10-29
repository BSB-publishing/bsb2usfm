# Quick Start Guide - BSB2USFM Web Service

Get up and running with the BSB2USFM web interface in under 5 minutes!

## Prerequisites

- Docker installed and running
- Git (to clone the repository)
- A web browser

## Step 1: Get the Code

```bash
git clone <repository-url>
cd bsb2usfm
git checkout web-service
```

## Step 2: Start the Web Service

### Option A: Using the Helper Script (Recommended)

```bash
chmod +x docker-run.sh
./docker-run.sh web
```

### Option B: Using Docker Compose Directly

```bash
docker-compose up -d web
```

## Step 3: Access the Web Interface

Open your web browser and navigate to:

**http://localhost:5000**

You should see the BSB2USFM Converter web interface!

## Step 4: Convert Data

1. Click the big **"Update Data"** button
2. Watch the real-time progress in the log window
3. Wait for the conversion to complete (usually 30-60 seconds)
4. View the generated USFM files in the results section

## Step 5: Access Your Files

The converted USFM files are located in:

```bash
./results/*.usfm
```

You can also see them listed in the web interface after conversion completes.

## Managing the Service

### View Logs

```bash
./docker-run.sh web-logs
```

Or press `Ctrl+C` to stop following logs.

### Stop the Service

```bash
./docker-run.sh web-stop
```

### Restart the Service

```bash
./docker-run.sh web-stop
./docker-run.sh web
```

## Troubleshooting

### Port 5000 is Already in Use

Edit `docker-compose.yml` and change the port:

```yaml
ports:
  - "8080:5000"  # Use port 8080 instead
```

Then access at http://localhost:8080

### Cannot Access the Web Interface

1. Check if the container is running:
   ```bash
   docker ps | grep bsb2usfm_web
   ```

2. Check the logs:
   ```bash
   ./docker-run.sh web-logs
   ```

3. Rebuild and restart:
   ```bash
   docker-compose down
   docker-compose build web
   docker-compose up -d web
   ```

### Permission Denied on Results Folder

```bash
# Linux/macOS
sudo chown -R $USER:$USER results/

# Or create the directory first
mkdir -p results
chmod 755 results
```

## What's Happening?

When you click "Update Data", the web service:

1. **Downloads** the latest BSB tables from https://bereanbible.com/bsb_tables.tsv
2. **Converts** all books to USFM 3.1 format
3. **Generates** individual `.usfm` files for each book
4. **Displays** progress and results in real-time

## Next Steps

- **Read the full documentation**: [README-WebService.md](README-WebService.md)
- **Customize conversion options**: Use the API endpoints
- **Automate**: Set up scheduled conversions
- **Integrate**: Connect to your Bible publishing workflow

## Command Line Alternative

If you prefer the command line interface:

```bash
# Build the image
./docker-run.sh build

# Convert all books
./docker-run.sh convert -o results/%.usfm

# Convert specific books
./docker-run.sh convert -o results/%.usfm -b GEN -b EXO -b MAT
```

See [README-Docker.md](README-Docker.md) for more CLI options.

## Support

Need help? Check:

- [README-WebService.md](README-WebService.md) - Detailed web service docs
- [README-Docker.md](README-Docker.md) - Docker configuration
- [README.md](README.md) - General usage guide

---

**Happy Converting! 📖✨**