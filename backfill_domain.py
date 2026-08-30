"""
One-time backfill: recomputes 'domain' (conflict vs disaster) for items
matched BEFORE domain classification existed. Every historical item
currently defaults to 'conflict' regardless of actual content -- this
script re-evaluates each item's stored matched_keywords against the
disaster keyword set and corrects the domain where it was wrong.

This is exactly why "only one earthquake showed as a triangle" -- the
rest of your history predates this feature and was never re-evaluated.

Safe to run multiple times -- only touches rows where the computed
domain differs from what's currently stored.

Run: python backfill_domain.py
"""
import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from core.severity import classify_domain


def main():
    conn = sqlite3.connect("intel_monitor.db")
    conn.row_factory = sqlite3.Row

    rows = conn.execute(
        "SELECT item_id, matched_keywords, domain, category FROM seen_items "
        "WHERE notified = 1 AND category != 'travel'"
    ).fetchall()

    print(f"Checking {len(rows)} historical item(s) for domain reclassification...\n")

    updates = []
    for row in rows:
        keywords = (row["matched_keywords"] or "").split(",")
        correct_domain = classify_domain(keywords)
        if correct_domain != row["domain"]:
            updates.append((row["item_id"], row["domain"], correct_domain))

    if not updates:
        print("Nothing to fix -- all items already have the correct domain.")
        conn.close()
        return

    print(f"Found {len(updates)} item(s) with an outdated domain classification "
          f"(all currently 'conflict' that should actually be 'disaster', or vice versa):\n")

    disaster_reclassified = sum(1 for _, old, new in updates if new == "disaster")
    conflict_reclassified = sum(1 for _, old, new in updates if new == "conflict")
    print(f"  {disaster_reclassified} item(s) will be corrected: conflict -> disaster")
    print(f"  {conflict_reclassified} item(s) will be corrected: disaster -> conflict")

    confirm = input(f"\nApply these {len(updates)} correction(s)? [y/N] ").strip().lower()
    if confirm != "y":
        print("Cancelled, nothing changed.")
        conn.close()
        return

    for item_id, old_domain, new_domain in updates:
        conn.execute("UPDATE seen_items SET domain = ? WHERE item_id = ?", (new_domain, item_id))
    conn.commit()
    conn.close()

    print(f"\nBackfilled {len(updates)} item(s). Run python main.py to regenerate the map "
          f"reflecting this -- you should see many more triangle markers now.")


if __name__ == "__main__":
    main()
