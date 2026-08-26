"""
One-time backfill: computes region + severity for items that were matched
BEFORE region/severity tracking existed in the database (i.e. everything
matched before this update was installed).

Safe to run multiple times -- only touches rows where region is still NULL,
so it does nothing on a second run once backfill is complete.

Run: python backfill_severity.py
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from core.db import init_db, get_items_needing_backfill, update_severity_region
from core import severity

CONFIG_PATH = Path(__file__).resolve().parent / "config.json"


def main():
    config = json.loads(CONFIG_PATH.read_text())
    regions = config["regions"]

    init_db()
    items = get_items_needing_backfill()
    print(f"Found {len(items)} item(s) needing backfill.")

    if not items:
        print("Nothing to do -- all items already have region/severity data.")
        return

    updated = 0
    skipped = 0
    for item in items:
        keywords_str = item.get("matched_keywords") or ""
        keywords = [k.strip() for k in keywords_str.split(",") if k.strip()]

        region_hits = [k for k in keywords if k in regions]
        keyword_hits = [k for k in keywords if k not in regions]
        primary_region = region_hits[0] if region_hits else None

        if not primary_region:
            # Can't plot without a region -- leave it, dashboard/map just won't show it geographically
            skipped += 1
            continue

        if item["category"] == "travel":
            score, tier = severity.score_travel(item.get("title") or "")
        else:
            score, tier = severity.score_geopolitical(keyword_hits)

        update_severity_region(item["item_id"], primary_region, tier, score)
        updated += 1

    print(f"Backfilled {updated} item(s). Skipped {skipped} item(s) with no identifiable region.")
    print("Run `python main.py` next (or just open dashboard.html / map.html directly --")
    print("they read straight from the database, no need to re-fetch feeds to see the backfill).")


if __name__ == "__main__":
    main()
