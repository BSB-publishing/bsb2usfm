# BSB2USFM Render.com Deployment Checklist

## Pre-Deployment Checklist

### 🧪 Local Testing (MANDATORY)

- [ ] **Docker builds successfully**
  ```bash
  docker-compose build web
  ```

- [ ] **Service starts without errors**
  ```bash
  docker-compose up -d web
  docker-compose logs web
  ```

- [ ] **Health check passes**
  ```bash
  curl http://localhost:5000/health
  # Should return: {"status":"healthy",...}
  ```

- [ ] **Web UI loads**
  - [ ] Open http://localhost:5000 in browser
  - [ ] Page loads completely
  - [ ] No JavaScript errors in console (F12)
  - [ ] All UI elements visible

- [ ] **Format selection works**
  - [ ] Can select USFM
  - [ ] Can select USX
  - [ ] Can select USJ

- [ ] **Conversion options work**
  - [ ] Interlinear checkbox functional
  - [ ] Strong's Numbers is disabled (grayed out)
  - [ ] Placeholders checkbox functional
  - [ ] Brackets checkbox functional

- [ ] **Conversion succeeds (USFM)**
  ```bash
  # In browser:
  # 1. Select USFM format
  # 2. Click "Convert"
  # 3. Wait 2-5 minutes
  # 4. Verify status shows "Completed"
  # 5. Verify 66 files listed
  ```

- [ ] **Conversion succeeds (USX)**
  - [ ] Select USX format
  - [ ] Click "Convert"
  - [ ] Verify completion
  - [ ] Verify 66 .usx files

- [ ] **Conversion succeeds (USJ)**
  - [ ] Select USJ format
  - [ ] Click "Convert"
  - [ ] Verify completion
  - [ ] Verify 66 .usj files

- [ ] **Download works**
  - [ ] Button changes to "Download X Files (ZIP)"
  - [ ] Click download button
  - [ ] ZIP file downloads
  - [ ] ZIP contains all 66 books
  - [ ] Files are valid (can open them)

- [ ] **Progress log shows updates**
  - [ ] Real-time updates during conversion
  - [ ] No errors in progress log
  - [ ] Clear button works

- [ ] **API endpoints work**
  ```bash
  curl http://localhost:5000/api/status
  curl http://localhost:5000/api/results
  curl http://localhost:5000/api/download -o test.zip
  ```

- [ ] **Container stops cleanly**
  ```bash
  docker-compose down
  ```

---

### 📦 Code Repository

- [ ] **All changes committed**
  ```bash
  git status
  # Should show: nothing to commit, working tree clean
  ```

- [ ] **All changes pushed**
  ```bash
  git push origin main
  ```

- [ ] **Repository is public OR cloud platform has access**

- [ ] **Required files present**
  - [ ] Dockerfile
  - [ ] docker-compose.yml
  - [ ] webapp.py
  - [ ] bsb2usfm.py
  - [ ] templates/index.html
  - [ ] requirements.txt
  - [ ] render.yaml

- [ ] **Optional documentation present**
  - [ ] render/DEPLOYMENT.md
  - [ ] render/DEPLOY-QUICKSTART.md
  - [ ] render/README.md
  - [ ] render/deployment-checklist.md
  - [ ] render/QUICKREF.txt

---

### 🔧 Configuration Files

- [ ] **Dockerfile is correct**
  - [ ] Base image: python:3.11-slim
  - [ ] All dependencies installed
  - [ ] Port 5000 exposed
  - [ ] Correct CMD: python3 webapp.py

- [ ] **docker-compose.yml is correct**
  - [ ] No version attribute (removed)
  - [ ] Port mapping: 5000:5000
  - [ ] Volume mounts configured
  - [ ] Environment variables set

- [ ] **render/render.yaml is correct**
  - [ ] Service type: web
  - [ ] Environment: docker
  - [ ] Plan: free
  - [ ] Health check path: /health
  - [ ] Disk mount configured
  - [ ] Port: 5000

---

### 🌐 Cloud Platform Account

- [ ] **Account created**
  - [ ] Render.com OR Fly.io
  - [ ] Email verified

- [ ] **Payment method (optional)**
  - [ ] Credit card added (some platforms require it even for free tier)
  - [ ] Free tier limits understood

- [ ] **Git connected** (Render.com)
  - [ ] GitHub/GitLab account linked
  - [ ] Repository permissions granted

- [ ] **Render dashboard accessible**
  - [ ] Can log in to https://render.com
  - [ ] Can view services
  - [ ] Can access logs

---

### 🚀 Deployment

#### Render.com Deployment

- [ ] **Account created**
  - [ ] Signed up at https://render.com
  - [ ] Connected GitHub/GitLab account
  - [ ] Email verified

- [ ] **Service created**
  - [ ] Name chosen
  - [ ] Region selected
  - [ ] Docker environment selected
  - [ ] Free plan selected
  - [ ] Health check path set to `/health`
  - [ ] Auto-deploy enabled (optional)

- [ ] **Build succeeds**
  - [ ] Watch build logs in Render dashboard
  - [ ] No errors during build
  - [ ] Image created successfully
  - [ ] Takes 5-10 minutes (first time)

- [ ] **Service starts**
  - [ ] Health check passes
  - [ ] Service shows "Live" in dashboard
  - [ ] URL accessible
  - [ ] No errors in logs

---

### ✅ Post-Deployment Testing

- [ ] **Health check works**
  ```bash
  curl https://your-app-url.com/health
  ```

- [ ] **Web UI loads**
  - [ ] Visit https://your-app-url.com
  - [ ] Page loads completely
  - [ ] No console errors

- [ ] **Can select formats**
  - [ ] All three formats selectable
  - [ ] Radio buttons work

- [ ] **Conversion works end-to-end**
  - [ ] Select format
  - [ ] Click Convert
  - [ ] Wait for completion (may take 3-10 minutes on free tier)
  - [ ] Success message appears
  - [ ] Files listed

- [ ] **Download works**
  - [ ] Button text correct
  - [ ] ZIP downloads
  - [ ] Contains 66 files
  - [ ] Files are valid

- [ ] **Performance acceptable**
  - [ ] UI responsive
  - [ ] Conversion completes (even if slow)
  - [ ] No timeouts

- [ ] **Logs accessible**
  - [ ] Can view logs in Render dashboard
  - [ ] Logs show expected output
  - [ ] No error messages
  - [ ] Can search and filter logs

- [ ] **Shell access works**
  - [ ] Can access Shell tab in dashboard
  - [ ] Can run commands interactively
  - [ ] Can check files and environment

---

### 🔍 Monitoring Setup (Optional but Recommended)

- [ ] **Uptime monitoring**
  - [ ] UptimeRobot configured
  - [ ] Monitoring health endpoint
  - [ ] Alerts configured

- [ ] **Error tracking**
  - [ ] Sentry or similar (optional)
  - [ ] Error notifications

- [ ] **Usage tracking**
  - [ ] Basic analytics
  - [ ] Conversion success rate

---

### 📚 Documentation

- [ ] **URL documented**
  - [ ] Saved in safe place
  - [ ] Shared with team (if applicable)
  - [ ] Documented in project README

- [ ] **Credentials saved**
  - [ ] Platform login
  - [ ] API keys (if any)

- [ ] **Maintenance notes**
  - [ ] How to redeploy
  - [ ] How to check logs
  - [ ] How to debug issues

---

### 🚨 Rollback Plan

- [ ] **Know how to rollback**
  - Render: Manual Deploy → Deploy specific commit
  - Or: Revert Git commit and push

- [ ] **Local backup works**
  - [ ] Can always run locally as fallback
  - [ ] docker-compose up -d web

---

### 🎯 Success Criteria

Deployment is successful when:

✅ Service is live and accessible  
✅ Health endpoint returns healthy status  
✅ Can perform full conversion workflow  
✅ Can download generated files  
✅ All three formats work (USFM, USX, USJ)  
✅ Logs show no critical errors  
✅ Performance is acceptable  

---

### 📝 Notes

**Free Tier Limitations:**
- Sleeps after 15 minutes of inactivity
- Takes ~30 seconds to wake up on first request
- Limited memory (512MB)
- Shared CPU (slower performance)
- Conversion takes 3-5 minutes
- 1GB persistent disk storage

**When Something Goes Wrong:**
1. Check logs on cloud platform
2. Test same action locally
3. Compare local vs cloud behavior
4. Fix locally first
5. Commit and push
6. Redeploy

**Remember:**
🧪 Test Local → 📦 Commit → 🚀 Deploy → ✅ Verify

**All deployment files are in the `render/` folder.**

---

## Quick Reference

```bash
# Local Testing
docker-compose build web
docker-compose up -d web
curl http://localhost:5000/health
# Test in browser at http://localhost:5000
docker-compose down

# Render.com Deployment
# 1. Push to Git: git push origin main
# 2. Deploy via Render dashboard or auto-deploy
# 3. View logs in dashboard
# 4. Access shell in dashboard
# 5. Monitor status in dashboard

# Render Commands (in dashboard)
# - View Logs: Logs tab
# - Shell Access: Shell tab
# - Manual Deploy: Manual Deploy button
# - Settings: Settings tab
```

---

**Last Updated:** 2025-10-30
**Version:** 1.0.0