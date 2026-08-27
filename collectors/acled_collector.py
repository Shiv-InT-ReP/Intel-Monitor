"""
ACLED collector -- pulls verified political violence/conflict event data
for the countries in your regions list.

Unlike the RSS/Telegram sources, ACLED data is already human-verified and
structured (not raw text needing keyword matching), so every event that
passes our event-type/fatality filter is treated as inherently relevant --
no separate keyword matching step needed for this source.

Auth: ACLED uses OAuth (email + password -> temporary bearer token), not a
static API key. We fetch a fresh token each run rather than caching it,
since a token request is cheap and this pipeline only runs a few times a
day -- not worth the complexity of persisting/refreshing tokens.

Countries: only regions that are actual ACLED-recognized country names are
queried (broad terms like "APAC" or "Middle East" are skipped -- ACLED's
API filters on exact country name matches).
"""
import hashlib
from datetime import datetime, timezone, timedelta

import requests

TOKEN_URL = "https://acleddata.com/oauth/token"
API_URL = "https://acleddata.com/api/acled/read"

# Only include event types that represent actual violence/serious unrest --
# excludes routine "Peaceful protest" sub-events, which would otherwise
# flood the pipeline (ACLED logs thousands of protests globally per week).
RELEVANT_EVENT_TYPES = {
    "Battles",
    "Violence against civilians",
    "Explosions/Remote violence",
    "Riots",
}

# Countries we ask ACLED about -- intersected against your config's region
# list at runtime, so this only needs to list what ACLED actually recognizes
# as a country name. Broad/non-country regions (APAC, Middle East, South
# Asia, etc.) are intentionally left out here.
ACLED_COUNTRIES = {
    "China", "Iran", "Israel", "Ukraine", "Russia", "India", "Pakistan",
    "Afghanistan", "Bangladesh", "Nepal", "Sri Lanka", "Myanmar",
    "Cambodia", "Vietnam", "Thailand", "Taiwan",
}


def _make_item_id(event_id: str) -> str:
    return hashlib.sha256(f"acled|{event_id}".encode()).hexdigest()


def _get_access_token(email: str, password: str) -> str:
    resp = requests.post(
        TOKEN_URL,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data={
            "username": email,
            "password": password,
            "grant_type": "password",
            "client_id": "acled",
            "scope": "authenticated",
        },
        timeout=15,
    )
    resp.raise_for_status()
    return resp.json()["access_token"]


def collect(acled_config: dict, regions: list[str], lookback_days: int = 7) -> list[dict]:
    if not acled_config.get("enabled"):
        return []

    countries_to_query = [r for r in regions if r in ACLED_COUNTRIES]
    if not countries_to_query:
        return []

    try:
        token = _get_access_token(acled_config["email"], acled_config["password"])
    except Exception as e:
        print(f"  [!] ACLED auth failed: {e}")
        return []

    country_filter = ":OR:country=".join(countries_to_query)
    start_date = (datetime.now(timezone.utc) - timedelta(days=lookback_days)).strftime("%Y-%m-%d")
    end_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    params = {
        "_format": "json",
        "country": country_filter,
        "event_date": f"{start_date}|{end_date}",
        "event_date_where": "BETWEEN",
        "limit": 500,
    }

    try:
        resp = requests.get(
            API_URL,
            params=params,
            headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
            timeout=30,
        )
        resp.raise_for_status()
        payload = resp.json()
    except Exception as e:
        print(f"  [!] ACLED data request failed: {e}")
        return []

    rows = payload.get("data", [])
    items = []
    for row in rows:
        event_type = row.get("event_type", "")
        fatalities = int(row.get("fatalities", 0) or 0)

        # Skip routine/low-signal events -- keep only serious event types,
        # OR any event with fatalities regardless of type (a "Riot" with
        # deaths is more significant than the type label alone suggests).
        if event_type not in RELEVANT_EVENT_TYPES and fatalities == 0:
            continue

        country = row.get("country", "")
        location = row.get("location", "")
        actor1 = row.get("actor1", "")
        event_id = row.get("event_id_cnty", "")

        title = f"{event_type}: {actor1} — {location}, {country}"
        if fatalities > 0:
            title += f" ({fatalities} fatalities)"

        items.append({
            "item_id": _make_item_id(event_id),
            "source": "acled",
            "title": title,
            "url": "https://acleddata.com/explorer",
            "published_at": row.get("event_date"),
            "text_for_matching": title,
            "fetched_at": datetime.now(timezone.utc).isoformat(),
            "_acled_country": country,
            "_acled_event_type": event_type,
            "_acled_fatalities": fatalities,
        })

    return items