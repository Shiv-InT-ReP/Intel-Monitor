"""
Supply chain dependency data -- critical civilian and military production/
processing chokepoints, distinct from the maritime SHIPPING chokepoints in
chokepoints.py. A strait has objective, reportable disruption events (a
ship gets struck, mines are laid); a semiconductor fab or a rare-earth
processing plant doesn't -- disruption signals here are diffuse (export
control announcements, capacity reports, policy statements), not the kind
of thing that can be reliably auto-detected from news matching.

This is therefore a STATIC, periodically-reviewed reference (same model as
conflict_backgrounds.py), not something that auto-updates from the daily
pipeline. Update `last_reviewed` and re-verify facts by hand when revisiting.

Each node has:
- linked_conflict: the conflict_backgrounds.py key this enriches, or None
  for the 3 nodes that don't map cleanly onto an existing tracked conflict
  (these live in a separate "Other Supply Chain Dependencies" section instead)
- stat_callouts: short, bolded-headline-style facts for the compact/summary
  view (used both for the enriched dossier bullets and the standalone section)
- chain_nodes: real locations with a role label (Mining/Processing/
  Manufacturing/Production/Consumer/Destination) and coordinates, used to
  draw the multi-node flow map in the click-through popup. Diffuse
  "consumer" endpoints use a single representative location rather than
  attempting to plot every importing country.
"""

SUPPLY_CHAIN_NODES = {

    # ============ Linked to china_taiwan_2026 ============
    "taiwan_semiconductors": {
        "name": "Taiwan Advanced Semiconductor Manufacturing",
        "category": "civilian",
        "linked_conflict": "china_taiwan_2026",
        "last_reviewed": "2026-09-04",
        "stat_callouts": [
            {"stat": "73% of global pure-foundry chip capacity",
             "detail": "TSMC's share as of Q1-Q2 2026, up from 69.9% in 2025 and 64.4% in 2024 -- dominance is growing despite years of Western re-shoring efforts."},
            {"stat": "90%+ of the world's most advanced chips",
             "detail": "Sub-5nm production is essentially Taiwan-exclusive; the US CHIPS Act's $450B+ investment remains several years behind Taiwan's technological edge."},
            {"stat": "Mutual dependency, not one-way",
             "detail": "China itself receives over half of Taiwan's chip exports -- a real complication for any full decoupling scenario."},
        ],
        "chain_nodes": [
            {"name": "Taiwan (TSMC, Hsinchu)", "role": "Manufacturing", "lat": 24.8, "lon": 121.0},
            {"name": "China", "role": "Consumer", "lat": 35.0, "lon": 105.0},
            {"name": "Global tech industry", "role": "Consumer", "lat": 38.9, "lon": -77.0},
        ],
        "why_it_matters": "No other single point of failure in global technology carries this much concentrated risk -- a disruption to Taiwan's fabs would stall production of phones, cars, computers, and defense systems worldwide simultaneously, with no near-term substitute capacity.",
        "alternative_suppliers": "Samsung (South Korea) is the only partial alternative at the leading edge, and remains meaningfully behind. US/EU re-shoring investment is real but measured in years, not months.",
        "current_status": "Stable but structurally unresolved -- TSMC's market share is increasing, not decreasing, even as geopolitical pressure to diversify grows.",
        "sources": ["TrendForce foundry market share reports 2026", "TSMC investor disclosures", "CHIPS Act program reporting"],
    },

    # ============ Linked to us_china_trade_2026 ============
    "rare_earth_processing": {
        "name": "China's Rare Earth Element Processing Dominance",
        "category": "dual-use",
        "linked_conflict": "us_china_trade_2026",
        "last_reviewed": "2026-09-04",
        "stat_callouts": [
            {"stat": "~90% of global rare earth processing",
             "detail": "China holds only ~35% of global reserves but dominates the industrial-policy-driven midstream processing capacity that actually determines supply."},
            {"stat": "F-35: 900+ lbs of rare earths. Virginia-class submarine: 9,200 lbs.",
             "detail": "Concrete US defense-platform exposure to a supply chain China effectively controls."},
            {"stat": "80% of tungsten, 60% of antimony",
             "detail": "Also dominant in these directly defense-relevant materials -- armor-piercing rounds and munitions manufacturing."},
            {"stat": "Licensing approvals below 25% for European firms",
             "detail": "2026 export-control tightening has produced sixfold price spikes on some materials since the January 2026 catalogue expansion."},
        ],
        "chain_nodes": [
            {"name": "China (Baotou processing hub)", "role": "Processing", "lat": 40.65, "lon": 109.84},
            {"name": "Australia (mining source)", "role": "Mining", "lat": -31.9, "lon": 115.9},
            {"name": "US defense/tech industry", "role": "Consumer", "lat": 38.9, "lon": -77.0},
        ],
        "why_it_matters": "This is a textbook demonstration that mining dominance and processing dominance are different things -- China's leverage comes from decades of deliberate midstream investment, not geological luck, which is exactly why it's hard to replicate quickly.",
        "alternative_suppliers": "Rebuilding meaningful alternative processing capacity is estimated at 5-7 years for partial scale, 20-30 years for full independence from China.",
        "current_status": "Active and escalating -- China's 2026 export licensing regime is a live, currently-tightening chokepoint, directly linked to the EDA software counter-leverage episode below.",
        "sources": ["USGS Mineral Commodity Summaries 2026", "reporting on January 2026 export catalogue expansion", "US DoD critical minerals assessments"],
    },
    "eda_design_software": {
        "name": "Semiconductor Design (EDA) Software -- US/Allied Leverage",
        "category": "dual-use",
        "linked_conflict": "us_china_trade_2026",
        "last_reviewed": "2026-09-04",
        "stat_callouts": [
            {"stat": "~70% of the global EDA market, ~80% in China specifically",
             "detail": "Synopsys, Cadence, and Siemens EDA control the software essential for designing any advanced chip -- a rare point of Western, not Chinese, leverage."},
            {"stat": "Restricted May 2025, rescinded July 2025",
             "detail": "The US lifted its own EDA export restrictions on China less than six weeks after imposing them -- explicitly tied to China's retaliatory rare earth export controls. Two chokepoints traded directly against each other."},
        ],
        "chain_nodes": [
            {"name": "US (Synopsys/Cadence, Silicon Valley)", "role": "Design Tools Origin", "lat": 37.4, "lon": -122.1},
            {"name": "China", "role": "Restricted Destination", "lat": 35.0, "lon": 105.0},
        ],
        "why_it_matters": "This is the clearest example in the whole supply chain picture of a two-way leverage fight -- it directly demonstrates that the rare earth story above isn't one-sided dependency, it's a live bargaining relationship where both sides hold real cards.",
        "alternative_suppliers": "China's domestic alternatives (Empyrean, Primarius) exist but still can't match Synopsys/Cadence capability at the leading edge.",
        "current_status": "Currently rescinded/inactive as an active restriction, but the July 2025 reversal shows how quickly this can be redeployed as leverage.",
        "sources": ["BIS export control announcements", "reporting on the May-July 2025 restriction and rescission"],
    },
    "naval_shipbuilding_capacity": {
        "name": "Naval Shipbuilding Capacity -- China vs. United States",
        "category": "military",
        "linked_conflict": "us_china_trade_2026",
        "last_reviewed": "2026-09-04",
        "stat_callouts": [
            {"stat": "~230x US shipbuilding capacity",
             "detail": "A figure from a leaked US Navy briefing slide, corroborated by CSIS and multiple 2026 sources -- China's industrial shipbuilding base dwarfs America's."},
            {"stat": "370+ warships vs. 287-296",
             "detail": "China's navy is now numerically larger than the US Navy."},
            {"stat": "Qualitative edge still favors the US",
             "detail": "11 carriers vs. China's 3, 64 nuclear submarines -- this is a narrowing gap, not current US inferiority."},
        ],
        "chain_nodes": [
            {"name": "China (Jiangnan Shipyard, Shanghai)", "role": "Production", "lat": 31.2, "lon": 121.5},
            {"name": "US (Newport News, VA)", "role": "Production", "lat": 37.0, "lon": -76.4},
        ],
        "why_it_matters": "In a prolonged conflict, the capacity to REPAIR damaged vessels and REPLACE losses matters as much as the current fleet size -- China's industrial throughput advantage compounds over the length of any sustained naval confrontation, directly relevant to Taiwan Strait and South China Sea scenarios.",
        "alternative_suppliers": "US shipbuilding is heavily concentrated in a handful of yards (Huntington Ingalls, General Dynamics); the 4 public yards are focused on maintenance, not new construction.",
        "current_status": "Gap actively widening -- China also holds 70%+ of the global COMMERCIAL shipbuilding orderbook, an industrial base advantage underpinning its naval capacity.",
        "sources": ["Leaked US Navy briefing reporting", "CSIS naval capacity assessments 2026"],
    },

    # ============ Linked to russia_ukraine_2026 ============
    "russia_titanium": {
        "name": "Russia's Titanium Supply (VSMPO-AVISMA) -- A Sanctions Paradox",
        "category": "dual-use",
        "linked_conflict": "russia_ukraine_2026",
        "last_reviewed": "2026-09-04",
        "stat_callouts": [
            {"stat": "Once ~80% of Boeing's, ~60% of Airbus's titanium",
             "detail": "Pre-war dependency levels -- titanium was deliberately EXEMPTED from initial sanctions specifically to avoid an aviation supply shock."},
            {"stat": "Airbus now down to ~20% dependency",
             "detail": "Real diversification since 2022; VSMPO's own output fell from ~32,000 to ~17,000 tonnes/year."},
            {"stat": "Same pattern as rare earths: processing, not mining, is the leverage",
             "detail": "Russia holds only ~14.5% of global titanium reserves -- its dominance came from midstream value-chain investment, not raw material abundance."},
        ],
        "chain_nodes": [
            {"name": "Russia (VSMPO-AVISMA, Urals)", "role": "Mining/Processing", "lat": 58.05, "lon": 60.5},
            {"name": "US (Boeing, Seattle)", "role": "Consumer", "lat": 47.6, "lon": -122.3},
            {"name": "France (Airbus, Toulouse)", "role": "Consumer", "lat": 43.6, "lon": 1.4},
        ],
        "why_it_matters": "This is a genuine sanctions-policy tension made concrete -- the West's own aviation industry needed this supply chain to keep functioning even while sanctioning the country that controlled it, which is exactly why titanium got carved out for so long.",
        "alternative_suppliers": "ATI/Howmet (US), Aubert & Duval (France), Japan (doubling sponge titanium production), Kazakhstan, and a new Bahrain complex are all ramping up as alternatives.",
        "current_status": "Actively diversifying -- the US did eventually sanction VSMPO directly in 2023, though some titanium reportedly still reroutes through China as an intermediary.",
        "sources": ["Reuters/Bloomberg VSMPO-AVISMA reporting", "BIS sanctions designations", "Airbus/Boeing supply chain disclosures"],
    },
    "nato_artillery_production": {
        "name": "NATO 155mm Artillery Shell Production Capacity",
        "category": "military",
        "linked_conflict": "russia_ukraine_2026",
        "last_reviewed": "2026-09-04",
        "stat_callouts": [
            {"stat": "US: ~14,400/month pre-war to ~50,000/month in 2026",
             "detail": "Targeting 90-100,000/month -- a real, substantial production ramp, but one that took years."},
            {"stat": "EU's public 2M-rounds/year pledge likely overstated",
             "detail": "An RFE/RL investigation found actual capacity closer to half the publicly claimed figure."},
            {"stat": "The real bottleneck is propellant, not shell casings",
             "detail": "Nitrocellulose production capacity is the specific constraint, not the more visible steel-casing manufacturing."},
            {"stat": "Russia still firing 5-10x Ukraine's rate",
             "detail": "A senior US general described Russia as building a stockpile 'triple the size of the US's and Europe's combined.'"},
        ],
        "chain_nodes": [
            {"name": "US (Scranton Army Ammunition Plant)", "role": "Production", "lat": 41.4, "lon": -75.7},
            {"name": "Germany (Rheinmetall)", "role": "Production", "lat": 51.2, "lon": 6.8},
            {"name": "Poland", "role": "Production", "lat": 52.2, "lon": 21.0},
            {"name": "Ukraine", "role": "Destination", "lat": 49.0, "lon": 32.0},
        ],
        "why_it_matters": "This is the clearest illustration that a coalition's own industrial capacity -- not just its political will -- can be the actual constraint on sustaining a partner in a prolonged conventional war.",
        "alternative_suppliers": "New NATO-Poland joint production deals (Northrop Grumman + Poland) are emerging specifically to address the propellant bottleneck.",
        "current_status": "Actively ramping but still short of stated targets -- genuine progress, genuine gap remains.",
        "sources": ["RFE/RL EU shell-capacity investigation", "US Army production announcements", "NATO Secretary General statements"],
    },
    "china_drone_components": {
        "name": "Chinese Drone/UAS Components -- Supplying Both Sides",
        "category": "dual-use",
        "linked_conflict": "russia_ukraine_2026",
        "last_reviewed": "2026-09-04",
        "stat_callouts": [
            {"stat": "~70% of the global commercial drone market (DJI)",
             "detail": "China's dominance in commercial drones directly feeds military and improvised drone supply chains on both sides of the war."},
            {"stat": "60-80% of critical electronics in Russian-made drones are Chinese-origin",
             "detail": "China supplies ~90% of Russia's high-priority dual-use imports, worth over $4B annually."},
            {"stat": "Ukraine's own drone production also relies on Chinese components",
             "detail": "The same civilian supply pipeline effectively arms both sides of an active war simultaneously."},
            {"stat": "China tightened drone-part export controls toward the US, August 2026",
             "detail": "An active, currently-evolving policy lever."},
        ],
        "chain_nodes": [
            {"name": "China (Shenzhen)", "role": "Component Manufacturing", "lat": 22.5, "lon": 114.0},
            {"name": "Russia", "role": "Destination", "lat": 55.7, "lon": 37.6},
            {"name": "Ukraine", "role": "Destination", "lat": 50.4, "lon": 30.5},
        ],
        "why_it_matters": "The 'both sides' dynamic here is genuinely unusual -- most supply chain dependencies have a clear beneficiary and a clear victim; this one shows a single civilian commercial supply chain arming both combatants in the same war simultaneously, which complicates any simple sanctions or export-control response.",
        "alternative_suppliers": "US response has been regulatory rather than substitutive so far -- NDAA banned DJI federal procurement, DOD blacklisted DJI, and the Blue UAS program is certifying alternatives, but Chinese components remain deeply embedded in both militaries' supply chains.",
        "current_status": "Active and largely unresolved -- both combatants remain dependent on the same third-country civilian supply chain.",
        "sources": ["US DOD Blue UAS program documentation", "reporting on Chinese dual-use export volumes to Russia", "Ukrainian drone-industry sourcing reports"],
    },
    "neon_gas_semiconductors": {
        "name": "Ukrainian Neon Gas for Chip Lithography -- A Resolved Vulnerability",
        "category": "civilian",
        "linked_conflict": "russia_ukraine_2026",
        "last_reviewed": "2026-09-04",
        "stat_callouts": [
            {"stat": "Ukraine once supplied 45-90% of global semiconductor-grade neon",
             "detail": "Estimates vary by source and year, but Ukraine's role (via Ingas and Cryoin) was genuinely large pre-war."},
            {"stat": "Prices spiked ~500% in early 2022",
             "detail": "When Russian invasion halted Ukrainian neon production."},
            {"stat": "Included here deliberately as a CONTRAST case",
             "detail": "By 2023-2026, chipmakers diversified suppliers, built stockpiles, and newer chip processes (5nm/2nm) need less neon as a laser buffer gas -- 'crisis averted,' prices stable as of early 2026."},
        ],
        "chain_nodes": [
            {"name": "Ukraine (Odessa/Mariupol -- historic production)", "role": "Historic Production", "lat": 46.5, "lon": 30.7},
            {"name": "Global chip fabs (representative: Taiwan)", "role": "Consumer", "lat": 24.8, "lon": 121.0},
        ],
        "why_it_matters": "This is the proof-of-concept case that a concentrated supply chain chokepoint CAN be successfully diversified away from, in contrast to rare earths or cobalt where alternatives remain years away -- worth keeping visible specifically because it shows the range of possible outcomes, not just the alarming ones.",
        "alternative_suppliers": "Successfully diversified -- China, and other neon producers, plus reduced per-chip neon intensity at leading-edge nodes.",
        "current_status": "Resolved -- included as historical/analytical context, not an active vulnerability.",
        "sources": ["Reporting on 2022 neon price spikes", "semiconductor industry supply diversification reporting 2023-2026"],
    },
    "russia_ukraine_grain": {
        "name": "Russia-Ukraine Grain Exports -- Global Food Security",
        "category": "civilian",
        "linked_conflict": "russia_ukraine_2026",
        "last_reviewed": "2026-09-04",
        "stat_callouts": [
            {"stat": "Pre-war: 9% of global wheat, 12% of corn, 46% of sunflower oil (Ukraine alone)",
             "detail": "A major share of global agricultural export capacity concentrated in the conflict zone itself."},
            {"stat": "50 countries depend on Russia+Ukraine for 30%+ of wheat demand",
             "detail": "26 countries depend on the two combined for over half their wheat needs; several African nations (Egypt, Sudan, Tanzania) are 70%+ dependent on Ukraine specifically."},
            {"stat": "Wheat futures jumped ~60% within days of the 2022 invasion",
             "detail": "Russia's July 2023 withdrawal from the Black Sea Grain Initiative immediately triggered renewed attacks on grain infrastructure."},
            {"stat": "Genuine resilience: both still major exporters in 2026-27",
             "detail": "Forecasts of 53.5M tonnes (Russia) and 41.9M tonnes (Ukraine) despite the ongoing war."},
        ],
        "chain_nodes": [
            {"name": "Russia", "role": "Production", "lat": 55.7, "lon": 37.6},
            {"name": "Ukraine", "role": "Production", "lat": 49.0, "lon": 32.0},
            {"name": "Egypt (representative importer)", "role": "Consumer", "lat": 30.0, "lon": 31.2},
        ],
        "why_it_matters": "This is the clearest humanitarian-stakes entry in the whole set -- disruption here doesn't primarily threaten a company's profit margin, it threatens food security for tens of millions of people in countries with no direct stake in the war itself.",
        "alternative_suppliers": "Partial diversification toward other exporters (Argentina, Australia, India in some years) exists but can't fully replace this volume at this price point for import-dependent nations.",
        "current_status": "Ongoing disruption alongside genuine resilience -- both countries continue exporting substantial volumes despite active attacks on shipping/infrastructure.",
        "sources": ["UN FAO trade data", "USDA export forecasts 2026-27", "Black Sea Grain Initiative reporting"],
    },

    # ============ Linked to korea_2026 (cross-references russia_ukraine_2026) ============
    "north_korea_artillery_supply": {
        "name": "North Korea's Artillery Supply to Russia",
        "category": "military",
        "linked_conflict": "korea_2026",
        "last_reviewed": "2026-09-04",
        "stat_callouts": [
            {"stat": "Estimated 25-50% of Russia's artillery needs at various points",
             "detail": "Some assessments cite up to 75-100% of daily front-line fire at peak periods."},
            {"stat": "North Korea halved shipments by late 2025",
             "detail": "As its own stockpiles ran low -- a genuinely dynamic, currently-shifting dependency, not a fixed one."},
            {"stat": "Russia's own production surged in parallel: 2-2.3M rounds (2024) to 7M (2025)",
             "detail": "Suggesting Russia may be becoming less dependent on North Korea as its own capacity grows."},
            {"stat": "Reciprocal exchange, not one-way aid",
             "detail": "Russia reportedly provides satellite technology, energy, and construction materials in return."},
        ],
        "chain_nodes": [
            {"name": "North Korea", "role": "Production/Source", "lat": 39.0, "lon": 125.7},
            {"name": "Russia", "role": "Destination", "lat": 55.7, "lon": 37.6},
        ],
        "why_it_matters": "This dependency directly links your Korea and Russia-Ukraine dossiers -- and it's actively evolving in real time, worth monitoring for whether the trend of Russia's self-sufficiency continues.",
        "alternative_suppliers": "Not really applicable in the traditional sense -- this is about Russia's OWN production capacity increasingly substituting for North Korean supply, not a third-party alternative supplier.",
        "current_status": "Shifting -- North Korean supply declining as Russia's domestic capacity grows; worth re-verifying this trend at the next review.",
        "sources": ["Ukrainian military intelligence assessments", "NATO Secretary General Rutte statements", "open-source ammunition tracking (Open Source Centre/Reuters)"],
    },

    # ============ NOT cleanly tied to an existing conflict dossier --
    # rendered in the separate "Other Supply Chain Dependencies" section ============
    "drc_cobalt": {
        "name": "DRC Cobalt Mining & Chinese Refining Dominance",
        "category": "dual-use",
        "linked_conflict": None,
        "last_reviewed": "2026-09-04",
        "stat_callouts": [
            {"stat": "DRC: 70-75%+ of global cobalt mining",
             "detail": "The Democratic Republic of Congo is the overwhelming source of the world's cobalt supply."},
            {"stat": "China: ~75-80% of global cobalt refining",
             "detail": "The same mining-vs-processing pattern as rare earths and titanium -- Chinese firms (CMOC, Zijin, Huayou) also directly operate 70-80% of DRC's industrial mines themselves."},
            {"stat": "Active conflict touches this supply chain directly",
             "detail": "M23 rebel activity in eastern DRC sits alongside this mineral trade, and adjacent conflict-mineral smuggling (coltan, gold) is well documented."},
            {"stat": "DRC weaponizing its own export policy",
             "detail": "A 2025 export ban, then a 2026-27 quota (96,000 tonnes/year) roughly halving 2024 export volumes -- a deliberate government move for more leverage/value."},
            {"stat": "Physically vulnerable logistics",
             "detail": "DRC is landlocked; cobalt is trucked over unpaved roads to South African or Tanzanian ports."},
        ],
        "chain_nodes": [
            {"name": "DRC (Katanga/Kolwezi)", "role": "Mining", "lat": -10.7, "lon": 25.5},
            {"name": "China", "role": "Refining", "lat": 35.0, "lon": 105.0},
            {"name": "Global EV/battery markets", "role": "Consumer", "lat": 38.9, "lon": -77.0},
        ],
        "why_it_matters": "Cobalt is essential to most current EV battery chemistries and to aerospace superalloys and precision-guided munitions -- a genuinely dual-use dependency sitting directly alongside an active, under-covered conflict.",
        "alternative_suppliers": "Limited near-term alternatives; some battery chemistries (LFP) are reducing cobalt intensity, similar to the nickel story below.",
        "current_status": "Active tension -- 2026 export quota changes have created real friction with Chinese investors, alongside ongoing M23-linked instability in the mining regions themselves.",
        "sources": ["USGS Mineral Commodity Summaries 2026", "DRC government export policy announcements", "UN Group of Experts on the DRC reporting"],
    },
    "indonesia_nickel": {
        "name": "Indonesia's Nickel Dominance -- A Monopoly Losing Strategic Value",
        "category": "civilian",
        "linked_conflict": None,
        "last_reviewed": "2026-09-04",
        "stat_callouts": [
            {"stat": "60%+ of global nickel supply",
             "detail": "Indonesia is the overwhelming source of the world's nickel."},
            {"stat": "Chinese firms control ~75% of Indonesia's own smelting capacity",
             "detail": "$25B+ invested since 2019 -- the same 'controls the processing, not just uses the ore' pattern as cobalt and rare earths."},
            {"stat": "The twist: battery chemistry is moving away from nickel",
             "detail": "China's own EV market is now ~80% LFP (nickel-free); a new nickel-free BYD model got 150,000 pre-orders. Even 90%+ of Indonesia's OWN domestic EV market runs on non-nickel batteries."},
            {"stat": "Indonesia remains a net importer of finished battery systems",
             "detail": "85-95% of domestic demand met by imports (60-70% from China) -- mining dominance hasn't captured the full value chain."},
        ],
        "chain_nodes": [
            {"name": "Indonesia (Sulawesi/Morowali)", "role": "Mining/Processing", "lat": -2.5, "lon": 121.0},
            {"name": "China (investment & refining control)", "role": "Processing", "lat": 35.0, "lon": 105.0},
            {"name": "Global EV/battery markets", "role": "Consumer", "lat": 38.9, "lon": -77.0},
        ],
        "why_it_matters": "This is a genuinely sophisticated case: a country can hold overwhelming PHYSICAL dominance over a resource and still see its strategic LEVERAGE erode if the underlying technology shifts away from needing that resource -- worth watching as a template for how resource monopolies can lose relevance without losing market share.",
        "alternative_suppliers": "Not really the right frame here -- the more relevant dynamic is battery chemistry substitution reducing nickel demand itself, not alternative nickel suppliers.",
        "current_status": "Actively evolving -- 2026 export quota cuts and regulatory reversals have strained relations with Chinese investors even as nickel's strategic importance itself is in question.",
        "sources": ["Indonesian Ministry of Energy and Mineral Resources data", "BYD/CATL battery chemistry announcements", "reporting on Indonesia's 2026 nickel export policy changes"],
    },
    "india_pharma_api": {
        "name": "India's Generic Pharmaceuticals -- With a Hidden China Dependency",
        "category": "civilian",
        "linked_conflict": None,
        "last_reviewed": "2026-09-04",
        "stat_callouts": [
            {"stat": "India: world's largest exporter of generic medicines",
             "detail": "40% of US generic demand, ~half of Africa's generic medicine needs, 25% of UK's generic demand -- the 'Pharmacy of the World.'"},
            {"stat": "But India imports 65-72% of its own API/key starting materials from China",
             "detail": "Confirmed by India's own government think tank (NITI Aayog, June 2026) -- including 100% dependency for 45 critical bulk drugs."},
            {"stat": "'17% of US API imports from China' is technically true but misleading",
             "detail": "Tracing the full chain -- including Chinese-sourced inputs flowing through India -- puts China's EFFECTIVE control over the US generic drug supply closer to 80%."},
            {"stat": "Real policy response underway",
             "detail": "India's Production Linked Incentive scheme and dedicated API parks (Gujarat hub) aim for 20-25% capacity increases, though progress is described as incremental."},
        ],
        "chain_nodes": [
            {"name": "China", "role": "API/Precursor Source", "lat": 35.0, "lon": 105.0},
            {"name": "India (Gujarat/Hyderabad hubs)", "role": "Formulation/Manufacturing", "lat": 23.0, "lon": 72.6},
            {"name": "US/Africa/UK (representative: US)", "role": "Consumer", "lat": 38.9, "lon": -77.0},
        ],
        "why_it_matters": "This is the most consequential example of a hidden, multi-tier dependency in the whole set -- most public statistics about 'China's share of the drug supply' miss the fact that India's OWN manufacturing is itself deeply China-dependent, meaning the real chain has an extra invisible link that simple trade statistics don't capture.",
        "alternative_suppliers": "Domestic Indian API capacity-building is underway but described by analysts as yielding only incremental gains so far, not a near-term structural fix.",
        "current_status": "Active government focus, unresolved dependency -- worth revisiting as India's PLI scheme matures.",
        "sources": ["NITI Aayog pharmaceutical sector report, June 2026", "US FDA API sourcing disclosures", "India Ministry of Chemicals and Fertilizers PLI scheme documentation"],
    },
}


def get_node(node_id: str) -> dict | None:
    return SUPPLY_CHAIN_NODES.get(node_id)


def get_nodes_for_conflict(conflict_key: str) -> list[dict]:
    """Returns all supply chain nodes linked to a given conflict_backgrounds.py
    entry, for enriching that dossier's display."""
    return [
        {**node, "node_id": node_id}
        for node_id, node in SUPPLY_CHAIN_NODES.items()
        if node.get("linked_conflict") == conflict_key
    ]


def get_unlinked_nodes() -> list[dict]:
    """Returns nodes that don't map cleanly onto a tracked conflict -- these
    render in a separate standalone section rather than inside a dossier."""
    return [
        {**node, "node_id": node_id}
        for node_id, node in SUPPLY_CHAIN_NODES.items()
        if node.get("linked_conflict") is None
    ]


def get_all_nodes() -> dict:
    return SUPPLY_CHAIN_NODES
