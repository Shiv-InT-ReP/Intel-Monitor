"""
Generates the radar map view (map.html) from real matched items in SQLite.

Reads map_template.html (kept as a separate file rather than an embedded
Python string, since the template contains a lot of JS template-literal
syntax with backticks and ${...} that would be painful and error-prone
to escape inside a Python triple-quoted string).
"""
import json
from datetime import datetime, timezone
from pathlib import Path

from core.db import get_dashboard_data

TEMPLATE_PATH = Path(__file__).resolve().parent / "map_template.html"
MAP_OUTPUT_PATH = Path(__file__).resolve().parent.parent / "map.html"

# Regions we have coordinates for -- must match REGION_COORDS in the template's JS.
# Broad/non-point regions (APAC, South Asia, Southeast Asia) are intentionally
# excluded since they don't have one sensible coordinate to plot.
KNOWN_REGIONS = {
    "Taiwan", "China", "Iran", "Israel", "Ukraine", "Russia", "India",
    "Pakistan", "Afghanistan", "Bangladesh", "Nepal", "Sri Lanka",
    "Myanmar", "Burma", "Cambodia", "Vietnam", "Thailand",
    "Middle East", "Europe", "South China Sea",
}


def generate_map():
    all_items = get_dashboard_data()

    # Only items with a real, plottable region and non-null severity make it onto the map.
    map_items = []
    for item in all_items:
        region = item.get("region")
        if not region or region not in KNOWN_REGIONS:
            continue
        # "Burma" and "Myanmar" both matched but only "Myanmar" has coords in the template
        if region == "Burma":
            region = "Myanmar"

        map_items.append({
            "region": region,
            "category": item.get("category", "geopolitical"),
            "severity": item.get("severity_tier", "low"),
            "title": item.get("title", ""),
            "source": item.get("source", ""),
            "url": item.get("url", "#"),
        })

    data_json = json.dumps(map_items)
    # Same </script guard as the dashboard generator -- see comment there.
    data_json = data_json.replace("</script", "<\\/script").replace("</SCRIPT", "<\\/SCRIPT")
    template = TEMPLATE_PATH.read_text(encoding="utf-8")
    html = template.replace("__DATA_JSON__", data_json)

    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    html = html.replace(
        '<p class="mono" style="font-size:10px;color:var(--text-dim);margin:6px 0 0;" id="genTime"></p>',
        f'<p class="mono" style="font-size:10px;color:var(--text-dim);margin:6px 0 0;">GENERATED {generated_at}</p>'
    )

    MAP_OUTPUT_PATH.write_text(html, encoding="utf-8")
    print(f"  [x] Map updated: {MAP_OUTPUT_PATH} ({len(map_items)} plottable items)")
    return MAP_OUTPUT_PATH
