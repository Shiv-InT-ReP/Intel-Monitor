"""
Fetches transcripts for official YouTube video announcements -- ministers
and officials often announce policy verbally in press briefings rather
than publishing a written statement. This lets the pipeline match against
what was actually SAID, not just the video's title.

Uses YouTube's own auto-generated captions via the youtube-transcript-api
library -- no video download, no local speech-to-text compute needed.
Genuinely lightweight, but has real limits: auto-captions aren't available
for every video (too new, disabled by the channel, or genuinely absent),
so this fails gracefully rather than blocking the pipeline.

pip install youtube-transcript-api --break-system-packages
"""
import re

from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import CouldNotRetrieveTranscript

_VIDEO_ID_PATTERNS = [
    re.compile(r"(?:v=|/videos/|embed/|youtu\.be/)([A-Za-z0-9_-]{11})"),
    re.compile(r"^([A-Za-z0-9_-]{11})$"),  # bare video ID
]


def extract_video_id(url_or_id: str) -> str | None:
    """Pulls an 11-character YouTube video ID out of any common URL format,
    or passes through a bare ID unchanged. Returns None if nothing matches."""
    if not url_or_id:
        return None
    for pattern in _VIDEO_ID_PATTERNS:
        m = pattern.search(url_or_id)
        if m:
            return m.group(1)
    return None


def get_transcript_text(url_or_id: str, languages: tuple[str, ...] = ("en", "hi")) -> str | None:
    """
    Returns the full transcript as a single text string, or None if no
    transcript is available (disabled, video too new, wrong language, or
    genuinely no captions) -- never raises, so one bad video can't break
    a whole pipeline run.
    """
    video_id = extract_video_id(url_or_id)
    if not video_id:
        return None

    try:
        api = YouTubeTranscriptApi()
        transcript = api.fetch(video_id, languages=list(languages))
        return " ".join(snippet.text for snippet in transcript).strip()
    except CouldNotRetrieveTranscript as e:
        # The library's shared parent exception for every KNOWN, expected
        # reason a transcript isn't available -- disabled captions, age
        # restriction, IP/region blocks, or (as we hit in practice) a
        # scheduled livestream that hasn't started yet. All genuinely
        # unretrievable, none worth a loud error -- just skip quietly.
        return None
    except Exception as e:
        print(f"  [!] Unexpected error fetching transcript for {video_id}: {e}")
        return None


def is_youtube_url(url: str) -> bool:
    return bool(url) and ("youtube.com" in url or "youtu.be" in url)
