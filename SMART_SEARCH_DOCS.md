# 🔥 NEXUS IGNIS - SMART SEARCH DOCUMENTATION

## Fitur Smart Search yang Telah Diimplementasikan

### ✅ 1. HIGHLIGHTING (Penyorotan Kata Kunci)
**Status:** Sudah aktif sejak awal

**Teknologi:** PostgreSQL `ts_headline()`
- Kata kunci yang dicari otomatis di-highlight dengan tag `<b>` 
- Styling retro: Background gelap + warna accent orange-red
- Contoh: Jika user mencari "Algoritma", kata tersebut akan muncul **tebal** dan berwarna di snippet

**Kode Implementasi:**
```sql
ts_headline('indonesian', cleaned_text, plainto_tsquery('indonesian', %s))
```

---

### ✅ 2. RANKING (Peringkat Relevansi)
**Status:** Sudah aktif sejak awal

**Teknologi:** PostgreSQL `ts_rank()`
- Dokumen dengan frekuensi kata kunci tertinggi muncul paling atas
- Menggunakan algoritma TF-IDF (Term Frequency-Inverse Document Frequency)
- Hasil diurutkan dari yang PALING RELEVAN ke yang kurang relevan

**Kode Implementasi:**
```sql
ORDER BY ts_rank(to_tsvector('indonesian', cleaned_text), 
                 plainto_tsquery('indonesian', %s)) DESC
```

---

### ✅ 3. AUTO-CATEGORIZATION (Filter Niche) ⭐ BARU!
**Status:** BARU DITAMBAHKAN

#### Kategori yang Terdeteksi:

1. **CODE** 🟢 (Hijau Neon)
   - Indikator: `{`, `}`, `function`, `class`, `def`, `var`, `const`, `import`, `return`
   - Threshold: Minimal 5 simbol/keyword code
   - Badge Color: Matrix Green (#00ff41)

2. **ACADEMIC** 🔵 (Biru Cyan)
   - Indikator: `et al`, `references`, `abstract`, `journal`, `university`, `research`
   - Pola tahun: (19xx, 20xx) di-weight 2x
   - Badge Color: Cyan (#00bfff)

3. **NEWS** 🟡 (Kuning/Amber)
   - Indikator: `breaking`, `reported`, `according to`, `spokesperson`, `press release`
   - Badge Color: Orange (#ffaa00)

4. **FORUM** 🟣 (Magenta)
   - Indikator: `reply`, `quote`, `posted by`, `thread`, `username`, `re:`
   - Badge Color: Magenta (#ff00ff)

5. **GENERAL** ⚪ (Abu-abu)
   - Default jika semua score < 5
   - Badge Color: Amber secondary

#### Algoritma Scoring:
```python
def _detect_category(text):
    # Hitung kemunculan indikator untuk setiap kategori
    code_score = sum(occurrences of code_indicators)
    academic_score = sum(occurrences of academic_patterns) + year_matches * 2
    news_score = sum(occurrences of news_patterns)
    forum_score = sum(occurrences of forum_patterns)
    
    # Pilih kategori dengan score tertinggi
    if max_score >= 5:
        return max_category
    else:
        return "General"
```

---

## Perubahan Database

### Schema Update:
```sql
ALTER TABLE archived_documents 
ADD COLUMN category VARCHAR(50) DEFAULT 'General';
```

**Field Baru:**
- `category`: Menyimpan hasil deteksi otomatis (Code/Academic/News/Forum/General)
- Auto-populated saat data baru masuk
- Diupdate jika konten berubah (ON CONFLICT DO UPDATE)

---

## Visual Badge System

Setiap hasil pencarian sekarang memiliki **badge kategori** di samping URL:

```
┌─────────────────────────────────────────────┐
│ https://stackoverflow.com/... [CODE]        │ <- Badge hijau neon
├─────────────────────────────────────────────┤
│ https://scholar.google.com/... [ACADEMIC]   │ <- Badge biru cyan
├─────────────────────────────────────────────┤
│ https://detik.com/... [NEWS]                │ <- Badge orange
└─────────────────────────────────────────────┘
```

**Styling:**
- Background: Dark navy (#1a1a2e)
- Border: Matching color dengan teks
- Font: Bold, uppercase, monospace
- Hover: Tidak ada (static badge)

---

## Testing

1. **Data Masuk Baru:**
   - Saat GitHub Actions jalan malam ini, semua data baru akan otomatis dikategorikan
   - Kategori tersimpan permanen di database

2. **Pencarian:**
   - User search "python tutorial" → Hasil dengan kategori CODE akan dominan
   - User search "penelitian AI" → Hasil dengan kategori ACADEMIC akan muncul
   - Keyword highlighting tetap aktif untuk semua kategori

3. **Badge Display:**
   - Badge muncul di sebelah URL pada setiap result card
   - Warna berbeda untuk setiap kategori (retro terminal aesthetic)

---

## Flow Lengkap

```
1. GitHub Actions mengambil URL mati (seed_list.txt)
         ↓
2. Wayback Machine memberikan konten arsip
         ↓
3. DBConnector._detect_category() menganalisis teks
         ↓
4. Kategori disimpan ke PostgreSQL bersama konten
         ↓
5. User melakukan pencarian
         ↓
6. Backend mengambil hasil + kategori
         ↓
7. Frontend menampilkan badge berwarna sesuai kategori
```

---

## Kelebihan Sistem Ini

✅ **100% Otomatis** - Tidak perlu manual tagging
✅ **Real-time** - Kategorisasi saat insert data
✅ **Scalable** - Bisa menangani ribuan dokumen
✅ **Extensible** - Mudah menambah kategori baru (edit `_detect_category()`)
✅ **Visual** - User langsung tahu jenis konten tanpa perlu baca

---

## Status Deployment

✅ Semua perubahan sudah di-push ke GitHub: **38297c3**
✅ Railway akan auto-deploy dalam 2-5 menit
✅ Database schema akan auto-update saat app restart
✅ Data lama akan tetap ada (kategori = "General" by default)

---

**Nexus Ignis** sekarang memiliki sistem pencarian yang benar-benar pintar! 🚀🔥
