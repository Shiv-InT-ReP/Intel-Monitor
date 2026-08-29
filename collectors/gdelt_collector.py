"""
GDELT verification -- queries GDELT's free DOC 2.0 full-text search API
to check whether a SPECIFIC already-flagged item is independently
corroborated elsewhere, rather than blanket-scanning all tracked regions
every run.

Why targeted, not blanket: querying all 23 tracked regions every run took
over 10 minutes and mostly timed out (GDELT's free API doesn't handle that
volume of rapid requests well). Targeted verification -- only checking the
handful of high-severity items that are currently unverified -- is faster,
more reliable, and matches the actual use case: "verify this specific
concerning report," not "scan everything constantly."

No API key or credentials needed.

Docs: https://blog.gdeltproject.org/gdelt-doc-2-0-api-debuts/
"""
import time
from datetime import datetime, timezone

import requests

API_URL = "https://api.gdeltproject.org/api/v2/doc/doc"

QUERY_DELAY_SECONDS = 2.0
MAX_RETRIES = 1
RETRY_DELAY_SECONDS = 4.0
REQUEST_TIMEOUT_SECONDS = 15


def verify_item(region: str, keywords: list[str], own_source: str,
                 lookback_hours: int = 48) -> list[dict]:
    """
    Checks GDELT for independent corroboration of a specific item, using
    its own region + its own matched keywords (not a generic broad list --
    this makes the query specific to what we're actually trying to verify).

    Returns a list of {"source": "gdelt:domain", "url": "..."} dicts for
    any DISTINCT-domain articles found that aren't the item's own source.
    Empty list if nothing found or the query fails.
    """
    # Use up to 3 of the item's own escalation keywords (skip the region
    # name itself if it appears in the keyword list) to keep the query tight
    # and specific to this exact story, not a broad regional sweep.
    escalation_terms = [k for k in keywords if k.lower() != region.lower()][:3]
    if not escalation_terms:
        return []

    query = f'"{region}" (' + " OR ".join(escalation_terms) + ")"
    params = {
        "query": query,
        "mode": "ArtList",
        "maxrecords": 10,  # only need a couple of corroborating hits, not a full sweep
        "timespan": f"{lookback_hours}h",
        "format": "json",
    }

    last_error = None
    data = None
    for attempt in range(MAX_RETRIES + 1):
        try:
            resp = requests.get(API_URL, params=params, timeout=REQUEST_TIMEOUT_SECONDS)
            resp.raise_for_status()
            data = resp.json()
            break
        except Exception as e:
            last_error = e
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_DELAY_SECONDS)
            continue
    else:
        print(f"  [!] GDELT verification failed for '{region}': {last_error}")
        return []

    articles = data.get("articles", []) if data else []
    own_domain = own_source.split(":", 1)[-1] if ":" in own_source else own_source

    results = []
    seen_domains = set()
    for art in articles:
        domain = art.get("domain", "")
        url = art.get("url")
        if not domain or not url or domain == own_domain or domain in seen_domains:
            continue
        seen_domains.add(domain)
        results.append({"source": f"gdelt:{domain}", "url": url})

    return results


def verify_batch(candidates: list[dict], gdelt_config: dict) -> dict[str, list[dict]]:
    """
    candidates: list of dicts with item_id, region, matched_keywords (comma
    string), source. Returns {item_id: [corroborating source dicts]} for
    items where GDELT found independent confirmation.
    """
    if not gdelt_config.get("enabled"):
        return {}

    results = {}
    for candidate in candidates:
        keywords = (candidate.get("matched_keywords") or "").split(",")
        found = verify_item(
            candidate["region"], keywords, candidate["source"],
            lookback_hours=gdelt_config.get("verify_lookback_hours", 48)
        )
        if found:
            results[candidate["item_id"]] = found
        time.sleep(QUERY_DELAY_SECONDS)

    return results
