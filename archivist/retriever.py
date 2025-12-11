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
            
            # Step 1: Check Availability (Get multiple snapshots via CDX)
            try:
                print(f"  -> Cukup ketersediaan (CDX)...", end=" ", flush=True)
                # Get up to 3 snapshots, collapsed by year (one per year)
                cdx_url = f"http://web.archive.org/cdx/search/cdx?url={url}&output=json&limit=3&collapse=timestamp:4&filter=statuscode:200"
                response = requests.get(cdx_url, timeout=15)
                
                snapshots_found = []
                if response.status_code == 200:
                    data = response.json()
                    # format: [['urlkey', 'timestamp', 'original', 'mimetype', 'statuscode', 'digest', 'length'], ...]
                    if len(data) > 1: # data[0] is header
                        for row in data[1:]:
                            ts = row[1]
                            # Construct Wayback URL
                            snap_url = f"https://web.archive.org/web/{ts}/{url}"
                            snapshots_found.append((ts, snap_url))
                        
                        print(f"FOUND {len(snapshots_found)} snapshots")
                    else:
                        print("NOT FOUND")
                else:
                    # Fallback to simple available API
                    print("CDX Fail, fallback...", end=" ")
                    api_url = f"https://archive.org/wayback/available?url={url}"
                    resp = requests.get(api_url, timeout=10)
                    d = resp.json()
                    if "archived_snapshots" in d and "closest" in d["archived_snapshots"]:
                         closest = d["archived_snapshots"]["closest"]
                         snapshots_found.append((closest["timestamp"], closest["url"]))
                         print("FOUND (fallback)")
                    else:
                         print("NOT FOUND")

            except Exception as e:
                print(f"ERROR API: {e}")
                snapshots_found = []

            # Step 2 & 3: Retrieve and Clean (Loop through snapshots)
            for ts, snap_url in snapshots_found:
                if not snap_url: continue
                
                # Check for existing logic? No, let's just process.
                # Skip variable defining since we loop now
                pass 


            # Step 2 & 3: Retrieve and Clean
            for ts, snap_url in snapshots_found:
                cleaned_text = ""
                try:
                    print(f"    -> [{ts}] Mengambil konten...", end=" ", flush=True)
                    content_response = requests.get(snap_url, timeout=20)
                    
                    if content_response.status_code == 200:
                        soup = BeautifulSoup(content_response.text, "html.parser")
                        
                        # Remove unwanted tags
                        for tag in soup(["script", "style", "nav", "footer", "header", "iframe"]):
                            tag.decompose()
                            
                        # Extract text
                        cleaned_text = soup.get_text(separator=' ', strip=True)
                        print("OK")
                        
                        results.append({
                            "original_url": url,
                            "archive_timestamp": ts,
                            "cleaned_text": cleaned_text
                        })
                    else:
                        print(f"FAILED (Status {content_response.status_code})")
                except Exception as e:
                    print(f"ERROR: {e}")
            
            time.sleep(2) # Connection cooldown

        print(f"\n[Retriever] Menyimpan {len(results)} data ke {self.output_file}...")
        try:
            with open(self.output_file, "w", encoding="utf-8") as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            print("[Retriever] Selesai.")
            return True
        except Exception as e:
            print(f"[Retriever] Gagal menyimpan output: {e}")
            return False
