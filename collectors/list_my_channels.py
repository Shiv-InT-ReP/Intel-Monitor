"""
One-time helper: logs into YOUR Telegram account (prompts for phone number +
login code, first run only) and prints every channel/group you're currently
a member of, with their @usernames where public.

Run standalone: python collectors/list_my_channels.py

This also happens to complete Telegram's one-time interactive login and
creates the session file the main pipeline needs -- so run this BEFORE
scheduling main.py.

NOTE: Uses explicit asyncio (not telethon.sync) for compatibility with
Python 3.12+ / 3.14, where implicit event-loop creation was removed.
"""
import asyncio
import json
from pathlib import Path

from telethon import TelegramClient
from telethon.tl.types import Channel


async def main():
    cfg = json.loads((Path(__file__).resolve().parent.parent / "config.json").read_text())
    tg = cfg["telegram"]

    client = TelegramClient(tg["session_name"], int(tg["api_id"]), tg["api_hash"])
    await client.start()  # prompts for phone number + login code on first run

    print("\nYour channels/groups (public ones show @username -- copy those into config.json):\n")
    print(f"{'Username':<30} {'Type':<12} {'Title'}")
    print("-" * 80)
    async for dialog in client.iter_dialogs():
        entity = dialog.entity
        if isinstance(entity, Channel):
            username = f"@{entity.username}" if entity.username else "(private, no username)"
            kind = "channel" if entity.broadcast else "group"
            print(f"{username:<30} {kind:<12} {dialog.name}")

    await client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())