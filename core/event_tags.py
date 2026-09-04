"""
Multi-tag event classification -- unlike domain (conflict vs disaster,
mutually exclusive), these tags OVERLAP. A "Russia launches airstrike on
Ukraine" story is simultaneously a Security Threat, a Defence Alert, AND
a Russia-Ukraine War Alert. Every matched item gets a LIST of applicable
tags, stored as a comma-separated string, and each dashboard/map filter
button shows everything carrying that one tag -- an item can legitimately
appear under several different filters.
"""
from core.chokepoints import region_has_chokepoint

SECURITY_KEYWORDS = {
    "missile", "strike", "airstrike", "drone strike", "attack", "explosion",
    "killed", "casualties", "suicide bombing", "ied", "hostage", "ambush",
    "terrorist attack", "assassination", "shooting", "stabbing", "bomb",
    "bomb blast", "embassy attack",
}

PROTEST_KEYWORDS = {
    "protest", "riot", "general strike", "mass arrest", "crackdown",
    "curfew", "state of emergency", "roadblock",
}

DISASTER_KEYWORDS = {
    "earthquake", "storm", "tsunami", "cyclone", "flood", "wildfire", "volcano",
}

SLOC_KEYWORDS = {
    "seized vessel", "piracy", "territorial waters violation", "naval",
    "warship", "blockade",
}

DEFENCE_KEYWORDS = {
    "military drill", "patrol", "fighter jet", "troop", "combat readiness",
    "mobiliz", "airspace violation", "arms deal", "weapons transfer", "incursion",
    # Procurement/deal terms added after the "Javelin deal" case -- a story
    # about ACQUIRING a weapon system (defence procurement) is a
    # fundamentally different kind of story than one about a weapon being
    # USED (security threat), even though both mention the same hardware.
    # Bare "deal" is deliberately excluded -- too generic, would false-positive
    # on trade deals, political deals, etc. Only compound defence-specific
    # phrases are included here.
    "defence deal", "missile deal", "weapons deal", "defence pact",
    "defence agreement", "defence exports", "procurement",
}

# The Iran War & Gulf Region tag covers the actual 2026 Iran war conflict
# system, not just Iran alone -- Yemen (Houthi Bab-el-Mandeb blockade),
# Saudi Arabia, and Qatar (US-Iran talks venue) are all directly tied to
# the same active conflict, per real reporting.
IRAN_GULF_REGIONS = {"Iran", "Yemen", "Saudi Arabia", "Qatar"}


def classify_event_tags(matched_keywords: list[str], region: str = None) -> list[str]:
    """Returns the list of tags applicable to this item, based on which
    keywords matched and its region. An item can carry multiple tags."""
    kw_lower = {k.lower() for k in matched_keywords}
    tags = []

    if kw_lower & SECURITY_KEYWORDS:
        tags.append("security")
    if kw_lower & PROTEST_KEYWORDS:
        tags.append("protest")
    if kw_lower & DISASTER_KEYWORDS:
        tags.append("disaster")
    # SLOC now uses the real chokepoint reference dataset -- a maritime
    # keyword only counts if the region actually has a known chokepoint
    # associated with it, not just a vague "sounds maritime" guess.
    if (kw_lower & SLOC_KEYWORDS) and region_has_chokepoint(region):
        tags.append("sloc")
    if kw_lower & DEFENCE_KEYWORDS:
        tags.append("defence")

    if region in IRAN_GULF_REGIONS:
        tags.append("iran_war")
    if region in ("Russia", "Ukraine"):
        tags.append("russia_ukraine_war")

    return tags


TAG_LABELS = {
    "security": "Security Threats",
    "protest": "Protests & Unrest",
    "disaster": "Natural Calamities",
    "sloc": "Sea Lines of Communication",
    "iran_war": "Iran War & Gulf Region Alerts",
    "russia_ukraine_war": "Russia-Ukraine War Alerts",
    "defence": "Defence Alerts",
}
