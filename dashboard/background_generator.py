"""
Generates background.html -- a third page alongside dashboard.html and
map.html, showing manually-curated conflict timelines. Matches the
existing dark ops-room visual language for continuity across the app.

Each conflict card also shows a "Recent Related Activity" section, pulled
LIVE from the pipeline's matched items (region-matched to that conflict).
This is deliberately separate from the curated timeline above it -- the
timeline is manually researched and reviewed, editorial judgment about
what belongs in a conflict's permanent history; the activity feed is raw,
unfiltered, automatically updated every run, and makes no claim about
significance. Never auto-promoted into the timeline itself.
"""
import json
from datetime import datetime, timezone
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from data.conflict_backgrounds import get_all_conflicts
from data.supply_chain_nodes import get_nodes_for_conflict, get_unlinked_nodes
from core.db import get_dashboard_data

OUTPUT_PATH = Path(__file__).resolve().parent.parent / "background.html"
RECENT_ACTIVITY_LIMIT = 6


def _get_recent_activity(conflict: dict, all_items: list[dict]) -> list[dict]:
    """Items whose region matches this conflict's tracked regions, newest first."""
    regions_lower = {r.lower() for r in conflict.get("regions", [])}
    matches = [item for item in all_items if (item.get("region") or "").lower() in regions_lower]
    matches.sort(key=lambda i: i.get("first_seen_at") or "", reverse=True)
    return matches[:RECENT_ACTIVITY_LIMIT]


def generate_background_page():
    conflicts = get_all_conflicts()
    all_items = get_dashboard_data()

    conflicts_with_activity = []
    for conflict_key, conflict in conflicts.items():
        conflict = dict(conflict)  # don't mutate the source data
        conflict["recent_activity"] = _get_recent_activity(conflict, all_items)
        # Supply chain nodes linked to this specific conflict -- rendered as
        # clickable stat-callouts within the card, superseding the old plain
        # second_order_effects.supply_chains string (still present in the
        # data for now, but excluded from rendering -- see the JS below).
        conflict["supply_chain_nodes"] = get_nodes_for_conflict(conflict_key)
        conflicts_with_activity.append(conflict)

    data_json = json.dumps(conflicts_with_activity)
    data_json = data_json.replace("</script", "<\\/script").replace("</SCRIPT", "<\\/SCRIPT")

    # Nodes that don't map onto any single tracked conflict (e.g. DRC cobalt,
    # Indonesia nickel, India pharma) -- rendered in their own standalone
    # section rather than forced into an unrelated dossier.
    unlinked_json = json.dumps(get_unlinked_nodes())
    unlinked_json = unlinked_json.replace("</script", "<\\/script").replace("</SCRIPT", "<\\/SCRIPT")

    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    html = HTML_TEMPLATE.replace("__DATA_JSON__", data_json)
    html = html.replace("__UNLINKED_SUPPLY_CHAINS_JSON__", unlinked_json)
    html = html.replace("__GENERATED__", generated_at)
    OUTPUT_PATH.write_text(html, encoding="utf-8")
    print(f"  [x] Background page updated: {OUTPUT_PATH} ({len(conflicts)} conflict(s))")
    return OUTPUT_PATH


HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Intel Monitor — Conflict Background</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500;600&display=swap" rel="stylesheet">
<style>
  :root {
    --bg: #0B1220;
    --panel: #131B2E;
    --panel-border: #1F2A44;
    --text: #E4E8F1;
    --text-muted: #7C89A6;
    --text-dim: #4C5876;
    --amber: #E8A33D;
    --amber-dim: rgba(232, 163, 61, 0.15);
    --red: #E83D5D;
  }
  * { box-sizing: border-box; }
  body {
    margin: 0;
    background: var(--bg);
    color: var(--text);
    font-family: 'IBM Plex Sans', sans-serif;
  }
  .mono { font-family: 'IBM Plex Mono', monospace; }

  header {
    padding: 24px 32px;
    border-bottom: 1px solid var(--panel-border);
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    flex-wrap: wrap;
    gap: 16px;
  }
  h1 { font-size: 22px; margin: 0; letter-spacing: 0.02em; }
  h1 span { color: var(--amber); }
  .subtitle { color: var(--text-muted); font-size: 13px; margin: 6px 0 0; max-width: 560px; }
  .nav-links a {
    display: inline-block;
    margin-left: 8px;
    color: var(--amber);
    text-decoration: none;
    border: 1px solid var(--panel-border);
    padding: 6px 12px;
    border-radius: 4px;
    font-size: 11px;
    font-family: 'IBM Plex Mono', monospace;
  }

  main { max-width: 900px; margin: 0 auto; padding: 32px; }

  .conflict-card {
    background: var(--panel);
    border: 1px solid var(--panel-border);
    border-radius: 6px;
    padding: 28px;
    margin-bottom: 32px;
  }
  .conflict-title-row { display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 12px; }
  .conflict-name { font-size: 20px; font-weight: 600; margin: 0; }
  .status-badge {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 10px;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    padding: 4px 10px;
    border-radius: 3px;
    background: var(--amber-dim);
    color: var(--amber);
    white-space: nowrap;
  }
  .badge-row { display: flex; gap: 8px; flex-wrap: wrap; margin-top: 8px; }
  .risk-badge {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 10px;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    padding: 4px 10px;
    border-radius: 3px;
    white-space: nowrap;
    border: 1px solid transparent;
  }
  .risk-low { color: #4FD16B; background: rgba(79,209,107,0.12); }
  .risk-medium { color: var(--amber); background: var(--amber-dim); }
  .risk-medium-high { color: #E8863D; background: rgba(232,134,61,0.14); }
  .risk-high { color: #E8863D; background: rgba(232,134,61,0.14); }
  .risk-critical { color: var(--red); background: rgba(232,61,93,0.15); border-color: rgba(232,61,93,0.4); }
  .chokepoint-tag {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 10px;
    padding: 4px 10px;
    border-radius: 3px;
    background: rgba(91,141,239,0.12);
    color: #5B8DEF;
    white-space: nowrap;
  }
  .conflict-meta { font-family: 'IBM Plex Mono', monospace; font-size: 11px; color: var(--text-dim); margin-top: 6px; }
  .status-summary { color: var(--text-muted); font-size: 14px; line-height: 1.6; margin: 16px 0 24px; padding: 14px 16px; background: rgba(232,163,61,0.06); border-left: 2px solid var(--amber); border-radius: 0 4px 4px 0; }

  /* Timeline -- the signature element. Order genuinely carries information
     here (this is a real chronological sequence, not decorative numbering),
     so a vertical rail with dated nodes is the honest structural choice. */
  .timeline { position: relative; padding-left: 28px; }
  .timeline::before {
    content: ''; position: absolute; left: 6px; top: 6px; bottom: 6px;
    width: 2px; background: var(--panel-border);
  }
  .timeline-event { position: relative; padding-bottom: 22px; }
  .timeline-event:last-child { padding-bottom: 0; }
  .timeline-event::before {
    content: ''; position: absolute; left: -28px; top: 4px;
    width: 10px; height: 10px; border-radius: 50%;
    background: var(--bg); border: 2px solid var(--amber);
  }
  .timeline-date { font-family: 'IBM Plex Mono', monospace; font-size: 11px; color: var(--amber); }
  .timeline-desc { font-size: 14px; color: var(--text); line-height: 1.55; margin: 4px 0 6px; }
  .timeline-source { font-size: 11px; }
  .timeline-source a { color: var(--text-muted); text-decoration: none; border-bottom: 1px dotted var(--text-dim); }
  .timeline-source a:hover { color: var(--amber); }

  .extra-facts { margin-top: 20px; padding-top: 16px; border-top: 1px solid var(--panel-border); font-size: 12px; color: var(--text-muted); line-height: 1.6; }
  .extra-facts strong { color: var(--text); }

  .analysis-section { margin-top: 24px; padding-top: 20px; border-top: 1px solid var(--panel-border); }
  .analysis-heading {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 11px;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    color: var(--amber);
    margin-bottom: 12px;
  }
  .actor-row { display: flex; gap: 10px; padding: 8px 0; border-bottom: 1px solid rgba(31,42,68,0.5); font-size: 13px; }
  .actor-row:last-child { border-bottom: none; }
  .actor-name { color: var(--text); font-weight: 600; min-width: 180px; flex-shrink: 0; }
  .actor-objective { color: var(--text-muted); }
  .analysis-text { font-size: 13px; color: var(--text-muted); line-height: 1.6; }
  .outlook-box { padding: 14px 16px; background: rgba(91,141,239,0.06); border-left: 2px solid #5B8DEF; border-radius: 0 4px 4px 0; font-size: 13px; color: var(--text-muted); line-height: 1.6; }
  .watch-list { list-style: none; padding: 0; margin: 8px 0 0; }
  .watch-list li { font-size: 13px; color: var(--text-muted); padding: 5px 0 5px 18px; position: relative; line-height: 1.5; }
  .watch-list li::before { content: '▸'; position: absolute; left: 0; color: var(--amber); }
  .second-order-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 12px; margin-top: 8px; }
  .second-order-item { font-size: 12px; }
  .second-order-label { font-family: 'IBM Plex Mono', monospace; font-size: 9px; text-transform: uppercase; letter-spacing: 0.05em; color: var(--text-dim); margin-bottom: 3px; }
  .second-order-value { color: var(--text-muted); line-height: 1.5; }
  .confidence-note { font-size: 11px; color: var(--text-dim); font-style: italic; margin-top: 10px; }

  .activity-section { margin-top: 20px; padding-top: 16px; border-top: 1px solid var(--panel-border); }
  .activity-label {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 10px;
    letter-spacing: 0.05em;
    color: var(--text-dim);
    display: flex;
    align-items: center;
    gap: 6px;
    margin-bottom: 10px;
  }
  .live-dot {
    width: 6px; height: 6px; border-radius: 50%;
    background: #4FD16B;
    box-shadow: 0 0 6px #4FD16B;
    animation: pulse-dot 2s infinite;
  }
  @keyframes pulse-dot { 0%, 100% { opacity: 1; } 50% { opacity: 0.3; } }
  .activity-item { padding: 8px 0; border-bottom: 1px solid rgba(31,42,68,0.5); }
  .activity-item:last-child { border-bottom: none; }
  .activity-item a { color: var(--text); font-size: 13px; text-decoration: none; }
  .activity-item a:hover { color: var(--amber); }
  .activity-meta { font-family: 'IBM Plex Mono', monospace; font-size: 10px; color: var(--text-dim); margin-top: 2px; text-transform: uppercase; }

  footer { text-align: center; padding: 24px; color: var(--text-dim); font-size: 11px; font-family: 'IBM Plex Mono', monospace; }

  /* ---- Supply chain stat-callouts + click-through modal ---- */
  .supply-chain-section { margin-top: 18px; }
  .supply-chain-callout {
    display: block; width: 100%; text-align: left; cursor: pointer;
    background: var(--amber-dim); border: 1px solid var(--panel-border);
    border-left: 3px solid var(--amber); border-radius: 4px;
    padding: 10px 14px; margin-bottom: 8px;
    font-family: inherit; color: inherit;
  }
  .supply-chain-callout:hover { border-left-color: var(--text); background: rgba(232,163,61,0.22); }
  .supply-chain-stat { font-weight: 700; color: var(--amber); font-size: 13px; }
  .supply-chain-detail { color: var(--text-muted); font-size: 12px; margin-top: 3px; line-height: 1.5; }
  .supply-chain-standalone-card {
    background: var(--panel); border: 1px solid var(--panel-border); border-radius: 6px;
    padding: 16px 20px; margin-bottom: 16px;
  }
  .supply-chain-standalone-card h3 { margin: 0 0 10px; font-size: 15px; color: var(--text); }

  .sc-modal-overlay {
    display: none; position: fixed; inset: 0; background: rgba(6,9,16,0.82);
    z-index: 2000; align-items: center; justify-content: center; padding: 24px;
  }
  .sc-modal-overlay.open { display: flex; }
  .sc-modal {
    background: var(--panel); border: 1px solid var(--panel-border); border-radius: 8px;
    max-width: 760px; width: 100%; max-height: 88vh; overflow-y: auto;
  }
  .sc-modal-header {
    display: flex; justify-content: space-between; align-items: flex-start;
    padding: 18px 22px; border-bottom: 1px solid var(--panel-border);
  }
  .sc-modal-header h2 { margin: 0; font-size: 17px; color: var(--text); }
  .sc-modal-close { background: none; border: none; color: var(--text-dim); font-size: 20px; cursor: pointer; padding: 0 4px; }
  .sc-modal-close:hover { color: var(--text); }
  .sc-modal-map { height: 260px; width: 100%; }
  .sc-modal-body { padding: 18px 22px; }
  .sc-chain-legend { display: flex; gap: 14px; flex-wrap: wrap; font-size: 11px; color: var(--text-dim); margin-bottom: 14px; font-family: 'IBM Plex Mono', monospace; text-transform: uppercase; }
  .sc-chain-legend span { display: inline-flex; align-items: center; gap: 5px; }
  .sc-chain-dot { width: 8px; height: 8px; border-radius: 50%; display: inline-block; }
  .sc-modal-field { margin-bottom: 14px; }
  .sc-modal-field-label { font-family: 'IBM Plex Mono', monospace; font-size: 10px; text-transform: uppercase; letter-spacing: 0.05em; color: var(--text-dim); margin-bottom: 4px; }
  .sc-modal-field-value { color: var(--text-muted); font-size: 13px; line-height: 1.6; }
  .sc-modal-sources { font-size: 11px; color: var(--text-dim); margin-top: 16px; padding-top: 12px; border-top: 1px solid var(--panel-border); }
</style>
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.css" />
<script src="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.js"></script>
</head>
<body>

<header>
  <div>
    <h1>CONFLICT <span>BACKGROUND</span></h1>
    <p class="subtitle">Manually-researched timelines for persistent conflicts your dashboard tracks -- context for wars that outlast any single day's headlines.</p>
    <p class="mono" style="font-size:10px;color:var(--text-dim);margin:6px 0 0;">GENERATED __GENERATED__ · Curated, not auto-scraped -- reviewed by hand</p>
  </div>
  <div class="nav-links">
    <a href="dashboard.html">LIST VIEW</a>
    <a href="map.html">MAP VIEW</a>
    <a href="releases.html">OFFICIAL RELEASES</a>
  </div>
</header>

<main id="conflicts"></main>

<section class="supply-chain-section" style="max-width:900px;margin:0 auto;padding:0 24px;">
  <h2 style="font-size:16px;color:var(--text);border-bottom:1px solid var(--panel-border);padding-bottom:10px;">
    OTHER SUPPLY CHAIN DEPENDENCIES
  </h2>
  <p class="subtitle" style="margin-bottom:16px;">Critical dependencies that don't map onto a single tracked conflict above -- civilian and dual-use chokepoints worth monitoring on their own.</p>
  <div id="otherSupplyChains"></div>
</section>

<div class="sc-modal-overlay" id="scModalOverlay" onclick="if(event.target===this) closeSupplyChainModal()">
  <div class="sc-modal">
    <div class="sc-modal-header">
      <div>
        <h2 id="scModalTitle"></h2>
        <div class="conflict-meta" id="scModalReviewed" style="margin-top:6px;"></div>
      </div>
      <button class="sc-modal-close" onclick="closeSupplyChainModal()">&times;</button>
    </div>
    <div id="scModalMap" class="sc-modal-map"></div>
    <div class="sc-modal-body">
      <div class="sc-chain-legend" id="scModalLegend"></div>
      <div class="sc-modal-field">
        <div class="sc-modal-field-label">Why It Matters</div>
        <div class="sc-modal-field-value" id="scModalWhyMatters"></div>
      </div>
      <div class="sc-modal-field">
        <div class="sc-modal-field-label">Alternative Suppliers</div>
        <div class="sc-modal-field-value" id="scModalAlternatives"></div>
      </div>
      <div class="sc-modal-field">
        <div class="sc-modal-field-label">Current Status</div>
        <div class="sc-modal-field-value" id="scModalStatus"></div>
      </div>
      <div class="sc-modal-sources" id="scModalSources"></div>
    </div>
  </div>
</div>

<footer>Intel Monitor — Conflict Background</footer>

<script>
  const CONFLICTS = __DATA_JSON__;
  const UNLINKED_SUPPLY_CHAINS = __UNLINKED_SUPPLY_CHAINS_JSON__;

  // Global lookup so the modal can find any linked node by ID regardless of
  // which conflict card it was clicked from.
  const SUPPLY_CHAIN_NODE_LOOKUP = {};
  CONFLICTS.forEach(c => (c.supply_chain_nodes || []).forEach(n => { SUPPLY_CHAIN_NODE_LOOKUP[n.node_id] = n; }));
  // The 3 unlinked nodes also get the full clickable map treatment -- they
  // already carry real multi-location chain_nodes data (e.g. DRC -> China ->
  // Global markets), so there's no reason to withhold the interactive view
  // just because they don't tie to one specific tracked conflict.
  UNLINKED_SUPPLY_CHAINS.forEach(n => { SUPPLY_CHAIN_NODE_LOOKUP[n.node_id] = n; });

  const ROLE_COLORS = {
    'Mining': '#E8703D', 'Mining/Processing': '#E8703D', 'Production': '#E8703D',
    'Production/Source': '#E8703D', 'Historic Production': '#7C89A6',
    'Processing': '#E8A33D', 'Manufacturing': '#E8A33D', 'Component Manufacturing': '#E8A33D',
    'Formulation/Manufacturing': '#E8A33D', 'Design Tools Origin': '#E8A33D',
    'Consumer': '#3D7FE8', 'Destination': '#3D7FE8', 'Restricted Destination': '#3D7FE8',
  };
  function roleColor(role) { return ROLE_COLORS[role] || '#7C89A6'; }

  let scLeafletMap = null;

  function openSupplyChainModal(nodeId) {
    const node = SUPPLY_CHAIN_NODE_LOOKUP[nodeId];
    if (!node) return;

    document.getElementById('scModalTitle').textContent = node.name;

    // Same 14-day staleness pattern already used for conflict dossiers --
    // this data is manually researched/reviewed, not auto-updated, so it's
    // worth flagging when it's due for a refresh.
    const reviewedEl = document.getElementById('scModalReviewed');
    if (node.last_reviewed) {
      const reviewedDate = new Date(node.last_reviewed);
      const daysSince = Math.floor((Date.now() - reviewedDate.getTime()) / (1000 * 60 * 60 * 24));
      const isStale = daysSince > 14;
      reviewedEl.style.color = isStale ? 'var(--red)' : '';
      reviewedEl.textContent = `LAST REVIEWED ${node.last_reviewed} (${daysSince}d ago)`
        + (isStale ? ' — consider refreshing given new developments' : '');
    } else {
      reviewedEl.textContent = '';
    }
    document.getElementById('scModalWhyMatters').textContent = node.why_it_matters || '';
    document.getElementById('scModalAlternatives').textContent = node.alternative_suppliers || '';
    document.getElementById('scModalStatus').textContent = node.current_status || '';
    document.getElementById('scModalSources').textContent = (node.sources || []).length
      ? 'Sources: ' + node.sources.join(' · ') : '';

    const legend = (node.chain_nodes || []).map(cn =>
      `<span><span class="sc-chain-dot" style="background:${roleColor(cn.role)}"></span>${cn.role}</span>`
    );
    // de-duplicate legend entries with the same role
    const seenRoles = new Set();
    document.getElementById('scModalLegend').innerHTML = legend.filter(entry => {
      const role = entry.match(/>([^<]+)<\/span>$/)[1];
      if (seenRoles.has(role)) return false;
      seenRoles.add(role);
      return true;
    }).join('');

    document.getElementById('scModalOverlay').classList.add('open');

    // Leaflet needs the container visible before init, and a fresh map
    // instance each open -- simplest reliable approach for a modal that
    // shows different data every time it opens.
    setTimeout(() => {
      if (scLeafletMap) { scLeafletMap.remove(); scLeafletMap = null; }
      const mapDiv = document.getElementById('scModalMap');
      scLeafletMap = L.map(mapDiv, { zoomControl: true, attributionControl: false });
      L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Base/MapServer/tile/{z}/{y}/{x}', {
        maxZoom: 8
      }).addTo(scLeafletMap);

      const points = [];
      (node.chain_nodes || []).forEach(cn => {
        const color = roleColor(cn.role);
        L.circleMarker([cn.lat, cn.lon], {
          radius: 8, color: color, fillColor: color, fillOpacity: 0.85, weight: 2
        }).addTo(scLeafletMap).bindTooltip(`${cn.name} (${cn.role})`, { permanent: false });
        points.push([cn.lat, cn.lon]);
      });
      if (points.length > 1) {
        L.polyline(points, { color: '#7C89A6', weight: 1.5, dashArray: '4,5', opacity: 0.6 }).addTo(scLeafletMap);
      }
      if (points.length > 0) {
        scLeafletMap.fitBounds(points, { padding: [30, 30], maxZoom: 5 });
      }
    }, 50);
  }

  function closeSupplyChainModal() {
    document.getElementById('scModalOverlay').classList.remove('open');
  }

  function renderOtherSupplyChains() {
    const container = document.getElementById('otherSupplyChains');
    container.innerHTML = UNLINKED_SUPPLY_CHAINS.map(node => `
      <div class="supply-chain-standalone-card">
        <h3>${node.name}</h3>
        ${(node.stat_callouts || []).map(sc => `
          <button class="supply-chain-callout" onclick="openSupplyChainModal('${node.node_id}')">
            <div class="supply-chain-stat">${sc.stat}</div>
            <div class="supply-chain-detail">${sc.detail}</div>
          </button>
        `).join('')}
      </div>
    `).join('');
  }

  function renderConflicts() {
    const container = document.getElementById('conflicts');
    if (CONFLICTS.length === 0) {
      container.innerHTML = '<p class="mono" style="color:var(--text-dim);">No conflict backgrounds recorded yet.</p>';
      return;
    }

    container.innerHTML = CONFLICTS.map(c => {
      const timelineHtml = c.timeline.map(ev => `
        <div class="timeline-event">
          <div class="timeline-date">${ev.date}</div>
          <div class="timeline-desc">${ev.event}</div>
          <div class="timeline-source">Source: <a href="${ev.url}" target="_blank" rel="noopener">${ev.source}</a></div>
        </div>
      `).join('');

      let extras = '';
      if (c.un_figures) extras += `<div><strong>UN figures:</strong> ${c.un_figures}</div>`;
      if (c.casualties) extras += `<div style="margin-top:8px;"><strong>Casualties:</strong> ${c.casualties}</div>`;
      if (c.chokepoint_impact) extras += `<div style="margin-top:8px;"><strong>Chokepoint impact:</strong> ${c.chokepoint_impact}</div>`;
      if (c.gaza_status) extras += `<div style="margin-top:8px;"><strong>Gaza ceasefire status:</strong> ${c.gaza_status}</div>`;
      if (c.pattern_note) extras += `<div style="margin-top:8px;"><strong>Cross-conflict pattern:</strong> ${c.pattern_note}</div>`;
      if (c.cross_conflict_note) extras += `<div style="margin-top:8px;"><strong>Cross-conflict link:</strong> ${c.cross_conflict_note}</div>`;
      const extrasHtml = extras ? `<div class="extra-facts">${extras}</div>` : '';

      const activity = c.recent_activity || [];
      const activityHtml = activity.length > 0
        ? `
          <div class="activity-section">
            <div class="activity-label">
              <span class="live-dot"></span> RECENT RELATED ACTIVITY (live, auto-updated)
            </div>
            ${activity.map(item => `
              <div class="activity-item">
                <a href="${item.url}" target="_blank" rel="noopener">${item.title}</a>
                <div class="activity-meta">${item.source.replace('rss:', '').replace('telegram:', '')} · ${item.severity_tier}</div>
              </div>
            `).join('')}
          </div>
        `
        : '';

      // Risk badge: normalize "Medium-High" etc. into a CSS class
      const riskClass = 'risk-' + (c.risk_level || 'medium').toLowerCase().replace(/[^a-z]+/g, '-').replace(/^-|-$/g, '');

      const chokepointsHtml = (c.strategic_chokepoints && c.strategic_chokepoints.length > 0)
        ? c.strategic_chokepoints.map(key => `<span class="chokepoint-tag">⚓ ${key.replace(/_/g, ' ')}</span>`).join('')
        : '';

      const actorsHtml = (c.key_actors && c.key_actors.length > 0)
        ? `
          <div class="analysis-section">
            <div class="analysis-heading">Key Actors &amp; Objectives — Who Wants What</div>
            ${c.key_actors.map(a => `
              <div class="actor-row">
                <div class="actor-name">${a.actor}</div>
                <div class="actor-objective">${a.objective}</div>
              </div>
            `).join('')}
          </div>
        `
        : '';

      let whyMatters = '';
      if (c.regional_linkages) whyMatters += `<div class="analysis-text"><strong style="color:var(--text);">Regional linkages:</strong> ${c.regional_linkages}</div>`;
      if (c.second_order_effects) {
        // "supply_chains" is deliberately excluded here -- it's superseded
        // by the richer, clickable stat-callout rendering below, which
        // pulls from supply_chain_nodes.py instead of this plain string.
        const items = Object.entries(c.second_order_effects)
          .filter(([k]) => k !== 'supply_chains')
          .map(([k, v]) => `
          <div class="second-order-item">
            <div class="second-order-label">${k.replace(/_/g, ' ')}</div>
            <div class="second-order-value">${v}</div>
          </div>
        `).join('');
        whyMatters += `<div class="second-order-grid">${items}</div>`;
      }
      const whyMattersHtml = whyMatters
        ? `<div class="analysis-section"><div class="analysis-heading">Why It Matters — Second-Order Effects</div>${whyMatters}</div>`
        : '';

      const supplyChainHtml = (c.supply_chain_nodes && c.supply_chain_nodes.length > 0)
        ? `<div class="analysis-section"><div class="analysis-heading">Supply Chain Dependencies</div>
            ${c.supply_chain_nodes.map(node => `
              ${node.stat_callouts.map(sc => `
                <button class="supply-chain-callout" onclick="openSupplyChainModal('${node.node_id}')">
                  <div class="supply-chain-stat">${sc.stat}</div>
                  <div class="supply-chain-detail">${sc.detail}</div>
                </button>
              `).join('')}
            `).join('')}
          </div>`
        : '';

      const outlookHtml = c.outlook_30_90
        ? `
          <div class="analysis-section">
            <div class="analysis-heading">What Happens Next — 30/90-Day Outlook</div>
            <div class="outlook-box">${c.outlook_30_90}</div>
          </div>
        `
        : '';

      let watchHtml = '';
      if (c.escalation_triggers && c.escalation_triggers.length > 0) {
        watchHtml += `<div style="font-size:12px;color:var(--text-dim);margin-top:10px;text-transform:uppercase;letter-spacing:0.04em;">Escalation triggers</div>
          <ul class="watch-list">${c.escalation_triggers.map(t => `<li>${t}</li>`).join('')}</ul>`;
      }
      if (c.early_warning_indicators && c.early_warning_indicators.length > 0) {
        watchHtml += `<div style="font-size:12px;color:var(--text-dim);margin-top:10px;text-transform:uppercase;letter-spacing:0.04em;">Early-warning indicators to monitor</div>
          <ul class="watch-list">${c.early_warning_indicators.map(t => `<li>${t}</li>`).join('')}</ul>`;
      }
      const watchSectionHtml = watchHtml
        ? `<div class="analysis-section"><div class="analysis-heading">What To Watch</div>${watchHtml}</div>`
        : '';

      const confidenceHtml = c.confidence_level
        ? `<div class="confidence-note">Confidence assessment: ${c.confidence_level}</div>`
        : '';

      // Staleness check: the ANALYSIS (outlook, risk, triggers) is manually
      // researched, not auto-scraped -- this makes clear exactly how fresh
      // it is, rather than silently presenting old judgment as current.
      let reviewedHtml = '';
      if (c.last_reviewed) {
        const reviewedDate = new Date(c.last_reviewed);
        const daysSince = Math.floor((Date.now() - reviewedDate.getTime()) / (1000 * 60 * 60 * 24));
        const isStale = daysSince > 14;
        reviewedHtml = `<div class="conflict-meta" style="${isStale ? 'color:var(--red);' : ''}">
          ANALYSIS LAST REVIEWED ${c.last_reviewed} (${daysSince}d ago)${isStale ? ' — consider refreshing given new developments' : ''}
        </div>`;
      }

      return `
        <div class="conflict-card">
          <div class="conflict-title-row">
            <h2 class="conflict-name">${c.name}</h2>
            <span class="status-badge">${c.status}</span>
          </div>
          <div class="conflict-meta">STARTED ${c.started} · REGIONS: ${c.regions.join(', ')}</div>
          ${reviewedHtml}
          <div class="badge-row">
            <span class="risk-badge ${riskClass}">RISK: ${c.risk_level || 'Unrated'}</span>
            ${chokepointsHtml}
          </div>
          <div class="status-summary">${c.status_summary}</div>
          <div class="analysis-heading" style="margin-top:4px;">What Happened</div>
          <div class="timeline">${timelineHtml}</div>
          ${extrasHtml}
          ${actorsHtml}
          ${whyMattersHtml}
          ${supplyChainHtml}
          ${outlookHtml}
          ${watchSectionHtml}
          ${confidenceHtml}
          ${activityHtml}
        </div>
      `;
    }).join('');
  }

  renderConflicts();
  renderOtherSupplyChains();
</script>

</body>
</html>
"""
