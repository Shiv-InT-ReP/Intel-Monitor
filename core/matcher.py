"""
Relevance matching. Two modes:

- "any" (old behavior): matches if ANY keyword or region appears. Broad, noisy.
- "strict" (default now): matches only if a REGION term AND an ESCALATION
  keyword both appear in the same item. This is what actually cuts noise --
  "Europe" alone or "sanctions" alone won't fire; "Taiwan" + "missile" will.
"""
import re


def _build_patterns(terms: list[str], case_sensitive: bool):
    flags = 0 if case_sensitive else re.IGNORECASE
    return [(term, re.compile(re.escape(term), flags)) for term in terms]


def build_matcher(keywords: list[str], regions: list[str], case_sensitive: bool = False):
    """Legacy 'any' mode: matches if any keyword OR region hits. Kept for reference/fallback."""
    terms = list(dict.fromkeys(keywords + regions))
    patterns = _build_patterns(terms, case_sensitive)

    def match(text: str):
        if not text:
            return []
        return [term for term, pat in patterns if pat.search(text)]

    return match


def build_strict_matcher(keywords: list[str], regions: list[str], case_sensitive: bool = False):
    """
    Strict mode: requires at least one REGION hit AND at least one
    ESCALATION KEYWORD hit in the same item. Cuts noise dramatically --
    routine mentions of a region with no escalation language are dropped.
    """
    region_patterns = _build_patterns(regions, case_sensitive)
    keyword_patterns = _build_patterns(keywords, case_sensitive)

    def match(text: str):
        if not text:
            return []
        region_hits = [term for term, pat in region_patterns if pat.search(text)]
        if not region_hits:
            return []
        keyword_hits = [term for term, pat in keyword_patterns if pat.search(text)]
        if not keyword_hits:
            return []
        return region_hits + keyword_hits

    return match


def get_matcher(config: dict):
    """Pick matcher based on config['match_mode']: 'strict' (default) or 'any'."""
    mode = config.get("match_mode", "strict")
    keywords = config["keywords"]
    regions = config["regions"]
    case_sensitive = config.get("case_sensitive", False)

    if mode == "any":
        return build_matcher(keywords, regions, case_sensitive)
    return build_strict_matcher(keywords, regions, case_sensitive)