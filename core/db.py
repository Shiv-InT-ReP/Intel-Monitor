"""
SQLite-backed dedup store for the intel monitor.
Every item we've ever seen (across all sources) gets a row here so we
never notify on the same story twice, even across separate runs.
Also serves as the data source for the dashboard.
"""
import sqlite3
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
    region TEXT DEFAULT NULL       -- primary matched region, for map plotting
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
              severity_tier: str = "low", severity_score: int = 0, region: str = None):
    keywords = item.get("matched_keywords", [])
    if isinstance(keywords, list):
        keywords = ",".join(keywords)

    with get_conn() as conn:
        conn.execute(
            """
            INSERT OR IGNORE INTO seen_items
                (item_id, source, title, url, published_at, matched_keywords, first_seen_at,
                 notified, category, severity_tier, severity_score, region)
            VALUES (:item_id, :source, :title, :url, :published_at, :matched_keywords, :first_seen_at,
                    :notified, :category, :severity_tier, :severity_score, :region)
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
            },
        )


def get_dashboard_data() -> list[dict]:
    """All notified (matched) items, newest first, for dashboard rendering."""
    with get_conn() as conn:
        rows = conn.execute(
            """
            SELECT source, title, url, published_at, matched_keywords, first_seen_at,
                   category, severity_tier, severity_score, region
            FROM seen_items
            WHERE notified = 1
            ORDER BY first_seen_at DESC
            """
        ).fetchall()
        return [dict(row) for row in rows]


def get_items_needing_backfill() -> list[dict]:
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
