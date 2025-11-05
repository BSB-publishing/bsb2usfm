# BSB2USFM Deployment Resources Index

Quick navigation guide to all deployment-related documentation and resources.

## 🚀 Quick Start

**Want to deploy the web service?** Start here:

1. **Test Locally First**: [Test the Web Service Locally](#test-locally)
2. **Choose Your Platform**: [Platform Comparison](#platform-comparison)
3. **Follow Platform Guide**: [Deployment Guides](#deployment-guides)

## 📚 Documentation

### Main Deployment Guides

| Document | Purpose | Audience |
|----------|---------|----------|
| **[DEPLOY_Docker.md](DEPLOY_Docker.md)** | Complete deployment guide for Render and Digital Ocean | DevOps, Deployment |
| **[DEPLOY_QUICKREF.md](DEPLOY_QUICKREF.md)** | Quick reference card with essential commands | Everyone |
| **[README-WebService.md](README-WebService.md)** | Web service features and API documentation | Developers |
| **[../render/DEPLOYMENT.md](../render/DEPLOYMENT.md)** | Render-specific deployment instructions | Render users |

### Developer Documentation

| Document | Purpose |
|----------|---------|
| **[../README_developer.md](../README_developer.md)** | Developer guide with CLI usage |
| **[../README.md](../README.md)** | End-user documentation |
| **[WEB-SERVICE-IMPLEMENTATION.md](WEB-SERVICE-IMPLEMENTATION.md)** | Technical implementation details |

## 🧪 Test Locally

Before deploying to production, always test locally:

```bash
# Navigate to web service directory
cd bsb2usfm/web_service

# Run deployment readiness check
./check_deployment.sh

# Start the service with Docker Compose
docker-compose up --build web

# Access at http://localhost:5000
# Test the conversion by clicking "Update Data"

# Check health endpoint
curl http://localhost:5000/health
```

## 🌐 Platform Comparison

| Platform | Setup Time | Monthly Cost | Difficulty | Best For |
|----------|------------|--------------|------------|----------|
| **Render** | 5 min | Free - $7 | ⭐ Easy | Quick start, demos, MVP |
| **Digital Ocean** | 15 min | $6+ | ⭐⭐⭐ Medium | Production, full control |
| **Local/VPS** | 5 min | Variable | ⭐⭐⭐⭐ Advanced | Custom infrastructure |

### Recommendation by Use Case

- **Hobbyist/Demo**: Render (free tier)
- **Small Production**: Digital Ocean Basic ($6/mo)
- **Production with SSL**: Digital Ocean with Nginx + Let's Encrypt
- **Custom Infrastructure**: VPS with Docker Compose
- **Quick Deploy**: Render (auto-deploy from GitHub)

## 📖 Deployment Guides

### Render.com (Easiest)

**Guide**: [DEPLOY_Docker.md - Render Section](DEPLOY_Docker.md#rendercom)

**Quick Steps**:
1. Push code to GitHub
2. Go to render.com → New → Blueprint
3. Connect repository (auto-detects `../render/render.yaml`)
4. Click "Apply" - Done!

**URL**: `https://bsb2usfm-converter.onrender.com`

**Features**:
- Free tier available
- Auto-deploy from Git
- Built-in SSL
- Persistent disk storage
- Health checks included

### Digital Ocean Droplet

**Guide**: [DEPLOY_Docker.md - Digital Ocean Section](DEPLOY_Docker.md#digital-ocean-droplet)

**Quick Steps**:
```bash
# 1. Create Ubuntu 22.04 droplet (1GB+ RAM)
# 2. SSH and install Docker
ssh root@your_ip
curl -fsSL https://get.docker.com | sh

# 3. Deploy
git clone <repo-url>
cd bsb2usfm/web_service
docker-compose up -d web

# 4. Setup Nginx + SSL (optional but recommended)
```

**Features**:
- Full control over server
- Custom domains
- SSH access
- Multiple apps per droplet
- Predictable pricing

### Docker Compose (Any VPS)

**Guide**: [DEPLOY_Docker.md - Docker Compose Section](DEPLOY_Docker.md#docker-compose-localvps)

**Quick Steps**:
```bash
cd bsb2usfm/web_service
docker-compose up -d web
```

**Use Cases**:
- Local development
- Testing
- Custom VPS deployments
- Behind existing infrastructure

## 🛠️ Essential Tools

### Deployment Readiness Checker

```bash
cd web_service
./check_deployment.sh
```

Verifies:
- ✓ Required files exist
- ✓ Dependencies are correct
- ✓ Docker is available
- ✓ Python syntax is valid
- ✓ Configuration is complete

### Docker Commands

```bash
# Start service
docker-compose up -d web

# View logs
docker-compose logs -f web

# Restart
docker-compose restart web

# Stop
docker-compose down

# Rebuild
docker-compose build --no-cache web
```

### Monitoring & Maintenance

```bash
# Health check
curl http://localhost:5000/health

# View logs
docker-compose logs -f web

# Resource usage
docker stats bsb2usfm_web

# Update application
git pull origin main
docker-compose down
docker-compose build --no-cache web
docker-compose up -d web

# Backup results
tar -czf backup-$(date +%Y%m%d).tar.gz ../results/
```

## 🔧 Configuration Files

### Key Configuration Files

| File | Purpose | Required |
|------|---------|----------|
| `Dockerfile` | Docker image definition | Yes |
| `docker-compose.yml` | Local orchestration | Yes |
| `../render/render.yaml` | Render deployment config | For Render |
| `../requirements.txt` | Python dependencies | Yes |
| `webapp.py` | Flask application | Yes |
| `templates/index.html` | Web UI | Yes |

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `PORT` | 5000 | Web service port |
| `PYTHONUNBUFFERED` | 1 | Enable real-time logging |
| `PYTHONDONTWRITEBYTECODE` | 1 | Prevent .pyc files |

## 🔒 Security Checklist

Before deploying to production:

- [ ] Use HTTPS (Let's Encrypt recommended for DO, built-in for Render)
- [ ] Enable firewall (UFW on Ubuntu for DO)
- [ ] Use non-root Docker user (already configured)
- [ ] Set up automatic security updates
- [ ] Enable rate limiting in Nginx (for DO)
- [ ] Configure regular backups
- [ ] Monitor logs for suspicious activity
- [ ] Keep dependencies updated

## 📊 API Endpoints

The web service provides these endpoints:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Web interface (HTML) |
| `/health` | GET | Health check (JSON) |
| `/api/status` | GET | Conversion status |
| `/api/update` | POST | Trigger conversion |
| `/api/progress` | GET | Progress history |
| `/api/progress/stream` | GET | Real-time SSE stream |
| `/api/results` | GET | List generated files |
| `/api/download` | GET | Download zip archive |

See [README-WebService.md](README-WebService.md) for detailed API documentation.

## 🐛 Troubleshooting

### Quick Diagnostic Steps

1. **Check deployment readiness**:
   ```bash
   ./check_deployment.sh
   ```

2. **View logs**:
   ```bash
   docker-compose logs -f web
   ```

3. **Test health endpoint**:
   ```bash
   curl http://localhost:5000/health
   ```

4. **Verify Docker is running**:
   ```bash
   docker ps
   ```

### Common Issues

| Problem | Solution |
|---------|----------|
| Port already in use | `sudo lsof -i :5000` then kill process |
| Permission errors | `sudo chown -R $USER:$USER ../results/` |
| Container won't start | Check logs: `docker-compose logs web` |
| Build fails | Clean and rebuild: `docker-compose build --no-cache` |
| Conversion hangs | Check resources: `docker stats` |
| Out of disk space | Clean Docker: `docker system prune -a` |

See [DEPLOY_Docker.md - Troubleshooting](DEPLOY_Docker.md#troubleshooting) for detailed solutions.

## 📈 Performance Benchmarks

Expected conversion times for full Bible:

| Platform | RAM | CPU | Time |
|----------|-----|-----|------|
| Local Dev | 2GB | 2 cores | 30-60s |
| Render Free | 512MB | Shared | 90-120s |
| Render Starter | 512MB | Shared | 60-90s |
| DO $6 Droplet | 1GB | 1 core | 45-90s |
| DO $12 Droplet | 2GB | 1 core | 30-60s |

## 🆘 Getting Help

1. **Check documentation**: Start with relevant guide above
2. **Run diagnostics**: `./check_deployment.sh`
3. **Review logs**: `docker-compose logs -f web`
4. **Search issues**: Check GitHub for similar problems
5. **Platform support**: Consult platform-specific docs
6. **Open issue**: Report bugs with logs and steps to reproduce

## 📚 Additional Resources

### Official Documentation

- **Docker**: https://docs.docker.com
- **Docker Compose**: https://docs.docker.com/compose
- **Flask**: https://flask.palletsprojects.com
- **Gunicorn**: https://gunicorn.org

### Platform Documentation

- **Render**: https://render.com/docs
- **Digital Ocean**: https://docs.digitalocean.com

### Related Projects

- **USFM Spec**: https://ubsicap.github.io/usfm/
- **Berean Bible**: https://bereanbible.com

## 🗺️ Project Structure

```
bsb2usfm/
├── web_service/              # Web service files
│   ├── webapp.py            # Flask application
│   ├── Dockerfile           # Docker image
│   ├── docker-compose.yml   # Orchestration
│   ├── templates/           # HTML templates
│   │   └── index.html
│   ├── static/              # Static assets
│   ├── check_deployment.sh  # Readiness checker
│   ├── README-WebService.md # Web service docs
│   ├── DEPLOY_Docker.md     # Main deployment guide
│   ├── DEPLOY_QUICKREF.md   # Quick reference
│   ├── DEPLOYMENT_INDEX.md  # This file
│   └── WEB-SERVICE-IMPLEMENTATION.md
│
├── render/                   # Render.com config
│   ├── render.yaml          # Blueprint
│   └── DEPLOYMENT.md        # Render guide
│
├── demo_data/               # Sample files
├── results/                 # Output directory
├── bsb2usfm.py             # Main converter
├── getirefs.py             # Reference extractor
├── requirements.txt         # Python deps
├── README_developer.md     # Developer guide
└── README.md               # User guide
```

## 🎯 Next Steps

1. **Test locally**: Run `check_deployment.sh` and test with Docker Compose
2. **Choose platform**: Render (easy) or Digital Ocean (flexible)
3. **Follow guide**: Use appropriate section in DEPLOY_Docker.md
4. **Configure monitoring**: Set up health checks and alerts
5. **Secure deployment**: Enable HTTPS and firewall
6. **Plan backups**: Set up regular backup schedule

## 📝 Version Information

- **Docker**: 24.0+ required
- **Docker Compose**: 2.0+ required
- **Python**: 3.11+ required
- **Platforms Tested**: Render, Digital Ocean, Local Docker

---

**Last Updated**: 2024-01-15  
**Maintainer**: BSB2USFM Project  
**License**: See LICENSE file

For the latest updates and issues, visit the project repository.