# 🔥 Nexus Ignis - Dead Link Hunter Extension

## Instalasi Chrome Extension (Developer Mode)

1. **Download Extension**
   - Klik tombol "🔥 DOWNLOAD EXTENSION" di website Nexus Ignis
   - Extract file `nexus-ignis-extension.zip`

2. **Install ke Chrome**
   - Buka Chrome browser
   - Ketik `chrome://extensions` di address bar
   - Aktifkan "Developer mode" (toggle di pojok kanan atas)
   - Klik "Load unpacked"
   - Pilih folder hasil extract extension

3. **Konfigurasi (PENTING!)**
   - Buka file `background.js` di folder extension
   - Ganti URL API:
     ```javascript
     // Ganti ini:
     'https://your-railway-app.up.railway.app/submit-url'
     
     // Dengan URL Railway Anda yang sebenarnya:
     'https://nexus-ignis-production.up.railway.app/submit-url'
     ```
   - Save file dan reload extension di Chrome

## Cara Kerja

### Auto-Detection (Otomatis)
Extension akan otomatis mendeteksi halaman 404 berdasarkan:
- Judul halaman mengandung "404", "not found", dll
- Konten halaman mengandung indikator error

Saat terdeteksi, URL akan langsung dikirim ke Nexus Ignis!

### Manual Submission
1. Klik icon extension (🔥) di toolbar
2. URL halaman saat ini otomatis terisi
3. Klik "REPORT DEAD LINK"

## Fitur

✅ Auto-detect 404 pages  
✅ Manual submission via popup  
✅ Notification saat berhasil report  
✅ Duplicate check (tidak akan report URL yang sama 2x)

## Privacy

Extension ini HANYA mengirim:
- URL halaman yang terdeteksi 404
- Timestamp

Tidak ada data pribadi yang dikumpulkan.

---

**Nexus Ignis** - Archived Knowledge Hunter 🔍🔥
