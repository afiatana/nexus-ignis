import requests
import time
import os

class Collector:
    def __init__(self, input_file, output_file):
        self.input_file = input_file
        self.output_file = output_file

    def run(self):
        print(f"[Collector] Membaca {self.input_file}...")
        
        try:
            with open(self.input_file, "r", encoding="utf-8") as f:
                urls = [line.strip() for line in f if line.strip()]
        except FileNotFoundError:
            print(f"[Collector] Error: File {self.input_file} tidak ditemukan.")
            return False
        except Exception as e:
            print(f"[Collector] Error membaca file input: {e}")
            return False

        dead_urls = []
        total_urls = len(urls)
        print(f"[Collector] Ditemukan {total_urls} URL untuk divalidasi.\n")

        # Connect to DB for status updates
        try:
            from db.connector import DBConnector
            db = DBConnector()
            conn = db.get_connection()
            cur = conn.cursor() if conn else None
        except:
            conn = None
            cur = None

        for index, url in enumerate(urls, 1):
            target_url = url
            if not target_url.startswith(('http://', 'https://')):
                target_url = 'http://' + target_url

            is_dead = False
            reason = ""

            print(f"[{index}/{total_urls}] Mengecek: {url} ...", end=" ", flush=True)

            try:
                response = requests.head(target_url, timeout=5, allow_redirects=True)
                if response.status_code == 404:
                    is_dead = True
                    reason = "404 Not Found"
                else:
                    reason = f"Alive ({response.status_code})"
            except requests.exceptions.Timeout:
                is_dead = True
                reason = "Timeout"
            except requests.exceptions.RequestException as e:
                is_dead = True
                reason = f"Error ({type(e).__name__})"
            except Exception as e:
                is_dead = True
                reason = f"Unknown Error ({e})"

            if is_dead:
                print(f"-> MATI ({reason})")
                dead_urls.append(url)
            else:
                print(f"-> HIDUP ({reason})")

            # DB Update Logic
            if conn and cur:
                try:
                    if is_dead:
                        # If dead, mark as CONFIRMED
                        cur.execute("UPDATE reported_urls SET status='CONFIRMED_DEAD' WHERE url=%s", (url,))
                    else:
                        # If alive, remove from DB to save space
                        cur.execute("DELETE FROM reported_urls WHERE url=%s", (url,))
                        print(f"  [DB] URL hidup dihapus dari database.")
                    conn.commit()
                except Exception as e:
                    print(f"  [DB Sync Error]: {e}")

            time.sleep(1) # Faster rate limit for verification
            
        if conn:
            conn.close()

        print(f"\n[Collector] Menyimpan {len(dead_urls)} URL mati ke {self.output_file}...")
        try:
            with open(self.output_file, "w", encoding="utf-8") as f:
                for d_url in dead_urls:
                    f.write(d_url + "\n")
            print("[Collector] Selesai.")
            return True
        except Exception as e:
            print(f"[Collector] Gagal menyimpan file output: {e}")
            return False
