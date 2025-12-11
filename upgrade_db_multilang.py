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
    conn.autocommit = True
    cur = conn.cursor()
    print("Connected to DB.")
    
    # Add English index for full-text search
    print("Adding English GIN index...")
    cur.execute("""
        CREATE INDEX IF NOT EXISTS idx_archived_documents_search_english 
        ON archived_documents 
        USING GIN (to_tsvector('english', cleaned_text));
    """)
    
    print("Success: English index added.")
    
    cur.close()
    conn.close()
except Exception as e:
    print(f"Error: {e}")
