"""
SQLite-backed dedup store for the intel monitor.
Every item we've ever seen (across all sources) gets a row here so we
never notify on the same story twice, even across separate runs.
Also serves as the data source for the dashboard.
"""
import sqlite3
import json
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "intel_monitor.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS seen_items (
    item_id TEXT PRIMARY KEY,      -- stable hash of source+url (or source+id)
    source TEXT NOT NULL,          -- e.g. 'rss:Reuters World', 'reddit:geopolitics'
    title TEXT,
    url TEXT,
    published_at TEXT,             -- ISO8601 string, may be null if unknown
    matched_keywords TEXT,         -- comma-separated
    first_seen_at TEXT NOT NULL,   -- ISO8601, when WE first saw it
    notified INTEGER NOT NULL DEFAULT 0,
    category TEXT DEFAULT 'geopolitical',  -- 'geopolitical' or 'travel'
    severity_tier TEXT DEFAULT 'low',      -- 'low' / 'moderate' / 'high' / 'critical'
    severity_score INTEGER DEFAULT 0,
    region TEXT DEFAULT NULL,      -- primary matched region, for map plotting
    city_name TEXT DEFAULT NULL,   -- specific city/place if extracted, for precise map plotting
    city_lat REAL DEFAULT NULL,
    city_lon REAL DEFAULT NULL,
    domain TEXT DEFAULT 'conflict',  -- 'conflict' or 'disaster', for map marker shape
    confidence_tier TEXT DEFAULT 'unverified',    -- 'unverified' / 'single-source' / 'corroborated'
    confidence_trusted_count INTEGER DEFAULT 0,   -- count of DISTINCT trusted (RSS/ACLED) outlets confirming this
    confidence_links TEXT DEFAULT NULL,           -- JSON list of {source, url} for trusted corroborating outlets
    archived INTEGER DEFAULT 0,    -- manually marked resolved by the user; excluded from default views
    event_tags TEXT DEFAULT NULL   -- comma-separated multi-tags: security, protest, disaster, sloc, iran_war, russia_ukraine_war, defence
);
CREATE INDEX IF NOT EXISTS idx_seen_items_source ON seen_items(source);
"""


@contextmanager
def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db():
    with get_conn() as conn:
        conn.executescript(SCHEMA)
        # Migrations for databases created before these columns existed.
        for column, coltype_default in [
            ("category", "TEXT DEFAULT 'geopolitical'"),
            ("severity_tier", "TEXT DEFAULT 'low'"),
            ("severity_score", "INTEGER DEFAULT 0"),
            ("region", "TEXT DEFAULT NULL"),
            ("city_name", "TEXT DEFAULT NULL"),
            ("city_lat", "REAL DEFAULT NULL"),
            ("city_lon", "REAL DEFAULT NULL"),
            ("domain", "TEXT DEFAULT 'conflict'"),
            ("confidence_tier", "TEXT DEFAULT 'unverified'"),
            ("confidence_trusted_count", "INTEGER DEFAULT 0"),
            ("confidence_links", "TEXT DEFAULT NULL"),
            ("archived", "INTEGER DEFAULT 0"),
            ("event_tags", "TEXT DEFAULT NULL"),
        ]:
            try:
                conn.execute(f"ALTER TABLE seen_items ADD COLUMN {column} {coltype_default}")
            except sqlite3.OperationalError:
                pass  # column already exists


def is_seen(item_id: str) -> bool:
    with get_conn() as conn:
        row = conn.execute(
            "SELECT 1 FROM seen_items WHERE item_id = ?", (item_id,)
        ).fetchone()
        return row is not None


def mark_seen(item: dict, notified: bool, category: str = "geopolitical",
              severity_tier: str = "low", severity_score: int = 0, region: str = None,
              city_name: str = None, city_lat: float = None, city_lon: float = None,
              domain: str = "conflict", event_tags: list = None):
    keywords = item.get("matched_keywords", [])
    if isinstance(keywords, list):
        keywords = ",".join(keywords)

    event_tags_str = ",".join(event_tags) if event_tags else None

    with get_conn() as conn:
        conn.execute(
            """
            INSERT OR IGNORE INTO seen_items
                (item_id, source, title, url, published_at, matched_keywords, first_seen_at,
                 notified, category, severity_tier, severity_score, region, city_name, city_lat, city_lon, domain, event_tags)
            VALUES (:item_id, :source, :title, :url, :published_at, :matched_keywords, :first_seen_at,
                    :notified, :category, :severity_tier, :severity_score, :region, :city_name, :city_lat, :city_lon, :domain, :event_tags)
            """,
            {
                "item_id": item["item_id"],
                "source": item["source"],
                "title": item.get("title"),
                "url": item.get("url"),
                "published_at": item.get("published_at"),
                "matched_keywords": keywords,
                "first_seen_at": item.get("fetched_at") or datetime.now(timezone.utc).isoformat(),
                "notified": int(notified),
                "category": category,
                "severity_tier": severity_tier,
                "severity_score": severity_score,
                "region": region,
                "city_name": city_name,
                "city_lat": city_lat,
                "city_lon": city_lon,
                "domain": domain,
                "event_tags": event_tags_str,
            },
        )


def get_dashboard_data(include_archived: bool = False) -> list[dict]:
    """All notified (matched) items, newest first, for dashboard rendering.

    Archived items (manually marked resolved) are excluded by default --
    they're never deleted, just kept out of the default view. Pass
    include_archived=True to get everything, e.g. for an "Archived" filter.
    """
    with get_conn() as conn:
        query = """
            SELECT item_id, source, title, url, published_at, matched_keywords, first_seen_at,
                   category, severity_tier, severity_score, region,
                   confidence_tier, confidence_trusted_count, confidence_links,
                   city_name, city_lat, city_lon, domain, archived, event_tags
            FROM seen_items
            WHERE notified = 1
        """
        if not include_archived:
            query += " AND archived = 0"
        query += " ORDER BY first_seen_at DESC"

        rows = conn.execute(query).fetchall()
        items = [dict(row) for row in rows]
        for item in items:
            item["confidence_links"] = json.loads(item["confidence_links"]) if item.get("confidence_links") else []
            item["event_tags"] = item["event_tags"].split(",") if item.get("event_tags") else []
        return items


def archive_item(item_id: str) -> bool:
    """Manually marks a single item as resolved/archived. Never deletes -- reversible."""
    with get_conn() as conn:
        cursor = conn.execute("UPDATE seen_items SET archived = 1 WHERE item_id = ?", (item_id,))
        return cursor.rowcount > 0


def unarchive_item(item_id: str) -> bool:
    """Reverses an archive action."""
    with get_conn() as conn:
        cursor = conn.execute("UPDATE seen_items SET archived = 0 WHERE item_id = ?", (item_id,))
        return cursor.rowcount > 0


def search_items_for_archiving(search_term: str, limit: int = 20) -> list[dict]:
    """Title search to help find items to archive, used by the archive CLI tool."""
    with get_conn() as conn:
        rows = conn.execute(
            """
            SELECT item_id, title, source, region, severity_tier, first_seen_at, archived
            FROM seen_items
            WHERE notified = 1 AND title LIKE ?
            ORDER BY first_seen_at DESC
            LIMIT ?
            """,
            (f"%{search_term}%", limit),
        ).fetchall()
        return [dict(row) for row in rows]


def get_recent_items_for_confidence_scoring(days: int = 5) -> list[dict]:
    """
    Notified items from the last N days, used for cross-source corroboration
    scoring. Scoped to a recent window rather than all history -- confidence
    scoring is only meaningful for events that could still gain corroborating
    reports, and this keeps the O(n^2) clustering comparison fast even as
    your total history grows into the thousands.
    """
    from datetime import datetime, timezone, timedelta
    cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
    with get_conn() as conn:
        rows = conn.execute(
            """
            SELECT item_id, source, title, url, matched_keywords, first_seen_at, region
            FROM seen_items
            WHERE notified = 1 AND first_seen_at >= ?
            """,
            (cutoff,),
        ).fetchall()
        return [dict(row) for row in rows]


def update_confidence_bulk(scores: dict[str, dict]):
    """scores: {item_id: {"tier": str, "trusted_count": int, "corroborating_links": [...]}}"""
    with get_conn() as conn:
        conn.executemany(
            "UPDATE seen_items SET confidence_trusted_count = ?, confidence_tier = ?, confidence_links = ? WHERE item_id = ?",
            [
                (v["trusted_count"], v["tier"], json.dumps(v["corroborating_links"]), item_id)
                for item_id, v in scores.items()
            ],
        )


def get_items_needing_verification(limit: int = 10, hours: int = 48) -> list[dict]:
    """
    Finds recent, high-severity items that are still 'unverified' -- good
    candidates for targeted GDELT verification. Capped at `limit` to keep
    the number of GDELT queries per run small and reliable.
    """
    from datetime import datetime, timezone, timedelta
    cutoff = (datetime.now(timezone.utc) - timedelta(hours=hours)).isoformat()
    with get_conn() as conn:
        rows = conn.execute(
            """
            SELECT item_id, source, region, matched_keywords, confidence_links
            FROM seen_items
            WHERE notified = 1 AND confidence_tier = 'unverified'
              AND severity_tier IN ('high', 'critical')
              AND region IS NOT NULL
              AND first_seen_at >= ?
            ORDER BY first_seen_at DESC
            LIMIT ?
            """,
            (cutoff, limit),
        ).fetchall()
        return [dict(row) for row in rows]


def apply_gdelt_verification(item_id: str, new_sources: list[dict], own_source: str):
    """
    Updates a single item's confidence based on new corroborating sources
    found via targeted GDELT verification. Combines with any existing
    corroboration links rather than overwriting.
    """
    with get_conn() as conn:
        row = conn.execute(
            "SELECT confidence_links FROM seen_items WHERE item_id = ?", (item_id,)
        ).fetchone()
        existing_links = json.loads(row["confidence_links"]) if row and row["confidence_links"] else []

        all_links = existing_links + new_sources
        seen_sources = set()
        deduped_links = []
        for link in all_links:
            if link["source"] not in seen_sources:
                seen_sources.add(link["source"])
                deduped_links.append(link)

        trusted_count = len(seen_sources)
        if own_source.startswith(("rss:", "acled", "gdelt:")) and own_source not in seen_sources:
            trusted_count += 1

        tier = "corroborated" if trusted_count >= 2 else "single-source" if trusted_count == 1 else "unverified"

        conn.execute(
            "UPDATE seen_items SET confidence_tier = ?, confidence_trusted_count = ?, confidence_links = ? WHERE item_id = ?",
            (tier, trusted_count, json.dumps(deduped_links), item_id),
        )
        return tier, trusted_count


def get_prior_related_count(region: str, keywords: list[str], days: int = 5) -> int:
    """
    Counts how many items in recent history relate to this region and share
    at least one keyword -- used for AI dedup's delta-awareness (is this a
    brand-new development or a continuation of an ongoing situation).
    """
    if not region:
        return 0
    from datetime import datetime, timezone, timedelta
    cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT matched_keywords FROM seen_items WHERE notified = 1 AND region = ? AND first_seen_at >= ?",
            (region, cutoff),
        ).fetchall()
    keyword_set = set(keywords)
    count = 0
    for row in rows:
        stored_kws = set((row["matched_keywords"] or "").split(","))
        if stored_kws & keyword_set:
            count += 1
    return count
    """Notified items where region is still NULL -- i.e. matched before
    severity/region tracking existed. Used by the one-time backfill script."""
    with get_conn() as conn:
        rows = conn.execute(
            """
            SELECT item_id, title, category, matched_keywords
            FROM seen_items
            WHERE notified = 1 AND region IS NULL
            """
        ).fetchall()
        return [dict(row) for row in rows]


def update_severity_region(item_id: str, region: str, severity_tier: str, severity_score: int):
    with get_conn() as conn:
        conn.execute(
            "UPDATE seen_items SET region = ?, severity_tier = ?, severity_score = ? WHERE item_id = ?",
            (region, severity_tier, severity_score, item_id),
        )
