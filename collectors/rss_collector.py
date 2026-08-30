"""
RSS/Atom feed collector. No API keys needed.
Works for Reuters, Al Jazeera, government advisory feeds, think-tank
feeds (CFR, Crisis Group, etc.), and most news outlets that publish RSS.

Deliberately does NOT reject old/stale items here -- staleness is handled
downstream (main.py) where we can distinguish "too old to alert on via
email" from "still worth storing so the dashboard's 90-day/all-time view
can show it." Rejecting at ingestion would have permanently lost data that
a broader time-window filter should legitimately be able to surface.
"""
import hashlib
import re
from datetime import datetime, timezone

import feedparser

_HTML_TAG_RE = re.compile(r"<[^>]+>")


def _make_item_id(source: str, url: str) -> str:
    return hashlib.sha256(f"{source}|{url}".encode()).hexdigest()


def _strip_html(text: str) -> str:
    """
    Some feeds (rarely, but it happens) embed literal HTML tags directly
    inside their <title> or <summary> XML elements -- feedparser only
    decodes HTML entities, it doesn't strip actual markup, so this can
    leak raw <a href="...">...</a> tags straight into our data otherwise.
    """
    if not text:
        return text
    return _HTML_TAG_RE.sub("", text).strip()


def _entry_published(entry) -> str | None:
    for field in ("published", "updated"):
        if hasattr(entry, field):
            return getattr(entry, field)
    return None


def collect(feed_configs: list[dict], filter_stale: bool = True) -> list[dict]:
    """
    feed_configs: [{"name": "Reuters World", "url": "https://...", ...}]
    Returns a list of normalized item dicts.

    filter_stale is kept as a parameter for backward compatibility with
    existing call sites, but no longer changes collection behavior --
    every item is collected regardless of age. Staleness-based decisions
    (what to email, what to show by default) happen in main.py instead.
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
            if not url:
                continue

            title = _strip_html(getattr(entry, "title", ""))
            summary = _strip_html(getattr(entry, "summary", ""))

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
