# BSB2USFM Web Service Files

This folder contains all files needed to run BSB2USFM as a web service using Docker.

## 📁 Files in This Folder

### Application Files
- **`webapp.py`** - Flask web application (main web service)
- **`templates/`** - HTML templates for web interface
- **`static/`** - Static assets (CSS, JS, images)

### Docker Configuration
- **`Dockerfile`** - Docker image definition
- **`docker-compose.yml`** - Docker Compose configuration
- **`docker-run.sh`** - Convenience script for Docker operations
- **`.dockerignore`** - Files to exclude from Docker build

### Documentation
- **`README-WebService.md`** - Web service features and usage
- **`README-Docker.md`** - Docker setup and commands
- **`WEB-SERVICE-IMPLEMENTATION.md`** - Technical implementation details
- **`INDEX.md`** - This file (navigation guide)

---

## 🚀 Quick Start

### Option 1: Using docker-compose (Recommended)

```bash
# From project root
cd web_service
docker-compose up -d web

# Access web interface
open http://localhost:5000

# Stop service
docker-compose down
```

### Option 2: Using docker-run.sh

```bash
# From project root
cd web_service
chmod +x docker-run.sh

# Start web service
./docker-run.sh web

# View logs
./docker-run.sh web-logs

# Stop service
./docker-run.sh web-stop
```

---

## 📚 Documentation Guide

### When to Read Each File

| File | When to Use |
|------|-------------|
| **README-WebService.md** | Learn about web interface features |
| **README-Docker.md** | Docker setup and commands |
| **WEB-SERVICE-IMPLEMENTATION.md** | Technical details, API endpoints |
| **INDEX.md** | Navigation (this file) |

---

## 🌐 Web Interface Features

- ✅ **Convert Button** - One-click Bible conversion
- ✅ **Output Format Selection** - USFM, USX, or USJ
- ✅ **Conversion Options** - Interlinear, Placeholders, Brackets
- ✅ **Real-time Progress** - Live conversion updates
- ✅ **Download ZIP** - Get all 66 books in one file
- ✅ **Health Check** - `/health` endpoint

---

## 🐳 Docker Commands Reference

### Build and Run
```bash
# Build image
docker-compose build web

# Start service
docker-compose up -d web

# View logs
docker-compose logs -f web

# Stop service
docker-compose down
```

### Check Status
```bash
# Health check
curl http://localhost:5000/health

# View running containers
docker-compose ps

# Execute commands in container
docker-compose exec web bash
```

---

## 📡 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Web interface |
| `/health` | GET | Health check |
| `/api/status` | GET | Conversion status |
| `/api/update` | POST | Start conversion |
| `/api/download` | GET | Download ZIP |
| `/api/results` | GET | List generated files |
| `/api/progress/stream` | GET | Real-time progress (SSE) |

---

## 🔧 Configuration

### Port Configuration
Default: `5000` (configurable via `PORT` environment variable)

### Volume Mounts
- `../data` → `/app/input` (read-only)
- `../results` → `/app/output` (read-write)
- `../demo_data` → `/app/demo_data` (read-only)

### Environment Variables
- `PORT` - Web service port (default: 5000)
- `PYTHONUNBUFFERED` - Enable real-time output
- `PYTHONDONTWRITEBYTECODE` - Prevent .pyc files

---

## 🧪 Testing Locally

### Full Test Workflow
```bash
cd web_service
docker-compose up -d web

# Wait for service to start (3-5 seconds)
sleep 5

# Test health
curl http://localhost:5000/health

# Open browser
open http://localhost:5000

# Complete workflow:
# 1. Select format (USFM/USX/USJ)
# 2. Check options if desired
# 3. Click "Convert"
# 4. Wait 2-5 minutes
# 5. Click "Download"
# 6. Verify ZIP contains 66 files

# Stop service
docker-compose down
```

---

## 🚨 Troubleshooting

### Service Won't Start
```bash
# Check logs
docker-compose logs web

# Check if port is already in use
lsof -i :5000

# Rebuild image
docker-compose build --no-cache web
docker-compose up -d web
```

### Conversion Fails
```bash
# Check logs during conversion
docker-compose logs -f web

# Check output directory permissions
docker-compose exec web ls -la /app/output/

# Test conversion directly
docker-compose exec web python3 bsb2usfm.py -o /app/output/%.usfm
```

### Can't Access Web Interface
```bash
# Verify service is running
docker-compose ps

# Check health endpoint
curl http://localhost:5000/health

# Check container logs
docker-compose logs web
```

---

## 📂 Directory Structure

```
web_service/
├── webapp.py                       # Flask application
├── templates/
│   └── index.html                 # Web interface
├── static/                        # Static assets (if any)
├── Dockerfile                     # Docker image definition
├── docker-compose.yml             # Docker Compose config
├── docker-run.sh                  # Convenience script
├── .dockerignore                  # Docker build exclusions
├── README-WebService.md           # Web service documentation
├── README-Docker.md               # Docker documentation
├── WEB-SERVICE-IMPLEMENTATION.md  # Technical details
└── INDEX.md                       # This file
```

---

## 🌍 Cloud Deployment

To deploy the web service to the cloud (Render.com):

See the **`../render/`** folder for complete cloud deployment documentation.

Quick link: [../render/DEPLOY-QUICKSTART.md](../render/DEPLOY-QUICKSTART.md)

---

## 🔗 Related Documentation

- **Main README**: [../README.md](../README.md)
- **Cloud Deployment**: [../render/](../render/)
- **CLI Usage**: See main README for command-line usage

---

## 💡 Tips

1. **Always use docker-compose** - Easier than manual Docker commands
2. **Check logs first** - Most issues are visible in logs
3. **Health check is your friend** - Use `/health` to verify service
4. **Volume mounts are important** - Ensure data/results folders exist
5. **Port 5000** - Default port, change in docker-compose.yml if needed

---

## 📞 Need Help?

1. Check logs: `docker-compose logs -f web`
2. Read documentation in this folder
3. Review API endpoints: `/health`, `/api/status`
4. Test conversion script directly in container
5. Check Docker/container status: `docker-compose ps`

---

## ✅ Success Criteria

Your web service is working when:
- ☑ Container starts without errors
- ☑ Health endpoint returns `{"status":"healthy"}`
- ☑ Web interface loads at http://localhost:5000
- ☑ Can complete full conversion workflow
- ☑ Download produces valid ZIP with 66 files
- ☑ All three formats work (USFM, USX, USJ)

---

**All web service files are in this folder (`web_service/`).**
**For cloud deployment, see the `render/` folder.**