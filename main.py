"""
Intel Monitor — orchestrator.

Pulls from RSS, Reddit, and Telegram (whichever are enabled in config.json),
dedupes against SQLite history, matches against your keyword/region list,
and emails you a digest of anything new and relevant.

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
from core.matcher import build_matcher
from collectors import rss_collector, reddit_collector, telegram_collector
from notifier import email_notifier

CONFIG_PATH = Path(__file__).resolve().parent / "config.json"


def load_config() -> dict:
    return json.loads(CONFIG_PATH.read_text())


def run():
    print(f"=== Intel Monitor run started {datetime.now().isoformat()} ===")
    config = load_config()
    init_db()

    matcher = build_matcher(
        keywords=config["keywords"],
        regions=config["regions"],
        case_sensitive=config.get("case_sensitive", False),
    )

    all_items = []

    print("[*] Fetching RSS feeds...")
    all_items += rss_collector.collect(config["rss_feeds"])

    print("[*] Fetching Reddit...")
    all_items += reddit_collector.collect(config["reddit"])

    print("[*] Fetching Telegram...")
    all_items += telegram_collector.collect(
        config["telegram"], lookback_hours=config.get("lookback_hours_first_run", 24)
    )

    print(f"[*] Fetched {len(all_items)} total items across all sources.")

    new_matched_items = []
    for item in all_items:
        if is_seen(item["item_id"]):
            continue

        hits = matcher(item["text_for_matching"])
        item["matched_keywords"] = hits

        if hits:
            new_matched_items.append(item)
            mark_seen(item, notified=True)
        else:
            mark_seen(item, notified=False)  # still record it so we never re-check it

    print(f"[*] {len(new_matched_items)} new item(s) matched your keywords/regions.")

    if new_matched_items:
        email_notifier.send_digest(config["email"], new_matched_items)
    else:
        print("[*] Nothing new to notify.")

    print(f"=== Run complete {datetime.now().isoformat()} ===\n")


if __name__ == "__main__":
    run()
