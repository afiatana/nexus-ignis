# Setup GitHub Actions dengan Railway Database

## 🚀 Panduan Cepat (5 Menit)

Karena Anda sudah memiliki database PostgreSQL di Railway, setup menjadi sangat mudah!

---

### **Langkah 1: Dapatkan DATABASE_URL dari Railway**

1. Buka **Railway.app** dan login
2. Pilih **project** Anda
3. Klik pada **Postgres** service (ikon database)
4. Pilih tab **"Variables"** atau **"Connect"**
5. **Copy** nilai `DATABASE_URL`
   
   Format biasanya:
   ```
   postgresql://postgres:password@containers-us-west-xxx.railway.app:5432/railway
   ```

6. **SIMPAN** connection string ini (akan digunakan di langkah 3)

---

### **Langkah 2: Verifikasi Database Schema (Optional)**

#### Opsi A: Gunakan Railway Query Tool
1. Di Railway, pilih Postgres service
2. Klik tab **"Data"** atau **"Query"**
3. Jalankan query ini untuk cek apakah table sudah ada:
   ```sql
   SELECT table_name 
   FROM information_schema.tables 
   WHERE table_name = 'archived_documents';
   ```
4. Jika **tidak ada hasil**, jalankan schema:
   - Copy isi dari file `db/schema.sql`
   - Paste dan jalankan di Query tool

#### Opsi B: Gunakan Tool External (pgAdmin/DBeaver)
1. Install pgAdmin atau DBeaver
2. Create new connection dengan DATABASE_URL dari Railway
3. Jalankan query dari `db/schema.sql`

#### Opsi C: Test Langsung
Kalau Anda yakin table sudah ada, skip langkah ini! Pipeline akan error jika table tidak ada.

---

### **Langkah 3: Tambahkan GitHub Secret**

1. Buka **GitHub repository** Anda di browser
2. Klik **Settings** (tab paling kanan)
3. Di sidebar kiri: **Secrets and variables** → **Actions**
4. Klik tombol **"New repository secret"**
5. Isi form:
   - **Name**: `DATABASE_URL`
   - **Secret**: Paste DATABASE_URL dari Railway (dari Langkah 1)
6. Klik **"Add secret"**

✅ **Warning di GitHub Actions akan hilang!**

---

### **Langkah 4: Test Workflow**

1. Buka tab **Actions** di GitHub repository
2. Pilih workflow **"Daily Scraper & Archiver"**
3. Klik **"Run workflow"** button
4. Pilih branch (biasanya `main`)
5. Klik **"Run workflow"**
6. Tunggu beberapa detik
7. Klik pada workflow run yang baru muncul
8. Lihat log untuk memastikan berhasil ✅

Jika berhasil, Anda akan lihat:
```
[DB] Berhasil upsert X data.
=== PIPELINE COMPLETED SUCCESSFULLY ===
```

---

### **Langkah 5: Setup Local Development (Optional)**

Untuk testing di komputer lokal:

1. Copy file `.env.example` menjadi `.env`:
   ```bash
   copy .env.example .env
   ```

2. Edit file `.env` dan isi dengan DATABASE_URL dari Railway:
   ```
   DATABASE_URL=postgresql://postgres:password@containers-us-west-xxx.railway.app:5432/railway
   ```

3. Test jalankan pipeline:
   ```bash
   python main.py
   ```

**PENTING:** File `.env` sudah di-ignore oleh git, jadi aman untuk development lokal.

---

## 🎯 Kenapa Gunakan Satu Database Saja?

| Keuntungan | Penjelasan |
|------------|------------|
| 💰 **Hemat Biaya** | Railway free tier sudah cukup untuk project ini |
| 🎯 **Data Konsisten** | Semua data tersimpan di satu tempat |
| 🛠️ **Mudah Maintain** | Tidak perlu manage dua database berbeda |
| ⚡ **Simple** | Less complexity = less bugs |

---

## ❓ Troubleshooting

### ❌ Warning masih muncul setelah add secret
**Solusi:** Tunggu 2-3 menit, GitHub Actions perlu waktu untuk refresh. Lalu coba run workflow lagi.

### ❌ Connection Error saat workflow run
**Solusi:** 
- Pastikan DATABASE_URL yang di-copy sudah benar dan lengkap
- Cek apakah Railway database masih aktif
- Verifikasi tidak ada typo saat paste ke GitHub Secrets

### ❌ "relation does not exist" error
**Solusi:** Table belum dibuat. Jalankan schema dari `db/schema.sql` di Railway Query tool.

### ❌ Workflow timeout
**Solusi:** Mungkin banyak URL yang di-scrape. Ini normal, tunggu sampai selesai.

---

## 📊 Monitoring Database

Untuk melihat data yang sudah masuk ke database:

1. Buka Railway → Postgres service → tab **Data**
2. Atau gunakan query:
   ```sql
   SELECT COUNT(*) FROM archived_documents;
   SELECT * FROM archived_documents ORDER BY created_at DESC LIMIT 10;
   ```

---

## 🔒 Security Best Practices

✅ **DO:**
- Gunakan GitHub Secrets untuk DATABASE_URL
- Jangan commit file `.env` ke repository
- Rotate database password secara berkala

❌ **DON'T:**
- Jangan share DATABASE_URL di public
- Jangan hardcode DATABASE_URL di code
- Jangan commit credentials

---

**Selamat! Setup Anda sudah lengkap! 🎉**
