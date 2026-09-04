"""
Manually-curated conflict background/timeline/analysis data.

Deliberately NOT auto-scraped -- deciding what belongs in a conflict's
historical record, and forming analytical judgments about actors, risk,
and outlook, is editorial/analytical work that shouldn't be automated.
This is meant to be periodically reviewed and extended by hand (or via a
research session), not continuously generated.

Each timeline entry should be independently verifiable -- cite the actual
source, and where casualty/outcome claims are disputed between parties,
say so explicitly rather than picking a side.

Analytical fields (actors, outlook, triggers, risk level, etc.) are
Claude's synthesis grounded in the cited timeline sources -- clearly
judgment calls, not verified facts, and should be read as informed
assessment rather than certainty. Where a conflict has genuinely disputed
casualty/attribution claims, the confidence_level field says so explicitly
rather than picking a side.
"""

CONFLICTS = {
    "pakistan_afghanistan_2025": {
        "name": "Pakistan-Afghanistan Border War",
        "regions": ["Pakistan", "Afghanistan"],
        "started": "2025-10-09",
        "last_reviewed": "2026-08-30",
        "status": "active",
        "risk_level": "High",
        "status_summary": (
            "Ongoing since October 2025. Three separate ceasefires have "
            "collapsed. As of the last verified update (June 29, 2026), "
            "both sides continue cross-border strikes with disputed "
            "casualty figures on each incident."
        ),
        "timeline": [
            {"date": "2025-10-09", "event": "Initial clashes along the Durand Line; ACLED recorded 107 armed incidents in this period",
             "source": "EUAA/UN country report", "url": "https://www.euaa.europa.eu/coi-report-afghanistan-country-focus/223-clashes-and-airstrikes-involving-pakistan"},
            {"date": "2026-02-21", "event": "Pakistan airstrikes on alleged TTP camps in Nangarhar, Paktika, Khost",
             "source": "UN OHCHR", "url": "https://www.ohchr.org/en/press-releases/2026/03/afghan-pakistani-border-un-experts-urgently-call-lasting-peace"},
            {"date": "2026-02-27", "event": "Pakistan's Defense Minister declares 'open war'; strikes on Kabul, Kandahar, Paktia",
             "source": "Britannica", "url": "https://www.britannica.com/topic/Afghanistan-Pakistan-Conflict-2025"},
            {"date": "2026-03-16", "event": "Disputed strike on a Kabul facility Afghanistan describes as a drug rehabilitation hospital -- "
                                              "Taliban says 400+ killed, Pakistan disputes the characterization and says it hit a militant camp",
             "source": "Peace Direct / Britannica", "url": "https://www.peacedirect.org/afghanistan-pakistan-2026/"},
            {"date": "2026-03-26", "event": "Eid ceasefire (brokered by Saudi Arabia, Turkey, Qatar) collapses; fighting resumes in Kunar",
             "source": "India state broadcaster", "url": "https://www.newsonair.gov.in/fighting-resumed-at-afghanistan-pakistan-border-after-temporary-ceasefire-expired"},
            {"date": "2026-04-27", "event": "Renewed cross-border attacks, ceasefire described as 'at risk'",
             "source": "Al Jazeera", "url": "https://www.aljazeera.com/news/2026/4/27/ceasefire-at-risk-as-pakistan-and-afghanistan-report-cross-border-attacks"},
            {"date": "2026-06-29", "event": "Pakistan strikes kill 29 fighters per Islamabad; Afghanistan says 36 civilians killed, 163 wounded -- "
                                              "same disputed-casualties pattern, now with named officials on record",
             "source": "Al Jazeera", "url": "https://www.aljazeera.com/news/2026/6/29/pakistan-says-its-security-forces-killed-29-fighters-along-afghan-border"},
        ],
        "un_figures": "At least 289 civilian casualties in Afghanistan (76 killed, 213 injured) since Feb 26, 2026; 115,000+ displaced, per UN OHCHR as of March 2026",

        "key_actors": [
            {"actor": "Pakistan government/military", "objective": "Eliminate TTP safe havens in Afghan territory; stop cross-border militant attacks"},
            {"actor": "Afghan Taliban authorities", "objective": "Assert sovereignty; resist Pakistani strikes on their territory; avoid appearing complicit with Pakistan against TTP"},
            {"actor": "Tehreek-e-Taliban Pakistan (TTP)", "objective": "Continue insurgency against the Pakistani state; exploit Afghan territory as a safe haven"},
            {"actor": "Saudi Arabia, Turkey, Qatar (mediators)", "objective": "Broker stability; protect wider regional interests and their own mediation credibility"},
        ],
        "regional_linkages": "Pakistan brokered the April 2026 Islamabad Talks in the separate Iran war, giving it added regional standing it may be leveraging amid its own border conflict. The same Gulf mediators (Saudi Arabia, Turkey, Qatar) are involved in both this conflict's ceasefires and broader regional de-escalation efforts.",
        "outlook_30_90": "Given three prior ceasefires have all collapsed within weeks, another announced truce is plausible, but a durable one within 90 days looks unlikely without a change in either side's core demands. Watch for a possible seasonal truce attempt around any major religious holiday, following the Eid pattern.",
        "escalation_triggers": [
            "A mass-casualty strike blamed on the other side (repeating the March 16 pattern)",
            "Either side formally abandoning border demarcation talks",
            "A major TTP attack inside Pakistan attributed to Afghan-based militants",
        ],
        "early_warning_indicators": [
            "Border crossing closures at Torkham or Chaman",
            "Troop mobilization near Kunar, Nangarhar, Paktika, or Paktia",
            "Statements from Saudi/Turkish/Qatari mediators on talks restarting or collapsing",
        ],
        "second_order_effects": {
            "trade": "Torkham/Chaman closures disrupt Afghanistan's primary trade routes to Pakistani ports",
            "migration": "Continued instability risks renewed Afghan refugee flows into Pakistan",
            "humanitarian": "115,000+ already displaced per UN OHCHR, likely to grow with continued fighting",
        },
        "confidence_level": "Moderate -- casualty and target-characterization claims are consistently disputed between the two governments (see the March 16 strike). UN OHCHR figures are the most independently verifiable data point available.",
        "strategic_chokepoints": [],
    },

    "iran_war_2026": {
        "name": "2026 Iran War, Strait of Hormuz Crisis & Gaza Ceasefire",
        "regions": ["Iran", "Israel", "Yemen", "Saudi Arabia", "Qatar"],
        "started": "2026-02-28",
        "last_reviewed": "2026-09-03",
        "status": "active",
        "risk_level": "Critical",
        "status_summary": (
            "Began with US-Israeli airstrikes on Iran; a ceasefire on April "
            "7-8 never fully held. Late August saw a return to direct kinetic "
            "exchange -- tanker strikes near Hormuz, a US strike on Larak "
            "Island, and Iranian retaliation reaching Jordan and the UAE -- "
            "alongside an intensifying economic-pressure campaign (Bessent's "
            "'Hormuz worthless within two years' framing signals a long-game "
            "US strategy of economic bypass over rapid diplomatic resolution). "
            "Sanctions and direct kinetic exchange are now running in parallel "
            "-- a genuinely multi-domain active conflict, not just an "
            "economic-pressure campaign with occasional flare-ups. The war "
            "has directly stalled progress on the separate Gaza ceasefire, "
            "which began October 10, 2025 -- the Trump administration's "
            "attention has been consumed by Iran, leaving Gaza's 20-point "
            "peace plan largely unimplemented beyond its initial phase."
        ),
        "timeline": [
            {"date": "2025-10-10", "event": "Gaza ceasefire takes effect under Trump's 20-Point Plan, endorsed by UN Security Council Resolution 2803 (the separate conflict this war has since overshadowed)",
             "source": "J Street", "url": "https://jstreet.org/nine-months-in-assessing-the-status-of-the-gaza-ceasefire/"},
            {"date": "2026-02-28", "event": "US and Israel launch airstrikes on Iran, including the assassination of Supreme Leader Ali Khamenei",
             "source": "Wikipedia (2026 Iran war)", "url": "https://en.wikipedia.org/wiki/2026_Iran_war"},
            {"date": "2026-02-28", "event": "Iran retaliates with missile/drone strikes on Israel, US bases, and US-allied Middle East states; closes the Strait of Hormuz",
             "source": "Wikipedia (2026 Iran war ceasefire)", "url": "https://en.wikipedia.org/wiki/2026_Iran_war_ceasefire"},
            {"date": "2026-04-07", "event": "US and Iran agree to a two-week ceasefire, mediated by Pakistan (the 'Islamabad Talks')",
             "source": "Wikipedia (2026 Iran war ceasefire)", "url": "https://en.wikipedia.org/wiki/2026_Iran_war_ceasefire"},
            {"date": "2026-04-13", "event": "Islamabad Talks fail; US imposes a naval blockade on Iran",
             "source": "Congress.gov CRS report", "url": "https://www.congress.gov/crs-product/R45281"},
            {"date": "2026-06", "event": "Memorandum of understanding reached, seeking to end the war and reopen the Strait",
             "source": "Britannica (2026 Iran war)", "url": "https://www.britannica.com/event/2026-Iran-war"},
            {"date": "2026-07-06", "event": "Three ships attacked in the Strait; Iran continues asserting control despite the MOU, provoking renewed US strikes",
             "source": "Britannica (2026 Iran war)", "url": "https://www.britannica.com/event/2026-Iran-war"},
            {"date": "2026-07-20", "event": "J Street's nine-month Gaza ceasefire assessment explicitly attributes stalled progress to the Trump administration being 'distracted by the ongoing conflict with Iran'",
             "source": "J Street", "url": "https://jstreet.org/nine-months-in-assessing-the-status-of-the-gaza-ceasefire/"},
            {"date": "2026-08-28", "event": "Iranian rial hits a record low (~210,000 rial); domestic gasoline shortages reported, with officials attributing lines partly to increased travel and partly to reserve drawdowns",
             "source": "Radio Farda", "url": "https://www.radiofarda.com/a/iran-currency-new-record-210-thousands-rial/33844113.html"},
            {"date": "2026-08-31", "event": "Two oil supertankers struck by projectiles near the Strait of Hormuz; UKMTO confirmed, IRGC claims mines were used.", "source": "Bloomberg, UKMTO, IranWire"},
            {"date": "2026-08-31", "event": "US strikes IRGC targets on Iran's Larak Island.", "source": "CENTCOM"},
            {"date": "2026-08-31", "event": "Iran launches retaliatory strikes on US-linked targets in Jordan and the UAE.", "source": "Al Jazeera, The Hill"},
            {"date": "2026-09-01", "event": "Iranian President Pezeshkian meets Putin at the SCO summit in Bishkek; Putin reaffirms Russian support for Iran; Pezeshkian signals openness to US talks \"if US returns to its commitments.\"", "source": "The Tribune"},
            {"date": "2026-09-01", "event": "US Treasury Secretary Bessent tells G20 meeting Hormuz will be \"worthless\" within two years.", "source": "The National"},
        ],
        "casualties": "1 tugboat sunk, 17+ merchant ships damaged (7 abandoned), 2 ships captured, 12 seafarers killed or missing, 1 port worker killed in Bahrain, per Wikipedia's 2026 Strait of Hormuz crisis tracker",
        "chokepoint_impact": "Strait of Hormuz (20-25% of world seaborne oil trade) has been disrupted/contested since the war began -- see the Chokepoints reference on the map for live status",
        "gaza_status": "As of August 26, 2026: 73,438+ confirmed Palestinian deaths since Oct 7, 2023 (incl. 21,500 children) per Gaza Health Ministry; only 35% of pledged aid trucks (66,607 of 189,000) have entered since the October 2025 ceasefire, per Gaza Government Media Office",

        "key_actors": [
            {"actor": "United States", "objective": "Prevent Iranian nuclear breakout; protect Israel and Gulf allies; restore free passage through Hormuz"},
            {"actor": "Israel", "objective": "Neutralize Iranian leadership and nuclear program; degrade Iran's regional proxy network"},
            {"actor": "Iran", "objective": "Regime survival; deter further strikes via Hormuz leverage; maintain its proxy network including the Houthis"},
            {"actor": "Yemen's Houthis", "objective": "Support Iran's axis; continue Red Sea disruption framed as Gaza solidarity"},
            {"actor": "Gulf states (Saudi Arabia, Qatar, UAE)", "objective": "Avoid direct entanglement; protect their own energy exports; position as mediators"},
            {"actor": "Hamas", "objective": "Survive as Gaza's governing/military force; extract concessions through the stalled ceasefire process"},
            {"actor": "Pakistan", "objective": "Regional mediator role, which also raises its standing amid its own border conflict"},
        ],
        "regional_linkages": "Directly stalls the separate Gaza ceasefire (Trump administration bandwidth consumed by Iran). Analysts link China's more assertive South China Sea posture to a belief the US is 'preoccupied in the Persian Gulf.' South Korea-US talks have explicitly referenced needing Seoul's help securing Hormuz passage -- a Gulf crisis reaching into Korean Peninsula diplomacy. Russia-Iran alignment is visibly strengthening (the Aug 31-Sept 1 Putin-Pezeshkian SCO meeting and public Russian backing) at the same time Russia itself faces intensifying Western economic pressure over Ukraine -- see the Russia-Ukraine dossier for the reverse link.",
        "outlook_30_90": "Short-term, expect continued tit-for-tat -- further Iranian harassment of Hormuz shipping met with targeted US strikes on IRGC assets. Both sides appear to be signaling controlled escalation (targeted, not maximal), which keeps near-term full-scale war unlikely. Medium-term, economic attrition becomes the dominant axis: a weakening rial and fuel shortages carry real domestic unrest risk, given Iran's history of fuel-price-triggered protests. The open question is whether internal economic pressure forces Tehran back to the table faster than Russian/Chinese support can offset the sanctions campaign.",
        "escalation_triggers": [
            "A US or Israeli strike killing senior IRGC or Iranian officials",
            "A successful Iranian attack sinking a US or allied naval vessel",
            "Iran moving toward an overt nuclear weapons test",
            "Further US strikes on Iranian territory beyond the Larak Island precedent",
            "Iran targeting additional Gulf state assets beyond Jordan and the UAE",
            "A move toward full enforcement of Hormuz closure",
        ],
        "early_warning_indicators": [
            "Insurance and shipping rates for Hormuz transits",
            "IRGC naval vessel movements reported via OSINT/AIS tracking",
            "Statements from Gulf states on evacuating diplomatic staff",
            "A strike on a neutral-flagged vessel (e.g. Indian- or Chinese-flagged) -- would signal expanding, less controlled targeting",
            "Any sign of direct Russian/Chinese military materiel reaching Iran, not just rhetorical solidarity",
            "Domestic unrest in Iran specifically tied to fuel shortages or currency collapse -- a historically real flashpoint",
            "Shifts in Saudi/UAE posture -- either tightening security cooperation with US CENTCOM, or conversely hedging toward direct engagement with Tehran to reduce their own exposure",
        ],
        "second_order_effects": {
            "energy": "Hormuz carries 20-25% of global oil trade; disruption directly drives global fuel prices, evidenced by the Philippines' March 2026 energy emergency thousands of miles away",
            "shipping": "17+ merchant ships already damaged; insurance costs for the route have risen sharply. Given Hormuz's centrality to Asian crude imports, sustained disruption has real knock-on exposure for India, China, Japan, and South Korea specifically.",
            "trade": "Qatar and UAE, as regional trade/logistics hubs, face indirect economic exposure even without direct attacks on their territory",
        },
        "confidence_level": "Moderate to low on casualty/attribution specifics -- Wikipedia and Britannica trackers here are secondary aggregators of primary reporting. Gaza casualty figures (Palestinian Health Ministry) and ceasefire violation counts (Gaza Government Media Office) are both party-reported, not independently verified by a neutral body. Iranian claims about strike attribution and casualties often can't be independently verified in real time. CENTCOM/Treasury statements are more directly attributable but represent one side's framing -- treat both with appropriate caution.",
        "strategic_chokepoints": ["strait_of_hormuz", "bab_el_mandeb"],
    },

    "south_china_sea_2026": {
        "name": "South China Sea Dispute (China-Philippines)",
        "regions": ["South China Sea", "China", "Philippines"],
        "started": "2016-07",
        "last_reviewed": "2026-08-30",
        "status": "active",
        "risk_level": "Medium-High",
        "status_summary": (
            "A long-running dispute over China's 'nine-dash line' claims, "
            "rejected by a 2016 international tribunal. 2026 has seen a "
            "shift toward 'hybrid' confrontation -- maritime militia "
            "harassment, intelligence operations -- alongside periodic "
            "direct clashes. Analysts note China may be acting more "
            "assertively in 2026 partly because it judges the US to be "
            "distracted by the Iran war."
        ),
        "timeline": [
            {"date": "2016-07", "event": "Permanent Court of Arbitration rules against China's nine-dash line claim; China rejects the ruling",
             "source": "CFR Global Conflict Tracker", "url": "https://www.cfr.org/global-conflict-tracker/conflict/territorial-disputes-south-china-sea"},
            {"date": "2026-01-29", "event": "China and Philippines meet in Cebu after nearly a year of frozen dialogue; progress reported on updating their coast guard MoU",
             "source": "Fulcrum/Asialink", "url": "https://fulcrum.sg/between-talks-and-tensions-why-the-south-china-sea-wont-stabilise-in-2026/"},
            {"date": "2026-03", "event": "Strait of Hormuz closure pushes the Philippines into a national energy emergency; President Marcos signals openness to restarting joint oil/gas talks with China at Reed Bank",
             "source": "Fulcrum/Asialink", "url": "https://fulcrum.sg/between-talks-and-tensions-why-the-south-china-sea-wont-stabilise-in-2026/"},
            {"date": "2026-04", "event": "A confirmed intelligence breach exposes Philippine naval operations, allowing Chinese forces to anticipate movements -- a notable hybrid-warfare escalation",
             "source": "WARWATCH Analysis", "url": "https://warwatchlive.com/analysis/south-china-sea-philippines-2026.html"},
            {"date": "2026-07", "event": "China and Philippines clash three times in a single week at Scarborough Shoal and Second Thomas Shoal; joint US-Philippines-Japan maritime drills follow; Japan deploys combat troops to Balikatan for the first time since 1945",
             "source": "CFR Global Conflict Tracker", "url": "https://www.cfr.org/global-conflict-tracker/conflict/territorial-disputes-south-china-sea"},
            {"date": "2026-08-03", "event": "Analysts describe the dispute entering a 'more dangerous phase,' citing a view that Beijing believes the US is too preoccupied in the Persian Gulf to respond decisively even if Manila invokes the Mutual Defense Treaty",
             "source": "China-Global South Project", "url": "https://chinaglobalsouth.com/2026/08/03/china-philippines-south-china-sea-dispute-dangerous-phase/"},
            {"date": "2026-08-27", "event": "China accuses the Philippines of 'flagrantly infringing' on its sovereignty after Manila formally presents a UN bid for extended seabed rights",
             "source": "CFR Global Conflict Tracker", "url": "https://www.cfr.org/global-conflict-tracker/conflict/territorial-disputes-south-china-sea"},
        ],

        "key_actors": [
            {"actor": "China", "objective": "Assert nine-dash-line claims; deny US-allied basing/access; control resource-rich waters"},
            {"actor": "Philippines", "objective": "Defend EEZ claims; secure US Mutual Defense Treaty backing; avoid direct war"},
            {"actor": "United States", "objective": "Maintain freedom of navigation; preserve credibility of alliance commitments"},
            {"actor": "Japan", "objective": "Support the Philippines to deter Chinese assertiveness that could otherwise extend to its own territorial disputes"},
            {"actor": "Vietnam, Malaysia, Brunei", "objective": "Secondary claimants -- generally quieter, but share the Philippines' core concern about Chinese claims"},
        ],
        "regional_linkages": "Analysts explicitly tie China's 2026 assertiveness to the belief the US is distracted by the Iran war. The same Trump-Xi summit cadence that's moderating Taiwan tensions has NOT extended to the South China Sea, suggesting Beijing is treating this dispute differently -- more opportunistically -- than the Taiwan question.",
        "outlook_30_90": "Given the shift to hybrid tactics (intelligence operations, militia harassment) rather than direct clashes, continued low-intensity friction is the most likely course. A repeat of the July 2026 pattern -- multiple clashes in a single week -- is plausible around any ASEAN Summit-related diplomatic moment, given the Philippines chairs ASEAN in 2026.",
        "escalation_triggers": [
            "A fatality in a coast guard confrontation (none confirmed as of this research)",
            "China declaring an Air Defense Identification Zone over contested areas",
            "A US warship directly intervening in a Philippines resupply mission",
        ],
        "early_warning_indicators": [
            "China Coast Guard vessel concentrations near Second Thomas or Scarborough Shoal",
            "PLA Navy live-fire drill announcements",
            "The Philippines formally invoking the Mutual Defense Treaty",
        ],
        "second_order_effects": {
            "shipping": "The South China Sea carries a major share of global trade transiting to and from the Strait of Malacca",
            "energy": "Reed Bank joint development talks, paused amid tension, sit atop undeveloped oil/gas reserves",
            "trade": "A collapse of ASEAN Code of Conduct negotiations could destabilize wider regional trade diplomacy",
        },
        "confidence_level": "Moderate -- CFR, Crisis Group, and multiple independent outlets consistently corroborate the broad pattern of clashes, though precise attribution of who-rammed-whom in individual incidents is often disputed between Manila and Beijing.",
        "strategic_chokepoints": ["strait_of_malacca"],
    },

    "china_taiwan_2026": {
        "name": "China-Taiwan Cross-Strait Tensions",
        "regions": ["Taiwan", "China"],
        "started": "2022-08",
        "last_reviewed": "2026-08-30",
        "status": "active",
        "risk_level": "Medium",
        "status_summary": (
            "Tensions have run lower in the first half of 2026 than at the "
            "end of 2025, largely due to direct Xi-Trump summits creating "
            "diplomatic off-ramps. PLA military activity measurably drops "
            "around each summit, then resumes -- a genuine, recurring "
            "pattern rather than a one-off."
        ),
        "timeline": [
            {"date": "2022-08", "event": "Speaker Pelosi's Taiwan visit sharply raises cross-strait tensions; PLA aircraft begin crossing the median line on a near-daily basis, a practice that continues",
             "source": "CFR Global Conflict Tracker", "url": "https://www.cfr.org/global-conflict-tracker/conflict/confrontation-over-taiwan"},
            {"date": "2026-01-02", "event": "Beijing fires rockets toward Taiwan as part of military drills; President Lai Ching-te vows to defend sovereignty, calls 2026 'a crucial year'",
             "source": "India state broadcaster", "url": "https://www.newsonair.gov.in/taiwan-president-vows-to-defend-sovereignty-and-boost-defence-amid-chinas-military-drills"},
            {"date": "2026-05-13", "event": "Xi-Trump summit in Beijing (May 13-17); daily PLA aircraft sorties around Taiwan drop to an average of 3/day (from a first-half average of 7.5), zero sorties on May 14-15",
             "source": "The Diplomat", "url": "https://thediplomat.com/2026/07/china-moves-to-lock-in-a-new-edge-on-taiwan-before-the-next-trump-xi-summit/"},
            {"date": "2026-05-19", "event": "Immediately after the summit, PLA conducts a joint combat readiness patrol; Taiwan detects 24 military aircraft that day",
             "source": "The Diplomat", "url": "https://thediplomat.com/2026/07/china-moves-to-lock-in-a-new-edge-on-taiwan-before-the-next-trump-xi-summit/"},
            {"date": "2026-08-14", "event": "Tracked as 'Elevated intensity' -- PLA aircraft and vessels routinely cross the median line, which no longer functions as an operational boundary",
             "source": "Taiwan Strait Tensions Tracker", "url": "https://armedconflicts.org/taiwan-strait-tensions.html"},
        ],
        "pattern_note": "A recurring pattern across three of your tracked conflicts: PLA activity near Taiwan measurably drops around Xi-Trump summits (May 2026), the same summit cadence that produced the June 2026 China trade truce -- diplomatic engagement on one front appears to correlate with de-escalation on others.",

        "key_actors": [
            {"actor": "China / PLA", "objective": "Deter formal independence moves; maintain pressure without triggering war; long-term unification goal"},
            {"actor": "Taiwan under President Lai", "objective": "Defend de facto sovereignty; avoid provoking overt invasion; deepen informal international ties"},
            {"actor": "United States", "objective": "Maintain strategic ambiguity; continue arms sales to Taiwan; deter invasion without provoking one"},
            {"actor": "Japan", "objective": "Deeply concerned a Taiwan contingency would directly threaten its own security"},
        ],
        "regional_linkages": "Tensions correlate inversely with US-China trade diplomacy -- both eased around the same May 2026 Xi-Trump summit, suggesting Beijing links Taiwan pressure to the broader US relationship rather than treating it in isolation.",
        "outlook_30_90": "Given the pattern of sortie counts dropping around summits then resuming, expect another dip around the planned September 2026 Xi-Trump summit, followed by a return to elevated baseline activity. No indicators currently point to an imminent invasion attempt within 90 days.",
        "escalation_triggers": [
            "A high-profile US political visit to Taiwan (repeating the 2022 Pelosi-visit pattern)",
            "A formal Taiwanese declaration of independence",
            "A PLA aircraft or vessel collision with a US or Taiwanese asset",
        ],
        "early_warning_indicators": [
            "Daily PLA aircraft sortie counts (baseline ~7.5/day -- watch for sustained spikes)",
            "Chinese amphibious/logistics ship movements near Fujian province",
            "Taiwanese reservist mobilization announcements",
        ],
        "second_order_effects": {
            "supply_chains": "Taiwan produces the large majority of the world's advanced semiconductors -- any conflict would be a severe global supply-chain shock",
            "shipping": "The Taiwan Strait is a major regional shipping corridor independent of the semiconductor issue",
        },
        "confidence_level": "High for aggregate sortie-count data (Taiwan's Ministry of National Defense publishes this daily). Lower for intent/planning assessments, which are necessarily speculative.",
        "strategic_chokepoints": [],
    },

    "korea_2026": {
        "name": "North Korea-South Korea / US Tensions",
        "regions": ["North Korea", "South Korea"],
        "started": "1953-07",
        "last_reviewed": "2026-08-30",
        "status": "active",
        "risk_level": "Medium",
        "status_summary": (
            "The two Koreas remain technically at war (1953 armistice, no "
            "peace treaty). 2026 has seen North Korea deepen ties with "
            "Russia and China while testing new missile technology, "
            "alongside an unusual dynamic where Trump has pushed to reduce "
            "US-South Korea joint exercises to avoid provoking Pyongyang."
        ),
        "timeline": [
            {"date": "2026-01-04", "event": "North Korea carries out a ballistic missile test over the Sea of Japan",
             "source": "Wikipedia (2026 in North Korea)", "url": "https://en.wikipedia.org/wiki/2026_in_North_Korea"},
            {"date": "2026-03-12", "event": "Beijing-Pyongyang train service resumes after a suspension dating to the COVID-19 pandemic",
             "source": "Wikipedia (2026 in North Korea)", "url": "https://en.wikipedia.org/wiki/2026_in_North_Korea"},
            {"date": "2026-05", "event": "China and Russia issue a joint statement opposing sanctions or military pressure on North Korea",
             "source": "AEI Korean Peninsula Update", "url": "https://www.aei.org/articles/korean-peninsula-update-june-16-2026/"},
            {"date": "2026-06-02", "event": "South Korea-US consultations on SSN development explicitly discuss the need for South Korean cooperation to help secure freedom of passage in the Strait of Hormuz",
             "source": "AEI Korean Peninsula Update", "url": "https://www.aei.org/articles/korean-peninsula-update-june-9-2026/"},
            {"date": "2026-07-14", "event": "Ukrainian military intelligence confirms North Korea is supplying Russia with an estimated 25-40% of its current artillery ammunition for the Ukraine war",
             "source": "AEI Korean Peninsula Update", "url": "https://www.aei.org/articles/korean-peninsula-update-july-14-2026/"},
            {"date": "2026-08-06", "event": "North Korea conducts a missile launch, followed by another on August 12 -- unusually silent about both, suggesting new missile technology being tested",
             "source": "AEI Korean Peninsula Update", "url": "https://www.aei.org/commentary/korean-peninsula-update-august-19-2026/"},
            {"date": "2026-08-14", "event": "North Korea denounces upcoming US-South Korea military drills, accuses the trilateral US-Japan-South Korea cooperation of 'turning into a nuclear alliance'",
             "source": "Al Jazeera", "url": "https://www.aljazeera.com/news/2026/8/14/north-korea-fumes-over-upcoming-us-south-korea-military-drills"},
            {"date": "2026-08-19", "event": "Trump instructs the Pentagon to reduce US-South Korea combined exercises to avoid an 'hostile' signal to North Korea; Pyongyang remains unlikely to accept dialogue overtures",
             "source": "AEI Korean Peninsula Update", "url": "https://www.aei.org/commentary/korean-peninsula-update-august-19-2026/"},
        ],
        "cross_conflict_note": "North Korea's material support for Russia's Ukraine war (25-40% of artillery) directly links this conflict to the Russia-Ukraine war tracked elsewhere on your dashboard.",

        "key_actors": [
            {"actor": "North Korea / Kim Jong Un", "objective": "Regime survival; consolidate nuclear deterrent; generate revenue via arms trade with Russia"},
            {"actor": "South Korea / Lee Jae Myung", "objective": "Avoid provocation; pursue engagement where possible; maintain the US alliance"},
            {"actor": "United States / Trump", "objective": "Reduce risk of unwanted escalation -- has actively pushed to scale back joint drills, a departure from prior posture"},
            {"actor": "China and Russia", "objective": "Shield North Korea from sanctions pressure; deepen their own strategic partnerships with Pyongyang"},
        ],
        "regional_linkages": "North Korea's 25-40% contribution to Russia's Ukraine-war artillery stock directly ties this conflict to Russia-Ukraine. South Korea has separately been asked to help secure Hormuz passage, tying it to the Iran war despite having no direct stake in the Gulf.",
        "outlook_30_90": "Trump's push to reduce joint exercises is a genuine departure from prior US posture; if sustained, watch for whether Pyongyang responds with any reciprocal de-escalation (historically it has not reliably done so). Continued North Korean missile testing, particularly of the new intermediate-range system suggested by the August tests, looks likely.",
        "escalation_triggers": [
            "A North Korean nuclear test (a long-anticipated 7th test that has not yet occurred)",
            "A North Korean provocation at the Northern Limit Line",
            "A South Korean pivot to direct military support for Ukraine, which Seoul has so far avoided",
        ],
        "early_warning_indicators": [
            "North Korean missile test frequency and silence patterns (recent tests have broken from normal announcement practice)",
            "Kim Ju Ae's public appearance frequency, read as a succession signal",
            "China-North Korea rail and trade resumption patterns",
        ],
        "second_order_effects": {
            "cyber": "North Korea remains a major source of state-linked cybercrime and cryptocurrency theft funding its weapons programs",
            "trade": "Sanctions evasion via China/Russia trade undermines the wider international sanctions regime",
        },
        "confidence_level": "Moderate -- AEI/ISW's Korean Peninsula Update is a rigorous, frequently-updated Western source, but North Korean state media (KCNA) is unreliable, and Pyongyang's silence on some recent tests limits independent verification of technical details.",
        "strategic_chokepoints": [],
    },

    "us_china_trade_2026": {
        "name": "US-China Trade War",
        "regions": ["China"],
        "started": "2018",
        "last_reviewed": "2026-08-30",
        "status": "active",
        "risk_level": "Medium",
        "status_summary": (
            "A fragile truce has held since the May 2026 Xi-Trump summit, "
            "but neither side has fully de-escalated -- new tariffs "
            "continue to be layered on even as both governments negotiate "
            "a formal reduction mechanism. Another Xi-Trump summit is "
            "expected in September 2026."
        ),
        "timeline": [
            {"date": "2026-02", "event": "US Supreme Court overrules some of Trump's proposed tariffs, forcing the administration to rely on other legal authorities; the bulk of China tariffs remain in place",
             "source": "CFR Backgrounder", "url": "https://www.cfr.org/backgrounders/contentious-us-china-trade-relationship"},
            {"date": "2026-05-13", "event": "Xi-Trump summit in Beijing produces a fragile truce; both sides agree to set up formal trade and investment boards to identify tariffs for possible removal",
             "source": "Congress.gov CRS", "url": "https://www.congress.gov/crs-product/IF11284"},
            {"date": "2026-06-02", "event": "USTR opens public comment on a proposed US-China Board of Trade, a bilateral mechanism to evaluate tariff reductions on non-sensitive goods",
             "source": "RVIA", "url": "https://www.rvia.org/news-insights/latest-tariff-developments"},
            {"date": "2026-07-24", "event": "New Section 301 tariffs (10-12.5%) take effect on 60 economies including China, over forced-labor enforcement findings -- stacking with existing China tariffs",
             "source": "Dimerco", "url": "https://dimerco.com/us-tariff-update-2026/"},
            {"date": "2026-08-24", "event": "US set to impose a new 7.5% tariff on Chinese goods over alleged manufacturing overcapacity, ahead of a planned September Xi-Trump summit -- would restore total duties to ~20%, a level Beijing has called consistent with the trade truce",
             "source": "Bloomberg", "url": "https://www.bloomberg.com/news/articles/2026-08-24/us-eyes-china-overcapacity-tariffs-of-7-5-before-xi-trump-talks"},
        ],
        "pattern_note": "The same Xi-Trump summit cadence driving this truce (May 2026, planned September 2026) correlates with measurable de-escalation in the separate Taiwan Strait tensions -- worth watching both together.",

        "key_actors": [
            {"actor": "US / Trump", "objective": "Reduce trade deficit; protect domestic manufacturing; retain tariff leverage over China"},
            {"actor": "China / Xi", "objective": "Preserve export-driven growth model; resist structural reforms demanded by the US; maintain rare-earth leverage"},
            {"actor": "US Congress and courts", "objective": "Check executive tariff authority -- the Supreme Court has already overruled some measures"},
        ],
        "regional_linkages": "The same May 2026 Xi-Trump summit that produced the trade truce also correlates with reduced Taiwan Strait military activity, suggesting Beijing and Washington are linking the two files to some degree.",
        "outlook_30_90": "Expect continued incremental tariff moves (like the August 24 overcapacity tariff) ahead of the September summit, used as negotiating leverage rather than a genuine rupture of the truce. A full breakdown of the trade relationship within 90 days looks unlikely given both sides' demonstrated preference for managed competition over full decoupling.",
        "escalation_triggers": [
            "China imposing new rare-earth export restrictions",
            "A further US legal ruling striking down tariff authority, forcing more unpredictable executive responses",
            "The September Xi-Trump summit failing to produce any agreement",
        ],
        "early_warning_indicators": [
            "USTR public comment periods and Federal Register notices on the Board of Trade mechanism",
            "New Section 301 tariff announcements",
            "Chinese rare-earth export licensing data",
        ],
        "second_order_effects": {
            "supply_chains": "Rare earth restrictions directly threaten US defense and tech manufacturing",
            "trade": "Tariff uncertainty continues to complicate corporate supply-chain planning globally, not just bilaterally",
        },
        "confidence_level": "High -- tariff actions are a matter of public record (Federal Register, USTR announcements). The more speculative element is whether the 'truce' framing will hold through September.",
        "strategic_chokepoints": [],
    },

    "russia_ukraine_2026": {
        "name": "Russia-Ukraine War",
        "regions": ["Russia", "Ukraine"],
        "started": "2022-02-24",
        "last_reviewed": "2026-09-03",
        "status": "active",
        "risk_level": "Critical",
        "status_summary": (
            "Now the largest active conventional war in the world, fought "
            "along a roughly 1,000-1,200km front. By mid-2026 the conflict "
            "had shifted from territorial offensives to a war of attrition "
            "defined by drone warfare, energy-infrastructure strikes, and "
            "electronic warfare -- neither side has achieved a decisive "
            "breakthrough."
        ),
        "timeline": [
            {"date": "2022-02-24", "event": "Russia launches full-scale invasion of Ukraine",
             "source": "Wikipedia (Russo-Ukrainian war timeline)", "url": "https://en.wikipedia.org/wiki/Timeline_of_the_Russo-Ukrainian_war_(1_June_2026_%E2%80%93_present)"},
            {"date": "2026-01-04", "event": "Front line stretches ~1,200km; Ukraine's Commander in Chief says drone-warfare 'kill zones' near the line are now up to 20km deep",
             "source": "Al Jazeera", "url": "https://www.aljazeera.com/news/2026/1/4/russia-ukraine-war-list-of-key-events-day-1410"},
            {"date": "2026-06", "event": "Russia suspends civilian shipping through the Don-Azov Shipping Canal and the Kerch Strait; Ukraine gains only ~31 sq mi of territory over the month despite continued fighting",
             "source": "Russia Matters", "url": "https://www.russiamatters.org/news/russia-ukraine-war-report-card/russia-ukraine-war-report-card-july-1-2026"},
            {"date": "2026-06", "event": "Ukrainian drone strikes take roughly 40% of Russia's oil export capacity offline, hitting Novorossiysk, Primorsk, and Ust-Luga; weeks-long power/water outages hit Belgorod",
             "source": "Russia Matters", "url": "https://www.russiamatters.org/news/russia-ukraine-war-report-card/russia-ukraine-war-report-card-july-1-2026"},
            {"date": "2026-08", "event": "Assessed as strategic stalemate: neither side capable of decisive victory; war increasingly defined by drone/electronic-warfare innovation rather than territorial gains",
             "source": "Lviv Herald", "url": "https://www.lvivherald.com/post/ukraine-russia-conflict-front-and-rear-lines-summary-assessment-early-august-2026"},
            {"date": "2026-08-29", "event": "Turkey summons Ukraine's ambassador after two Turkish-operated vessels are struck in the Black Sea; five drones enter Moldova's airspace during a Russian overnight attack",
             "source": "The World Now (live tracker)", "url": "https://www.the-world-now.com/ukraine-war-map"},
            {"date": "2026-09-01", "event": "Sixth consecutive night of intensified Russian strikes on Kyiv, an unprecedented sustained tempo since 2022; at least 12 killed.", "source": "AP, Washington Times"},
            {"date": "2026-09-01", "event": "Russian ballistic missile strike on a Kyiv railway depot kills 7, including 6 railway workers.", "source": "Ukrinform"},
            {"date": "2026-09-01", "event": "Russia now producing an estimated ~3,000 jet-powered (Geran-4-type) drones per month, a significant capability increase.", "source": "Ukrinform"},
            {"date": "2026-09-01", "event": "Ukraine is combat-testing at least four new interceptor systems specifically designed to counter jet-powered drones.", "source": "Ukrinform"},
        ],

        "key_actors": [
            {"actor": "Russia", "objective": "Consolidate territorial gains in Donetsk, Luhansk, Zaporizhzhia, Kherson, and Crimea; degrade Ukraine's war-fighting capacity via energy infrastructure strikes"},
            {"actor": "Ukraine", "objective": "Defend remaining territory; degrade Russia's military-industrial and energy export capacity through long-range strikes rather than pursue large territorial offensives"},
            {"actor": "NATO/Western allies", "objective": "Sustain Ukraine's defense without direct NATO-Russia confrontation; increasingly strained by the parallel airspace-incursion crisis on NATO's own eastern flank"},
            {"actor": "North Korea", "objective": "Supply Russia with artillery (25-40% of Russia's current stock) in exchange for economic and possibly technological benefits"},
        ],
        "regional_linkages": "North Korea's arms supply role directly links this war to the Korea conflict tracked separately. Russia's suspension of Kerch Strait/Don-Azov shipping and repeated Black Sea vessel strikes (including Turkish-flagged ships) tie this conflict to the Turkish Straits chokepoint and Turkey's own security posture. Drone incursions into Baltic NATO airspace during Ukrainian long-range strikes are actively straining the separate Russia-NATO relationship. Russia and Iran are simultaneously under intensifying Western economic pressure and appear to be coordinating/aligning in response -- the Aug 31-Sept 1 Putin-Pezeshkian SCO meeting is the clearest recent signal; see the Iran War dossier for the reverse link.",
        "outlook_30_90": "Given the current stalemate and both sides' declared preference for attrition over decisive offensives, expect continued gradual, small territorial shifts alongside intensified drone/infrastructure strikes on both sides. A drone/counter-drone arms race is now visibly underway -- Russia's ~3,000/month jet-powered drone production against Ukraine's newly fielded interceptor systems -- worth tracking as a distinct dynamic. No credible near-term ceasefire process is currently underway; watch for any renewed diplomatic initiative tied to broader US-Russia dynamics.",
        "escalation_triggers": [
            "A Ukrainian strike killing a large number of Russian civilians, prompting disproportionate retaliation",
            "A Russian strike directly hitting NATO territory or personnel (distinct from the ongoing drone-incursion pattern)",
            "A major battlefield collapse on either side altering the current attritional balance",
            "The shift from episodic strikes to sustained multi-night bombardment campaigns (the 'sixth straight night' Kyiv pattern) becoming the new normal operating tempo rather than a temporary surge",
        ],
        "early_warning_indicators": [
            "DeepState/ISW front-line territorial-change data (currently near-static, watch for acceleration)",
            "Russian oil export capacity offline percentage (currently ~40%)",
            "Frequency and location of drone incursions into NATO Baltic airspace",
        ],
        "second_order_effects": {
            "energy": "~40% of Russia's oil export capacity currently offline from Ukrainian strikes, with global market effects",
            "shipping": "Kerch Strait and Don-Azov Canal shipping suspended; Black Sea vessel strikes (including on Turkish-flagged ships) are raising insurance costs and diplomatic tension with Turkey",
            "migration": "Continued fighting sustains one of the largest refugee/displacement crises in Europe since WWII",
        },
        "confidence_level": "Moderate to high for territorial/front-line data (DeepState OSINT and ISW are widely used, cross-referenced trackers), but attribution of specific incidents (e.g. which side's drones caused a given incursion) is sometimes genuinely disputed, as seen in the Baltic drone cases where Finnish officials suggested Russian jamming may have diverted Ukrainian drones off course. The reported ~1.49 million Russian troop-loss figure circulating in Ukrainian sources is a Ukrainian government claim, not independently verified by a neutral body.",
        "strategic_chokepoints": ["turkish_straits"],
    },

    "myanmar_2026": {
        "name": "Myanmar Civil War",
        "regions": ["Myanmar", "Burma"],
        "started": "2021-02-01",
        "last_reviewed": "2026-08-30",
        "status": "active",
        "risk_level": "High",
        "status_summary": (
            "Now in its sixth year, the world's most fragmented active "
            "conflict (over 1,200 armed groups per ACLED). After a period "
            "of resistance momentum, the junta regained significant "
            "ground through mid-2026, aided by conscription, drone "
            "adoption, and continued Chinese and Russian backing -- "
            "though a full military victory remains distant."
        ),
        "timeline": [
            {"date": "2021-02-01", "event": "Tatmadaw coup ousts the elected NLD government, detains Aung San Suu Kyi",
             "source": "Defcon Level", "url": "https://www.defconlevel.com/myanmar-civil-war"},
            {"date": "2025-03-28", "event": "A 7.7-magnitude earthquake near Mandalay kills 5,000+ and affects 17 million; the junta conducts 550+ attacks in the two months after, while restricting aid access",
             "source": "World on Fire", "url": "https://world-on-fire.com/conflicts/myanmar.html"},
            {"date": "2026-01", "event": "Junta holds tightly controlled elections excluding the opposition",
             "source": "Armed Conflicts Tracker", "url": "https://armedconflicts.org/myanmar-civil-war.html"},
            {"date": "2026-03", "event": "National Unity Government and four major ethnic armed groups (Chin National Front, Kachin Independence Army, Karen National Union, Karenni National Progressive Party) form the Steering Council for the Emergence of a Federal Democratic Union",
             "source": "War on the Rocks", "url": "https://warontherocks.com/misreading-myanmars-war-why-the-juntas-recent-gains-dont-mean-imminent-victory/"},
            {"date": "2026-04", "event": "Coup leader Min Aung Hlaing installed as 'civilian' president; junta recaptures Falam after resistance forces withdraw citing ammunition shortages",
             "source": "Myanmar Civil War Tracker", "url": "https://armedconflicts.org/myanmar-civil-war.html"},
            {"date": "2026-07", "event": "Described as 'crunch time' -- the junta is on a steady roll of countrywide advances, pushing the resistance onto the defensive after years of losses",
             "source": "Asia Times", "url": "https://asiatimes.com/2026/07/crunch-time-looms-over-myanmars-grinding-civil-war/"},
        ],

        "key_actors": [
            {"actor": "Tatmadaw / junta (Min Aung Hlaing)", "objective": "Reassert nationwide control; legitimize military rule through a civilian veneer"},
            {"actor": "National Unity Government + Steering Council alliance", "objective": "Build a unified federal-democratic military strategy across previously fragmented resistance groups"},
            {"actor": "Arakan Army (Rakhine State)", "objective": "De facto proto-state governance with its own significant military capacity, distinct from the wider NUG coalition"},
            {"actor": "China and Russia", "objective": "Back the junta with materiel and diplomatic cover at the UN; China separately pursues its own stability-focused track along the border"},
        ],
        "regional_linkages": "India and Thailand, sharing long borders, pragmatically engage with whichever local authority controls adjacent territory. China and Russia have blocked stronger UN Security Council action, paralleling their posture toward other conflicts they're aligned against Western pressure on.",
        "outlook_30_90": "Given the junta's described 'steady roll' of advances through mid-2026, continued territorial consolidation in central/northern regions looks likely in the near term, but a full military victory remains distant given the resistance's demonstrated resilience and rural guerrilla capacity. Watch whether the Steering Council alliance can translate political unity into a coordinated military response.",
        "escalation_triggers": [
            "A major resistance urban center falling to the junta, replicating the Falam pattern at larger scale",
            "A significant split within the Steering Council alliance",
            "A new natural disaster compounding the existing humanitarian crisis",
        ],
        "early_warning_indicators": [
            "Territorial control percentage estimates (sources currently disagree, ranging from ~21% to ~40% junta control -- watch the trend, not the exact figure)",
            "Ammunition/supply reports from resistance-held towns",
            "China-junta border diplomacy signals",
        ],
        "second_order_effects": {
            "migration": "5.2 million internally/cross-border displaced per UN estimates; continued instability strains Thailand and India border regions",
            "humanitarian": "15,000+ conflict-related deaths in 2025 alone per ACLED; healthcare/education systems have collapsed in contested areas",
        },
        "confidence_level": "Low to moderate on territorial control specifics -- sources reviewed for this entry gave meaningfully different percentages for junta vs. resistance control (from 21% to 40%+), reflecting how genuinely fragmented and hard-to-verify this conflict is. Casualty and displacement figures (ACLED, UN) are more consistently cited across sources.",
        "strategic_chokepoints": [],
    },

    "yemen_redsea_2026": {
        "name": "Yemen Civil War & Red Sea Crisis",
        "regions": ["Yemen"],
        "started": "2014",
        "last_reviewed": "2026-08-30",
        "status": "active",
        "risk_level": "High",
        "status_summary": (
            "Distinct from (but entangled with) the Houthi-Israel strikes "
            "tracked under the Iran War entry: Yemen's OWN internal civil "
            "war -- dormant under a 2022 UN-brokered truce -- reignited in "
            "2026 after a Saudi strike prevented an Iranian delegation "
            "from landing in Sanaa, triggering renewed fighting between "
            "the Houthis and the Saudi-backed government."
        ),
        "timeline": [
            {"date": "2014", "event": "Houthi rebels begin fighting the Saudi-led coalition backing Yemen's internationally recognized government",
             "source": "CFR Global Conflict Tracker", "url": "https://www.cfr.org/global-conflict-tracker/conflict/war-yemen"},
            {"date": "2022", "event": "UN-brokered ceasefire quiets the civil war (though Houthi Red Sea shipping attacks continue separately, tied to Gaza)",
             "source": "CFR Global Conflict Tracker", "url": "https://www.cfr.org/global-conflict-tracker/conflict/war-yemen"},
            {"date": "2026-03-28", "event": "Houthis resume attacks on Israel directly, joining the 2026 Iran war after pausing under the October 2025 Gaza ceasefire",
             "source": "Wikipedia (2026 Houthi strikes on Israel)", "url": "https://en.wikipedia.org/wiki/2026_Houthi_strikes_on_Israel"},
            {"date": "2026-07-13", "event": "A Saudi airstrike on Sanaa airport's runway prevents an Iranian flight carrying a senior Houthi delegation from landing, breaking the 2022 truce",
             "source": "Al Jazeera", "url": "https://www.aljazeera.com/news/2026/8/12/six-killed-in-houthi-attack-on-bab-al-mandeb-ship-yemens-government-says"},
            {"date": "2026-07", "event": "Saudi-led coalition strikes Houthi-controlled Hodeidah and Kamaran; Houthis retaliate against government-held al-Makha (Mocha) and Marib, killing dozens; Houthi strikes on Abha Airport threaten to fully reignite the civil war",
             "source": "CFR Global Conflict Tracker", "url": "https://www.cfr.org/global-conflict-tracker/conflict/war-yemen"},
            {"date": "2026-07", "event": "Saudi Arabia, Turkey, and Pakistan sign a joint defense agreement; two days later, Houthis strike an oil facility in Saudi Arabia",
             "source": "CFR Global Conflict Tracker", "url": "https://www.cfr.org/global-conflict-tracker/conflict/war-yemen"},
            {"date": "2026-08-12", "event": "A Houthi attack on a ship in the Bab el-Mandeb Strait kills at least six",
             "source": "Al Jazeera", "url": "https://www.aljazeera.com/news/2026/8/12/six-killed-in-houthi-attack-on-bab-al-mandeb-ship-yemens-government-says"},
        ],

        "key_actors": [
            {"actor": "Houthis (Ansar Allah)", "objective": "Consolidate control over northern Yemen; maintain Iran alignment; leverage Red Sea shipping disruption as strategic pressure tied to Gaza and the wider Iran war"},
            {"actor": "Yemen's internationally recognized government", "objective": "Survive as the internationally-backed authority; regain lost territory with Saudi coalition support"},
            {"actor": "Saudi Arabia (coalition leader)", "objective": "Prevent a fully Iran-aligned state on its southern border; protect its own territory and oil facilities from Houthi strikes"},
            {"actor": "United States/United Kingdom", "objective": "Protect Red Sea/Bab-el-Mandeb shipping freedom, conducting periodic strikes on Houthi military infrastructure"},
        ],
        "regional_linkages": "Directly entangled with the 2026 Iran war (Houthi strikes on Israel are explicitly part of that conflict) and with the new Saudi-Turkey-Pakistan defense pact -- linking this conflict to Pakistan's own regional posture. Ethiopian migration into Yemen (91% of July 2026 arrivals) ties this conflict to instability in Ethiopia's Amhara, Oromia, and Tigray regions.",
        "outlook_30_90": "Given the truce has now broken down with active strikes on both sides, a return to full-scale civil war looks more likely than a swift re-stabilization. Continued Bab-el-Mandeb shipping attacks are likely regardless of the internal civil war's trajectory, since they're tied to the separate Iran-war dynamic.",
        "escalation_triggers": [
            "A mass-casualty Houthi strike on a major Saudi city (beyond the current pattern of airport/facility strikes)",
            "A direct US/UK ground or naval engagement with Houthi forces beyond airstrikes",
            "Collapse of the newly-formed Saudi-Turkey-Pakistan defense pact's coordination",
        ],
        "early_warning_indicators": [
            "Frequency of Bab-el-Mandeb vessel attacks (currently averaging multiple per month)",
            "Saudi coalition strike patterns on Hodeidah/Kamaran",
            "Ethiopian and Horn of Africa migration flow data into Yemen",
        ],
        "second_order_effects": {
            "shipping": "Bab-el-Mandeb attacks continue to force shipping reroutes around the Cape of Good Hope, raising costs and transit times globally",
            "migration": "Yemen is simultaneously a conflict zone and a destination for Horn of Africa migrants fleeing separate crises",
            "energy": "Saudi oil facility strikes (like the one following the Turkey-Pakistan pact signing) pose a direct threat to Gulf energy infrastructure",
        },
        "confidence_level": "Moderate -- CFR and Al Jazeera consistently corroborate the broad pattern of renewed strikes, but exact casualty figures from individual incidents are typically sourced to only one side (Yemen's government or Houthi media) without independent confirmation.",
        "strategic_chokepoints": ["bab_el_mandeb"],
    },

    "india_pakistan_2025": {
        "name": "India-Pakistan Tensions (Kashmir)",
        "regions": ["India", "Pakistan", "Kashmir", "PoK"],
        "started": "1947",
        "last_reviewed": "2026-08-30",
        "status": "active",
        "risk_level": "High",
        "status_summary": (
            "The two nuclear-armed neighbors fought their worst conflict "
            "in decades in May 2025 after a militant attack on tourists in "
            "Pahalgam. A ceasefire has held since, but relations remain in "
            "a state analysts describe as 'armed coexistence' -- high "
            "alert, minimal diplomacy, narrow margin for error."
        ),
        "timeline": [
            {"date": "2025-04-22", "event": "Militants attack tourists in Pahalgam, Indian-administered Kashmir, killing 26 (mostly Hindu) and 1 Nepalese national; India blames Pakistan, which denies involvement",
             "source": "CSIS", "url": "https://www.csis.org/analysis/what-led-recent-crisis-between-india-and-pakistan"},
            {"date": "2025-04-23", "event": "India suspends the six-decade-old Indus Waters Treaty, which governs shared river usage; Pakistan calls this an existential threat given its dependence on the Indus, Chenab, and Jhelum rivers",
             "source": "Al Jazeera", "url": "https://www.aljazeera.com/news/2026/1/2/handshake-in-dhaka-can-india-and-pakistan-revive-ties-in-2026"},
            {"date": "2025-05-07", "event": "India launches 'Operation Sindoor,' missile strikes on nine sites in Pakistan and Pakistan-administered Kashmir, targeting alleged terrorist infrastructure",
             "source": "CSIS", "url": "https://www.csis.org/analysis/what-led-recent-crisis-between-india-and-pakistan"},
            {"date": "2025-05-10", "event": "Ceasefire agreed after a four-day war that killed 70+ people -- the worst India-Pakistan conflict in decades",
             "source": "Al Jazeera", "url": "https://www.aljazeera.com/news/2026/5/27/india-orders-demolition-drive-along-border-as-pakistan-tensions-simmer"},
            {"date": "2026-01-02", "event": "'Handshake in Dhaka' -- an attempted rapprochement, though the Indus Waters Treaty suspension remains a core sticking point",
             "source": "Al Jazeera", "url": "https://www.aljazeera.com/news/2026/1/2/handshake-in-dhaka-can-india-and-pakistan-revive-ties-in-2026"},
            {"date": "2026-04-29", "event": "J&K Chief Minister Omar Abdullah continues demanding statehood; ties remain 'severely strained'",
             "source": "International Crisis Group", "url": "https://www.crisisgroup.org/asia-pacific/south-asia/india-pakistan-kashmir"},
            {"date": "2026-05-27", "event": "India orders a demolition drive along the border, tightening enforcement against alleged infiltration, narcotics, and smuggling within 15km of the frontier",
             "source": "Al Jazeera", "url": "https://www.aljazeera.com/news/2026/5/27/india-orders-demolition-drive-along-border-as-pakistan-tensions-simmer"},
        ],

        "key_actors": [
            {"actor": "India", "objective": "Deter cross-border militancy via high-intensity response (the 'Operation Sindoor' precedent); retain leverage over shared river resources"},
            {"actor": "Pakistan", "objective": "Restore the Indus Waters Treaty (existential water-security concern); deny backing militant groups while accusing India of supporting separatists"},
            {"actor": "Jammu & Kashmir regional government", "objective": "Secure statehood and greater autonomy, caught between both nations' security postures"},
            {"actor": "Kashmiri militant groups", "objective": "Continue insurgency; exact objectives and state sponsorship remain genuinely disputed between India and Pakistan"},
        ],
        "regional_linkages": "This is a live example of the exact 'coverage gap' risk in isolated conflict tracking -- India and Pakistan are both increasingly engaged in other theaters (India via non-Kashmir security policy, Pakistan via its own border war with Afghanistan and the new Saudi-Turkey-Pakistan defense pact), any of which could shift bandwidth or leverage in this relationship.",
        "outlook_30_90": "Given the 'armed coexistence' framing from Crisis Group analysts, expect continued low-level friction (border security measures, diplomatic sniping) without a return to open conflict in the near term, absent a new large-scale militant attack. The Indus Waters Treaty impasse remains the single most likely genuine crisis trigger given Pakistan's stated existential framing of it.",
        "escalation_triggers": [
            "A new mass-casualty militant attack in Indian-administered Kashmir attributed to Pakistan-based groups",
            "India making the Indus Waters Treaty suspension effectively permanent rather than a pressure tactic",
            "A significant militant escalation timed to Pakistan's other regional commitments (e.g. if its Afghan border conflict draws away security resources)",
        ],
        "early_warning_indicators": [
            "Line of Control (LoC) exchange-of-fire frequency",
            "Indus Waters Treaty diplomatic signals (any resumption talks)",
            "J&K statehood/political developments",
        ],
        "second_order_effects": {
            "water_security": "The Indus Waters Treaty suspension directly threatens Pakistan's agricultural water supply, a genuine existential-level concern per Pakistani officials",
            "trade": "Continued border closures and diplomatic freezes limit any bilateral trade normalization",
        },
        "confidence_level": "Moderate -- casualty figures for the April-May 2025 crisis are relatively consistent across CSIS, CFR, and Al Jazeera, but attribution of the original Pahalgam attack (India blames Pakistan, Pakistan denies) remains genuinely disputed and unresolved.",
        "strategic_chokepoints": [],
    },

    "syria_2026": {
        "name": "Post-Assad Syria Transition",
        "regions": ["Syria"],
        "started": "2024-12-08",
        "last_reviewed": "2026-08-30",
        "status": "active",
        "risk_level": "Medium-High",
        "status_summary": (
            "Since Bashar al-Assad's fall in December 2024, interim "
            "president Ahmed al-Sharaa has pursued a fragile political "
            "transition -- while also directly absorbing spillover damage "
            "from the 2026 Iran war (missile debris from Israeli/Iranian "
            "strikes has hit Syrian territory) and renegotiating Russia's "
            "military basing rights."
        ),
        "timeline": [
            {"date": "2024-12-08", "event": "Ahmed al-Sharaa's forces (Hayat Tahrir al-Sham) topple Bashar al-Assad, ending Syria's 13-year civil war; Assad flees to Russia",
             "source": "Al Jazeera", "url": "https://www.aljazeera.com/news/2026/8/10/they-need-each-other-whats-behind-the-new-syria-russia-accord"},
            {"date": "2025-01", "event": "Al-Sharaa declared Syria's transitional president",
             "source": "House of Commons Library", "url": "https://commonslibrary.parliament.uk/research-briefings/cbp-10430/"},
            {"date": "2025-03-10", "event": "Damascus and the Kurdish-led SDF agree the militia will integrate into government forces by end of 2025 -- implementation later stalls over autonomy demands",
             "source": "UN Security Council Report", "url": "https://www.securitycouncilreport.org/monthly-forecast/2026-02/syria-88.php"},
            {"date": "2026-02-28", "event": "US-Israeli strikes on Iran begin; Israeli and Iranian missile debris subsequently violates Syrian airspace and causes deaths/injuries inside Syrian territory as the interim government tries to stay neutral",
             "source": "UN Security Council Report", "url": "https://www.securitycouncilreport.org/monthly-forecast/2026-04/syria-90.php"},
            {"date": "2026-04-16", "event": "US finalizes withdrawal of its forces from Syria, handing bases over to the interim government",
             "source": "UN Security Council Report", "url": "https://www.securitycouncilreport.org/monthly-forecast/2026-05/syria-91.php"},
            {"date": "2026-05", "event": "Russian oil shipments to Syria jump 75% to ~60,000 barrels/day, using US-sanctioned tankers, as Damascus and Moscow rebuild ties",
             "source": "FDD", "url": "https://www.fdd.org/analysis/2026/05/19/post-assad-syria-is-mending-fences-with-russia/"},
            {"date": "2026-08-10", "event": "Syria and Russia sign a memorandum of understanding on the Hmeimim airbase and Tartus naval base -- Syria takes control of civilian facilities, Russia retains its core military presence",
             "source": "Al Jazeera", "url": "https://www.aljazeera.com/news/2026/8/10/they-need-each-other-whats-behind-the-new-syria-russia-accord"},
        ],

        "key_actors": [
            {"actor": "Interim President Ahmed al-Sharaa / HTS", "objective": "Consolidate a unified Syrian state; balance Western outreach with pragmatic re-engagement with Russia"},
            {"actor": "Kurdish-led Syrian Democratic Forces (SDF)", "objective": "Retain meaningful autonomy in the northeast rather than full integration into a centralized government"},
            {"actor": "Turkish-backed Syrian National Army (SNA)", "objective": "Control northern border areas; prevent Kurdish autonomy, a core Turkish strategic priority"},
            {"actor": "Russia", "objective": "Preserve its Tartus/Hmeimim military presence for Mediterranean and NATO-monitoring capability"},
            {"actor": "Iran", "objective": "Relations remain frozen post-Assad; watching for any opening while Syria maintains studied neutrality in the wider Iran war"},
        ],
        "regional_linkages": "Directly absorbing spillover from the 2026 Iran war (missile debris, mobilized border defenses with Iraq and Lebanon). Russia's renewed Tartus/Hmeimim presence gives it NATO-monitoring capability in the eastern Mediterranean, tying this to the broader Russia-NATO relationship. Turkey's role as a NATO member managing both Syrian refugee return and anti-Kurdish priorities links this to Turkey's own regional posture across multiple tracked conflicts.",
        "outlook_30_90": "Given the interim government's demonstrated ability to stay largely insulated from the Iran war so far, continued gradual state consolidation looks likely, but the unresolved SDF autonomy question remains a persistent flashpoint. Watch whether the new Russia accord provokes any Western or Gulf-state pushback against Damascus.",
        "escalation_triggers": [
            "A major SDF-government or SDF-SNA clash breaking the fragile integration process",
            "A significant escalation of Iran-war spillover striking Syrian civilians directly (rather than debris/mobilization)",
            "ISIL/Da'esh exploiting the security vacuum for a significant resurgence",
        ],
        "early_warning_indicators": [
            "SDF integration negotiation status",
            "Foreign Terrorist Fighter (FTF) integration into Syrian armed forces, a concern China has repeatedly raised at the UN",
            "Frequency of Iran-war-related missile debris incidents over Syrian territory",
        ],
        "second_order_effects": {
            "migration": "~3.5 million Syrian refugees remain in Turkey; their return is a major domestic Turkish political issue tied to this transition's success",
            "humanitarian": "16.5 million Syrians in need projected for 2026, with only 33.5% of the 2025 humanitarian response plan funded",
            "energy": "Russian oil shipments (up 75% in 2026) via sanctioned tankers raise sanctions-enforcement questions for Western governments",
        },
        "confidence_level": "Moderate to high -- UN Security Council Report's monthly forecasts and the House of Commons Library briefing are both institutional, citation-heavy sources; the underlying SDF integration and FTF concerns are consistently corroborated across multiple sources.",
        "strategic_chokepoints": [],
    },

    "russia_nato_2026": {
        "name": "Russia-NATO Tensions",
        "regions": ["Russia", "Europe"],
        "started": "2022-02",
        "last_reviewed": "2026-08-30",
        "status": "active",
        "risk_level": "High",
        "status_summary": (
            "A distinct thread from the Russia-Ukraine war itself: a "
            "sustained pattern of Russian airspace incursions and hybrid "
            "threats against NATO's eastern flank (Poland, Romania, "
            "Estonia, the Baltic states), running in parallel with -- and "
            "sometimes entangled with -- the Ukraine war's own spillover "
            "effects."
        ),
        "timeline": [
            {"date": "2025-09-09", "event": "20+ Russian drones enter Polish airspace overnight; NATO jets down some -- the most serious cross-border incident into NATO territory since the 2022 invasion began",
             "source": "Al Jazeera", "url": "https://www.aljazeera.com/news/2025/9/28/poland-briefly-closes-airspace-as-nato-increases-presence-in-the-baltic-sea"},
            {"date": "2025-09-19", "event": "Three Russian MiG-31 fighter jets violate Estonian airspace for 12 minutes -- Estonia's fourth violation of the year; Estonia requests NATO Article 4 consultations",
             "source": "CBC", "url": "https://www.cbc.ca/lite/story/1.7638294"},
            {"date": "2025-09-28", "event": "Poland briefly closes airspace amid 'unplanned military activity'; NATO upgrades its Baltic Sea mission with an air-defense frigate after drone incursions in Denmark and sightings in Norway",
             "source": "Al Jazeera", "url": "https://www.aljazeera.com/news/2025/9/28/poland-briefly-closes-airspace-as-nato-increases-presence-in-the-baltic-sea"},
            {"date": "2026-03-23", "event": "Ukrainian or suspected-Ukrainian drones begin entering Baltic NATO airspace (Lithuania, then Latvia and Estonia) after crossing from Russia during long-range Ukrainian strikes on Russian oil infrastructure",
             "source": "Wikipedia (2026 Baltic drone incursions)", "url": "https://en.wikipedia.org/wiki/2026_Ukrainian_drone_incursions_into_the_Baltic_states_and_Finland"},
            {"date": "2026-05-19", "event": "A Romanian F-16 under NATO's Baltic Air Policing mission intercepts and destroys a suspected Ukrainian drone over Estonia -- the first such NATO shootdown in this series",
             "source": "Wikipedia (2026 Baltic drone incursions)", "url": "https://en.wikipedia.org/wiki/2026_Ukrainian_drone_incursions_into_the_Baltic_states_and_Finland"},
            {"date": "2026-07-15", "event": "Lithuania's president warns of intelligence indicating Russia is planning a hybrid provocation against Baltic/Polish energy or transport infrastructure",
             "source": "Organization for World Peace", "url": "https://theowp.org/reports/russian-hybrid-attacks-in-the-baltic-region-and-poland-how-to-stop-them/"},
            {"date": "2026-08-12", "event": "NATO meets over renewed Polish and Romanian airspace incursions, concludes Russia bears 'full responsibility,' and discusses new security measures for its frontline borders",
             "source": "Euronews", "url": "https://www.euronews.com/my-europe/2026/08/12/nato-stands-with-poland-and-romania-amid-russian-airspace-violations"},
        ],

        "key_actors": [
            {"actor": "Russia", "objective": "Test NATO's readiness and resolve along its eastern flank; potentially conduct deniable hybrid operations against Baltic/Polish infrastructure"},
            {"actor": "NATO (Poland, Romania, Baltic states)", "objective": "Deter further incursions; maintain alliance cohesion and Article 4/5 credibility without direct escalation to war with Russia"},
            {"actor": "Ukraine", "objective": "Continue long-range strikes on Russian oil infrastructure, an activity whose side-effects (stray/jammed drones) are complicating the separate NATO-Russia dynamic"},
        ],
        "regional_linkages": "Directly entangled with the Russia-Ukraine war -- a meaningful share of the airspace incursions are Ukrainian drones gone astray during strikes on Russia, not solely deliberate Russian provocations, complicating attribution and NATO's response calculus. Also connects to Syria via Russia's Tartus/Hmeimim bases, which explicitly serve a NATO-monitoring function for Moscow.",
        "outlook_30_90": "Given Lithuania's July warning of planned Russian hybrid action, expect continued (and possibly escalating) infrastructure-focused incidents in the Baltic/Poland region over the next 90 days. A direct kinetic NATO-Russia clash remains unlikely in this window, but the margin for miscalculation given the mixed Russian/Ukrainian-origin incursions is genuinely narrow.",
        "escalation_triggers": [
            "A confirmed Russian (not Ukrainian-origin) drone or aircraft causing NATO casualties",
            "A successful Russian hybrid attack on critical Baltic/Polish infrastructure, as Lithuania warned",
            "NATO invoking Article 5 (collective defense) rather than Article 4 (consultation) in response to an incident",
        ],
        "early_warning_indicators": [
            "Frequency of airspace violation incidents by country",
            "NATO Baltic Air Policing intercept/shootdown rates",
            "Public intelligence warnings from Baltic state leaders (a pattern that preceded the July 2026 warning)",
        ],
        "second_order_effects": {
            "cyber": "Hybrid threats extend beyond airspace to suspected cyber and infrastructure sabotage targeting, per NATO's own hybrid-threats framework",
            "trade": "Repeated airspace closures (Poland, others) disrupt regional civil aviation and logistics",
        },
        "confidence_level": "Moderate -- individual airspace-violation incidents are well-documented by NATO member governments, but attribution between deliberate Russian provocation and genuine Ukrainian-drone spillover (acknowledged even by Finnish officials) is sometimes ambiguous, and should not be treated as uniformly deliberate Russian action.",
        "strategic_chokepoints": [],
    },
}


def get_conflict(key: str) -> dict | None:
    return CONFLICTS.get(key)


def get_all_conflicts() -> dict:
    return CONFLICTS