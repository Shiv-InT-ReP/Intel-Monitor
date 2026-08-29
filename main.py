"""
Intel Monitor — orchestrator.

Pulls from RSS, Reddit, and Telegram (whichever are enabled in config.json),
dedupes against SQLite history, matches against your keyword/region list,
and emails you a two-section digest: geopolitical/security alerts (strict
region+keyword matching) and travel advisories (region-only matching,
since travel advisory feeds are already inherently travel-risk content).

Run manually:      python main.py
Schedule (Windows): see README.md for a Task Scheduler snippet, same
                     pattern as your price tracker.
"""
import json
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from core.db import init_db, is_seen, mark_seen, get_recent_items_for_confidence_scoring, update_confidence_bulk, get_prior_related_count, get_items_needing_verification, apply_gdelt_verification
from core.matcher import get_matcher, build_region_only_matcher
from core import severity, confidence, ai_dedup, geocoding
from collectors import rss_collector, reddit_collector, telegram_collector, acled_collector, usgs_collector, gdelt_collector
from notifier import email_notifier
from dashboard.dashboard_generator import generate_dashboard
from dashboard.map_generator import generate_map

CONFIG_PATH = Path(__file__).resolve().parent / "config.json"


def load_config() -> dict:
    return json.loads(CONFIG_PATH.read_text())


def _process_items(items: list[dict], matcher, category: str, regions: list[str], geocoding_enabled: bool = False) -> list[dict]:
    """Dedupe + match + score a batch of items. Returns only new, matched items."""
    matched = []
    for item in items:
        if is_seen(item["item_id"]):
            continue

        hits = matcher(item["text_for_matching"])
        item["matched_keywords"] = hits

        if hits:
            # Separate which hits were REGION terms vs ESCALATION keyword terms,
            # so we can plot by region and score by keyword severity separately.
            region_hits = [h for h in hits if h in regions]
            keyword_hits = [h for h in hits if h not in regions]
            primary_region = region_hits[0] if region_hits else None

            if category == "travel":
                score, tier = severity.score_travel(item["text_for_matching"])
            else:
                score, tier = severity.score_geopolitical(keyword_hits)

            # City-level geocoding, geopolitical items only -- the map excludes
            # travel advisories entirely, so there's no point geocoding those.
            city_name = city_lat = city_lon = None
            if geocoding_enabled and category != "travel":
                enriched = geocoding.enrich_item_with_city(item, regions)
                city_name = enriched.get("city_name")
                city_lat = enriched.get("city_lat")
                city_lon = enriched.get("city_lon")

            domain = severity.classify_domain(hits) if category != "travel" else "conflict"

            matched.append(item)
            item["region"] = primary_region  # attach for reuse by AI dedup clustering
            item["severity_tier"] = tier
            mark_seen(item, notified=True, category=category,
                      severity_tier=tier, severity_score=score, region=primary_region,
                      city_name=city_name, city_lat=city_lat, city_lon=city_lon, domain=domain)
        else:
            mark_seen(item, notified=False, category=category)  # record so we never re-check it
    return matched


def run():
    print(f"=== Intel Monitor run started {datetime.now().isoformat()} ===")
    config = load_config()
    init_db()

    geo_matcher = get_matcher(config)
    travel_matcher = build_region_only_matcher(
        regions=config["regions"],
        case_sensitive=config.get("case_sensitive", False),
    )
    print(f"[*] Match mode: {config.get('match_mode', 'strict')} (geopolitical) / region-only (travel advisories)")

    # --- Geopolitical / security sources ---
    geo_items = []
    print("[*] Fetching RSS feeds...")
    geo_items += rss_collector.collect(config["rss_feeds"])

    print("[*] Fetching Reddit...")
    geo_items += reddit_collector.collect(config["reddit"])

    print("[*] Fetching Telegram...")
    geo_items += telegram_collector.collect(
        config["telegram"], lookback_hours=config.get("lookback_hours_first_run", 24)
    )

    print(f"[*] Fetched {len(geo_items)} total geopolitical items.")
    new_geo_matches = _process_items(geo_items, geo_matcher, category="geopolitical", regions=config["regions"],
                                      geocoding_enabled=config.get("geocoding", {}).get("enabled", False))
    print(f"[*] {len(new_geo_matches)} new geopolitical item(s) matched.")

    # --- Travel advisory sources (separate feed list, separate matcher) ---
    new_travel_matches = []
    travel_feeds = config.get("travel_advisory_feeds", [])
    if travel_feeds:
        print("[*] Fetching travel advisory feeds...")
        travel_items = rss_collector.collect(travel_feeds)
        print(f"[*] Fetched {len(travel_items)} total travel advisory items.")
        new_travel_matches = _process_items(travel_items, travel_matcher, category="travel", regions=config["regions"])
        print(f"[*] {len(new_travel_matches)} new travel advisory item(s) matched.")

    # --- ACLED verified conflict data (already-structured, no keyword matching needed) ---
    new_acled_matches = []
    if config.get("acled", {}).get("enabled"):
        print("[*] Fetching ACLED conflict data...")
        acled_items = acled_collector.collect(
            config["acled"], regions=config["regions"],
            lookback_days=config["acled"].get("lookback_days", 7)
        )
        print(f"[*] Fetched {len(acled_items)} total ACLED event(s) (after event-type/fatality filtering).")
        for item in acled_items:
            if is_seen(item["item_id"]):
                continue
            score, tier = severity.score_acled(item["_acled_event_type"], item["_acled_fatalities"])
            item["matched_keywords"] = [item["_acled_country"], item["_acled_event_type"]]
            item["region"] = item["_acled_country"]  # attach for reuse by AI dedup clustering
            item["severity_tier"] = tier
            mark_seen(item, notified=True, category="geopolitical",
                      severity_tier=tier, severity_score=score, region=item["_acled_country"])
            new_acled_matches.append(item)
        print(f"[*] {len(new_acled_matches)} new ACLED event(s) added.")

    # --- USGS earthquakes (free, precise, no keyword matching needed) ---
    new_usgs_matches = []
    usgs_config = config.get("usgs", {})
    if usgs_config.get("enabled"):
        print("[*] Fetching USGS earthquake data...")
        usgs_items = usgs_collector.collect(usgs_config)
        print(f"[*] Fetched {len(usgs_items)} total USGS earthquake event(s).")

        # Filter to events near a region you actually track -- USGS is global,
        # and most earthquakes worldwide aren't relevant to your monitoring scope.
        for item in usgs_items:
            if is_seen(item["item_id"]):
                continue
            place_text = item["_usgs_place"].lower()
            matched_region = next((r for r in config["regions"] if r.lower() in place_text), None)
            if not matched_region:
                continue

            score, tier = severity.score_usgs(item["_usgs_magnitude"], item["_usgs_tsunami"])
            item["matched_keywords"] = [matched_region, "earthquake"]
            item["region"] = matched_region
            item["severity_tier"] = tier
            mark_seen(item, notified=True, category="geopolitical",
                      severity_tier=tier, severity_score=score, region=matched_region,
                      city_name=item["_usgs_place"], city_lat=item["_usgs_lat"], city_lon=item["_usgs_lon"], domain="disaster")
            new_usgs_matches.append(item)
        print(f"[*] {len(new_usgs_matches)} new USGS earthquake event(s) near tracked regions.")

    # --- Notify ---
    if new_geo_matches or new_travel_matches or new_acled_matches or new_usgs_matches:
        combined_geo = new_geo_matches + new_acled_matches + new_usgs_matches

        ai_config = config.get("ai_dedup", {})
        if ai_config.get("enabled"):
            print("[*] Running AI dedup/synthesis on clustered stories...")
            before_count = len(combined_geo)
            combined_geo = ai_dedup.dedupe_and_synthesize(
                combined_geo, ai_config,
                get_prior_context_count=lambda region, keywords: get_prior_related_count(region, keywords)
            )
            print(f"[*] Digest consolidated: {before_count} raw item(s) -> {len(combined_geo)} digest entr{'y' if len(combined_geo) == 1 else 'ies'}.")

        try:
            email_notifier.send_digest(config["email"], combined_geo, new_travel_matches)
        except Exception as e:
            # Email failure (Gmail hiccup, network issue, etc.) should never
            # block the rest of the pipeline -- all matched items are already
            # safely stored in the database by this point. Log it and continue,
            # so dashboard/map/confidence scoring still run with the new data.
            print(f"  [!] Email digest failed to send (data was still saved successfully): {e}")
    else:
        print("[*] Nothing new to notify.")

    # --- Cross-source confidence scoring against TRUSTED sources only (not raw repetition) ---
    print("[*] Scoring cross-source confidence for recent items...")
    recent_items = get_recent_items_for_confidence_scoring(days=5)
    confidence_scores = confidence.score_confidence(recent_items)
    update_confidence_bulk(confidence_scores)
    corroborated_count = sum(1 for v in confidence_scores.values() if v["tier"] == "corroborated")
    unverified_count = sum(1 for v in confidence_scores.values() if v["tier"] == "unverified")
    print(f"[*] Confidence scored for {len(confidence_scores)} recent item(s): "
          f"{corroborated_count} corroborated, {unverified_count} unverified.")

    # --- Targeted GDELT verification: only checks high-severity items that
    # are STILL unverified after regular confidence scoring, instead of
    # scanning all regions blindly every run (which was slow and unreliable). ---
    gdelt_config = config.get("gdelt", {})
    if gdelt_config.get("enabled"):
        candidates = get_items_needing_verification(limit=gdelt_config.get("verify_limit", 10))
        if candidates:
            print(f"[*] Verifying {len(candidates)} high-severity unverified item(s) via GDELT...")
            verification_results = gdelt_collector.verify_batch(candidates, gdelt_config)
            for item_id, new_sources in verification_results.items():
                candidate = next(c for c in candidates if c["item_id"] == item_id)
                tier, count = apply_gdelt_verification(item_id, new_sources, candidate["source"])
                print(f"  [x] Verified item {item_id[:12]}... -> {tier} ({count} trusted source(s))")
            print(f"[*] GDELT confirmed {len(verification_results)}/{len(candidates)} candidate(s).")
        else:
            print("[*] No high-severity unverified items to check via GDELT.")

    # --- Refresh dashboard and map (always, so they reflect full history even on quiet runs) ---
    generate_dashboard()
    generate_map()

    print(f"=== Run complete {datetime.now().isoformat()} ===\n")


if __name__ == "__main__":
    run()
