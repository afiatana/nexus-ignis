-- Enable the UUID extension if we were using UUIDs, but we are using SERIAL here.
-- Just creating the table as requested.

CREATE TABLE IF NOT EXISTS archived_documents (
    id SERIAL PRIMARY KEY,
    original_url TEXT UNIQUE NOT NULL,
    archive_timestamp TIMESTAMP WITH TIME ZONE, -- Menggunakan TIMESTAMPTZ agar akurat
    cleaned_text TEXT,
    category VARCHAR(50) DEFAULT 'General', -- Auto-detected category
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Membuat GIN Index untuk Full-Text Search yang efisien
-- Menggunakan konfigurasi 'indonesian' untuk stemming dan stop words bahasa Indonesia.
-- Jika database tidak memiliki config 'indonesian' (defaultnya biasanya ada), fallback ke 'simple' atau 'english'.
-- Syntax: CREATE INDEX name ON table USING GIN (to_tsvector('config', column));

CREATE INDEX IF NOT EXISTS idx_archived_documents_search 
ON archived_documents 
USING GIN (to_tsvector('indonesian', cleaned_text));
