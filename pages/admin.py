import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / ".env")

st.set_page_config(
    page_title="PestTrail Admin",
    page_icon="🔒",
    layout="wide"
)

DB_PATH = Path(__file__).parent.parent / "analytics" / "visits.db"

# --- Auth gate ---
st.title("🔒 PestTrail Admin")
st.caption("Visitor analytics — private access only")

admin_pw = os.getenv("ADMIN_PASSWORD", "changeme")

if "admin_authenticated" not in st.session_state:
    st.session_state.admin_authenticated = False

if not st.session_state.admin_authenticated:
    pw = st.text_input("Enter admin password", type="password")
    if st.button("Login"):
        if pw == admin_pw:
            st.session_state.admin_authenticated = True
            st.rerun()
        else:
            st.error("Incorrect password.")
    st.stop()

# --- GA4 IP capture diagnostic (shows what IP is being sent to GA4 for your own session) ---
_dbg_ip = st.session_state.get("_dbg_ip_header", "(visit main page first)")
st.info(f"🔍 **GA4 IP sent for your session:** `{_dbg_ip}` — if this shows a real IP (not blank/not-captured), geo tracking is working.")

# --- Load analytics data ---
def load_visits():
    if not DB_PATH.exists():
        return pd.DataFrame()
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM visits ORDER BY timestamp DESC", conn)
    conn.close()
    return df

df = load_visits()

if df.empty:
    st.info("No visit data recorded yet. Data will appear here once visitors use the main dashboard.")
    st.stop()

df["timestamp"] = pd.to_datetime(df["timestamp"])
df["date"] = df["timestamp"].dt.date

# --- KPIs ---
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Visits", len(df))
col2.metric("Unique Sessions", df["session_id"].nunique())
col3.metric("Days with Activity", df["date"].nunique())
first_visit = df["timestamp"].min().strftime("%b %d, %Y")
col4.metric("First Visit Recorded", first_visit)

st.markdown("---")

# --- Daily visits chart ---
col_a, col_b = st.columns(2)

with col_a:
    st.subheader("Daily Visits")
    daily = df.groupby("date").size().reset_index(name="visits")
    daily["date"] = pd.to_datetime(daily["date"])
    fig_daily = px.bar(daily, x="date", y="visits", color="visits",
                       color_continuous_scale="Greens",
                       labels={"date": "Date", "visits": "Visits"})
    fig_daily.update_layout(height=320, margin=dict(l=0, r=0, t=20, b=0), showlegend=False)
    fig_daily.update_xaxes(tickformat="%b %d", dtick="D1")
    st.plotly_chart(fig_daily, use_container_width=True)

with col_b:
    st.subheader("Top Search Terms")
    searches = df[df["search_term"].notna() & (df["search_term"].str.strip() != "")]
    if not searches.empty:
        top_searches = searches["search_term"].str.lower().value_counts().head(15).reset_index()
        top_searches.columns = ["search_term", "count"]
        fig_s = px.bar(top_searches, x="count", y="search_term", orientation="h",
                       color="count", color_continuous_scale="Blues",
                       labels={"count": "Searches", "search_term": "Term"})
        fig_s.update_layout(height=320, margin=dict(l=0, r=0, t=20, b=0), showlegend=False)
        st.plotly_chart(fig_s, use_container_width=True)
    else:
        st.info("No search terms recorded yet.")

st.markdown("---")

# --- Top filters used ---
st.subheader("Filters Used by Visitors")
filter_cols = ["filter_pest_type", "filter_origin_region", "filter_entry_mode", "filter_impact_sector"]
filter_data = []
for col in filter_cols:
    if col in df.columns:
        vals = df[df[col].notna() & (df[col] != "All") & (df[col].str.strip() != "")][col].value_counts().head(5)
        for val, cnt in vals.items():
            filter_data.append({"filter": col.replace("filter_", "").replace("_", " ").title(), "value": val, "count": cnt})

if filter_data:
    fdf = pd.DataFrame(filter_data)
    fig_f = px.bar(fdf, x="count", y="value", color="filter", orientation="h",
                   color_discrete_sequence=px.colors.qualitative.Safe,
                   labels={"count": "Times Used", "value": "Filter Value"})
    fig_f.update_layout(height=350, margin=dict(l=0, r=0, t=20, b=0))
    st.plotly_chart(fig_f, use_container_width=True)

st.markdown("---")

# --- Raw log + export ---
st.subheader("Full Visit Log")
st.caption(f"{len(df)} records")
st.dataframe(df, use_container_width=True, height=350)

csv_export = df.to_csv(index=False).encode("utf-8")
st.download_button(
    "⬇️ Export Full Log as CSV",
    data=csv_export,
    file_name="pesttrail_visits_export.csv",
    mime="text/csv"
)

st.markdown("---")
if st.button("🔓 Logout"):
    st.session_state.admin_authenticated = False
    st.rerun()
