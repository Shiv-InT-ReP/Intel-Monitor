"""
One-time fix: USGS earthquakes on oceanic ridges/junctions (e.g. "Southwest
Indian Ridge") got incorrectly tagged region="India" before the word-boundary
matching fix, since "india" is a substring of "indian ridge". These aren't
actually near India or any tracked region -- clearing their region so they
correctly stop showing on the map (matching how any item with no real
region is already handled), rather than showing as a misleading India blip.
"""
import sqlite3

conn = sqlite3.connect("intel_monitor.db")
conn.row_factory = sqlite3.Row

rows = conn.execute(
    "SELECT item_id, title FROM seen_items "
    "WHERE source = 'usgs' AND region = 'India' "
    "AND (title LIKE '%Ridge%' OR title LIKE '%Triple Junction%' OR title LIKE '%Ocean%')"
).fetchall()

print(f"Found {len(rows)} mis-tagged oceanic USGS event(s):\n")
for row in rows:
    print(f"  {row['title']}")

if rows:
    for row in rows:
        conn.execute("UPDATE seen_items SET region = NULL WHERE item_id = ?", (row["item_id"],))
    conn.commit()
    print(f"\nCleared region tag for {len(rows)} item(s) -- they'll correctly stop appearing on the map.")
else:
    print("\nNothing to fix.")

conn.close()
