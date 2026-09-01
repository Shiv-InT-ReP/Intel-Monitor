"""
Summarizes (and translates, if needed) official YouTube briefing
transcripts -- ministers and officials often announce policy verbally in
press briefings rather than publishing a written statement. This turns
the raw transcript (already fetched for matching purposes by
youtube_transcript.py) into a short, readable English summary for display
on the releases page, instead of just a bare video link.

One API call per video (not batched like context_classifier) -- each
summary needs its own distinct output, and batching multiple long-form
text outputs into one structured response is more error-prone to parse
reliably than context_classifier's simple boolean-array approach.

Transcript text is truncated before sending to control cost -- a 2-4
sentence summary doesn't need the full transcript if it's unusually long.
"""
import requests

API_URL = "https://api.anthropic.com/v1/messages"
DEFAULT_MODEL = "claude-haiku-4-5-20251001"
MAX_TRANSCRIPT_CHARS = 8000  # roughly 2000 tokens -- keeps cost/latency bounded


def _build_prompt(title: str, transcript: str) -> str:
    truncated = transcript[:MAX_TRANSCRIPT_CHARS]
    return f"""This is a transcript of an official government/press briefing video. \
Summarize the key points in 2-4 concise sentences, in English. If the transcript is in a \
language other than English (e.g. Hindi), translate the key points as part of your summary \
rather than summarizing in the original language. Focus on factual content -- what was \
announced, discussed, or stated -- not commentary.

Title: {title}

Transcript:
{truncated}

Respond with ONLY the summary text, no preamble, no "Here is a summary:" prefix."""


def summarize_video(title: str, transcript: str, ai_config: dict) -> str | None:
    """
    Returns a short English summary of the transcript, or None if
    summarization isn't configured/fails -- never raises, callers should
    fall back to just showing the video link when this returns None.
    """
    if not ai_config.get("enabled") or not ai_config.get("api_key") or not transcript:
        return None

    model = ai_config.get("model", DEFAULT_MODEL)
    prompt = _build_prompt(title, transcript)

    try:
        resp = requests.post(
            API_URL,
            headers={
                "x-api-key": ai_config["api_key"],
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            json={
                "model": model,
                "max_tokens": 300,
                "messages": [{"role": "user", "content": prompt}],
            },
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()
        return data["content"][0]["text"].strip()
    except Exception as e:
        print(f"  [!] Video summarization failed for '{title[:50]}...': {e}")
        return None
