# Search Quality Integration

This document explains the new search-quality foundation added to Nexus Ignis.

## Database Changes

Run migrations in order:

```bash
psql "$DATABASE_URL" -f db/migrations/001_pipeline_queue.sql
psql "$DATABASE_URL" -f db/migrations/002_search_quality.sql
```

## Added Search Fields

`archived_documents` now supports:

- `title`
- `domain`
- `snapshot_url`
- `archive_year`
- `content_hash`
- `word_count`
- `last_indexed_at`

These fields allow search results to become more useful than body-text-only search.

## Weighted Ranking

The new search index weights fields like this:

| Field | Weight | Purpose |
|---|---:|---|
| `title` | A | strongest signal |
| `domain` | B | medium relevance signal |
| `cleaned_text` | D | body/content fallback |

## Query Parser

The new service uses PostgreSQL `websearch_to_tsquery`, which supports user-friendly search syntax such as:

```text
"exact phrase" tutorial -spam
```

## Filters

The new `web/search_service.py` module supports:

- `category`
- `domain`
- `year`
- `page`
- `page_size`

## Flask Route Integration Example

Replace the current search route internals with a call to `search_service`:

```python
from web.search_service import normalize_search_params, search_archives

@app.route('/search')
def search():
    query = request.args.get('q', '')
    params = normalize_search_params(
        query=query,
        category=request.args.get('category'),
        domain=request.args.get('domain'),
        year=request.args.get('year'),
        page=request.args.get('page', 1),
        page_size=request.args.get('page_size', 20),
    )

    payload = {
        'query': params.query,
        'results': [],
        'page': params.page,
        'page_size': params.page_size,
        'total': 0,
        'has_next': False,
        'has_prev': params.page > 1,
        'filters': {
            'category': params.category,
            'domain': params.domain,
            'year': params.year,
        },
    }

    if params.query:
        conn = get_db_connection()
        if conn:
            try:
                payload = search_archives(conn, params)
            finally:
                conn.close()

    return render_template(
        'index.html',
        query=payload['query'],
        results=payload['results'],
        search=payload,
    )
```

## Template Notes

For each result, prefer:

```jinja2
<a href="{{ result.snapshot_url or result.original_url }}" target="_blank" rel="noopener noreferrer">
    {{ result.title or result.original_url }}
</a>
```

Show metadata:

```jinja2
{{ result.domain }} · {{ result.category }} · {{ result.archive_year }}
```

For snippets, avoid rendering arbitrary archived HTML. If `snippet` contains only the server-generated `<mark>` tags from `ts_headline`, sanitize before marking it safe or render without `|safe` until a sanitizer is added.

## Next Step

After this PR, the next implementation step is to refactor `web/app.py` to use `web/search_service.py` directly and update the template to show title/domain/snapshot URL plus pagination controls.
