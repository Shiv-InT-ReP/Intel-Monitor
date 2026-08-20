"""
SQLite-backed dedup store for the intel monitor.
Every item we've ever seen (across all sources) gets a row here so we
never notify on the same story twice, even across separate runs.
"""
import sqlite3
from contextlib import contextmanager
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
    notified INTEGER NOT NULL DEFAULT 0
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


def is_seen(item_id: str) -> bool:
    with get_conn() as conn:
        row = conn.execute(
            "SELECT 1 FROM seen_items WHERE item_id = ?", (item_id,)
        ).fetchone()
        return row is not None


def mark_seen(item: dict, notified: bool):
    from datetime import datetime, timezone

    keywords = item.get("matched_keywords", [])
    if isinstance(keywords, list):
        keywords = ",".join(keywords)

    with get_conn() as conn:
        conn.execute(
            """
            INSERT OR IGNORE INTO seen_items
                (item_id, source, title, url, published_at, matched_keywords, first_seen_at, notified)
            VALUES (:item_id, :source, :title, :url, :published_at, :matched_keywords, :first_seen_at, :notified)
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
            },
        )
