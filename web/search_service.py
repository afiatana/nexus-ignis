"""Search service for Nexus Ignis.

This module centralizes search behavior so Flask routes stay thin and the
ranking logic can be tested independently.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import psycopg2
from psycopg2.extras import RealDictCursor


DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 50


@dataclass(frozen=True)
class SearchParams:
    query: str
    category: str | None = None
    domain: str | None = None
    year: int | None = None
    page: int = 1
    page_size: int = DEFAULT_PAGE_SIZE

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size


def normalize_search_params(
    query: str,
    category: str | None = None,
    domain: str | None = None,
    year: str | int | None = None,
    page: str | int | None = 1,
    page_size: str | int | None = DEFAULT_PAGE_SIZE,
) -> SearchParams:
    """Normalize user-provided search params.

    This keeps route code small and prevents invalid pagination/filter values
    from reaching SQL.
    """

    clean_query = (query or "").strip()
    clean_category = (category or "").strip() or None
    clean_domain = (domain or "").strip().lower() or None

    parsed_year: int | None = None
    if year not in (None, ""):
        try:
            parsed_year = int(year)
            if parsed_year < 1990 or parsed_year > 2100:
                parsed_year = None
        except (TypeError, ValueError):
            parsed_year = None

    try:
        parsed_page = max(1, int(page or 1))
    except (TypeError, ValueError):
        parsed_page = 1

    try:
        parsed_page_size = int(page_size or DEFAULT_PAGE_SIZE)
    except (TypeError, ValueError):
        parsed_page_size = DEFAULT_PAGE_SIZE

    parsed_page_size = min(MAX_PAGE_SIZE, max(1, parsed_page_size))

    return SearchParams(
        query=clean_query,
        category=clean_category,
        domain=clean_domain,
        year=parsed_year,
        page=parsed_page,
        page_size=parsed_page_size,
    )


def search_archives(conn: psycopg2.extensions.connection, params: SearchParams) -> dict[str, Any]:
    """Run weighted archive search with filters and pagination.

    Ranking weights:
    - title: A, strongest
    - domain: B, medium
    - cleaned_text/body: D, lowest

    PostgreSQL `websearch_to_tsquery` supports user-friendly syntax such as
    quoted phrases and minus terms while still using full-text indexes.
    """

    if not params.query:
        return {
            "query": params.query,
            "results": [],
            "page": params.page,
            "page_size": params.page_size,
            "total": 0,
            "has_next": False,
            "has_prev": params.page > 1,
            "filters": {
                "category": params.category,
                "domain": params.domain,
                "year": params.year,
            },
        }

    where_clauses = [
        "search_vector @@ websearch_to_tsquery('indonesian', %(query)s)"
    ]
    sql_params: dict[str, Any] = {
        "query": params.query,
        "limit": params.page_size,
        "offset": params.offset,
    }

    if params.category:
        where_clauses.append("category = %(category)s")
        sql_params["category"] = params.category

    if params.domain:
        where_clauses.append("domain = %(domain)s")
        sql_params["domain"] = params.domain

    if params.year:
        where_clauses.append("archive_year = %(year)s")
        sql_params["year"] = params.year

    where_sql = " AND ".join(where_clauses)

    sql = f"""
        WITH ranked AS (
            SELECT
                id,
                original_url,
                snapshot_url,
                title,
                domain,
                archive_year,
                category,
                archive_timestamp,
                ts_rank_cd(search_vector, websearch_to_tsquery('indonesian', %(query)s)) AS rank,
                ts_headline(
                    'indonesian',
                    coalesce(cleaned_text, ''),
                    websearch_to_tsquery('indonesian', %(query)s),
                    'StartSel=<mark>, StopSel=</mark>, MaxWords=35, MinWords=12, ShortWord=3, HighlightAll=false'
                ) AS snippet
            FROM (
                SELECT
                    *,
                    (
                        setweight(to_tsvector('indonesian', coalesce(title, '')), 'A') ||
                        setweight(to_tsvector('simple', coalesce(domain, '')), 'B') ||
                        setweight(to_tsvector('indonesian', coalesce(cleaned_text, '')), 'D')
                    ) AS search_vector
                FROM archived_documents
            ) docs
            WHERE {where_sql}
        ), counted AS (
            SELECT count(*) AS total FROM ranked
        )
        SELECT ranked.*, counted.total
        FROM ranked, counted
        ORDER BY ranked.rank DESC, ranked.archive_timestamp DESC NULLS LAST, ranked.id DESC
        LIMIT %(limit)s OFFSET %(offset)s;
    """

    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(sql, sql_params)
        rows = [dict(row) for row in cur.fetchall()]

    total = rows[0]["total"] if rows else 0
    for row in rows:
        row.pop("total", None)

    return {
        "query": params.query,
        "results": rows,
        "page": params.page,
        "page_size": params.page_size,
        "total": total,
        "has_next": params.offset + len(rows) < total,
        "has_prev": params.page > 1,
        "filters": {
            "category": params.category,
            "domain": params.domain,
            "year": params.year,
        },
    }
