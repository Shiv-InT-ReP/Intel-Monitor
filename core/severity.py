"""
Severity scoring. Not all matched keywords carry equal weight -- a single
"nuclear test" hit is more significant than three "patrol" hits. This
module scores matched items into four tiers: low, moderate, high, critical.

Geopolitical items are scored by the weighted sum of matched escalation
keywords. Travel advisory items are scored by detecting the advisory
LEVEL language itself (Level 1-4 / "reconsider travel" / "do not travel"),
since that's how governments already communicate severity.
"""
import re

# Weight reflects real-world severity, not just "is this word scary."
# Higher weight = more consequential if true.
KEYWORD_WEIGHTS = {
    # Critical (weight 3) -- events with mass-casualty or strategic potential
    "invasion": 3, "nuclear test": 3, "coup": 3, "coup attempt": 3, "martial law": 3,
    "airstrike": 3, "missile": 3, "suicide bombing": 3, "terrorist attack": 3,
    "assassination": 3, "embassy attack": 3, "bomb blast": 3, "critical infrastructure hack": 3,
    "tsunami": 3,

    # High (weight 2) -- active kinetic events, or serious non-kinetic escalation
    "strike": 2, "drone strike": 2, "attack": 2, "explosion": 2,
    "killed": 2, "casualties": 2, "blockade": 2, "ceasefire collapse": 2,
    "ied": 2, "hostage": 2, "ambush": 2, "kidnap": 2, "political violence": 2,
    "state of emergency": 2, "cyberattack": 2, "expel diplomat": 2,
    "seized vessel": 2, "piracy": 2, "territorial waters violation": 2,
    "shooting": 2, "stabbing": 2, "bomb": 2, "earthquake": 2, "cyclone": 2,

    # Moderate (weight 1) -- posture/escalation signals, not yet kinetic, or lower-severity incidents
    "mobiliz": 1, "clash": 1, "military drill": 1, "warship": 1,
    "patrol": 1, "fighter jet": 1, "incursion": 1, "troop": 1,
    "combat readiness": 1, "naval": 1, "airspace violation": 1, "evacuate": 1,
    "insurgent": 1, "militant": 1, "sabotage": 1, "curfew": 1, "crackdown": 1,
    "mass arrest": 1, "data breach": 1, "sanctions": 1, "arms deal": 1,
    "weapons transfer": 1, "trade war": 1, "protest": 1, "fire incident": 1, "storm": 1,
}

TIER_THRESHOLDS = [
    (6, "critical"),
    (3, "high"),
    (1, "moderate"),
    (0, "low"),
]

TRAVEL_LEVEL_PATTERNS = [
    (re.compile(r"level\s*4|do not travel", re.IGNORECASE), "critical"),
    (re.compile(r"level\s*3|reconsider travel", re.IGNORECASE), "high"),
    (re.compile(r"level\s*2|increased caution", re.IGNORECASE), "moderate"),
    (re.compile(r"level\s*1|normal precautions", re.IGNORECASE), "low"),
]


def score_geopolitical(matched_keywords: list[str]) -> tuple[int, str]:
    """Returns (numeric_score, tier) for a geopolitical item's matched keywords."""
    score = 0
    for kw in matched_keywords:
        kw_lower = kw.lower()
        for weighted_term, weight in KEYWORD_WEIGHTS.items():
            if weighted_term in kw_lower or kw_lower in weighted_term:
                score += weight
                break

    for threshold, tier in TIER_THRESHOLDS:
        if score >= threshold:
            return score, tier
    return score, "low"


def score_travel(text: str) -> tuple[int, str]:
    """Returns (numeric_score, tier) for a travel advisory based on advisory level language."""
    for pattern, tier in TRAVEL_LEVEL_PATTERNS:
        if pattern.search(text):
            score = {"critical": 4, "high": 3, "moderate": 2, "low": 1}[tier]
            return score, tier
    return 0, "low"  # no explicit level language found -- default to low


def score_acled(event_type: str, fatalities: int) -> tuple[int, str]:
    """
    Returns (numeric_score, tier) for an ACLED event. Since ACLED data is
    already verified conflict data (not raw text), we score by event type
    severity plus fatality count, rather than keyword matching.
    """
    base_score = {
        "Battles": 3,
        "Violence against civilians": 3,
        "Explosions/Remote violence": 3,
        "Riots": 1,
    }.get(event_type, 1)

    if fatalities >= 50:
        base_score += 4
    elif fatalities >= 10:
        base_score += 3
    elif fatalities >= 1:
        base_score += 2

    for threshold, tier in TIER_THRESHOLDS:
        if base_score >= threshold:
            return base_score, tier
    return base_score, "low"


def score_usgs(magnitude: float, tsunami: bool) -> tuple[int, str]:
    """
    Returns (numeric_score, tier) for a USGS earthquake event, based on the
    standard Richter/moment magnitude severity bands, with a tsunami flag
    override -- a tsunami warning is high-impact regardless of the quake's
    magnitude alone.
    """
    if magnitude is None:
        return 0, "low"

    if magnitude >= 7.0:
        score = 6  # critical
    elif magnitude >= 6.0:
        score = 4  # high
    elif magnitude >= 5.0:
        score = 2  # moderate
    else:
        score = 1  # low-moderate

    if tsunami:
        score = max(score, 6)  # tsunami risk always pushes to at least critical

    for threshold, tier in TIER_THRESHOLDS:
        if score >= threshold:
            return score, tier
    return score, "low"


# Keywords that indicate a NATURAL DISASTER rather than a conflict/security
# event -- used to pick the map marker shape (triangle vs circle), so the two
# very different categories of signal are visually distinguishable at a glance.
NATURAL_DISASTER_KEYWORDS = {
    "earthquake", "storm", "tsunami", "cyclone", "flood", "wildfire", "volcano",
}


def classify_domain(matched_keywords: list[str]) -> str:
    """Returns 'disaster' or 'conflict' based on which keywords matched."""
    kw_lower = {k.lower() for k in matched_keywords}
    if kw_lower & NATURAL_DISASTER_KEYWORDS:
        return "disaster"
    return "conflict"
