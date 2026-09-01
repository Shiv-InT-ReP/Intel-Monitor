"""
One-time (or occasional) backfill: re-checks EXISTING historical matched
items against the current AI context classifier, catching everything it
now knows how to catch that older data predates:

1. Off-topic/irrelevant matches (e.g. the Egypt necklace theft story) --
   gets ARCHIVED (reversible, never deleted).
2. Wrong domain classification (e.g. "drone storm" wrongly tagged as a
   natural disaster) -- corrected in place.
3. False-positive event tags (e.g. "troop" matching a Boy Scout troop
   story under Defence) -- stripped in place.
4. Wrong disaster-location region (e.g. a Nepal flood story pinned to
   Israel because of an incidentally-mentioned victim's nationality) --
   corrected in place, with any now-stale city coordinates cleared too.

Processes in batches of MAX_ITEMS_PER_RUN (reusing context_classifier's
existing batching/cost controls). Shows you a full summary and asks for
confirmation before changing anything.

Run: python backfill_context_check.py
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from core.db import (
    init_db, get_dashboard_data, archive_item,
    set_item_domain, remove_event_tag, set_item_region,
)
from core.context_classifier import classify_context_batch, MAX_ITEMS_PER_RUN


def _load_config() -> dict:
    config_path = Path(__file__).resolve().parent / "config.json"
    try:
        return json.loads(config_path.read_text())
    except Exception as e:
        print(f"Couldn't load config.json: {e}")
        return {}


def _prepare_candidates(item: dict, all_regions: list[str]) -> dict:
    """Reconstructs the candidate tags/regions a historical item needs for
    re-classification, mirroring what the live pipeline attaches in main.py."""
    item["_candidate_tags"] = [t for t in item.get("event_tags", []) if t not in ("iran_war", "russia_ukraine_war")]

    stored_hits = (item.get("matched_keywords") or "").split(",")
    regions_lower = {r.lower(): r for r in all_regions}
    candidate_regions = [regions_lower[h.lower()] for h in stored_hits if h.lower() in regions_lower]
    item["_candidate_regions"] = candidate_regions or ([item["region"]] if item.get("region") else [])
    return item


def main():
    init_db()
    config = _load_config()
    all_regions = config.get("regions", [])
    ai_config = config.get("ai_dedup", {})

    if not ai_config.get("enabled") or not ai_config.get("api_key"):
        print("AI dedup/context classifier isn't enabled in config.json (or no api_key set) -- nothing to do.")
        return

    all_items = get_dashboard_data(include_archived=False)
    candidates = [item for item in all_items if item.get("category") == "geopolitical"]
    candidates = [_prepare_candidates(item, all_regions) for item in candidates]

    print(f"Found {len(candidates)} historical geopolitical item(s) to re-check.\n")
    if not candidates:
        print("Nothing to check.")
        return

    total_batches = (len(candidates) + MAX_ITEMS_PER_RUN - 1) // MAX_ITEMS_PER_RUN
    confirm = input(
        f"This will make ~{total_batches} API call(s) (batched {MAX_ITEMS_PER_RUN} headlines "
        f"per call) using your configured Anthropic API key. Continue? [y/N] "
    ).strip().lower()
    if confirm != "y":
        print("Cancelled, nothing changed.")
        return

    to_archive = []
    to_correct_domain = []   # (item, new_domain)
    to_correct_tags = []     # (item, tags_to_remove)
    to_correct_region = []   # (item, new_region)

    for batch_start in range(0, len(candidates), MAX_ITEMS_PER_RUN):
        batch = candidates[batch_start:batch_start + MAX_ITEMS_PER_RUN]
        batch_num = batch_start // MAX_ITEMS_PER_RUN + 1
        print(f"Checking batch {batch_num}/{total_batches} ({len(batch)} items)...")

        classifications = classify_context_batch(batch, ai_config)
        for item in batch:
            result = classifications.get(item["item_id"])
            if result is None:
                continue  # API failure or malformed entry for this item -- fail safe, leave unchanged

            if not result["relevant"]:
                to_archive.append(item)
                if item.get("_candidate_tags"):
                    to_correct_tags.append((item, item["_candidate_tags"]))
                continue

            if item.get("domain") and item["domain"] != result["domain"]:
                to_correct_domain.append((item, result["domain"]))

            rejected = [t for t in item.get("_candidate_tags", []) if t not in result.get("confirmed_tags", [])]
            if rejected:
                to_correct_tags.append((item, rejected))

            correct_region = result.get("correct_region")
            if correct_region and item.get("region") and correct_region != item["region"]:
                to_correct_region.append((item, correct_region))

    total_changes = len(to_archive) + len(to_correct_domain) + len(to_correct_tags) + len(to_correct_region)
    if total_changes == 0:
        print("\nNo issues found -- everything already checks out.")
        return

    print(f"\n=== Summary of proposed changes ===")
    print(f"  Archive as irrelevant: {len(to_archive)}")
    print(f"  Correct domain (conflict/disaster): {len(to_correct_domain)}")
    print(f"  Strip false-positive tags: {len(to_correct_tags)}")
    print(f"  Correct wrong region: {len(to_correct_region)}\n")

    if to_archive:
        print("Items to archive:")
        for item in to_archive:
            print(f"  [{item['region']}] {item['title'][:75]}")
        print()
    if to_correct_domain:
        print("Domain corrections:")
        for item, new_domain in to_correct_domain:
            print(f"  {item['title'][:60]}: {item['domain']} -> {new_domain}")
        print()
    if to_correct_region:
        print("Region corrections:")
        for item, new_region in to_correct_region:
            print(f"  {item['title'][:60]}: {item['region']} -> {new_region}")
        print()

    confirm2 = input(f"Apply all {total_changes} change(s)? (all reversible) [y/N] ").strip().lower()
    if confirm2 != "y":
        print("Cancelled, nothing changed.")
        return

    for item in to_archive:
        archive_item(item["item_id"])
    for item, new_domain in to_correct_domain:
        set_item_domain(item["item_id"], new_domain)
    for item, tags_to_remove in to_correct_tags:
        for tag in tags_to_remove:
            remove_event_tag(item["item_id"], tag)
    for item, new_region in to_correct_region:
        set_item_region(item["item_id"], new_region)

    print(f"\nApplied {total_changes} change(s). Run python main.py to regenerate the "
          f"dashboard/map/background/releases pages reflecting this.")
    print("Archives are reversible: python archive_item.py --unarchive <item_id>")


if __name__ == "__main__":
    main()
