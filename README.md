# Intel Monitor

A Python OSINT aggregation and alerting pipeline that consolidates
fragmented open-source intelligence -- news, government advisories,
official releases, Telegram, Reddit, verified conflict data, and
real-time disaster feeds -- into a filtered, severity-scored,
cross-source-verified, geopolitically-analyzed system spanning four
views: a searchable dashboard, an interactive radar map, curated
conflict background timelines, and an official releases feed.

## What it does

- Pulls from 30+ RSS sources across South Asia, Middle East, Eurasia,
  and 94 individually-tracked countries, plus curated OSINT Telegram
  channels, USGS earthquakes, GDACS cyclones/floods, and official
  government/IGO press releases
- Filters using strict region+keyword co-occurrence matching
- Scores every matched item by severity, and multi-tags it (Security,
  Protests, Natural Calamities, Sea Lines of Communication, Iran War &
  Gulf Region, Russia-Ukraine War, Defence) -- an item can carry several
  tags at once, each independently filterable
- Cross-references matches against CREDIBLE sources only for confidence
  scoring -- resistant to echo chambers, with a hard safeguard so state
  propaganda outlets can never manufacture false "corroborated" status
- Discloses source ownership/funding transparently (state-funded,
  state-linked) rather than silently excluding anything
- Validates geocoded city-level pins against a real distance check, so
  extraction errors can't plot a story on the wrong continent
- Filters by TRUE article publish date (not capture date) for the
  dashboard/map's time windows, while still storing everything so
  nothing is lost -- the email digest separately excludes stale content
- Tracks 5 real maritime chokepoints (Hormuz, Bab-el-Mandeb, Malacca,
  Suez, Turkish Straits) with live status, tied into SLOC detection
- Maintains 12 manually-researched, fully-sourced conflict background
  timelines with real geopolitical analysis (key actors, regional
  linkages, 30/90-day outlook, escalation triggers, early-warning
  indicators, second-order effects, risk/confidence levels), each with
  a live "recent activity" feed pulled from your own matched items and
  a staleness indicator showing when the analysis was last reviewed
- Surfaces official government/IGO releases on their own page, matched
  by region, kept separate from the alert-focused email digest

## Architecture

    main.py                     Orchestrator: collect -> dedupe -> match ->
                                 score -> tag -> verify -> notify -> render

    collectors/
      rss_collector.py           RSS/Atom feeds -- news, advisories, GDACS,
                                  official releases; HTML-sanitizes titles
      reddit_collector.py        Public subreddit RSS
      telegram_collector.py      Personal-account Telegram channel reading
      list_my_channels.py        One-time helper: completes Telegram login
      usgs_collector.py          USGS real-time earthquake GeoJSON feed
      acled_collector.py         ACLED conflict data (DISABLED -- ACLED
                                  denied elevated API access citing their
                                  EULA's redistribution terms)
      gdelt_collector.py         Targeted GDELT verification (DISABLED --
                                  persistent connectivity issues from this
                                  network; code kept in case that changes)

    core/
      matcher.py                 Strict region+keyword AND-matching
      severity.py                Weighted severity scoring
      confidence.py               Cross-source corroboration, echo-chamber
                                  resistant
      source_reliability.py       Ownership/funding transparency + hard
                                  propaganda-corroboration safeguard
      event_tags.py               Multi-tag classification (Security,
                                  Protest, Disaster, SLOC, Iran/Gulf,
                                  Russia-Ukraine, Defence)
      chokepoints.py              Real maritime chokepoint reference data
      geocoding.py                spaCy NER + Nominatim geocoding, with a
                                  distance sanity-check against the story's
                                  own region (catches wildly wrong matches)
      db.py                       SQLite store + all query/update logic

    dashboard/
      dashboard_generator.py       Searchable/filterable list view
      map_generator.py             Radar map data prep
      map_template.html            Severity color, conflict/disaster shape,
                                  chokepoint markers, confidence badges,
                                  age badges, time/tag filters
      background_generator.py      Conflict background page: timelines,
                                  analysis, live activity, staleness
      releases_generator.py        Official government/IGO releases page

    notifier/
      email_notifier.py            Two-section digest email

    data/
      conflict_backgrounds.py      Manually-curated conflict timelines and
                                  analysis -- deliberately NOT auto-scraped

    archive_item.py                Manual, human-in-the-loop event archiving
    backfill_domain.py              One-time: recompute conflict/disaster
                                  domain for pre-feature historical items
    backfill_event_tags.py          One-time: recompute multi-tags for
                                  pre-feature historical items
    cleanup_bad_geocoding.py        One-time: re-validate existing geocoded
                                  pins against the plausibility check
    fix_ocean_ridge_usgs.py         One-time: clear mis-tagged oceanic USGS
                                  events caught by the region word-boundary fix
    backfill_severity.py            One-time: severity/region for early
                                  pre-tracking items

## Design decisions worth noting

- **Strict AND-matching, not OR.** A region term and an escalation
  keyword must co-occur -- cuts false positives dramatically versus
  naive keyword-only matching.

- **Confidence is about CREDIBILITY, not repetition.** Only edited,
  accountable outlets count as trusted corroboration -- Telegram/Reddit
  chatter never does, no matter how many times it's repeated.

- **Source ownership is disclosed, not silently judged.** Every source's
  funding/ownership gets a transparency tag. The one hard exception:
  direct propaganda arms of authoritarian states are structurally barred
  from ever counting as trusted corroboration.

- **Curated content stays human-in-the-loop, deliberately.** Event
  archiving and the conflict background analysis are never
  auto-generated or auto-updated -- deciding what belongs in a
  conflict's historical record, or forming a risk/outlook judgment, is
  an editorial call. The conflict pages show a "last reviewed" date and
  flag staleness rather than silently presenting old judgment as
  current; the live "recent activity" feed gives real-time signal in
  between manual reviews.

- **Time filters use the article's real publish date**, not when Intel
  Monitor happened to capture it -- otherwise a "last 30 days" filter
  would be meaningless, since almost everything gets captured close to
  "now" regardless of how old the actual news is.

- **Geocoding is sanity-checked against real geography.** Every
  city-level match is validated against a distance threshold from its
  own region's centroid, specifically to prevent the class of bug where
  an ambiguous extracted place name resolves to an unrelated location on
  the other side of the world.

- **ACLED and GDELT are built but disabled.** ACLED explicitly denied
  elevated API access citing their EULA's redistribution terms -- don't
  attempt to work around this. GDELT's targeted verification queries
  failed consistently from this specific network (other free APIs work
  fine, so it's isolated to GDELT's servers) -- worth retrying from a
  different network.

- **NATO's own official RSS feed is confirmed broken** (403 Forbidden,
  per Wikidata's own record) -- don't waste time re-adding it without
  checking whether that's changed.

## Stack

Python 3, feedparser, telethon, requests, spacy (+ en_core_web_sm
model), SQLite, SMTP.

## Setup

1. Install dependencies: pip install -r requirements.txt
2. Download the language model: python -m spacy download en_core_web_sm
3. Copy config.example.json to config.json, fill in your own values.
   config.json is gitignored -- never commit real credentials.
4. For Telegram: get a free api_id/api_hash from my.telegram.org, then
   run python collectors/list_my_channels.py once to complete login.
5. For email: use a Gmail App Password.
6. Run python main.py once, or schedule it (see below).

This produces four pages: dashboard.html, map.html, background.html,
and releases.html.

## Scheduling

Windows (Task Scheduler via PowerShell):

    $pythonPath = (Get-Command python).Source
    $action = New-ScheduledTaskAction -Execute $pythonPath -Argument "main.py" -WorkingDirectory (Get-Location).Path
    $trigger = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Hours 6) -RepetitionDuration (New-TimeSpan -Days 3650)
    Register-ScheduledTask -TaskName "IntelMonitor" -Action $action -Trigger $trigger

## License

MIT
