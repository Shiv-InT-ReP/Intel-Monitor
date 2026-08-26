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
    "invasion": 3, "nuclear test": 3, "coup": 3, "martial law": 3,
    "airstrike": 3, "missile": 3,

    # High (weight 2) -- active kinetic events
    "strike": 2, "drone strike": 2, "attack": 2, "explosion": 2,
    "killed": 2, "casualties": 2, "blockade": 2, "ceasefire collapse": 2,

    # Moderate (weight 1) -- posture/escalation signals, not yet kinetic
    "mobiliz": 1, "clash": 1, "military drill": 1, "warship": 1,
    "patrol": 1, "fighter jet": 1, "incursion": 1, "troop": 1,
    "combat readiness": 1, "naval": 1, "airspace violation": 1, "evacuate": 1,
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
