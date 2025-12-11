import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

db_url = os.environ.get("DATABASE_URL")
if not db_url:
    print("DATABASE_URL not found!")
    exit(1)

try:
    conn = psycopg2.connect(db_url)
    cur = conn.cursor()
    print("Connected to DB.")
    
    # 1. Drop existing unique constraint on original_url
    # Note: We need to find the constraint name. Usually it's 'archived_documents_original_url_key'.
    print("Dropping legacy unique constraint...")
    try:
        cur.execute("ALTER TABLE archived_documents DROP CONSTRAINT IF EXISTS archived_documents_original_url_key;")
    except Exception as e:
        print(f"Warning dropping constraint: {e}")
        conn.rollback()
    
    # 2. Add composite unique constraint (url + timestamp)
    print("Adding composite unique constraint...")
    cur.execute("""
        CREATE UNIQUE INDEX IF NOT EXISTS idx_url_timestamp 
        ON archived_documents (original_url, archive_timestamp);
    """)
    
    conn.commit()
    print("Success: Database constraints updated to allow multiple snapshots per URL.")
    
    cur.close()
    conn.close()
except Exception as e:
    print(f"Error: {e}")
