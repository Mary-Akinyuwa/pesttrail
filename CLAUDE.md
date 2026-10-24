# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Is

PestTrail is a US invasive pest intelligence platform built in Python/Streamlit. It provides pathway analysis, detection lag analytics, and eradication tracking for ~30–50 validated pest/pathogen records spanning 1995–present. The platform is deployed on Streamlit Cloud at `pesttrail.streamlit.app`. All economic figures must be cited to primary sources (USDA, peer-reviewed journals) — never use figures that cannot be traced to a primary source.

## Running Locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

Requires Python 3.9+. Secrets can be set in `.env` (local) or Streamlit Secrets (cloud). The app uses a `_secret()` helper that checks `st.secrets` first, then `os.getenv`.

## Agents

All four agents require `ANTHROPIC_API_KEY` in `.env` or environment:

```bash
# Data update agent — scheduled on GitHub Actions (data-agent.yml), not local cron
python3 data_update_agent.py                # quarterly (1st): new species + new state records (past 100 days)
python3 data_update_agent.py --validate     # re-verify the 16 stalest records (manual)
python3 data_update_agent.py --validate --all  # quarterly (2nd): every record not verified in 21 days
python3 data_update_agent.py --policy       # quarterly (3rd): check policy_intelligence.json figures
python3 data_update_agent.py --backfill     # one-time: historical sweep 1995–2026

# Economic research — two-pass source verification before writing to CSV
python3 economic_research_agent.py          # research pests missing economic figures
python3 economic_research_agent.py --all    # re-research all pests
python3 economic_research_agent.py --pest "Emerald Ash Borer"
python3 economic_research_agent.py --doc-only  # regenerate Word doc, no API calls

# Sanity check — verifies headline KPI claims in 4 tiers
python3 pesttrail_sanity_check_agent.py
python3 pesttrail_sanity_check_agent.py --tier 1  # Policy Gap KPIs only (fastest)
python3 pesttrail_sanity_check_agent.py --doc-only  # from cache, no API calls

# One-time data population (already run; use to re-apply or add records)
python3 apply_economic_data.py
```

Agent output documents go to `~/Desktop/`. The sanity check agent caches results in `analytics/sanity_check_cache.json` so it survives crashes during long runs.

## Architecture

### app.py (main dashboard, ~1500 lines)

Single-file Streamlit app structured in this order:

1. **Analytics setup** — dual tracking: client-side GA4 (JavaScript injected via `components.html`) + server-side GA4 Measurement Protocol (`_ga4_pageview()`). Also uses `streamlit_analytics2` for simple page-level stats and SQLite (`analytics/visits.db`) for session logging via `log_visit()`.

2. **Custom CSS block** — large inline `<style>` block with Oswald/Roboto fonts and a dark navy (`#07334E`) theme. Mobile layout is handled via CSS media queries and `_detect_mobile()`. The sidebar is locked to 260px on desktop, full-width overlay on mobile.

3. **Helper functions** — `load_data()` (cached, reads CSV), `load_policy()` (reads JSON), `init_db()` (creates SQLite schema), `_secret()` (checks `st.secrets` then `os.getenv`), `make_hero()` (generates SVG hero graphic).

4. **Sidebar** — search input + four `st.sidebar.selectbox` filters (pest type, origin region, mode of entry, impact sector). Filtering happens inline before the tab views.

5. **Tab navigation** — `st.tabs()` with analytical views: Pathway Analysis, Detection Lag, Temporal Trends, Pest Search/Detail, Policy Gap, Eradication Scorecard (in progress), Threat Horizon (in progress).

### pages/admin.py

Streamlit multi-page admin. Password-gated via `ADMIN_PASSWORD` secret. Shows visitor analytics from both SQLite (`visits.db`) and Supabase. Uses `SUPABASE_SERVICE_KEY` (not the anon key) to bypass RLS on the visits table — the anon key will fail for SELECT after RLS is enabled.

### Data files

- `data/invasive_pests_1995_2025.csv` — 21-field schema (see `docs/data_model.md`); `detection_lag_years` is computed in the dashboard as `year_first_detected_us - estimated_year_arrival`
- `data/policy_intelligence.json` — policy gap KPIs and sector vulnerability figures displayed in the Policy Gap tab; checked by `data_update_agent.py --policy`
- `data/agent_status.json` — last attempt/success, summary and estimated cost per agent mode; the sidebar's "last checked" date reads it
- `data/verification_log.csv` — public audit trail: one row per check (confirmed, rejected, unverifiable, flagged for human review) with the evidence URL

Verification dates shown in the app (sidebar, footer, chart notes) are computed from `data_verified_date` — never hardcode a month.

### Required environment variables

| Variable | Used by |
|---|---|
| `ANTHROPIC_API_KEY` | All four agents |
| `GA4_API_SECRET` | Server-side GA4 in `app.py` |
| `SUPABASE_URL` | `app.py`, `pages/admin.py` |
| `SUPABASE_ANON_KEY` | `app.py`, `pages/admin.py` |
| `SUPABASE_SERVICE_KEY` | `pages/admin.py` (admin SELECT, bypasses RLS) |
| `ADMIN_PASSWORD` | `pages/admin.py` |

### CI

`.github/workflows/keepalive.yml` keeps the Streamlit Cloud app from sleeping. It does not run tests.

It visits the app every 4 hours in headless Chromium (Playwright), each run offset by a random 0–45 minutes so the visit time varies daily. If the sleep screen is up it clicks "Yes, get this app back up!", then waits for a cold boot and holds the session open 45s. The job fails and uploads a screenshot artifact if the app never renders.

Two non-obvious constraints are baked in — do not "simplify" past them:

- **Never replace this with `curl`.** A bare GET to `pesttrail.streamlit.app` returns `303` to `share.streamlit.io/-/auth/app`, and Streamlit measures activity by the websocket a rendered page opens. An HTTP fetch never registers as a visit and cannot click the wake button. The original curl version reported green for months while doing nothing.
- **Readiness must be checked inside the app iframe.** Community Cloud serves the real app in a nested iframe at `<app>.streamlit.app/~/+/`; the top-level document is a wrapper shell whose `body.innerText` is always empty. Sleep detection reads the top frame, readiness reads the app frame via the `stAppViewContainer` test id.

The separate `keep-schedule-alive` job pushes an empty commit when the repo has been quiet 45+ days. GitHub disables scheduled workflows after 60 days of repository inactivity, which silently killed this workflow once already (last push 2026-05-06, last run 2026-07-05).

`.github/workflows/data-agent.yml` runs `data_update_agent.py` quarterly — Jan/Apr/Jul/Oct: scan on the 1st, full re-verification on the 2nd, policy check on the 3rd — and commits the data files; the push redeploys Streamlit Cloud. It needs the repo secret `ANTHROPIC_API_KEY`. Quarterly was the owner's choice for cost (~$25–30 a quarter: scan ~$2, full re-verification ~$20–25, policy ~$3). The scan's 100-day look-back overlaps consecutive quarters so no detection falls between runs. The agent used to run from local cron, which never reached the live app and stopped when the laptop changed (records sat at April 2026 until 2026-10-24).

What the agent checks: new US species and new state records; eradication outcomes, quarantine, biosurveillance (states, spread), entry pathway/origin (feeds the Origin–Commodity Risk Matrix) and economics per record (watch-list records — Not Yet Arrived / Eradication Ongoing / Limited Detection — go first); policy gap figures, sector damage/risk and threat risk/pathway. All quarterly. Source tiers are in `CREDIBLE_SOURCES`: only USDA APHIS / state regulatory officials can confirm a US detection or status; EDDMapS, CABI, EPPO Reporting Service and NAPPO Emerging Pest Alerts are leads only; Emergency Action Notifications are port interceptions, never detections.

Agent guarantees — do not weaken them:
- A record is re-dated only when a call that actually ran web searches confirmed it AND the cited source URL is among the pages those searches returned. API errors, refusals, verifier errors and unusable batches fail the run (exit 1) and change nothing; records the model skipped are left unverified and retried.
- Every change passes a second, independent `verify_change` call, whose evidence URL must come from its OWN search results, before it is written.
- The agent may edit only `MUTABLE_FIELDS` (plus `economic_impact_source_url` / `economic_verified_date` alongside a verified economic change). A proposed change to any other field, a status the dashboard can't express, or a value in the wrong shape (`field_format_problem`) goes to human review; the record keeps its old date. `data_sources` is appended to, never replaced.
- `eradication_status` must start with an `ERADICATION_STATUSES` value and be grouped the same way by app.py's `erad_group` (`valid_eradication_status`).
- Risk levels (threat `risk`, sector `risk_level`) are PestTrail's own judgment: the agent verifies the evidence but never writes them — they go to the owner as review items.
- Policy labels and ratios (`loss_ratio`, `plum_pox_roi`, labels) are recomputed in code from the stated figures; the model never writes a ratio.
- A change is reported as published only after it is saved; the workflow opens a GitHub issue (→ email) only after a successful push, and only when something was published or needs a decision.

## Data Integrity Rules

Every figure in the database must trace to a primary source (USDA official document, federal register entry, or peer-reviewed publication). The `economic_research_agent.py` enforces two-pass verification — a figure is only written to the CSV when an independent second search confirms it or finds a consistent second source. Do not add or modify economic figures manually without noting the source in `data_sources`.
