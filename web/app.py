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
    recent_urls = []
    conn = get_db_connection()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute("SELECT url FROM reported_urls ORDER BY created_at DESC LIMIT 20;")
            rows = cur.fetchall()
            recent_urls = [row[0] for row in rows]
            cur.close()
            conn.close()
        except Exception as e:
            print(f"Error fetching recent urls: {e}")
            if conn: conn.close()
            
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
                # Multi-language Full Text Search (Indonesian + English)
                sql = """
                    SELECT original_url, 
                           ts_headline('indonesian', cleaned_text, plainto_tsquery('indonesian', %s)) as snippet_id,
                           ts_headline('english', cleaned_text, plainto_tsquery('english', %s)) as snippet_en,
                           archive_timestamp,
                           category
                    FROM archived_documents
                    WHERE 
                        to_tsvector('indonesian', cleaned_text) @@ plainto_tsquery('indonesian', %s)
                        OR
                        to_tsvector('english', cleaned_text) @@ plainto_tsquery('english', %s)
                    ORDER BY 
                        (ts_rank(to_tsvector('indonesian', cleaned_text), plainto_tsquery('indonesian', %s)) +
                         ts_rank(to_tsvector('english', cleaned_text), plainto_tsquery('english', %s))) DESC
                    LIMIT 20;
                """
                # Params: query, query, query, query, query, query
                cur.execute(sql, (query, query, query, query, query, query))
                
                rows = cur.fetchall()
                for row in rows:
                    # Choose the best snippet (if indonesian snippet is empty, use english)
                    snippet = row[1] if "<b>" in str(row[1]) else row[2]
                    
                    results.append({
                        "original_url": row[0],
                        "snippet": snippet,
                        "archive_timestamp": row[3],
                        "category": row[4] if len(row) > 4 else "General"
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
    """API endpoint to get recent reported URLs from DB"""
    recent_urls = []
    conn = get_db_connection()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute("SELECT url FROM reported_urls ORDER BY created_at DESC LIMIT 20;")
            rows = cur.fetchall()
            recent_urls = [row[0] for row in rows]
            cur.close()
            conn.close()
        except Exception as e:
            print(f"Error fetching recent urls: {e}")
            if conn: conn.close()
    
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
        
        conn = get_db_connection()
        if not conn:
            return jsonify({"success": False, "message": "Database error"}), 500

        try:
            cur = conn.cursor()
            # Try insert, ignore if duplicate
            cur.execute("""
                INSERT INTO reported_urls (url, source, status) 
                VALUES (%s, %s, 'PENDING')
                ON CONFLICT (url) DO NOTHING;
            """, (url, source))
            
            rows_affected = cur.rowcount
            conn.commit()
            cur.close()
            conn.close()
            
            if rows_affected > 0:
                print(f"[Submit] New URL added from {source}: {url}")
                return jsonify({"success": True, "message": "URL submitted successfully"})
            else:
                print(f"[Submit] Duplicate URL from {source}: {url}")
                return jsonify({"success": True, "message": "URL already in queue"})
                
        except Exception as e:
            print(f"[Submit] DB Error: {e}")
            if conn: conn.close()
            return jsonify({"success": False, "message": "Server error"}), 500
            
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
