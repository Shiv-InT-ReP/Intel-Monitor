"""
RSS/Atom feed collector. No API keys needed.
Works for Reuters, Al Jazeera, government advisory feeds, think-tank
feeds (CFR, Crisis Group, etc.), and most news outlets that publish RSS.
"""
import hashlib
from datetime import datetime, timezone

import feedparser


def _make_item_id(source: str, url: str) -> str:
    return hashlib.sha256(f"{source}|{url}".encode()).hexdigest()


def _entry_published(entry) -> str | None:
    for field in ("published", "updated"):
        if hasattr(entry, field):
            return getattr(entry, field)
    return None


def collect(feed_configs: list[dict]) -> list[dict]:
    """
    feed_configs: [{"name": "Reuters World", "url": "https://..."}, ...]
    Returns a list of normalized item dicts.
    """
    items = []
    for feed in feed_configs:
        source_label = f"rss:{feed['name']}"
        try:
            parsed = feedparser.parse(feed["url"])
        except Exception as e:
            print(f"  [!] Failed to fetch {feed['name']}: {e}")
            continue

        if parsed.bozo and not parsed.entries:
            print(f"  [!] Feed error for {feed['name']}: {parsed.bozo_exception}")
            continue

        for entry in parsed.entries:
            url = getattr(entry, "link", None)
            title = getattr(entry, "title", "")
            summary = getattr(entry, "summary", "")
            if not url:
                continue
            items.append({
                "item_id": _make_item_id(source_label, url),
                "source": source_label,
                "title": title,
                "url": url,
                "published_at": _entry_published(entry),
                "text_for_matching": f"{title}\n{summary}",
                "fetched_at": datetime.now(timezone.utc).isoformat(),
            })

    return items
