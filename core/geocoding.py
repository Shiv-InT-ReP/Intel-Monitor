"""
City/place-level location extraction for the map, using spaCy's free local
NER model plus OpenStreetMap's free Nominatim geocoding service.

Two-step process:
1. spaCy extracts candidate place names (GPE/LOC entities) from an item's
   title. We filter out anything matching our already-tracked country/region
   list (Pakistan, India, etc.) -- we already have those, we want the CITY.
2. The remaining candidate (if any) gets geocoded via Nominatim to get real
   lat/lon coordinates.

Honest limitation: spaCy's small English model is good but not perfect --
it will miss some cities, especially in complex sentences, and Nominatim
occasionally can't resolve ambiguous or very small place names. When either
step fails, the caller should fall back to the country-centroid pin (the
map already does this) rather than showing nothing.

Rate limiting: Nominatim's usage policy requires max 1 request/second and a
descriptive User-Agent identifying the application. We only geocode NEWLY
matched items each run (typically single digits to low tens), so this is
comfortably within the free tier.
"""
import time

import requests
import spacy

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
USER_AGENT = "IntelMonitor-PersonalOSINTTool/1.0 (github.com/Shiv-InT-ReP/Intel-Monitor)"
GEOCODE_DELAY_SECONDS = 1.0  # respects Nominatim's 1 req/sec policy

_nlp = None


def _get_nlp():
    """Lazy-load the spaCy model once, not on every call."""
    global _nlp
    if _nlp is None:
        _nlp = spacy.load("en_core_web_sm")
    return _nlp


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


def geocode_place(place_name: str) -> tuple[float, float] | None:
    """Returns (lat, lon) for a place name via Nominatim, or None if it can't be resolved."""
    try:
        resp = requests.get(
            NOMINATIM_URL,
            params={"q": place_name, "format": "json", "limit": 1},
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


def enrich_item_with_city(item: dict, known_regions: list[str]) -> dict:
    """
    Attempts to find and geocode a specific city/place for this item.
    Mutates and returns the item with 'city_name', 'city_lat', 'city_lon'
    added if successful. Leaves them unset (falls back to country centroid
    on the map) if extraction or geocoding fails at any step -- this
    function is designed to never raise, only enrich when it can.
    """
    text = item.get("title", "")
    candidates = extract_place_candidates(text, known_regions)

    for candidate in candidates:
        coords = geocode_place(candidate)
        time.sleep(GEOCODE_DELAY_SECONDS)  # rate limit compliance
        if coords:
            item["city_name"] = candidate
            item["city_lat"], item["city_lon"] = coords
            return item

    return item  # no city found/geocoded -- caller falls back to country centroid
