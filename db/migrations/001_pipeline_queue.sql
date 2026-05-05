-- Nexus Ignis migration 001
-- Adds durable URL submission and pipeline job tracking.
-- Safe to run more than once.

BEGIN;

CREATE TABLE IF NOT EXISTS submitted_urls (
    id SERIAL PRIMARY KEY,
    url TEXT NOT NULL UNIQUE,
    normalized_url TEXT UNIQUE,
    source VARCHAR(50) DEFAULT 'unknown',
    status VARCHAR(40) NOT NULL DEFAULT 'pending',
    submitter_ip_hash TEXT,
    user_agent_hash TEXT,
    last_error TEXT,
    retry_count INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_checked_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX IF NOT EXISTS idx_submitted_urls_status
    ON submitted_urls (status);

CREATE INDEX IF NOT EXISTS idx_submitted_urls_created_at
    ON submitted_urls (created_at DESC);

CREATE TABLE IF NOT EXISTS pipeline_jobs (
    id SERIAL PRIMARY KEY,
    submitted_url_id INTEGER REFERENCES submitted_urls(id) ON DELETE SET NULL,
    url TEXT NOT NULL,
    job_type VARCHAR(50) NOT NULL DEFAULT 'archive_url',
    status VARCHAR(40) NOT NULL DEFAULT 'pending',
    priority INTEGER NOT NULL DEFAULT 100,
    locked_at TIMESTAMP WITH TIME ZONE,
    locked_by TEXT,
    started_at TIMESTAMP WITH TIME ZONE,
    finished_at TIMESTAMP WITH TIME ZONE,
    retry_count INTEGER NOT NULL DEFAULT 0,
    max_retries INTEGER NOT NULL DEFAULT 3,
    last_error TEXT,
    result JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_pipeline_jobs_status_priority
    ON pipeline_jobs (status, priority, created_at);

CREATE INDEX IF NOT EXISTS idx_pipeline_jobs_url
    ON pipeline_jobs (url);

CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_submitted_urls_updated_at ON submitted_urls;
CREATE TRIGGER trg_submitted_urls_updated_at
BEFORE UPDATE ON submitted_urls
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();

DROP TRIGGER IF EXISTS trg_pipeline_jobs_updated_at ON pipeline_jobs;
CREATE TRIGGER trg_pipeline_jobs_updated_at
BEFORE UPDATE ON pipeline_jobs
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();

COMMIT;
