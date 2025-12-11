import requests
import json
import time
import os
from bs4 import BeautifulSoup

class ArchiveRetriever:
    def __init__(self, input_file, output_file):
        self.input_file = input_file
        self.output_file = output_file

    def run(self):
        print(f"[Retriever] Membaca {self.input_file}...")
        try:
            if not os.path.exists(self.input_file):
                 print(f"[Retriever] Error: File {self.input_file} tidak ditemukan.")
                 return False

            with open(self.input_file, "r", encoding="utf-8") as f:
                urls = [line.strip() for line in f if line.strip()]
        except Exception as e:
            print(f"[Retriever] Error membaca input: {e}")
            return False

        results = []
        total_urls = len(urls)
        print(f"[Retriever] Ditemukan {total_urls} URL untuk diproses.\n")

        for index, url in enumerate(urls, 1):
            print(f"[{index}/{total_urls}] Processing: {url}")
            
            snapshot_url = None
            timestamp = None
            cleaned_text = ""
            
            # Step 1: Check Availability
            try:
                print(f"  -> Cek ketersediaan...", end=" ", flush=True)
                api_url = f"https://archive.org/wayback/available?url={url}"
                response = requests.get(api_url, timeout=10)
                data = response.json()
                
                if "archived_snapshots" in data and "closest" in data["archived_snapshots"]:
                    closest = data["archived_snapshots"]["closest"]
                    snapshot_url = closest["url"]
                    timestamp = closest["timestamp"]
                    print(f"FOUND ({timestamp})")
                else:
                    print("NOT FOUND")
            except Exception as e:
                print(f"ERROR API: {e}")

            # Step 2 & 3: Retrieve and Clean
            if snapshot_url:
                try:
                    print(f"  -> Mengambil konten...", end=" ", flush=True)
                    content_response = requests.get(snapshot_url, timeout=20)
                    
                    if content_response.status_code == 200:
                        soup = BeautifulSoup(content_response.text, "lxml")
                        
                        # Remove unwanted tags
                        for tag in soup(["script", "style", "nav", "footer", "header", "iframe"]):
                            tag.decompose()
                            
                        # Extract text
                        cleaned_text = soup.get_text(separator=' ', strip=True)
                        print("OK")
                    else:
                        print(f"FAILED (Status {content_response.status_code})")
                except Exception as e:
                    print(f"ERROR download/parse: {e}")

            if snapshot_url:
                results.append({
                    "original_url": url,
                    "archive_timestamp": timestamp,
                    "cleaned_text": cleaned_text
                })
            
            time.sleep(3)

        print(f"\n[Retriever] Menyimpan {len(results)} data ke {self.output_file}...")
        try:
            with open(self.output_file, "w", encoding="utf-8") as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            print("[Retriever] Selesai.")
            return True
        except Exception as e:
            print(f"[Retriever] Gagal menyimpan output: {e}")
            return False
