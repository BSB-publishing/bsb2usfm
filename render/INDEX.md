# BSB2USFM Render.com Deployment Files

This folder contains all files and documentation needed to deploy BSB2USFM to Render.com.

## 📁 Files in This Folder

### Configuration
- **`render.yaml`** - Render.com deployment configuration (auto-detected by Render)

### Documentation

#### Quick Start (Start Here!)
- **`DEPLOY-QUICKSTART.md`** - 5-minute deployment guide
- **`QUICKREF.txt`** - One-page quick reference card (printable)

#### Detailed Documentation
- **`DEPLOYMENT.md`** - Complete deployment guide with troubleshooting
- **`deployment-checklist.md`** - Pre/post deployment checklist
- **`README.md`** - Overview and summary

#### Navigation
- **`INDEX.md`** - This file (navigation guide)

---

## 🚀 Getting Started

### New to Render.com Deployment?

**Follow these steps in order:**

1. **Read**: `DEPLOY-QUICKSTART.md` (5 minutes)
2. **Review**: `QUICKREF.txt` (quick reference)
3. **Use**: `deployment-checklist.md` (before deploying)
4. **Deploy**: Follow the steps in DEPLOY-QUICKSTART.md
5. **Troubleshoot**: Refer to `DEPLOYMENT.md` if needed

---

## 📚 Documentation Guide

### When to Use Each File

| File | When to Use |
|------|-------------|
| **DEPLOY-QUICKSTART.md** | First time deploying, need quick steps |
| **QUICKREF.txt** | Quick lookup of commands and settings |
| **deployment-checklist.md** | Before and after deploying (verification) |
| **DEPLOYMENT.md** | Need detailed info, troubleshooting, or advanced setup |
| **README.md** | Want overview of deployment features and benefits |
| **render.yaml** | Render.com auto-detects this (no action needed) |

---

## 🎯 Quick Deploy (5 Steps)

```bash
# 1. Test locally
cd ..  # Go back to project root
docker-compose up -d web
# Test in browser at http://localhost:5000
docker-compose down

# 2. Push to Git
git add .
git commit -m "Ready for Render"
git push origin main

# 3. Go to Render.com
# - Sign up at https://render.com
# - New + → Web Service
# - Connect your repository
# - Select Docker environment
# - Select Free plan
# - Click Create Web Service

# 4. Wait 5-10 minutes for build

# 5. Test deployment
curl https://your-app.onrender.com/health
```

---

## 💡 Key Points

- ✅ **render.yaml is auto-detected** - Render finds it automatically
- ✅ **Always test locally first** - Never debug in the cloud
- ✅ **Free tier sleeps after 15 min** - Normal behavior
- ✅ **Wake time is ~30 seconds** - First request after sleep
- ✅ **Conversion takes 3-5 minutes** - Shared CPU on free tier
- ✅ **Auto-deploy from Git** - Push to Git = automatic deployment

---

## 📞 Need Help?

1. **Quick answer?** Check `QUICKREF.txt`
2. **Detailed help?** Read `DEPLOYMENT.md`
3. **Troubleshooting?** See troubleshooting section in `DEPLOYMENT.md`
4. **Render docs**: https://render.com/docs
5. **Community**: https://community.render.com

---

## 🎉 You're Ready!

All the files you need for Render.com deployment are in this folder.

**Start with**: `DEPLOY-QUICKSTART.md`

Good luck! 🚀