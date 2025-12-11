## ⚡ Quick Setup Checklist

### 🚀 Sudah Punya Database Railway? (RECOMMENDED)

- [ ] Login ke Railway.app
- [ ] Buka project → Postgres service
- [ ] Copy `DATABASE_URL` dari Variables tab
- [ ] (Optional) Cek apakah table `archived_documents` sudah ada
- [ ] Skip ke Langkah 4 (Setup GitHub Secret) di bawah ⬇️

---

### 🆕 Belum Punya Database? Setup Supabase (Gratis)

### 1️⃣ Setup Supabase Database (5 menit)
- [ ] Buka https://supabase.com
- [ ] Login dengan GitHub
- [ ] Buat project baru: `my-search-engine`
- [ ] Set region: Singapore
- [ ] Set password (SIMPAN!)
- [ ] Tunggu project selesai dibuat

### 2️⃣ Run Database Schema (1 menit)
- [ ] Klik "SQL Editor"
- [ ] Copy isi dari `db/schema.sql`
- [ ] Paste dan Run query

### 3️⃣ Copy Connection String (1 menit)
- [ ] Klik "Project Settings" → "Database"
- [ ] Copy "Connection string" (URI format)
- [ ] Ganti `[YOUR-PASSWORD]` dengan password Anda

### 4️⃣ Setup GitHub Secret (2 menit)
- [ ] Buka GitHub repo → Settings → Secrets → Actions
- [ ] Klik "New repository secret"
- [ ] Name: `DATABASE_URL`
- [ ] Value: Connection string dari Supabase
- [ ] Klik "Add secret"

### 5️⃣ Test Workflow (1 menit)
- [ ] GitHub → Actions → "Daily Scraper & Archiver"
- [ ] Klik "Run workflow"
- [ ] Tunggu hasilnya ✅

---

## 📝 Connection String Format

```
postgresql://postgres.[project-id]:[PASSWORD]@aws-0-ap-southeast-1.pooler.supabase.com:6543/postgres
```

**Ganti `[PASSWORD]` dengan password Supabase Anda!**

---

## 🔍 Cara Test Lokal (Optional)

```bash
# 1. Buat file .env
copy .env.example .env

# 2. Edit .env, isi DATABASE_URL

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run pipeline
python main.py
```

---

## ❓ Troubleshooting

| Error | Solusi |
|-------|--------|
| Warning: DATABASE_URL invalid | Secret belum ditambahkan ke GitHub |
| Connection refused | Password salah di connection string |
| Relation does not exist | Schema SQL belum dijalankan |
| Workflow masih error | Tunggu 5 menit, coba run ulang |

---

**📚 Panduan lengkap:** Lihat file `DATABASE_SETUP.md`
