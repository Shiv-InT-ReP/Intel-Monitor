"""
Source ownership/funding transparency, and a hard safeguard against
state propaganda counting as trusted corroboration.

Design principle: we don't unilaterally decide a source is "too biased"
to include -- that's an editorial judgment call that should be visible
and made by the reader, not silently baked into the pipeline. Instead:

1. Every source gets an ownership/funding classification, shown as a
   transparency tag in the dashboard/map/digest -- so you (and any
   newsletter readers) can see "this outlet is state-funded" and weigh
   that themselves.

2. ONE hard exception: outlets that are direct propaganda arms of
   authoritarian states (not just state-funded, but state-CONTROLLED
   with no editorial independence) are permanently barred from counting
   as "trusted" in the confidence/corroboration system. This isn't a
   political judgment about content -- it's a structural safeguard so
   that propaganda can never manufacture false "verified" status just
   by being technically an RSS feed. If you disagree with a specific
   classification below, it's meant to be easy to review and edit.

Matching is against the FEED NAME as it appears in config.json (source
strings are formatted "rss:{feed_name}"), not the domain -- since that's
what's actually available at match time.
"""
import re

# Direct propaganda arms of authoritarian states -- editorially controlled
# by the state, not just funded by it. These NEVER count as trusted
# corroboration, even if somehow added as a source later. Matched with
# word boundaries to avoid false positives on short/ambiguous terms (e.g.
# "RT" alone would otherwise match "reporting", "party", "airport", etc.).
STATE_PROPAGANDA_PATTERNS = [
    re.compile(r"\brt\b", re.IGNORECASE),
    re.compile(r"russia today", re.IGNORECASE),
    re.compile(r"sputnik", re.IGNORECASE),
    re.compile(r"\btass\b", re.IGNORECASE),
    re.compile(r"ria novosti", re.IGNORECASE),  # state-owned; the same government entity that later launched Sputnik
    re.compile(r"xinhua", re.IGNORECASE),
    re.compile(r"\bcgtn\b", re.IGNORECASE),
    re.compile(r"global times", re.IGNORECASE),
    re.compile(r"china daily", re.IGNORECASE),
    re.compile(r"press tv", re.IGNORECASE),
    re.compile(r"tasnim", re.IGNORECASE),
    re.compile(r"\birna\b", re.IGNORECASE),
    re.compile(r"pars today", re.IGNORECASE),
    re.compile(r"\bkcna\b", re.IGNORECASE),
    re.compile(r"korean central news agency", re.IGNORECASE),
]

# State-funded but editorially independent public broadcasters -- shown
# with a transparency tag, but NOT excluded from trusted corroboration,
# since they have genuine, documented editorial independence (distinct
# from the blocklist above). Matched against feed name substrings.
STATE_FUNDED_INDEPENDENT = {
    "dw (deutsche welle)": "German public broadcaster, editorially independent by law",
    "rfa": "US-funded (USAGM) international broadcaster, editorial independence from US government",
    "rferl": "US-funded (USAGM) international broadcaster, editorial independence from US government",
    "radio farda": "RFE/RL's Persian-language service -- same funding/independence model as RFA/RFE/RL above; documented history of Iranian government censorship attempts against it, evidence of genuine independence from Tehran",
}

# State-LINKED ownership (government owns the parent company via an
# investment arm), not a full editorial-independence guarantee the way
# DW/RFA have, but also not a propaganda blocklist case -- shown
# transparently so readers can weigh it.
STATE_LINKED_OWNERSHIP = {
    "cna": "Owned by Mediacorp, which Singapore's government owns via Temasek Holdings",
    "daily sabah": "Owned by Turkuvaz Media Group, widely described as close to Turkey's ruling AKP and President Erdoğan; not a state-controlled propaganda outlet, but a documented ownership tie worth knowing",
}


def is_propaganda_blocked(source: str) -> bool:
    """True if this source should NEVER count as trusted corroboration."""
    return any(pattern.search(source) for pattern in STATE_PROPAGANDA_PATTERNS)


def get_ownership_tag(source: str) -> dict | None:
    """
    Returns {"tag": str, "note": str} for sources with a disclosed
    ownership/funding structure worth surfacing, or None for sources
    with no special classification (independent/private ownership).
    """
    if is_propaganda_blocked(source):
        return {"tag": "STATE PROPAGANDA", "note": "Direct state-controlled outlet, excluded from trusted corroboration"}

    source_lower = source.lower()

    for name_fragment, note in STATE_FUNDED_INDEPENDENT.items():
        if name_fragment in source_lower:
            return {"tag": "STATE-FUNDED", "note": note}

    for name_fragment, note in STATE_LINKED_OWNERSHIP.items():
        if name_fragment in source_lower:
            return {"tag": "STATE-LINKED", "note": note}

    return None
