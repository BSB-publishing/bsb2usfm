# BSB2USFM Docker Deployment Guide

Complete guide for deploying the BSB2USFM web service to production using Docker on Render.com or Digital Ocean.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Platform-Specific Guides](#platform-specific-guides)
  - [Render.com](#rendercom)
  - [Digital Ocean Droplet](#digital-ocean-droplet)
- [Docker Compose (Local/VPS)](#docker-compose-localvps)
- [Production Configuration](#production-configuration)
- [Monitoring & Maintenance](#monitoring--maintenance)
- [Troubleshooting](#troubleshooting)

---

## Prerequisites

Before deploying, ensure you have:

- Git repository with the BSB2USFM code
- Docker installed (for local testing)
- Account on your chosen platform (Render or Digital Ocean)
- Basic understanding of Docker and web services

## Quick Start

### Test Locally First

Always test the deployment locally before pushing to production:

```bash
# Clone the repository
git clone <your-repo-url>
cd bsb2usfm

# Build and test the web service
cd web_service
docker-compose up --build web

# Access at http://localhost:5000
# Test the conversion by clicking "Update Data"
```

### Verify Health Check

```bash
curl http://localhost:5000/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T12:34:56",
  "environment": "development",
  "conversion_running": false
}
```

---

## Platform-Specific Guides

## Render.com

Render is the easiest platform for deployment with built-in Docker support and a free tier.

### Step 1: Prepare Your Repository

1. Ensure `../render/render.yaml` exists in your repository (already included)
2. Commit and push your code to GitHub, GitLab, or Bitbucket

### Step 2: Connect to Render

1. Go to https://render.com and sign up/login
2. Click **"New +"** → **"Blueprint"**
3. Connect your Git repository
4. Render will automatically detect `render/render.yaml`

### Step 3: Configure Service

The `render.yaml` file includes:

```yaml
services:
  - type: web
    name: bsb2usfm-converter
    runtime: docker
    dockerfilePath: ./web_service/Dockerfile
    dockerContext: .
    plan: free  # or starter/standard for production
    healthCheckPath: /health
    disk:
      name: bsb2usfm-data
      mountPath: /app/output
      sizeGB: 1
```

### Step 4: Deploy

1. Click **"Apply"** to create the service
2. Render will build and deploy automatically
3. Access your service at: `https://bsb2usfm-converter.onrender.com`

### Step 5: Configure Environment Variables (Optional)

In the Render dashboard:
- Go to **Environment**
- Add any custom variables:
  - `PORT` (default: 5000, Render sets this automatically)
  - `PYTHONUNBUFFERED=1` (already set)

### Important Render Notes

- **Free tier**: Service spins down after 15 minutes of inactivity
- **Persistent storage**: The disk mount persists generated files
- **Build time**: First build takes 3-5 minutes
- **Auto-deploy**: Pushes to main branch trigger automatic deploys

### Render Production Checklist

- [ ] Use Starter plan or higher for production (no spin-down)
- [ ] Enable health checks (already configured)
- [ ] Set up custom domain if needed
- [ ] Configure disk size based on expected output volume
- [ ] Enable email notifications for failed deploys

---

## Digital Ocean Droplet

Deploy on a Virtual Private Server (VPS) for full control.

### Step 1: Create a Droplet

1. Log into Digital Ocean: https://cloud.digitalocean.com
2. Click **"Create"** → **"Droplets"**
3. Choose configuration:
   - **Image**: Ubuntu 22.04 LTS
   - **Plan**: Basic ($6/month minimum recommended)
   - **CPU**: Regular with SSD (1 GB RAM minimum)
   - **Datacenter**: Choose closest to your users
   - **Authentication**: SSH keys (recommended) or password
4. Click **"Create Droplet"**

### Step 2: Initial Server Setup

SSH into your droplet:

```bash
ssh root@your_droplet_ip
```

Update system and install Docker:

```bash
# Update packages
apt update && apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Install Docker Compose
apt install docker-compose -y

# Create non-root user (recommended)
adduser bsb2usfm
usermod -aG docker bsb2usfm
usermod -aG sudo bsb2usfm

# Switch to new user
su - bsb2usfm
```

### Step 3: Deploy Application

```bash
# Clone repository
git clone <your-repo-url> bsb2usfm
cd bsb2usfm/web_service

# Create necessary directories
mkdir -p ../results ../data

# Start the service
docker-compose up -d web

# Check status
docker-compose ps
docker-compose logs -f web
```

### Step 4: Configure Firewall

```bash
# Allow SSH
sudo ufw allow OpenSSH

# Allow HTTP
sudo ufw allow 80/tcp

# Allow HTTPS
sudo ufw allow 443/tcp

# Enable firewall
sudo ufw enable
```

### Step 5: Set Up Reverse Proxy (Nginx)

Install and configure Nginx:

```bash
sudo apt install nginx -y

# Create Nginx configuration
sudo nano /etc/nginx/sites-available/bsb2usfm
```

Add this configuration:

```nginx
server {
    listen 80;
    server_name your_domain.com;  # or droplet IP

    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # SSE support (for real-time progress)
        proxy_buffering off;
        proxy_cache off;
        proxy_set_header Connection '';
        proxy_http_version 1.1;
        chunked_transfer_encoding on;
        proxy_read_timeout 300s;
    }

    location /health {
        proxy_pass http://localhost:5000/health;
        access_log off;
    }
}
```

Enable the site:

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/bsb2usfm /etc/nginx/sites-enabled/

# Remove default site
sudo rm /etc/nginx/sites-enabled/default

# Test configuration
sudo nginx -t

# Restart Nginx
sudo systemctl restart nginx
```

### Step 6: Set Up SSL with Let's Encrypt (Optional but Recommended)

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx -y

# Get SSL certificate
sudo certbot --nginx -d your_domain.com

# Auto-renewal is set up automatically
# Test renewal:
sudo certbot renew --dry-run
```

### Step 7: Set Up Auto-Start

Create systemd service for auto-start on reboot:

```bash
sudo nano /etc/systemd/system/bsb2usfm.service
```

Add this content:

```ini
[Unit]
Description=BSB2USFM Web Service
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/home/bsb2usfm/bsb2usfm/web_service
ExecStart=/usr/bin/docker-compose up -d web
ExecStop=/usr/bin/docker-compose down
User=bsb2usfm

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl enable bsb2usfm
sudo systemctl start bsb2usfm
sudo systemctl status bsb2usfm
```

### Digital Ocean Maintenance

```bash
# View logs
cd ~/bsb2usfm/web_service
docker-compose logs -f web

# Restart service
docker-compose restart web

# Update application
git pull origin main
docker-compose down
docker-compose build web
docker-compose up -d web

# Check disk usage
df -h
du -sh ~/bsb2usfm/results/*

# Clean up old Docker images
docker system prune -a
```

---

## Docker Compose (Local/VPS)

For custom VPS deployments or local development.

### Full Production docker-compose.yml

Create `docker-compose.prod.yml`:

```yaml
version: '3.8'

services:
  web:
    build:
      context: ..
      dockerfile: web_service/Dockerfile
    container_name: bsb2usfm_web
    ports:
      - "5000:5000"
    volumes:
      - bsb2usfm_output:/app/output
      - ../demo_data:/app/demo_data:ro
    environment:
      - PYTHONPATH=/app
      - PYTHONDONTWRITEBYTECODE=1
      - PYTHONUNBUFFERED=1
      - PORT=5000
    working_dir: /app
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

  nginx:
    image: nginx:alpine
    container_name: bsb2usfm_nginx
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/conf.d/default.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - web
    restart: unless-stopped

volumes:
  bsb2usfm_output:
    driver: local
```

### Nginx Configuration for Docker

Create `nginx.conf`:

```nginx
upstream bsb2usfm {
    server web:5000;
}

server {
    listen 80;
    server_name localhost;

    client_max_body_size 50M;

    location / {
        proxy_pass http://bsb2usfm;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # SSE support
        proxy_buffering off;
        proxy_cache off;
        proxy_set_header Connection '';
        proxy_http_version 1.1;
        chunked_transfer_encoding on;
        proxy_read_timeout 300s;
    }
}
```

### Deploy

```bash
docker-compose -f docker-compose.prod.yml up -d
```

---

## Production Configuration

### Environment Variables

Key environment variables for production:

| Variable | Default | Description |
|----------|---------|-------------|
| `PORT` | 5000 | Web service port |
| `PYTHONUNBUFFERED` | 1 | Enable real-time logging |
| `PYTHONDONTWRITEBYTECODE` | 1 | Prevent .pyc files |
| `RENDER` | - | Auto-detected on Render |

### Security Best Practices

1. **Use HTTPS in Production**
   - Let's Encrypt for free SSL certificates
   - Cloudflare for DDoS protection

2. **Enable Rate Limiting**
   - Add rate limiting to Nginx
   - Prevent abuse of conversion endpoint

3. **Restrict Access**
   - Use basic auth or OAuth if needed
   - Whitelist IPs if for internal use

4. **Regular Updates**
   ```bash
   # Update dependencies
   pip install --upgrade -r requirements.txt
   
   # Rebuild Docker image
   docker-compose build --no-cache
   ```

5. **Backup Strategy**
   - Regular snapshots of VPS
   - Backup generated USFM files
   - Version control for configuration

### Nginx Rate Limiting

Add to nginx.conf:

```nginx
# Rate limiting zone
limit_req_zone $binary_remote_addr zone=conversion:10m rate=5r/m;

server {
    # ...
    
    location /api/update {
        limit_req zone=conversion burst=2 nodelay;
        proxy_pass http://bsb2usfm;
        # ... other proxy settings
    }
}
```

### Resource Limits

For docker-compose, add resource limits:

```yaml
services:
  web:
    # ...
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 1G
        reservations:
          cpus: '0.5'
          memory: 512M
```

---

## Monitoring & Maintenance

### Health Monitoring

Set up monitoring with automated health checks:

```bash
# Simple cron job for health monitoring
# Add to crontab: crontab -e

*/5 * * * * curl -f http://localhost:5000/health || echo "BSB2USFM health check failed" | mail -s "Alert" admin@example.com
```

### Log Management

```bash
# View real-time logs
docker-compose logs -f web

# Search logs
docker-compose logs web | grep ERROR

# Export logs
docker-compose logs --no-color web > /var/log/bsb2usfm.log

# Rotate logs (add to logrotate)
sudo nano /etc/logrotate.d/bsb2usfm
```

Logrotate configuration:

```
/var/log/bsb2usfm.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
}
```

### Performance Monitoring

Install monitoring tools:

```bash
# Docker stats
docker stats bsb2usfm_web

# System resources
htop
iotop
nethogs
```

### Backup Automation

```bash
#!/bin/bash
# backup-bsb2usfm.sh

BACKUP_DIR="/backups/bsb2usfm"
DATE=$(date +%Y%m%d_%H%M%S)

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup results
tar -czf $BACKUP_DIR/results_$DATE.tar.gz /home/bsb2usfm/bsb2usfm/results

# Keep only last 7 days
find $BACKUP_DIR -name "results_*.tar.gz" -mtime +7 -delete

# Upload to S3/Backblaze (optional)
# aws s3 cp $BACKUP_DIR/results_$DATE.tar.gz s3://your-bucket/
```

Add to cron:

```bash
# Daily backup at 2 AM
0 2 * * * /home/bsb2usfm/backup-bsb2usfm.sh
```

### Update Procedure

```bash
# 1. Backup current state
docker-compose down
tar -czf backup-$(date +%Y%m%d).tar.gz results/

# 2. Update code
git pull origin main

# 3. Rebuild and restart
docker-compose build --no-cache web
docker-compose up -d web

# 4. Verify health
curl http://localhost:5000/health

# 5. Check logs
docker-compose logs -f web
```

---

## Troubleshooting

### Common Issues

#### 1. Container Won't Start

```bash
# Check logs
docker-compose logs web

# Common causes:
# - Port already in use
# - Missing dependencies
# - Incorrect file paths

# Solution: Check port and rebuild
docker-compose down
docker-compose build --no-cache web
docker-compose up web
```

#### 2. Permission Errors

```bash
# Fix ownership
sudo chown -R $USER:$USER results/

# In Docker, check user
docker-compose exec web whoami
docker-compose exec web ls -la /app/output
```

#### 3. Conversion Fails

```bash
# Check available disk space
df -h

# Check memory
free -h

# Check conversion logs
docker-compose exec web cat /app/output/*.log
```

#### 4. Slow Performance

```bash
# Check resource usage
docker stats

# Increase resources in docker-compose.yml
services:
  web:
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 2G
```

#### 5. SSE Connection Issues

```bash
# Check if Nginx/proxy is blocking SSE
# Ensure proxy_buffering is off

# Test SSE endpoint directly
curl -N http://localhost:5000/api/progress/stream
```

#### 6. Build Fails on ARM (M1/M2 Mac)

```bash
# Build for specific platform
docker build --platform linux/amd64 -f Dockerfile ..

# Or use docker-compose
docker-compose build --build-arg BUILDPLATFORM=linux/amd64 web
```

### Debug Mode

Enable debug logging:

```bash
# Add to docker-compose.yml
environment:
  - FLASK_DEBUG=1
  - LOG_LEVEL=DEBUG
```

### Getting Help

1. **Check logs first**: `docker-compose logs -f web`
2. **Health check**: `curl http://localhost:5000/health`
3. **Test locally**: Run outside Docker to isolate issues
4. **Check GitHub issues**: Search for similar problems
5. **Platform docs**: Render and Digital Ocean have extensive docs

### Performance Benchmarks

Expected performance on recommended hardware:

| Platform | RAM | CPU | Full Bible Conversion Time |
|----------|-----|-----|----------------------------|
| Local | 2GB | 2 cores | ~30-60 seconds |
| Render Free | 512MB | Shared | ~90-120 seconds |
| Render Starter | 512MB | Shared | ~60-90 seconds |
| DO Droplet ($6) | 1GB | 1 core | ~45-90 seconds |
| DO Droplet ($12) | 2GB | 1 core | ~30-60 seconds |

---

## Quick Reference Commands

### Docker Compose

```bash
# Start service
docker-compose up -d web

# Stop service
docker-compose down

# Rebuild
docker-compose build --no-cache web

# View logs
docker-compose logs -f web

# Restart
docker-compose restart web

# Execute command in container
docker-compose exec web bash
```

### Docker

```bash
# List containers
docker ps -a

# View logs
docker logs -f bsb2usfm_web

# Stop container
docker stop bsb2usfm_web

# Remove container
docker rm bsb2usfm_web

# Clean up
docker system prune -a
```

### System

```bash
# Check disk usage
df -h

# Check memory
free -h

# Check processes
ps aux | grep python

# Check port
netstat -tulpn | grep 5000
```

---

## Additional Resources

- **Main Documentation**: [../README.md](../README.md)
- **Developer Guide**: [../README_developer.md](../README_developer.md)
- **Web Service Docs**: [README-WebService.md](README-WebService.md)
- **Render Deployment**: [../render/DEPLOYMENT.md](../render/DEPLOYMENT.md)

## Support

For deployment issues:

1. Check this guide's troubleshooting section
2. Review platform-specific documentation
3. Check Docker and application logs
4. Open an issue on GitHub with:
   - Platform used (Render or Digital Ocean)
   - Error messages
   - Steps to reproduce
   - Docker and system info

---

**Last Updated**: 2024-01-15  
**Tested Platforms**: Render, Digital Ocean, Local Docker  
**Docker Version**: 24.0+  
**Docker Compose Version**: 2.0+