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
from core.chokepoints import CHOKEPOINTS, get_chokepoints_for_region
from core.shipping_routes import get_all_routes_with_status

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
    "Kashmir", "PoK", "Saudi Arabia", "Yemen", "Qatar",
    "Japan",
    "South Korea",
    "North Korea",
    "Australia",
    "New Zealand",
    "Indonesia",
    "Malaysia",
    "Singapore",
    "Philippines",
    "Papua New Guinea",
    "Mongolia",
    "Laos",
    "Brunei",
    "Timor-Leste",
    "Iraq",
    "Syria",
    "Lebanon",
    "Jordan",
    "Kuwait",
    "United Arab Emirates",
    "Bahrain",
    "Oman",
    "Turkey",
    "Egypt",
    "United Kingdom",
    "France",
    "Germany",
    "Italy",
    "Spain",
    "Poland",
    "Netherlands",
    "Belgium",
    "Sweden",
    "Norway",
    "Finland",
    "Denmark",
    "Switzerland",
    "Austria",
    "Portugal",
    "Greece",
    "Ireland",
    "Czech Republic",
    "Romania",
    "Hungary",
    "Bulgaria",
    "Croatia",
    "Serbia",
    "Slovakia",
    "Slovenia",
    "Lithuania",
    "Latvia",
    "Estonia",
    "Belarus",
    "Moldova",
    "Bosnia and Herzegovina",
    "Albania",
    "North Macedonia",
    "Montenegro",
    "Kosovo",
    "Iceland",
    "Luxembourg",
    "Malta",
    "Cyprus",
    "Georgia",
    "Armenia",
    "Azerbaijan",
}


def generate_map():
    all_items = get_dashboard_data()

    # Only items with a real, plottable region and non-null severity make it onto the map.
    # Travel advisories are deliberately excluded -- the map is for conflicts,
    # geopolitical developments, and security incidents. Travel advisories live
    # exclusively in the dashboard's Travel filter, not on the radar view.
    map_items = []
    for item in all_items:
        if item.get("category") == "travel":
            continue

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
            "confidence_tier": item.get("confidence_tier", "unverified"),
            "confidence_links": item.get("confidence_links", []),
            "title": item.get("title", ""),
            "source": item.get("source", ""),
            "url": item.get("url", "#"),
            "city_name": item.get("city_name"),
            "city_lat": item.get("city_lat"),
            "city_lon": item.get("city_lon"),
            "domain": item.get("domain", "conflict"),
            "event_tags": item.get("event_tags", []),
            "first_seen_at": item.get("first_seen_at"),
            "published_at": item.get("published_at"),
            "sloc_chokepoint_names": (
                [cp["name"] for cp in get_chokepoints_for_region(item.get("region"))]
                if "sloc" in (item.get("event_tags") or []) else []
            ),
        })

    data_json = json.dumps(map_items)
    # Same </script guard as the dashboard generator -- see comment there.
    data_json = data_json.replace("</script", "<\\/script").replace("</SCRIPT", "<\\/SCRIPT")

    chokepoints_json = json.dumps(list(CHOKEPOINTS.values()))
    chokepoints_json = chokepoints_json.replace("</script", "<\\/script").replace("</SCRIPT", "<\\/SCRIPT")

    routes_json = json.dumps(get_all_routes_with_status())
    routes_json = routes_json.replace("</script", "<\\/script").replace("</SCRIPT", "<\\/SCRIPT")

    template = TEMPLATE_PATH.read_text(encoding="utf-8")
    html = template.replace("__DATA_JSON__", data_json)
    html = html.replace("__CHOKEPOINTS_JSON__", chokepoints_json)
    html = html.replace("__ROUTES_JSON__", routes_json)

    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    html = html.replace(
        '<p class="mono" style="font-size:10px;color:var(--text-dim);margin:6px 0 0;" id="genTime"></p>',
        f'<p class="mono" style="font-size:10px;color:var(--text-dim);margin:6px 0 0;">GENERATED {generated_at}</p>'
    )

    MAP_OUTPUT_PATH.write_text(html, encoding="utf-8")
    print(f"  [x] Map updated: {MAP_OUTPUT_PATH} ({len(map_items)} plottable items)")
    return MAP_OUTPUT_PATH
