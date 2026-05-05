-- Nexus Ignis migration 002
-- Search quality upgrade: title/domain/snapshot URL, archive year, and indexes.
-- Safe to run more than once.

BEGIN;

ALTER TABLE archived_documents
    ADD COLUMN IF NOT EXISTS title TEXT,
    ADD COLUMN IF NOT EXISTS domain TEXT,
    ADD COLUMN IF NOT EXISTS snapshot_url TEXT,
    ADD COLUMN IF NOT EXISTS archive_year INTEGER,
    ADD COLUMN IF NOT EXISTS content_hash TEXT,
    ADD COLUMN IF NOT EXISTS word_count INTEGER,
    ADD COLUMN IF NOT EXISTS last_indexed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW();

-- Backfill domain from original_url where possible.
UPDATE archived_documents
SET domain = lower(regexp_replace(original_url, '^https?://([^/]+).*$', '\1'))
WHERE (domain IS NULL OR domain = '')
  AND original_url ~* '^https?://';

-- Backfill archive_year from archive_timestamp.
UPDATE archived_documents
SET archive_year = EXTRACT(YEAR FROM archive_timestamp)::INTEGER
WHERE archive_year IS NULL
  AND archive_timestamp IS NOT NULL;

-- Backfill a minimal title when no extracted title exists yet.
UPDATE archived_documents
SET title = left(regexp_replace(coalesce(cleaned_text, ''), '\s+', ' ', 'g'), 120)
WHERE title IS NULL
  AND cleaned_text IS NOT NULL
  AND length(cleaned_text) > 0;

CREATE INDEX IF NOT EXISTS idx_archived_documents_domain
    ON archived_documents (domain);

CREATE INDEX IF NOT EXISTS idx_archived_documents_archive_year
    ON archived_documents (archive_year);

CREATE INDEX IF NOT EXISTS idx_archived_documents_category
    ON archived_documents (category);

CREATE INDEX IF NOT EXISTS idx_archived_documents_snapshot_url
    ON archived_documents (snapshot_url);

CREATE INDEX IF NOT EXISTS idx_archived_documents_content_hash
    ON archived_documents (content_hash);

-- Weighted full-text search index.
-- Title is strongest, domain is medium, body is lowest.
CREATE INDEX IF NOT EXISTS idx_archived_documents_weighted_search
ON archived_documents
USING GIN (
    setweight(to_tsvector('indonesian', coalesce(title, '')), 'A') ||
    setweight(to_tsvector('simple', coalesce(domain, '')), 'B') ||
    setweight(to_tsvector('indonesian', coalesce(cleaned_text, '')), 'D')
);

COMMIT;
