# Setup DATABASE_URL untuk GitHub Actions

## Ringkasan Masalah
GitHub Actions workflow `scrape.yml` menampilkan warning: **"Context access might be invalid: DATABASE_URL"** karena secret `DATABASE_URL` belum dikonfigurasi di repository.

## Pilihan Database

### ✅ **Opsi 1: Railway (RECOMMENDED - Jika Sudah Punya)**

Jika Anda sudah memiliki database PostgreSQL di Railway, **gunakan yang ini**! Tidak perlu buat database baru.

**Langkah Cepat:**
1. Login ke Railway.app
2. Buka project → Postgres service
3. Tab "Variables" → Copy `DATABASE_URL`
4. (Optional) Jika table belum ada, run query dari `db/schema.sql`
5. Tambahkan `DATABASE_URL` sebagai GitHub Secret (lihat Langkah 2 di bawah)

---

### 🆕 **Opsi 2: Supabase (Jika Belum Punya Database)**

### 🔹 Langkah 1: Buat Database di Supabase (Gratis)

1. **Buat Akun & Project**
   - Buka https://supabase.com
   - Login dengan GitHub atau email
   - Klik "New Project"
   - Isi informasi:
     - **Name**: `my-search-engine`
     - **Database Password**: Buat password kuat (SIMPAN INI!)
     - **Region**: Singapore (Southeast Asia)
   - Tunggu ~2 menit hingga project siap

2. **Setup Database Schema**
   - Klik "SQL Editor" di sidebar
   - Klik "New query"
   - Copy & paste isi file `db/schema.sql`
   - Klik "Run" atau tekan Ctrl+Enter

3. **Dapatkan Connection String**
   - Klik "Project Settings" (icon gear)
   - Pilih tab "Database"
   - Scroll ke "Connection string"
   - Pilih tab "URI"
   - Copy connection string, format:
     ```
     postgresql://postgres.[project-id]:[YOUR-PASSWORD]@aws-0-ap-southeast-1.pooler.supabase.com:6543/postgres
     ```
   - **PENTING**: Ganti `[YOUR-PASSWORD]` dengan password yang tadi dibuat

---

### 🔹 Langkah 2: Tambahkan Secret ke GitHub

1. Buka GitHub repository Anda
2. Klik **Settings** → **Secrets and variables** → **Actions**
3. Klik **"New repository secret"**
4. Masukkan:
   - **Name**: `DATABASE_URL`
   - **Secret**: Paste connection string dari Supabase
5. Klik **"Add secret"**

---

### 🔹 Langkah 3: Test Workflow

1. Buka tab **Actions** di GitHub
2. Pilih workflow **"Daily Scraper & Archiver"**
3. Klik **"Run workflow"** → **"Run workflow"**
4. Tunggu eksekusi selesai
5. Periksa log untuk memastikan tidak ada error

---

## Testing Lokal (Optional)

Untuk testing di komputer lokal:

1. Copy file `.env.example` menjadi `.env`
2. Edit `.env` dan isi `DATABASE_URL` dengan connection string Supabase Anda
3. Jalankan: `python main.py`

**PENTING**: File `.env` sudah ada di `.gitignore`, jadi tidak akan ter-commit ke GitHub.

---

## Troubleshooting

### Error: "connection refused"
- Pastikan connection string benar
- Cek apakah password sudah diganti di connection string
- Verifikasi region Supabase sesuai

### Error: "relation does not exist"
- Schema belum dijalankan
- Jalankan ulang query di SQL Editor Supabase

### Workflow masih error setelah setup
- Tunggu beberapa menit (GitHub Actions butuh waktu refresh secrets)
- Coba re-run workflow

---

## Catatan Keamanan

- ✅ Jangan pernah commit file `.env` ke GitHub
- ✅ Jangan share DATABASE_URL di public
- ✅ Gunakan GitHub Secrets untuk menyimpan credentials
- ✅ File `.gitignore` sudah mengabaikan `.env`
