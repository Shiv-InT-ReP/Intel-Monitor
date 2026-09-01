"""
Generates releases.html -- a fourth page alongside dashboard.html, map.html,
and background.html, showing official government/IGO releases (Ministries,
UN, NATO, etc.) matched by region. Matches the existing dark ops-room
visual language for continuity.
"""
import json
from datetime import datetime, timezone
from pathlib import Path

from core.db import get_official_releases

OUTPUT_PATH = Path(__file__).resolve().parent.parent / "releases.html"


def generate_releases_page():
    releases = get_official_releases()
    data_json = json.dumps(releases)
    data_json = data_json.replace("</script", "<\\/script").replace("</SCRIPT", "<\\/SCRIPT")

    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    html = HTML_TEMPLATE.replace("__DATA_JSON__", data_json).replace("__GENERATED__", generated_at)
    OUTPUT_PATH.write_text(html, encoding="utf-8")
    print(f"  [x] Releases page updated: {OUTPUT_PATH} ({len(releases)} release(s))")
    return OUTPUT_PATH


HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Intel Monitor — Official Releases</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500;600&display=swap" rel="stylesheet">
<style>
  :root {
    --bg: #0B1220; --panel: #131B2E; --panel-border: #1F2A44;
    --text: #E4E8F1; --text-muted: #7C89A6; --text-dim: #4C5876;
    --amber: #E8A33D; --amber-dim: rgba(232, 163, 61, 0.15);
  }
  * { box-sizing: border-box; }
  body { margin: 0; background: var(--bg); color: var(--text); font-family: 'IBM Plex Sans', sans-serif; }
  .mono { font-family: 'IBM Plex Mono', monospace; }
  header {
    padding: 24px 32px; border-bottom: 1px solid var(--panel-border);
    display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 16px;
  }
  h1 { font-size: 22px; margin: 0; letter-spacing: 0.02em; }
  h1 span { color: var(--amber); }
  .subtitle { color: var(--text-muted); font-size: 13px; margin: 6px 0 0; max-width: 560px; }
  .nav-links a {
    display: inline-block; margin-left: 8px; color: var(--amber); text-decoration: none;
    border: 1px solid var(--panel-border); padding: 6px 12px; border-radius: 4px;
    font-size: 11px; font-family: 'IBM Plex Mono', monospace;
  }
  main { max-width: 800px; margin: 0 auto; padding: 32px; }
  .controls { margin-bottom: 20px; }
  .controls select {
    background: var(--panel); border: 1px solid var(--panel-border); color: var(--text);
    font-family: 'IBM Plex Sans', sans-serif; font-size: 12px; padding: 6px 10px; border-radius: 4px;
  }
  .release-item {
    background: var(--panel); border: 1px solid var(--panel-border); border-radius: 6px;
    padding: 16px 20px; margin-bottom: 10px;
  }
  .release-item a { color: var(--text); font-size: 14px; text-decoration: none; }
  .release-item a:hover { color: var(--amber); }
  .release-meta {
    font-family: 'IBM Plex Mono', monospace; font-size: 10px; color: var(--text-dim);
    margin-top: 6px; text-transform: uppercase; letter-spacing: 0.03em;
  }
  .video-summary {
    margin-top: 10px; padding: 10px 12px; background: rgba(232,163,61,0.06);
    border-left: 2px solid var(--amber); border-radius: 0 4px 4px 0;
    font-size: 13px; color: var(--text-muted); line-height: 1.6;
  }
  .summary-label {
    font-family: 'IBM Plex Mono', monospace; font-size: 9px; color: var(--amber);
    letter-spacing: 0.05em; margin-right: 6px;
  }
  .empty-state { color: var(--text-dim); font-size: 13px; padding: 40px; text-align: center; }
  footer { text-align: center; padding: 24px; color: var(--text-dim); font-size: 11px; font-family: 'IBM Plex Mono', monospace; }
</style>
</head>
<body>

<header>
  <div>
    <h1>OFFICIAL <span>RELEASES</span></h1>
    <p class="subtitle">Press releases and statements from ministries, the UN, NATO, and other government/IGO sources, filtered to your tracked regions.</p>
    <p class="mono" style="font-size:10px;color:var(--text-dim);margin:6px 0 0;">GENERATED __GENERATED__</p>
  </div>
  <div class="nav-links">
    <a href="dashboard.html">LIST VIEW</a>
    <a href="map.html">MAP VIEW</a>
    <a href="background.html">CONFLICT BACKGROUND</a>
  </div>
</header>

<main>
  <div class="controls">
    <select id="sourceFilter">
      <option value="all">All sources</option>
    </select>
  </div>
  <div id="releaseList"></div>
</main>

<footer>Intel Monitor — Official Releases</footer>

<script>
  const RELEASES = __DATA_JSON__;
  const state = { source: 'all' };

  function timeAgo(iso) {
    if (!iso) return '';
    const diffMs = Date.now() - new Date(iso).getTime();
    const days = Math.floor(diffMs / (1000 * 60 * 60 * 24));
    if (days < 1) return 'today';
    if (days === 1) return '1 day ago';
    return days + ' days ago';
  }

  function escapeHtml(str) {
    const div = document.createElement('div');
    div.textContent = str || '';
    return div.innerHTML;
  }

  function populateSourceFilter() {
    const sources = [...new Set(RELEASES.map(r => r.source.replace('rss:', '')))].sort();
    const sel = document.getElementById('sourceFilter');
    sources.forEach(s => {
      const opt = document.createElement('option');
      opt.value = s;
      opt.textContent = s;
      sel.appendChild(opt);
    });
  }

  function render() {
    let items = RELEASES;
    if (state.source !== 'all') {
      items = items.filter(r => r.source.replace('rss:', '') === state.source);
    }

    const container = document.getElementById('releaseList');
    if (items.length === 0) {
      container.innerHTML = '<div class="empty-state">No official releases matched yet for your tracked regions. This updates automatically as your pipeline runs.</div>';
      return;
    }

    container.innerHTML = items.map(r => {
      const summaryHtml = r.video_summary
        ? `<div class="video-summary"><span class="summary-label">AI SUMMARY</span> ${escapeHtml(r.video_summary)}</div>`
        : '';
      return `
      <div class="release-item">
        <a href="${r.url}" target="_blank" rel="noopener">${escapeHtml(r.title)}</a>
        <div class="release-meta">${escapeHtml(r.source.replace('rss:', ''))} · ${escapeHtml(r.region || 'Unspecified')} · ${timeAgo(r.first_seen_at)}</div>
        ${summaryHtml}
      </div>
    `;
    }).join('');
  }

  document.getElementById('sourceFilter').addEventListener('change', e => {
    state.source = e.target.value;
    render();
  });

  populateSourceFilter();
  render();
</script>

</body>
</html>
"""
