# BSB2USFM Render.com Deployment - Quick Start

## 🚀 Deploy in 5 Minutes

### Prerequisites
- GitHub/GitLab account
- Code pushed to repository
- Docker installed locally

---

## Step-by-Step Deployment

### Step 1: Test Locally (MANDATORY!)

```bash
# Build and start
docker-compose build web
docker-compose up -d web

# Test health
curl http://localhost:5000/health

# Test in browser
open http://localhost:5000
```

**Complete test workflow:**
1. Select format (USFM/USX/USJ)
2. Optionally check conversion options
3. Click "Convert"
4. Wait 2-5 minutes for completion
5. Click "Download" button
6. Verify ZIP contains 66 Bible books
7. Stop Docker: `docker-compose down`

---

### Step 2: Push to Git

```bash
git add .
git commit -m "Ready for Render deployment"
git push origin main
```

---

### Step 3: Deploy on Render.com

1. **Go to**: https://render.com
2. **Sign up** with GitHub/GitLab
3. **New +** → **Web Service**
4. **Connect** your repository
5. **Configure**:
   - Name: `bsb2usfm-converter` (or your choice)
   - Environment: `Docker`
   - Plan: `Free`
   - Health Check Path: `/health`
6. **Click**: Create Web Service
7. **Wait**: 5-10 minutes for build
8. **Done!** ✅

---

### Step 4: Test Deployment

```bash
# Check health (replace with your URL)
curl https://your-app.onrender.com/health

# Expected response:
# {
#   "status": "healthy",
#   "environment": "production",
#   "conversion_running": false
# }
```

Open in browser:
```
https://your-app.onrender.com
```

---

## 🐛 Local Debugging (ALWAYS DO THIS FIRST!)

### View Logs
```bash
docker-compose logs -f web
```

### Check Generated Files
```bash
docker-compose exec web ls -lh /app/output/
```

### Test Conversion Directly
```bash
docker-compose exec web python3 bsb2usfm.py -o /app/output/%.usfm
```

### Access Shell
```bash
docker-compose exec web bash
```

---

## 📊 What You Get (Free Tier)

| Feature | Details |
|---------|---------|
| **Cost** | Free (750 hrs/month) |
| **Memory** | 512 MB |
| **Storage** | 1 GB persistent disk |
| **CPU** | Shared (conversion ~3-5 min) |
| **Sleep** | After 15 min inactivity |
| **Wake Time** | ~30 seconds |
| **HTTPS** | Automatic ✅ |
| **Auto-Deploy** | From Git ✅ |

---

## 🔧 Configuration

### render.yaml
The `render.yaml` file is already included. Render auto-detects it.

### Environment Variables
Usually auto-detected, but you can set manually in Render dashboard:
- `PORT`: `5000`
- `PYTHONUNBUFFERED`: `1`
- `PYTHONDONTWRITEBYTECODE`: `1`

---

## ✅ Post-Deployment Checklist

- [ ] Service shows "Live" in Render dashboard
- [ ] Health endpoint responds: `/health`
- [ ] Web UI loads at your Render URL
- [ ] Can start conversion
- [ ] Conversion completes successfully
- [ ] Can download ZIP file
- [ ] ZIP contains 66 files
- [ ] Tested all formats (USFM, USX, USJ)

---

## 🆘 Troubleshooting

### Build Fails
```bash
# Test locally first
docker-compose build web
# Check Render build logs in dashboard
```

### Service Won't Start
```bash
# Test locally
docker-compose up web
# Check Render logs in dashboard
```

### Conversion Fails
```bash
# Test locally with same options
docker-compose exec web python3 bsb2usfm.py -o /app/output/%.usfm
```

### Slow Performance
- Expected on free tier (3-5 min conversion)
- Shared CPU limitations
- Consider upgrading to paid tier ($7/month) for 2x-3x speed

### Service Sleeping
- Normal behavior on free tier
- Sleeps after 15 min inactivity
- First request takes ~30 seconds to wake
- Subsequent requests are fast

---

## 📚 More Documentation

- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Complete Render deployment guide
- **[deployment-checklist.md](deployment-checklist.md)** - Full checklist
- **[README.md](README.md)** - Overview
- **[QUICKREF.txt](QUICKREF.txt)** - Quick reference card

---

## 🎯 Quick Commands Reference

### Local Development
```bash
docker-compose build web              # Build image
docker-compose up -d web              # Start service
docker-compose logs -f web            # View logs
docker-compose exec web bash          # Shell access
docker-compose down                   # Stop service
curl http://localhost:5000/health     # Test health
```

### Render Dashboard
- **View Logs**: Dashboard → Logs tab
- **Shell Access**: Dashboard → Shell tab
- **Manual Deploy**: Dashboard → Manual Deploy button
- **Settings**: Dashboard → Settings tab

### Testing
```bash
# Health check
curl https://your-app.onrender.com/health

# Trigger conversion via API
curl -X POST https://your-app.onrender.com/api/update \
  -H "Content-Type: application/json" \
  -d '{"format":"usfm"}'

# Check status
curl https://your-app.onrender.com/api/status

# Download files
curl -O https://your-app.onrender.com/api/download
```

---

## 💡 Tips

1. **Always test locally** before deploying
2. **Enable auto-deploy** for easy updates
3. **Monitor logs** regularly in Render dashboard
4. **Use Git tags** for version tracking
5. **Bookmark your Render URL**
6. **Set up UptimeRobot** for free uptime monitoring

---

## 💰 Upgrading (Optional)

### Free Tier → Starter ($7/month)

**Benefits:**
- ✅ Always on (no sleep)
- ✅ Faster CPU (2x-3x speed)
- ✅ More memory (512MB → 2GB+)
- ✅ Priority support

**How to upgrade:**
1. Dashboard → Settings
2. Select "Starter" plan
3. Confirm
4. Automatic upgrade

---

## 🎉 Success!

Your BSB2USFM converter is now live at:
```
https://your-app.onrender.com
```

**Remember:** Always test locally before deploying! 🧪

---

**Need help?** Check [DEPLOYMENT.md](DEPLOYMENT.md) for detailed documentation.

---

**All files in this folder (`render/`) are for Render.com deployment.**