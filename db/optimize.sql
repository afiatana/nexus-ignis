-- =====================================
-- OPTIMIZATION SCRIPT FOR RAILWAY POSTGRES
-- Jalankan script ini untuk optimisasi performa database
-- =====================================

-- 1. CREATE ADDITIONAL INDEXES untuk performa lebih baik
-- =====================================

-- Index untuk URL lookup (cek URL sudah ada di database atau belum)
CREATE INDEX IF NOT EXISTS idx_archived_documents_url 
ON archived_documents (original_url);

-- Index untuk sorting by date (newest first)
CREATE INDEX IF NOT EXISTS idx_archived_documents_created 
ON archived_documents (created_at DESC);

-- Index untuk filtering by category
CREATE INDEX IF NOT EXISTS idx_archived_documents_category 
ON archived_documents (category);

-- Composite index untuk query dengan filter category + sort by date
CREATE INDEX IF NOT EXISTS idx_archived_documents_category_created 
ON archived_documents (category, created_at DESC);

-- Partial index untuk non-empty text (optimize storage)
CREATE INDEX IF NOT EXISTS idx_archived_documents_nonempty_text 
ON archived_documents (cleaned_text) 
WHERE cleaned_text IS NOT NULL AND cleaned_text != '';


-- 2. OPTIMIZE PostgreSQL SETTINGS
-- =====================================

-- Increase work memory untuk full-text search queries
ALTER DATABASE railway SET work_mem = '16MB';

-- Optimize random page cost (lower = faster for SSD)
ALTER DATABASE railway SET random_page_cost = 1.1;

-- Better statistics untuk query planner
ALTER DATABASE railway SET default_statistics_target = 100;

-- Enable efficient query planning
ALTER DATABASE railway SET effective_cache_size = '128MB';


-- 3. ANALYZE TABLES untuk update statistics
-- =====================================

ANALYZE archived_documents;


-- 4. VERIFY INDEX CREATION
-- =====================================

-- Check all indexes on archived_documents table
SELECT 
    indexname,
    indexdef
FROM pg_indexes
WHERE tablename = 'archived_documents'
ORDER BY indexname;


-- 5. CHECK DATABASE SIZE
-- =====================================

SELECT 
    pg_size_pretty(pg_database_size('railway')) as database_size,
    pg_size_pretty(pg_total_relation_size('archived_documents')) as table_size,
    (SELECT count(*) FROM archived_documents) as total_records;


-- =====================================
-- Script selesai!
-- Jalankan VACUUM ANALYZE untuk finalize optimization
-- =====================================

VACUUM ANALYZE archived_documents;
