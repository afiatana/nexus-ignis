from flask import Flask, render_template, request, jsonify, send_file
import psycopg2
import os
import zipfile
import tempfile

from web.search_service import normalize_search_params, search_archives, empty_search_response
from web.abuse_protection import InMemoryRateLimiter, get_rate_limit_key, validate_public_url

app = Flask(__name__)
submit_rate_limiter = InMemoryRateLimiter()

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
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            schema_paths = [
                os.path.join(base_dir, 'db', 'schema.sql'),
                os.path.join(os.path.dirname(__file__), '..', 'db', 'schema.sql'),
                '/app/db/schema.sql',
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
    params = normalize_search_params(
        query=request.args.get('q', ''),
        category=request.args.get('category'),
        domain=request.args.get('domain'),
        year=request.args.get('year'),
        page=request.args.get('page', 1),
        page_size=request.args.get('page_size', 20),
    )
    search_payload = empty_search_response(params)

    if params.query:
        conn = get_db_connection()
        if conn:
            try:
                search_payload = search_archives(conn, params)
            except Exception as e:
                print(f"Search Error: {e}")
            finally:
                conn.close()

    return render_template(
        'search_results.html',
        query=search_payload['query'],
        results=search_payload['results'],
        search=search_payload,
    )

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
            cur.execute("""
                SELECT url, status 
                FROM reported_urls 
                WHERE status IN ('PENDING', 'CONFIRMED_DEAD') 
                ORDER BY 
                    CASE WHEN status = 'CONFIRMED_DEAD' THEN 1 ELSE 2 END, 
                    created_at DESC 
                LIMIT 20;
            """)
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
    rate_key = get_rate_limit_key(request.remote_addr, request.headers.get('X-Forwarded-For'))
    if not submit_rate_limiter.is_allowed(rate_key):
        return jsonify({"success": False, "message": "Too many submissions. Please try again later."}), 429

    try:
        data = request.get_json(silent=True) or {}
        raw_url = data.get('url', '').strip()
        source = (data.get('source', 'unknown') or 'unknown').strip()[:50]

        validation = validate_public_url(raw_url)
        if not validation.is_valid:
            return jsonify({"success": False, "message": validation.error}), 400

        url = validation.normalized_url
        conn = get_db_connection()
        if not conn:
            return jsonify({"success": False, "message": "Database error"}), 500

        try:
            cur = conn.cursor()
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
        temp_zip = tempfile.NamedTemporaryFile(delete=False, suffix='.zip')
        
        with zipfile.ZipFile(temp_zip.name, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(extension_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, extension_dir)
                    
                    if file == 'config.js':
                        base_url = request.url_root.rstrip('/')
                        api_url = f"{base_url}/submit-url"
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
