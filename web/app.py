from flask import Flask, render_template, request, jsonify
import psycopg2
import os

app = Flask(__name__)

def get_db_connection():
    dsn = os.environ.get("DATABASE_URL")
    if not dsn: return None
    try:
        return psycopg2.connect(dsn)
    except Exception as e:
        print(f"DB Error: {e}")
        return None

def init_db():
    """Initializes the database using schema.sql"""
    conn = get_db_connection()
    if conn:
        try:
            with app.open_resource('../db/schema.sql', mode='r') as f:
                schema_sql = f.read()
            
            cur = conn.cursor()
            cur.execute(schema_sql)
            conn.commit()
            cur.close()
            conn.close()
            print("Database initialized successfully.")
        except Exception as e:
            print(f"DB Init Error: {e}")

# Attempt to initialize DB on startup if URL is present (Cloud environment)
if os.environ.get("DATABASE_URL"):
    with app.app_context():
        init_db()

@app.route('/')
def index():
    return render_template('index.html', query="", results=[])

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/search')
def search():
    query = request.args.get('q', '')
    results = []
    
    if query:
        conn = get_db_connection()
        if conn:
            try:
                cur = conn.cursor()
                # Full Text Search with Category
                sql = """
                    SELECT original_url, 
                           ts_headline('indonesian', cleaned_text, plainto_tsquery('indonesian', %s)) as snippet,
                           archive_timestamp,
                           category
                    FROM archived_documents
                    WHERE to_tsvector('indonesian', cleaned_text) @@ plainto_tsquery('indonesian', %s)
                    ORDER BY ts_rank(to_tsvector('indonesian', cleaned_text), plainto_tsquery('indonesian', %s)) DESC
                    LIMIT 20;
                """
                cur.execute(sql, (query, query, query))
                rows = cur.fetchall()
                for row in rows:
                    results.append({
                        "original_url": row[0],
                        "snippet": row[1],
                        "archive_timestamp": row[2],
                        "category": row[3] if len(row) > 3 else "General"
                    })
                cur.close()
                conn.close()
            except Exception as e:
                print(f"Search Error: {e}")

    return render_template('search_results.html', query=query, results=results)

@app.route('/suggest')
def suggest():
    q = request.args.get('q', '')
    if not q or len(q) < 2:
        return jsonify([])

    suggestions = []
    conn = get_db_connection()
    if conn:
        try:
            cur = conn.cursor()
            # Gunakan ts_stat untuk mencari kata-kata yang paling sering muncul
            # yang diawali dengan huruf yang diketik user (prefix match)
            sql = """
                SELECT word 
                FROM ts_stat('SELECT to_tsvector(''indonesian'', cleaned_text) FROM archived_documents') 
                WHERE word ILIKE %s 
                ORDER BY nentry DESC 
                LIMIT 5;
            """
            cur.execute(sql, (q + '%',))
            rows = cur.fetchall()
            suggestions = [row[0] for row in rows]
            cur.close()
            conn.close()
        except Exception as e:
            print(f"Suggestion Error: {e}")
            
    return jsonify(suggestions)

@app.route('/submit-url', methods=['POST'])
def submit_url():
    """API endpoint for receiving dead URL submissions from extension or community"""
    try:
        data = request.get_json()
        url = data.get('url', '').strip()
        source = data.get('source', 'unknown')  # 'extension' or 'community'
        
        if not url:
            return jsonify({"success": False, "message": "URL is required"}), 400
        
        # Append to seed_list.txt
        import os
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        seed_file = os.path.join(base_dir, 'data', 'seed_list.txt')
        
        # Check if URL already exists
        existing_urls = []
        if os.path.exists(seed_file):
            with open(seed_file, 'r', encoding='utf-8') as f:
                existing_urls = [line.strip() for line in f if line.strip()]
        
        if url not in existing_urls:
            with open(seed_file, 'a', encoding='utf-8') as f:
                f.write(url + '\n')
            print(f"[Submit] New URL added from {source}: {url}")
            return jsonify({"success": True, "message": "URL submitted successfully"})
        else:
            return jsonify({"success": True, "message": "URL already in queue"})
            
    except Exception as e:
        print(f"[Submit] Error: {e}")
        return jsonify({"success": False, "message": "Server error"}), 500

@app.route('/download-extension')
def download_extension():
    """Serve the browser extension for download"""
    try:
        from flask import send_file
        import os
        import zipfile
        import tempfile
        
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        extension_dir = os.path.join(base_dir, 'extension')
        
        # Create a temporary ZIP file
        temp_zip = tempfile.NamedTemporaryFile(delete=False, suffix='.zip')
        
        with zipfile.ZipFile(temp_zip.name, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(extension_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, extension_dir)
                    zipf.write(file_path, arcname)
        
        return send_file(
            temp_zip.name,
            as_attachment=True,
            download_name='nexus-ignis-extension.zip',
            mimetype='application/zip'
        )
    except Exception as e:
        print(f"[Download] Error: {e}")
        return "Extension not found", 404

if __name__ == '__main__':
    app.run(debug=True, port=5000)
