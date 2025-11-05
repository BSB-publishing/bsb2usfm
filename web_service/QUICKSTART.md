# BSB2USFM Web Service - Quick Start Guide

Get the BSB2USFM web service running in under 5 minutes!

## 🚀 Fastest Path to Running

### Option 1: Local Docker (Recommended for Testing)

```bash
# 1. Navigate to web service directory
cd web_service

# 2. Start the service
docker-compose up -d web

# 3. Open in browser
open http://localhost:5000
# Or visit: http://localhost:5000

# 4. Click "Update Data" to start conversion
```

That's it! The web interface is now running locally.

### Option 2: Deploy to Render (Easiest Cloud Deploy)

```bash
# 1. Push your code to GitHub
git add .
git commit -m "Ready to deploy"
git push origin main

# 2. Go to https://render.com
# 3. Click "New +" → "Blueprint"
# 4. Connect your GitHub repository
# 5. Render auto-detects render/render.yaml
# 6. Click "Apply"

# Done! Your service will be live at:
# https://bsb2usfm-converter.onrender.com
```

## ✅ Verify It's Working

### Check Health Endpoint

```bash
# Local
curl http://localhost:5000/health

# Render
curl https://your-app.onrender.com/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T12:34:56",
  "environment": "production",
  "conversion_running": false
}
```

### Test Conversion

1. Open the web interface in your browser
2. Click the **"Update Data"** button
3. Watch the real-time progress log
4. See generated files listed after completion

## 🎯 What You Get

- 🌐 **Web Interface**: User-friendly browser-based UI
- 🔄 **Real-Time Progress**: Live streaming conversion status
- 📁 **File Management**: Automatic listing and download of results
- 💾 **Persistent Storage**: Generated files are saved
- 🚀 **Production Ready**: Gunicorn WSGI server included

## 📋 Common Tasks

### Start Service
```bash
docker-compose up -d web
```

### Stop Service
```bash
docker-compose down
```

### View Logs
```bash
docker-compose logs -f web
```

### Restart Service
```bash
docker-compose restart web
```

### Update Code
```bash
git pull origin main
docker-compose down
docker-compose build --no-cache web
docker-compose up -d web
```

## 🔧 Configuration

### Change Port (Local)

Edit `docker-compose.yml`:
```yaml
ports:
  - "8080:5000"  # Change 8080 to your preferred port
```

### Environment Variables

The service uses these environment variables:

| Variable | Default | Purpose |
|----------|---------|---------|
| `PORT` | 5000 | Web service port |
| `PYTHONUNBUFFERED` | 1 | Real-time logging |

## 🐛 Troubleshooting

### Port Already in Use

```bash
# Find and kill the process
sudo lsof -i :5000
sudo kill -9 <PID>

# Or change the port in docker-compose.yml
```

### Container Won't Start

```bash
# View detailed logs
docker-compose logs web

# Rebuild from scratch
docker-compose down
docker-compose build --no-cache web
docker-compose up web  # Without -d to see errors
```

### Permission Errors

```bash
# Fix ownership of results directory
sudo chown -R $USER:$USER ../results/
```

## 📚 Next Steps

### For More Details

- **Full Deployment Guide**: [DEPLOY_Docker.md](DEPLOY_Docker.md)
- **Quick Reference**: [DEPLOY_QUICKREF.md](DEPLOY_QUICKREF.md)
- **API Documentation**: [README-WebService.md](README-WebService.md)
- **Developer Guide**: [../README_developer.md](../README_developer.md)

### Deploy to Production

Choose your platform:

1. **Render** (Easiest): See [DEPLOY_Docker.md - Render](DEPLOY_Docker.md#rendercom)
2. **Digital Ocean** (Full Control): See [DEPLOY_Docker.md - DO](DEPLOY_Docker.md#digital-ocean-droplet)

### Run Deployment Check

```bash
# Verify everything is ready
./check_deployment.sh
```

## 💡 Tips

### Use Demo Data

The web service automatically downloads BSB tables from bereanbible.com, but you can also:

```bash
# Use local demo data or download from URL
# The web service automatically downloads BSB tables
# Demo data is already mounted in docker-compose.yml
```

### Monitor Resources

```bash
# Check Docker resource usage
docker stats bsb2usfm_web

# Check disk space
df -h

# Check results size
du -sh ../results/
```

### Backup Results

```bash
# Create backup archive
tar -czf backup-$(date +%Y%m%d).tar.gz ../results/

# Or use the web interface
# Visit http://localhost:5000 and click "Download Zip"
```

## 🆘 Getting Help

1. **Check logs**: `docker-compose logs -f web`
2. **Health check**: `curl http://localhost:5000/health`
3. **Run diagnostics**: `./check_deployment.sh`
4. **Read full guide**: [DEPLOY_Docker.md](DEPLOY_Docker.md)
5. **Review API docs**: [README-WebService.md](README-WebService.md)

## 🎉 Success Checklist

- [ ] Service starts without errors
- [ ] Health endpoint returns `"status": "healthy"`
- [ ] Web interface loads in browser
- [ ] "Update Data" button triggers conversion
- [ ] Progress log shows real-time updates
- [ ] Files are generated in results directory
- [ ] Can download generated files

If all checks pass, you're ready to deploy to production! 🚀

---

**Quick Links**:
- 📖 [Full Deployment Guide](DEPLOY_Docker.md)
- 📋 [Deployment Index](DEPLOYMENT_INDEX.md)
- 🔍 [Quick Reference](DEPLOY_QUICKREF.md)
- 🌐 [Web Service Docs](README-WebService.md)
- 💻 [Developer Guide](../README_developer.md)

**Need Help?** Check the troubleshooting section above or review the full deployment documentation.