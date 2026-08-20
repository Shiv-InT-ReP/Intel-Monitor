"""
Reddit collector using PRAW. Requires a free Reddit "script" app.

Setup (~2 minutes):
1. Go to https://www.reddit.com/prefs/apps
2. Click "create app" -> select "script"
3. Name it anything, redirect URI can be http://localhost:8080
4. Copy the client_id (under the app name) and client_secret into config.json
"""
import hashlib
from datetime import datetime, timezone

import praw


def _make_item_id(source: str, post_id: str) -> str:
    return hashlib.sha256(f"{source}|{post_id}".encode()).hexdigest()


def collect(reddit_config: dict, limit_per_subreddit: int = 25) -> list[dict]:
    if not reddit_config.get("enabled"):
        return []

    reddit = praw.Reddit(
        client_id=reddit_config["client_id"],
        client_secret=reddit_config["client_secret"],
        user_agent=reddit_config["user_agent"],
    )
    reddit.read_only = True

    items = []
    for sub_name in reddit_config["subreddits"]:
        source_label = f"reddit:{sub_name}"
        try:
            subreddit = reddit.subreddit(sub_name)
            for post in subreddit.new(limit=limit_per_subreddit):
                items.append({
                    "item_id": _make_item_id(source_label, post.id),
                    "source": source_label,
                    "title": post.title,
                    "url": f"https://reddit.com{post.permalink}",
                    "published_at": datetime.fromtimestamp(
                        post.created_utc, tz=timezone.utc
                    ).isoformat(),
                    "text_for_matching": f"{post.title}\n{getattr(post, 'selftext', '')}",
                    "fetched_at": datetime.now(timezone.utc).isoformat(),
                })
        except Exception as e:
            print(f"  [!] Failed to fetch r/{sub_name}: {e}")
            continue

    return items
