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
    
    def _detect_category(self, text):
        """Deteksi kategori konten berdasarkan pola karakteristik"""
        if not text:
            return "General"
        
        # Convert to lowercase for easier matching
        text_lower = text.lower()
        
        # Code detection: banyak simbol {}, (), function keywords
        code_indicators = ['{', '}', 'function', 'class', 'def ', 'var ', 'const ', 'import ', 'return']
        code_score = sum(text.count(indicator) for indicator in code_indicators)
        
        # Academic detection: citation patterns, years in parentheses, author names
        academic_patterns = ['et al', 'references', 'abstract', 'journal', 'university', 'research']
        academic_score = sum(text_lower.count(pattern) for pattern in academic_patterns)
        # Check for year patterns (19xx, 20xx)
        import re
        year_matches = re.findall(r'\b(19|20)\d{2}\b', text)
        academic_score += len(year_matches) * 2
        
        # News detection: journalist terms, date mentions
        news_patterns = ['breaking', 'reported', 'according to', 'spokesperson', 'press release', 'journalist']
        news_score = sum(text_lower.count(pattern) for pattern in news_patterns)
        
        # Forum/Discussion detection
        forum_patterns = ['reply', 'quote', 'posted by', 'thread', 'username', 're:']
        forum_score = sum(text_lower.count(pattern) for pattern in forum_patterns)
        
        # Determine category based on highest score
        scores = {
            'Code': code_score,
            'Academic': academic_score,
            'News': news_score,
            'Forum': forum_score
        }
        
        max_category = max(scores, key=scores.get)
        max_score = scores[max_category]
        
        # Minimum threshold to classify (otherwise General)
        if max_score >= 5:
            return max_category
        
        return "General"

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
                
                # Auto-detect category
                category = self._detect_category(text)
                
                if url:
                    records.append((url, self._parse_isodate(ts), text, category))

            if not records:
                print("[DB] Tidak ada record valid untuk diinsert.")
                return True

            query = """
                INSERT INTO archived_documents (original_url, archive_timestamp, cleaned_text, category)
                VALUES %s
                ON CONFLICT (original_url, archive_timestamp) DO UPDATE 
                SET cleaned_text = EXCLUDED.cleaned_text,
                    category = EXCLUDED.category;
            """
            
            cur = conn.cursor()
            # Use page_size=100 to batch inserts and avoid "server closed connection" on large payloads
            execute_values(cur, query, records, page_size=100)
            conn.commit()
            print(f"[DB] Berhasil upsert {len(records)} data.")
            cur.close()
            return True

        except Exception as e:
            try:
                if conn: conn.rollback()
            except:
                pass # Connection was likely already closed
            print(f"[DB] Transaction Error: {e}")
            return False
        finally:
            conn.close()

    def init_db(self, schema_path):
        if not os.path.exists(schema_path):
             print(f"[DB] Schema file not found: {schema_path}")
             return False

        conn = self.get_connection()
        if not conn: return False
        try:
            with open(schema_path, 'r') as f:
                schema_sql = f.read()
            cur = conn.cursor()
            cur.execute(schema_sql)
            conn.commit()
            cur.close()
            print(f"[DB] Database initialized successfully.")
            return True
        except Exception as e:
            print(f"[DB] Init Error: {e}")
            try: conn.rollback()
            except: pass
            return False
        finally:
            conn.close()

    def fix_constraints(self):
        """Fixes the UNIQUE constraint issue on archived_documents"""
        conn = self.get_connection()
        if not conn: return
        try:
            cur = conn.cursor()
            # 1. Drop old constraint if exists (default name often archived_documents_original_url_key)
            cur.execute("""
                DO $$
                BEGIN
                    IF EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'archived_documents_original_url_key') THEN
                        ALTER TABLE archived_documents DROP CONSTRAINT archived_documents_original_url_key;
                    END IF;
                END $$;
            """)
            
            # 2. Add new constraint if missing
            cur.execute("""
                DO $$
                BEGIN
                    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'archived_documents_url_ts_unique') THEN
                        ALTER TABLE archived_documents ADD CONSTRAINT archived_documents_url_ts_unique UNIQUE (original_url, archive_timestamp);
                    END IF;
                END $$;
            """)
            
            conn.commit()
            cur.close()
            print("[DB] Schema constraints validated.")
        except Exception as e:
            # Clean up duplicates if adding constraint failed (Optional but good)
            print(f"[DB] Schema Fix Error (Non-fatal): {e}")
            try: conn.rollback()
            except: pass
        finally:
            conn.close()
