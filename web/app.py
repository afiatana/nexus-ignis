from flask import Flask, render_template, request
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

if __name__ == '__main__':
    app.run(debug=True, port=5000)
