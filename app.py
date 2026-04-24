import streamlit as st
import streamlit.components.v1 as components
import streamlit_analytics2 as streamlit_analytics
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sqlite3
import uuid
import hashlib
import requests as _requests
from datetime import datetime, timezone
from pathlib import Path

st.set_page_config(
    page_title="PestTrail — US Invasive Pest Intelligence",
    page_icon="🌿",
    layout="wide"
)

# ── Client-side GA4 (runs in visitor's browser — real IP → correct geo on map) ──
components.html("""
<script async src="https://www.googletagmanager.com/gtag/js?id=G-9MKGHB8W6R"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'G-9MKGHB8W6R', { send_page_view: true });
</script>
""", height=0)

# ── Server-side GA4 Measurement Protocol ─────────────────────────────────────
def _ga4_pageview():
    try:
        api_secret = _secret("GA4_API_SECRET")
        if not api_secret:
            return
        if "ga4_sent" not in st.session_state:
            st.session_state["ga4_sent"] = True
            client_id = st.session_state.get("ga4_client_id", str(uuid.uuid4()))
            st.session_state["ga4_client_id"] = client_id
            session_id = str(abs(hash(client_id)) % 1_000_000_000)
            # Capture real visitor IP for GA4 geo-resolution
            # Private/internal IPs (192.168.x, 10.x, 172.16-31.x, 127.x) are skipped —
            # they can't be geo-resolved and come from Streamlit/Cloudflare internal infra.
            def _is_private(ip):
                try:
                    parts = [int(x) for x in ip.split(".")]
                    if len(parts) != 4: return True
                    return (parts[0] == 10 or parts[0] == 127 or
                            (parts[0] == 172 and 16 <= parts[1] <= 31) or
                            (parts[0] == 192 and parts[1] == 168))
                except Exception:
                    return True

            client_ip = ""
            try:
                hdrs = st.context.headers
                # Check all IPs in each header, skip private ones
                for _h in ["CF-Connecting-IP", "cf-connecting-ip",
                           "X-Forwarded-For", "x-forwarded-for",
                           "True-Client-IP", "true-client-ip",
                           "X-Real-Ip", "x-real-ip"]:
                    _v = hdrs.get(_h, "")
                    if not _v:
                        continue
                    for _candidate in _v.split(","):
                        _candidate = _candidate.strip()
                        if _candidate and not _is_private(_candidate):
                            client_ip = _candidate
                            break
                    if client_ip:
                        break
                st.session_state["_dbg_ip_header"] = client_ip or "(private/internal IP — geo not available)"
            except Exception:
                pass
            payload = {
                "client_id": client_id,
                "events": [{"name": "page_view", "params": {
                    "page_title": "PestTrail",
                    "page_location": "https://pesttrail.streamlit.app",
                    "session_id": session_id,
                    "engagement_time_msec": 10001,  # GA4 needs ≥10 000ms to count as engaged session
                    "session_engaged": "1",
                }}]
            }
            if client_ip:
                payload["user_ip_address"] = client_ip
            _requests.post(
                f"https://www.google-analytics.com/mp/collect"
                f"?measurement_id=G-9MKGHB8W6R&api_secret={api_secret}",
                json=payload,
                timeout=2
            )
    except Exception:
        pass

_ga4_pageview()

def _detect_mobile() -> bool:
    try:
        ua = st.context.headers.get("User-Agent", "")
        return any(x in ua for x in ["Mobile","Android","iPhone","iPad","webOS","BlackBerry","IEMobile"])
    except Exception:
        return False

is_mobile = _detect_mobile()

streamlit_analytics.start_tracking()

# Mobile viewport
st.markdown('<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0">', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# CUSTOM CSS  — Oswald headings · Roboto body · STELLA/FAO/Corteva aesthetic
# ══════════════════════════════════════════════════════════════════════════════
CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Oswald:wght@400;500;600;700&family=Roboto:wght@300;400;500;700&display=swap');

/* ── Base typography ───────────────────────────────────────────── */
html, body, [class*="css"] {
    font-family: 'Roboto', sans-serif !important;
    font-size: 15px;
    color: #1a2e22;
}
h1, h2, h3, h4, h5 {
    font-family: 'Oswald', sans-serif !important;
    letter-spacing: 0.02em;
    color: #07334E !important;
}

/* ── Full viewport background — unified dark navy ──────────────── */
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
.stApp {
    background: #07334E !important;
}

/* ── Streamlit main container ──────────────────────────────────── */
.main .block-container {
    padding: 0 !important;
    max-width: 100% !important;
}

/* ── Sidebar — desktop only fixed width ────────────────────────── */
@media (min-width: 769px) {
    section[data-testid="stSidebar"] {
        width: 260px !important;
        min-width: 260px !important;
        max-width: 260px !important;
    }
    [data-testid="stSidebarResizeHandle"],
    [class*="ResizeHandle"],
    [class*="resizeHandle"],
    [class*="resize-handle"] {
        display: none !important;
        pointer-events: none !important;
        visibility: hidden !important;
    }
    [data-testid="stSidebarCollapsedControl"] { display: none !important; }
    [data-testid="stSidebarCollapseButton"] { display: none !important; }
}
section[data-testid="stSidebar"] {
    background: #07334E !important;
    border-right: none;
}
[data-testid="stSidebarNav"] { display: none !important; }
[data-testid="stToolbar"] { display: none !important; }
[data-testid="stSidebarCollapsedControl"] { display: none !important; }
[data-testid="stSidebarCollapseButton"] { display: none !important; }
header[data-testid="stHeader"] { display: none !important; }
button[title="streamlitApp"],
[aria-label="streamlitApp"],
[title="streamlitApp"] { display: none !important; }


/* ── Mobile ────────────────────────────────────────────────────── */
@media (max-width: 768px) {
    section[data-testid="stSidebar"] {
        width: 100vw !important;
        min-width: 0 !important;
        max-width: 100vw !important;
        position: fixed !important;
        z-index: 999 !important;
        transform: translateX(-100%);
        transition: transform 0.3s ease;
    }
    section[data-testid="stSidebar"][aria-expanded="true"] {
        transform: translateX(0);
    }
    /* Show sidebar open button on mobile so users can access filters */
    [data-testid="stSidebarCollapsedControl"] {
        display: flex !important;
        position: fixed !important;
        top: 0.75rem !important;
        left: 0.75rem !important;
        z-index: 1000 !important;
        background: #07334E !important;
        border-radius: 6px !important;
    }
    .main .block-container {
        padding: 0 0.75rem 0.75rem 0.75rem !important;
        max-width: 100vw !important;
        width: 100vw !important;
        overflow-x: hidden !important;
    }
    [data-testid="stAppViewContainer"],
    [data-testid="stMain"] {
        width: 100vw !important;
        overflow-x: hidden !important;
    }
    /* Stack all st.columns() layouts */
    [data-testid="stHorizontalBlock"] {
        flex-wrap: wrap !important;
        gap: 0 !important;
    }
    [data-testid="column"] {
        width: 100% !important;
        min-width: 100% !important;
        flex: 1 1 100% !important;
        max-width: 100% !important;
    }
    /* KPI grid: 2 across on mobile */
    .kpi-row {
        grid-template-columns: 1fr 1fr !important;
        gap: 10px !important;
    }
    .kpi-value { font-size: 1.8rem !important; }
    /* Pest detail: 2-col grid on mobile */
    .pdc-grid {
        grid-template-columns: 1fr 1fr !important;
    }
    div[data-testid="stTabs"] button[role="tab"] {
        font-size: 0.72rem !important;
        padding: 4px 5px !important;
    }
    .pt-section-title { font-size: 1.15rem !important; }
    .pt-section-sub { font-size: 0.78rem !important; }
    .pt-section-header { padding: 14px 16px 12px 16px !important; gap: 10px !important; }
    /* Plotly charts — fill width, hide toolbar, allow vertical scroll */
    .stPlotlyChart { overflow-x: hidden !important; width: 100% !important; }
    .js-plotly-plot .modebar-container { display: none !important; }
    /* Dataframes — scrollable on mobile */
    .stDataFrame { overflow-x: auto !important; }
}
section[data-testid="stSidebar"] > div {
    padding-top: 1.5rem;
}
section[data-testid="stSidebar"] * {
    color: #d0e8f2 !important;
    font-family: 'Roboto', sans-serif !important;
}
section[data-testid="stSidebar"] h2 {
    font-family: 'Oswald', sans-serif !important;
    font-size: 1.5rem !important;
    font-weight: 700 !important;
    color: #ffffff !important;
    letter-spacing: 0.06em !important;
}
section[data-testid="stSidebar"] .stSelectbox label,
section[data-testid="stSidebar"] .stTextInput label {
    color: #86B233 !important;
    font-weight: 700 !important;
    font-size: 0.72rem !important;
    text-transform: uppercase !important;
    letter-spacing: 0.09em !important;
}
section[data-testid="stSidebar"] input,
section[data-testid="stSidebar"] .stSelectbox > div > div {
    background: rgba(255,255,255,0.07) !important;
    border: 1px solid rgba(134,178,51,0.35) !important;
    border-radius: 4px !important;
    color: #ffffff !important;
}
section[data-testid="stSidebar"] .stButton button {
    background: #86B233 !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 4px !important;
    font-family: 'Oswald', sans-serif !important;
    font-weight: 600 !important;
    letter-spacing: 0.05em !important;
    width: 100% !important;
}
section[data-testid="stSidebar"] .stButton button:hover {
    background: #6e9428 !important;
}
section[data-testid="stSidebar"] hr {
    border-color: rgba(134,178,51,0.25) !important;
}
section[data-testid="stSidebar"] .stExpander {
    border: 1px solid rgba(134,178,51,0.25) !important;
    border-radius: 4px !important;
    background: rgba(255,255,255,0.04) !important;
}

/* ── KPI Cards — STELLA style ──────────────────────────────────── */
.kpi-row {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 14px;
    margin: 20px 0 28px 0;
}
.kpi-card {
    background: #ffffff;
    border-radius: 6px;
    padding: 16px 20px;
    box-shadow: 0 2px 16px rgba(7,51,78,0.08), 0 1px 4px rgba(7,51,78,0.04);
    border-top: 4px solid var(--accent);
    position: relative;
    transition: transform 0.15s, box-shadow 0.15s;
}
.kpi-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 6px 24px rgba(7,51,78,0.13);
}
.kpi-card.green  { --accent: #86B233; }
.kpi-card.navy   { --accent: #07334E; }
.kpi-card.teal   { --accent: #116AAB; }
.kpi-card.gold   { --accent: #EEB638; }
.kpi-icon-circle {
    width: 52px; height: 52px;
    border-radius: 50%;
    background: var(--accent);
    opacity: 0.12;
    position: absolute;
    top: 20px; right: 20px;
    display: flex; align-items: center; justify-content: center;
}
.kpi-icon-overlay {
    position: absolute;
    top: 14px; right: 14px;
    font-size: 1.7rem;
    opacity: 0.5;
}
.kpi-value {
    font-family: 'Oswald', sans-serif;
    font-size: 2.2rem;
    font-weight: 700;
    color: #07334E;
    line-height: 1;
    margin-bottom: 4px;
}
.kpi-label {
    font-size: 0.875rem;
    font-weight: 700;
    color: #6b7280;
    text-transform: uppercase;
    letter-spacing: 0.09em;
}
.kpi-sub {
    font-size: 1.0rem;
    color: var(--accent);
    font-weight: 500;
    margin-top: 4px;
}

/* ── Section headers ───────────────────────────────────────────── */
.pt-section-header {
    display: flex;
    align-items: flex-start;
    gap: 16px;
    margin: 36px 0 0 0;
    padding: 20px 24px 18px 24px;
    background: rgba(255,255,255,0.06);
    border-radius: 10px 10px 0 0;
    border-left: 4px solid #86B233;
    border-bottom: 2px solid rgba(134,178,51,0.35);
    backdrop-filter: blur(4px);
}
.pt-section-header .section-icon {
    width: 40px; height: 40px;
    background: #86B233;
    border-radius: 8px;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.1rem;
    flex-shrink: 0;
    box-shadow: 0 2px 8px rgba(134,178,51,0.35);
}
.pt-section-title {
    font-family: 'Oswald', sans-serif;
    font-size: 1.75rem;
    font-weight: 600;
    color: #86B233;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    margin: 0;
    text-shadow: 0 1px 4px rgba(0,0,0,0.3);
}
.pt-section-sub {
    font-size: 1.0rem;
    color: #c4dce8;
    margin: 6px 0 0 0;
    font-weight: 400;
    line-height: 1.65;
}

/* ── Color-blocked panel wrappers ──────────────────────────────── */
.panel-white  { background: #ffffff; }
.panel-navy   { background: #07334E; padding: 32px; border-radius: 10px; }
.panel-light  { background: #f4f8fb; padding: 32px 36px; border-radius: 10px; margin: 8px 0; }
.panel-green  { background: #f2f8ec; padding: 32px 36px; border-radius: 10px; margin: 8px 0; }

/* ── Pest detail card ──────────────────────────────────────────── */
.pest-detail-card {
    background: #ffffff;
    border-left: 6px solid #86B233;
    border-radius: 0 10px 10px 0;
    padding: 24px 32px;
    margin: 16px 0;
    box-shadow: 0 3px 20px rgba(7,51,78,0.09);
}
.pdc-name {
    font-family: 'Oswald', sans-serif;
    font-size: 2.0rem;
    font-weight: 700;
    color: #07334E;
    margin-bottom: 2px;
}
.pdc-sci {
    font-style: italic;
    color: #116AAB;
    font-size: 1.0625rem;
    margin-bottom: 18px;
    font-weight: 400;
}
.pdc-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 12px;
    margin-bottom: 14px;
}
.pdc-field {
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 6px;
    padding: 10px 14px;
}
.pdc-field-label {
    font-size: 0.875rem;
    font-weight: 700;
    color: #116AAB;
    text-transform: uppercase;
    letter-spacing: 0.09em;
    margin-bottom: 3px;
}
.pdc-field-value {
    font-size: 1.0rem;
    color: #1e293b;
    font-weight: 400;
    line-height: 1.6;
}
.pdc-inoculum {
    background: #f2f8ec;
    border: 1px solid #c3e88d;
    border-radius: 6px;
    padding: 14px 18px;
    font-size: 1.0rem;
    color: #2d5a10;
    margin-top: 4px;
    line-height: 1.6;
}
.pdc-footer {
    font-size: 0.875rem;
    color: #6b7280;
    margin-top: 12px;
    padding-top: 10px;
    border-top: 1px solid #f1f5f9;
    line-height: 1.65;
}

/* ── Status badge ──────────────────────────────────────────────── */
.status-badge {
    display: inline-block;
    padding: 5px 13px;
    border-radius: 3px;
    font-size: 0.875rem;
    font-weight: 700;
    font-family: 'Oswald', sans-serif;
    letter-spacing: 0.05em;
    text-transform: uppercase;
}
.badge-red    { background: #fef2f2; color: #991b1b; border: 1px solid #fecaca; }
.badge-green  { background: #f0fdf4; color: #14532d; border: 1px solid #bbf7d0; }
.badge-yellow { background: #fffbeb; color: #713f12; border: 1px solid #fde68a; }
.badge-blue   { background: #eff6ff; color: #1e3a5f; border: 1px solid #bfdbfe; }

/* ── Plotly chart container ────────────────────────────────────── */
.stPlotlyChart {
    border-radius: 8px;
    overflow: hidden;
    box-shadow: 0 1px 8px rgba(7,51,78,0.06);
}

/* ── Dataframe ─────────────────────────────────────────────────── */
.stDataFrame {
    border-radius: 8px;
    overflow: hidden;
    box-shadow: 0 1px 8px rgba(7,51,78,0.06);
}

/* ── Footer ────────────────────────────────────────────────────── */
.site-footer {
    background: #07334E;
    border-radius: 10px;
    padding: 28px 36px;
    margin-top: 40px;
    color: #a8c8dc;
    font-size: 0.82rem;
    line-height: 2;
}
.site-footer strong { color: #86B233; font-weight: 600; }
.site-footer a { color: #86B233; text-decoration: none; }
.site-footer a:hover { text-decoration: underline; }
.footer-brand {
    font-family: 'Oswald', sans-serif;
    font-size: 1.2rem;
    font-weight: 700;
    color: #ffffff;
    letter-spacing: 0.08em;
    margin-bottom: 6px;
}

/* ── Metric area spacing ───────────────────────────────────────── */
[data-testid="metric-container"] { display: none; }

/* ── Warning/info box ──────────────────────────────────────────── */
.stAlert {
    border-radius: 6px !important;
}

/* ── Hide st.iframe component label (main content + sidebar) ───── */
div[data-testid="stIFrame"] > div:first-child,
div[data-testid="stIFrame"] label,
div[data-testid="stIFrame"] > div > div > div:first-child,
section[data-testid="stSidebar"] div[data-testid="stIFrame"] > div:first-child,
section[data-testid="stSidebar"] div[data-testid="stIFrame"] label,
section[data-testid="stSidebar"] div[data-testid="stIFrame"] > div > div > div:first-child {
    display: none !important;
}

/* ── Navigation tab bar — Corteva-inspired, clearly distinct from KPI cards ── */
div[data-testid="stTabs"] {
    margin-top: 32px !important;
}
div[data-testid="stTabs"] > div:first-child {
    background: linear-gradient(180deg,
        #1a5878 0%,
        #0f4060 35%,
        #07334E 100%) !important;
    border-radius: 10px 10px 0 0 !important;
    border-bottom: 4px solid #86B233 !important;
    border-top: 1px solid rgba(255,255,255,0.18) !important;
    box-shadow:
        inset 0 1px 0 rgba(255,255,255,0.22),
        inset 0 -1px 0 rgba(0,0,0,0.18),
        0 4px 16px rgba(7,51,78,0.35) !important;
    padding: 0 16px !important;
    gap: 0 !important;
    flex-wrap: nowrap !important;
    overflow-x: auto !important;
    scrollbar-width: none !important;
    justify-content: flex-start !important;
    align-items: stretch !important;
    position: relative !important;
}
div[data-testid="stTabs"] > div:first-child::-webkit-scrollbar {
    display: none !important;
}
div[data-testid="stTabs"] button[role="tab"] {
    background: transparent !important;
    border: none !important;
    border-bottom: 4px solid transparent !important;
    margin-bottom: -4px !important;
    border-radius: 0 !important;
    padding: 16px 24px !important;
    font-family: 'Oswald', sans-serif !important;
    font-size: 1.05rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.08em !important;
    color: #88b9d0 !important;
    text-transform: uppercase !important;
    cursor: pointer !important;
    transition: color 0.2s ease, border-bottom-color 0.2s ease !important;
    white-space: nowrap !important;
    flex-shrink: 0 !important;
    position: relative !important;
}
div[data-testid="stTabs"] button[role="tab"]:hover {
    color: #ffffff !important;
    background: rgba(255,255,255,0.08) !important;
    border-bottom-color: rgba(134,178,51,0.55) !important;
    box-shadow: inset 0 1px 0 rgba(255,255,255,0.12) !important;
}
div[data-testid="stTabs"] button[role="tab"][aria-selected="true"] {
    color: #ffffff !important;
    background: rgba(255,255,255,0.06) !important;
    border-bottom: 4px solid #86B233 !important;
    box-shadow: inset 0 1px 0 rgba(255,255,255,0.18) !important;
    margin-bottom: -4px !important;
}
div[data-testid="stTabs"] button[role="tab"] p,
div[data-testid="stTabs"] button[role="tab"] * {
    font-family: 'Oswald', sans-serif !important;
    font-size: 1.05rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.08em !important;
    margin: 0 !important;
    color: inherit !important;
}
div[data-testid="stTabContent"] {
    background: #ffffff !important;
    border-radius: 0 0 10px 10px !important;
    border: 1px solid #cbd5e1 !important;
    border-top: none !important;
    font-size: 1rem !important;
    line-height: 1.65 !important;
    padding: 32px 32px 40px 32px !important;
    box-shadow: 0 6px 24px rgba(7,51,78,0.08) !important;
}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# HTML HERO BANNER  — CSS-based, fully responsive, no iframe, no cropping
# ══════════════════════════════════════════════════════════════════════════════
def make_hero(n_records: int) -> str:
    return f"""
<style>
.pt-hero-side {{ display:block; }}
.pt-hero-mobile-viz {{ display:none; }}
@media (max-width:860px) {{ .pt-hero-side {{ display:none !important; }} }}
@media (max-width:768px) {{
  .pt-hero-outer {{
    padding: 24px 18px 22px 18px !important;
    min-height: auto !important;
  }}
  .pt-hero-content {{ max-width: 100% !important; }}
  .pt-hero-pest  {{ font-size: 2.8rem !important; }}
  .pt-hero-trail {{ font-size: 2rem   !important; }}
  .pt-hero-underline {{ width: 160px !important; margin: 8px 0 12px 0 !important; }}
  .pt-hero-sub  {{ font-size: 0.9rem !important; margin-bottom: 5px !important; }}
  .pt-hero-tag  {{ font-size: 0.76rem !important; margin-bottom: 16px !important; }}
  .pt-hero-chip {{ padding: 5px 12px !important; font-size: 0.74rem !important; }}
  .pt-hero-mobile-viz {{ display:block !important; margin-top:16px; width:100%; }}
}}
</style>
<div class="pt-hero-outer" style="
  width:100%;min-height:340px;
  padding:56px 52px 80px 52px;
  background:linear-gradient(135deg,#04243a 0%,#07334E 60%,#0d4a2e 100%);
  border-radius:0 0 14px 14px;box-sizing:border-box;
  position:relative;overflow:hidden;">

  <!-- Subtle grid lines -->
  <div class="pt-hero-side" style="position:absolute;inset:0;pointer-events:none;opacity:0.04;">
    <svg width="100%" height="100%" xmlns="http://www.w3.org/2000/svg">
      <line x1="0" y1="25%" x2="100%" y2="25%" stroke="#fff" stroke-width="0.5"/>
      <line x1="0" y1="50%" x2="100%" y2="50%" stroke="#fff" stroke-width="0.5"/>
      <line x1="0" y1="75%" x2="100%" y2="75%" stroke="#fff" stroke-width="0.5"/>
      <line x1="25%" y1="0" x2="25%" y2="100%" stroke="#fff" stroke-width="0.5"/>
      <line x1="50%" y1="0" x2="50%" y2="100%" stroke="#fff" stroke-width="0.5"/>
      <line x1="75%" y1="0" x2="75%" y2="100%" stroke="#fff" stroke-width="0.5"/>
    </svg>
  </div>

  <!-- Ambient glow spots -->
  <div style="position:absolute;bottom:30px;left:80px;width:240px;height:80px;
    background:radial-gradient(ellipse,#86B233 0%,transparent 70%);
    opacity:0.07;pointer-events:none;border-radius:50%;"></div>
  <div class="pt-hero-side" style="position:absolute;bottom:20px;right:200px;width:280px;height:90px;
    background:radial-gradient(ellipse,#116AAB 0%,transparent 70%);
    opacity:0.07;pointer-events:none;border-radius:50%;"></div>

  <!-- Crop stalk silhouettes (bottom) -->
  <div style="position:absolute;bottom:18px;left:0;right:0;pointer-events:none;">
    <svg width="100%" height="70" xmlns="http://www.w3.org/2000/svg" preserveAspectRatio="none">
      <!-- Left stalk group -->
      <g opacity="0.45" fill="#1b4332">
        <rect x="2%"  y="20" width="3" height="50"/><ellipse cx="2.2%"  cy="18" rx="5"  ry="14" fill="#2d6a4f"/>
        <rect x="3.5%" y="28" width="3" height="42"/><ellipse cx="3.7%"  cy="26" rx="4"  ry="11" fill="#2d6a4f"/>
        <rect x="5%"  y="22" width="3" height="48"/><ellipse cx="5.2%"  cy="20" rx="5"  ry="13" fill="#2d6a4f"/>
        <rect x="6.5%" y="30" width="3" height="40"/><ellipse cx="6.7%"  cy="28" rx="4"  ry="10" fill="#2d6a4f"/>
        <rect x="8%"  y="24" width="3" height="46"/><ellipse cx="8.2%"  cy="22" rx="5"  ry="12" fill="#2d6a4f"/>
        <rect x="9.5%" y="32" width="3" height="38"/><ellipse cx="9.7%"  cy="30" rx="4"  ry="10" fill="#2d6a4f"/>
        <rect x="11%" y="18" width="3" height="52"/><ellipse cx="11.2%" cy="16" rx="6"  ry="15" fill="#2d6a4f"/>
        <rect x="12.5%" y="26" width="3" height="44"/><ellipse cx="12.7%" cy="24" rx="5" ry="12" fill="#2d6a4f"/>
      </g>
      <!-- Ground strip -->
      <rect x="0" y="48" width="100%" height="22" fill="#0d2b1e" opacity="0.6"/>
      <rect x="0" y="55" width="100%" height="15" fill="#0a2018" opacity="0.8"/>
    </svg>
  </div>

  <!-- Leaf shapes (top right, above detection panel) -->
  <div class="pt-hero-side" style="position:absolute;top:-18px;right:60px;
    width:90px;height:36px;background:linear-gradient(135deg,#86B233,#4a7c10);
    border-radius:50%;transform:rotate(15deg);opacity:0.25;pointer-events:none;"></div>
  <div class="pt-hero-side" style="position:absolute;top:16px;right:80px;
    width:60px;height:24px;background:#86B233;border-radius:50%;
    transform:rotate(-20deg);opacity:0.15;pointer-events:none;"></div>

  <!-- Radar / biosurveillance scope — sits between trail and detection map -->
  <div class="pt-hero-side" style="position:absolute;right:260px;top:50%;
    transform:translateY(-58%);pointer-events:none;">
    <svg width="140" height="140" viewBox="-70 -70 140 140" xmlns="http://www.w3.org/2000/svg">
      <circle r="70" fill="#03192b" opacity="0.92" stroke="#86B233" stroke-width="2"/>
      <circle r="55" fill="none" stroke="#86B233" stroke-width="0.75" opacity="0.35"/>
      <circle r="40" fill="none" stroke="#86B233" stroke-width="0.75" opacity="0.25"/>
      <circle r="24" fill="none" stroke="#86B233" stroke-width="0.75" opacity="0.2"/>
      <line x1="-70" y1="0" x2="-26" y2="0" stroke="#86B233" stroke-width="0.8" opacity="0.4"/>
      <line x1="26" y1="0" x2="70" y2="0" stroke="#86B233" stroke-width="0.8" opacity="0.4"/>
      <line x1="0" y1="-70" x2="0" y2="-26" stroke="#86B233" stroke-width="0.8" opacity="0.4"/>
      <line x1="0" y1="26" x2="0" y2="70" stroke="#86B233" stroke-width="0.8" opacity="0.4"/>
      <line x1="-70" y1="-4" x2="-70" y2="4" stroke="#86B233" stroke-width="1.5" opacity="0.55"/>
      <line x1="70" y1="-4" x2="70" y2="4" stroke="#86B233" stroke-width="1.5" opacity="0.55"/>
      <line x1="-4" y1="-70" x2="4" y2="-70" stroke="#86B233" stroke-width="1.5" opacity="0.55"/>
      <line x1="-4" y1="70" x2="4" y2="70" stroke="#86B233" stroke-width="1.5" opacity="0.55"/>
      <line x1="-55" y1="-19" x2="55" y2="-19" stroke="#86B233" stroke-width="1" opacity="0.4" stroke-dasharray="5,4"/>
      <ellipse cx="0" cy="12" rx="13" ry="19" fill="none" stroke="#d0e8f2" stroke-width="1.5"/>
      <ellipse cx="0" cy="-10" rx="11" ry="9" fill="none" stroke="#d0e8f2" stroke-width="1.5"/>
      <circle cx="0" cy="-26" r="8" fill="none" stroke="#d0e8f2" stroke-width="1.5"/>
      <line x1="-10" y1="-3" x2="10" y2="-3" stroke="#d0e8f2" stroke-width="1" opacity="0.55"/>
      <line x1="0" y1="-3" x2="0" y2="29" stroke="#d0e8f2" stroke-width="1" opacity="0.55"/>
      <path d="M-4,-33 L-9,-43 L-15,-50 L-17,-58" stroke="#a8c8dc" stroke-width="1.2" fill="none" stroke-linejoin="round"/>
      <path d="M 4,-33 L  9,-43 L 15,-50 L 17,-58" stroke="#a8c8dc" stroke-width="1.2" fill="none" stroke-linejoin="round"/>
      <circle cx="-17" cy="-58" r="2.5" fill="#EEB638" opacity="0.9"/>
      <circle cx="17" cy="-58" r="2.5" fill="#EEB638" opacity="0.9"/>
      <path d="M-9,-8 L-22,-4 L-36,-12" stroke="#a8c8dc" stroke-width="1.2" fill="none"/>
      <path d="M 9,-8 L 22,-4 L 36,-12" stroke="#a8c8dc" stroke-width="1.2" fill="none"/>
      <path d="M-11,4 L-28,4 L-42,14" stroke="#a8c8dc" stroke-width="1.2" fill="none"/>
      <path d="M 11,4 L 28,4 L 42,14" stroke="#a8c8dc" stroke-width="1.2" fill="none"/>
      <path d="M-11,18 L-27,24 L-36,36" stroke="#a8c8dc" stroke-width="1.2" fill="none"/>
      <path d="M 11,18 L 27,24 L 36,36" stroke="#a8c8dc" stroke-width="1.2" fill="none"/>
      <circle cx="0" cy="12" r="6" fill="none" stroke="#EEB638" stroke-width="1.5" opacity="0.9"/>
      <circle cx="0" cy="12" r="2" fill="#EEB638" opacity="0.9"/>
      <line x1="48" y1="48" x2="68" y2="68" stroke="#a8c8dc" stroke-width="8" stroke-linecap="round" opacity="0.3"/>
      <line x1="48" y1="48" x2="68" y2="68" stroke="#d0e8f2" stroke-width="3" stroke-linecap="round" opacity="0.18"/>
    </svg>
  </div>

  <!-- Detection panel: label + dot grid + legend — far right -->
  <div class="pt-hero-side" style="position:absolute;right:28px;top:50%;
    transform:translateY(-55%);pointer-events:none;opacity:0.85;">
    <svg width="215" height="160" viewBox="0 0 215 160" xmlns="http://www.w3.org/2000/svg">
      <text x="0" y="13" font-family="Oswald,sans-serif" font-size="11" font-weight="600"
            fill="#86B233" letter-spacing="0.12em" opacity="0.9">DETECTION MAP</text>
      <!-- Row 1 -->
      <circle cx="8"   cy="33" r="5" fill="#86B233"/><circle cx="8"   cy="33" r="9" fill="none" stroke="#86B233" stroke-width="1" opacity="0.4"/>
      <circle cx="36"  cy="25" r="4" fill="#86B233" opacity="0.6"/>
      <circle cx="64"  cy="38" r="6" fill="#EEB638"/><circle cx="64"  cy="38" r="10" fill="none" stroke="#EEB638" stroke-width="1" opacity="0.4"/>
      <circle cx="92"  cy="28" r="4" fill="#86B233" opacity="0.7"/>
      <circle cx="120" cy="41" r="5" fill="#86B233"/>
      <circle cx="150" cy="25" r="6" fill="#116AAB" opacity="0.8"/>
      <circle cx="178" cy="37" r="4" fill="#86B233" opacity="0.6"/>
      <!-- Row 2 -->
      <circle cx="16"  cy="65" r="4" fill="#86B233" opacity="0.6"/>
      <circle cx="46"  cy="58" r="6" fill="#EEB638"/><circle cx="46" cy="58" r="10" fill="none" stroke="#EEB638" stroke-width="1" opacity="0.35"/>
      <circle cx="74"  cy="71" r="5" fill="#86B233"/>
      <circle cx="102" cy="61" r="4" fill="#86B233" opacity="0.5"/>
      <circle cx="130" cy="73" r="6" fill="#116AAB" opacity="0.75"/>
      <circle cx="158" cy="63" r="5" fill="#86B233" opacity="0.7"/>
      <circle cx="186" cy="75" r="4" fill="#EEB638" opacity="0.6"/>
      <!-- Row 3 -->
      <circle cx="22"  cy="97" r="5" fill="#86B233" opacity="0.7"/>
      <circle cx="52"  cy="90" r="4" fill="#86B233" opacity="0.5"/>
      <circle cx="80"  cy="103" r="6" fill="#EEB638"/>
      <circle cx="110" cy="93" r="5" fill="#86B233" opacity="0.6"/>
      <circle cx="140" cy="105" r="4" fill="#86B233"/>
      <circle cx="168" cy="95" r="6" fill="#116AAB" opacity="0.8"/>
      <circle cx="196" cy="107" r="4" fill="#86B233" opacity="0.6"/>
      <!-- Legend -->
      <circle cx="6"   cy="133" r="5" fill="#86B233"/>
      <text x="16" y="138" font-family="Roboto,sans-serif" font-size="11" fill="#a8c8dc">Established</text>
      <circle cx="105" cy="133" r="5" fill="#EEB638"/>
      <text x="115" y="138" font-family="Roboto,sans-serif" font-size="11" fill="#a8c8dc">Active Spread</text>
      <circle cx="6"   cy="153" r="5" fill="#116AAB"/>
      <text x="16" y="158" font-family="Roboto,sans-serif" font-size="11" fill="#a8c8dc">New Detection</text>
    </svg>
  </div>

  <!-- Invasion spread path — curves from content area toward the radar -->
  <div class="pt-hero-side" style="position:absolute;left:43%;top:54%;
    transform:translateY(-50%);pointer-events:none;opacity:0.45;">
    <svg width="200" height="70" viewBox="0 0 200 70" xmlns="http://www.w3.org/2000/svg">
      <path d="M 0 52 Q 70 18 130 36 Q 170 48 175 24"
            fill="none" stroke="#86B233" stroke-width="2" stroke-dasharray="8,6"/>
      <circle cx="72"  cy="24" r="6" fill="#86B233" opacity="0.3"/>
      <circle cx="72"  cy="24" r="11" fill="none" stroke="#86B233" stroke-width="1.5" opacity="0.2"/>
      <circle cx="138" cy="36" r="6" fill="#EEB638" opacity="0.5"/>
      <circle cx="138" cy="36" r="11" fill="none" stroke="#EEB638" stroke-width="1.5" opacity="0.3"/>
    </svg>
  </div>

  <!-- Main left content -->
  <div class="pt-hero-content" style="position:relative;z-index:1;max-width:600px;">
    <div style="font-family:'Oswald',sans-serif;font-weight:700;
      line-height:1;letter-spacing:0.04em;margin-bottom:0;">
      <span class="pt-hero-pest" style="font-size:4.8rem;color:#ffffff;">PEST</span><span class="pt-hero-trail" style="font-size:3.4rem;color:#86B233;">TRAIL</span>
    </div>
    <div class="pt-hero-underline" style="width:280px;height:4px;background:#86B233;border-radius:2px;margin:10px 0 16px 0;"></div>
    <div class="pt-hero-sub" style="font-family:'Roboto',sans-serif;font-size:1rem;font-weight:300;
      color:#a8c8dc;letter-spacing:0.02em;margin-bottom:6px;">
      US Invasive Pest &amp; Pathogen Intelligence Platform
    </div>
    <div class="pt-hero-tag" style="font-family:'Roboto',sans-serif;font-size:0.8rem;color:#6a9aaf;margin-bottom:26px;">
      Tracking pests &middot; pathogens &middot; inocula introduced since 1995
    </div>
    <div style="display:flex;gap:8px;flex-wrap:wrap;">
      <div class="pt-hero-chip" style="background:rgba(134,178,51,0.18);border:1px solid rgba(134,178,51,0.7);
        border-radius:4px;padding:7px 18px;font-family:'Oswald',sans-serif;font-size:0.82rem;
        font-weight:600;color:#86B233;letter-spacing:0.04em;">{n_records} SPECIES TRACKED</div>
      <div class="pt-hero-chip" style="background:rgba(17,106,171,0.18);border:1px solid rgba(17,106,171,0.7);
        border-radius:4px;padding:7px 18px;font-family:'Oswald',sans-serif;font-size:0.82rem;
        font-weight:600;color:#116AAB;letter-spacing:0.04em;">1995 — 2026</div>
      <div class="pt-hero-chip" style="background:rgba(238,182,56,0.15);border:1px solid rgba(238,182,56,0.7);
        border-radius:4px;padding:7px 18px;font-family:'Oswald',sans-serif;font-size:0.82rem;
        font-weight:600;color:#EEB638;letter-spacing:0.04em;">PEER-REVIEWED</div>
    </div>
  </div>
  <div class="pt-hero-mobile-viz">
    <svg width="100%" viewBox="0 0 360 100" xmlns="http://www.w3.org/2000/svg" preserveAspectRatio="xMinYMid meet">
      <path d="M 8 72 Q 48 40 88 56 Q 112 66 115 48" fill="none" stroke="#86B233" stroke-width="2" stroke-dasharray="6,4" opacity="0.6"/>
      <circle cx="52" cy="44" r="5" fill="#86B233" opacity="0.3"/><circle cx="52" cy="44" r="9" fill="none" stroke="#86B233" stroke-width="1.5" opacity="0.2"/>
      <circle cx="92" cy="56" r="5" fill="#EEB638" opacity="0.5"/><circle cx="92" cy="56" r="9" fill="none" stroke="#EEB638" stroke-width="1.5" opacity="0.3"/>
      <g transform="translate(155,50)">
        <circle r="42" fill="#03192b" opacity="0.92" stroke="#86B233" stroke-width="1.5"/>
        <circle r="33" fill="none" stroke="#86B233" stroke-width="0.6" opacity="0.35"/>
        <circle r="22" fill="none" stroke="#86B233" stroke-width="0.6" opacity="0.25"/>
        <line x1="-42" y1="0" x2="-16" y2="0" stroke="#86B233" stroke-width="0.6" opacity="0.4"/>
        <line x1="16" y1="0" x2="42" y2="0" stroke="#86B233" stroke-width="0.6" opacity="0.4"/>
        <line x1="0" y1="-42" x2="0" y2="-16" stroke="#86B233" stroke-width="0.6" opacity="0.4"/>
        <line x1="0" y1="16" x2="0" y2="42" stroke="#86B233" stroke-width="0.6" opacity="0.4"/>
        <ellipse cx="0" cy="7" rx="8" ry="12" fill="none" stroke="#d0e8f2" stroke-width="1"/>
        <ellipse cx="0" cy="-6" rx="7" ry="6" fill="none" stroke="#d0e8f2" stroke-width="1"/>
        <circle cx="0" cy="-16" r="5" fill="none" stroke="#d0e8f2" stroke-width="1"/>
        <path d="M-2,-20 L-5,-26 L-9,-31 L-11,-36" stroke="#a8c8dc" stroke-width="0.8" fill="none"/>
        <path d="M 2,-20 L  5,-26 L  9,-31 L 11,-36" stroke="#a8c8dc" stroke-width="0.8" fill="none"/>
        <path d="M-6,-5 L-14,-2 L-22,-8" stroke="#a8c8dc" stroke-width="0.8" fill="none"/>
        <path d="M 6,-5 L 14,-2 L 22,-8" stroke="#a8c8dc" stroke-width="0.8" fill="none"/>
        <path d="M-7,3 L-18,3 L-26,9" stroke="#a8c8dc" stroke-width="0.8" fill="none"/>
        <path d="M 7,3 L 18,3 L 26,9" stroke="#a8c8dc" stroke-width="0.8" fill="none"/>
        <circle cx="0" cy="7" r="4" fill="none" stroke="#EEB638" stroke-width="1.2" opacity="0.9"/>
        <circle cx="0" cy="7" r="1.5" fill="#EEB638" opacity="0.9"/>
      </g>
      <text x="210" y="10" font-family="Oswald,sans-serif" font-size="8" font-weight="600" fill="#86B233" letter-spacing="0.1em">DETECTION MAP</text>
      <circle cx="212" cy="24" r="4" fill="#86B233"/><circle cx="212" cy="24" r="7" fill="none" stroke="#86B233" stroke-width="0.8" opacity="0.4"/>
      <circle cx="228" cy="19" r="3" fill="#86B233" opacity="0.6"/>
      <circle cx="244" cy="27" r="5" fill="#EEB638"/><circle cx="244" cy="27" r="8" fill="none" stroke="#EEB638" stroke-width="0.8" opacity="0.4"/>
      <circle cx="260" cy="21" r="3" fill="#86B233" opacity="0.7"/>
      <circle cx="276" cy="28" r="4" fill="#86B233"/>
      <circle cx="292" cy="19" r="4" fill="#116AAB" opacity="0.8"/>
      <circle cx="308" cy="25" r="3" fill="#86B233" opacity="0.6"/>
      <circle cx="220" cy="44" r="3" fill="#86B233" opacity="0.6"/>
      <circle cx="236" cy="38" r="5" fill="#EEB638"/><circle cx="236" cy="38" r="8" fill="none" stroke="#EEB638" stroke-width="0.8" opacity="0.35"/>
      <circle cx="252" cy="47" r="4" fill="#86B233"/>
      <circle cx="268" cy="40" r="3" fill="#86B233" opacity="0.5"/>
      <circle cx="284" cy="49" r="4" fill="#116AAB" opacity="0.75"/>
      <circle cx="300" cy="41" r="4" fill="#86B233" opacity="0.7"/>
      <circle cx="316" cy="50" r="3" fill="#EEB638" opacity="0.6"/>
      <circle cx="212" cy="68" r="4" fill="#86B233"/>
      <text x="220" y="72" font-family="Roboto,sans-serif" font-size="9" fill="#a8c8dc">Established</text>
      <circle cx="275" cy="68" r="4" fill="#EEB638"/>
      <text x="283" y="72" font-family="Roboto,sans-serif" font-size="9" fill="#a8c8dc">Active Spread</text>
      <circle cx="212" cy="84" r="4" fill="#116AAB"/>
      <text x="220" y="88" font-family="Roboto,sans-serif" font-size="9" fill="#a8c8dc">New Detection</text>
    </svg>
  </div>
</div>
"""

# ══════════════════════════════════════════════════════════════════════════════
# PATHS & ANALYTICS
# ══════════════════════════════════════════════════════════════════════════════
DATA_PATH   = Path(__file__).parent / "data" / "invasive_pests_1995_2025.csv"
POLICY_PATH = Path(__file__).parent / "data" / "policy_intelligence.json"
DB_PATH     = Path(__file__).parent / "analytics" / "visits.db"

@st.cache_data(ttl=3600)
def load_policy():
    """Load live policy intelligence data. Falls back to safe defaults if file missing."""
    if POLICY_PATH.exists():
        import json as _json
        with open(POLICY_PATH, "r") as f:
            return _json.load(f)
    # Minimal safe defaults (agent will create full file on first run)
    return {
        "policy_gap": {
            "annual_damage_label": "~$21B", "annual_prevention_label": "$70.7M",
            "loss_ratio": "~297×", "roi_per_dollar": "~$17 (OTA 1993)",
            "plum_pox_cost_million": 65, "plum_pox_avoided_billion": 4.7,
            "plum_pox_roi": "~72×", "eradication_window_years": 5,
            "sources": ["Fantle-Lepczyk et al. 2022 Sci. Total Environ. 819:153048", "USDA APHIS FY2025 PPA §7721 Spending Plan"]
        },
        "sector_vulnerability": [],
        "threat_intel": {}
    }

def init_db():
    DB_PATH.parent.mkdir(exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS visits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT, session_id TEXT, search_term TEXT,
            filter_pest_type TEXT, filter_origin_region TEXT,
            filter_entry_mode TEXT, filter_impact_sector TEXT
        )
    """)
    conn.commit(); conn.close()

def _secret(key, default=""):
    try:
        return st.secrets[key]
    except Exception:
        return os.getenv(key, default)

_SB_URL = _secret("SUPABASE_URL")
_SB_KEY = _secret("SUPABASE_ANON_KEY")

def log_visit(session_id, search_term, pest_type, origin_region, entry_mode, impact_sector):
    row = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "session_id": session_id,
        "search_term": search_term or "",
        "filter_pest_type": pest_type if pest_type != "All" else "",
        "filter_origin_region": origin_region if origin_region != "All" else "",
        "filter_entry_mode": entry_mode if entry_mode != "All" else "",
        "filter_impact_sector": impact_sector if impact_sector != "All" else "",
    }
    # Write to Supabase (persistent across redeploys)
    if _SB_URL and _SB_KEY:
        try:
            _requests.post(
                f"{_SB_URL}/rest/v1/visits",
                headers={"apikey": _SB_KEY, "Authorization": f"Bearer {_SB_KEY}",
                         "Content-Type": "application/json", "Prefer": "return=minimal"},
                json=row, timeout=3
            )
        except Exception:
            pass
    # Always also write to local SQLite (for local dev / fallback)
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.execute("""
            INSERT INTO visits
            (timestamp,session_id,search_term,filter_pest_type,filter_origin_region,filter_entry_mode,filter_impact_sector)
            VALUES (?,?,?,?,?,?,?)
        """, tuple(row.values()))
        conn.commit(); conn.close()
    except Exception:
        pass

init_db()

if "session_id" not in st.session_state:
    st.session_state.session_id = hashlib.md5(str(uuid.uuid4()).encode()).hexdigest()

# ══════════════════════════════════════════════════════════════════════════════
# DATA
# ══════════════════════════════════════════════════════════════════════════════
@st.cache_data(ttl=300)
def load_data():
    df = pd.read_csv(DATA_PATH)
    df["year_first_detected_us"] = pd.to_numeric(
        df["year_first_detected_us"].astype(str).str.extract(r"(\d{4})")[0], errors="coerce")
    df["estimated_year_arrival"] = pd.to_numeric(df["estimated_year_arrival"], errors="coerce")
    df["detection_lag_years"] = (df["year_first_detected_us"] - df["estimated_year_arrival"]).clip(lower=0)
    df["economic_impact_clean"] = (
        df["economic_impact_usd"].str.extract(r"\$([0-9,.]+)")[0]
        .str.replace(",","").astype(float, errors="ignore"))
    return df

df = load_data()

# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════
st.sidebar.markdown("""
<div style="display:flex;align-items:center;gap:10px;margin-bottom:4px;">
  <svg width="36" height="36" viewBox="0 0 36 36" xmlns="http://www.w3.org/2000/svg">
    <circle cx="18" cy="18" r="18" fill="#07334E" stroke="#86B233" stroke-width="1.5"/>
    <circle r="12" cx="18" cy="18" fill="none" stroke="#86B233" stroke-width="0.8" opacity="0.4"/>
    <circle r="7" cx="18" cy="18" fill="none" stroke="#86B233" stroke-width="0.8" opacity="0.25"/>
    <line x1="18" y1="6" x2="18" y2="12" stroke="#86B233" stroke-width="1.2" opacity="0.5"/>
    <line x1="18" y1="24" x2="18" y2="30" stroke="#86B233" stroke-width="1.2" opacity="0.5"/>
    <line x1="6" y1="18" x2="12" y2="18" stroke="#86B233" stroke-width="1.2" opacity="0.5"/>
    <line x1="24" y1="18" x2="30" y2="18" stroke="#86B233" stroke-width="1.2" opacity="0.5"/>
    <circle cx="18" cy="18" r="3" fill="none" stroke="#86B233" stroke-width="1.5"/>
    <circle cx="18" cy="18" r="1" fill="#EEB638"/>
  </svg>
  <span style="font-family:'Oswald',sans-serif;font-size:1.4rem;font-weight:700;
               color:#ffffff;letter-spacing:0.08em;">PEST<span style="font-size:1.05rem;color:#86B233;">TRAIL</span></span>
</div>
<p style='font-size:0.75rem;color:#b8d8ec;margin-top:0;margin-bottom:0;'>US Biosurveillance · Pests &amp; Pathogens · 1995–2026</p>
""", unsafe_allow_html=True)

if st.sidebar.button("🔄 Reload Dataset"):
    st.cache_data.clear(); st.rerun()
st.sidebar.caption(f"Static dataset · last verified April 2026 · **{len(df)} records**")
st.sidebar.markdown("---")

st.sidebar.markdown(
    "<p style='font-size:1.125rem;font-weight:700;color:#86B233;text-transform:uppercase;"
    "letter-spacing:0.09em;margin-bottom:2px;'>Species / Pathogen Search</p>",
    unsafe_allow_html=True
)
search_term = st.sidebar.text_input(
    "Search by common name, scientific name, host, or state",
    placeholder="e.g. Agrilus planipennis, soybean, Florida…",
    key="search_input",
    label_visibility="collapsed"
)

st.sidebar.markdown("---")
st.sidebar.markdown(
    "<p style='font-size:1.125rem;font-weight:700;color:#86B233;text-transform:uppercase;"
    "letter-spacing:0.09em;margin-bottom:6px;'>Filter Database</p>",
    unsafe_allow_html=True
)

pest_types         = ["All"] + sorted(df["pest_type"].dropna().unique().tolist())
selected_type      = st.sidebar.selectbox("Pest Type", pest_types)

origin_regions     = ["All"] + sorted(df["origin_region"].dropna().unique().tolist())
selected_region    = st.sidebar.selectbox("Origin Region", origin_regions)

entry_modes        = ["All"] + sorted(df["mode_of_entry"].dropna().unique().tolist())
selected_mode      = st.sidebar.selectbox("Mode of Entry", entry_modes)

sectors            = ["All"] + sorted(df["impact_sector"].dropna().unique().tolist())
selected_sector    = st.sidebar.selectbox("Impact Sector", sectors)

record_types       = ["All"] + sorted(df["record_type"].dropna().unique().tolist())
selected_record_type = st.sidebar.selectbox("Record Type", record_types)

eradication_statuses = ["All"] + sorted(df["eradication_status"].dropna().unique().tolist())
selected_status    = st.sidebar.selectbox("Eradication Status", eradication_statuses)

log_visit(st.session_state.session_id, search_term,
          selected_type, selected_region, selected_mode, selected_sector)

# ══════════════════════════════════════════════════════════════════════════════
# FILTER LOGIC
# ══════════════════════════════════════════════════════════════════════════════
search_filtered = df.copy()
if search_term and search_term.strip():
    q = search_term.strip()
    # Search only pest names — prevents false positives from host/state/sector fields
    mask = (
        df["pest_common_name"].str.contains(q, case=False, na=False) |
        df["pest_scientific_name"].str.contains(q, case=False, na=False)
    )
    search_filtered = df[mask]

filtered = search_filtered.copy()
if selected_type   != "All": filtered = filtered[filtered["pest_type"] == selected_type]
if selected_region != "All": filtered = filtered[filtered["origin_region"].str.contains(selected_region, na=False)]
if selected_mode   != "All": filtered = filtered[filtered["mode_of_entry"] == selected_mode]
if selected_sector != "All": filtered = filtered[filtered["impact_sector"].str.contains(selected_sector, na=False)]
if selected_record_type != "All": filtered = filtered[filtered["record_type"] == selected_record_type]
if selected_status != "All": filtered = filtered[filtered["eradication_status"] == selected_status]

# ══════════════════════════════════════════════════════════════════════════════
# HERO
# ══════════════════════════════════════════════════════════════════════════════
st.markdown(make_hero(len(df)), unsafe_allow_html=True)
st.markdown('<div style="padding:0 2rem;margin-top:0;">', unsafe_allow_html=True)

# ── Mobile search bar — injected into main content so users don't need sidebar ─
if is_mobile:
    st.markdown(
        '<p style="font-family:\'Oswald\',sans-serif;font-size:0.85rem;font-weight:600;'
        'color:#86B233;text-transform:uppercase;letter-spacing:0.08em;margin:14px 0 4px 0;">'
        'Species / Pathogen Search</p>',
        unsafe_allow_html=True
    )
    _mobile_search = st.text_input(
        "Search",
        placeholder="e.g. emerald ash borer, soybean, Florida…",
        key="mobile_search_input",
        label_visibility="collapsed"
    )
    if _mobile_search and _mobile_search.strip():
        search_term = _mobile_search

# ══════════════════════════════════════════════════════════════════════════════
# SEARCH RESULT DETAIL CARD
# ══════════════════════════════════════════════════════════════════════════════
PEST_ICONS = {"Insect":"🐛","Fungal":"🍄","Bacterial":"🦠","Viral":"🔬",
              "Oomycete":"💧","Nematode":"🪱","Tick":"🕷️"}
def pest_icon(t):
    for k, v in PEST_ICONS.items():
        if isinstance(t, str) and k.lower() in t.lower(): return v
    return "🔸"

if search_term and search_term.strip():
    if filtered.empty:
        st.markdown(f"""
        <div style="background:#fff7ed;border-left:5px solid #f59e0b;border-radius:0 8px 8px 0;
                    padding:16px 20px;margin:16px 0;">
          <div style="font-family:'Oswald',sans-serif;font-size:1.1rem;font-weight:600;color:#92400e;">
            ⚠️ &nbsp;"{search_term}" is not currently in the PestTrail database.
          </div>
          <div style="font-size:1.125rem;color:#78350f;margin-top:6px;">
            This pest or pathogen has not yet been added to our verified records.
            The daily update agent will pick it up if a confirmed US detection exists in
            USDA APHIS, NPDN, or peer-reviewed literature.
            You can also check: <strong>aphis.usda.gov</strong> · <strong>invasivespeciesinfo.gov</strong>
          </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        exact = filtered[filtered["pest_common_name"].str.lower() == search_term.strip().lower()]
        r = exact.iloc[0] if not exact.empty else filtered.iloc[0]
        status = r.get("eradication_status", "")
        bcls = {"Eradicated":"badge-green","Eradication Ongoing":"badge-yellow",
                "Not Yet Arrived":"badge-blue"}.get(status, "badge-red")
        sico = {"Eradicated":"🟢","Eradication Ongoing":"🟡","Not Yet Arrived":"🔵"}.get(status,"🔴")
        inoc = r.get("inoculum_type","")
        inoc_html = ""
        if inoc and inoc not in ("Not applicable — insect pest","Not applicable — tick",""):
            inoc_html = f'<div class="pdc-inoculum"><strong>🧫 Inoculum / Transmission:</strong> {inoc}</div>'

        fields = [
            ("Type",              r["pest_type"]),
            ("First Detected (US)", r["year_first_detected_us"]),
            ("Est. Year of Arrival", r["estimated_year_arrival"]),
            ("Origin Country",    r["origin_country"]),
            ("Mode of Entry",     r["mode_of_entry"]),
            ("Port of Entry",     r["port_of_entry"]),
            ("Host Plants / Animals", r["host_plant_animal"]),
            ("States Affected",   r["us_states_affected"]),
        ]
        fields_html = "".join(
            f'<div class="pdc-field"><div class="pdc-field-label">{lbl}</div>'
            f'<div class="pdc-field-value">{val}</div></div>'
            for lbl, val in fields
        )
        # Enriched Economic Impact field with source URL + year + verified badge
        _econ_val   = str(r.get("economic_impact_usd", "") or "")
        _econ_url   = str(r.get("economic_impact_source_url", "") or "")
        _econ_year  = str(r.get("economic_impact_year", "") or "")
        _econ_vdate = str(r.get("economic_verified_date", "") or "")
        _src_link = (f'<a href="{_econ_url}" target="_blank" rel="noopener" '
            f'style="color:#116AAB;font-size:1.0625rem;text-decoration:none;font-weight:600;'
            f'margin-left:8px;white-space:nowrap;">→ View Source</a>'
            if _econ_url and _econ_url not in ("", "nan") else "")
        _year_badge = (f'<span style="background:#eff6ff;color:#1e3a5f;border-radius:3px;'
            f'font-size:0.875rem;padding:2px 7px;font-weight:600;margin-left:8px;">'
            f'Est. {_econ_year}</span>'
            if _econ_year and _econ_year not in ("", "nan") else "")
        _vpill = (f'<div style="margin-top:5px;">'
            f'<span style="background:#dcfce7;color:#14532d;border-radius:10px;'
            f'font-size:1.125rem;padding:2px 9px;font-weight:600;">'
            f'✓ Verified {_econ_vdate}</span></div>'
            if _econ_vdate and _econ_vdate not in ("", "nan") else "")
        fields_html += (
            f'<div class="pdc-field" style="grid-column:1/-1;">'
            f'<div class="pdc-field-label">Economic Impact</div>'
            f'<div class="pdc-field-value">{_econ_val}{_year_badge}{_src_link}{_vpill}</div>'
            f'</div>'
        )
        st.markdown(f"""
        <div class="pdc-name" style="margin-top:20px;">
          {pest_icon(r['pest_type'])} &nbsp;Top result for <em>"{search_term}"</em>
        </div>
        <div class="pest-detail-card">
          <div style="display:flex;align-items:flex-start;justify-content:space-between;gap:12px;">
            <div>
              <div class="pdc-name">{r['pest_common_name']}</div>
              <div class="pdc-sci">{r['pest_scientific_name']}</div>
            </div>
            <span class="status-badge {bcls}">{sico} {status}</span>
          </div>
          <div class="pdc-grid">{fields_html}</div>
          {inoc_html}
          <div class="pdc-footer">
            <strong>Quarantine:</strong> {r['quarantine_status']} &nbsp;·&nbsp;
            <strong>Sources:</strong> {r['data_sources']} &nbsp;·&nbsp;
            <strong>Verified:</strong> {r.get('data_verified_date','N/A')}
          </div>
        </div>
        <p style="font-size:1.0625rem;color:#6b7280;margin-bottom:0;">
          Showing {len(filtered)} result(s) for '{search_term}'
        </p>
        """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# KPI CARDS — STELLA-style large counters
# ══════════════════════════════════════════════════════════════════════════════
def two_col_legend(color_map, pull_up=22):
    """Render a 2-column legend pulled up into the chart's bottom margin space."""
    items_html = "".join(
        f'<div style="display:flex;align-items:center;gap:8px;">'
        f'<span style="width:12px;height:12px;border-radius:50%;background:{c};'
        f'flex-shrink:0;display:inline-block;"></span>'
        f'<span style="font-size:14px;color:#1e293b;">{pt}</span></div>'
        for pt, c in color_map.items()
    )
    st.markdown(
        f'<div style="background:#ffffff;border-radius:0 0 8px 8px;'
        f'padding:10px 16px 14px 16px;margin-top:-{pull_up}px;'
        f'border:1px solid #f1f5f9;border-top:none;">'
        f'<p style="font-weight:700;font-size:16px;color:#1e293b;margin:0 0 6px 0;">Organism Type</p>'
        f'<div style="display:grid;grid-template-columns:1fr 1fr;gap:5px 32px;">{items_html}</div>'
        f'</div>',
        unsafe_allow_html=True
    )


def section_header(icon, title, sub=""):
    sub_html = f'<p class="pt-section-sub">{sub}</p>' if sub else ""
    st.markdown(f"""
    <div class="pt-section-header">
      <div class="section-icon">{icon}</div>
      <div>
        <p class="pt-section-title">{title}</p>
        {sub_html}
      </div>
    </div>
    """, unsafe_allow_html=True)

def fig_note(heading, description, footnote):
    st.markdown(
        f'<div style="margin:0 0 10px 0;">'
        f'<p style="font-family:Oswald,sans-serif;font-size:1.05rem;font-weight:600;'
        f'color:#86B233;text-transform:uppercase;letter-spacing:0.05em;margin:0 0 4px 0;">{heading}</p>'
        f'<p style="font-size:0.88rem;color:#ffffff;font-style:normal;margin:0 0 4px 0;line-height:1.6;">{description}</p>'
        f'<p style="font-size:0.82rem;color:#c4dce8;font-style:italic;margin:0;line-height:1.65;">{footnote}</p>'
        f'</div>', unsafe_allow_html=True)

_lag_series     = filtered["detection_lag_years"].dropna()
_lag_nonzero    = _lag_series[_lag_series > 0]
_lag_median_val = f"{_lag_nonzero.median():.1f}" if not _lag_nonzero.empty else "N/A"
_lag_max        = int(_lag_nonzero.max()) if not _lag_nonzero.empty else 0
_lag_n          = len(_lag_nonzero)
median_lag      = f"{_lag_median_val} yrs"
n_origins = filtered["origin_country"].nunique()

_MAJOR_SECTOR_KEYS = {
    "forest": "Forestry", "timber": "Forestry",
    "soybean": "Field Crops", "wheat": "Field Crops", "grain": "Field Crops", "corn": "Field Crops",
    "citrus": "Fruit & Vegetables", "horticultur": "Fruit & Vegetables",
    "viticultur": "Fruit & Vegetables", "vegetable": "Fruit & Vegetables",
    "pollinator": "Pollinators & Apiculture", "apicultur": "Pollinators & Apiculture", "honey": "Pollinators & Apiculture",
    "aquatic": "Aquatic & Water Systems", "water": "Aquatic & Water Systems",
    "urban": "Urban & Landscape", "ornamental": "Urban & Landscape", "turf": "Urban & Landscape",
    "agriculture": "Agriculture (General)",
}
def _norm_major_sector(s):
    if not isinstance(s, str): return "Agriculture (General)"
    sl = s.lower()
    for k, v in _MAJOR_SECTOR_KEYS.items():
        if k in sl:
            return v
    return "Agriculture (General)"

n_major_sectors = filtered["impact_sector"].apply(_norm_major_sector).nunique() if not filtered.empty else 0

st.markdown(f"""
<div class="kpi-row">
  <div class="kpi-card green">
    <span class="kpi-icon-overlay">🌿</span>
    <div class="kpi-value">{len(filtered)}</div>
    <div class="kpi-label">Taxa Tracked</div>
    <div class="kpi-sub">insects · pathogens · nematodes · 1995–2026</div>
  </div>
  <div class="kpi-card navy">
    <span class="kpi-icon-overlay">⏱</span>
    <div class="kpi-value">{median_lag}</div>
    <div class="kpi-label">Median Detection Lag</div>
    <div class="kpi-sub">pre-detection spread only · range: 1–{_lag_max} yrs (n={_lag_n})</div>
  </div>
  <div class="kpi-card teal">
    <span class="kpi-icon-overlay">🌍</span>
    <div class="kpi-value">{n_origins}</div>
    <div class="kpi-label">Recorded Origins</div>
    <div class="kpi-sub">countries of first detection</div>
  </div>
  <div class="kpi-card gold">
    <span class="kpi-icon-overlay">🌾</span>
    <div class="kpi-value">{n_major_sectors}</div>
    <div class="kpi-label">Sectors Impacted</div>
    <div class="kpi-sub">agriculture · forestry · horticulture</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# CHART THEME HELPERS  — defined here so all sections below can use them
# ══════════════════════════════════════════════════════════════════════════════
COLORS = ["#86B233","#116AAB","#EEB638","#07334E","#4D849D","#d95f02","#7570b3","#e7298a","#1b9e77"]
BASE = dict(
    plot_bgcolor="#ffffff", paper_bgcolor="#ffffff",
    font=dict(family="Roboto, sans-serif", size=15, color="#1e293b"),
)
TICK = dict(tickfont=dict(size=15, color="#1e293b"), title_font=dict(size=15, color="#1e293b"))
# Chart heights — smaller on mobile so charts fit without scrolling
_CH = dict(small=240 if is_mobile else 310, medium=290 if is_mobile else 400,
           large=300 if is_mobile else 480, hrow=36 if is_mobile else 52)
_PCFG = dict(displayModeBar=False, responsive=True)

(tab_econ, tab_policy, tab_sector, tab_erad, tab_pathway, tab_detect) = st.tabs([
    "💰 Economic Impact",
    "📊 Biosecurity Economics",
    "🎯 Risk & Threat Intelligence",
    "🏆 Eradication Scorecard",
    "🚢 Entry Pathways",
    "🔬 Biosurveillance & Records",
])

with tab_policy:
    # ══════════════════════════════════════════════════════════════════════════════
    # POLICY GAP  — The site's most shareable single number
    # Sources: Fantle-Lepczyk et al. 2022 Sci. Total Environ. 819:153048 · USDA APHIS FY2025 PPA §7721
    #          Diagne et al. 2021 Nature 592:571-576 · USDA ERS · Bee Informed Partnership 2024-25
    # ══════════════════════════════════════════════════════════════════════════════
    _pol = load_policy()
    _pg  = _pol.get("policy_gap", {})
    _updated = _pol.get("_metadata", {}).get("last_updated", "")
    _updated_str = f" · Data refreshed {_updated}" if _updated else ""

    _damage_label = _pg.get('annual_damage_label','$40B').lstrip('~')
    _prev_label   = _pg.get('annual_prevention_label','$75M').lstrip('~')
    section_header("⚖️", "Federal Investment vs. Documented Economic Damage",
                   f"Observed US invasive pest damage: ~{_damage_label}/year · USDA APHIS EDRR prevention appropriation: ~{_prev_label}/year · loss ratio quantifies the structural underinvestment in early detection and rapid response{_updated_str}")

    _src_footnote = "Fantle-Lepczyk et al. 2022 Sci. Total Environ. 819:153048 · USDA APHIS FY2025 Congressional Justification PPA §7721 · Liebhold &amp; Tobin (2008) Annu. Rev. Entomol. 53:387–408"

    _roi_label  = str(_pg.get('roi_per_dollar','$17')).split('(')[0].strip()
    _pox_roi    = _pg.get('plum_pox_roi','80×')
    _pox_cost   = _pg.get('plum_pox_cost_million',50)
    _pox_avoid  = _pg.get('plum_pox_avoided_billion',4)
    _erad_win   = _pg.get('eradication_window_years',5)
    _damage_val = _pg.get('annual_damage_label','$40B')
    _prev_val   = _pg.get('annual_prevention_label','$75M')
    _loss_ratio = _pg.get('loss_ratio','533×')

    if is_mobile:
        st.markdown(f"""
<div style="background:#07334E;border-radius:12px;padding:18px 16px;">
  <div style="background:rgba(239,68,68,0.12);border:1px solid rgba(239,68,68,0.4);
    border-radius:10px;padding:18px;text-align:center;margin-bottom:10px;">
    <div style="font-family:'Oswald',sans-serif;font-size:0.9rem;font-weight:700;
      color:#fca5a5;letter-spacing:0.1em;text-transform:uppercase;margin-bottom:6px;">
      Annual Crop &amp; Ecosystem Damage</div>
    <div style="font-family:'Oswald',sans-serif;font-size:2.6rem;font-weight:700;
      color:#f87171;line-height:1;">{_damage_val}</div>
    <div style="font-size:0.88rem;color:#fca5a5;margin-top:4px;">per year · US economy</div>
    <div style="font-size:0.88rem;color:#c4dff0;margin-top:8px;line-height:1.5;">
      Crops · forestry · water systems · invasive species only</div>
  </div>
  <div style="text-align:center;padding:10px 0;margin-bottom:10px;">
    <div style="font-family:'Oswald',sans-serif;font-size:2.2rem;font-weight:700;
      color:#EEB638;line-height:1;">{_loss_ratio}</div>
    <div style="font-size:0.85rem;color:#a8c8dc;text-transform:uppercase;
      letter-spacing:0.08em;margin-top:4px;">implied loss ratio per $1 prevention spent</div>
    <div style="font-size:0.8rem;color:#9dc8dc;margin-top:3px;font-style:italic;">
      computed from figures above — not independently cited</div>
  </div>
  <div style="background:rgba(134,178,51,0.1);border:1px solid rgba(134,178,51,0.35);
    border-radius:10px;padding:18px;text-align:center;margin-bottom:14px;">
    <div style="font-family:'Oswald',sans-serif;font-size:0.9rem;font-weight:700;
      color:#86B233;letter-spacing:0.1em;text-transform:uppercase;margin-bottom:6px;">
      Annual Federal Prevention Budget</div>
    <div style="font-family:'Oswald',sans-serif;font-size:2.6rem;font-weight:700;
      color:#86B233;line-height:1;">{_prev_val}</div>
    <div style="font-size:0.88rem;color:#a8d070;margin-top:4px;">per year · USDA APHIS PPQ</div>
    <div style="font-size:0.88rem;color:#c4dff0;margin-top:8px;line-height:1.5;">
      Early Detection &amp; Rapid Response · PPA §7721 · FY2025</div>
  </div>
  <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:0;
    padding-top:12px;border-top:1px solid rgba(134,178,51,0.2);">
    <div style="text-align:center;padding:10px 4px;">
      <div style="font-family:'Oswald',sans-serif;font-size:1.5rem;color:#EEB638;
        font-weight:700;line-height:1;">{_roi_label}</div>
      <div style="font-size:0.78rem;color:#fff;font-weight:600;margin-top:4px;">per $1 spent</div>
      <div style="font-size:0.72rem;color:#a8c8dc;margin-top:2px;">OTA 1993</div>
    </div>
    <div style="text-align:center;padding:10px 4px;
      border-left:1px solid rgba(134,178,51,0.2);
      border-right:1px solid rgba(134,178,51,0.2);">
      <div style="font-family:'Oswald',sans-serif;font-size:1.5rem;color:#EEB638;
        font-weight:700;line-height:1;">{_pox_roi}</div>
      <div style="font-size:0.78rem;color:#fff;font-weight:600;margin-top:4px;">Plum Pox ROI</div>
      <div style="font-size:0.72rem;color:#a8c8dc;margin-top:2px;">${_pox_cost}M → ${_pox_avoid}B</div>
    </div>
    <div style="text-align:center;padding:10px 4px;">
      <div style="font-family:'Oswald',sans-serif;font-size:1.5rem;color:#EEB638;
        font-weight:700;line-height:1;">&lt;{_erad_win} yrs</div>
      <div style="font-size:0.78rem;color:#fff;font-weight:600;margin-top:4px;">erad. window</div>
      <div style="font-size:0.72rem;color:#a8c8dc;margin-top:2px;">Liebhold 2008</div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)
    else:
        components.html(f"""
<link href="https://fonts.googleapis.com/css2?family=Oswald:wght@600;700&family=Roboto:wght@400;500&display=swap" rel="stylesheet">
<style>*{{box-sizing:border-box;margin:0;padding:0;font-family:'Roboto',sans-serif;}}iframe{{display:none;}}</style>
<div style="background:#07334E;border-radius:12px;padding:28px 32px;">
  <div style="display:flex;gap:20px;align-items:stretch;">
    <div style="flex:1;background:rgba(239,68,68,0.12);border:1px solid rgba(239,68,68,0.4);border-radius:10px;padding:22px 24px;text-align:center;display:flex;flex-direction:column;justify-content:center;">
      <div style="font-family:'Oswald',sans-serif;font-size:1.125rem;font-weight:700;color:#fca5a5;letter-spacing:0.12em;text-transform:uppercase;margin-bottom:8px;">Annual Crop &amp; Ecosystem Damage</div>
      <div style="font-family:'Oswald',sans-serif;font-size:3rem;font-weight:700;color:#f87171;line-height:1;">{_damage_val}</div>
      <div style="font-size:1.0625rem;color:#fca5a5;margin-top:6px;">per year &middot; US economy</div>
      <div style="font-size:1.125rem;color:#c4dff0;margin-top:10px;line-height:1.5;">Crops · forestry · water systems<br>Invasive species only — native pest losses excluded</div>
    </div>
    <div style="display:flex;flex-direction:column;align-items:center;justify-content:center;padding:0 8px;min-width:110px;">
      <div style="font-family:'Oswald',sans-serif;font-size:2.6rem;font-weight:700;color:#EEB638;line-height:1;">{_loss_ratio}</div>
      <div style="font-size:1.125rem;color:#a8c8dc;text-transform:uppercase;letter-spacing:0.1em;margin-top:4px;text-align:center;">implied loss ratio<br>per $1 prevention spent</div>
      <div style="font-size:1.0625rem;color:#9dc8dc;margin-top:5px;text-align:center;font-style:italic;">computed from figures above —<br>not independently cited</div>
      <div style="width:2px;height:24px;background:rgba(134,178,51,0.3);margin-top:10px;"></div>
    </div>
    <div style="flex:1;background:rgba(134,178,51,0.1);border:1px solid rgba(134,178,51,0.35);border-radius:10px;padding:22px 24px;text-align:center;display:flex;flex-direction:column;justify-content:center;">
      <div style="font-family:'Oswald',sans-serif;font-size:1.125rem;font-weight:700;color:#86B233;letter-spacing:0.12em;text-transform:uppercase;margin-bottom:8px;">Annual Federal Prevention Budget</div>
      <div style="font-family:'Oswald',sans-serif;font-size:3rem;font-weight:700;color:#86B233;line-height:1;">{_prev_val}</div>
      <div style="font-size:1.0625rem;color:#a8d070;margin-top:6px;">per year &middot; USDA APHIS PPQ</div>
      <div style="font-size:1.125rem;color:#c4dff0;margin-top:10px;line-height:1.5;">Early Detection &amp; Rapid Response line item<br>PPA §7721 · FY2025 Congressional Justification</div>
    </div>
  </div>
  <div style="margin-top:18px;padding-top:16px;border-top:1px solid rgba(134,178,51,0.2);display:flex;gap:0;">
    <div style="flex:1;text-align:center;padding:16px 12px;">
      <div style="font-family:'Oswald',sans-serif;font-size:2rem;color:#EEB638;font-weight:700;line-height:1;">{_roi_label}</div>
      <div style="font-size:1.125rem;color:#ffffff;font-weight:600;margin-top:6px;">returned per $1 spent</div>
      <div style="font-size:1.0625rem;color:#a8c8dc;margin-top:3px;">on early detection · OTA 1993 OTA-F-565</div>
    </div>
    <div style="width:1px;background:rgba(134,178,51,0.2);"></div>
    <div style="flex:1;text-align:center;padding:16px 12px;">
      <div style="font-family:'Oswald',sans-serif;font-size:2rem;color:#EEB638;font-weight:700;line-height:1;">{_pox_roi}</div>
      <div style="font-size:1.125rem;color:#ffffff;font-weight:600;margin-top:6px;">Plum Pox eradication ROI</div>
      <div style="font-size:1.0625rem;color:#a8c8dc;margin-top:3px;">${_pox_cost}M cost · ${_pox_avoid}B avoided</div>
    </div>
    <div style="width:1px;background:rgba(134,178,51,0.2);"></div>
    <div style="flex:1;text-align:center;padding:16px 12px;">
      <div style="font-family:'Oswald',sans-serif;font-size:2rem;color:#EEB638;font-weight:700;line-height:1;">&lt;{_erad_win} yrs</div>
      <div style="font-size:1.125rem;color:#ffffff;font-weight:600;margin-top:6px;">eradication window</div>
      <div style="font-size:1.0625rem;color:#a8c8dc;margin-top:3px;">after establishment, feasibility drops sharply · Liebhold &amp; Tobin (2008)</div>
    </div>
  </div>
</div>
""", height=380, scrolling=False)

    st.markdown('<div style="height:8px;"></div>', unsafe_allow_html=True)

    # Historical damage trend — InvaCost / Fantle-Lepczyk 2022 derived US annual estimates
    import plotly.graph_objects as _go_pg
    # Build cumulative established species count from live CSV data
    import pandas as _pd_pg
    _est = df[~df["eradication_status"].str.contains("Not Yet", na=False)].copy()
    _est = _est.dropna(subset=["year_first_detected_us"])
    _est["_yr"] = _est["year_first_detected_us"].astype(str).str.extract(r"(\d{4})")[0].astype(int)
    _cum = _est.groupby("_yr").size().reset_index(name="new").sort_values("_yr")
    _cum["cumulative"] = _cum["new"].cumsum()
    # Filter out pre-1993 outlier — dataset is 1995-focused; 1951 single point distorts x-axis
    _cum_plot = _cum[_cum["_yr"] >= 1993].copy()
    _fig_trend = _go_pg.Figure()
    # Bars — annual new invasive species detections (1993+)
    _fig_trend.add_trace(_go_pg.Bar(
        x=_cum_plot["_yr"].tolist(), y=_cum_plot["new"].tolist(),
        name="New Invasive Species Detected (per year)",
        yaxis="y1",
        marker_color="#EEB638", opacity=0.8,
        hovertemplate="%{x}: %{y} new species detected<extra></extra>"
    ))
    # Line — cumulative established invasive species (1993+)
    _fig_trend.add_trace(_go_pg.Scatter(
        x=_cum_plot["_yr"].tolist(), y=_cum_plot["cumulative"].tolist(),
        mode="lines+markers", name="Cumulative Established Invasive Species",
        yaxis="y2",
        line=dict(color="#116AAB", width=2.5),
        marker=dict(size=7, color="#116AAB"),
        hovertemplate="%{x}: %{y} species total<extra></extra>"
    ))
    _fig_trend.update_layout(
        height=_CH['small'],
        margin=dict(l=10, r=60, t=30, b=70),
        legend=dict(orientation="h", y=-0.26, x=0, font=dict(size=11, color="#1e293b"),
                    bgcolor="rgba(0,0,0,0)"),
        bargap=0.15,
        yaxis=dict(title="New Detections / Year", showgrid=True, gridcolor="#e2e8f0",
                   tickfont=dict(size=12, color="#EEB638"), title_font=dict(size=12, color="#EEB638")),
        yaxis2=dict(title="Cumulative Species", overlaying="y", side="right", showgrid=False,
                    tickfont=dict(size=12, color="#116AAB"), title_font=dict(size=12, color="#116AAB")),
        **BASE
    )
    _fig_trend.update_xaxes(showgrid=True, gridcolor="#e2e8f0", title_text="Year",
                             range=[1993, 2025], **TICK)
    fig_note(
        "Annual New Detections & Cumulative Established Invasive Species (1993–2025)",
        "Bars show new invasive species confirmed in the US each year; the overlaid line tracks the cumulative count of established species since 1993.",
        "Detection data: USDA-APHIS / USGS US-RIIS (verified April 2026) · One pre-1993 record (1951) excluded from chart, included in cumulative total · "
        "Sources: Fantle-Lepczyk et al. 2022 Sci. Total Environ. 819:153048 · USDA APHIS FY2025 CJ PPA §7721 · "
        "Liebhold & Tobin (2008) Annu. Rev. Entomol. 53:387–408 · OTA 1993 OTA-F-565"
    )
    st.plotly_chart(_fig_trend, use_container_width=True, config=_PCFG)

with tab_erad:
    # ══════════════════════════════════════════════════════════════════════════════
    # ERADICATION SCORECARD  — What works, what doesn't
    # Uses eradication_status field from CSV
    # ══════════════════════════════════════════════════════════════════════════════
    section_header("🏆", "Eradication Program Outcomes",
                   "Status classification for USDA APHIS and cooperative eradication programs · species are grouped by confirmed eradication, active management, or long-term containment; detection lag data inform program response benchmarks")

    erad_df = df.copy()
    status_map = {
        "Eradicated":           ("🟢", "badge-green",  "Eradicated"),
        "Eradication Ongoing":  ("🟡", "badge-yellow", "Eradication Ongoing"),
        "Established":          ("🔴", "badge-red",    "Established (failed to eradicate)"),
        "Not Yet Arrived":      ("🔵", "badge-blue",   "Threat — Not Yet in US"),
    }
    def erad_group(s):
        for k in status_map:
            if isinstance(s, str) and k.lower() in s.lower():
                return k
        return "Established"

    erad_df["erad_group"] = erad_df["eradication_status"].apply(erad_group)
    counts = erad_df["erad_group"].value_counts()
    n_erad     = counts.get("Eradicated", 0)
    n_ongoing  = counts.get("Eradication Ongoing", 0)
    n_threat   = counts.get("Not Yet Arrived", 0)

    # Split "Established" into program-attempted vs never-attempted
    n_abandoned = int(erad_df["eradication_status"].str.contains("abandoned", case=False, na=False).sum())
    n_managed   = int(erad_df["eradication_status"].apply(
        lambda s: isinstance(s, str) and
        erad_group(s) == "Established" and
        "abandoned" not in s.lower()
    ).sum())

    # Success rate: completed programs only (excludes ongoing — outcome not yet determined)
    n_completed = n_erad + n_abandoned
    success_pct = round(n_erad / n_completed * 100) if n_completed else 0

    ecol1, ecol2, ecol3 = st.columns(3)
    for col, emoji, label, val, sub, color in [
        (ecol1, "🟢", "Eradicated",             n_erad,   "confirmed elimination — program closed",  "#14532d"),
        (ecol2, "🟡", "Eradication Ongoing",     n_ongoing,"active federal program underway",         "#713f12"),
        (ecol3, "⚫", "Under Active Management", n_managed,"no eradication program initiated · managed through ongoing suppression", "#374151"),
    ]:
        col.markdown(
    f'<div style="background:#ffffff;border-radius:8px;padding:24px 20px;'
    f'box-shadow:0 2px 12px rgba(7,51,78,0.08);border-top:4px solid {color};'
    f'text-align:center;margin-bottom:8px;'
    f'min-height:260px;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:4px;">'
    f'<div style="font-size:1.6rem;line-height:1;">{emoji}</div>'
    f'<div style="font-family:Oswald,sans-serif;font-size:2.4rem;font-weight:700;color:{color};line-height:1.1;">{val}</div>'
    f'<div style="font-size:1.0rem;font-weight:700;color:#374151;text-transform:uppercase;letter-spacing:0.08em;margin-top:6px;">{label}</div>'
    f'<div style="font-size:0.95rem;color:#4b5563;margin-top:4px;line-height:1.5;max-width:220px;">{sub}</div>'
    f'</div>', unsafe_allow_html=True)

    st.markdown(
    f'<div style="background:#fef9ec;border:1px solid #fde68a;border-radius:8px;padding:14px 20px;margin-top:4px;margin-bottom:4px;">'
    f'<span style="font-family:Oswald,sans-serif;font-size:1rem;color:#92400e;font-weight:600;">Dataset summary: </span>'
    f'<span style="font-size:1.125rem;color:#78350f;">'
    f'Of {n_completed} completed eradication programs in this dataset, '
    f'<strong>{success_pct}% ({n_erad} of {n_completed})</strong> achieved confirmed elimination. '
    f'{n_ongoing} programs are currently active — outcomes pending. '
    f'{n_managed} established species are managed through suppression with no eradication program initiated '
    f'(includes 1 abandoned program — Citrus Canker, USDA APHIS 1995–2006). '
    f'Eradication feasibility declines substantially with detection delay.</span>'
    f'<span style="font-size:1.125rem;color:#a16207;"> — Liebhold &amp; Tobin (2008) Annu. Rev. Entomol. 53:387–408 · '
    f'Dataset: {len(erad_df)} species, USDA-APHIS / USGS US-RIIS (verified April 2026)</span>'
    f'</div>', unsafe_allow_html=True)

    # Detailed eradication table
    erad_detail = df[["pest_common_name","pest_scientific_name","pest_type",
                       "year_first_detected_us","detection_lag_years",
                       "eradication_status","economic_impact_usd"]].copy()
    erad_detail = erad_detail.rename(columns={
        "pest_common_name":"Pest",
        "pest_scientific_name":"Scientific Name",
        "pest_type":"Type",
        "year_first_detected_us":"Detected",
        "detection_lag_years":"Lag (yrs)",
        "eradication_status":"Status",
        "economic_impact_usd":"Economic Impact",
    })
    erad_detail["erad_group"] = df["eradication_status"].apply(erad_group)
    erad_detail = erad_detail.sort_values("erad_group", key=lambda x: x.map(
        {"Eradicated":0,"Eradication Ongoing":1,"Established":2,"Not Yet Arrived":3}))
    _erad_display = erad_detail.drop(columns="erad_group").reset_index(drop=True)
    _erad_display.index = _erad_display.index + 1
    _erad_display.index.name = "#"
    st.dataframe(_erad_display, width="stretch", height=300)

with tab_econ:
    # ══════════════════════════════════════════════════════════════════════════════
    # ECONOMIC IMPACT INTELLIGENCE
    # Sources: apply_economic_data.py wrote economic_impact_source_url,
    #          economic_impact_year, economic_verified_date into the CSV.
    # ══════════════════════════════════════════════════════════════════════════════
    section_header("💰", "Per-Species Documented Economic Losses",
                   "Observed annual and cumulative cost estimates for established invasive pests · figures drawn from USDA ERS, USDA USFS, and primary peer-reviewed sources · potential or modeled losses are excluded")

    def _parse_dollar(raw):
        """Return a float (USD billions) from strings like '$8.7B', '$450M', '~$2.4 billion'.
        Only accepts figures with explicit magnitude markers (B/M/T/billion/million/trillion).
        Returns None for bare years, per-unit costs, or unparseable text."""
        import re
        if not isinstance(raw, str):
            return None
        # Skip strings that are purely 'Under assessment' / no figure
        upper = raw.upper()
        if not any(k in upper for k in ("BILLION","TRILLION","MILLION"," B "," M ","$","USD")):
            return None
        # Patterns: "$X.XB", "$X billion", "X.X billion dollars", etc.
        # Require explicit B/M/T suffix or written-out word immediately after the number
        # Strip "+" (e.g. "$1+" → "$1") and "~" so patterns match cleanly
        upper = upper.replace("+", "").replace("~", "")
        patterns = [
            r"\$\s*(\d[\d,]*\.?\d*)\s*T(?:RILLION)?",    # $X trillion
            r"\$\s*(\d[\d,]*\.?\d*)\s*B(?:ILLION)?",     # $X billion / $XB
            r"\$\s*(\d[\d,]*\.?\d*)\s*M(?:ILLION)?",     # $X million / $XM
            r"(\d[\d,]*\.?\d*)\s*TRILLION\s*(?:DOLLAR)?",
            r"(\d[\d,]*\.?\d*)\s*BILLION\s*(?:DOLLAR)?",
            r"(\d[\d,]*\.?\d*)\s*MILLION\s*(?:DOLLAR)?",
        ]
        multipliers = [1_000, 1, 1/1_000, 1_000, 1, 1/1_000]
        for pat, mult in zip(patterns, multipliers):
            m = re.search(pat, upper.replace(",", ""))
            if m:
                return float(m.group(1)) * mult
        return None

    # Build working dataframe — include eradication_status for filtering
    _econ_base_cols = ["pest_common_name","pest_scientific_name","pest_type",
                       "economic_impact_usd","impact_sector","eradication_status"]
    _econ_enriched  = ["economic_impact_source_url","economic_impact_year","economic_verified_date"]
    _econ_cols = _econ_base_cols + [c for c in _econ_enriched if c in df.columns]
    econ_df = df[_econ_cols].copy()
    for col in _econ_enriched:
        if col not in econ_df.columns:
            econ_df[col] = None

    econ_df["_val_billions"] = econ_df["economic_impact_usd"].apply(_parse_dollar)

    # Flag figures as potential/projected vs observed
    _potential_keywords = ["potential","if unchecked","if established","at risk","threatened","threatens","could","would","projected"]
    def _is_potential(raw):
        if not isinstance(raw, str): return False
        return any(k in raw.lower() for k in _potential_keywords)
    econ_df["_is_potential"] = econ_df["economic_impact_usd"].apply(_is_potential)

    # Flag cumulative multi-year totals (not annual figures)
    def _is_cumulative(raw):
        if not isinstance(raw, str): return False
        return "cumulative" in raw.lower()
    econ_df["_is_cumulative"] = econ_df["economic_impact_usd"].apply(_is_cumulative)

    # Flag eradication program costs (not crop damage)
    def _is_eradication_cost(raw):
        if not isinstance(raw, str): return False
        return "eradication cost" in raw.lower()
    econ_df["_is_eradication_cost"] = econ_df["economic_impact_usd"].apply(_is_eradication_cost)

    # Flag old estimates (pre-2015)
    def _is_old(yr):
        try: return int(yr) < 2015
        except: return False
    econ_df["_is_old"] = econ_df["economic_impact_year"].apply(_is_old)

    # Filter: only established/ongoing pests — exclude Not Yet Arrived and Eradicated
    _active_mask = ~econ_df["eradication_status"].str.contains("Not Yet|Eradicated", na=False, case=False)
    econ_active = econ_df[_active_mask].copy()

    has_data = econ_active["_val_billions"].notna().any()
    verified_col_present = "economic_verified_date" in df.columns and df["economic_verified_date"].notna().any()

    # Annual observed only — excludes projected, cumulative, and eradication costs
    _annual_mask = (
        econ_active["_val_billions"].notna() &
        ~econ_active["_is_potential"] &
        ~econ_active["_is_cumulative"] &
        ~econ_active["_is_eradication_cost"]
    )
    annual_total   = econ_active.loc[_annual_mask, "_val_billions"].sum()
    n_annual       = int(_annual_mask.sum())

    # ── KPI — single bottom-line figure ──────────────────────────────────────────
    st.markdown(
f'<div style="background:#ffffff;border-radius:8px;padding:22px 28px;'
f'box-shadow:0 2px 12px rgba(7,51,78,0.08);border-top:4px solid #116AAB;'
f'margin-bottom:8px;">'
f'<div style="display:flex;align-items:baseline;gap:12px;flex-wrap:wrap;">'
f'<span style="font-family:Oswald,sans-serif;font-size:2.6rem;font-weight:700;color:#116AAB;line-height:1;">'
f'${annual_total:.1f}B</span>'
f'<span style="font-size:1.0625rem;font-weight:700;color:#374151;text-transform:uppercase;letter-spacing:0.06em;">'
f'Documented Annual Losses from Established Invasive Pests</span>'
f'</div>'
f'<div style="font-size:1.125rem;color:#4b5563;margin-top:6px;">'
f'Sum of annual observed figures only ({n_annual} species) · '
f'Cumulative totals, eradication program costs, and projected estimates excluded · '
f'Sources: USDA ERS, USFS, APHIS, peer-reviewed literature'
f'</div>'
f'</div>', unsafe_allow_html=True)

    st.markdown('<div style="height:12px;"></div>', unsafe_allow_html=True)

    # ── Agent-not-yet-run notice ──────────────────────────────────────────────────
    if not verified_col_present:
        st.markdown(
'<div style="background:#eff6ff;border-left:5px solid #3b82f6;border-radius:0 8px 8px 0;'
'padding:14px 20px;margin-bottom:16px;">'
'<div style="font-family:Oswald,sans-serif;font-size:1.0625rem;font-weight:600;color:#1e3a5f;">'
'🤖 &nbsp;Economic Research Agent has not yet run</div>'
'<div style="font-size:1.125rem;color:#1e40af;margin-top:5px;">'
'Charts below show figures already in the CSV. Run <code>python3 economic_research_agent.py</code> '
'to verify all 49 figures, add source URLs, and generate the Word review document.</div>'
'</div>', unsafe_allow_html=True)

    # ── Chart: Documented Economic Losses (observed/cumulative only) ─────────────
    if has_data:
        # Exclude projected/modeled figures — those live in Risk & Threat Intelligence
        observed_mask = ~econ_active["_is_potential"]
        top_econ = (econ_active[observed_mask & econ_active["_val_billions"].notna()]
                    .nlargest(15, "_val_billions")
                    .sort_values("_val_billions"))
        top_econ = top_econ.copy()
        top_econ["hover_src"] = top_econ.apply(
            lambda r: r["economic_impact_source_url"]
            if isinstance(r.get("economic_impact_source_url"), str) and r["economic_impact_source_url"]
            else "Run economic_research_agent.py for source URLs",
            axis=1
        )
        top_econ["year_label"] = top_econ["economic_impact_year"].apply(
            lambda y: f" ({int(y)})" if y and str(y).isdigit() else ""
        )
        top_econ["bar_label"] = top_econ.apply(
            lambda r: (
                f"${r['_val_billions']:.1f}B{r['year_label']}"
                + (" · potential" if r["_is_potential"] else "")
                + (" · cumulative" if r["_is_cumulative"] and not r["_is_potential"] else "")
                + (" · eradication cost" if r["_is_eradication_cost"] and not r["_is_potential"] else "")
                + (" · est. pre-2015" if r["_is_old"] and not r["_is_potential"] and not r["_is_cumulative"] and not r["_is_eradication_cost"] else "")
            ), axis=1
        )
        top_econ["mobile_label"] = top_econ.apply(
            lambda r: f"${r['_val_billions']:.1f}B{r['year_label']}", axis=1
        )
        row_h  = 38
        height = max(380, len(top_econ) * row_h + 140)

        fig_note(
            "Observed annual losses and verified cumulative figures",
            "Per-species economic damage drawn from USDA ERS, USDA USFS, and primary peer-reviewed sources. Bars represent individual pest impact; color indicates pest type. Potential or modeled losses are excluded.",
            "· cumulative = multi-year total, not annual · eradication cost = program expenditure · est. pre-2015 = outdated estimate · Pre-arrival and eradicated species excluded"
        )

        import plotly.graph_objects as _go2
        econ_color_map  = {t: COLORS[i % len(COLORS)] for i, t in enumerate(top_econ["pest_type"].unique())}
        _econ_leg_rows  = -(-len(econ_color_map) // 2)
        _econ_leg_b     = _econ_leg_rows * 25 + 56
        fig = _go2.Figure()
        for _, r in top_econ.iterrows():
            fig.add_shape(type="line",
                x0=0, x1=r["_val_billions"],
                y0=r["pest_common_name"], y1=r["pest_common_name"],
                line=dict(color=econ_color_map.get(r["pest_type"], "#94a3b8"), width=2))
        seen_e = set()
        for _, r in top_econ.iterrows():
            pt  = r["pest_type"]
            col = econ_color_map.get(pt, "#94a3b8")
            show_leg = pt not in seen_e
            seen_e.add(pt)
            _lbl = r["mobile_label"] if is_mobile else r["bar_label"]
            fig.add_trace(_go2.Scatter(
                x=[r["_val_billions"]],
                y=[r["pest_common_name"]],
                mode="markers+text",
                marker=dict(color=col, size=14, line=dict(color="white", width=1.5)),
                text=[f"  {_lbl}"],
                textposition="middle right",
                textfont=dict(size=9 if is_mobile else 11, color="#1e293b"),
                cliponaxis=False,
                name=pt, legendgroup=pt, showlegend=show_leg,
                hovertemplate=(
                    f"<b>{r['pest_common_name']}</b><br>"
                    f"Est. Cost: {r['economic_impact_usd']}<br>"
                    f"Year: {r['economic_impact_year']}<br>"
                    f"Source: {r['hover_src']}<extra></extra>"
                )
            ))
        x_max = top_econ["_val_billions"].max() if not top_econ.empty else 1
        _econ_r = 100 if is_mobile else 120
        _econ_b = 20 if is_mobile else _econ_leg_b
        fig.update_layout(
            height=height, showlegend=False,
            margin=dict(l=10, r=_econ_r, t=20, b=_econ_b),
            **BASE
        )
        fig.update_xaxes(showgrid=True, gridcolor="#e2e8f0",
                         range=[-0.5, x_max * (1.8 if is_mobile else 1.55)],
                         showticklabels=True, ticks="outside",
                         title_text="USD Billions — annual unless labeled cumulative", **TICK)
        fig.update_yaxes(showgrid=False, automargin=True,
                         showticklabels=True, **TICK)
        st.plotly_chart(fig, use_container_width=True, config=_PCFG)
        two_col_legend(econ_color_map, pull_up=0 if is_mobile else _econ_leg_b + 16)

        # ── Source transparency footer ────────────────────────────────────────────
        st.markdown(
'<div style="background:#f8fafc;border:1px solid #e2e8f0;border-radius:6px;'
'padding:12px 18px;font-size:1.125rem;color:#64748b;margin-top:4px;">'
'📊 <strong>Figures verified by PestTrail AI Agent</strong> · '
'Most recent available estimate used per pest · '
'Sources: USDA ERS, USFS, APHIS official reports, peer-reviewed literature'
'</div>', unsafe_allow_html=True)

    else:
        st.info("No parseable economic figures in the current dataset. Check `economic_impact_usd` column in the CSV.")

with tab_sector:
    # ══════════════════════════════════════════════════════════════════════════════
    # SECTOR VULNERABILITY  — Who should be worried
    # Sources: USDA ERS, USFS, Florida Dept. of Agriculture, Cornell Extension
    # ══════════════════════════════════════════════════════════════════════════════
    section_header("🌾", "Agricultural & Natural Resource Sector Exposure",
                   "Cumulative annual economic exposure by sector, derived from peer-reviewed literature and USDA commodity loss assessments · risk ratings reflect current establishment status, damage trajectory, and available management options")

    # Load sector data from live policy intelligence JSON (agent keeps this current)
    _raw_sectors = _pol.get("sector_vulnerability", [])
    SECTOR_DATA = [
        {
            "Sector":       s.get("sector", ""),
            "Key Pests":    s.get("key_pests", ""),
            "Damage/yr":    s.get("damage_per_year", ""),
            "States at Risk": s.get("states_at_risk", ""),
            "Risk Level":   s.get("risk_level", "MODERATE"),
            "Source":       s.get("source", ""),
            "color":        s.get("color", "#EEB638"),
        }
        for s in _raw_sectors
    ] or [
        # Safe fallback if JSON not yet generated
        {"Sector":"Citrus","Key Pests":"HLB, Citrus Canker, Citrus Black Spot","Damage/yr":"$9.4B",
         "States at Risk":"FL, CA, TX, AZ","Risk Level":"CRITICAL","Source":"USDA ERS EIB-219","color":"#ef4444"},
        {"Sector":"Hardwood Forestry","Key Pests":"EAB, ALB, HWA, SOD","Damage/yr":"$7.8B+",
         "States at Risk":"38 states","Risk Level":"CRITICAL","Source":"Aukema et al. 2011 BioScience","color":"#ef4444"},
        {"Sector":"Soybeans","Key Pests":"Asian Soybean Rust, Soybean Aphid","Damage/yr":"$2.4B",
         "States at Risk":"Midwest, Southeast","Risk Level":"HIGH","Source":"USDA NASS","color":"#f97316"},
    ]

    scols = st.columns(2)
    for i, s in enumerate(SECTOR_DATA):
        with scols[i % 2]:
            badge_bg  = {"CRITICAL":"#fef2f2","HIGH":"#fff7ed","MODERATE":"#fffbeb"}[s["Risk Level"]]
            badge_col = {"CRITICAL":"#991b1b","HIGH":"#9a3412","MODERATE":"#713f12"}[s["Risk Level"]]
            c = s['color']; rl = s['Risk Level']
            st.markdown(
f'<div style="background:#fff;border-left:5px solid {c};border-radius:0 8px 8px 0;padding:16px 20px;margin-bottom:12px;box-shadow:0 2px 10px rgba(7,51,78,0.07);">'
f'<div style="display:flex;justify-content:space-between;align-items:flex-start;gap:8px;">'
f'<span style="font-family:Oswald,sans-serif;font-size:1.1rem;font-weight:700;color:#07334E;">{s["Sector"]}</span>'
f'<span style="background:{badge_bg};color:{badge_col};border:1px solid {badge_col}33;border-radius:3px;font-size:1.0625rem;font-weight:700;letter-spacing:0.08em;padding:3px 8px;white-space:nowrap;">{rl}</span>'
f'</div>'
f'<div style="font-size:1.0625rem;color:#374151;margin-top:6px;">🐛 {s["Key Pests"]}</div>'
f'<div style="display:flex;gap:20px;margin-top:8px;">'
f'<div><div style="font-size:1.0625rem;color:#6b7280;text-transform:uppercase;font-weight:700;">Est. Annual Damage</div>'
f'<div style="font-family:Oswald,sans-serif;font-size:1.1rem;color:{c};font-weight:600;">{s["Damage/yr"]}</div></div>'
f'<div><div style="font-size:1.0625rem;color:#6b7280;text-transform:uppercase;font-weight:700;">States at Risk</div>'
f'<div style="font-size:1.125rem;color:#374151;">{s["States at Risk"]}</div></div>'
f'</div>'
f'<div style="font-size:1.0625rem;color:#4b5563;margin-top:8px;border-top:1px solid #f1f5f9;padding-top:6px;">📚 {s["Source"]}</div>'
f'</div>', unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════════════════════════════
    # ESTABLISHED THREATS: PROJECTED ECONOMIC SCENARIOS
    # ══════════════════════════════════════════════════════════════════════════════
    section_header("📈", "Established Threats: Modeled Worst-Case Exposure",
                   "Maximum potential damage estimates under full geographic establishment scenarios · derived from USDA APHIS regulatory impact analyses and published modeling studies · these are not observed annual losses")

    st.markdown(
'<div style="background:#fef3c7;border-left:4px solid #d97706;border-radius:0 8px 8px 0;'
'padding:10px 16px;font-size:1.0625rem;color:#78350f;margin-bottom:16px;">'
'These figures are <strong>economic modeling outputs or threat assessments</strong>, not documented annual losses. '
'They represent what full establishment or unchecked spread could cost — sourced from USDA APHIS risk assessments, '
'academic projections, and sector impact studies.'
'</div>', unsafe_allow_html=True)

    proj_pests = econ_active[econ_active["_is_potential"] & econ_active["_val_billions"].notna()].copy()
    proj_pests = proj_pests[proj_pests["_val_billions"] >= 0.2]  # exclude sub-$200M entries
    proj_pests["_year_sort"] = pd.to_numeric(proj_pests["economic_impact_year"], errors="coerce")
    proj_pests = proj_pests.sort_values("_year_sort", ascending=False, na_position="last")

    # YLH special case: $15B is US pollination industry value, not a YLH damage projection
    _YLH_NAME = "Yellow-Legged Hornet"

    if not proj_pests.empty:
        proj_cols = st.columns(2)
        for i, (_, row) in enumerate(proj_pests.iterrows()):
            is_ylh = row["pest_common_name"] == _YLH_NAME
            is_old = row.get("_is_old", False)
            yr = f" ({int(row['economic_impact_year'])})" if str(row.get("economic_impact_year","")).isdigit() else ""
            src = row.get("economic_impact_source_url","") or row.get("data_sources","USDA APHIS")
            # YLH: show industry at risk, not a damage figure
            cost_display = (
                "Industry at Risk: $15B/yr US pollination value (FDA 2018) — no peer-reviewed YLH damage estimate available"
                if is_ylh else f"${row['_val_billions']:.1f}B{yr}"
            )
            cost_color = "#6a9aaf" if is_ylh else "#EEB638"
            cost_size  = "0.82rem" if is_ylh else "1.2rem"
            old_badge  = (
                f'<span style="background:#451a03;color:#fed7aa;border:1px solid #92400e;border-radius:3px;'
                f'font-size:0.75rem;font-weight:700;padding:2px 6px;margin-left:8px;">est. pre-2015</span>'
                if is_old and not is_ylh else ""
            )
            with proj_cols[i % 2]:
                st.markdown(
f'<div style="background:#07334E;border-radius:10px;padding:18px 22px;margin-bottom:10px;border-left:6px solid #EEB638;">'
f'<div style="display:flex;justify-content:space-between;align-items:flex-start;gap:8px;">'
f'<div style="flex:1;">'
f'<span style="font-family:Oswald,sans-serif;font-size:1.05rem;font-weight:700;color:#fff;">{row["pest_common_name"]}</span>'
f'{old_badge}'
f'<span style="font-style:italic;color:#b8d8ec;font-size:1.0625rem;margin-left:8px;display:block;margin-top:2px;">{row.get("pest_scientific_name","")}</span>'
f'</div>'
f'<span style="font-family:Oswald,sans-serif;font-size:{cost_size};font-weight:700;color:{cost_color};'
f'white-space:{"normal" if is_ylh else "nowrap"};text-align:right;max-width:{"200px" if is_ylh else "none"};">'
f'{cost_display}</span>'
f'</div>'
f'<div style="display:flex;gap:16px;margin-top:12px;flex-wrap:wrap;">'
f'<div style="flex:1;min-width:120px;"><div style="font-size:1.0625rem;color:#b8d8ec;text-transform:uppercase;letter-spacing:0.1em;font-weight:700;">Pest Type</div>'
f'<div style="font-size:1.0625rem;color:#d0e8f2;margin-top:2px;">{row.get("pest_type","")}</div></div>'
f'<div style="flex:1;min-width:120px;"><div style="font-size:1.0625rem;color:#b8d8ec;text-transform:uppercase;letter-spacing:0.1em;font-weight:700;">Host / Sector</div>'
f'<div style="font-size:1.0625rem;color:#d0e8f2;margin-top:2px;">{row.get("impact_sector","")}</div></div>'
f'<div style="flex:1;min-width:120px;"><div style="font-size:1.0625rem;color:#b8d8ec;text-transform:uppercase;letter-spacing:0.1em;font-weight:700;">Current Status</div>'
f'<div style="font-size:1.0625rem;color:#d0e8f2;margin-top:2px;">{row.get("eradication_status","Established")}</div></div>'
f'</div>'
f'<div style="font-size:1.0625rem;color:#8ec4d8;margin-top:10px;padding-top:8px;border-top:1px solid rgba(134,178,51,0.15);">📚 {src}</div>'
f'</div>', unsafe_allow_html=True)
    else:
        st.info("No projected economic scenarios in current dataset.")

    # ══════════════════════════════════════════════════════════════════════════════
    # THREAT HORIZON  — What's coming next
    # ══════════════════════════════════════════════════════════════════════════════
    section_header("🚨", "Pre-Establishment Threat Profiles",
                   "Species designated as high-priority interception targets by USDA APHIS; not yet confirmed as established in the contiguous US · pathway data and economic exposure figures are pre-arrival modeled estimates")

    threat_df = df[df["eradication_status"].str.contains("Not Yet", na=False)].copy()

    # Augment with known intelligence from USDA APHIS PestLens & EPPO alert list
    # Load threat intel from live policy intelligence JSON
    THREAT_INTEL = _pol.get("threat_intel", {}) or {
        "Wheat Blast": {
            "risk": "CRITICAL", "pathway": "Contaminated seed / wind dispersal",
            "if_established": "$3B-$10B/yr wheat losses (CIMMYT 2022)",
            "source": "Cruz et al. 2016 Science · CIMMYT Wheat Blast Alert",
            "color": "#ef4444"
        },
        "Wheat Stem Rust Ug99": {
            "risk": "CRITICAL", "pathway": "Wind-borne urediniospores from East Africa",
            "if_established": "$1.5B-$3B/yr — affects ~84% of US hard red spring wheat varieties (USDA ARS 2024)",
            "source": "Singh et al. 2008 Science 320:730 · Figueroa et al. 2024 Mol. Plant · BGRI 2024",
            "color": "#ef4444"
        },
    }

    if not threat_df.empty:
        for _, row in threat_df.iterrows():
            name = row["pest_common_name"]
            intel = THREAT_INTEL.get(name, {})
            risk  = intel.get("risk", "MONITORED")
            color = intel.get("color", "#116AAB")
            badge_bg  = {"CRITICAL":"#fef2f2","HIGH":"#fff7ed","MONITORED":"#eff6ff"}.get(risk,"#eff6ff")
            badge_col = {"CRITICAL":"#991b1b","HIGH":"#9a3412","MONITORED":"#1e3a5f"}.get(risk,"#1e3a5f")
            pathway_val = intel.get('pathway', row.get('mode_of_entry','Unknown'))
            impact_val  = intel.get('if_established', row.get('economic_impact_usd','Unknown'))
            host_val    = row.get('host_plant_animal','Unknown')
            origin_val  = row.get('origin_country','Unknown')
            sci_val     = row.get('pest_scientific_name','')
            src_val     = intel.get('source', row.get('data_sources','USDA APHIS'))
            st.markdown(
f'<div style="background:#07334E;border-radius:10px;padding:20px 28px;margin-bottom:10px;border-left:6px solid {color};">'
f'<div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px;">'
f'<div><span style="background:{badge_bg};color:{badge_col};border:1px solid {badge_col}44;border-radius:3px;font-size:1.0625rem;font-weight:700;padding:3px 8px;margin-right:10px;">{risk}</span>'
f'<span style="font-family:Oswald,sans-serif;font-size:1.2rem;font-weight:700;color:#fff;">{name}</span>'
f'<span style="font-style:italic;color:#b8d8ec;font-size:1.125rem;margin-left:10px;">{sci_val}</span></div>'
f'<span style="font-size:1.125rem;color:#EEB638;font-weight:600;">🌍 Origin: {origin_val}</span>'
f'</div>'
f'<div style="display:flex;gap:16px;margin-top:14px;flex-wrap:wrap;">'
f'<div style="flex:1;min-width:140px;"><div style="font-size:1.0625rem;color:#b8d8ec;text-transform:uppercase;letter-spacing:0.1em;font-weight:700;">Entry Pathway</div>'
f'<div style="font-size:1.125rem;color:#d0e8f2;margin-top:3px;">{pathway_val}</div></div>'
f'<div style="flex:1;min-width:140px;"><div style="font-size:1.0625rem;color:#b8d8ec;text-transform:uppercase;letter-spacing:0.1em;font-weight:700;">If Established</div>'
f'<div style="font-size:1.125rem;color:#f87171;font-weight:600;margin-top:3px;">{impact_val}</div></div>'
f'<div style="flex:1;min-width:140px;"><div style="font-size:1.0625rem;color:#b8d8ec;text-transform:uppercase;letter-spacing:0.1em;font-weight:700;">Host / Crop</div>'
f'<div style="font-size:1.125rem;color:#d0e8f2;margin-top:3px;">{host_val}</div></div>'
f'</div>'
f'<div style="font-size:1.0625rem;color:#8ec4d8;margin-top:10px;padding-top:8px;border-top:1px solid rgba(134,178,51,0.15);">📚 {src_val}</div>'
f'</div>', unsafe_allow_html=True)
    else:
        st.info("No 'Not Yet Arrived' records match current filters.")

with tab_detect:
    # ══════════════════════════════════════════════════════════════════════════════
    # ROW 1 — Detection Lag + Origin Breakdown
    # ══════════════════════════════════════════════════════════════════════════════
    section_header("📊", "Detection Lag & Origin Intelligence",
                   "Time elapsed between estimated US arrival and confirmed species detection · disaggregated by organism type, impacted sector, and geographic origin region · lag distributions inform EDRR resource allocation")

    col_a, col_b = st.columns([2.4, 1.6], gap="large")

    with col_a:
        fig_note(
            "Detection Lag by Pest",
            "Horizontal bars show the number of years elapsed between a pest's estimated US arrival and its first confirmed detection. Sorted by lag duration; color indicates pest type.",
            "Years between estimated US arrival and first confirmed US detection — longer = harder to catch"
        )
        lag_df = filtered[["pest_common_name","detection_lag_years","pest_type"]].dropna()
        lag_df = lag_df[lag_df["detection_lag_years"] > 0].sort_values("detection_lag_years", ascending=False)
        if not lag_df.empty:
            lag_df = lag_df.copy()
            import plotly.graph_objects as _go
            color_map    = {t: COLORS[i % len(COLORS)] for i, t in enumerate(lag_df["pest_type"].unique())}
            adj_h        = _CH['large']
            _lag_leg_rows = -(-len(color_map) // 2)
            _lag_leg_b    = _lag_leg_rows * 25 + 56
            row_h         = 40
            height        = adj_h
            fig = _go.Figure()
            for _, r in lag_df.iterrows():
                fig.add_shape(type="line",
                    x0=0, x1=r["detection_lag_years"],
                    y0=r["pest_common_name"], y1=r["pest_common_name"],
                    line=dict(color=color_map.get(r["pest_type"], "#94a3b8"), width=2))
            seen = set()
            for _, r in lag_df.iterrows():
                pt  = r["pest_type"]
                col = color_map.get(pt, "#94a3b8")
                show_leg = pt not in seen
                seen.add(pt)
                fig.add_trace(_go.Scatter(
                    x=[r["detection_lag_years"]],
                    y=[r["pest_common_name"]],
                    mode="markers+text",
                    marker=dict(color=col, size=14, line=dict(color="white", width=1.5)),
                    text=[f"  {int(r['detection_lag_years'])}y" if is_mobile else f"  {int(r['detection_lag_years'])} yrs"],
                    textposition="middle right",
                    textfont=dict(size=9 if is_mobile else 11, color="#1e293b"),
                    cliponaxis=False,
                    name=pt, legendgroup=pt, showlegend=show_leg,
                    hovertemplate=f"<b>{r['pest_common_name']}</b><br>Lag: {int(r['detection_lag_years'])} yrs<br>Type: {pt}<extra></extra>"
                ))
            x_max = lag_df["detection_lag_years"].max()
            _lag_r = 90 if is_mobile else 60
            _lag_b = 20 if is_mobile else _lag_leg_b
            fig.update_layout(
                height=adj_h, showlegend=False,
                margin=dict(l=10, r=_lag_r, t=20, b=_lag_b),
                **BASE
            )
            fig.update_xaxes(showgrid=True, gridcolor="#e2e8f0", gridwidth=1,
                             range=[-0.3, x_max * (1.5 if is_mobile else 1.3)],
                             showticklabels=True, ticks="outside",
                             title_text="Detection Lag (years)", **TICK)
            fig.update_yaxes(showgrid=False, automargin=True,
                             showticklabels=True, **TICK)
            st.plotly_chart(fig, use_container_width=True, config=_PCFG)
            two_col_legend(color_map, pull_up=0 if is_mobile else _lag_leg_b + 16)
        else:
            st.info("No detection lag data for current selection.")

    with col_b:
        fig_note(
            "Pests by Origin Region",
            "Pie chart showing the proportion of tracked invasive species by broad geographic region of origin. Hover any slice to see the species count.",
            "Proportion of invasive species by broad geographic origin — hover a slice for the count"
        )
        region_counts = filtered["origin_region"].value_counts().reset_index()
        region_counts.columns = ["origin_region","count"]
        if not region_counts.empty:
            # Clean region names: strip only parenthetical qualifiers, not "/" separators
            # Then normalize known multi-region strings to a single clean label
            _REGION_MAP = {
                "South/Southeast Asia": "South & SE Asia",
                "South America; South Africa": "S. America / S. Africa",
                "South America; South Asia": "S. America / S. Asia",
                "Southeast Asia": "SE Asia",
                "East Africa": "East Africa",
            }
            region_counts["short_region"] = (
                region_counts["origin_region"]
                .str.split(r"[\(—]").str[0].str.strip()          # remove (parenthetical) and —em-dash suffixes only
                .replace(_REGION_MAP)
            )
            grouped = region_counts.groupby("short_region", as_index=False)["count"].sum()
            grouped = grouped.sort_values("count", ascending=False)

            # Consolidate slices < 4% of total into "Other" to reduce clutter
            total = grouped["count"].sum()
            threshold = max(2, total * 0.04)
            main   = grouped[grouped["count"] >= threshold].copy()
            other_sum = grouped[grouped["count"] < threshold]["count"].sum()
            if other_sum > 0:
                import pandas as _pd
                main = _pd.concat([main, _pd.DataFrame([{"short_region":"Other", "count": other_sum}])],
                                   ignore_index=True)

            # Build legend labels that include the % value
            _total = main["count"].sum()
            legend_labels = [
                f"{r}  ({c/_total*100:.1f}%)"
                for r, c in zip(main["short_region"], main["count"])
            ]
            pull_vals = [0.05] + [0] * (len(main) - 1)
            fig = go.Figure(go.Pie(
                labels=legend_labels,          # legend shows "East Asia  (28.6%)"
                values=main["count"],
                text=main["short_region"],     # inside slice shows short name + auto %
                texttemplate="%{text}<br>%{percent}",
                hole=0.42,
                textposition="inside",
                insidetextorientation="auto",  # allow slanting for tight slices
                textfont=dict(size=11, color="#ffffff", family="Roboto, sans-serif"),
                marker=dict(
                    colors=COLORS[:len(main)],
                    line=dict(color="#ffffff", width=2)
                ),
                pull=pull_vals,
            ))
            fig.update_layout(
                height=_CH['large'], showlegend=True,
                legend=dict(
                    orientation="v", x=1.02, y=0.5, xanchor="left",
                    font=dict(size=11, color="#1e293b"),
                    bgcolor="rgba(0,0,0,0)",
                    title=dict(text="Region", font=dict(size=11, color="#6b7280"))
                ),
                margin=dict(l=10, r=170, t=20, b=20),
                **BASE
            )
            st.plotly_chart(fig, use_container_width=True, config=_PCFG)

    # ══════════════════════════════════════════════════════════════════════════════
    # PEST INTELLIGENCE DATABASE TABLE
    # ══════════════════════════════════════════════════════════════════════════════
    st.markdown('<div class="panel-green">', unsafe_allow_html=True)
    section_header("🗄️", "Pest & Pathogen Intelligence Records",
                   f"Displaying {len(filtered)} of {len(df)} verified species records · sortable by any column · all entries cross-referenced against primary USDA, peer-reviewed, or government regulatory sources")

    display_cols = {
        "pest_common_name":"Pest / Pathogen","record_type":"Record Type","pest_type":"Type",
        "year_first_detected_us":"Year Detected","detection_lag_years":"Lag (yrs)",
        "origin_country":"Origin","mode_of_entry":"Entry Mode",
        "commodity_pathway":"Commodity","host_plant_animal":"Host",
        "inoculum_type":"Inoculum / Transmission","economic_impact_usd":"Economic Impact",
        "impact_sector":"Sector","eradication_status":"Status","quarantine_status":"Quarantine",
    }
    table_df = filtered[list(display_cols.keys())].rename(columns=display_cols).reset_index(drop=True)
    table_df.index = table_df.index + 1
    table_df.index.name = "#"
    st.dataframe(table_df, width="stretch", height=460)
    st.markdown('</div>', unsafe_allow_html=True)

with tab_pathway:
    # ══════════════════════════════════════════════════════════════════════════════
    # ROW 2 — Entry Mode + Temporal Trend
    # ══════════════════════════════════════════════════════════════════════════════
    section_header("🚢", "Introduction Pathway Analysis & Temporal Trends",
                   "Distribution of confirmed US establishments by introduction vector · encompasses commercial trade, natural dispersal, and accidental release pathways · first-detection year data reveal decadal shifts in invasion pressure")

    # ── Pathway normalisation ─────────────────────────────────────────────────────
    def _norm_pathway(raw):
        if not isinstance(raw, str): return "Unknown"
        r = raw.lower()
        if any(k in r for k in ["wind dispersal","airborne","wind-assisted","atmospheric"]):
            return "Natural Dispersal / Wind"
        if any(k in r for k in ["wooden","wood packing","dunnage","timber","firewood","lumber"]):
            return "Solid Wood / Packing Material"
        if any(k in r for k in ["cargo","shipping container","packing material","stone shipment",
                                  "hitchhiker","passenger baggage","accidental"]):
            return "Cargo / Shipping"
        if any(k in r for k in ["nursery","planting material","budwood","transplant","ornamental",
                                  "horticultural","hedge","plant trade","plant material",
                                  "grape","wine","impatiens","boxwood","buxus","crapemyrtle",
                                  "ficus","rhododendron","camellia","hemlock","erythrina"]):
            return "Nursery & Plant Trade"
        if any(k in r for k in ["seed","grain","wheat","potato","corn","fruit import","produce",
                                  "citrus","psyllid","insect vector"]):
            return "Agricultural Produce / Seed"
        if any(k in r for k in ["livestock","wildlife","animal"]):
            return "Livestock / Wildlife"
        return "Unknown"

    def _norm_origin(raw):
        if not isinstance(raw, str): return "Unknown"
        r = raw.lower()
        if any(k in r for k in ["china","japan","korea","taiwan","east asia","mongolia"]):
            return "East Asia"
        if any(k in r for k in ["india","vietnam","indonesia","southeast asia","south asia",
                                  "southeast asian","south/southeast","pacific islands"]):
            return "South / SE Asia"
        if any(k in r for k in ["europe","mediterranean","bulgaria","new zealand","australia",
                                  "southwestern asia"]):
            return "Europe / Pacific"
        if any(k in r for k in ["brazil","latin america","mexico","central america",
                                  "south america","caribbean","andean","argentina","chile"]):
            return "Latin America / Caribbean"
        if any(k in r for k in ["africa","middle east","israel","tanzania","uganda"]):
            return "Africa / Middle East"
        if any(k in r for k in ["north america","canada","western north america","united states"]):
            return "North America"
        return "Unknown"

    col_c, col_d = st.columns(2, gap="large")

    with col_c:
        fig_note(
            "Entry Pathway Distribution",
            "Bars show the number of invasive species grouped by their primary US entry pathway. Categories are normalised from USDA APHIS records to standardised pathway classifications.",
            "Invasive species aggregated by normalised USDA APHIS entry pathway category"
        )
        import pandas as _pd_pw
        pw_df = filtered.copy()
        pw_df["_pathway_cat"] = pw_df["mode_of_entry"].apply(_norm_pathway)
        pw_counts = pw_df["_pathway_cat"].value_counts().reset_index()
        pw_counts.columns = ["pathway","count"]
        pw_counts = pw_counts.sort_values("count", ascending=False)
        if not pw_counts.empty:
            fig = px.treemap(
                pw_counts, path=["pathway"], values="count",
                color="count",
                color_continuous_scale=[[0,"#a8d5f0"],[0.5,"#116AAB"],[1,"#07334E"]],
                labels={"count":"Species Count","pathway":"Pathway"},
            )
            fig.update_traces(
                texttemplate="<b>%{label}</b><br>%{value} species",
                textfont=dict(size=13),
                hovertemplate="<b>%{label}</b><br>%{value} species<extra></extra>"
            )
            fig.update_layout(
                height=_CH['medium'],
                coloraxis_showscale=False,
                margin=dict(l=10, r=10, t=20, b=10),
                **BASE
            )
            st.plotly_chart(fig, use_container_width=True, config=_PCFG)

    with col_d:
        fig_note(
            "Detections by Year",
            "Bar chart of first confirmed US detections by calendar year. Peaks indicate years with elevated numbers of newly identified invasive species arrivals.",
            "Year of first confirmed US detection — peaks show years with multiple new arrivals identified"
        )
        year_counts = filtered["year_first_detected_us"].dropna().astype(int).value_counts().sort_index().reset_index()
        year_counts.columns = ["year","count"]
        if not year_counts.empty:
            # Focus on the 1990-2026 window where most detections occur
            year_counts = year_counts[year_counts["year"] >= 1990]
            fig = px.bar(year_counts, x="year", y="count",
                         text="count",
                         color="count", color_continuous_scale=[[0,"#c8e6c9"],[1,"#2e7d32"]],
                         labels={"year":"Year First Detected","count":"New Detections"})
            fig.update_traces(textposition="outside", textfont=dict(size=11, color="#1e293b"))
            fig.update_layout(
                height=_CH['medium'], showlegend=False, coloraxis_showscale=False,
                margin=dict(l=60, r=20, t=30, b=80),
                **BASE
            )
            fig.update_xaxes(showgrid=False, tickangle=-45, tickmode="linear", dtick=2,
                             range=[1989, year_counts["year"].max() + 1.5], **TICK)
            fig.update_yaxes(showgrid=True, gridcolor="#e2e8f0",
                             title_text="New Detections", **TICK)
            st.plotly_chart(fig, use_container_width=True, config=_PCFG)

    # ══════════════════════════════════════════════════════════════════════════════
    # PATHWAY HOTSPOT
    # ══════════════════════════════════════════════════════════════════════════════
    section_header("🗺️", "Origin–Commodity Risk Matrix",
                   "Cross-tabulation of pest introduction events by geographic origin region and associated commodity vector · identifies highest-priority surveillance targets for USDA APHIS port-of-entry inspection programs")

    import pandas as _pd_hs
    hs_df = filtered.copy()
    hs_df["_origin_cat"]  = hs_df["origin_country"].apply(_norm_origin)
    hs_df["_pathway_cat"] = hs_df["commodity_pathway"].apply(_norm_pathway)
    hs_df = hs_df[hs_df["_origin_cat"] != "Unknown"]

    heat_pivot = (
        hs_df.groupby(["_origin_cat","_pathway_cat"])
        .agg(count=("pest_common_name","count"),
             pests=("pest_common_name", lambda x: "<br>".join(sorted(x))))
        .reset_index()
        .pivot(index="_origin_cat", columns="_pathway_cat", values="count")
        .fillna(0).astype(int)
    )
    heat_hover = (
        hs_df.groupby(["_origin_cat","_pathway_cat"])
        .agg(pests=("pest_common_name", lambda x: "<br>".join(sorted(x))))
        .reset_index()
        .pivot(index="_origin_cat", columns="_pathway_cat", values="pests")
        .fillna("")
    )

    # Order rows by total
    heat_pivot = heat_pivot.loc[heat_pivot.sum(axis=1).sort_values(ascending=True).index]
    heat_hover = heat_hover.reindex(heat_pivot.index)

    if not heat_pivot.empty:
        import plotly.graph_objects as _go_hs
        fig = _go_hs.Figure(data=_go_hs.Heatmap(
            z=heat_pivot.values,
            x=list(heat_pivot.columns),
            y=list(heat_pivot.index),
            colorscale=[[0,"#f0f9ff"],[0.01,"#bae6fd"],[0.4,"#0ea5e9"],[1,"#07334E"]],
            showscale=True,
            colorbar=dict(title=dict(text="Species", font=dict(size=12, color="#1e293b")),
                         tickfont=dict(size=11, color="#1e293b"), thickness=14),
            text=heat_pivot.values,
            texttemplate="%{text}",
            textfont=dict(size=13, color="#1e293b"),
            customdata=heat_hover.values,
            hovertemplate="<b>%{y} × %{x}</b><br>%{z} species:<br>%{customdata}<extra></extra>",
            zmin=0,
        ))
        fig.update_layout(
            height=max(_CH['small'], len(heat_pivot) * _CH['hrow'] + 120),
            margin=dict(l=10, r=100, t=20, b=120),
            xaxis=dict(tickangle=-30, tickfont=dict(size=11, color="#1e293b"),
                       title_text="Entry Commodity Category", title_font=dict(size=12, color="#1e293b")),
            yaxis=dict(tickfont=dict(size=11, color="#1e293b"),
                       title_text="Origin Region", title_font=dict(size=12, color="#1e293b")),
            **BASE
        )
        fig_note(
            "Origin–Commodity Risk Matrix",
            "Heatmap showing the intersection of pest origin region and US entry commodity category. Darker cells indicate more species sharing that origin–pathway combination. Hover any cell for pest names.",
            "Cell values = number of species. Hover for pest names. Origin and commodity normalised from raw CSV entries — raw data available in Biosurveillance & Records."
        )
        st.plotly_chart(fig, use_container_width=True, config=_PCFG)

# ══════════════════════════════════════════════════════════════════════════════
# FOOTER
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="site-footer">
  <div class="footer-brand">PESTTRAIL</div>
  <strong>Data sources:</strong>
  USDA APHIS · USGS US-RIIS · USFS · EDDMapS (UGA) · EPPO Global Database · NISIC · Peer-reviewed literature<br/>
  <strong>Verified:</strong> April 2026 · Cross-checked against USDA APHIS, USFS, Cornell &amp; UGA Extension<br/>
  <strong>Built by</strong>
  <a href="https://www.linkedin.com/in/mary-akinyuwa-700268165/">Mary Akinyuwa</a>
  · Life Scientist &amp; AI Strategist &nbsp;|&nbsp;
  <a href="https://github.com/Mary-Akinyuwa/plantpath-ai">PlantPath AI</a> ·
  <a href="https://github.com/Mary-Akinyuwa/lifescience-servicenow-workflows">LifeScience ServiceNow</a><br/>
  <em style="color:#8ca9bb;font-size:0.78rem;">Data sourced from public USDA, USGS, and peer-reviewed databases. For informational purposes only. Not affiliated with or endorsed by any government agency.</em>
</div>
""", unsafe_allow_html=True)

_analytics_pw = _secret("ANALYTICS_PASSWORD")
streamlit_analytics.stop_tracking(unsafe_password=_analytics_pw)
