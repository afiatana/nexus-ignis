# 🚀 RUN PIPELINE UNTUK POPULATE DATABASE

## ❌ Masalah yang Terjadi

Search menampilkan "TIDAK ADA HASIL" karena **database masih kosong!**

Pipeline scraping belum pernah dijalankan, jadi:
- ❌ URL mati belum divalidasi
- ❌ Snapshot dari Wayback Machine belum diambil  
- ❌ Data belum masuk database PostgreSQL
- ❌ Search engine tidak punya data untuk dicari

---

## ✅ Solusi: Jalankan Pipeline

Ada **2 cara** untuk populate database:

### **Opsi 1: Manual Run Lokal (RECOMMENDED - Cepat!)**

#### **Step 1: Setup DATABASE_URL**

Buat file `.env`:

```bash
# Copy dari Railway
# Format: postgresql://postgres:password@host:port/railway
DATABASE_URL=your_database_url_from_railway
```

**Cara dapat DATABASE_URL dari Railway:**
1. Railway Dashboard → Postgres service
2. Tab "Variables" → Copy `DATABASE_URL`
3. Paste ke file `.env` di atas

#### **Step 2: Install Dependencies**

```bash
cd "c:\Users\q3j5c\OneDrive\Desktop\My Search Engine"
pip install -r requirements.txt
```

#### **Step 3: Run Pipeline!**

```bash
python main.py
```

Expected output:
```
=== STARTING ARCHIVE PIPELINE ===

--- [1] COLLECTOR & VALIDATOR ---
✅ Validating URLs...
✅ Found X dead URLs

--- [2] ARCHIVE RETRIEVER ---
✅ Fetching from Wayback Machine...
✅ Retrieved X snapshots

--- [3] DB INSERTION ---
✅ Inserting into database...
[DB] Berhasil upsert X data.

=== PIPELINE COMPLETED SUCCESSFULLY ===
```

**Timeline:** 5-10 menit tergantung jumlah URL

---

### **Opsi 2: Trigger GitHub Actions (Auto, tapi tunggu lama)**

#### **Manual Trigger GitHub Actions:**

1. Buka **GitHub repository** → Tab **"Actions"**
2. Pilih workflow **"Daily Scraper & Archiver"**
3. Klik **"Run workflow"** dropdown
4. Pilih branch **"master"**
5. Klik **"Run workflow"** button
6. Tunggu ~5-10 menit

**CONDITIONS:**
- ⚠️ Harus sudah set `DATABASE_URL` di GitHub Secrets
- ⚠️ Workflow berjalan di Railway (butuh credits/active plan)
- ⚠️ Lebih lambat dari run lokal

---

## 🎯 RECOMMENDED: Run Lokal Sekarang

Jalankan commands ini berurutan:

### **1. Buat .env file**

```powershell
cd "c:\Users\q3j5c\OneDrive\Desktop\My Search Engine"

# Buat file .env (akan open di notepad)
notepad .env
```

Lalu isi dengan:
```
DATABASE_URL=postgresql://postgres:PASSWORD@HOST:PORT/railway
```
*Ganti dengan connection string dari Railway!*

Save & close.

### **2. Install dependencies (jika belum)**

```powershell
pip install -r requirements.txt
```

### **3. Run pipeline!**

```powershell
python main.py
```

---

## 📊 Expected Pipeline Flow

```
START
  ↓
[1] COLLECTOR
  → Check kaskus.co.id (dead? ✅)
  → Check friendster.com (dead? ✅)
  → Check myspace.com (dead? ✅)
  → Write to dead_urls.txt
  ↓
[2] RETRIEVER
  → Query Wayback Machine for kaskus.co.id
  → Get snapshot HTML
  → Extract clean text
  → Save to archive_data.json
  ↓
[3] DB INDEXER
  → Read archive_data.json
  → INSERT into PostgreSQL
  → Auto-detect category
  ↓
DONE! ✅
  → Database sekarang ada data
  → Search "kaskus" = ADA HASIL! 🎉
```

---

## 🔍 Verify Database Setelah Run

### **Query di Railway:**

```sql
-- Check total data
SELECT COUNT(*) FROM archived_documents;

-- Check apakah kaskus ada
SELECT original_url, category, created_at 
FROM archived_documents 
WHERE original_url LIKE '%kaskus%';

-- Search test
SELECT original_url, 
       ts_headline('indonesian', cleaned_text, plainto_tsquery('indonesian', 'kaskus')) as snippet
FROM archived_documents
WHERE to_tsvector('indonesian', cleaned_text) @@ plainto_tsquery('indonesian', 'kaskus')
LIMIT 5;
```

---

## 🚨 Troubleshooting

### **Error: "DATABASE_URL not set"**

```bash
Solusi: Buat file .env dengan DATABASE_URL dari Railway
```

### **Error: "No module named 'requests'"**

```bash
Solusi: pip install -r requirements.txt
```

### **Error: "Connection refused" / Database error**

```bash
Solusi: 
1. Cek DATABASE_URL benar
2. Cek Railway database sedang running
3. Cek internet connection
```

### **Wayback Machine tidak menemukan snapshot**

```bash
Normal! Tidak semua URL punya snapshot.
Pipeline akan skip URL tanpa snapshot.
```

---

## ⏱️ Expected Timeline

| Step | Duration | Output |
|------|----------|--------|
| Collector | 1-2 min | Validate ~12 URLs |
| Retriever | 3-5 min | Fetch snapshots dari Wayback |
| DB Insert | 10 sec | Insert ~5-10 records |
| **TOTAL** | **5-10 min** | Database populated! |

---

## 📋 Checklist

Sebelum run pipeline:
- [ ] ✅ Railway Postgres database running
- [ ] ✅ DATABASE_URL sudah ada (dari Railway)
- [ ] ✅ File `.env` sudah dibuat dengan DATABASE_URL
- [ ] ✅ Dependencies sudah install (`pip install -r requirements.txt`)
- [ ] ✅ seed_list.txt ada URLs (sudah ada ✅)

Run pipeline:
- [ ] ⚠️ `python main.py` (LAKUKAN SEKARANG!)

After pipeline:
- [ ] Verify data di database (query di atas)
- [ ] Test search di web app
- [ ] Search "kaskus" should show results! 🎉

---

## 🎊 After Success

Setelah pipeline berhasil:

✅ Database populated dengan archived content  
✅ Search "kaskus" akan tampil hasil  
✅ Full-text search works  
✅ Category auto-detected  
✅ GitHub Actions akan run otomatis setiap hari jam 2 pagi  

---

**Ready? Jalankan commands di atas sekarang untuk populate database! 🚀**

Share output jika ada error! 😊
