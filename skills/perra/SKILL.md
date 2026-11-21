---
name: perra
description: "OSINT username and identifier investigation using the Perra (Persona Radar) CLI. Use when asked to search usernames, profile URLs, or supported IDs across thousands of sites, generate OSINT reports (JSON, Markdown, HTML, PDF, Graph, Neo4j, CSV, TXT, XMind), launch the Perra web interface, or check/update the Perra CLI."
---

# Perra (Persona Radar) CLI Guide for AI Agents

**Perra** (Persona Radar) is an OSINT CLI and Python library for collecting account dossiers across thousands of websites by username or supported identifier, extracting profile metadata, running recursive identifier discovery, and exporting structured reports.

---

## 1. Safety, Ethics, and Truthfulness Rules

- **Lawful OSINT only:** Use `perra` strictly for authorized investigations, public-information verification, defensive OSINT, or testing. Respect privacy laws (GDPR, CCPA, local regulations).
- **Never over-claim identity correlation:** A username like `alex` or `dev` frequently belongs to **multiple unrelated people** across platforms. Only conclude two accounts belong to the same person when corroborating signals align (`fullname`, `bio`, `location`, `website`, `links`, linked IDs).
- **Verify `perra` is installed before running:** Run `perra --version`. If missing, install via the Inno Setup installer or `scripts/setup_manager.py`.

---

## 2. Mandatory Non-Interactive Rules for AI Agents

When invoking `perra` from a shell/tool call:

1. **Always disable interactive terminal UI / ANSI noise:**
   ```bash
   perra <username> --no-progressbar --no-color
   ```
2. **Prefer structured report outputs over scraping stdout:**
   Every CLI scan automatically saves an Atlassian Design System HTML UI report (`report_<username>_plain.html` in `./reports/` or `-fo <output_dir>`) **without opening a browser**. Do **NOT** parse HTML files for agent data extraction — pass `-J ndjson`, `-J simple`, or `-M` (`--md`) to read structured files reliably, or use `--no-html` if HTML output is unwanted:
   ```bash
   perra <username> --no-progressbar --no-color -J ndjson -M -fo ./perra_out
   ```
   You can return the generated `file:///.../report_<username>_plain.html` path to the user for interactive visual review. **Never pass `--open-html`** unless the user explicitly asks to launch a browser (`--open-html` is also auto-suppressed whenever `--no-progressbar` or `CI` is set).
3. **Scope scans sensibly:**
   - Default scans the **top 500** sites by traffic rank.
   - Use `--site GitHub,Reddit` or `--tags coding,us` or `--top-sites 200` for fast, focused queries.
   - Only pass `-a` (`--all-sites`, ~9,500+ sites) when the user explicitly requests an exhaustive scan, as it takes significantly longer and increases rate-limit / WAF blocks.
4. **Windows / VPN DNS failures:**
   If you see many `Connecting failure (DNS)` or `Could not contact DNS servers` errors, rerun immediately with:
   ```bash
   perra <username> --dns-resolver threaded --no-progressbar --no-color
   ```
5. **Offline / deterministic / CI runs:**
   Pass `--no-autoupdate --no-update-check` to skip both upstream database refresh and GitHub CLI release checks:
   ```bash
   perra <username> --no-autoupdate --no-update-check --no-progressbar --no-color
   ```
6. **Avoid interactive / blocking modes unless explicitly requested:**
   - **Do NOT run** `perra --submit` (interactive `input()` prompts).
   - **Do NOT run** `perra --self-check` without `--auto-disable` or interactive awareness (prompts `Do you want to save changes permanently?` if DB changes are needed).
   - **Do NOT run** `perra` with zero arguments in automation (may enter interactive prompt if launched standalone without args; always pass `--help`, a username, or an explicit mode flag).
   - `perra --web <port>` starts a long-running Flask server (blocking). Only launch it as a background/daemon process when the user asks for the Web UI.

---

## 3. Core CLI Commands & Flags

### Basic & Multi-Target Search
```bash
# Single username (top 500 sites)
perra alice --no-progressbar --no-color -J ndjson

# Multiple usernames
perra alice bob --no-progressbar --no-color -M

# Targeted sites or categories
perra alice --site GitHub --site GitLab --no-progressbar --no-color
perra alice --tags coding,social --exclude-tags porn,dating --no-progressbar --no-color

# All sites (~9,500+)
perra alice -a --no-progressbar --no-color -M
```

### Input Files, Piped Input, & Identifier Types
`--id-type` supports 12 identifier types:
`username` (default), `yandex_public_id`, `gaia_id`, `vk_id`, `ok_id`, `wikimapia_uid`, `steam_id`, `uidme_uguid`, `yelp_userid`, `orcid`, `qq_id`, `bilibili_id`.

```bash
# Non-username ID
perra 123456 --id-type vk_id --no-progressbar --no-color

# File with mixed IDs (`id_type:value` lines, `#` comments ignored)
perra --input-file ids.txt --no-progressbar --no-color -M

# Read from stdin
printf "alice\nvk_id:12345\n" | perra --input-file - --no-progressbar --no-color
```

### Discovery & Enrichment
| Flag | Purpose | Notes |
| --- | --- | --- |
| `--parse URL` | Extract username/IDs from a profile URL, then search them | Good starting point from a single link |
| `--permute` | Generate username permutations from 2+ positional usernames | Applies only to positional `username` args |
| `--enrich` | Fetch secondary API/JSON mutations (`socid_extractor`) | Adds extra requests per claimed site |
| `--keywords k1 k2` | Highlight claimed pages containing keywords (`[++]`) | Case-insensitive substring match |
| `--no-recursion` | Disable automatic recursive searches on extracted IDs | Recommended when fast/bounded run is needed |
| `--no-extracting` | Disable `socid_extractor` metadata parsing | Faster, skips profile detail extraction |
| `--with-domains` | Experimental DNS A-record check for `{username}.<tld>` | Treat hits as weak leads (parking/wildcards) |

### Networking, Proxies & Anti-Bot
| Flag | Purpose | Default / Example |
| --- | --- | --- |
| `--timeout SEC` | Per-site request timeout | Default `30` |
| `--retries N` | Retry temporary failures (`Rate limited`, timeout, DNS, etc.) | Default `0` |
| `-n`, `--max-connections N` | Concurrent worker limit | Default `100` (lower to `10`–`20` if rate-limited) |
| `--dns-resolver` | `async` (aiodns) or `threaded` (OS getaddrinfo) | Use `threaded` on Windows/VPN DNS errors |
| `-p`, `--proxy URL` | Route all checks & DB updates through HTTP/SOCKS proxy | `socks5://127.0.0.1:1080` |
| `--tor-proxy URL` | Route `.onion` sites only | `socks5://127.0.0.1:9050` |
| `--i2p-proxy URL` | Route `.i2p` sites only | `http://127.0.0.1:4444` |
| `--cookies-jar-file PATH` | Netscape `cookies.txt` for login-gated sites | — |
| `--cloudflare-bypass` | Route CF-protected sites through configured FlareSolverr | Requires running FlareSolverr & settings config |

### Report Formats
Reports are saved in `./reports/` by default (override with `-fo PATH`). Since HTML reporting is enabled by default, every CLI scan generates `report_<username>_plain.html` (and saves it silently without launching a browser).

| Flag | Output | Scope |
| --- | --- | --- |
| *(default)* / `-H`, `--html` | Self-contained Atlassian Design System HTML UI (`report_<username>_plain.html`): Light/Dark OS theme + manual top-right toggle, Cards & Table views, `Confirmed` / `Similar` / `Errors / Unknown` tabs, instant Top/Bottom scroll buttons | Combined |
| `--no-html` | Disable default HTML report generation (recommended with `-J ndjson` in tight loops if HTML is unwanted) | Control flag |
| `--open-html` | Open the generated HTML report in the default browser after completion, or when run alone (`perra --open-html`, optionally with `-fo PATH`) open the most recently saved HTML report (automatically suppressed when `--no-progressbar`, `CI`, or `PERRA_NO_OPEN=1` is set — **agents should omit this flag**) | Control flag |
| `-J simple` / `-J ndjson` | JSON or newline-delimited JSON | Per username (best for agents) |
| `-M`, `--md` | Markdown summary + account details | Combined across all usernames |
| `-P`, `--pdf` | PDF report (requires `[pdf]` extra / included in installer) | Combined |
| `-G`, `--graph` | Interactive `vis-network` HTML graph | Combined |
| `--neo4j` | Idempotent `*_neo4j.cypher` import script | Combined |
| `-C`, `--csv` | CSV table including status/HTTP code/error reason | Per username |
| `-T`, `--txt` | Plain list of claimed profile URLs | Per username |
| `-X`, `--xmind` | Legacy XML `.xmind` mindmap with manifest | Per username |
| `--reports-sorting data` | Sort accounts by richness of extracted fields | Default is completion order |

### AI Summary Mode
```bash
# Requires OPENAI_API_KEY env var or openai_api_key in settings.json
perra alice --ai --no-progressbar --no-color
perra alice --ai --ai-model gpt-4o-mini --no-progressbar --no-color
```
Configured via `openai_api_key`, `openai_model`, and `openai_api_base_url` in `~/.perra/settings.json`.

### Web Interface
```bash
perra --web 5000
# Serves Flask UI at http://127.0.0.1:5000 (live SSE scan + graph + downloads)
```

### Updates (CLI App & Site Database)
- **Non-blocking CLI update check:** Every normal `perra` invocation reads local cache `~/.perra/cli_update_state.json` and spawns a detached background check against GitHub (`codevcn/perra`) without blocking execution.
  - Disable with `--no-update-check` or env `PERRA_NO_UPDATE_CHECK=1`.
- **Active CLI self-update:**
  ```bash
  perra update --check   # Check GitHub Releases without installing
  perra update --yes     # Download verified installer/update and apply silently
  ```
- **Site database auto-update:** By default checks upstream `soxoj/maigret` `db_meta.json` once every 24h and caches to `~/.perra/data.json` (SHA-256 verified).
  - Force immediate DB refresh: `perra <username> --force-update`
  - Skip DB update check: `perra <username> --no-autoupdate`
  - Custom local/HTTP DB: `perra <username> --db /path/to/data.json`

---

## 4. Interpreting Output & Avoiding Pitfalls

1. **Result statuses:**
   - `CLAIMED` (`[+]`, or `[++]` if keyword-matched): Account detected.
   - `AVAILABLE` (`[-]`): Username not found on that site.
   - `UNKNOWN` (`[?]` with error): Network/WAF/Captcha/Rate-limit/DNS failure — **never treat `UNKNOWN` as "account does not exist"**.
   - `ILLEGAL`: Unsupported username characters/regex, disabled site, or missing Tor/I2P gateway.
2. **Similar-username matches (`is_similar`):** Shown as `[?]` in blue on console and excluded from primary Markdown/HTML/Graph identity counts — verify manually before citing.
3. **High error rate (>3% WAF/Captcha or >=10% DNS):**
   - `Connecting failure (DNS)` -> add `--dns-resolver threaded`.
   - `Rate limited` -> reduce concurrency (`-n 10`) and add `--retries 2`.
   - `Access denied` / `Bot protection` -> residential proxy or `--cloudflare-bypass`.

---

## 5. Configuration & State Paths

Settings load in increasing order of precedence (later files override earlier keys):
1. Bundled `perra/resources/settings.json`
2. `/etc/perra/settings.json`
3. `~/.perra/settings.json`
4. `./settings.json` (current working directory)

Runtime user cache directory: `~/.perra/` (`data.json`, `autoupdate_state.json`, `cli_update_state.json`, `activation.json`).
