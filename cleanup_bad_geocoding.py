"""
One-time cleanup: re-validates every EXISTING city-geocoded item against
the new region-plausibility check, and clears any that fail (falls back
to the safe region-centroid pin instead).

This exists because the plausibility check only protects NEW items going
forward -- any bad geocoding that happened before this fix (like a
Russia/Ukraine story that ended up plotted in the Philippines) is still
sitting in the database with wrong coordinates until this runs once.

Safe to run multiple times -- only touches rows that currently have city
coordinates set, and only clears the ones that fail the check.

Run: python cleanup_bad_geocoding.py
"""
import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from core.geocoding import is_plausible_for_region


def main():
    conn = sqlite3.connect("intel_monitor.db")
    conn.row_factory = sqlite3.Row

    rows = conn.execute(
        "SELECT item_id, title, region, city_name, city_lat, city_lon "
        "FROM seen_items WHERE city_name IS NOT NULL AND city_lat IS NOT NULL"
    ).fetchall()

    print(f"Checking {len(rows)} existing geocoded item(s) against the plausibility check...\n")

    cleared = []
    for row in rows:
        if not is_plausible_for_region(row["city_lat"], row["city_lon"], row["region"]):
            cleared.append(row)

    if not cleared:
        print("Nothing to clean up -- all existing geocoded items pass the plausibility check.")
        conn.close()
        return

    print(f"Found {len(cleared)} item(s) with implausible geocoding:\n")
    for row in cleared:
        print(f"  '{row['city_name']}' tagged as {row['region']}, but coordinates are implausibly far away")
        print(f"    Title: {row['title'][:70]}")
        print()

    confirm = input(f"Clear city-level coordinates for these {len(cleared)} item(s)? "
                     f"(they'll fall back to their region's centroid pin instead) [y/N] ").strip().lower()

    if confirm != "y":
        print("Cancelled, nothing changed.")
        conn.close()
        return

    for row in cleared:
        conn.execute(
            "UPDATE seen_items SET city_name = NULL, city_lat = NULL, city_lon = NULL WHERE item_id = ?",
            (row["item_id"],),
        )
    conn.commit()
    conn.close()

    print(f"\nCleared {len(cleared)} item(s). Run python main.py to regenerate the map "
          f"reflecting this -- those items will now show at their region's centroid instead.")


if __name__ == "__main__":
    main()
