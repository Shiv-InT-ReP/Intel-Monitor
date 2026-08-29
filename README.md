# Intel Monitor

A Python OSINT aggregation and alerting pipeline that consolidates
fragmented open-source intelligence -- news, government advisories,
Telegram, Reddit, verified conflict data, and real-time disaster feeds --
into a single filtered, severity-scored, cross-source-verified digest and
an interactive situation-board map.

## What it does

- Pulls from 30+ RSS sources (including local/regional outlets across
  South Asia, Middle East, and Eurasia), curated OSINT Telegram channels,
  subreddits, USGS earthquake data, and GDACS cyclone/flood alerts
- Filters using strict region+keyword co-occurrence matching (not naive
  keyword matching, which is nearly useless at scale)
- Scores every matched item by severity (low/moderate/high/critical) using
  weighted keyword logic, government advisory levels, or event-specific
  scoring (magnitude for earthquakes, fatalities for conflict events)
- Cross-references matched items against CREDIBLE sources only (not just
  repetition) to classify confidence as unverified / single-source /
  corroborated -- resistant to echo chambers, since raw repetition from
  low-trust sources never counts as verification on its own
- Flags source ownership/funding structure transparently (state-funded,
  state-linked, or state propaganda) -- with a hard safeguard so
  propaganda outlets can never manufacture false "corroborated" status,
  even by agreeing with each other
- Plots conflict/security events and natural disasters separately on an
  interactive radar map, with city-level precision where a specific place
  can be extracted from the text (via spaCy NER + free geocoding)
- Delivers a two-section email digest (geopolitical alerts + travel
  advisories) and a searchable, filterable dashboard

## Architecture

    main.py                     Orchestrator: collect -> dedupe -> match ->
                                 score -> verify -> notify -> render

    collectors/
      rss_collector.py           RSS/Atom feeds (news, think tanks, IGOs,
                                  government advisories, GDACS)
      reddit_collector.py        Public subreddit RSS (no API needed --
                                  Reddit's official API now requires
                                  approval we couldn't get)
      telegram_collector.py      Personal-account Telegram channel reading
      list_my_channels.py        One-time helper: lists your Telegram
                                  channels + completes login
      usgs_collector.py          USGS real-time earthquake GeoJSON feed
      acled_collector.py         ACLED conflict data (built, but DISABLED --
                                  ACLED denied elevated API access citing
                                  their EULA's redistribution terms)
      gdelt_collector.py         Targeted GDELT verification for high-severity
                                  unverified items (DISABLED by default --
                                  persistent connectivity issues from this
                                  network; code kept in case that changes)

    core/
      matcher.py                 Strict region+keyword AND-matching
      severity.py                Weighted severity scoring per source type
      confidence.py              Cross-source corroboration against
                                  CREDIBLE sources only (echo-chamber resistant)
      source_reliability.py      Ownership/funding transparency + hard
                                  safeguard against propaganda "corroboration"
      geocoding.py                spaCy NER + free Nominatim geocoding for
                                  city-level map precision
      db.py                       SQLite dedup store + all query/update logic
      ai_dedup.py                 AI-powered cluster synthesis for the email
                                  digest (built, requires your own Anthropic
                                  API key to activate -- currently inactive)

    dashboard/
      dashboard_generator.py       Searchable/filterable list view
      map_generator.py             Radar map data prep
      map_template.html            The map itself (severity color, conflict/
                                  disaster shape, confidence badges, city pins)

    notifier/
      email_notifier.py            Two-section digest email

    backfill_severity.py           One-time script: computes region/severity
                                  for historical items matched before that
                                  tracking existed

## Design decisions worth noting

- **Strict AND-matching, not OR.** A region term AND an escalation keyword
  must co-occur -- cuts false positives by roughly 95% versus naive
  keyword-only matching.

- **Confidence is about CREDIBILITY, not repetition.** Four Telegram
  channels reposting the same unverified rumor stay "unverified." Only
  edited, accountable outlets count as trusted corroboration.

- **Source ownership is disclosed, not silently judged.** Rather than
  unilaterally excluding "biased" sources, every source's funding/ownership
  structure is surfaced as a transparency tag. The one hard exception:
  outlets that are direct propaganda arms of authoritarian states (RT,
  Xinhua, CGTN, Press TV, etc.) are structurally barred from ever counting
  as trusted corroboration, since letting them "verify" each other would
  break the entire point of the confidence system.

- **Travel advisories and the conflict map are deliberately separate.**
  Travel advisories live only in the dashboard's Travel filter; the map is
  reserved for conflicts, geopolitical developments, and security/disaster
  incidents.

- **City-level map precision is opportunistic, not guaranteed.** spaCy's
  free local NER model catches most well-known cities but will miss some.
  When it can't find a specific place, items fall back to the
  country-centroid pin.

- **ACLED and GDELT are built but disabled**, for two different reasons:
  ACLED explicitly denied elevated API access citing their EULA's
  data-redistribution terms -- don't attempt to work around this. GDELT's
  targeted verification queries failed consistently from this specific
  network (other free APIs like USGS/GDACS/Nominatim work fine, so it's
  isolated to GDELT's servers) -- worth retrying from a different network.

## Stack

Python 3, feedparser, telethon, requests, spacy (+ en_core_web_sm
model), SQLite, SMTP.

## Setup

1. Install dependencies: pip install -r requirements.txt
2. Download the language model: python -m spacy download en_core_web_sm
3. Copy config.example.json to config.json, fill in your own values.
   config.json is gitignored -- never commit real credentials.
4. For Telegram: get a free api_id/api_hash from my.telegram.org, then
   run python collectors/list_my_channels.py once to complete login and
   list channels you can monitor.
5. For email: use a Gmail App Password (myaccount.google.com/apppasswords).
6. Run python main.py once, or schedule it (see below).

## Scheduling

Windows (Task Scheduler via PowerShell):

    $pythonPath = (Get-Command python).Source
    $action = New-ScheduledTaskAction -Execute $pythonPath -Argument "main.py" -WorkingDirectory (Get-Location).Path
    $trigger = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Hours 6) -RepetitionDuration (New-TimeSpan -Days 3650)
    Register-ScheduledTask -TaskName "IntelMonitor" -Action $action -Trigger $trigger

## License

MIT