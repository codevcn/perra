<!DOCTYPE html>
<html lang="en" data-color-mode="light">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{{ username }} — Perra OSINT Report</title>
  <script>
    (function () {
      var saved = null;
      try { saved = localStorage.getItem('perra-ads-theme'); } catch (e) {}
      var prefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
      var mode = (saved === 'dark' || saved === 'light') ? saved : (prefersDark ? 'dark' : 'light');
      document.documentElement.setAttribute('data-color-mode', mode);
    })();
  </script>
  <style>
    /* Atlassian Design System (ADS) Tokens — Light & Dark */
    :root,
    html[data-color-mode="light"] {
      --ds-surface: #FFFFFF;
      --ds-surface-raised: #FFFFFF;
      --ds-surface-sunken: #F7F8F9;
      --ds-surface-hovered: #F1F2F4;
      --ds-surface-pressed: #DCDFE4;
      --ds-surface-overlay: #FFFFFF;
      --ds-text: #172B4D;
      --ds-text-subtle: #44546F;
      --ds-text-subtlest: #626F86;
      --ds-text-inverse: #FFFFFF;
      --ds-link: #0C66E4;
      --ds-link-pressed: #0055CC;
      --ds-border: rgba(9, 30, 66, 0.14);
      --ds-border-bold: #758195;
      --ds-border-focused: #388BFF;
      --ds-border-input: #8590A2;
      --ds-background-input: #FFFFFF;
      --ds-background-neutral: rgba(9, 30, 66, 0.06);
      --ds-background-neutral-hovered: rgba(9, 30, 66, 0.12);
      --ds-background-brand-bold: #0C66E4;
      --ds-background-brand-bold-hovered: #0055CC;
      --ds-background-brand-subtlest: #E9F2FF;
      --ds-text-brand: #0C66E4;
      --ds-background-success: #DFFCF0;
      --ds-text-success: #216E4E;
      --ds-border-success: #4BCE97;
      --ds-background-warning: #FFF7D6;
      --ds-text-warning: #7F5F01;
      --ds-border-warning: #F5CD47;
      --ds-background-danger: #FFECEB;
      --ds-text-danger: #AE2E24;
      --ds-border-danger: #F87168;
      --ds-background-discovery: #F3F0FF;
      --ds-text-discovery: #5E4DB2;
      --ds-background-information: #E9F2FF;
      --ds-text-information: #0055CC;
      --ds-shadow-raised: 0 1px 1px rgba(9, 30, 66, 0.25), 0 0 1px rgba(9, 30, 66, 0.31);
      --ds-shadow-overlay: 0 8px 12px rgba(9, 30, 66, 0.15), 0 0 1px rgba(9, 30, 66, 0.31);
      --ds-dot-fill: #0F172A;
      --ds-dot-accent: #0EA5E9;
    }

    html[data-color-mode="dark"] {
      --ds-surface: #1D2125;
      --ds-surface-raised: #22272B;
      --ds-surface-sunken: #161A1D;
      --ds-surface-hovered: #282E33;
      --ds-surface-pressed: #2C333A;
      --ds-surface-overlay: #282E33;
      --ds-text: #B6C2CF;
      --ds-text-subtle: #9FADBC;
      --ds-text-subtlest: #8C9BAB;
      --ds-text-inverse: #1D2125;
      --ds-link: #579DFF;
      --ds-link-pressed: #85B8FF;
      --ds-border: rgba(166, 197, 226, 0.16);
      --ds-border-bold: #738496;
      --ds-border-focused: #85B8FF;
      --ds-border-input: #738496;
      --ds-background-input: #22272B;
      --ds-background-neutral: rgba(161, 189, 217, 0.08);
      --ds-background-neutral-hovered: rgba(161, 189, 217, 0.16);
      --ds-background-brand-bold: #579DFF;
      --ds-background-brand-bold-hovered: #85B8FF;
      --ds-background-brand-subtlest: #1C2B41;
      --ds-text-brand: #579DFF;
      --ds-background-success: #1C3329;
      --ds-text-success: #7EE2B8;
      --ds-border-success: #22A06B;
      --ds-background-warning: #332E1B;
      --ds-text-warning: #F5CD47;
      --ds-border-warning: #B38600;
      --ds-background-danger: #42221F;
      --ds-text-danger: #FD9891;
      --ds-border-danger: #E2483D;
      --ds-background-discovery: #2B273F;
      --ds-text-discovery: #B8ACF6;
      --ds-background-information: #1C2B41;
      --ds-text-information: #85B8FF;
      --ds-shadow-raised: 0 1px 1px rgba(3, 4, 4, 0.5), 0 0 1px rgba(188, 214, 240, 0.12);
      --ds-shadow-overlay: 0 8px 16px rgba(3, 4, 4, 0.6), 0 0 1px rgba(188, 214, 240, 0.16);
      --ds-dot-fill: #E2E8F0;
      --ds-dot-accent: #38BDF8;
    }

    *, *::before, *::after { box-sizing: border-box; }

    html {
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Roboto", "Oxygen", "Ubuntu", "Fira Sans", "Droid Sans", "Helvetica Neue", sans-serif;
      font-size: 14px;
      line-height: 1.4286;
      color: var(--ds-text);
      background-color: var(--ds-surface-sunken);
      -webkit-font-smoothing: antialiased;
    }

    body {
      margin: 0;
      padding: 0 0 84px;
      background-color: var(--ds-surface-sunken);
      color: var(--ds-text);
    }

    a {
      color: var(--ds-link);
      text-decoration: none;
    }
    a:hover {
      text-decoration: underline;
      color: var(--ds-link-pressed);
    }

    code, .mono {
      font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
      font-size: 12px;
    }

    .text-muted { color: var(--ds-text-subtlest); }
    .hidden { display: none !important; }

    /* Top Navigation Bar (ADS AtlassianNavigation style) */
    .ads-topbar {
      position: sticky;
      top: 0;
      z-index: 90;
      background: var(--ds-surface);
      border-bottom: 1px solid var(--ds-border);
      padding: 12px 24px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 16px;
      flex-wrap: wrap;
    }

    .ads-brand {
      display: flex;
      align-items: center;
      gap: 12px;
      min-width: 0;
    }

    .ads-logo {
      width: 32px;
      height: 32px;
      flex-shrink: 0;
    }

    .ads-title-group {
      display: flex;
      flex-direction: column;
      min-width: 0;
    }

    .ads-page-title {
      margin: 0;
      font-size: 16px;
      font-weight: 600;
      line-height: 1.25;
      color: var(--ds-text);
      display: flex;
      align-items: center;
      gap: 8px;
      flex-wrap: wrap;
    }

    .ads-subtitle {
      font-size: 12px;
      color: var(--ds-text-subtlest);
      margin-top: 2px;
    }

    .ads-topbar-actions {
      display: flex;
      align-items: center;
      gap: 8px;
      flex-wrap: wrap;
    }

    /* ADS Buttons */
    .ads-btn {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 6px;
      height: 32px;
      padding: 0 12px;
      border-radius: 3px;
      border: 1px solid var(--ds-border);
      background: var(--ds-background-neutral);
      color: var(--ds-text);
      font-family: inherit;
      font-size: 13px;
      font-weight: 500;
      cursor: pointer;
      transition: background-color 0.12s ease, border-color 0.12s ease;
    }
    .ads-btn:hover {
      background: var(--ds-background-neutral-hovered);
    }
    .ads-btn:focus-visible,
    .ads-input:focus-visible,
    .ads-select:focus-visible {
      outline: 2px solid var(--ds-border-focused);
      outline-offset: 2px;
    }
    .ads-btn-primary {
      background: var(--ds-background-brand-bold);
      border-color: transparent;
      color: var(--ds-text-inverse);
    }
    .ads-btn-primary:hover {
      background: var(--ds-background-brand-bold-hovered);
    }
    .ads-btn.is-active {
      background: var(--ds-background-brand-subtlest);
      color: var(--ds-text-brand);
      border-color: var(--ds-border-focused);
    }

    /* Container */
    .ads-container {
      max-width: 1280px;
      margin: 0 auto;
      padding: 20px 24px;
    }

    /* ADS Lozenges */
    .ads-lozenge {
      display: inline-flex;
      align-items: center;
      gap: 4px;
      padding: 2px 6px;
      border-radius: 3px;
      font-size: 11px;
      font-weight: 700;
      line-height: 16px;
      letter-spacing: 0.02em;
      text-transform: uppercase;
      white-space: nowrap;
    }
    .ads-lozenge-success { background: var(--ds-background-success); color: var(--ds-text-success); }
    .ads-lozenge-warning { background: var(--ds-background-warning); color: var(--ds-text-warning); }
    .ads-lozenge-danger  { background: var(--ds-background-danger);  color: var(--ds-text-danger); }
    .ads-lozenge-discovery { background: var(--ds-background-discovery); color: var(--ds-text-discovery); }
    .ads-lozenge-info    { background: var(--ds-background-information); color: var(--ds-text-information); }
    .ads-lozenge-neutral { background: var(--ds-background-neutral); color: var(--ds-text-subtle); }

    /* KPI Summary Grid */
    .ads-kpi-grid {
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 12px;
      margin-bottom: 16px;
    }
    @media (max-width: 960px) { .ads-kpi-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); } }
    @media (max-width: 520px) { .ads-kpi-grid { grid-template-columns: 1fr; } }

    .ads-kpi-card {
      background: var(--ds-surface-raised);
      border-radius: 8px;
      padding: 14px 16px;
      box-shadow: var(--ds-shadow-raised);
      border: 1px solid var(--ds-border);
      display: flex;
      flex-direction: column;
      gap: 4px;
    }
    .ads-kpi-label {
      font-size: 11px;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.04em;
      color: var(--ds-text-subtlest);
    }
    .ads-kpi-value {
      font-size: 24px;
      font-weight: 600;
      line-height: 1.2;
      color: var(--ds-text);
    }
    .ads-kpi-hint {
      font-size: 12px;
      color: var(--ds-text-subtle);
    }

    /* ADS SectionMessage Callout */
    .ads-banner {
      border-radius: 3px;
      padding: 12px 16px;
      margin-bottom: 16px;
      display: flex;
      align-items: flex-start;
      gap: 12px;
      font-size: 13px;
      border-left: 3px solid transparent;
    }
    .ads-banner-warning {
      background: var(--ds-background-warning);
      color: var(--ds-text);
      border-left-color: var(--ds-border-warning);
    }
    .ads-banner-info {
      background: var(--ds-background-information);
      color: var(--ds-text);
      border-left-color: var(--ds-link);
    }
    .ads-banner strong { font-weight: 600; }

    /* Main Workspace Grid: Sidebar Dossier + Results */
    .ads-workspace {
      display: grid;
      grid-template-columns: 300px minmax(0, 1fr);
      gap: 16px;
      align-items: start;
    }
    @media (max-width: 980px) { .ads-workspace { grid-template-columns: 1fr; } }

    .ads-panel {
      background: var(--ds-surface-raised);
      border-radius: 8px;
      border: 1px solid var(--ds-border);
      box-shadow: var(--ds-shadow-raised);
      padding: 16px;
      margin-bottom: 16px;
    }
    .ads-panel-title {
      margin: 0 0 12px;
      font-size: 14px;
      font-weight: 600;
      color: var(--ds-text);
      display: flex;
      align-items: center;
      justify-content: space-between;
    }

    .ads-meta-list {
      display: flex;
      flex-direction: column;
      gap: 10px;
      font-size: 13px;
    }
    .ads-meta-row {
      display: flex;
      flex-direction: column;
      gap: 2px;
      padding-bottom: 8px;
      border-bottom: 1px solid var(--ds-border);
    }
    .ads-meta-row:last-child { border-bottom: none; padding-bottom: 0; }
    .ads-meta-key {
      font-size: 11px;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.03em;
      color: var(--ds-text-subtlest);
    }
    .ads-meta-val {
      color: var(--ds-text);
      word-break: break-word;
    }

    .ads-tag-btn {
      display: inline-flex;
      align-items: center;
      gap: 4px;
      padding: 2px 8px;
      border-radius: 3px;
      border: 1px solid var(--ds-border);
      background: var(--ds-background-neutral);
      color: var(--ds-text-subtle);
      font-size: 12px;
      cursor: pointer;
      margin: 2px 4px 2px 0;
      font-family: inherit;
    }
    .ads-tag-btn:hover { background: var(--ds-background-neutral-hovered); }
    .ads-tag-btn.is-selected {
      background: var(--ds-background-brand-subtlest);
      color: var(--ds-text-brand);
      border-color: var(--ds-border-focused);
      font-weight: 600;
    }

    /* Tabs (ADS Tab Bar) */
    .ads-tabs {
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      gap: 4px;
      border-bottom: 2px solid var(--ds-border);
      margin-bottom: 14px;
    }
    .ads-tab {
      position: relative;
      padding: 8px 12px;
      background: transparent;
      border: none;
      color: var(--ds-text-subtle);
      font-family: inherit;
      font-size: 13px;
      font-weight: 500;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 6px;
      white-space: nowrap;
    }
    .ads-tab:hover { color: var(--ds-text); }
    .ads-tab.is-active {
      color: var(--ds-text-brand);
      font-weight: 600;
    }
    .ads-tab.is-active::after {
      content: "";
      position: absolute;
      left: 8px;
      right: 8px;
      bottom: -2px;
      height: 2px;
      background: var(--ds-text-brand);
    }

    /* Toolbar */
    .ads-toolbar {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      align-items: center;
      margin-bottom: 14px;
    }
    .ads-input, .ads-select {
      height: 32px;
      padding: 4px 10px;
      border-radius: 3px;
      border: 2px solid var(--ds-border-input);
      background: var(--ds-background-input);
      color: var(--ds-text);
      font-family: inherit;
      font-size: 13px;
    }
    .ads-input { flex: 1 1 220px; min-width: 180px; }

    /* Account Cards */
    .ads-cards-list {
      display: flex;
      flex-direction: column;
      gap: 12px;
    }
    .ads-account-card {
      background: var(--ds-surface-raised);
      border: 1px solid var(--ds-border);
      border-radius: 8px;
      box-shadow: var(--ds-shadow-raised);
      padding: 16px;
      display: flex;
      gap: 16px;
      align-items: flex-start;
      transition: background-color 0.12s ease;
    }
    .ads-account-card:hover {
      border-color: var(--ds-border-bold);
    }
    @media (max-width: 640px) {
      .ads-account-card { flex-direction: column; }
    }

    .ads-avatar-box {
      width: 72px;
      height: 72px;
      border-radius: 8px;
      border: 1px solid var(--ds-border);
      background: var(--ds-surface-sunken);
      flex-shrink: 0;
      display: flex;
      align-items: center;
      justify-content: center;
      overflow: hidden;
      font-size: 24px;
      font-weight: 700;
      color: var(--ds-text-brand);
    }
    .ads-avatar-box img {
      width: 100%;
      height: 100%;
      object-fit: cover;
      display: block;
    }

    .ads-card-main {
      flex: 1 1 auto;
      min-width: 0;
    }
    .ads-card-header {
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      gap: 10px;
      flex-wrap: wrap;
      margin-bottom: 6px;
    }
    .ads-site-name {
      margin: 0;
      font-size: 16px;
      font-weight: 600;
    }
    .ads-site-name a { color: var(--ds-text); }
    .ads-site-name a:hover { color: var(--ds-link); }

    .ads-badges {
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
      align-items: center;
    }

    .ads-profile-url {
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      gap: 8px;
      margin-bottom: 8px;
      word-break: break-all;
    }

    .ads-tags-row {
      display: flex;
      flex-wrap: wrap;
      gap: 4px;
      margin-bottom: 10px;
    }
    .ads-pill {
      display: inline-block;
      padding: 1px 7px;
      border-radius: 3px;
      background: var(--ds-background-neutral);
      color: var(--ds-text-subtle);
      font-size: 11px;
    }

    /* ADS Dynamic Table */
    .ads-table-wrap {
      overflow-x: auto;
      border: 1px solid var(--ds-border);
      border-radius: 6px;
      background: var(--ds-surface-raised);
    }
    table.ads-table {
      width: 100%;
      border-collapse: collapse;
      font-size: 13px;
    }
    table.ads-table th,
    table.ads-table td {
      text-align: left;
      padding: 8px 10px;
      border-bottom: 1px solid var(--ds-border);
      vertical-align: top;
      word-break: break-word;
    }
    table.ads-table th {
      font-size: 12px;
      font-weight: 600;
      color: var(--ds-text-subtle);
      background: var(--ds-surface-sunken);
      white-space: nowrap;
    }
    table.ads-table tbody tr:last-child td { border-bottom: none; }
    table.ads-table tbody tr:hover { background: var(--ds-surface-hovered); }

    table.ads-kv-table {
      width: 100%;
      border-collapse: collapse;
      margin-top: 6px;
      font-size: 12.5px;
      border: 1px solid var(--ds-border);
      border-radius: 4px;
    }
    table.ads-kv-table th,
    table.ads-kv-table td {
      padding: 5px 8px;
      border-bottom: 1px solid var(--ds-border);
      vertical-align: top;
      text-align: left;
      word-break: break-word;
    }
    table.ads-kv-table th {
      width: 170px;
      color: var(--ds-text-subtle);
      font-weight: 600;
      background: var(--ds-surface-sunken);
    }
    table.ads-kv-table tr:last-child th,
    table.ads-kv-table tr:last-child td { border-bottom: none; }

    .ads-empty {
      text-align: center;
      padding: 36px 16px;
      color: var(--ds-text-subtlest);
      background: var(--ds-surface-raised);
      border: 1px dashed var(--ds-border);
      border-radius: 8px;
    }

    /* Floating Instant Scroll Controls (Bottom-Right) */
    .ads-scroll-fab {
      position: fixed;
      right: 24px;
      bottom: 24px;
      z-index: 200;
      display: flex;
      flex-direction: column;
      gap: 8px;
    }
    .ads-scroll-btn {
      width: 40px;
      height: 40px;
      border-radius: 8px;
      border: 1px solid var(--ds-border);
      background: var(--ds-surface-overlay);
      color: var(--ds-text);
      box-shadow: var(--ds-shadow-overlay);
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      font-size: 16px;
      font-weight: 600;
      transition: background-color 0.12s ease, border-color 0.12s ease;
    }
    .ads-scroll-btn:hover {
      background: var(--ds-surface-hovered);
      border-color: var(--ds-border-bold);
      color: var(--ds-link);
    }
    .ads-scroll-btn:focus-visible {
      outline: 2px solid var(--ds-border-focused);
      outline-offset: 2px;
    }

    @media print {
      .ads-topbar-actions, .ads-toolbar, .ads-tabs, .ads-scroll-fab { display: none !important; }
      .ads-workspace { grid-template-columns: 1fr; }
      body { padding-bottom: 0; background: #FFFFFF; }
    }
  </style>
</head>
<body>
  <header class="ads-topbar">
    <div class="ads-brand">
      <svg class="ads-logo" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" aria-hidden="true">
        <g fill="var(--ds-dot-fill)">
          <circle cx="46" cy="54" r="6.5"/><circle cx="46" cy="36.5" r="3.6"/><circle cx="63.5" cy="54" r="3.6"/>
          <circle cx="58.37" cy="66.37" r="2.8"/><circle cx="46" cy="71.5" r="2.8"/><circle cx="33.63" cy="66.37" r="2.8"/>
          <circle cx="28.5" cy="54" r="2.8"/><circle cx="33.63" cy="41.63" r="3.6"/><circle cx="46" cy="22.5" r="3.8"/>
          <circle cx="77.5" cy="54" r="3.8"/><circle cx="73.28" cy="69.75" r="2.9"/><circle cx="61.75" cy="81.28" r="2.9"/>
          <circle cx="46" cy="85.5" r="2.9"/><circle cx="30.25" cy="81.28" r="2.9"/><circle cx="18.72" cy="69.75" r="2.9"/>
          <circle cx="14.5" cy="54" r="2.9"/><circle cx="18.72" cy="38.25" r="2.9"/><circle cx="30.25" cy="26.72" r="2.9"/>
        </g>
        <g fill="var(--ds-dot-accent)" stroke="var(--ds-dot-accent)">
          <circle cx="71.1" cy="28.9" r="11" fill="none" stroke-width="2.6"/>
          <circle cx="71.1" cy="28.9" r="5.5" stroke="none"/>
        </g>
      </svg>
      <div class="ads-title-group">
        <h1 class="ads-page-title">
          <span>Perra OSINT Dossier</span>
          <span class="ads-lozenge ads-lozenge-info">{{ username }}</span>
        </h1>
        <div class="ads-subtitle">
          Generated at {{ generated_at }} &middot;
          <a href="https://github.com/codevcn/perra" target="_blank" rel="noopener noreferrer">Perra (Persona Radar)</a>
        </div>
      </div>
    </div>

    <div class="ads-topbar-actions">
      <button type="button" class="ads-btn" id="copy-urls-btn" title="Copy all confirmed profile URLs">
        Copy Claimed URLs
      </button>
      <button type="button" class="ads-btn" id="theme-toggle-btn" aria-label="Toggle Light/Dark theme">
        <span id="theme-toggle-label">Theme</span>
      </button>
    </div>
  </header>

  <main class="ads-container">
    <!-- KPI Strip -->
    <section class="ads-kpi-grid" aria-label="Scan summary metrics">
      <div class="ads-kpi-card">
        <span class="ads-kpi-label">Confirmed Accounts</span>
        <span class="ads-kpi-value">{{ ui_stats.claimed_count }}</span>
        <span class="ads-kpi-hint">
          {% if ui_stats.keyword_match_count %}
            {{ ui_stats.keyword_match_count }} keyword match(es)
          {% else %}
            Exact status matches
          {% endif %}
        </span>
      </div>
      <div class="ads-kpi-card">
        <span class="ads-kpi-label">Similar Matches</span>
        <span class="ads-kpi-value">{{ ui_stats.similar_count }}</span>
        <span class="ads-kpi-hint">Requires manual verification</span>
      </div>
      <div class="ads-kpi-card">
        <span class="ads-kpi-label">Errors / Unknown</span>
        <span class="ads-kpi-value">{{ ui_stats.unknown_count }}</span>
        <span class="ads-kpi-hint">Out of {{ ui_stats.total_checked }} checks</span>
      </div>
      <div class="ads-kpi-card">
        <span class="ads-kpi-label">Extracted Profiles</span>
        <span class="ads-kpi-value">{{ ui_stats.extended_info_count }}</span>
        <span class="ads-kpi-hint">
          {% if first_seen %}First seen: {{ first_seen }}{% else %}{{ ui_stats.targets | length }} target(s) scanned{% endif %}
        </span>
      </div>
    </section>

    <!-- Diagnostic Banners -->
    {% if ui_stats.dns_error_count > 0 %}
    <div class="ads-banner ads-banner-warning" role="status">
      <div>
        <strong>DNS Failures Detected ({{ ui_stats.dns_error_count }}):</strong>
        On Windows or VPN networks, rerun with <code class="mono">--dns-resolver threaded</code> to resolve via OS DNS.
      </div>
    </div>
    {% endif %}
    {% if ui_stats.rate_limit_count > 0 %}
    <div class="ads-banner ads-banner-info" role="status">
      <div>
        <strong>Rate Limits Observed ({{ ui_stats.rate_limit_count }}):</strong>
        Try lowering concurrency with <code class="mono">-n 10 --retries 2</code> for skipped hosts.
      </div>
    </div>
    {% endif %}

    <div class="ads-workspace">
      <!-- Sidebar: Dossier Summary -->
      <aside aria-label="Target summary and tags">
        <div class="ads-panel">
          <h2 class="ads-panel-title">Executive Brief</h2>
          <p style="margin: 0; font-size: 13px; color: var(--ds-text);">{{ brief }}</p>
        </div>

        <div class="ads-panel">
          <h2 class="ads-panel-title">Supposed Identity Signals</h2>
          <div class="ads-meta-list">
            {% for k, v in supposed_data.items() %}
            <div class="ads-meta-row">
              <span class="ads-meta-key">{{ k }}</span>
              <span class="ads-meta-val">{{ v }}</span>
            </div>
            {% else %}
            <div class="ads-meta-row">
              <span class="ads-meta-val text-muted">No common profile fields aggregated yet.</span>
            </div>
            {% endfor %}

            {% if countries_tuple_list %}
            <div class="ads-meta-row">
              <span class="ads-meta-key">Geography</span>
              <span class="ads-meta-val">Geo: {% for k, v in countries_tuple_list %}{{ k }} <span class="text-muted">({{ v }})</span>{{ ", " if not loop.last }}{% endfor %}</span>
            </div>
            {% endif %}

            {% if interests_tuple_list %}
            <div class="ads-meta-row">
              <span class="ads-meta-key">Top Interests &amp; Tags</span>
              <span class="ads-meta-val">Interests: {% for k, v in interests_tuple_list %}{{ k }} <span class="text-muted">({{ v }})</span>{{ ", " if not loop.last }}{% endfor %}</span>
            </div>
            {% endif %}

            {% if first_seen %}
            <div class="ads-meta-row">
              <span class="ads-meta-key">First Seen</span>
              <span class="ads-meta-val mono">{{ first_seen }}</span>
            </div>
            {% endif %}

            {% if ui_stats.discovered_ids %}
            <div class="ads-meta-row">
              <span class="ads-meta-key">Recursive IDs Discovered</span>
              <div class="ads-badges" style="margin-top: 4px;">
                {% for item in ui_stats.discovered_ids %}
                <span class="ads-lozenge ads-lozenge-discovery">{{ item.value }} ({{ item.type }})</span>
                {% endfor %}
              </div>
            </div>
            {% endif %}
          </div>
        </div>

        {% if ui_stats.all_tags %}
        <div class="ads-panel">
          <h2 class="ads-panel-title">
            <span>Filter by Tag</span>
            <button type="button" class="ads-btn" id="clear-tag-btn" style="height: 24px; padding: 0 8px; font-size: 11px;">Clear</button>
          </h2>
          <div id="tag-filter-list">
            {% for tag in ui_stats.all_tags %}
            <button type="button" class="ads-tag-btn" data-tag="{{ tag }}">{{ tag }}</button>
            {% endfor %}
          </div>
        </div>
        {% endif %}
      </aside>

      <!-- Main Panel: Interactive Results -->
      <section aria-label="Search results">
        <div class="ads-panel" style="margin-bottom: 12px; padding-bottom: 12px;">
          <div class="ads-tabs" role="tablist">
            <button type="button" class="ads-tab is-active" role="tab" data-tab="claimed" aria-selected="true">
              Confirmed <span class="ads-lozenge ads-lozenge-success">{{ ui_stats.claimed_count }}</span>
            </button>
            <button type="button" class="ads-tab" role="tab" data-tab="similar" aria-selected="false">
              Similar <span class="ads-lozenge ads-lozenge-warning">{{ ui_stats.similar_count }}</span>
            </button>
            <button type="button" class="ads-tab" role="tab" data-tab="errors" aria-selected="false">
              Errors / Unknown <span class="ads-lozenge ads-lozenge-danger">{{ ui_stats.unknown_count }}</span>
            </button>
          </div>

          <div class="ads-toolbar">
            <input type="search" id="search-input" class="ads-input" placeholder="Search site, username, URL, bio, fullname..." aria-label="Filter results" />
            {% if ui_stats.targets | length > 1 %}
            <select id="target-filter" class="ads-select" aria-label="Filter by target identifier">
              <option value="">All targets ({{ ui_stats.targets | length }})</option>
              {% for t in ui_stats.targets %}
              <option value="{{ t.username }}">{{ t.username }} ({{ t.found_count }})</option>
              {% endfor %}
            </select>
            {% endif %}
            <select id="sort-select" class="ads-select" aria-label="Sort confirmed accounts">
              <option value="default">Sort: Default</option>
              <option value="data">Sort: Richest Data</option>
              <option value="rank">Sort: Alexa Rank</option>
              <option value="name">Sort: Site Name A–Z</option>
            </select>
            <button type="button" class="ads-btn is-active" id="view-cards-btn" title="Card view">Cards</button>
            <button type="button" class="ads-btn" id="view-table-btn" title="Compact table view">Table</button>
          </div>
          <div id="visible-count-bar" class="text-muted" style="font-size: 12px;"></div>
        </div>

        <!-- Tab 1: Confirmed Claimed Accounts -->
        <div id="panel-claimed">
          <div id="cards-container" class="ads-cards-list">
            {% set ns = namespace(idx=0) %}
            {% for u, t, data in results %}
              {% for k, v in data.items() %}
                {% if v.found and not v.is_similar %}
                  {% set ns.idx = ns.idx + 1 %}
                  {% set avatar = safe_avatar_url(v.status and v.status.ids_data and v.status.ids_data.image) %}
                  {% set kw_hit = v.status and v.status.keyword_match_status and v.status.keyword_match_status.value == 'Keyword Found' %}
                  {% set fields_count = (v.ids_data | length) if v.ids_data else 0 %}
                  {% set site_tags = (v.status.tags | join(',')) if (v.status and v.status.tags) else '' %}
                  <article class="ads-account-card result-item"
                           data-idx="{{ ns.idx }}"
                           data-site="{{ k | lower }}"
                           data-target="{{ u }}"
                           data-rank="{{ v.rank if v.rank is defined and v.rank else 99999999 }}"
                           data-fields="{{ fields_count }}"
                           data-tags="{{ site_tags }}"
                           data-url="{{ safe_external_url(v.url_user) }}"
                           data-search="{{ (k ~ ' ' ~ u ~ ' ' ~ (v.url_user or '') ~ ' ' ~ site_tags) | lower }}">
                    <div class="ads-avatar-box">
                      {% if avatar %}
                      <img src="{{ avatar }}" alt="{{ k }} avatar" loading="lazy" onerror="this.style.display='none'; this.nextElementSibling.style.display='flex';" />
                      <span style="display:none; width:100%; height:100%; align-items:center; justify-content:center;">{{ k[:1] | upper }}</span>
                      {% else %}
                      <span>{{ k[:1] | upper }}</span>
                      {% endif %}
                    </div>

                    <div class="ads-card-main">
                      <div class="ads-card-header">
                        <h3 class="ads-site-name">
                          <a href="{{ safe_external_url(v.url_main) }}" target="_blank" rel="noopener noreferrer">{{ k }}</a>
                        </h3>
                        <div class="ads-badges">
                          {% if kw_hit %}
                          <span class="ads-lozenge ads-lozenge-discovery">Keyword Match</span>
                          {% endif %}
                          <span class="ads-lozenge ads-lozenge-success">Claimed</span>
                          <span class="ads-lozenge ads-lozenge-neutral">{{ u }}</span>
                          {% if v.http_status %}
                          <span class="ads-lozenge ads-lozenge-neutral mono">HTTP {{ v.http_status }}</span>
                          {% endif %}
                        </div>
                      </div>

                      <div class="ads-profile-url">
                        <a href="{{ safe_external_url(v.url_user) }}" target="_blank" rel="noopener noreferrer" class="mono">{{ v.url_user }}</a>
                        {% if v.url_user %}
                        <span class="text-muted" style="font-size: 11px;">
                          (<a href="https://web.archive.org/web/*/{{ v.url_user }}" target="_blank" rel="noopener noreferrer">web.archive.org</a>
                          &middot;
                          <a href="https://archive.is/newest/{{ v.url_user }}" target="_blank" rel="noopener noreferrer">archive.is</a>)
                        </span>
                        {% endif %}
                      </div>

                      {% if v.status and v.status.tags %}
                      <div class="ads-tags-row">
                        {% for tag in v.status.tags %}
                        <span class="ads-pill">{{ tag }}</span>
                        {% endfor %}
                      </div>
                      {% endif %}

                      {% if v.ids_data %}
                      <table class="ads-kv-table">
                        <tbody>
                        {% for k1, v1 in v.ids_data.items() %}
                          {% if k1 != 'image' %}
                          <tr>
                            <th>{{ title(k1) }}</th>
                            <td>{% if v1 is iterable and (v1 is not string and v1 is not mapping) %}{{ v1 | map('string') | join(', ') }}{% else %}{{ detect_link(v1) }}{% endif %}</td>
                          </tr>
                          {% endif %}
                        {% endfor %}
                        </tbody>
                      </table>
                      {% endif %}
                    </div>
                  </article>
                {% endif %}
              {% endfor %}
            {% endfor %}
          </div>

          <!-- Compact Table View -->
          <div id="table-container" class="ads-table-wrap hidden">
            <table class="ads-table">
              <thead>
                <tr>
                  <th>Site</th>
                  <th>Target</th>
                  <th>Profile URL</th>
                  <th>HTTP</th>
                  <th>Tags</th>
                  <th>Extracted Info</th>
                </tr>
              </thead>
              <tbody id="table-body">
                {% set tns = namespace(idx=0) %}
                {% for u, t, data in results %}
                  {% for k, v in data.items() %}
                    {% if v.found and not v.is_similar %}
                      {% set tns.idx = tns.idx + 1 %}
                      {% set fields_count = (v.ids_data | length) if v.ids_data else 0 %}
                      {% set site_tags = (v.status.tags | join(',')) if (v.status and v.status.tags) else '' %}
                      <tr class="result-table-row"
                          data-idx="{{ tns.idx }}"
                          data-site="{{ k | lower }}"
                          data-target="{{ u }}"
                          data-rank="{{ v.rank if v.rank is defined and v.rank else 99999999 }}"
                          data-fields="{{ fields_count }}"
                          data-tags="{{ site_tags }}"
                          data-search="{{ (k ~ ' ' ~ u ~ ' ' ~ (v.url_user or '') ~ ' ' ~ site_tags) | lower }}">
                        <td><strong>{{ k }}</strong></td>
                        <td><span class="ads-lozenge ads-lozenge-neutral">{{ u }}</span></td>
                        <td class="mono"><a href="{{ safe_external_url(v.url_user) }}" target="_blank" rel="noopener noreferrer">{{ v.url_user }}</a></td>
                        <td class="mono">{{ v.http_status or '-' }}</td>
                        <td>{{ site_tags or '-' }}</td>
                        <td>
                          {% if v.ids_data %}
                            {{ fields_count }} field(s)
                          {% else %}
                            <span class="text-muted">—</span>
                          {% endif %}
                        </td>
                      </tr>
                    {% endif %}
                  {% endfor %}
                {% endfor %}
              </tbody>
            </table>
          </div>

          <div id="claimed-empty" class="ads-empty hidden">
            No confirmed accounts match the active filter.
          </div>
        </div>

        <!-- Tab 2: Similar Matches -->
        <div id="panel-similar" class="hidden">
          {% if ui_similar %}
          <div class="ads-banner ads-banner-warning">
            <div>
              <strong>Potential False Positives:</strong>
              Similar matches reflect relaxed/substring matching and are excluded from primary confirmed counts. Verify manually before linking identities.
            </div>
          </div>
          <div class="ads-table-wrap">
            <table class="ads-table">
              <thead>
                <tr>
                  <th>Site</th>
                  <th>Target</th>
                  <th>Candidate URL</th>
                  <th>HTTP</th>
                  <th>Tags</th>
                </tr>
              </thead>
              <tbody>
                {% for item in ui_similar %}
                <tr class="similar-row"
                    data-target="{{ item.username }}"
                    data-tags="{{ item.tags | join(',') }}"
                    data-search="{{ (item.site ~ ' ' ~ item.username ~ ' ' ~ item.url_user) | lower }}">
                  <td><strong>{{ item.site }}</strong></td>
                  <td><span class="ads-lozenge ads-lozenge-warning">{{ item.username }}</span></td>
                  <td class="mono"><a href="{{ safe_external_url(item.url_user) }}" target="_blank" rel="noopener noreferrer">{{ item.url_user }}</a></td>
                  <td class="mono">{{ item.http_status or '-' }}</td>
                  <td>{{ item.tags | join(', ') or '-' }}</td>
                </tr>
                {% endfor %}
              </tbody>
            </table>
          </div>
          {% else %}
          <div class="ads-empty">No similar-username matches were returned in this scan.</div>
          {% endif %}
        </div>

        <!-- Tab 3: Unknown / Errors Breakdown -->
        <div id="panel-errors" class="hidden">
          {% if ui_errors %}
          <div class="ads-banner ads-banner-info">
            <div>
              <strong>Interpreting Unknowns:</strong>
              Sites listed here failed due to timeouts, WAF/bot protection, rate limits, or DNS issues &mdash; they do <em>not</em> indicate an account does not exist.
            </div>
          </div>
          <div class="ads-table-wrap">
            <table class="ads-table">
              <thead>
                <tr>
                  <th>Error Reason</th>
                  <th>Count</th>
                  <th>Affected Sites (sample)</th>
                </tr>
              </thead>
              <tbody>
                {% for grp in ui_errors %}
                <tr>
                  <td><span class="ads-lozenge ads-lozenge-danger">{{ grp.reason }}</span></td>
                  <td class="mono"><strong>{{ grp.count }}</strong></td>
                  <td>
                    {{ grp.sites | join(', ') }}
                    {% if grp.more %}<span class="text-muted">(+{{ grp.more }} more)</span>{% endif %}
                  </td>
                </tr>
                {% endfor %}
              </tbody>
            </table>
          </div>
          {% else %}
          <div class="ads-empty">Zero check errors recorded. All checked sites returned decisive results.</div>
          {% endif %}
        </div>
      </section>
    </div>
  </main>

  <!-- Instant Scroll Controls (Bottom-Right) -->
  <div class="ads-scroll-fab" role="group" aria-label="Page scroll controls">
    <button type="button" class="ads-scroll-btn" id="scroll-top-btn" title="Scroll to top (instant)" aria-label="Scroll to top">
      <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor" aria-hidden="true">
        <path d="M8 3.293l4.354 4.353-.708.708L8.5 5.207V13h-1V5.207L4.354 8.354l-.708-.708L8 3.293z"/>
      </svg>
    </button>
    <button type="button" class="ads-scroll-btn" id="scroll-bottom-btn" title="Scroll to bottom (instant)" aria-label="Scroll to bottom">
      <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor" aria-hidden="true">
        <path d="M8 12.707l-4.354-4.353.708-.708L7.5 10.793V3h1v7.793l3.146-3.147.708.708L8 12.707z"/>
      </svg>
    </button>
  </div>

  <script>
    (function () {
      var htmlEl = document.documentElement;
      var themeBtn = document.getElementById('theme-toggle-btn');
      var themeLabel = document.getElementById('theme-toggle-label');

      function syncThemeLabel() {
        var mode = htmlEl.getAttribute('data-color-mode') || 'light';
        if (themeLabel) themeLabel.textContent = mode === 'dark' ? 'Switch to Light' : 'Switch to Dark';
      }
      syncThemeLabel();

      if (themeBtn) {
        themeBtn.addEventListener('click', function () {
          var next = htmlEl.getAttribute('data-color-mode') === 'dark' ? 'light' : 'dark';
          htmlEl.setAttribute('data-color-mode', next);
          try { localStorage.setItem('perra-ads-theme', next); } catch (e) {}
          syncThemeLabel();
        });
      }

      if (window.matchMedia) {
        var mq = window.matchMedia('(prefers-color-scheme: dark)');
        var onSystemChange = function (e) {
          var saved = null;
          try { saved = localStorage.getItem('perra-ads-theme'); } catch (err) {}
          if (!saved) {
            htmlEl.setAttribute('data-color-mode', e.matches ? 'dark' : 'light');
            syncThemeLabel();
          }
        };
        if (mq.addEventListener) mq.addEventListener('change', onSystemChange);
      }

      // Bottom-right instant scroll controls
      var topBtn = document.getElementById('scroll-top-btn');
      var bottomBtn = document.getElementById('scroll-bottom-btn');
      if (topBtn) {
        topBtn.addEventListener('click', function () {
          window.scrollTo({ top: 0, behavior: 'instant' });
        });
      }
      if (bottomBtn) {
        bottomBtn.addEventListener('click', function () {
          var h = Math.max(document.body.scrollHeight, document.documentElement.scrollHeight);
          window.scrollTo({ top: h, behavior: 'instant' });
        });
      }

      // Tabs
      var tabs = document.querySelectorAll('.ads-tab');
      var panels = {
        claimed: document.getElementById('panel-claimed'),
        similar: document.getElementById('panel-similar'),
        errors: document.getElementById('panel-errors')
      };
      tabs.forEach(function (tab) {
        tab.addEventListener('click', function () {
          var name = tab.getAttribute('data-tab');
          tabs.forEach(function (t) {
            var active = t === tab;
            t.classList.toggle('is-active', active);
            t.setAttribute('aria-selected', active ? 'true' : 'false');
          });
          Object.keys(panels).forEach(function (k) {
            if (panels[k]) panels[k].classList.toggle('hidden', k !== name);
          });
        });
      });

      // Cards / Table switcher
      var cardsBtn = document.getElementById('view-cards-btn');
      var tableBtn = document.getElementById('view-table-btn');
      var cardsContainer = document.getElementById('cards-container');
      var tableContainer = document.getElementById('table-container');
      if (cardsBtn && tableBtn && cardsContainer && tableContainer) {
        cardsBtn.addEventListener('click', function () {
          cardsBtn.classList.add('is-active');
          tableBtn.classList.remove('is-active');
          cardsContainer.classList.remove('hidden');
          tableContainer.classList.add('hidden');
        });
        tableBtn.addEventListener('click', function () {
          tableBtn.classList.add('is-active');
          cardsBtn.classList.remove('is-active');
          tableContainer.classList.remove('hidden');
          cardsContainer.classList.add('hidden');
        });
      }

      // Filtering & Sorting
      var searchInput = document.getElementById('search-input');
      var targetSelect = document.getElementById('target-filter');
      var sortSelect = document.getElementById('sort-select');
      var tagButtons = document.querySelectorAll('.ads-tag-btn');
      var clearTagBtn = document.getElementById('clear-tag-btn');
      var countBar = document.getElementById('visible-count-bar');
      var claimedEmpty = document.getElementById('claimed-empty');
      var selectedTag = '';

      function applyFilters() {
        var q = (searchInput ? searchInput.value : '').trim().toLowerCase();
        var tgt = targetSelect ? targetSelect.value : '';
        var cards = Array.prototype.slice.call(document.querySelectorAll('.result-item'));
        var rows = Array.prototype.slice.call(document.querySelectorAll('.result-table-row'));
        var visible = 0;

        cards.forEach(function (el) {
          var tags = (el.getAttribute('data-tags') || '').split(',');
          var text = (el.getAttribute('data-search') || '') + ' ' + (el.textContent || '').toLowerCase();
          var elTarget = el.getAttribute('data-target') || '';
          var ok = (!q || text.indexOf(q) !== -1)
                && (!tgt || elTarget === tgt)
                && (!selectedTag || tags.indexOf(selectedTag) !== -1);
          el.classList.toggle('hidden', !ok);
          if (ok) visible += 1;
        });

        rows.forEach(function (el) {
          var tags = (el.getAttribute('data-tags') || '').split(',');
          var text = (el.getAttribute('data-search') || '') + ' ' + (el.textContent || '').toLowerCase();
          var elTarget = el.getAttribute('data-target') || '';
          var ok = (!q || text.indexOf(q) !== -1)
                && (!tgt || elTarget === tgt)
                && (!selectedTag || tags.indexOf(selectedTag) !== -1);
          el.classList.toggle('hidden', !ok);
        });

        if (countBar) {
          countBar.textContent = 'Showing ' + visible + ' of ' + cards.length + ' confirmed account(s)'
            + (selectedTag ? ' · tag: ' + selectedTag : '');
        }
        if (claimedEmpty) {
          claimedEmpty.classList.toggle('hidden', visible > 0);
        }
      }

      function applySort() {
        var mode = sortSelect ? sortSelect.value : 'default';
        function cmp(a, b) {
          if (mode === 'data') {
            return (parseInt(b.getAttribute('data-fields') || '0', 10) - parseInt(a.getAttribute('data-fields') || '0', 10))
              || (parseInt(a.getAttribute('data-idx') || '0', 10) - parseInt(b.getAttribute('data-idx') || '0', 10));
          }
          if (mode === 'rank') {
            return (parseInt(a.getAttribute('data-rank') || '99999999', 10) - parseInt(b.getAttribute('data-rank') || '99999999', 10));
          }
          if (mode === 'name') {
            return (a.getAttribute('data-site') || '').localeCompare(b.getAttribute('data-site') || '');
          }
          return parseInt(a.getAttribute('data-idx') || '0', 10) - parseInt(b.getAttribute('data-idx') || '0', 10);
        }
        if (cardsContainer) {
          Array.prototype.slice.call(cardsContainer.querySelectorAll('.result-item')).sort(cmp).forEach(function (el) {
            cardsContainer.appendChild(el);
          });
        }
        var tbody = document.getElementById('table-body');
        if (tbody) {
          Array.prototype.slice.call(tbody.querySelectorAll('.result-table-row')).sort(cmp).forEach(function (el) {
            tbody.appendChild(el);
          });
        }
      }

      tagButtons.forEach(function (btn) {
        btn.addEventListener('click', function () {
          var t = btn.getAttribute('data-tag') || '';
          selectedTag = (selectedTag === t) ? '' : t;
          tagButtons.forEach(function (b) { b.classList.toggle('is-selected', b.getAttribute('data-tag') === selectedTag); });
          applyFilters();
        });
      });
      if (clearTagBtn) {
        clearTagBtn.addEventListener('click', function () {
          selectedTag = '';
          tagButtons.forEach(function (b) { b.classList.remove('is-selected'); });
          applyFilters();
        });
      }
      if (searchInput) searchInput.addEventListener('input', applyFilters);
      if (targetSelect) targetSelect.addEventListener('change', applyFilters);
      if (sortSelect) sortSelect.addEventListener('change', applySort);

      // Copy visible confirmed URLs
      var copyBtn = document.getElementById('copy-urls-btn');
      if (copyBtn) {
        copyBtn.addEventListener('click', function () {
          var urls = [];
          document.querySelectorAll('.result-item:not(.hidden)').forEach(function (el) {
            var u = el.getAttribute('data-url');
            if (u && u !== '#') urls.push(u);
          });
          var text = urls.join('\n');
          if (navigator.clipboard && navigator.clipboard.writeText) {
            navigator.clipboard.writeText(text).then(function () {
              copyBtn.textContent = 'Copied ' + urls.length + ' URL(s)';
              setTimeout(function () { copyBtn.textContent = 'Copy Claimed URLs'; }, 1800);
            });
          }
        });
      }

      applyFilters();
    })();
  </script>
</body>
</html>
