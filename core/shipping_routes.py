"""
Major shipping route reference data -- simplified waypoint paths for the
sea lines of communication connecting Europe, the Middle East, Russia, and
APAC. These are schematic (not precise nautical charts), following the
real general path of each route while staying simple enough to render
cleanly on the map. Waypoint density was increased for smoother, more
natural-looking curves that avoid obviously cutting across landmasses.

Each route's status is DERIVED from the chokepoint(s) it passes through
(see chokepoints.py) -- a route is only as "clear" as the most disrupted
chokepoint along it. This keeps status in one place rather than needing
separate manual updates for routes and chokepoints.
"""
from core.chokepoints import CHOKEPOINTS

SHIPPING_ROUTES = {
    "suez_corridor": {
        "name": "Suez Corridor (Asia-Europe, primary)",
        "connects": "East/South Asia to Europe via the Red Sea and Suez Canal",
        "chokepoints": ["bab_el_mandeb", "suez_canal"],
        "waypoints": [
            [1.3, 103.8], [2.5, 98.0], [4.5, 92.0], [6.0, 85.0], [6.5, 78.0],
            [8.0, 68.0], [10.5, 58.0], [12.0, 50.0], [12.5, 45.5], [12.5, 43.3],
            [15.5, 41.5], [19.0, 39.0], [24.0, 36.5], [27.5, 34.0], [29.2, 32.6],
            [30.5, 32.3], [31.5, 32.0], [33.5, 28.5], [35.0, 22.0], [36.5, 14.0],
            [37.5, 5.0], [36.0, -5.4], [43.0, -8.5], [48.5, -5.0], [51.0, -1.0],
            [51.9, 4.0],
        ],
    },

    "cape_of_good_hope": {
        "name": "Cape of Good Hope (Asia-Europe alternate)",
        "connects": "East/South Asia to Europe, bypassing the Red Sea -- the route ships increasingly use when Bab-el-Mandeb is too risky",
        "chokepoints": [],  # deliberately not tied to any chokepoint -- that's the whole point of this route
        "waypoints": [
            [1.3, 103.8], [-3.0, 92.0], [-8.0, 82.0], [-12.0, 70.0], [-16.0, 58.0],
            [-20.0, 48.0], [-25.0, 40.0], [-29.5, 32.0], [-33.0, 26.0], [-34.4, 18.5],
            [-32.0, 14.0], [-25.0, 8.0], [-15.0, 2.0], [-5.0, -8.0], [8.0, -16.0],
            [20.0, -18.0], [30.0, -14.0], [36.0, -10.0], [44.0, -6.0], [48.5, -5.0],
            [51.9, 4.0],
        ],
    },

    "hormuz_to_asia": {
        "name": "Persian Gulf Oil Corridor",
        "connects": "Gulf oil exports (Iran, Saudi Arabia, Qatar, UAE) to South/East Asian markets via the Strait of Hormuz",
        "chokepoints": ["strait_of_hormuz"],
        "waypoints": [
            [26.5, 56.25], [24.5, 59.0], [22.0, 62.0], [18.0, 66.0], [14.0, 70.0],
            [10.0, 75.0], [6.0, 82.0], [3.0, 90.0], [1.3, 103.8],
        ],
    },

    "turkish_straits_corridor": {
        "name": "Black Sea Corridor (Russia/Ukraine grain & energy)",
        "connects": "Russian and Ukrainian Black Sea ports to the Mediterranean and global markets via the Turkish Straits",
        "chokepoints": ["turkish_straits"],
        "waypoints": [
            [44.7, 37.8], [44.0, 35.5], [43.0, 33.0], [42.0, 30.5], [41.1, 29.0],
            [40.2, 27.0], [39.0, 26.0], [37.5, 24.5], [35.5, 23.0], [37.0, 15.0],
        ],
    },

    "malacca_corridor": {
        "name": "Strait of Malacca Corridor (core APAC artery)",
        "connects": "Indian Ocean trade (including Gulf oil) to East Asia -- the busiest strait in the world by traffic",
        "chokepoints": ["strait_of_malacca"],
        "waypoints": [
            [10.0, 75.0], [7.0, 82.0], [5.5, 90.0], [5.5, 95.0], [3.5, 99.0],
            [2.5, 101.4], [1.3, 103.8], [3.0, 106.0], [7.0, 109.0], [10.0, 112.0],
            [15.0, 113.5], [22.3, 114.2],
        ],
    },

    "taiwan_strait_corridor": {
        "name": "Taiwan Strait Corridor (East Asia manufacturing artery)",
        "connects": "South China Sea to East China Sea -- carries 20%+ of global maritime trade by value, including the bulk of the world's advanced semiconductor exports",
        "chokepoints": ["taiwan_strait"],
        "waypoints": [
            [22.3, 114.2], [22.5, 116.0], [23.0, 117.5], [24.0, 119.5],
            [25.0, 121.0], [26.5, 122.0], [29.0, 123.0], [31.5, 122.5],
        ],
    },

    "baltic_danish_straits_corridor": {
        "name": "Baltic Corridor (Danish Straits)",
        "connects": "The only maritime exit for all Baltic Sea nations (Russia, Finland, Sweden, Poland, Germany, the Baltic states) -- carries the bulk of Russia's seaborne Baltic oil exports",
        "chokepoints": ["danish_straits"],
        "waypoints": [
            [59.9, 30.3],   # St. Petersburg, Russia
            [59.5, 24.5], [58.5, 20.0], [57.0, 16.0], [56.0, 12.5],
            [55.5, 11.0], [55.0, 10.0], [56.5, 8.0], [57.5, 6.0],
            [58.0, 4.0], [58.5, 0.0],
        ],
    },
}


def _route_status(route: dict) -> dict:
    """
    Derives a route's status from the worst status among the chokepoints
    it passes through. A route with no chokepoint dependency (like the
    Cape of Good Hope bypass) is always "normal" by definition.
    """
    status_severity = {"normal": 0, "reduced": 1, "disrupted": 2}
    worst_status = "normal"
    worst_notes = []

    for cp_key in route["chokepoints"]:
        cp = CHOKEPOINTS.get(cp_key)
        if not cp:
            continue
        if status_severity[cp["status"]] > status_severity[worst_status]:
            worst_status = cp["status"]
        if cp["status"] != "normal":
            worst_notes.append(f"{cp['name']}: {cp['status_note']}")

    return {"status": worst_status, "status_notes": worst_notes}


def get_all_routes_with_status() -> list[dict]:
    """Returns every route enriched with its derived status, ready for the map."""
    routes = []
    for key, route in SHIPPING_ROUTES.items():
        enriched = dict(route)
        enriched["key"] = key
        enriched.update(_route_status(route))
        routes.append(enriched)
    return routes
