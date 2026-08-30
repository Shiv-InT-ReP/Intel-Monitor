"""
Interactive tool to manually mark events as resolved/archived.

Archiving is deliberately a HUMAN decision, not automated -- Intel Monitor
never guesses that a conflict or crisis is "over." You search for the
event, review the matches, and decide yourself. Archived items are never
deleted, just excluded from the default dashboard/map view -- you can
always find them again with --show-archived or unarchive them.

Usage:
    python archive_item.py "search text"          Search and interactively pick items to archive
    python archive_item.py --show-archived         List everything currently archived
    python archive_item.py --unarchive <item_id>   Reverse an archive action
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from core.db import init_db, search_items_for_archiving, archive_item, unarchive_item, get_dashboard_data


def interactive_archive(search_term: str):
    init_db()
    matches = search_items_for_archiving(search_term)

    if not matches:
        print(f"No items found matching '{search_term}'.")
        return

    print(f"\nFound {len(matches)} item(s) matching '{search_term}':\n")
    for i, item in enumerate(matches, 1):
        status = " [ALREADY ARCHIVED]" if item["archived"] else ""
        print(f"  {i}. [{item['severity_tier']}] {item['title'][:80]}{status}")
        print(f"     {item['source']} | {item['region']} | {item['first_seen_at'][:10]}")
        print()

    print("Enter the number(s) to archive (comma-separated, e.g. '1,3'), or 'q' to quit:")
    choice = input("> ").strip()

    if choice.lower() == "q":
        print("Cancelled, nothing archived.")
        return

    try:
        indices = [int(x.strip()) - 1 for x in choice.split(",")]
    except ValueError:
        print("Invalid input, nothing archived.")
        return

    archived_count = 0
    for idx in indices:
        if 0 <= idx < len(matches):
            item = matches[idx]
            if archive_item(item["item_id"]):
                print(f"  [x] Archived: {item['title'][:60]}")
                archived_count += 1

    print(f"\nArchived {archived_count} item(s). They're excluded from the dashboard/map by default now,")
    print("but never deleted -- run 'python archive_item.py --show-archived' anytime to see them,")
    print("or unarchive with 'python archive_item.py --unarchive <item_id>'.")
    print("\nRun python main.py to regenerate the dashboard/map reflecting this change.")


def show_archived():
    init_db()
    all_items = get_dashboard_data(include_archived=True)
    archived = [i for i in all_items if i.get("archived")]

    if not archived:
        print("Nothing is currently archived.")
        return

    print(f"\n{len(archived)} archived item(s):\n")
    for item in archived:
        print(f"  [{item['item_id'][:12]}...] {item['title'][:70]}")
        print(f"     {item['source']} | {item['region']} | {item['first_seen_at'][:10]}")
        print()


def do_unarchive(item_id: str):
    init_db()
    if unarchive_item(item_id):
        print(f"Unarchived item {item_id[:12]}... -- it will show up in the dashboard/map again.")
    else:
        print(f"No item found with id starting {item_id[:12]}... (use the full item_id from --show-archived)")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
    elif sys.argv[1] == "--show-archived":
        show_archived()
    elif sys.argv[1] == "--unarchive" and len(sys.argv) > 2:
        do_unarchive(sys.argv[2])
    else:
        interactive_archive(" ".join(sys.argv[1:]))
