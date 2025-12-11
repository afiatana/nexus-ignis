import os
import json
import psycopg2
from psycopg2.extras import execute_values
from datetime import datetime

class DBConnector:
    def __init__(self, db_url=None):
        self.db_url = db_url or os.environ.get("DATABASE_URL")

    def get_connection(self):
        if not self.db_url:
            print("[DB] Error: DATABASE_URL not set.")
            return None
        try:
            return psycopg2.connect(self.db_url)
        except Exception as e:
            print(f"[DB] Connection Error: {e}")
            return None

    def _parse_isodate(self, date_str):
        if not date_str: return None
        try:
            return datetime.strptime(date_str, "%Y%m%d%H%M%S")
        except ValueError:
            return None

    def insert_archive_data(self, json_file):
        if not os.path.exists(json_file):
            print(f"[DB] File {json_file} tidak ditemukan.")
            return False

        conn = self.get_connection()
        if not conn:
            return False

        try:
            with open(json_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            if not data:
                print("[DB] Tidak ada data JSON.")
                return False

            records = []
            for item in data:
                url = item.get("original_url")
                ts = item.get("archive_timestamp")
                text = item.get("cleaned_text", "")
                
                if url:
                    records.append((url, self._parse_isodate(ts), text))

            if not records:
                print("[DB] Tidak ada record valid untuk diinsert.")
                return True

            query = """
                INSERT INTO archived_documents (original_url, archive_timestamp, cleaned_text)
                VALUES %s
                ON CONFLICT (original_url) DO UPDATE 
                SET archive_timestamp = EXCLUDED.archive_timestamp,
                    cleaned_text = EXCLUDED.cleaned_text;
            """
            
            cur = conn.cursor()
            execute_values(cur, query, records)
            conn.commit()
            print(f"[DB] Berhasil upsert {len(records)} data.")
            cur.close()
            return True

        except Exception as e:
            conn.rollback()
            print(f"[DB] Transaction Error: {e}")
            return False
        finally:
            conn.close()
