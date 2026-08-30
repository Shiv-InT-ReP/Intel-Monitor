"""
Generates a self-contained HTML dashboard from the SQLite dedup store.
No server needed -- data is embedded directly in the HTML file, so it
just opens in any browser like a regular file.

Regenerated on every main.py run, so it always reflects everything the
pipeline has ever matched, not just the latest digest.
"""
import json
from pathlib import Path

from core.db import get_dashboard_data
from core.source_reliability import get_ownership_tag

DASHBOARD_PATH = Path(__file__).resolve().parent.parent / "dashboard.html"

HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Intel Monitor — Situation Board</title>
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
    --teal: #4FD1C5;
    --teal-dim: rgba(79, 209, 197, 0.15);
  }

  * { box-sizing: border-box; }

  body {
    margin: 0;
    background: var(--bg);
    color: var(--text);
    font-family: 'IBM Plex Sans', sans-serif;
    -webkit-font-smoothing: antialiased;
  }

  .mono { font-family: 'IBM Plex Mono', monospace; }

  header {
    position: relative;
    padding: 28px 32px 22px;
    border-bottom: 1px solid var(--panel-border);
    overflow: hidden;
  }

  header::after {
    content: "";
    position: absolute;
    bottom: 0;
    left: -100%;
    width: 100%;
    height: 2px;
    background: linear-gradient(90deg, transparent, var(--amber), transparent);
    animation: sweep 5s linear infinite;
  }

  @media (prefers-reduced-motion: reduce) {
    header::after { animation: none; opacity: 0.4; left: 0; }
  }

  @keyframes sweep {
    0% { left: -100%; }
    100% { left: 100%; }
  }

  .header-row {
    display: flex;
    justify-content: space-between;
    align-items: baseline;
    flex-wrap: wrap;
    gap: 12px;
  }

  h1 {
    margin: 0;
    font-size: 22px;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
  }

  h1 span { color: var(--amber); }

  .subtitle {
    margin: 4px 0 0;
    color: var(--text-muted);
    font-size: 13px;
    letter-spacing: 0.04em;
  }

  .generated {
    color: var(--text-dim);
    font-size: 12px;
    display: flex;
    align-items: center;
    gap: 8px;
  }

  .dot {
    width: 7px;
    height: 7px;
    border-radius: 50%;
    background: var(--amber);
    animation: pulse 2s ease-in-out infinite;
  }

  @media (prefers-reduced-motion: reduce) {
    .dot { animation: none; }
  }

  @keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.35; }
  }

  .stats {
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: 1px;
    background: var(--panel-border);
    border-bottom: 1px solid var(--panel-border);
  }

  .stat {
    background: var(--panel);
    padding: 18px 24px;
  }

  .stat-value {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 28px;
    font-weight: 600;
    color: var(--text);
  }

  .stat-label {
    font-size: 11px;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: var(--text-muted);
    margin-top: 4px;
  }

  .stat.amber .stat-value { color: var(--amber); }
  .stat.teal .stat-value { color: var(--teal); }

  .controls {
    display: flex;
    gap: 12px;
    padding: 20px 32px;
    flex-wrap: wrap;
    align-items: center;
    border-bottom: 1px solid var(--panel-border);
  }

  .search-wrap {
    flex: 1;
    min-width: 220px;
    display: flex;
    align-items: center;
    background: var(--panel);
    border: 1px solid var(--panel-border);
    border-radius: 4px;
    padding: 0 12px;
  }

  .search-wrap span {
    color: var(--amber);
    font-family: 'IBM Plex Mono', monospace;
    margin-right: 8px;
  }

  .search-wrap input {
    flex: 1;
    background: none;
    border: none;
    outline: none;
    color: var(--text);
    font-family: 'IBM Plex Mono', monospace;
    font-size: 13px;
    padding: 10px 0;
  }

  .search-wrap input::placeholder { color: var(--text-dim); }

  .segmented {
    display: flex;
    background: var(--panel);
    border: 1px solid var(--panel-border);
    border-radius: 4px;
    overflow: hidden;
  }

  .segmented button {
    background: none;
    border: none;
    color: var(--text-muted);
    font-family: 'IBM Plex Sans', sans-serif;
    font-size: 12px;
    font-weight: 500;
    letter-spacing: 0.03em;
    padding: 10px 16px;
    cursor: pointer;
    border-right: 1px solid var(--panel-border);
    transition: background 0.15s, color 0.15s;
  }

  .segmented button:last-child { border-right: none; }
  .segmented button:hover { color: var(--text); }
  .segmented button.active { background: var(--amber-dim); color: var(--amber); }

  select {
    background: var(--panel);
    border: 1px solid var(--panel-border);
    color: var(--text);
    font-family: 'IBM Plex Sans', sans-serif;
    font-size: 12px;
    padding: 10px 12px;
    border-radius: 4px;
    outline: none;
    cursor: pointer;
  }

  main { padding: 8px 32px 48px; }

  .item {
    display: flex;
    gap: 16px;
    padding: 16px 4px;
    border-bottom: 1px solid var(--panel-border);
  }

  .item-bar {
    width: 3px;
    border-radius: 2px;
    flex-shrink: 0;
    background: var(--amber);
  }

  .item.travel .item-bar { background: var(--teal); }

  .item-body { flex: 1; min-width: 0; }

  .item-title {
    color: var(--text);
    text-decoration: none;
    font-size: 15px;
    font-weight: 500;
    line-height: 1.4;
  }

  .item-title:hover { color: var(--amber); }
  .item.travel .item-title:hover { color: var(--teal); }

  .item-meta {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-top: 8px;
    flex-wrap: wrap;
  }

  .source-pill {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 11px;
    color: var(--text-muted);
    background: var(--panel);
    border: 1px solid var(--panel-border);
    padding: 3px 8px;
    border-radius: 3px;
  }

  .ownership-tag {
    font-size: 9px;
    font-weight: 600;
    letter-spacing: 0.03em;
    padding: 2px 6px;
    border-radius: 3px;
    text-transform: uppercase;
    cursor: help;
  }
  .ownership-tag.state-funded { color: #E8A33D; background: rgba(232, 163, 61, 0.15); }
  .ownership-tag.state-linked { color: #E8A33D; background: rgba(232, 163, 61, 0.15); }
  .ownership-tag.state-propaganda { color: #E83D5D; background: rgba(232, 61, 93, 0.2); }

  .age-badge {
    font-size: 9px;
    font-weight: 600;
    letter-spacing: 0.03em;
    padding: 2px 7px;
    border-radius: 3px;
    text-transform: uppercase;
    cursor: help;
    border: 1px solid transparent;
  }
  .age-badge.age-recent { color: var(--text-dim); background: rgba(76, 88, 118, 0.15); }
  .age-badge.age-months { color: var(--amber); background: var(--amber-dim); }
  .age-badge.age-years {
    color: #C9A876;
    background: rgba(201, 168, 118, 0.12);
    border-color: rgba(201, 168, 118, 0.35);
    font-style: italic;
  }

  .kw-tag {
    font-size: 11px;
    color: var(--amber);
    background: var(--amber-dim);
    padding: 3px 8px;
    border-radius: 3px;
  }

  .sev-badge, .conf-badge {
    font-size: 10px;
    font-weight: 600;
    letter-spacing: 0.03em;
    text-transform: uppercase;
    padding: 3px 7px;
    border-radius: 3px;
  }
  .sev-badge::before { content: "SEV \00b7 "; opacity: 0.65; font-weight: 500; }
  .conf-badge::before { content: "VERIFY \00b7 "; opacity: 0.65; font-weight: 500; }

  .sev-badge.low { color: #5B8DEF; background: rgba(91, 141, 239, 0.15); }
  .sev-badge.moderate { color: var(--amber); background: var(--amber-dim); }
  .sev-badge.high { color: #E8703D; background: rgba(232, 112, 61, 0.15); }
  .sev-badge.critical { color: #E83D5D; background: rgba(232, 61, 93, 0.15); }

  .conf-badge.corroborated { color: #4FD16B; background: rgba(79, 209, 107, 0.15); }
  .conf-badge.single-source { color: var(--amber); background: var(--amber-dim); }
  .conf-badge.unverified { color: var(--text-dim); background: rgba(76, 88, 118, 0.15); }

  .corroboration-links {
    margin-top: 6px;
    font-size: 11px;
    color: var(--text-muted);
  }
  .corroboration-links a {
    color: #4FD16B;
    text-decoration: none;
    margin-right: 10px;
  }
  .corroboration-links a:hover { text-decoration: underline; }

  .item.travel .kw-tag { color: var(--teal); background: var(--teal-dim); }

  .item-time {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 11px;
    color: var(--text-dim);
    margin-left: auto;
    white-space: nowrap;
  }

  .empty {
    text-align: center;
    padding: 80px 20px;
    color: var(--text-muted);
  }

  .empty-title { font-size: 15px; color: var(--text); margin-bottom: 6px; }

  footer {
    padding: 20px 32px;
    color: var(--text-dim);
    font-size: 11px;
    border-top: 1px solid var(--panel-border);
  }

  @media (max-width: 640px) {
    .stats { grid-template-columns: repeat(2, 1fr); }
    header, .controls, main, footer { padding-left: 16px; padding-right: 16px; }
  }
</style>
</head>
<body>

<header>
  <div class="header-row">
    <div>
      <h1>INTEL <span>MONITOR</span></h1>
      <p class="subtitle">Situation Board — matched items, all sources</p>
    </div>
    <div class="generated">
      <a href="map.html" class="mono" style="color:var(--amber); text-decoration:none; border:1px solid var(--panel-border); padding:6px 12px; border-radius:4px; margin-right:12px;">MAP VIEW →</a>
      <a href="background.html" class="mono" style="color:var(--amber); text-decoration:none; border:1px solid var(--panel-border); padding:6px 12px; border-radius:4px; margin-right:12px;">CONFLICT BACKGROUND →</a>
      <span class="dot"></span>
      <span class="mono" id="generatedAt"></span>
    </div>
  </div>
</header>

<div class="stats">
  <div class="stat">
    <div class="stat-value" id="statTotal">0</div>
    <div class="stat-label">Total Signals</div>
  </div>
  <div class="stat amber">
    <div class="stat-value" id="statGeo">0</div>
    <div class="stat-label">Geopolitical</div>
  </div>
  <div class="stat teal">
    <div class="stat-value" id="statTravel">0</div>
    <div class="stat-label">Travel Advisories</div>
  </div>
  <div class="stat" style="color: #4C5876;">
    <div class="stat-value" id="statUnverified" style="color: #4C5876;">0</div>
    <div class="stat-label">Unverified</div>
  </div>
  <div class="stat">
    <div class="stat-value" id="stat24h">0</div>
    <div class="stat-label">Last 24 Hours</div>
  </div>
</div>

<div class="controls">
  <div class="search-wrap">
    <span>&gt;</span>
    <input type="text" id="searchInput" placeholder="search title, source, keyword...">
  </div>
  <div class="segmented" id="categoryFilter">
    <button data-cat="all" class="active">All</button>
    <button data-cat="geopolitical">Geopolitical</button>
    <button data-cat="travel">Travel</button>
  </div>
  <div class="segmented" id="confidenceFilter">
    <button data-conf="all" class="active">All verification</button>
    <button data-conf="corroborated">Corroborated</button>
    <button data-conf="single-source">Single-source</button>
    <button data-conf="unverified">Unverified</button>
  </div>
  <select id="timeFilter" title="Filtered by each article's own published date, not when Intel Monitor captured it">
    <option value="30" selected>Published: last 30 days</option>
    <option value="90">Published: last 90 days</option>
    <option value="all">All time</option>
  </select>
  <select id="tagFilter">
    <option value="all" selected>All types</option>
    <option value="security">Security Threats</option>
    <option value="protest">Protests &amp; Unrest</option>
    <option value="disaster">Natural Calamities</option>
    <option value="sloc">Sea Lines of Communication</option>
    <option value="iran_war">Iran War &amp; Gulf Region Alerts</option>
    <option value="russia_ukraine_war">Russia-Ukraine War Alerts</option>
    <option value="defence">Defence Alerts</option>
  </select>
  <select id="sourceFilter">
    <option value="all">All sources</option>
  </select>
</div>

<main id="itemList"></main>

<footer>
  Generated locally by Intel Monitor. Data never leaves this machine — this file reads only the embedded snapshot below.
</footer>

<script>
  const DATA = __DATA_JSON__;

  const state = { search: "", category: "all", source: "all", confidence: "all", days: 30, tag: "all" };

  function timeAgo(iso) {
    if (!iso) return "";
    const then = new Date(iso);
    const diffMs = Date.now() - then.getTime();
    const mins = Math.floor(diffMs / 60000);
    if (mins < 60) return mins + "m ago";
    const hrs = Math.floor(mins / 60);
    if (hrs < 24) return hrs + "h ago";
    const days = Math.floor(hrs / 24);
    return days + "d ago";
  }

  // Prefer the article's own TRUE published date over first_seen_at (when
  // Intel Monitor happened to capture it) -- this is what makes the
  // 30/90-day filters mean "news from the last N days" rather than "things
  // captured in the last N days of running." Falls back to first_seen_at
  // when published_at is missing or unparseable.
  function trueDate(item) {
    if (item.published_at) {
      const d = new Date(item.published_at);
      if (!isNaN(d.getTime())) return d;
    }
    return item.first_seen_at ? new Date(item.first_seen_at) : null;
  }

  // Age badge: makes long-running conflicts visible as historical context,
  // not just noise -- a story that's been active for years (Russia-Ukraine,
  // Pakistan-Afghanistan) deserves a different visual treatment than
  // something that just happened, so you can tell "background context" from
  // "breaking now" at a glance.
  function ageBadge(item) {
    const d = trueDate(item);
    if (!d) return '';
    const ageDays = (Date.now() - d.getTime()) / (1000 * 60 * 60 * 24);

    if (ageDays < 7) return '';  // recent items don't need an age callout
    let label, cls;
    if (ageDays < 30) {
      label = Math.floor(ageDays) + 'd old'; cls = 'age-recent';
    } else if (ageDays < 365) {
      label = Math.floor(ageDays / 30) + 'mo old'; cls = 'age-months';
    } else {
      const years = (ageDays / 365).toFixed(1);
      label = years + 'yr old'; cls = 'age-years';
    }
    return '<span class="age-badge ' + cls + '" title="Published ' + d.toISOString().slice(0, 10) + '">' + label + '</span>';
  }

  function escapeHtml(str) {
    const div = document.createElement("div");
    div.textContent = str || "";
    return div.innerHTML;
  }

  function populateSources() {
    const sources = [...new Set(DATA.map(d => d.source))].sort();
    const sel = document.getElementById("sourceFilter");
    sources.forEach(s => {
      const opt = document.createElement("option");
      opt.value = s;
      opt.textContent = s;
      sel.appendChild(opt);
    });
  }

  function updateStats(filtered) {
    document.getElementById("statTotal").textContent = DATA.length;
    document.getElementById("statGeo").textContent = DATA.filter(d => d.category === "geopolitical").length;
    document.getElementById("statTravel").textContent = DATA.filter(d => d.category === "travel").length;
    document.getElementById("statUnverified").textContent = DATA.filter(d => (d.confidence_tier || "unverified") === "unverified").length;
    const cutoff = Date.now() - 24 * 60 * 60 * 1000;
    document.getElementById("stat24h").textContent = DATA.filter(d => new Date(d.first_seen_at).getTime() > cutoff).length;
  }

  function render() {
    let items = DATA;

    if (state.days !== "all") {
      const cutoffTime = Date.now() - (state.days * 24 * 60 * 60 * 1000);
      items = items.filter(d => {
        const dt = trueDate(d);
        return dt && dt.getTime() > cutoffTime;
      });
    }
    if (state.tag !== "all") {
      items = items.filter(d => (d.event_tags || []).includes(state.tag));
    }
    if (state.category !== "all") {
      items = items.filter(d => d.category === state.category);
    }
    if (state.confidence !== "all") {
      items = items.filter(d => (d.confidence_tier || "unverified") === state.confidence);
    }
    if (state.source !== "all") {
      items = items.filter(d => d.source === state.source);
    }
    if (state.search.trim()) {
      const q = state.search.toLowerCase();
      items = items.filter(d =>
        (d.title || "").toLowerCase().includes(q) ||
        (d.source || "").toLowerCase().includes(q) ||
        (d.matched_keywords || "").toLowerCase().includes(q)
      );
    }

    const list = document.getElementById("itemList");

    if (items.length === 0) {
      list.innerHTML = '<div class="empty"><div class="empty-title">No signals match this filter</div>Try a broader search or a different category.</div>';
      return;
    }

    list.innerHTML = items.map(d => {
      const kws = (d.matched_keywords || "").split(",").filter(Boolean).slice(0, 4);
      const kwHtml = kws.map(k => '<span class="kw-tag">' + escapeHtml(k.trim()) + '</span>').join("");

      const sevTier = d.severity_tier || "low";
      const sevHtml = '<span class="sev-badge ' + sevTier + '">' + escapeHtml(sevTier) + '</span>';

      const confTier = d.confidence_tier || "unverified";
      const confHtml = '<span class="conf-badge ' + confTier + '">' + escapeHtml(confTier) + '</span>';

      const ownership = d.ownership_tag;
      const ownershipHtml = ownership
        ? '<span class="ownership-tag ' + ownership.tag.toLowerCase().replace(/ /g, '-') + '" title="' + escapeHtml(ownership.note) + '">' + escapeHtml(ownership.tag) + '</span>'
        : '';

      const ageHtml = ageBadge(d);

      const links = d.confidence_links || [];
      const linksHtml = links.length > 0
        ? '<div class="corroboration-links">Confirmed by: ' +
          links.map(l => '<a href="' + escapeHtml(l.url) + '" target="_blank" rel="noopener">' + escapeHtml(l.source.replace('rss:', '')) + '</a>').join('') +
          '</div>'
        : '';

      return `
        <div class="item ${d.category === 'travel' ? 'travel' : ''}">
          <div class="item-bar"></div>
          <div class="item-body">
            <a class="item-title" href="${escapeHtml(d.url)}" target="_blank" rel="noopener">${escapeHtml(d.title)}</a>
            <div class="item-meta">
              <span class="source-pill">${escapeHtml(d.source)}</span>
              ${ownershipHtml}
              ${sevHtml}
              ${confHtml}
              ${kwHtml}
              ${ageHtml}
              <span class="item-time mono">${timeAgo(d.first_seen_at)}</span>
            </div>
            ${linksHtml}
          </div>
        </div>
      `;
    }).join("");
  }

  document.getElementById("searchInput").addEventListener("input", e => {
    state.search = e.target.value;
    render();
  });

  document.getElementById("categoryFilter").addEventListener("click", e => {
    if (e.target.tagName !== "BUTTON") return;
    document.querySelectorAll("#categoryFilter button").forEach(b => b.classList.remove("active"));
    e.target.classList.add("active");
    state.category = e.target.dataset.cat;
    render();
  });

  document.getElementById("confidenceFilter").addEventListener("click", e => {
    if (e.target.tagName !== "BUTTON") return;
    document.querySelectorAll("#confidenceFilter button").forEach(b => b.classList.remove("active"));
    e.target.classList.add("active");
    state.confidence = e.target.dataset.conf;
    render();
  });

  document.getElementById("timeFilter").addEventListener("change", e => {
    state.days = e.target.value === "all" ? "all" : parseInt(e.target.value);
    render();
  });

  document.getElementById("tagFilter").addEventListener("change", e => {
    state.tag = e.target.value;
    render();
  });

  document.getElementById("sourceFilter").addEventListener("change", e => {
    state.source = e.target.value;
    render();
  });

  document.getElementById("generatedAt").textContent = "GENERATED " + new Date("__GENERATED_ISO__").toISOString().replace("T", " ").slice(0, 16) + " UTC";

  populateSources();
  updateStats();
  render();
</script>

</body>
</html>
"""


def generate_dashboard():
    items = get_dashboard_data()
    for item in items:
        item["ownership_tag"] = get_ownership_tag(item.get("source", ""))
    data_json = json.dumps(items)
    # Guard against any matched item's title containing a literal "</script"
    # (e.g. quoting HTML/code in a headline) which would otherwise prematurely
    # close the script tag and break the entire page's JavaScript.
    data_json = data_json.replace("</script", "<\\/script").replace("</SCRIPT", "<\\/SCRIPT")

    from datetime import datetime, timezone
    generated_iso = datetime.now(timezone.utc).isoformat()

    html = HTML_TEMPLATE.replace("__DATA_JSON__", data_json).replace("__GENERATED_ISO__", generated_iso)
    DASHBOARD_PATH.write_text(html, encoding="utf-8")
    print(f"  [x] Dashboard updated: {DASHBOARD_PATH} ({len(items)} items)")
    return DASHBOARD_PATH
