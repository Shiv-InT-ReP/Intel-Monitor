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
import re
import sys
import time
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from core.db import init_db, is_seen, mark_seen, get_recent_items_for_confidence_scoring, update_confidence_bulk, get_prior_related_count, get_items_needing_verification, apply_gdelt_verification, set_video_summary, set_item_domain, remove_event_tag, set_item_region
from core.matcher import get_matcher, build_region_only_matcher
from core import severity, confidence, ai_dedup, geocoding, event_tags, youtube_transcript, context_classifier, video_summarizer
from collectors import rss_collector, reddit_collector, telegram_collector, acled_collector, usgs_collector, gdelt_collector
from notifier import email_notifier
from dashboard.dashboard_generator import generate_dashboard
from dashboard.map_generator import generate_map
from dashboard.background_generator import generate_background_page
from dashboard.releases_generator import generate_releases_page

CONFIG_PATH = Path(__file__).resolve().parent / "config.json"

# For deciding whether a matched item is fresh enough to include in the
# EMAIL digest -- not whether to store it. Everything gets stored regardless
# (mark_seen always runs), so the dashboard/map's "All time" view can still
# surface genuinely old content; this only controls what triggers an alert.
# Travel advisories are deliberately exempt (see the check site below) --
# standing government guidance doesn't stop being valid just because it
# wasn't republished recently.
MAX_ITEM_AGE_DAYS_FOR_DIGEST = 30


def _is_recently_published(item: dict, max_age_days: int = MAX_ITEM_AGE_DAYS_FOR_DIGEST) -> bool:
    """
    True if the item's own published_at date is recent enough to alert on,
    or if the date can't be parsed at all (fail open -- better to include
    an item we're uncertain about than silently drop it).
    """
    from email.utils import parsedate_to_datetime
    from datetime import timezone as _tz, timedelta as _td

    published_at = item.get("published_at")
    if not published_at:
        return True

    try:
        published_dt = parsedate_to_datetime(published_at)
        if published_dt.tzinfo is None:
            published_dt = published_dt.replace(tzinfo=_tz.utc)
    except (TypeError, ValueError):
        return True  # unparseable -- fail open, don't silently exclude

    age = datetime.now(_tz.utc) - published_dt
    return age <= _td(days=max_age_days)


def load_config() -> dict:
    return json.loads(CONFIG_PATH.read_text())


def _process_items(items: list[dict], matcher, category: str, regions: list[str], geocoding_enabled: bool = False) -> list[dict]:
    """Dedupe + match + score a batch of items. Returns only new, matched items
    that are also fresh enough to include in the email digest -- stale items
    are still fully stored (mark_seen always runs) for dashboard/map browsing,
    just excluded from what gets returned/alerted on."""
    matched = []
    stale_but_stored = 0
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
                enriched = geocoding.enrich_item_with_city(item, regions, primary_region=primary_region,
                                                            all_matched_regions=region_hits)
                city_name = enriched.get("city_name")
                city_lat = enriched.get("city_lat")
                city_lon = enriched.get("city_lon")

            domain = severity.classify_domain(hits) if category != "travel" else "conflict"
            tags = event_tags.classify_event_tags(keyword_hits, region=primary_region) if category != "travel" else []

            item["region"] = primary_region  # attach for reuse by AI dedup clustering
            item["severity_tier"] = tier
            item["domain"] = domain  # attach for reuse by the context classifier's domain-correction check
            # Only the keyword-derived tags are candidates for AI verification --
            # iran_war/russia_ukraine_war are region-based, not vulnerable to the
            # same "ambiguous word" false-positive pattern (see event_tags.py).
            item["_candidate_tags"] = [t for t in tags if t not in ("iran_war", "russia_ukraine_war")]
            item["_candidate_regions"] = region_hits  # all matched regions, for disaster-location disambiguation
            mark_seen(item, notified=True, category=category,
                      severity_tier=tier, severity_score=score, region=primary_region,
                      city_name=city_name, city_lat=city_lat, city_lon=city_lon, domain=domain, event_tags=tags)

            # Always store (above), but only include in the returned list --
            # which feeds the email digest -- if it's either a travel
            # advisory (standing guidance, exempt from freshness) or was
            # actually published recently. Stale items are still fully
            # queryable via the dashboard/map's 90-day/all-time views.
            if category == "travel" or _is_recently_published(item):
                matched.append(item)
            else:
                stale_but_stored += 1
        else:
            mark_seen(item, notified=False, category=category)  # record so we never re-check it

    if stale_but_stored:
        print(f"  [i] {stale_but_stored} matched item(s) stored but excluded from digest "
              f"(published >{MAX_ITEM_AGE_DAYS_FOR_DIGEST} days ago -- still browsable via 'All time' on the dashboard/map)")
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

    # --- AI context classification: catches false-positive matches from
    # ambiguous keywords ("heart attack" matching "attack", etc.). Only
    # affects the EMAIL DIGEST -- items flagged as not-actually-relevant
    # still stay fully stored/browsable (same "store everything, be
    # selective about what alerts" principle as the published-date fix).
    ai_config = config.get("ai_dedup", {})  # reuses the same API key config as AI dedup
    if ai_config.get("enabled") and ai_config.get("api_key"):
        context_candidates = context_classifier.get_items_needing_context_check(new_geo_matches, config["regions"])
        if context_candidates:
            print(f"[*] Checking {len(context_candidates)} ambiguous-keyword match(es) with AI context classifier...")
            classifications = context_classifier.classify_context_batch(context_candidates, ai_config)
            filtered_count = 0
            corrected_domain_count = 0
            rejected_tags_count = 0
            corrected_region_count = 0
            new_geo_matches_after_context = []
            for item in new_geo_matches:
                result = classifications.get(item["item_id"])  # None -- fail safe, keep unverified items as-is
                if result is None:
                    new_geo_matches_after_context.append(item)
                    continue

                if not result["relevant"]:
                    filtered_count += 1
                    print(f"  [x] Filtered from digest (context check): {item['title'][:70]}")
                    # Not relevant at all -- none of its keyword-matched tags are
                    # valid either. The item stays fully stored (mark_seen already
                    # ran), but strip its tags so it doesn't pollute filter views
                    # like "Defence Alerts" for a story that isn't genuinely one.
                    for candidate in item.get("_candidate_tags", []):
                        if remove_event_tag(item["item_id"], candidate):
                            rejected_tags_count += 1
                    continue

                new_geo_matches_after_context.append(item)
                # Correct a wrong keyword-based domain guess (e.g. "drone storm"
                # matching the disaster keyword "storm") -- domain was already
                # computed, attached to the item, and stored via mark_seen
                # inside _process_items, so this is a write-back fix.
                if item.get("domain") and item["domain"] != result["domain"]:
                    set_item_domain(item["item_id"], result["domain"])
                    corrected_domain_count += 1
                    # Same misclassification also affects the "disaster" event
                    # tag (shows as "Natural Calamities" in the UI filter) --
                    # strip it if the AI determined this isn't really a disaster.
                    if result["domain"] == "conflict":
                        remove_event_tag(item["item_id"], "disaster")

                # Strip any OTHER keyword-matched tag the AI didn't confirm --
                # e.g. "troop" matching a Boy Scout troop story under "defence".
                candidate_tags = item.get("_candidate_tags", [])
                confirmed_tags = set(result.get("confirmed_tags", []))
                for candidate in candidate_tags:
                    if candidate not in confirmed_tags and candidate != "disaster":  # disaster already handled above
                        if remove_event_tag(item["item_id"], candidate):
                            rejected_tags_count += 1

                # Correct a wrong disaster-location region pick -- e.g. "Second
                # Israeli confirmed missing in Nepal floods" wrongly pinned to
                # Israel (a victim's nationality) instead of Nepal (the actual
                # disaster location).
                correct_region = result.get("correct_region")
                if correct_region and item.get("region") and correct_region != item["region"]:
                    set_item_region(item["item_id"], correct_region)
                    corrected_region_count += 1

            new_geo_matches = new_geo_matches_after_context
            if filtered_count:
                print(f"[*] Context classifier excluded {filtered_count} false-positive keyword match(es) from the digest.")
            if corrected_domain_count:
                print(f"[*] Context classifier corrected {corrected_domain_count} domain misclassification(s) "
                      f"(e.g. metaphorical 'storm'/'flood' wording wrongly tagged as a natural disaster).")
            if rejected_tags_count:
                print(f"[*] Context classifier rejected {rejected_tags_count} false-positive tag(s) "
                      f"(e.g. 'troop' matching a Boy Scout troop story under Defence).")
            if corrected_region_count:
                print(f"[*] Context classifier corrected {corrected_region_count} disaster-location region "
                      f"mismatch(es) (e.g. pinned to a victim's nationality instead of the actual disaster location).")

    # --- Travel advisory sources (separate feed list, separate matcher) ---
    new_travel_matches = []
    travel_feeds = config.get("travel_advisory_feeds", [])
    if travel_feeds:
        print("[*] Fetching travel advisory feeds...")
        travel_items = rss_collector.collect(travel_feeds, filter_stale=False)
        print(f"[*] Fetched {len(travel_items)} total travel advisory items.")
        new_travel_matches = _process_items(travel_items, travel_matcher, category="travel", regions=config["regions"])
        print(f"[*] {len(new_travel_matches)} new travel advisory item(s) matched.")

    # --- Official government/IGO releases (Ministries, UN, NATO, etc.) --
    # Same region-only matching as travel advisories -- these are official
    # statements, they don't need an escalation keyword to be relevant.
    new_release_matches = []
    release_feeds = config.get("official_release_feeds", [])
    if release_feeds:
        print("[*] Fetching official government/IGO release feeds...")
        release_items = rss_collector.collect(release_feeds, filter_stale=False)
        print(f"[*] Fetched {len(release_items)} total official release items.")

        # For YouTube-sourced releases (video briefings, spoken announcements
        # with no written statement), fetch the auto-generated transcript and
        # fold it into the matchable text -- otherwise a generically-titled
        # video ("Weekly MEA Briefing") that verbally covers something
        # region-relevant would never match on title alone. Capped and rate
        # limited to keep runtime reasonable and avoid hammering YouTube.
        yt_config = config.get("youtube_transcripts", {})
        if yt_config.get("enabled", True):
            transcript_count = 0
            transcript_cap = yt_config.get("max_per_run", 15)
            for item in release_items:
                if transcript_count >= transcript_cap:
                    break
                if is_seen(item["item_id"]) or not youtube_transcript.is_youtube_url(item["url"]):
                    continue
                transcript = youtube_transcript.get_transcript_text(item["url"])
                if transcript:
                    item["text_for_matching"] = item.get("text_for_matching", "") + "\n" + transcript
                    item["_transcript"] = transcript  # preserved for summarization after matching, below
                transcript_count += 1
                time.sleep(1.0)  # be polite to YouTube's transcript endpoint
            if transcript_count:
                print(f"[*] Fetched {transcript_count} YouTube transcript(s) for spoken-content matching.")

        new_release_matches = _process_items(release_items, travel_matcher, category="official_release", regions=config["regions"])
        print(f"[*] {len(new_release_matches)} new official release item(s) matched.")

        # Summarize (and translate, if needed) matched YouTube briefings --
        # only for items that actually matched AND have a transcript, so we
        # never spend API calls summarizing something that turned out to be
        # irrelevant to your tracked regions.
        ai_config_for_video = config.get("ai_dedup", {})
        if ai_config_for_video.get("enabled") and ai_config_for_video.get("api_key"):
            summarized_count = 0
            for item in new_release_matches:
                transcript = item.get("_transcript")
                if not transcript:
                    continue
                summary = video_summarizer.summarize_video(item["title"], transcript, ai_config_for_video)
                if summary:
                    set_video_summary(item["item_id"], summary)
                    summarized_count += 1
            if summarized_count:
                print(f"[*] Summarized {summarized_count} YouTube briefing(s) for the releases page.")

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
            # Word-boundary matching, not naive substring -- "india" as a
            # substring incorrectly matches "Indian Ridge" or "Indian Ocean
            # Triple Junction" (real USGS location names for oceanic seismic
            # features nowhere near India). Same bug class as "RT" matching
            # "Reporting" in the source-bias safeguard.
            matched_region = next(
                (r for r in config["regions"] if re.search(r'\b' + re.escape(r.lower()) + r'\b', place_text)),
                None
            )
            if not matched_region:
                continue

            score, tier = severity.score_usgs(item["_usgs_magnitude"], item["_usgs_tsunami"])
            item["matched_keywords"] = [matched_region, "earthquake"]
            item["region"] = matched_region
            item["severity_tier"] = tier
            mark_seen(item, notified=True, category="geopolitical",
                      severity_tier=tier, severity_score=score, region=matched_region,
                      city_name=item["_usgs_place"], city_lat=item["_usgs_lat"], city_lon=item["_usgs_lon"],
                      domain="disaster", event_tags=["disaster"])
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
    generate_background_page()
    generate_releases_page()

    print(f"=== Run complete {datetime.now().isoformat()} ===\n")


if __name__ == "__main__":
    run()
