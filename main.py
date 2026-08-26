"""
Intel Monitor — orchestrator.

Pulls from RSS, Reddit, and Telegram (whichever are enabled in config.json),
dedupes against SQLite history, matches against your keyword/region list,
and emails you a two-section digest: geopolitical/security alerts (strict
region+keyword matching) and travel advisories (region-only matching,
since travel advisory feeds are already inherently travel-risk content).

Run manually:      python main.py
Schedule (Windows): see README.md for a Task Scheduler snippet, same
                     pattern as your price tracker.
"""
import json
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from core.db import init_db, is_seen, mark_seen
from core.matcher import get_matcher, build_region_only_matcher
from core import severity
from collectors import rss_collector, reddit_collector, telegram_collector
from notifier import email_notifier
from dashboard.dashboard_generator import generate_dashboard
from dashboard.map_generator import generate_map

CONFIG_PATH = Path(__file__).resolve().parent / "config.json"


def load_config() -> dict:
    return json.loads(CONFIG_PATH.read_text())


def _process_items(items: list[dict], matcher, category: str, regions: list[str]) -> list[dict]:
    """Dedupe + match + score a batch of items. Returns only new, matched items."""
    matched = []
    for item in items:
        if is_seen(item["item_id"]):
            continue

        hits = matcher(item["text_for_matching"])
        item["matched_keywords"] = hits

        if hits:
            # Separate which hits were REGION terms vs ESCALATION keyword terms,
            # so we can plot by region and score by keyword severity separately.
            region_hits = [h for h in hits if h in regions]
            keyword_hits = [h for h in hits if h not in regions]
            primary_region = region_hits[0] if region_hits else None

            if category == "travel":
                score, tier = severity.score_travel(item["text_for_matching"])
            else:
                score, tier = severity.score_geopolitical(keyword_hits)

            matched.append(item)
            mark_seen(item, notified=True, category=category,
                      severity_tier=tier, severity_score=score, region=primary_region)
        else:
            mark_seen(item, notified=False, category=category)  # record so we never re-check it
    return matched


def run():
    print(f"=== Intel Monitor run started {datetime.now().isoformat()} ===")
    config = load_config()
    init_db()

    geo_matcher = get_matcher(config)
    travel_matcher = build_region_only_matcher(
        regions=config["regions"],
        case_sensitive=config.get("case_sensitive", False),
    )
    print(f"[*] Match mode: {config.get('match_mode', 'strict')} (geopolitical) / region-only (travel advisories)")

    # --- Geopolitical / security sources ---
    geo_items = []
    print("[*] Fetching RSS feeds...")
    geo_items += rss_collector.collect(config["rss_feeds"])

    print("[*] Fetching Reddit...")
    geo_items += reddit_collector.collect(config["reddit"])

    print("[*] Fetching Telegram...")
    geo_items += telegram_collector.collect(
        config["telegram"], lookback_hours=config.get("lookback_hours_first_run", 24)
    )

    print(f"[*] Fetched {len(geo_items)} total geopolitical items.")
    new_geo_matches = _process_items(geo_items, geo_matcher, category="geopolitical", regions=config["regions"])
    print(f"[*] {len(new_geo_matches)} new geopolitical item(s) matched.")

    # --- Travel advisory sources (separate feed list, separate matcher) ---
    new_travel_matches = []
    travel_feeds = config.get("travel_advisory_feeds", [])
    if travel_feeds:
        print("[*] Fetching travel advisory feeds...")
        travel_items = rss_collector.collect(travel_feeds)
        print(f"[*] Fetched {len(travel_items)} total travel advisory items.")
        new_travel_matches = _process_items(travel_items, travel_matcher, category="travel", regions=config["regions"])
        print(f"[*] {len(new_travel_matches)} new travel advisory item(s) matched.")

    # --- Notify ---
    if new_geo_matches or new_travel_matches:
        email_notifier.send_digest(config["email"], new_geo_matches, new_travel_matches)
    else:
        print("[*] Nothing new to notify.")

    # --- Refresh dashboard and map (always, so they reflect full history even on quiet runs) ---
    generate_dashboard()
    generate_map()

    print(f"=== Run complete {datetime.now().isoformat()} ===\n")


if __name__ == "__main__":
    run()
