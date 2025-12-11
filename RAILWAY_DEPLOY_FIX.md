# 🚀 Railway Deployment Fix Guide

## ✅ Yang Sudah Diperbaiki

Saya sudah memperbarui konfigurasi deployment Anda:

### **1. Dibuat `nixpacks.toml`** ✅
Railway sekarang menggunakan Nixpacks, bukan Heroku buildpack. File ini menentukan Python 3.11 dan cara install dependencies.

### **2. Diperbaiki `Procfile`** ✅
Updated untuk bind ke Railway's PORT variable:
```
web: gunicorn web.app:app --bind 0.0.0.0:$PORT
```

---

## 🔧 Langkah Deploy Ulang

### **Step 1: Commit & Push Perubahan**

```bash
# Di terminal, jalankan:
cd "c:\Users\q3j5c\OneDrive\Desktop\My Search Engine"

git add .
git commit -m "Fix Railway deployment configuration"
git push origin main
```

Railway akan auto-deploy setelah push! 

---

## 🚨 Troubleshooting Berdasarkan Error Message

### **Error 1: "Port already in use" atau "Failed to bind"**

**Solusi:** ✅ Sudah diperbaiki dengan `--bind 0.0.0.0:$PORT` di Procfile

### **Error 2: "ModuleNotFoundError" atau "No module named..."**

**Penyebab:** Dependencies tidak terinstall
**Solusi:** Pastikan `requirements.txt` lengkap (sudah OK)

### **Error 3: "No web process running"**

**Penyebab:** Procfile tidak terdeteksi atau salah format
**Solusi:** ✅ Sudah diperbaiki

### **Error 4: "Database connection failed"**

**Penyebab:** DATABASE_URL belum diset di Railway
**Solusi:**
1. Railway Dashboard → Project → Variables
2. Pastikan `DATABASE_URL` sudah ada
3. Format: `postgresql://postgres:password@host:port/railway`

### **Error 5: "Application failed to start"**

**Penyebab:** Error di app.py saat startup
**Solusi:** Check logs untuk detail error
Kemungkinan: `db/schema.sql` tidak ditemukan

**Fix:**
```python
# Di app.py line 23, path mungkin salah
# Pastikan path ke schema.sql benar
```

### **Error 6: "Build timeout"**

**Penyebab:** Install dependencies terlalu lama
**Solusi:** 
- Gunakan `psycopg2-binary` (sudah OK)
- Kurangi dependencies di requirements.txt

---

## 📋 Checklist Deployment

Sebelum deploy, pastikan:

- [ ] ✅ `nixpacks.toml` sudah ada
- [ ] ✅ `Procfile` sudah updated dengan `--bind 0.0.0.0:$PORT`
- [ ] ✅ `requirements.txt` ada gunicorn
- [ ] ✅ `web/app.py` tidak ada syntax error
- [ ] ✅ Folder `web/templates/` ada
- [ ] ✅ DATABASE_URL di Railway Variables sudah diset
- [ ] ✅ Git changes sudah commit & push

---

## 🔍 Cara Lihat Detailed Logs di Railway

1. Railway Dashboard → Project
2. Klik service "web" (yang deploy app Flask)
3. Tab **"Deployments"**
4. Klik deployment terakhir
5. Lihat section **"Build Logs"** dan **"Deploy Logs"**
6. **Copy error message** yang merah/failed
7. Share ke sini untuk analisis lebih lanjut

---

## 🎯 Quick Deploy Commands

```bash
# 1. Check git status
git status

# 2. Add all changes
git add .

# 3. Commit
git commit -m "Fix Railway deployment"

# 4. Push to trigger deploy
git push origin main

# 5. Watch logs di Railway dashboard
```

---

## 💡 Alternative: Deploy Manual via Railway CLI

Jika web deploy masih error, gunakan Railway CLI:

```bash
# Install Railway CLI
npm i -g @railway/cli

# Login
railway login

# Link project
railway link

# Deploy manual
railway up

# Check status
railway status

# View logs
railway logs
```

---

## 🔗 Common Railway Issues & Fixes

| Issue | Fix |
|-------|-----|
| Port binding error | ✅ Fixed: Use `$PORT` in Procfile |
| Python version wrong | ✅ Fixed: `nixpacks.toml` specifies 3.11 |
| Gunicorn not found | ✅ OK: Already in `requirements.txt` |
| Templates not found | ✅ OK: `/web/templates/` exists |
| Database connection fails | Set `DATABASE_URL` in Railway Variables |
| Schema init fails | Path issue in `app.py` line 23 |

---

## 📞 Next Steps

### **1. Deploy Ulang (Sekarang):**

```bash
cd "c:\Users\q3j5c\OneDrive\Desktop\My Search Engine"
git add .
git commit -m "Fix Railway deployment - nixpacks and Procfile"
git push origin main
```

### **2. Monitor Deploy:**

- Buka Railway Dashboard
- Watch build progress
- Check logs untuk errors

### **3. Jika Masih Error:**

**Copy EXACT error message dari Railway logs dan share ke sini!**

Format yang helpful:
```
===== BUILD LOGS =====
[error message dari build phase]

===== DEPLOY LOGS =====
[error message dari deploy phase]
```

---

## 🎯 Files Updated

- ✅ **NEW**: `nixpacks.toml` - Railway configuration
- ✅ **FIXED**: `Procfile` - Port binding fix
- ✅ **OK**: `requirements.txt` - Already correct
- ✅ **OK**: `web/app.py` - Already correct

---

**Deploy ulang sekarang dengan commands di atas, lalu share error logs jika masih gagal! 🚀**
