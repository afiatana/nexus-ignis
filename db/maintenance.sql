-- =====================================
-- MAINTENANCE QUERIES
-- Jalankan secara berkala untuk menjaga performa database
-- =====================================

-- 1. CHECK CONNECTION COUNT
-- Jalankan jika suspect "too many connections"
-- =====================================

SELECT 
    count(*) as total_connections,
    count(*) FILTER (WHERE state = 'active') as active_connections,
    count(*) FILTER (WHERE state = 'idle') as idle_connections
FROM pg_stat_activity 
WHERE datname = 'railway';


-- 2. FIND SLOW QUERIES
-- Cari query yang berjalan lebih dari 5 detik
-- =====================================

SELECT 
    pid,
    now() - pg_stat_activity.query_start AS duration,
    state,
    query 
FROM pg_stat_activity 
WHERE state = 'active' 
  AND now() - pg_stat_activity.query_start > interval '5 seconds'
  AND datname = 'railway';


-- 3. CHECK DISK USAGE
-- Monitor storage usage
-- =====================================

-- Total database size
SELECT pg_size_pretty(pg_database_size('railway')) as database_size;

-- Table size dengan details
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS total_size,
    pg_size_pretty(pg_relation_size(schemaname||'.'||tablename)) AS table_size,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename) - pg_relation_size(schemaname||'.'||tablename)) AS index_size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;


-- 4. CHECK INDEX USAGE
-- Cek apakah index digunakan atau tidak
-- =====================================

SELECT 
    schemaname,
    tablename,
    indexname,
    idx_scan as times_used,
    pg_size_pretty(pg_relation_size(indexrelid)) as index_size
FROM pg_stat_user_indexes
WHERE schemaname = 'public'
ORDER BY idx_scan ASC;

-- Jika ada index dengan idx_scan = 0 atau sangat rendah, 
-- pertimbangkan untuk drop index tersebut


-- 5. TABLE STATISTICS
-- Lihat statistik table archived_documents
-- =====================================

SELECT 
    n_tup_ins as inserts,
    n_tup_upd as updates,
    n_tup_del as deletes,
    n_live_tup as live_rows,
    n_dead_tup as dead_rows,
    last_vacuum,
    last_autovacuum,
    last_analyze,
    last_autoanalyze
FROM pg_stat_user_tables
WHERE tablename = 'archived_documents';


-- 6. VACUUM ANALYZE (Weekly Maintenance)
-- Cleanup dead rows dan update statistics
-- =====================================

VACUUM (VERBOSE, ANALYZE) archived_documents;


-- 7. REINDEX (Monthly Maintenance)
-- Rebuild indexes untuk optimal performance
-- =====================================

-- Option 1: Reindex specific table
REINDEX TABLE archived_documents;

-- Option 2: Reindex specific index
-- REINDEX INDEX idx_archived_documents_search;


-- 8. CHECK FOR TABLE BLOAT
-- Cek apakah table memiliki bloat (wasted space)
-- =====================================

SELECT 
    current_database() AS database,
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS total_size,
    pg_size_pretty(pg_relation_size(schemaname||'.'||tablename)) AS table_size,
    ROUND(100 * pg_relation_size(schemaname||'.'||tablename) / 
          NULLIF(pg_total_relation_size(schemaname||'.'||tablename), 0), 2) AS table_pct
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;


-- 9. TOP 10 MOST COMMON CATEGORIES
-- Analytics: kategori apa yang paling banyak
-- =====================================

SELECT 
    category,
    count(*) as count,
    ROUND(100.0 * count(*) / (SELECT count(*) FROM archived_documents), 2) as percentage
FROM archived_documents
GROUP BY category
ORDER BY count DESC
LIMIT 10;


-- 10. RECENT ARCHIVED DOCUMENTS
-- Lihat 20 dokumen terakhir yang diarsipkan
-- =====================================

SELECT 
    id,
    original_url,
    category,
    LEFT(cleaned_text, 100) as text_preview,
    created_at
FROM archived_documents
ORDER BY created_at DESC
LIMIT 20;


-- 11. CLEANUP OLD DATA (Optional)
-- Jika database terlalu besar, archive data lama
-- HATI-HATI: Backup dulu sebelum delete!
-- =====================================

-- Step 1: Create archive table (uncomment untuk execute)
-- CREATE TABLE archived_documents_archive AS 
-- SELECT * FROM archived_documents 
-- WHERE created_at < NOW() - INTERVAL '6 months';

-- Step 2: Verify count
-- SELECT count(*) FROM archived_documents_archive;

-- Step 3: Delete dari main table (BACKUP DULU!)
-- DELETE FROM archived_documents 
-- WHERE created_at < NOW() - INTERVAL '6 months';

-- Step 4: Reclaim space
-- VACUUM FULL archived_documents;


-- =====================================
-- MAINTENANCE SCHEDULE RECOMMENDATION
-- =====================================

-- DAILY: Check #1 (connection count)
-- WEEKLY: Run #6 (VACUUM ANALYZE)
-- MONTHLY: Run #7 (REINDEX)
-- QUARTERLY: Check #8 (bloat check)
-- YEARLY: Consider #11 (archive old data)
