"""
Real-world maritime chokepoint reference data -- the five most strategically
critical straits/canals controlling global shipping, per US EIA and multiple
maritime trade sources. Used to give the SLOC (Sea Lines of Communication)
tag a genuine geographic basis instead of a crude "is this region near any
ocean" guess, and to show these chokepoints as permanent reference markers
on the map.

Status fields reflect known conditions as of this module's last update --
maritime security conditions change quickly (the Strait of Hormuz has been
disrupted since February 2026 amid the 2026 Iran war; Bab-el-Mandeb has
been under intermittent Houthi blockade since 2023-2025). Treat "status" as
a snapshot to periodically review, not a live feed -- we don't have a
real-time chokepoint status source, this is maintained by hand.
"""

CHOKEPOINTS = {
    "strait_of_hormuz": {
        "name": "Strait of Hormuz",
        "lat": 26.5, "lon": 56.25,
        "connects": "Persian Gulf to Gulf of Oman / Arabian Sea",
        "significance": "~20-25% of world's seaborne oil trade; the single most critical global oil chokepoint",
        "status": "disrupted",
        "status_note": "Closed/contested by Iran since February 2026 amid the 2026 Iran war; US naval blockade and repeated attacks on shipping since",
    },
    "bab_el_mandeb": {
        "name": "Bab-el-Mandeb",
        "lat": 12.5, "lon": 43.3,
        "connects": "Red Sea to Gulf of Aden (Indian Ocean)",
        "significance": "~8.7% of global seaborne trade; critical link between Suez Canal and Indian Ocean",
        "status": "disrupted",
        "status_note": "Under intermittent Houthi (Yemen) blockade/attacks on shipping since 2023, tied to the same regional conflict system as the Iran war",
    },
    "strait_of_malacca": {
        "name": "Strait of Malacca",
        "lat": 2.5, "lon": 101.4,
        "connects": "Indian Ocean to South China Sea / Pacific",
        "significance": "Busiest strait globally by traffic volume; primary Asia-Middle East-Europe corridor",
        "status": "normal",
        "status_note": "No major active disruption, though historically a hotspot for piracy",
    },
    "suez_canal": {
        "name": "Suez Canal",
        "lat": 30.5, "lon": 32.3,
        "connects": "Mediterranean Sea to Red Sea",
        "significance": "~12-15% of global trade; primary Europe-Asia shortcut avoiding the Cape of Good Hope",
        "status": "reduced",
        "status_note": "Traffic significantly depressed since 2024 as ships reroute around Africa to avoid Bab-el-Mandeb/Red Sea risk",
    },
    "turkish_straits": {
        "name": "Turkish Straits (Bosphorus/Dardanelles)",
        "lat": 41.1, "lon": 29.0,
        "connects": "Black Sea to Sea of Marmara / Mediterranean",
        "significance": "Sole sea route for Black Sea grain/energy exports, including Ukraine and Russia",
        "status": "reduced",
        "status_note": "Operating under wartime traffic restrictions and elevated insurance risk tied to the Russia-Ukraine war; Turkey summoned Ukraine's ambassador in August 2026 after Turkish-flagged vessels were struck in the Black Sea",
    },
    "taiwan_strait": {
        "name": "Taiwan Strait",
        "lat": 24.0, "lon": 119.5,
        "connects": "South China Sea to East China Sea, separating Taiwan from mainland China",
        "significance": "Handles 20%+ of global maritime trade by value; carries nearly half the world's container fleet and the bulk of Taiwan's semiconductor exports (TSMC) -- a disruption here threatens chip supply, not oil",
        "status": "reduced",
        "status_note": "PLA aircraft and vessels routinely cross the median line amid ongoing China-Taiwan tension (see Conflict Background) -- not currently blockaded, but under a real, elevated risk premium",
    },
    "danish_straits": {
        "name": "Danish Straits (Great Belt/Øresund)",
        "lat": 55.5, "lon": 11.0,
        "connects": "Baltic Sea to the North Sea, between Denmark and Sweden",
        "significance": "The only maritime exit for all Baltic Sea nations (Russia, Finland, Sweden, Poland, Germany, the Baltic states); carries the bulk of Russia's seaborne Baltic oil exports",
        "status": "reduced",
        "status_note": "Oil volumes ~60% higher than 2021 as Russia reroutes sanctioned Baltic crude to Asian buyers via 'shadow fleet' tankers (~175/month); Denmark expanded port-state inspections and fuel-sulfur monitoring in its 2026 budget in response",
    },
}

# Maps tracked regions to their most relevant chokepoint(s) -- used to give
# the SLOC tag a real geographic basis instead of a vague "sounds maritime"
# guess. A region can map to more than one if it has coastline on multiple
# critical waterways.
REGION_TO_CHOKEPOINTS = {
    "Iran": ["strait_of_hormuz"],
    "Yemen": ["bab_el_mandeb"],
    "Saudi Arabia": ["strait_of_hormuz", "bab_el_mandeb"],
    "Qatar": ["strait_of_hormuz"],
    "Middle East": ["suez_canal", "bab_el_mandeb"],
    "South China Sea": ["strait_of_malacca"],
    "Southeast Asia": ["strait_of_malacca"],
    "Vietnam": ["strait_of_malacca"],
    "Thailand": ["strait_of_malacca"],
    "Russia": ["turkish_straits", "danish_straits"],
    "Ukraine": ["turkish_straits"],
    "Europe": ["turkish_straits", "suez_canal", "danish_straits"],
    "Taiwan": ["taiwan_strait"],
    "China": ["taiwan_strait"],
}


def get_chokepoints_for_region(region: str) -> list[dict]:
    """Returns the chokepoint dict(s) associated with a region, or [] if none."""
    keys = REGION_TO_CHOKEPOINTS.get(region, [])
    return [CHOKEPOINTS[k] for k in keys]


def region_has_chokepoint(region: str) -> bool:
    return region in REGION_TO_CHOKEPOINTS
