"""
City/place-level location extraction for the map, using spaCy's free local
NER model plus OpenStreetMap's free Nominatim geocoding service.

Two-step process:
1. spaCy extracts candidate place names (GPE/LOC entities) from an item's
   title. We filter out anything matching our already-tracked country/region
   list (Pakistan, India, etc.) -- we already have those, we want the CITY.
2. The remaining candidate (if any) gets geocoded via Nominatim to get real
   lat/lon coordinates.

CRITICAL SAFETY CHECK: Nominatim's search is completely global and
unscoped. If spaCy ever extracts an ambiguous word (a name, an acronym,
anything that happens to coincide with a small town name anywhere in the
world), Nominatim can return a real result on the opposite side of the
planet from where the story is actually about -- e.g. a Russia/Ukraine
story getting geocoded to a barangay in the Philippines because some
extracted word happened to match a place name there. We validate every
geocoded result against the item's own known region's approximate
location, and reject (fall back to the safe region-centroid pin) if the
result is absurdly far away.

Honest limitation: spaCy's small English model is good but not perfect --
it will miss some cities, especially in complex sentences, and Nominatim
occasionally can't resolve ambiguous or very small place names. When
either step fails, the caller should fall back to the country-centroid
pin (the map already does this) rather than showing nothing.

Rate limiting: Nominatim's usage policy requires max 1 request/second and a
descriptive User-Agent identifying the application. We only geocode NEWLY
matched items each run (typically single digits to low tens), so this is
comfortably within the free tier.
"""
import math
import time

import requests
import spacy

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
USER_AGENT = "IntelMonitor-PersonalOSINTTool/1.0 (github.com/Shiv-InT-ReP/Intel-Monitor)"
GEOCODE_DELAY_SECONDS = 1.0  # respects Nominatim's 1 req/sec policy

# Same centroids used by the map's JS REGION_COORDS -- kept here too so we
# can sanity-check geocoded results against the region the story is
# actually about. If a "city" geocodes more than MAX_PLAUSIBLE_DISTANCE_KM
# from its own region's centroid, it's almost certainly a bad match
# (ambiguous extraction + global unscoped search), not a real location.
REGION_CENTROIDS = {
    "Taiwan": (23.7, 121.0), "China": (35.0, 105.0), "Iran": (32.4, 53.7),
    "Israel": (31.0, 34.8), "Ukraine": (48.4, 31.2), "Russia": (61.5, 105.3),
    "India": (20.6, 79.0), "Pakistan": (30.4, 69.3), "Afghanistan": (33.9, 67.7),
    "Bangladesh": (23.7, 90.4), "Nepal": (28.4, 84.1), "Sri Lanka": (7.9, 80.7),
    "Myanmar": (21.9, 95.9), "Burma": (21.9, 95.9), "Cambodia": (12.6, 104.9),
    "Vietnam": (14.1, 108.3), "Thailand": (15.9, 100.9), "Middle East": (33.3, 44.4),
    "Europe": (50.1, 10.4), "South China Sea": (12.0, 114.0),
    "Kashmir": (34.0, 76.5), "PoK": (34.4, 73.5), "Saudi Arabia": (24.0, 45.0),
    "Yemen": (15.5, 47.5), "Qatar": (25.3, 51.2),
    "Japan": (36.2, 138.3), "South Korea": (35.9, 127.8), "North Korea": (40.3, 127.5), "Australia": (-25.3, 133.8), "New Zealand": (-40.9, 174.9), "Indonesia": (-0.8, 113.9), "Malaysia": (4.2, 101.9), "Singapore": (1.35, 103.8), "Philippines": (12.9, 121.8), "Papua New Guinea": (-6.3, 143.9), "Mongolia": (46.9, 103.8), "Laos": (19.9, 102.6), "Brunei": (4.5, 114.7), "Timor-Leste": (-8.9, 125.7), "Iraq": (33.2, 43.7), "Syria": (34.8, 39.0), "Lebanon": (33.9, 35.9), "Jordan": (31.2, 36.5), "Kuwait": (29.3, 47.5), "United Arab Emirates": (23.4, 53.8), "Bahrain": (26.0, 50.6), "Oman": (21.5, 55.9), "Turkey": (38.9, 35.2), "Egypt": (26.8, 30.8), "United Kingdom": (55.4, -3.4), "France": (46.6, 2.2), "Germany": (51.2, 10.4), "Italy": (41.9, 12.6), "Spain": (40.5, -3.7), "Poland": (51.9, 19.1), "Netherlands": (52.1, 5.3), "Belgium": (50.5, 4.5), "Sweden": (60.1, 18.6), "Norway": (60.5, 8.5), "Finland": (61.9, 25.7), "Denmark": (56.3, 9.5), "Switzerland": (46.8, 8.2), "Austria": (47.5, 14.6), "Portugal": (39.4, -8.2), "Greece": (39.1, 21.8), "Ireland": (53.4, -8.2), "Czech Republic": (49.8, 15.5), "Romania": (45.9, 25.0), "Hungary": (47.2, 19.5), "Bulgaria": (42.7, 25.5), "Croatia": (45.1, 15.2), "Serbia": (44.0, 21.0), "Slovakia": (48.7, 19.7), "Slovenia": (46.2, 15.0), "Lithuania": (55.2, 23.9), "Latvia": (56.9, 24.6), "Estonia": (58.6, 25.0), "Belarus": (53.7, 27.9), "Moldova": (47.4, 28.4), "Bosnia and Herzegovina": (43.9, 17.7), "Albania": (41.2, 20.2), "North Macedonia": (41.6, 21.7), "Montenegro": (42.7, 19.4), "Kosovo": (42.6, 20.9), "Iceland": (64.9, -19.0), "Luxembourg": (49.8, 6.1), "Malta": (35.9, 14.4), "Cyprus": (35.1, 33.4), "Georgia": (42.3, 43.4), "Armenia": (40.1, 45.0), "Azerbaijan": (40.1, 47.6),
}

# Region-size-tiered plausibility thresholds. A flat 2500km threshold sized
# for Russia was far too permissive for tiny countries -- Qatar is only
# ~160km across, so a "city" 2000km away could pass as plausible under a
# one-size-fits-all threshold. Each region gets a threshold roughly matching
# its own real-world geographic extent instead.
REGION_SIZE_TIER = {}
for _r in ["Bahrain", "Brunei", "Cyprus", "Kosovo", "Kuwait", "Luxembourg", "Malta", "Montenegro", "Qatar", "Singapore", "Timor-Leste"]:
    REGION_SIZE_TIER[_r] = "tiny"
for _r in ["Albania", "Armenia", "Austria", "Azerbaijan", "Belgium", "Bosnia and Herzegovina", "Bulgaria", "Cambodia", "Croatia", "Czech Republic", "Denmark", "Estonia", "Georgia", "Greece", "Hungary", "Iceland", "Ireland", "Israel", "Jordan", "Kashmir", "Laos", "Latvia", "Lebanon", "Lithuania", "Moldova", "Nepal", "Netherlands", "North Korea", "North Macedonia", "PoK", "Portugal", "Serbia", "Slovakia", "Slovenia", "South Korea", "Sri Lanka", "Switzerland", "Taiwan", "United Arab Emirates"]:
    REGION_SIZE_TIER[_r] = "small"
for _r in ["Afghanistan", "Bangladesh", "Burma", "Finland", "Germany", "Iraq", "Italy", "Japan", "Malaysia", "Myanmar", "Nepal", "New Zealand", "Norway", "Pakistan", "Philippines", "Poland", "Romania", "Sweden", "Syria", "Thailand", "Turkey", "United Kingdom", "Vietnam", "Yemen"]:
    REGION_SIZE_TIER[_r] = "medium"
for _r in ["Egypt", "Europe", "India", "Indonesia", "Iran", "Middle East", "Mongolia", "Saudi Arabia", "South China Sea"]:
    REGION_SIZE_TIER[_r] = "large"
# Anything not listed defaults to "huge" (Russia, China, Australia, etc. --
# the true giants the original flat threshold was sized for).

TIER_DISTANCES_KM = {"tiny": 300, "small": 650, "medium": 1200, "large": 2000, "huge": 2500}


def _max_plausible_distance_for(region: str) -> int:
    tier = REGION_SIZE_TIER.get(region, "huge")
    return TIER_DISTANCES_KM[tier]

_nlp = None


def _get_nlp():
    """Lazy-load the spaCy model once, not on every call."""
    global _nlp
    if _nlp is None:
        _nlp = spacy.load("en_core_web_sm")
    return _nlp


def haversine_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Great-circle distance between two lat/lon points, in kilometers."""
    R = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return 2 * R * math.asin(math.sqrt(a))


def is_plausible_for_region(lat: float, lon: float, region: str) -> bool:
    """
    True if the given coordinates are within a plausible distance of the
    named region's centroid. Returns True (permissive) if we don't have a
    centroid for this region at all, since we can't validate what we don't
    have a reference point for -- better to allow than to silently discard
    with no real check performed. The threshold itself is sized to the
    region's real-world geographic extent (see _max_plausible_distance_for).
    """
    centroid = REGION_CENTROIDS.get(region)
    if not centroid:
        return True
    distance = haversine_distance_km(lat, lon, centroid[0], centroid[1])
    return distance <= _max_plausible_distance_for(region)


def extract_place_candidates(text: str, known_regions: list[str]) -> list[str]:
    """
    Returns candidate place names from the text, excluding anything that
    matches an already-tracked region/country name (we already have that
    handled -- we want the more specific city/place, if any).
    """
    if not text:
        return []

    known_lower = {r.lower() for r in known_regions}
    nlp = _get_nlp()
    doc = nlp(text)

    candidates = []
    for ent in doc.ents:
        if ent.label_ not in ("GPE", "LOC"):
            continue
        if ent.text.lower() in known_lower:
            continue
        candidates.append(ent.text)

    return candidates


def geocode_place(place_name: str, bias_region: str = None) -> tuple[float, float] | None:
    """
    Returns (lat, lon) for a place name via Nominatim, or None if it can't
    be resolved. When bias_region is given, biases the search toward that
    region's known centroid using a wide viewbox -- a SOFT preference
    (bounded=0), not a hard filter, so a genuinely correct but distant match
    (e.g. a real city in a huge country) still isn't excluded. This exists
    specifically to stop ambiguous same-named places (e.g. Moscow, Russia
    vs. Moscow, Idaho) from resolving to the wrong one when Nominatim's own
    unscoped global ranking doesn't happen to favor the expected place.
    """
    params = {"q": place_name, "format": "json", "limit": 1}

    centroid = REGION_CENTROIDS.get(bias_region) if bias_region else None
    if centroid:
        lat, lon = centroid
        # A generous ~15-degree box around the region's centroid -- wide
        # enough to still find real cities well within a large country,
        # narrow enough to meaningfully favor the right same-named place.
        params["viewbox"] = f"{lon - 15},{lat + 15},{lon + 15},{lat - 15}"
        params["bounded"] = 0  # preference, not a hard restriction

    try:
        resp = requests.get(
            NOMINATIM_URL,
            params=params,
            headers={"User-Agent": USER_AGENT},
            timeout=10,
        )
        resp.raise_for_status()
        results = resp.json()
        if not results:
            return None
        return float(results[0]["lat"]), float(results[0]["lon"])
    except Exception as e:
        print(f"  [!] Geocoding failed for '{place_name}': {e}")
        return None


def enrich_item_with_city(item: dict, known_regions: list[str], primary_region: str = None,
                           all_matched_regions: list[str] = None) -> dict:
    """
    Attempts to find and geocode a specific city/place for this item.
    Mutates and returns the item with 'city_name', 'city_lat', 'city_lon'
    added if successful. Leaves them unset (falls back to country centroid
    on the map) if extraction, geocoding, OR the plausibility check fails --
    this function is designed to never raise, and never plot a wildly wrong
    location, only enrich when it can do so safely.

    When a story matches MULTIPLE regions (all_matched_regions), a city that
    doesn't fit the arbitrarily-first "primary" region might still
    genuinely belong to one of the OTHER regions the story also mentioned
    -- e.g. a story about "China" and "Sydney" where Sydney is a real,
    correct match for Australia, not China. Each candidate is checked
    against every matched region in turn, using whichever one it's
    actually plausible for, rather than only ever checking against the
    single first-matched region and discarding otherwise-valid matches.
    """
    text = item.get("title", "")
    candidates = extract_place_candidates(text, known_regions)

    regions_to_try = all_matched_regions or ([primary_region] if primary_region else [])
    # Try primary_region first (most likely correct), then any others.
    if primary_region and primary_region in regions_to_try:
        regions_to_try = [primary_region] + [r for r in regions_to_try if r != primary_region]

    for candidate in candidates:
        coords = geocode_place(candidate, bias_region=primary_region)
        time.sleep(GEOCODE_DELAY_SECONDS)  # rate limit compliance
        if not coords:
            continue

        if not regions_to_try:
            item["city_name"] = candidate
            item["city_lat"], item["city_lon"] = coords
            return item

        matched_region = next(
            (r for r in regions_to_try if is_plausible_for_region(coords[0], coords[1], r)),
            None
        )
        if matched_region is None:
            print(f"  [!] Rejected geocoding: '{candidate}' resolved to a location implausibly "
                  f"far from {regions_to_try} -- falling back to region centroid instead.")
            continue

        item["city_name"] = candidate
        item["city_lat"], item["city_lon"] = coords
        return item

    return item  # no city found/geocoded/plausible -- caller falls back to country centroid
