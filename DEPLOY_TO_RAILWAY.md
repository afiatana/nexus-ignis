# 🚂 Deploy ke Railway - Quick Guide

## ✅ Files Sudah Siap Deploy

Semua konfigurasi untuk Railway sudah diperbaiki:

- ✅ `nixpacks.toml` - Railway build configuration (Python 3.11)
- ✅ `Procfile` - Start command dengan port binding
- ✅ `requirements.txt` - Python dependencies
- ✅ `web/app.py` - Schema path sudah diperbaiki

---

## 🚀 Deploy Sekarang (3 Langkah)

### **1. Commit & Push**

```bash
cd "c:\Users\q3j5c\OneDrive\Desktop\My Search Engine"

git add .
git commit -m "Fix Railway deployment configuration"
git push origin main
```

### **2. Check Railway Variables**

1. Buka **Railway Dashboard** → Project Anda
2. Klik service **Postgres**
3. Tab **"Variables"** → Copy `DATABASE_URL`
4. Klik service **Web** (Flask app)
5. Tab **"Variables"** → Add new variable:
   - Name: `DATABASE_URL`
   - Value: Paste dari Postgres service

### **3. Deploy!**

Railway akan auto-deploy setelah push ke GitHub!

Watch progress di:
- Railway Dashboard → Deployments tab
- Lihat build & deploy logs

---

## 📊 Expected Deployment Flow

```
1. GitHub Push
   ↓
2. Railway Detects Push
   ↓
3. BUILD PHASE (2-3 min)
   - Install Python 3.11
   - Install dependencies dari requirements.txt
   ✅ "Build successful"
   ↓
4. DEPLOY PHASE (30 sec)
   - Start gunicorn
   - Bind to Railway's port
   - Initialize database (if needed)
   ✅ "Deployment successful"
   ↓
5. LIVE! 🎉
   - App accessible via Railway URL
```

---

## 🔍 Jika Deploy Gagal

### **Lihat Logs:**
1. Railway → Deployments tab
2. Click failed deployment (red status)
3. Expand logs sections:
   - `Build Logs` - untuk errors saat install
   - `Deploy Logs` - untuk errors saat start app

### **Common Errors:**

**Build Error: "Could not find Python"**
```
Fix: nixpacks.toml sudah specify Python 3.11 ✅
```

**Deploy Error: "Port binding failed"**
```
Fix: Procfile sudah updated dengan $PORT ✅
```

**Runtime Error: "Database connection failed"**
```
Fix: Set DATABASE_URL di Railway Variables (Step 2)
```

**Runtime Error: "schema.sql not found"**
```
Fix: app.py sudah updated dengan multi-path lookup ✅
```

---

## 🎯 Deployment Checklist

Before deploy:
- [x] ✅ `nixpacks.toml` created
- [x] ✅ `Procfile` fixed
- [x] ✅ `requirements.txt` has gunicorn
- [x] ✅ `web/app.py` schema path fixed
- [ ] ⚠️ DATABASE_URL set di Railway Variables (Anda perlu lakukan Step 2)
- [ ] ⚠️ Git commit & push (Anda perlu lakukan Step 1)

---

## 💻 Railway Dashboard Structure

```
Your Project
├── 📦 Postgres Service
│   ├── Database URL (copy this)
│   ├── Metrics
│   └── Data
│
└── 🌐 Web Service (Flask App)
    ├── Variables (paste DATABASE_URL here)
    ├── Deployments (check status)
    ├── Metrics
    └── Settings
```

---

## 🔧 Troubleshooting Commands

### Check if schema.sql exists:
```bash
ls -la db/schema.sql
```

### Test locally before deploy:
```bash
# Set DATABASE_URL
set DATABASE_URL=postgresql://...

# Run locally
python web/app.py
```

### View Railway logs (CLI):
```bash
railway logs
```

---

## 📞 Need Help?

**Share error logs dengan format:**

```
=== BUILD LOGS ===
[paste build errors here]

=== DEPLOY LOGS ===
[paste deploy errors here]

=== RUNTIME LOGS ===
[paste runtime errors here]
```

---

## 🎊 Success Indicators

Deploy berhasil jika lihat:
- ✅ Build status: "Build successful"
- ✅ Deploy status: "Deployment successful"
- ✅ Logs show: "Database initialized successfully"
- ✅ Web URL accessible
- ✅ No error 500 atau crashes

---

**Ready to deploy? Run Step 1 commands now! 🚀**
