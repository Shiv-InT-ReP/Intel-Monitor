"""
AI-powered dedup + delta summarization for the email digest.

Problem this solves: the same real-world event often gets reported by
multiple sources (BBC, Al Jazeera, a Telegram channel) and shows up as
several separate rows in the digest, forcing you to manually notice
they're the same story.

This module reuses the SAME clustering logic already built and tested for
confidence scoring (core.confidence.cluster_items) -- free, no API needed
for that part. Only for clusters of 2+ items does it call Claude (Haiku,
the cheapest/fastest model) to write one clean synthesized summary instead
of showing every raw headline separately.

"Delta" awareness: before writing the summary, we check how many related
reports already existed in the recent history (before this run) for the
same region+keyword combination, and tell Claude whether this is a
brand-new development or a continuation of an ongoing situation.

Failure handling: if the API call fails for any reason (bad key, network,
rate limit), that cluster's items are shown individually as normal --
dedup is a nice-to-have polish layer, never a point of failure for the
core pipeline.
"""
import requests

from core.confidence import cluster_items

API_URL = "https://api.anthropic.com/v1/messages"
DEFAULT_MODEL = "claude-haiku-4-5-20251001"


def _build_prompt(cluster: list[dict], prior_context_count: int) -> str:
    lines = []
    for item in cluster:
        lines.append(f"- [{item['source']}] {item['title']}")

    continuity_note = (
        f"Note: there have been {prior_context_count} other related report(s) about this "
        f"region/topic in the past 5 days -- treat this as a CONTINUING situation, not a brand-new one."
        if prior_context_count > 0
        else "This appears to be a NEW development with no recent related reports."
    )

    return (
        "You are summarizing OSINT/security monitoring reports for an intelligence analyst's "
        "daily digest. The following items appear to describe the SAME real-world event, "
        "reported by different sources:\n\n"
        + "\n".join(lines)
        + f"\n\n{continuity_note}\n\n"
        "Write ONE concise 2-3 sentence synthesis of the event. Note any factual differences "
        "between sources if they conflict (e.g. different casualty counts). Do not editorialize "
        "or speculate beyond what the sources state. Do not include a preamble -- output only "
        "the synthesis text itself."
    )


def _call_claude(prompt: str, api_key: str, model: str) -> str | None:
    try:
        resp = requests.post(
            API_URL,
            headers={
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            json={
                "model": model,
                "max_tokens": 200,
                "messages": [{"role": "user", "content": prompt}],
            },
            timeout=20,
        )
        resp.raise_for_status()
        data = resp.json()
        return data["content"][0]["text"].strip()
    except Exception as e:
        print(f"  [!] AI dedup: API call failed, showing items individually instead: {e}")
        return None


def _merge_cluster_metadata(cluster: list[dict]) -> dict:
    """Combines source list, keywords, and picks representative url/time from a cluster."""
    sources = sorted(set(item["source"] for item in cluster))
    all_keywords = set()
    for item in cluster:
        kws = item.get("matched_keywords", [])
        if isinstance(kws, list):
            all_keywords.update(kws)
        elif isinstance(kws, str):
            all_keywords.update(kws.split(","))

    # Use the item with the most detailed title as the "primary" one for the link
    primary = max(cluster, key=lambda i: len(i.get("title", "")))

    return {
        "sources": sources,
        "keywords": list(all_keywords),
        "url": primary.get("url"),
        "region": primary.get("region"),
        "severity_tier": primary.get("severity_tier", "low"),
        "published_at": primary.get("published_at"),
        "fetched_at": primary.get("fetched_at"),
    }


def dedupe_and_synthesize(items: list[dict], ai_config: dict, get_prior_context_count) -> list[dict]:
    """
    items: list of newly-matched item dicts (must have region, matched_keywords,
           title, first_seen_at/fetched_at, source, url, severity_tier set).
    get_prior_context_count: callable(region, keywords) -> int, used for delta context.

    Returns a list of digest-ready item dicts. Clusters of 1 pass through
    unchanged. Clusters of 2+ become ONE synthesized item (or, if the API
    call fails, the original items unchanged -- never silently drop stories).
    """
    if not ai_config.get("enabled") or not items:
        return items

    api_key = ai_config.get("api_key")
    model = ai_config.get("model", DEFAULT_MODEL)
    if not api_key:
        print("  [!] AI dedup enabled but no api_key configured -- skipping, showing items individually.")
        return items

    # cluster_items expects matched_keywords as comma-strings and needs 'item_id',
    # 'region', 'first_seen_at' -- items here have those (first_seen_at may be
    # under 'fetched_at' for freshly-collected items, so normalize).
    normalized = []
    for item in items:
        kws = item.get("matched_keywords", [])
        kw_str = ",".join(kws) if isinstance(kws, list) else (kws or "")
        normalized.append({
            **item,
            "matched_keywords": kw_str,
            "first_seen_at": item.get("first_seen_at") or item.get("fetched_at"),
        })

    clusters = cluster_items(normalized)
    digest_items = []

    for cluster in clusters:
        if len(cluster) == 1:
            digest_items.append(items[0] if len(items) == 1 else
                                 next(i for i in items if i["item_id"] == cluster[0]["item_id"]))
            continue

        meta = _merge_cluster_metadata(cluster)
        prior_count = get_prior_context_count(meta["region"], meta["keywords"])
        prompt = _build_prompt(cluster, prior_count)
        synthesis = _call_claude(prompt, api_key, model)

        if synthesis is None:
            # API failed -- fall back to showing original items individually for this cluster
            original_items = [i for i in items if i["item_id"] in {c["item_id"] for c in cluster}]
            digest_items.extend(original_items)
            continue

        source_count = len(meta["sources"])
        source_label = ", ".join(s.replace("rss:", "").replace("telegram:", "") for s in meta["sources"])
        digest_items.append({
            "item_id": "synth_" + "_".join(sorted(c["item_id"] for c in cluster))[:40],
            "title": synthesis,
            "source": f"{source_label} ({source_count} sources)",
            "url": meta["url"],
            "matched_keywords": meta["keywords"],
            "severity_tier": meta["severity_tier"],
            "published_at": meta["published_at"],
            "fetched_at": meta["fetched_at"],
        })

    return digest_items
