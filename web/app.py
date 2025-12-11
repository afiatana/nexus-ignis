from flask import Flask, render_template, request, jsonify, send_file
import psycopg2
import os
import zipfile
import tempfile

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
            # Try multiple possible paths for schema.sql
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            schema_paths = [
                os.path.join(base_dir, 'db', 'schema.sql'),  # Local/Railway
                os.path.join(os.path.dirname(__file__), '..', 'db', 'schema.sql'),  # Relative
                '/app/db/schema.sql',  # Railway absolute path
            ]
            
            schema_sql = None
            for schema_path in schema_paths:
                if os.path.exists(schema_path):
                    with open(schema_path, 'r') as f:
                        schema_sql = f.read()
                    print(f"Found schema at: {schema_path}")
                    break
            
            if not schema_sql:
                print("Warning: schema.sql not found. Database may need manual initialization.")
                return
            
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
    # Read recent dead URLs from seed list
    import os
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    seed_file = os.path.join(base_dir, 'data', 'seed_list.txt')
    
    recent_urls = []
    try:
        if os.path.exists(seed_file):
            with open(seed_file, 'r', encoding='utf-8') as f:
                urls = [line.strip() for line in f if line.strip()]
                # Reverse to show newest first (last added = first shown)
                recent_urls = list(reversed(urls))[:20]  # Show max 20 recent URLs
    except Exception as e:
        print(f"Error reading seed list: {e}")
    
    return render_template('index.html', query="", results=[], recent_urls=recent_urls)

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

@app.route('/api/recent-urls')
def get_recent_urls():
    """API endpoint to get recent dead URLs for auto-refresh"""
    import os
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    seed_file = os.path.join(base_dir, 'data', 'seed_list.txt')
    
    recent_urls = []
    try:
        if os.path.exists(seed_file):
            with open(seed_file, 'r', encoding='utf-8') as f:
                urls = [line.strip() for line in f if line.strip()]
                recent_urls = list(reversed(urls))[:20]
    except Exception as e:
        print(f"Error reading seed list: {e}")
    
    return jsonify({"urls": recent_urls})

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
        data_dir = os.path.join(base_dir, 'data')
        seed_file = os.path.join(data_dir, 'seed_list.txt')
        
        # Ensure data directory exists
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
            print(f"[Submit] Created data directory: {data_dir}")
        
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
            print(f"[Submit] Duplicate URL from {source}: {url}")
            return jsonify({"success": True, "message": "URL already in queue"})
            
    except Exception as e:
        print(f"[Submit] Error: {e}")
        return jsonify({"success": False, "message": "Server error"}), 500

@app.route('/download-extension')
def download_extension():
    """Serve the browser extension for download"""
    try:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        extension_dir = os.path.join(base_dir, 'extension')
        
        # Create a temporary ZIP file
        temp_zip = tempfile.NamedTemporaryFile(delete=False, suffix='.zip')
        
        with zipfile.ZipFile(temp_zip.name, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(extension_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, extension_dir)
                    
                    # Dynamically update config.js with current server URL
                    if file == 'config.js':
                        # Get current base URL (e.g., https://my-app.railway.app/)
                        base_url = request.url_root.rstrip('/')
                        api_url = f"{base_url}/submit-url"
                        
                        # Create new config content
                        config_content = f"""
// Auto-generated config
const CONFIG = {{
    API_URL: '{api_url}'
}};

if (typeof module !== 'undefined' && module.exports) {{
    module.exports = CONFIG;
}}
"""
                        zipf.writestr(arcname, config_content)
                    else:
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
