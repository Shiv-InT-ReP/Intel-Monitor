"""
Confidence scoring via cross-source corroboration -- specifically against
CREDIBLE sources, not just any repetition.

Design principle: corroboration only counts if it comes from an edited,
accountable news outlet (RSS sources, ACLED) -- not from Telegram or Reddit
chatter. If four Telegram channels repost the same unverified rumor, that's
an echo chamber, not verification. A single BBC or Al Jazeera article
independently confirming an event is worth more than five reposts of the
same unconfirmed claim.

Three tiers (deliberately different vocabulary from severity's low/moderate/
high/critical, so the two concepts never look interchangeable in the UI):

- "unverified"    -- no trusted-tier source reports this; only chatter/OSINT
- "single-source"  -- exactly one trusted outlet reports it, no second confirmation
- "corroborated"  -- 2+ DISTINCT trusted outlets independently report it

Deliberately NOT using an LLM/embedding model for clustering: title
similarity via difflib is free, fast, zero dependencies, and "good enough"
here -- it doesn't need to be perfect, just directionally useful.
"""
import difflib
from datetime import datetime, timezone, timedelta
from core.source_reliability import is_propaganda_blocked

TITLE_SIMILARITY_THRESHOLD = 0.5
TIME_WINDOW_HOURS = 48

# Trusted = edited, accountable news/institutional sources (identified by
# source-string prefix). Untrusted = raw social/chatter aggregation, which
# can still be useful signal but should never count as "verification" on
# its own, however many times it's repeated.
TRUSTED_PREFIXES = ("rss:", "acled", "gdelt:")
# telegram: and reddit: are deliberately NOT in this list.


def _is_trusted(source: str) -> bool:
    if is_propaganda_blocked(source):
        return False  # state propaganda never counts as trusted corroboration, even if RSS-sourced
    return source.startswith(TRUSTED_PREFIXES)


def _normalize_title(title: str) -> str:
    return " ".join(title.lower().split())


def _titles_similar(a: str, b: str) -> bool:
    ratio = difflib.SequenceMatcher(None, _normalize_title(a), _normalize_title(b)).ratio()
    return ratio >= TITLE_SIMILARITY_THRESHOLD


def _parse_time(iso_str: str):
    if not iso_str:
        return None
    try:
        return datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
    except ValueError:
        return None


def _within_time_window(a: str, b: str) -> bool:
    ta, tb = _parse_time(a), _parse_time(b)
    if ta is None or tb is None:
        return True
    return abs((ta - tb).total_seconds()) <= TIME_WINDOW_HOURS * 3600


def _likely_same_event(item_a: dict, item_b: dict) -> bool:
    if item_a["item_id"] == item_b["item_id"]:
        return False
    region = item_a.get("region")
    if item_b.get("region") != region or not region:
        return False

    kw_a = set((item_a.get("matched_keywords") or "").split(",")) - {region}
    kw_b = set((item_b.get("matched_keywords") or "").split(",")) - {region}
    if not (kw_a & kw_b):
        return False

    if not _within_time_window(item_a.get("first_seen_at"), item_b.get("first_seen_at")):
        return False

    return _titles_similar(item_a.get("title", ""), item_b.get("title", ""))


def cluster_items(items: list[dict]) -> list[list[dict]]:
    """Groups items into clusters of likely-same-event via connected components."""
    n = len(items)
    parent = list(range(n))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(x, y):
        rx, ry = find(x), find(y)
        if rx != ry:
            parent[rx] = ry

    for i in range(n):
        for j in range(i + 1, n):
            if _likely_same_event(items[i], items[j]):
                union(i, j)

    clusters_map = {}
    for i in range(n):
        root = find(i)
        clusters_map.setdefault(root, []).append(items[i])

    return list(clusters_map.values())


def score_confidence(items: list[dict]) -> dict[str, dict]:
    """
    Given item dicts (each needs: item_id, region, matched_keywords, title,
    first_seen_at, source, url), returns:
        {item_id: {"tier": str, "trusted_count": int, "corroborating_links": [{"source": str, "url": str}, ...]}}

    Every item in a cluster gets the SAME tier and the SAME list of trusted
    corroborating links -- so even a Telegram post shows which credible
    outlet(s), if any, independently confirmed the same event.
    """
    clusters = cluster_items(items)
    result = {}

    for cluster in clusters:
        # Dedup trusted sources by source name (not by item -- if the same
        # outlet posted twice about the same event, that's still 1 source).
        trusted_by_source = {}
        for item in cluster:
            if _is_trusted(item["source"]) and item["source"] not in trusted_by_source:
                trusted_by_source[item["source"]] = item.get("url", "#")

        trusted_count = len(trusted_by_source)
        links = [{"source": src, "url": url} for src, url in trusted_by_source.items()]

        if trusted_count >= 2:
            tier = "corroborated"
        elif trusted_count == 1:
            tier = "single-source"
        else:
            tier = "unverified"

        for item in cluster:
            result[item["item_id"]] = {
                "tier": tier,
                "trusted_count": trusted_count,
                "corroborating_links": links,
            }

    return result
