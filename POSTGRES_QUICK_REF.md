# ⚡ Railway Postgres - Quick Reference Card

## 🎯 Setup Cepat (5 Menit)

### 1. Jalankan Optimization Script
```bash
# Di Railway Query Tool atau pgAdmin, jalankan:
db/optimize.sql
```

✅ Script ini akan:
- Membuat index tambahan untuk performa
- Optimize PostgreSQL settings
- Analyze table statistics

### 2. Verifikasi
```sql
-- Cek apakah index sudah dibuat
SELECT indexname FROM pg_indexes WHERE tablename = 'archived_documents';

-- Cek database size
SELECT pg_size_pretty(pg_database_size('railway'));
```

---

## 📊 Monitoring Harian (1 Menit)

### Check Resource Usage di Railway Dashboard
1. Login Railway → Project → Postgres service
2. Tab **"Metrics"** → Lihat:
   - ✅ Disk usage (jangan sampai >80%)
   - ✅ Memory usage
   - ✅ CPU usage

### Quick Health Check Query
```sql
-- Copy-paste di Railway Query tool
SELECT 
    pg_size_pretty(pg_database_size('railway')) as db_size,
    (SELECT count(*) FROM archived_documents) as total_records,
    (SELECT count(*) FROM pg_stat_activity WHERE datname='railway') as connections;
```

---

## 🔧 Maintenance Schedule

| Frequency | Action | File | Time |
|-----------|--------|------|------|
| **Daily** | Check metrics di Railway | Dashboard | 1 min |
| **Weekly** | Run VACUUM ANALYZE | `maintenance.sql` #6 | 2 min |
| **Monthly** | Run REINDEX | `maintenance.sql` #7 | 5 min |
| **Quarterly** | Check bloat | `maintenance.sql` #8 | 2 min |

### Quick Copy-Paste Commands

**Weekly (Setiap Minggu):**
```sql
VACUUM ANALYZE archived_documents;
```

**Monthly (Setiap Bulan):**
```sql
REINDEX TABLE archived_documents;
```

---

## 🚨 Troubleshooting

### Issue: Database penuh (disk 100%)

```sql
-- 1. Check table size
SELECT pg_size_pretty(pg_total_relation_size('archived_documents'));

-- 2. Cleanup
VACUUM FULL archived_documents;

-- 3. Jika masih penuh, archive old data (BACKUP DULU!)
-- Lihat maintenance.sql #11
```

### Issue: Slow queries

```sql
-- 1. Find slow queries
SELECT pid, now() - query_start AS duration, query 
FROM pg_stat_activity 
WHERE state = 'active' AND now() - query_start > interval '5 seconds';

-- 2. Analyze slow query
EXPLAIN ANALYZE [your_slow_query_here];

-- 3. Add index jika perlu
```

### Issue: Too many connections

```sql
-- Check connections
SELECT count(*) FROM pg_stat_activity WHERE datname = 'railway';

-- Railway free tier limit: 20 connections
-- Solusi: Close unused connections atau upgrade plan
```

---

## 💰 Cost Optimization

### Free Tier Limits
- ✅ 512 MB RAM
- ✅ 1 GB Storage
- ✅ 20 Connections
- ⚠️ Sleeps after 5 min inactivity

### Kapan Upgrade?

| Scenario | Recommendation |
|----------|----------------|
| Database <1GB, <1000 URLs | ✅ Free tier |
| Database 1-5GB, 1000-10k URLs | 💰 Developer ($5) |
| Database >5GB, >10k URLs | 💰💰 Team ($20) |
| Production, need 24/7 uptime | 💰 Developer+ |

---

## 📈 Performance Tips

### ✅ DO's
- Use full-text search index untuk searching
- Run VACUUM weekly
- Monitor disk usage
- Use prepared statements di code
- Limit query results dengan LIMIT

### ❌ DON'Ts
- Jangan pakai LIKE '%keyword%' (slow!)
- Jangan SELECT * jika tidak perlu semua columns
- Jangan forget to close connections
- Jangan skip maintenance
- Jangan delete backup tanpa backup baru

---

## 🎯 Quick Wins (Lakukan Sekarang!)

### 1. Run Optimization (5 min)
```bash
# Di Railway Query Tool:
# 1. Copy isi db/optimize.sql
# 2. Paste & Run
# 3. Done! ✅
```

### 2. Set Reminder (1 min)
- [ ] Calendar reminder: **"VACUUM database"** - Every Sunday
- [ ] Calendar reminder: **"REINDEX database"** - Every 1st of month
- [ ] Calendar reminder: **"Check disk usage"** - Every Monday

### 3. Monitor Now (2 min)
- [ ] Buka Railway Dashboard → Metrics
- [ ] Screenshot current usage sebagai baseline
- [ ] Set alarm jika disk >80%

---

## 📱 Emergency Contact

Jika database crash atau masalah serius:

1. **Check Railway Status:** https://railway.statuspage.io/
2. **Railway Discord:** https://discord.gg/railway
3. **Backup terakhir:** `.github/workflows/db_backup.yml`
4. **Restore dari backup:**
   ```bash
   psql $DATABASE_URL < backup.sql
   ```

---

## 🔗 Useful Links

- 📖 Full Guide: `RAILWAY_POSTGRES_OPTIMIZATION.md`
- 🛠️ Optimize Script: `db/optimize.sql`
- 🔧 Maintenance Queries: `db/maintenance.sql`
- 🚀 Railway Dashboard: https://railway.app
- 📚 PostgreSQL Docs: https://www.postgresql.org/docs/

---

**Last Updated:** 2025-12-12  
**Database Version:** PostgreSQL 15+  
**Platform:** Railway.app
