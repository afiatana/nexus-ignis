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
    
    # Add category column
    print("Adding category column...")
    cur.execute("""
        ALTER TABLE archived_documents 
        ADD COLUMN IF NOT EXISTS category VARCHAR(50) DEFAULT 'General';
    """)
    
    conn.commit()
    print("Success: Column 'category' added.")
    
    cur.close()
    conn.close()
except Exception as e:
    print(f"Error: {e}")
