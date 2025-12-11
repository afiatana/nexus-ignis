import os
import sys
from archivist.collector import Collector
from archivist.retriever import ArchiveRetriever
from db.connector import DBConnector
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

def main():
    print("=== STARTING ARCHIVE PIPELINE ===\n")

    # DEFINE PATHS
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(base_dir, "data")
    
    # Ensure data dir exists
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)

    # Input/Output Files
    seed_file = os.path.join(data_dir, "seed_list.txt")
    dead_urls_file = os.path.join(data_dir, "dead_urls.txt")
    archive_json = os.path.join(data_dir, "archive_data.json")

    # Check if seed list exists, if not create dummy
    if not os.path.exists(seed_file):
        print(f"File seed_list.txt tidak ditemukan di {seed_file}. Membuat dummy...")
        with open(seed_file, "w") as f:
            f.write("https://google.com\nhttps://thisurldoesnotexist123456789.com\nhttps://friendster.com")
            
    # Sync Reports from DB to Seed List
    try:
        from db.connector import DBConnector
        db_reports = DBConnector()
        conn = db_reports.get_connection()
        if conn:
            cur = conn.cursor()
            cur.execute("SELECT url FROM reported_urls WHERE status='PENDING'")
            pending_urls = [row[0] for row in cur.fetchall()]
            
            if pending_urls:
                print(f"\n[Sync] Found {len(pending_urls)} pending reports in DB.")
                with open(seed_file, "a", encoding="utf-8") as f:
                    f.write("\n" + "\n".join(pending_urls))
                print(f"[Sync] Added to seed_list.txt")
                
                # Update status to PROCESSING
                cur.execute("UPDATE reported_urls SET status='PROCESSING' WHERE status='PENDING'")
                conn.commit()
                
            cur.close()
            conn.close()
    except Exception as e:
        print(f"[Sync] Warning: Failed to sync DB reports: {e}")
    
    # --- MODULE 1: COLLECTOR ---
    print("\n--- [1] COLLECTOR & VALIDATOR ---")
    collector = Collector(seed_file, dead_urls_file)
    if not collector.run():
        print("Collector gagal. Menghentikan proses.")
        sys.exit(1)

    # --- MODULE 2: RETRIEVER ---
    print("\n--- [2] ARCHIVE RETRIEVER ---")
    retriever = ArchiveRetriever(dead_urls_file, archive_json)
    if not retriever.run():
        print("Retriever gagal. Menghentikan proses.")
        sys.exit(1)

    # --- MODULE 3: DB INDEXER ---
    print("\n--- [3] DB INSERTION ---")
    db = DBConnector()
    if not db.insert_archive_data(archive_json):
        print("Database insertion gagal.")
        sys.exit(1)

    print("\n=== PIPELINE COMPLETED SUCCESSFULLY ===")

if __name__ == "__main__":
    main()
