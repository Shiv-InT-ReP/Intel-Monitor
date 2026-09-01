"""
Catches false-positive matches -- items that technically matched a region
+ keyword co-occurrence but aren't actually a security/conflict/geopolitical
story. Two known patterns:

1. Ambiguous keyword usage: "attack" matching a heart attack, "strike"
   matching a legal ruling to "strike down" a law, "explosion" matching
   "population explosion," "bomb" matching "the movie bombed."
2. Off-topic stories that happen to mention a tracked country: e.g. a
   jewelry theft story mentioning "Egypt" as historical context for the
   item's origin, combined with some keyword elsewhere in the text --
   region+keyword co-occurrence without genuine topical relevance.

Checks EVERY newly-matched item, not just a pre-defined "ambiguous
keyword" list -- trying to enumerate every keyword that could theoretically
produce an off-topic match is a losing whack-a-mole game (the Egypt/necklace
case matched through a keyword we hadn't anticipated). Checking everything
is barely more expensive since it's all batched into one API call per run
on the cheap Haiku model regardless of how many items are included.

Failure handling: matches ai_dedup.py's pattern -- if the API call fails
for any reason (bad key, network, rate limit), every item defaults to
KEPT (context_uncertain=False) rather than risk losing a genuinely
relevant story. Classification is a precision improvement, never a point
of failure for the core pipeline.
"""
import json
import requests

API_URL = "https://api.anthropic.com/v1/messages"
DEFAULT_MODEL = "claude-haiku-4-5-20251001"

MAX_ITEMS_PER_RUN = 30


def get_items_needing_context_check(items: list[dict], regions: list[str]) -> list[dict]:
    """
    Returns up to MAX_ITEMS_PER_RUN newly-matched items for AI relevance
    verification. Checks everything rather than pre-filtering by keyword --
    trying to guess every keyword that could produce an off-topic match
    (art theft, celebrity news, sports mentioning a tracked country) is a
    losing game; a general relevance check catches the whole class of
    problem instead of one keyword at a time.
    """
    return items[:MAX_ITEMS_PER_RUN]


def _build_prompt(items: list[dict]) -> str:
    numbered_lines = []
    for i, item in enumerate(items):
        candidate_tags = item.get("_candidate_tags", [])
        tags_note = f" [keyword-matched tags to verify: {', '.join(candidate_tags)}]" if candidate_tags else ""

        candidate_regions = item.get("_candidate_regions", [])
        regions_note = ""
        if len(candidate_regions) > 1:
            regions_note = f" [multiple regions mentioned: {', '.join(candidate_regions)} -- if this is a disaster story, which one is where the disaster IMPACT actually is, not just an incidentally-mentioned nationality/context?]"

        numbered_lines.append(f"{i+1}. \"{item['title']}\"{tags_note}{regions_note}")
    numbered = "\n".join(numbered_lines)

    return f"""For each numbered headline below, determine THREE things:

(A) RELEVANT: does it describe a genuine security, military, conflict, disaster, or geopolitical \
event -- versus (a) using a similar-sounding word in an unrelated sense, or (b) being an off-topic \
story (art, culture, crime, sports, entertainment) that merely happens to mention a tracked country \
or region, without the story itself being about a security/conflict/geopolitical development there.

(B) DOMAIN: if relevant, is it fundamentally a "conflict" (military, security, political violence, \
defence) story, or a "disaster" (natural disaster -- earthquake, storm, flood, wildfire, volcano, \
tsunami) story? Watch for words that sound like natural disasters but are being used metaphorically \
for a military/conflict event -- e.g. a "drone storm" is a wave of drone attacks (conflict), not \
a weather event (disaster). If not relevant, domain doesn't matter -- just use "conflict" as a filler.

(C) CONFIRMED_TAGS: each headline lists which tags a simple keyword search matched (in brackets). \
Keyword matching is naive and produces false positives from ambiguous words -- e.g. "troop" \
matching a Boy Scout troop (not military), "curfew" matching a parental curfew (not a security \
state of emergency), "crackdown" on jaywalking (not political unrest). For each listed candidate \
tag, decide whether it's GENUINELY accurate for this headline, and return only the ones that are. \
Possible tags: "security" (genuine military/security threat), "protest" (genuine political \
protest/unrest), "disaster" (genuine natural disaster), "sloc" (genuine maritime/shipping security \
threat), "defence" (genuine military deployment/deal/exercise). Never add a tag that wasn't in the \
candidate list, even if you think it should apply -- only confirm or reject what was already matched.

(D) CORRECT_REGION: some headlines list multiple mentioned regions/countries. A naive matcher just \
picks whichever region happened to be mentioned first in the text -- which is often WRONG. E.g. \
"Second Israeli confirmed missing in Nepal floods" mentions Israel only because of a victim's \
nationality; the disaster itself is entirely in Nepal. If a headline lists multiple candidate \
regions AND is a genuine disaster story, return the region where the disaster's actual impact is \
occurring in "correct_region". CRITICAL: you must return EXACTLY ONE of the candidate regions \
listed for that headline -- never invent a new region, never combine multiple regions into one \
value (e.g. never return "Ukraine, Russia" -- pick just one). If only one region was listed, or \
this isn't a disaster story, or you're not confident, just return the first-listed candidate \
region unchanged.

IMPORTANT: economic warfare is a core part of what counts as relevant here, not just kinetic/
military events. Sanctions campaigns, trade wars, oil export/import shifts tied to sanctions \
evasion, and export control measures are ALL genuinely relevant -- they are a primary tool of \
modern geopolitical conflict, not "just business news." A story about sanctions targeting a \
country's oil trade is exactly as relevant as a story about a military strike on it.

Examples of NOT relevant: "heart attack" (medical, not military), "strike a deal" (negotiation, \
not a strike), "population explosion" (demographic, not an explosion), "shooting a film" \
(entertainment), "invasion of privacy" (not a military invasion), a stolen necklace historically \
linked to a country's former royalty (art/crime story, not a current event in that country).

Examples of genuinely relevant: an actual military strike, an actual explosion from a bomb or \
attack, an actual protest or crackdown, an actual natural disaster, actual diplomatic/security \
developments, AND sanctions/trade-war/economic-pressure campaigns, oil trade shifts tied to \
sanctions evasion, export control measures.

Headlines:
{numbered}

Respond with ONLY a JSON array of {len(items)} objects, each with "relevant" (boolean), "domain" \
(either "conflict" or "disaster"), "confirmed_tags" (array of strings, the subset of that item's \
candidate tags that are genuinely accurate -- empty array if none, or if no candidates were \
listed), and "correct_region" (string, the single correct region -- see rule D above; use the \
item's own listed candidate region(s) if there's only one, or if not applicable). No other text.
Example format: [{{"relevant": true, "domain": "conflict", "confirmed_tags": ["security"], "correct_region": "Iran"}}, \
{{"relevant": false, "domain": "conflict", "confirmed_tags": [], "correct_region": "Egypt"}}]"""


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
                "max_tokens": 3000,
                "messages": [{"role": "user", "content": prompt}],
            },
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()
        return data["content"][0]["text"].strip()
    except Exception as e:
        print(f"  [!] Context classifier: API call failed, keeping all items as-is: {e}")
        return None


def classify_context_batch(items: list[dict], ai_config: dict) -> dict[str, dict]:
    """
    Returns {item_id: {"relevant": bool, "domain": "conflict"|"disaster"}}
    for each item checked. Items NOT in the returned dict were either not
    candidates for checking, or the API call failed -- callers should treat
    missing entries as "keep as-is, unverified" (fail safe), never as
    "discard" or "recategorize."
    """
    if not items or not ai_config.get("enabled") or not ai_config.get("api_key"):
        return {}

    model = ai_config.get("model", DEFAULT_MODEL)
    prompt = _build_prompt(items)
    response_text = _call_claude(prompt, ai_config["api_key"], model)
    if response_text is None:
        return {}

    try:
        # Strip markdown code fences if the model wrapped its JSON in them
        cleaned = response_text.replace("```json", "").replace("```", "").strip()
        results = json.loads(cleaned)
        if not isinstance(results, list) or len(results) != len(items):
            print(f"  [!] Context classifier: unexpected response shape, keeping all items as-is")
            return {}

        output = {}
        for i, result in enumerate(results):
            if not isinstance(result, dict) or "relevant" not in result:
                continue  # malformed entry for this one item -- skip it, fail safe for just this item
            domain = result.get("domain", "conflict")
            if domain not in ("conflict", "disaster"):
                domain = "conflict"  # unexpected value -- fail safe to the more common domain
            confirmed_tags = result.get("confirmed_tags", [])
            if not isinstance(confirmed_tags, list):
                confirmed_tags = []
            correct_region = result.get("correct_region")
            if not isinstance(correct_region, str) or not correct_region:
                correct_region = None  # fail safe -- caller keeps the original region unchanged
            else:
                # Hard validation backstop: only accept a region that was
                # actually one of THIS item's own matched candidates -- never
                # trust the model to have invented a new region or combined
                # multiple into one value (e.g. "Ukraine, Russia"), even
                # though the prompt instructs against it. Prompt compliance
                # alone isn't a reliable enough guarantee for data integrity.
                item_candidates = items[i].get("_candidate_regions", [])
                if correct_region not in item_candidates:
                    correct_region = None
            output[items[i]["item_id"]] = {
                "relevant": bool(result["relevant"]),
                "domain": domain,
                "confirmed_tags": [t for t in confirmed_tags if isinstance(t, str)],
                "correct_region": correct_region,
            }
        return output
    except (json.JSONDecodeError, ValueError, IndexError, KeyError) as e:
        print(f"  [!] Context classifier: couldn't parse response, keeping all items as-is: {e}")
        return {}
