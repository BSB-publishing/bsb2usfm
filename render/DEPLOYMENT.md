# BSB2USFM Render.com Deployment Guide

This guide will help you deploy the BSB2USFM web service to Render.com with their free tier. All debugging and testing should be done locally before deploying.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Local Testing](#local-testing)
3. [Render.com Deployment](#rendercom-deployment)
4. [Environment Variables](#environment-variables)
5. [Monitoring & Debugging](#monitoring--debugging)
6. [Troubleshooting](#troubleshooting)
7. [Production Best Practices](#production-best-practices)

---

## Prerequisites

Before deploying, ensure you have:

- ✅ Git repository (GitHub, GitLab, or Bitbucket)
- ✅ Docker installed locally for testing
- ✅ Render.com account (free tier)
- ✅ Code committed and pushed to your repository

## Local Testing

**ALWAYS test locally before deploying to cloud!**

### 1. Test Docker Build

```bash
docker-compose build web
```

### 2. Test Docker Run

```bash
docker-compose up -d web
```

### 3. Test Health Endpoint

```bash
curl http://localhost:5000/health
```

Expected response:
```json
{
  "status": "healthy",
  "environment": "development",
  "conversion_running": false,
  "timestamp": "2025-10-30T10:27:13.097746"
}
```

### 4. Test Full Conversion

1. Open http://localhost:5000 in browser
2. Select output format (USFM, USX, or USJ)
3. Check any desired options (Interlinear, Placeholders, Brackets)
4. Click "Convert" and wait for completion (2-5 minutes)
5. Click download button to get ZIP file
6. Verify ZIP contains all 66 Bible books

### 5. Test All Output Formats

```bash
# Test USFM (default)
curl -X POST http://localhost:5000/api/update -H "Content-Type: application/json" -d '{"format":"usfm"}'

# Test USX
curl -X POST http://localhost:5000/api/update -H "Content-Type: application/json" -d '{"format":"usx"}'

# Test USJ
curl -X POST http://localhost:5000/api/update -H "Content-Type: application/json" -d '{"format":"usj"}'
```

### 6. Stop Local Docker

```bash
docker-compose down
```

---

## Render.com Deployment

### Why Render.com?

- ✅ 750 free hours per month (enough for 1 service running 24/7)
- ✅ Automatic deploys from Git
- ✅ Native Docker support
- ✅ Easy setup with zero configuration
- ✅ Free SSL/HTTPS
- ✅ Simple dashboard and logs

### Free Tier Limitations

- ⚠️ Service spins down after 15 minutes of inactivity
- ⚠️ First request after spin-down takes ~30 seconds to wake up
- ⚠️ 750 hours/month limit (enough for 1 service running 24/7)
- ℹ️ Persistent disk: 1GB free (enough for output files)
- ℹ️ Memory: 512 MB
- ℹ️ Shared CPU (conversion takes 3-5 minutes)

### Step-by-Step Deployment

#### 1. Push Code to Git Repository

```bash
git add .
git commit -m "Prepare for deployment"
git push origin main
```

#### 2. Sign Up for Render.com

1. Go to https://render.com
2. Sign up with GitHub/GitLab account (recommended)
3. Verify email

#### 3. Create New Web Service

1. Click "New +" → "Web Service"
2. Connect your Git repository
3. Select the `bsb2usfm` repository

#### 4. Configure Service

**Basic Settings:**
- **Name**: `bsb2usfm-converter` (or your choice)
- **Region**: Choose closest to your users
- **Branch**: `main` (or your default branch)
- **Root Directory**: Leave empty (or set to `bsb2usfm` if it's in a subdirectory)

**Build & Deploy:**
- **Environment**: `Docker`
- **Dockerfile Path**: `./Dockerfile`
- **Docker Build Context Directory**: `.`

**Instance Type:**
- **Plan**: `Free`

#### 5. Advanced Settings

**Health Check Path:**
```
/health
```

**Auto-Deploy:**
- Enable "Auto-Deploy" for automatic updates from Git

#### 6. Add Environment Variables

In the "Environment" tab, the following are usually auto-detected but you can add them if needed:

- `PORT`: `5000`
- `PYTHONUNBUFFERED`: `1`
- `PYTHONDONTWRITEBYTECODE`: `1`

#### 7. Deploy

1. Click "Create Web Service"
2. Wait 5-10 minutes for initial build
3. Watch build logs for any errors
4. Service will show "Live" when ready

#### 8. Test Deployment

Once deployed, Render provides a URL like:
```
https://bsb2usfm-converter.onrender.com
```

Test it:
```bash
curl https://bsb2usfm-converter.onrender.com/health
```

Expected response:
```json
{
  "status": "healthy",
  "environment": "production",
  "conversion_running": false,
  "timestamp": "2025-10-30T10:27:13.097746"
}
```

### Using render.yaml (Alternative Method)

The `render.yaml` file is included in your repository. Render can auto-detect it:

1. Go to Render Dashboard
2. Click "New +" → "Blueprint"
3. Connect repository
4. Render will auto-detect `render.yaml`
5. Click "Apply"

The configuration in `render.yaml`:
```yaml
services:
  - type: web
    name: bsb2usfm-converter
    env: docker
    plan: free
    healthCheckPath: /health
    disk:
      name: bsb2usfm-data
      mountPath: /app/output
      sizeGB: 1
```

---

## Environment Variables

### Required Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `PORT` | `5000` | Port the web service listens on (auto-detected by Render) |
| `PYTHONUNBUFFERED` | `1` | Enable real-time Python output |
| `PYTHONDONTWRITEBYTECODE` | `1` | Prevent .pyc file creation |

### Optional Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `PYTHONPATH` | `/app` | Python module search path |

Render automatically injects:
- `RENDER`: `true` (identifies Render environment)
- `RENDER_SERVICE_NAME`: Your service name
- `RENDER_EXTERNAL_URL`: Your service URL

---

## Monitoring & Debugging

### Local Debugging (ALWAYS DO THIS FIRST)

#### 1. Check Docker Logs

```bash
docker-compose logs -f web
```

#### 2. Execute Commands in Container

```bash
docker-compose exec web bash
```

#### 3. Test Individual Components

```bash
# Test conversion script directly
docker-compose exec web python3 bsb2usfm.py -o /app/output/%.usfm

# Check output files
docker-compose exec web ls -lh /app/output/

# Test webapp endpoints
curl http://localhost:5000/api/status
curl http://localhost:5000/api/results
```

#### 4. Check File Permissions

```bash
docker-compose exec web ls -la /app/output/
```

### Cloud Debugging (After Local Testing)

#### View Logs on Render

1. Go to your service dashboard on Render.com
2. Click "Logs" tab
3. Watch real-time logs
4. Use search to filter logs

#### Shell Access

1. Click "Shell" tab in dashboard
2. Run commands interactively:
```bash
ls -lh /app/output/
python3 --version
env | grep RENDER
```

#### Manual Deploy

Trigger a manual deployment:
1. Go to service dashboard
2. Click "Manual Deploy" → "Deploy latest commit"
3. Or commit to Git (auto-deploys if enabled)

#### Check Service Status

Dashboard shows:
- **Live**: Service is running
- **Build**: Currently building
- **Failed**: Build or deploy failed (check logs)

---

## Troubleshooting

### Common Issues

#### 1. Build Fails

**Symptom:** Docker build errors during deployment

**Solution:**
1. Test build locally first:
   ```bash
   docker-compose build web
   ```
2. Check Dockerfile syntax
3. Verify all files are committed to Git
4. Check `.dockerignore` isn't excluding needed files
5. Review build logs in Render dashboard

#### 2. Service Won't Start

**Symptom:** Service fails health checks or crashes

**Solution:**
1. Test locally:
   ```bash
   docker-compose up web
   curl http://localhost:5000/health
   ```
2. Check logs for errors in Render dashboard
3. Verify PORT environment variable
4. Ensure webapp.py binds to `0.0.0.0` not `127.0.0.1`
5. Check memory usage (512MB limit on free tier)

#### 3. Conversion Fails

**Symptom:** Conversion starts but fails or hangs

**Solution:**
1. Test locally with same options
2. Check output directory permissions
3. Verify internet access (needs to download BSB tables)
4. Check memory limits (conversion needs ~500MB)
5. Review logs during conversion
6. Verify disk space available (1GB free tier)

#### 4. Download Fails

**Symptom:** Can't download ZIP file

**Solution:**
1. Test locally:
   ```bash
   curl -O http://localhost:5000/api/download
   ```
2. Check if files were generated:
   ```bash
   # In Render Shell tab
   ls -lh /app/output/
   ```
3. Verify disk space available
4. Check file permissions in output directory

#### 5. Slow Performance

**Symptom:** Conversion takes very long

**Solution:**
- Free tier has limited CPU (shared)
- Conversion typically takes 3-5 minutes on free tier
- This is expected behavior
- Consider upgrading to paid tier ($7/month) for faster CPU

#### 6. Service Sleeping

**Symptom:** First request takes 30 seconds

**Solution:**
- This is normal on free tier
- Service spins down after 15 minutes of inactivity
- First request wakes it up (~30 seconds)
- Subsequent requests are fast
- Upgrade to paid tier for always-on service

#### 7. Out of Memory

**Symptom:** Process killed during conversion

**Solution:**
- Free tier has 512MB RAM
- Conversion needs ~500MB
- Try clearing old files first
- Or upgrade to paid tier (more memory)

### Debug Checklist

Before asking for help, verify:

- [ ] Works perfectly on local Docker
- [ ] All tests pass locally
- [ ] Git repository is up to date
- [ ] Environment variables are set correctly
- [ ] Health check endpoint responds: `/health`
- [ ] Logs show specific error messages
- [ ] Sufficient memory/disk space
- [ ] Network connectivity works

---

## Production Best Practices

### 1. Use Git Tags for Releases

```bash
git tag -a v1.0.0 -m "Production release v1.0.0"
git push origin v1.0.0
```

In Render, you can deploy specific tags from the dashboard.

### 2. Monitor Service Health

Set up monitoring:
- **Uptime monitoring**: UptimeRobot (free)
  - Monitor your Render URL
  - Get alerts for downtime
  - Track response times
- **Render built-in monitoring**:
  - View metrics in dashboard
  - Memory usage
  - CPU usage
  - Request logs

### 3. Regular Updates

```bash
# Pull latest changes
git pull origin main

# Test locally
docker-compose up -d web
# Run tests...
docker-compose down

# Push to trigger auto-deploy
git push origin main
```

### 4. Backup Strategy

Generated files are temporary, but to backup:
- Download ZIP files regularly
- Store in Git LFS or separate storage
- Document regeneration process

### 5. Security Considerations

For production use:
- Add authentication (not included in free version)
- HTTPS is automatic on Render
- Add rate limiting if needed
- Input validation is already included
- Regular security updates

### 6. Performance Optimization

On free tier:
- Accept 15-minute sleep behavior
- Optimize Docker image size (already done)
- Use persistent disk efficiently
- Clear old files regularly

To improve performance:
- Upgrade to paid tier ($7/month)
- Get dedicated CPU
- Always-on service (no sleep)
- More memory (512MB → 2GB+)

### 7. Cost Management

Free tier is free as long as:
- Stay under 750 hours/month (1 service = 750 hours max)
- Disk under 1GB
- No additional services

Monitor usage in Render dashboard.

---

## Deployment Workflow

```
┌─────────────┐
│ Local Dev   │
│ & Testing   │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ Git Commit  │
│ & Push      │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ Auto Deploy │ (Render auto-detects push)
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ Cloud Build │
│ & Start     │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ Verify &    │
│ Test        │
└─────────────┘
```

---

## Quick Start Summary

### Deployment in 5 Steps

```bash
# 1. Test locally
docker-compose up -d web
# Test in browser at http://localhost:5000
docker-compose down

# 2. Push to Git
git add .
git commit -m "Ready for deployment"
git push origin main

# 3. Deploy on Render.com
# - Go to https://render.com
# - New → Web Service
# - Connect Git repo
# - Choose Docker environment
# - Click "Create Web Service"

# 4. Wait for build (5-10 minutes)

# 5. Test deployment
curl https://your-app.onrender.com/health
```

---

## Performance Expectations

### Free Tier

- **Build time**: 5-10 minutes (first time), 2-5 minutes (subsequent)
- **Startup**: 30 seconds (after sleep)
- **Conversion**: 3-5 minutes (shared CPU)
- **Download**: 5-15 seconds
- **Memory**: 512 MB
- **Storage**: 1 GB

### Paid Tier ($7/month)

- **Build time**: 2-5 minutes
- **Startup**: Instant (always on)
- **Conversion**: 2-3 minutes (dedicated CPU)
- **Download**: <5 seconds
- **Memory**: 2 GB+
- **Storage**: 10 GB+

---

## Support & Resources

### Documentation

- **Render.com Docs**: https://render.com/docs
- **Docker Support**: https://render.com/docs/docker
- **Health Checks**: https://render.com/docs/health-checks
- **Persistent Disks**: https://render.com/docs/disks

### Community

- **Render Community**: https://community.render.com
- **Status Page**: https://status.render.com

### Getting Help

1. Check logs first (locally, then cloud)
2. Review this documentation
3. Search Render community forums
4. Post in community (be specific)
5. Contact Render support (paid plans get priority)

---

## Upgrading to Paid Plan

### When to Upgrade?

Consider upgrading when:
- Need faster conversion (2-3 min vs 3-5 min)
- Want always-on service (no 30s wake time)
- Need more memory (>512MB)
- Higher traffic expected
- Professional use case

### How to Upgrade

1. Go to service dashboard
2. Click "Settings"
3. Select "Starter" plan ($7/month)
4. Confirm upgrade
5. Service upgrades automatically

### Benefits

- ✅ Always on (no sleep)
- ✅ Faster CPU (2x-3x)
- ✅ More memory (2GB+)
- ✅ Priority support
- ✅ Better performance

---

## Conclusion

You're now ready to deploy BSB2USFM to Render.com! Remember:

1. ✅ **ALWAYS test locally first**
2. ✅ Use version control (Git)
3. ✅ Monitor your service
4. ✅ Start with free tier
5. ✅ Upgrade if needed

The free tier is excellent for:
- Personal projects
- Low-to-moderate traffic
- Testing and development
- Sharing with small groups

Good luck with your deployment! 🚀