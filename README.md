# Intel Monitor

A lightweight OSINT aggregation and alerting pipeline that consolidates
fragmented open-source signals -- news, Reddit, and Telegram -- into a
single filtered, deduplicated digest.

Built to solve a real problem in intelligence/OSINT monitoring workflows:
relevant signal is scattered across many platforms, each with its own
noise floor. This pipeline centralizes collection, applies rule-based
relevance triage, and delivers only what matters.

## Why this exists

Manually checking a dozen news feeds, subreddits, and Telegram channels
for geopolitical/security-relevant developments doesn't scale. This
pipeline runs unattended on a schedule, remembers what it's already seen,
and only surfaces genuinely new, relevant items -- cutting review time
from "read everything" to "read the digest."

## Architecture

- `collectors/` -- Pull raw items from each source (RSS, Reddit via
  public RSS, Telegram via personal account)
- `core/matcher.py` -- Relevance filtering: strict AND-logic between
  region terms and escalation-language keywords
- `core/db.py` -- SQLite-backed dedup store; every item is fingerprinted
  so nothing is ever surfaced twice
- `notifier/` -- Digest delivery (currently email; extensible)
- `main.py` -- Orchestrator: collect -> dedupe -> match -> notify

## Design decisions worth noting

- **Strict AND-matching, not OR.** A naive keyword filter (match if
  ANY term appears) is nearly useless at scale -- "Europe" or "sanctions"
  alone appear constantly with zero operational relevance. This pipeline
  requires a REGION term AND an ESCALATION-language term to co-occur in
  the same item, which empirically cut false positives by roughly 95%
  (58 -> 2 matches on identical source data in testing) while still
  catching genuine breaking developments.

- **Reddit via public RSS, not the official API.** Reddit's API access
  policy tightened significantly in 2025/2026, gating new developer
  access behind manual approval. Public subreddit RSS feeds
  (`/r/subreddit/new/.rss`) require no authentication and deliver the
  same data for this use case -- a pragmatic workaround that also means
  one less credential to manage.

- **Telegram via personal account (Telethon), not a bot.** Bots cannot
  read channel history unless granted admin rights on every channel.
  Reading public channels as a normal user, via the official (free)
  Telegram API, avoids that limitation entirely.

- **SQLite dedup, not in-memory state.** The pipeline is designed to run
  as a scheduled task (cron / Windows Task Scheduler) with no persistent
  process -- state must survive between runs. A simple `item_id` hash
  (source + URL, or source + message ID) makes re-notification
  structurally impossible rather than relying on time-window heuristics.

## Stack

Python 3, `feedparser` (RSS), `telethon` (Telegram, async), SQLite,
SMTP (email digest delivery).

## Setup

1. `pip install -r requirements.txt`
2. Copy `config.example.json` to `config.json` and fill in your own
   values. `config.json` is gitignored -- never commit real credentials.
3. For Telegram: get a free `api_id`/`api_hash` from my.telegram.org,
   then run `python collectors/list_my_channels.py` once to complete
   interactive login and list channels you can monitor.
4. For email: use a Gmail App Password (myaccount.google.com/apppasswords,
   requires 2-Step Verification), not your normal password.
5. `python main.py` to run once, or schedule it (see below).

## Scheduling

Windows (Task Scheduler via PowerShell), run once to register:

    $pythonPath = (Get-Command python).Source
    $action = New-ScheduledTaskAction -Execute $pythonPath -Argument "main.py" -WorkingDirectory (Get-Location).Path
    $trigger = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Hours 6) -RepetitionDuration (New-TimeSpan -Days 3650)
    Register-ScheduledTask -TaskName "IntelMonitor" -Action $action -Trigger $trigger -Description "Fragmented-source intel monitor"

Linux/Mac: standard cron entry pointing at `main.py`.

## Possible extensions

- AI-assisted relevance scoring (swap the rule-based matcher for an LLM
  call) for nuance beyond keyword co-occurrence
- Bluesky as an additional source (free, open AT Protocol API -- a
  viable alternative now that X's API requires paid access)
- Web dashboard instead of/alongside email digest
- Configurable per-region keyword sets rather than one global list

## License

MIT