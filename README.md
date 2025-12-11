# 🔥 Nexus Ignis - Archive Search Engine

**Titik Hubung Pengetahuan yang Terlupakan**

Nexus Ignis adalah mesin pencari arsip digital yang menyelamatkan dan mengindeks konten web yang telah hilang. Melawan "Link Rot" dengan preservasi pengetahuan digital.

---

## 🚀 Fitur Utama

- **🔍 Smart Search** - Full-text search dengan autocomplete dan keyword highlighting
- **🤖 Auto-Categorization** - AI mendeteksi jenis konten (Code, Academic, News, Forum)
- **🔥 Browser Extension** - Auto-detect 404 pages saat browsing
- **👥 Community-Driven** - User dapat submit dead URLs via web form
- **⏰ Daily Automation** - GitHub Actions crawl & index otomatis
- **📡 Live Feed** - Real-time sidebar menampilkan recent reports
- **🌐 Open Source** - Transparent, auditable, community-owned

---

## 📦 Tech Stack

**Backend:**
- Python 3.11
- Flask (Web Framework)
- PostgreSQL (Database dengan Full-Text Search)
- BeautifulSoup + lxml (HTML Parsing)
- Requests (HTTP Client)

**Frontend:**
- Vanilla JavaScript
- Jinja2 Templates
- Retro Terminal CSS Theme

**Infrastructure:**
- Railway.app (Cloud Hosting)
- GitHub Actions (CI/CD + Automation)
- Internet Archive API (Content Source)

**Extension:**
- Chrome Manifest V3
- Service Worker API

---

## 🛠️ Setup Lokal

### Prerequisites
- Python 3.11+
- PostgreSQL database
- Git

### Installation

1. **Clone Repository:**
```bash
git clone https://github.com/afiatana/nexus-ignis.git
cd nexus-ignis
```

2. **Install Dependencies:**
```bash
pip install -r requirements.txt
```

3. **Setup Environment Variables:**
```bash
# Create .env file
DATABASE_URL=postgresql://user:password@localhost:5432/nexus_ignis
```

4. **Initialize Database:**
```bash
# Schema akan auto-init saat Flask app start
python -m web.app
```

5. **Run Development Server:**
```bash
python -m flask --app web.app run
```

Access: `http://localhost:5000`

---

## 🌐 Deployment ke Railway

### Step-by-Step

1. **Create Railway Account:** https://railway.app
2. **New Project** → Import from GitHub
3. **Add PostgreSQL Database:**
   - Add service → PostgreSQL
   - Copy connection URL

4. **Configure Environment:**
   - Variables → Add `DATABASE_URL`
   - Paste PostgreSQL connection URL

5. **Deploy:**
   - Railway auto-detects `Procfile`
   - Build & deploy otomatis

6. **Setup GitHub Actions Secret:**
   - GitHub repo → Settings → Secrets
   - Add `DATABASE_URL` dengan Railway PostgreSQL URL

---

## 🔄 Automated Pipeline (GitHub Actions)

**Schedule:** Every day at 02:00 WIB (19:00 UTC)

**Process:**
1. Read URLs from `data/seed_list.txt`
2. Validate HTTP status (filter dead URLs)
3. Query Wayback Machine for snapshots
4. Extract & clean text content
5. Auto-categorize content type
6. Insert to PostgreSQL database

**Manual Trigger:**
```
GitHub → Actions → Daily Scraper & Archiver → Run workflow
```

---

## 🔌 Browser Extension

### Installation

1. Download extension: Click "🔥 DOWNLOAD EXTENSION" on website
2. Extract ZIP file
3. Chrome → `chrome://extensions`
4. Enable "Developer mode"
5. Click "Load unpacked"
6. Select extracted folder

### Configuration

**IMPORTANT:** Edit `extension/background.js` line 2:

```javascript
// Change this:
const API_URL = 'https://your-railway-app.up.railway.app/submit-url';

// To your actual URL:
const API_URL = 'https://nexus-ignis-production.up.railway.app/submit-url';
```

Reload extension di Chrome.

---

## 📊 Usage

### Search Archive
1. Go to homepage
2. Enter query in search box
3. View results with category badges & highlights

### Submit Dead URL
1. Click "📡 LAPORKAN LINK MATI"
2. Enter dead URL
3. Submit  
4. URL appears in sidebar feed within 10 seconds

### Browse Live Feed
- Right sidebar shows recent 20 reported URLs
- Auto-refreshes every 10 seconds
- New submissions appear at #1

---

## 🗂️ Project Structure

```
nexus-ignis/
├── archivist/          # Data collection modules
│   ├── collector.py    # URL validator
│   └── retriever.py    # Archive fetcher
├── db/
│   ├── connector.py    # Database operations
│   └── schema.sql      # PostgreSQL schema
├── web/
│   ├── app.py          # Flask application
│   └── templates/      # HTML templates
├── extension/          # Chrome extension
├── .github/workflows/  # GitHub Actions
├── data/               # Data directory
├── main.py             # Pipeline entry point
├── requirements.txt    # Python dependencies
├── Procfile            # Railway config
└── runtime.txt         # Python version spec
```

---

## 🤝 Contributing

1. Fork repository
2. Create feature branch
3. Commit changes
4. Push & create Pull Request

---

## 📄 License

Open Source - MIT License

---

## 👨‍💻 Developer

Created by **Aaafa Fiatna**  
Web Developer & SEO Specialist

Portfolio: https://myportfolio-aafafiatna.vercel.app  
GitHub: https://github.com/afiatana/nexus-ignis

---

## 📞 Support

Issues: GitHub Issues  
Docs: `SMART_SEARCH_DOCS.md`, `GROWTH_STRATEGY.md`

---

**Nexus Ignis** © 2025 - Fighting Link Rot, One Archive at a Time 🔥
