"""
USGS earthquake collector -- pulls real-time earthquake data directly from
USGS's official GeoJSON feed. Free, no API key, no signup.

Unlike our RSS/Telegram sources, this gives EXACT coordinates and magnitude
per event -- no text extraction or geocoding guesswork needed. Every event
here is inherently precise, real data (like ACLED, if that had worked out).

We filter by magnitude to avoid flooding with minor tremors that happen
constantly worldwide -- only magnitude 4.5+ is included by default (roughly
"felt by people, could cause minor damage" and up), configurable.

Feed docs: https://earthquake.usgs.gov/earthquakes/feed/v1.0/
"""
import hashlib
from datetime import datetime, timezone

import requests

FEED_URL = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/{magnitude}_{period}.geojson"


def _make_item_id(event_id: str) -> str:
    return hashlib.sha256(f"usgs|{event_id}".encode()).hexdigest()


def collect(usgs_config: dict) -> list[dict]:
    if not usgs_config.get("enabled"):
        return []

    magnitude = usgs_config.get("min_magnitude", "4.5")  # "significant", "4.5", "2.5", "1.0", "all"
    period = usgs_config.get("period", "day")  # "hour", "day", "week", "month"

    url = FEED_URL.format(magnitude=magnitude, period=period)

    try:
        resp = requests.get(url, timeout=15)
        resp.raise_for_status()
        payload = resp.json()
    except Exception as e:
        print(f"  [!] USGS earthquake feed request failed: {e}")
        return []

    items = []
    for feature in payload.get("features", []):
        props = feature.get("properties", {})
        geom = feature.get("geometry", {})
        coords = geom.get("coordinates", [None, None, None])  # [lon, lat, depth]
        if coords[0] is None or coords[1] is None:
            continue

        mag = props.get("mag")
        place = props.get("place", "Unknown location")
        event_time_ms = props.get("time")
        event_time_iso = (
            datetime.fromtimestamp(event_time_ms / 1000, tz=timezone.utc).isoformat()
            if event_time_ms else None
        )
        event_id = feature.get("id", "")
        tsunami_flag = props.get("tsunami", 0)

        title = f"M{mag} earthquake — {place}"
        if tsunami_flag:
            title += " (tsunami warning issued)"

        items.append({
            "item_id": _make_item_id(event_id),
            "source": "usgs",
            "title": title,
            "url": props.get("url", "https://earthquake.usgs.gov"),
            "published_at": event_time_iso,
            "fetched_at": datetime.now(timezone.utc).isoformat(),
            "_usgs_magnitude": mag,
            "_usgs_place": place,
            "_usgs_lat": coords[1],
            "_usgs_lon": coords[0],
            "_usgs_tsunami": bool(tsunami_flag),
        })

    return items
