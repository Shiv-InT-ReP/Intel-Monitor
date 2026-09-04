"""
Translates new items from non-English-language sources (Tamil, Hindi,
Malayalam, Arabic, Persian, Hebrew, Turkish, Russian, or whatever else
gets added) to English BEFORE they reach the region+keyword matcher --
the entire matching pipeline (region names, escalation keywords) is
English-only, so untranslated text would never match anything, regardless
of how relevant the actual story is. Local-language sources often carry
signal well before it reaches English-language wire coverage -- this is
precisely the gap RSS-only, English-only OSINT pipelines have.

Unlike video_summarizer.py (which condenses a long transcript into a
short summary), this needs a genuinely complete translation, not a
condensed one -- matching needs the actual region/keyword mentions
preserved, not just the gist. Batched like context_classifier.py (not
one-call-per-item like video_summarizer.py) since a single run may have
many new items to translate, and batching keeps API call overhead and
cost down.

Only translates NEW (unseen) items -- called before matching, not after,
since we don't know if something matches until it's been translated.
"""
import json
import requests

API_URL = "https://api.anthropic.com/v1/messages"
DEFAULT_MODEL = "claude-haiku-4-5-20251001"
MAX_ITEMS_PER_BATCH = 12  # smaller than context_classifier's batches -- full-text translation
                          # output is much larger per item than a short boolean/tag classification,
                          # so smaller batches keep each individual API call fast and reliable


def _build_prompt(items: list[dict]) -> str:
    numbered = "\n".join(
        f"{i+1}. \"{item['text_for_matching'][:600]}\""
        for i, item in enumerate(items)
    )
    return f"""Translate each numbered news item below into English. These are news headlines \
and summaries (combined), most likely in one of: Tamil, Hindi, Malayalam, Arabic, Persian/Farsi, \
Hebrew, Turkish, or Russian -- but detect and translate whatever language is actually present, \
don't assume it must be one of these. Provide a COMPLETE translation, not a \
condensed summary -- preserve all place names, people, and specific details exactly, since this \
translation will be used to detect mentions of specific countries/regions and events, not just \
read for gist. If a proper noun (country, city, person, organization) has a standard English \
form, use it (e.g. translate பாகிஸ்தான் as "Pakistan", Россия as "Russia", إيران as "Iran" -- \
not a phonetic transliteration).

{numbered}

Respond with ONLY a JSON array of {len(items)} objects, each with "title" (a short English \
headline capturing the main point) and "full_text" (the complete English translation of the \
whole item). No other text.
Example format: [{{"title": "Pakistan conducts military drill near border", "full_text": "..."}}]"""


def _call_claude(prompt: str, api_key: str, model: str) -> str | None:
    try:
        resp = requests.post(
            API_URL,
            headers={
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            json={
                "model": model,
                "max_tokens": 4000,
                "messages": [{"role": "user", "content": prompt}],
            },
            timeout=90,  # translation of full article text is a heavier task than short
                         # structured classification -- needs real headroom, not the 30s that
                         # was timing out on 8 of 10 batches in production
        )
        resp.raise_for_status()
        data = resp.json()
        return data["content"][0]["text"].strip()
    except Exception as e:
        print(f"  [!] Vernacular translation: API call failed, skipping this batch: {e}")
        return None


def translate_batch(items: list[dict], ai_config: dict) -> dict[str, dict]:
    """
    Returns {item_id: {"title": translated_title, "full_text": translated_full_text}}
    for each item successfully translated. Items NOT in the returned dict
    (API failure, malformed response, or not configured) should be SKIPPED
    by the caller for this run -- never matched against untranslated text,
    and never dropped/archived just because translation failed once.
    """
    if not items or not ai_config.get("enabled") or not ai_config.get("api_key"):
        return {}

    model = ai_config.get("model", DEFAULT_MODEL)
    output = {}

    for batch_start in range(0, len(items), MAX_ITEMS_PER_BATCH):
        batch = items[batch_start:batch_start + MAX_ITEMS_PER_BATCH]
        prompt = _build_prompt(batch)
        response_text = _call_claude(prompt, ai_config["api_key"], model)
        if response_text is None:
            continue  # this batch failed -- skip it, don't fail the whole run

        try:
            cleaned = response_text.replace("```json", "").replace("```", "").strip()
            results = json.loads(cleaned)
            if not isinstance(results, list) or len(results) != len(batch):
                print(f"  [!] Vernacular translation: unexpected response shape for a batch, skipping it")
                continue
            for i, result in enumerate(results):
                if not isinstance(result, dict) or "title" not in result:
                    continue  # malformed entry for this one item -- skip just this one
                output[batch[i]["item_id"]] = {
                    "title": result["title"],
                    "full_text": result.get("full_text", result["title"]),
                }
        except (json.JSONDecodeError, ValueError, IndexError, KeyError) as e:
            print(f"  [!] Vernacular translation: couldn't parse a batch response, skipping it: {e}")
            continue

    return output
