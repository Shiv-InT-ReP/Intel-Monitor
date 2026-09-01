"""
One-time fix: unarchives specific items that were WRONGLY archived by the
context classifier during the historical backfill (backfill_context_check.py)
-- genuine security/SLOC/economic-impact stories that got misclassified as
irrelevant when checked in large batches with minimal context.

Matches by distinctive title substrings (exact item_ids weren't shown in
the original archive output, only titles), unarchives anything that
matches, and reports what it found. Safe to re-run -- unarchiving an
already-active item is a no-op.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from core.db import init_db, get_dashboard_data, unarchive_item

# Distinctive substrings from the headlines identified as wrongly archived --
# genuine SLOC/security/economic-impact stories, not off-topic false positives.
TITLES_TO_RESTORE = [
    "Vessel Hit by Projectile in Strait of Hormuz",
    "Hormuz flows remain choppy",
    "Berlin Pride attack pledged allegiance",
    "plotting attack on New York State Capitol",
    "coordinated arson attacks carried out across Thailand",
    "Iran war drained the piggy bank",
    "US strike on Iran school, parents still grieve",
    "Arctic Shipping Route to Europe",
    "Fozzy Group is cutting costs following Russian attacks",
]


def main():
    init_db()
    all_items = get_dashboard_data(include_archived=True)
    archived_items = [item for item in all_items if item.get("archived")]

    restored = []
    for item in archived_items:
        title = item["title"]
        if any(substr.lower() in title.lower() for substr in TITLES_TO_RESTORE):
            if unarchive_item(item["item_id"]):
                restored.append(item)

    print(f"Restored {len(restored)} item(s):\n")
    for item in restored:
        print(f"  [{item['region']}] {item['title'][:80]}")

    not_found = len(TITLES_TO_RESTORE) - len(restored)
    if not_found > 0:
        print(f"\n{not_found} of the {len(TITLES_TO_RESTORE)} target title(s) weren't found "
              f"among archived items -- they may already be active, or the title match didn't hit.")

    print("\nRun python main.py to regenerate the dashboard/map reflecting this.")


if __name__ == "__main__":
    main()
