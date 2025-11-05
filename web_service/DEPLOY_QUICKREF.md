# BSB2USFM Docker Deployment - Quick Reference

Quick reference card for deploying BSB2USFM web service to Render.com or Digital Ocean.

## Pre-Deployment Checklist

```bash
# Run deployment readiness check
./check_deployment.sh

# Test locally
docker-compose up --build web
# Visit http://localhost:5000

# Test health check
curl http://localhost:5000/health
```

---

## Render.com (Easiest - Free Tier Available)

**Time to Deploy**: ~5 minutes

```bash
# 1. Push code to GitHub
git push origin main

# 2. Go to render.com → New → Blueprint
# 3. Connect your repository
# 4. Render auto-detects ../render/render.yaml
# 5. Click "Apply" - Done!
```

**URL**: `https://bsb2usfm-converter.onrender.com`

**Notes**:
- Free tier spins down after 15 min inactivity
- Use Starter plan ($7/mo) for production (no spin-down)
- Persistent disk included (1GB)
- Auto-deploy on Git push
- Built-in SSL

---

## Digital Ocean Droplet (Full Control)

**Time to Deploy**: ~15 minutes | **Cost**: $6/month minimum

```bash
# 1. Create Droplet (Ubuntu 22.04, 1GB RAM)
# 2. SSH to droplet
ssh root@your_droplet_ip

# 3. Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
apt install docker-compose -y

# 4. Deploy
git clone <your-repo-url>
cd bsb2usfm/web_service
docker-compose up -d web

# 5. Setup Nginx (optional but recommended)
apt install nginx -y
# Copy nginx config from DEPLOY_Docker.md

# 6. Setup SSL (optional)
apt install certbot python3-certbot-nginx -y
certbot --nginx -d your_domain.com
```

**Access**: `http://your_droplet_ip:5000` or `https://your_domain.com`

---

## Docker Compose (Any VPS/Local)

**Time to Deploy**: ~5 minutes

```bash
# Start
docker-compose up -d web

# Stop
docker-compose down

# Rebuild
docker-compose build --no-cache web
docker-compose up -d web

# Logs
docker-compose logs -f web

# Restart
docker-compose restart web
```

---

## Essential Commands

### Health Check
```bash
curl http://localhost:5000/health
```

### View Logs
```bash
# Docker Compose
docker-compose logs -f web

# Docker
docker logs -f bsb2usfm_web

# System (if using systemd)
journalctl -u bsb2usfm -f
```

### Update Application
```bash
git pull origin main
docker-compose down
docker-compose build --no-cache web
docker-compose up -d web
```

### Backup Results
```bash
tar -czf backup-$(date +%Y%m%d).tar.gz ../results/
```

### Clean Docker
```bash
docker system prune -a
```

---

## Troubleshooting Quick Fixes

### Service Won't Start
```bash
docker-compose logs web
docker-compose down
docker-compose build --no-cache web
docker-compose up web  # Without -d to see errors
```

### Port Already in Use
```bash
# Find process
sudo lsof -i :5000
# or
sudo netstat -tulpn | grep 5000

# Kill process
sudo kill -9 <PID>
```

### Permission Errors
```bash
sudo chown -R $USER:$USER ../results/
```

### Out of Disk Space
```bash
# Check space
df -h

# Clean Docker
docker system prune -a

# Remove old results
rm -rf ../results/*.usfm
```

### Conversion Hangs
```bash
# Check resources
docker stats

# Restart service
docker-compose restart web

# Check logs for errors
docker-compose logs --tail=100 web
```

---

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Web interface |
| `/health` | GET | Health check |
| `/api/status` | GET | Conversion status |
| `/api/update` | POST | Trigger conversion |
| `/api/progress` | GET | Progress history |
| `/api/progress/stream` | GET | Real-time SSE stream |
| `/api/results` | GET | List generated files |
| `/api/download` | GET | Download zip of files |

---

## Monitoring

### Set Up Basic Monitoring
```bash
# Add to crontab
*/5 * * * * curl -f http://localhost:5000/health || echo "Service down" | mail -s "Alert" admin@example.com
```

### Resource Usage
```bash
# Docker stats
docker stats bsb2usfm_web

# System resources
htop
free -h
df -h
```

---

## Platform Comparison

| Platform | Setup Time | Cost | Ease | Control | Best For |
|----------|------------|------|------|---------|----------|
| **Render** | 5 min | Free-$7/mo | ⭐⭐⭐⭐⭐ | ⭐⭐ | Quick start, demos |
| **Digital Ocean** | 15 min | $6+/mo | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | Production, full control |
| **Local Docker** | 5 min | Free | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | Development, testing |

---

## Security Checklist

- [ ] Use HTTPS in production (Let's Encrypt for DO, built-in for Render)
- [ ] Enable firewall (ufw on Ubuntu for DO)
- [ ] Use non-root user for Docker
- [ ] Set up automatic security updates
- [ ] Enable rate limiting (nginx for DO)
- [ ] Regular backups
- [ ] Monitor logs for suspicious activity
- [ ] Keep dependencies updated

---

## Performance Tips

1. **Increase memory** if conversions are slow
   - Render: Upgrade to Standard plan (2GB)
   - DO: Use droplet with 2GB+ RAM ($12/mo)
   
2. **Use SSD storage** for output directory

3. **Set resource limits** in docker-compose.yml:
   ```yaml
   deploy:
     resources:
       limits:
         cpus: '1.0'
         memory: 1G
   ```

4. **Monitor with** `docker stats bsb2usfm_web`

---

## Getting Help

1. **Check logs first**: `docker-compose logs -f web`
2. **Run health check**: `curl http://localhost:5000/health`
3. **Test locally**: `docker-compose up web` (without -d)
4. **Full guide**: [DEPLOY_Docker.md](DEPLOY_Docker.md)
5. **Web service docs**: [README-WebService.md](README-WebService.md)
6. **GitHub issues**: Report bugs with logs

---

## Quick Links

- **Full Deployment Guide**: [DEPLOY_Docker.md](DEPLOY_Docker.md)
- **Deployment Index**: [DEPLOYMENT_INDEX.md](DEPLOYMENT_INDEX.md)
- **Web Service Docs**: [README-WebService.md](README-WebService.md)
- **Developer Guide**: [../README_developer.md](../README_developer.md)
- **User Guide**: [../README.md](../README.md)

---

**Last Updated**: 2024-01-15  
**Supported Platforms**: Render, Digital Ocean, Docker Compose