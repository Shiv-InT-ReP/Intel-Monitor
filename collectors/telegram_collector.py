"""
Telegram collector using Telethon (reads PUBLIC channels your account
can see -- this uses your personal Telegram account, not a bot, since
bots can't read channel history unless they're admins).

Setup (~5 minutes):
1. Go to https://my.telegram.org/apps and log in with your phone number
2. Create an app -> copy api_id and api_hash into config.json
3. First run must complete login interactively -- run:
   python collectors/list_my_channels.py
   once before scheduling this. It creates a session file so future
   runs (including scheduled ones) don't need interactive login.

NOTE: Uses explicit asyncio (not telethon.sync) for compatibility with
Python 3.12+ / 3.14, where implicit event-loop creation was removed.
"""
import asyncio
import hashlib
from datetime import datetime, timezone, timedelta

from telethon import TelegramClient


def _make_item_id(source: str, msg_id: int) -> str:
    return hashlib.sha256(f"{source}|{msg_id}".encode()).hexdigest()


async def _collect_async(telegram_config: dict, lookback_hours: int, limit_per_channel: int) -> list[dict]:
    items = []
    cutoff = datetime.now(timezone.utc) - timedelta(hours=lookback_hours)

    client = TelegramClient(
        telegram_config["session_name"],
        int(telegram_config["api_id"]),
        telegram_config["api_hash"],
    )
    await client.start()  # uses existing session file silently if already logged in

    for channel in telegram_config["channels"]:
        source_label = f"telegram:{channel}"
        try:
            async for message in client.iter_messages(channel, limit=limit_per_channel):
                if not message.date or message.date < cutoff:
                    break  # newest-first; stop once past lookback window
                if not message.text:
                    continue
                items.append({
                    "item_id": _make_item_id(source_label, message.id),
                    "source": source_label,
                    "title": message.text[:120],
                    "url": f"https://t.me/{channel.lstrip('@')}/{message.id}",
                    "published_at": message.date.isoformat(),
                    "text_for_matching": message.text,
                    "fetched_at": datetime.now(timezone.utc).isoformat(),
                })
        except Exception as e:
            print(f"  [!] Failed to fetch {channel}: {e}")
            continue

    await client.disconnect()
    return items


def collect(telegram_config: dict, lookback_hours: int = 24, limit_per_channel: int = 100) -> list[dict]:
    """Sync wrapper so main.py doesn't need to know this is async under the hood."""
    if not telegram_config.get("enabled"):
        return []
    if not telegram_config.get("channels"):
        return []
    return asyncio.run(_collect_async(telegram_config, lookback_hours, limit_per_channel))


if __name__ == "__main__":
    import json
    from pathlib import Path

    cfg = json.loads((Path(__file__).resolve().parent.parent / "config.json").read_text())
    results = collect(cfg["telegram"], lookback_hours=cfg.get("lookback_hours_first_run", 24))
    print(f"Login complete. Fetched {len(results)} messages as a test.")