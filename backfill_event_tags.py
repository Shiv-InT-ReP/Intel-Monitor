"""
One-time backfill: computes event_tags for items matched BEFORE the
multi-tag filter system existed. Every historical item currently has
event_tags = NULL, meaning none of them show up under any of the new
Security/Protest/Disaster/SLOC/Iran/Russia-Ukraine/Defence filters until
this runs once.

Safe to run multiple times -- only touches rows where event_tags is
currently NULL/empty.

Run: python backfill_event_tags.py
"""
import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from core.db import init_db
from core.event_tags import classify_event_tags, TAG_LABELS


def main():
    init_db()  # ensures the event_tags column migration has run, regardless of execution order
    conn = sqlite3.connect("intel_monitor.db")
    conn.row_factory = sqlite3.Row

    rows = conn.execute(
        "SELECT item_id, matched_keywords, region, category FROM seen_items "
        "WHERE notified = 1 AND (event_tags IS NULL OR event_tags = '')"
    ).fetchall()

    print(f"Checking {len(rows)} historical item(s) for tag backfill...\n")

    if not rows:
        print("Nothing to do -- all items already have tags computed.")
        conn.close()
        return

    tag_counts = {tag: 0 for tag in TAG_LABELS}
    untagged = 0
    updates = []

    for row in rows:
        if row["category"] == "travel":
            continue  # travel advisories don't get these tags

        keywords = (row["matched_keywords"] or "").split(",")
        tags = classify_event_tags(keywords, region=row["region"])

        if tags:
            for t in tags:
                tag_counts[t] += 1
            updates.append((row["item_id"], ",".join(tags)))
        else:
            untagged += 1

    print("Tag distribution after backfill:")
    for tag, label in TAG_LABELS.items():
        print(f"  {label}: {tag_counts[tag]}")
    print(f"  (no applicable tag): {untagged}")

    confirm = input(f"\nApply tags to {len(updates)} item(s)? [y/N] ").strip().lower()
    if confirm != "y":
        print("Cancelled, nothing changed.")
        conn.close()
        return

    for item_id, tags_str in updates:
        conn.execute("UPDATE seen_items SET event_tags = ? WHERE item_id = ?", (tags_str, item_id))
    conn.commit()
    conn.close()

    print(f"\nBackfilled {len(updates)} item(s). Run python main.py to regenerate the "
          f"dashboard/map with all the new filters populated.")


if __name__ == "__main__":
    main()
