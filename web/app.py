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

@app.route('/search')
def search():
    query = request.args.get('q', '')
    results = []
    
    if query:
        conn = get_db_connection()
        if conn:
            try:
                cur = conn.cursor()
                # Full Text Search
                sql = """
                    SELECT original_url, 
                           ts_headline('indonesian', cleaned_text, plainto_tsquery('indonesian', %s)) as snippet,
                           archive_timestamp
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
                        "archive_timestamp": row[2]
                    })
                cur.close()
                conn.close()
            except Exception as e:
                print(f"Search Error: {e}")

    return render_template('index.html', query=query, results=results)

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

if __name__ == '__main__':
    app.run(debug=True, port=5000)
