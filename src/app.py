
from pathlib import Path

import duckdb
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "cloudpulse.duckdb"

# Earthy palette
BG = "#F7F4EE"
PANEL = "#FFFEFA"
BROWN = "#72513D"
DARK = "#382B23"
MUTED = "#8C8176"
BEIGE = "#E8DFD2"
SAGE = "#89947A"
TERRACOTTA = "#B9785D"
GOLD = "#C5A56B"

st.set_page_config(
    page_title="CloudPulse | Analytics",
    page_icon="◉",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=DM+Serif+Display&display=swap');

:root {{
    --bg: {BG};
    --panel: {PANEL};
    --brown: {BROWN};
    --dark: {DARK};
    --muted: {MUTED};
    --border: {BEIGE};
}}

.stApp {{
    background: var(--bg);
    color: var(--dark);
    font-family: 'DM Sans', sans-serif;
}}

[data-testid="stHeader"] {{
    background: rgba(247,244,238,0.92);
}}

[data-testid="stSidebar"] {{
    background: #EEE7DC;
    border-right: 1px solid {BEIGE};
}}

[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3,
[data-testid="stSidebar"] label {{
    color: {DARK};
}}

h1, h2, h3 {{
    color: {DARK} !important;
    letter-spacing: -0.035em;
}}

h1 {{
    font-family: 'DM Serif Display', Georgia, serif !important;
    font-weight: 400 !important;
    font-size: 2.55rem !important;
}}

h2 {{
    font-size: 1.28rem !important;
    font-weight: 600 !important;
}}

p, label, .stMarkdown {{
    color: {DARK};
}}

[data-testid="stMetric"] {{
    background: {PANEL};
    border: 1px solid {BEIGE};
    border-radius: 14px;
    padding: 19px 20px;
    box-shadow: 0 3px 12px rgba(56,43,35,0.025);
}}

[data-testid="stMetricLabel"] {{
    color: {MUTED};
    font-size: 0.84rem;
}}

[data-testid="stMetricValue"] {{
    color: {DARK};
    font-size: 1.8rem;
    font-weight: 600;
}}

[data-testid="stMetricDelta"] {{
    font-size: 0.8rem;
}}

[data-testid="stPlotlyChart"],
[data-testid="stDataFrame"] {{
    background: {PANEL};
    border: 1px solid {BEIGE};
    border-radius: 14px;
    padding: 8px;
}}

.stButton > button,
.stDownloadButton > button {{
    background: {BROWN};
    color: #FFFEFA;
    border: 1px solid {BROWN};
    border-radius: 9px;
    padding: 0.55rem 1rem;
    font-weight: 600;
}}

.stButton > button:hover,
.stDownloadButton > button:hover {{
    background: {DARK};
    color: white;
    border-color: {DARK};
}}

div[data-baseweb="select"] > div {{
    background: {PANEL};
    border-color: {BEIGE};
    border-radius: 9px;
}}

hr {{
    border-color: {BEIGE};
}}

.eyebrow {{
    color: {BROWN};
    text-transform: uppercase;
    letter-spacing: 0.16em;
    font-size: 0.7rem;
    font-weight: 700;
}}

.subtitle {{
    color: {MUTED};
    font-size: 0.95rem;
    margin-top: -12px;
}}

.section-note {{
    color: {MUTED};
    font-size: 0.84rem;
}}

.brand-mark {{
    background: {BROWN};
    color: #FFFEFA;
    border-radius: 10px;
    display: inline-block;
    padding: 8px 12px;
    font-weight: 700;
    margin-bottom: 10px;
}}

footer {{visibility: hidden;}}
#MainMenu {{visibility: hidden;}}
</style>
""", unsafe_allow_html=True)


def make_chart(fig):
    fig.update_layout(
        paper_bgcolor=PANEL,
        plot_bgcolor=PANEL,
        font=dict(family="DM Sans, sans-serif", color=DARK, size=12),
        margin=dict(l=18, r=18, t=30, b=18),
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="left",
            x=0,
        ),
        xaxis=dict(
            showgrid=False,
            linecolor=BEIGE,
            zeroline=False,
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor="#EEE8DF",
            zeroline=False,
        ),
    )
    return fig


# Sidebar
with st.sidebar:
    st.markdown('<div class="brand-mark">CP / CLOUDPULSE</div>',
                unsafe_allow_html=True)
    st.markdown("### Analytics workspace")
    st.caption("HTTP traffic · Performance · Reliability")
    st.divider()

    st.markdown("**FILTER DATA**")

    if not DB.exists():
        st.error("Database not found. Run `python src/pipeline.py` first.")
        st.stop()

    @st.cache_data
    def load_data():
        con = duckdb.connect(str(DB), read_only=True)
        result = con.execute("SELECT * FROM access_logs").df()
        con.close()
        return result

    df = load_data()

    if df.empty:
        st.warning("No records found in the database.")
        st.stop()

    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    df["server_id"] = pd.to_numeric(df["server_id"], errors="coerce")
    df["status_code"] = pd.to_numeric(df["status_code"], errors="coerce")
    df["response_time_ms"] = pd.to_numeric(
        df["response_time_ms"], errors="coerce"
    )

    df = df.dropna(
        subset=["timestamp", "server_id", "status_code", "response_time_ms"]
    )

    servers = sorted(df["server_id"].unique().tolist())
    statuses = sorted(df["status_class"].dropna().unique().tolist())

    selected_servers = st.multiselect(
        "Servers", servers, default=servers
    )
    selected_statuses = st.multiselect(
        "HTTP status classes", statuses, default=statuses
    )

    st.divider()
    st.caption("DATA SOURCE")
    st.caption("Sample HTTP access logs")
    st.caption("Local DuckDB database")

filtered = df[
    df["server_id"].isin(selected_servers)
    & df["status_class"].isin(selected_statuses)
].copy()

# Header
st.markdown('<div class="eyebrow">OBSERVABILITY / OVERVIEW</div>',
            unsafe_allow_html=True)
st.title("CloudPulse")
st.markdown(
    '<div class="subtitle">A clearer view of your system’s traffic, '
    'performance and reliability.</div>',
    unsafe_allow_html=True,
)
st.write("")

if filtered.empty:
    st.info("No records match your filters. Select more servers or status classes.")
    st.stop()

# KPI cards
total = len(filtered)
errors = int(filtered["status_code"].ge(400).sum())
error_rate = errors / total * 100
avg_latency = filtered["response_time_ms"].mean()
p95_latency = filtered["response_time_ms"].quantile(0.95)

k1, k2, k3, k4 = st.columns(4)
k1.metric("Total requests", f"{total:,}")
k2.metric("HTTP errors", f"{errors:,}", f"{error_rate:.1f}% of requests")
k3.metric("Average latency", f"{avg_latency:,.1f} ms")
k4.metric("95th percentile", f"{p95_latency:,.1f} ms")

st.write("")

# Charts
left, right = st.columns([1.55, 1])

with left:
    st.subheader("Traffic over time")
    st.markdown(
        '<div class="section-note">Request volume by hour</div>',
        unsafe_allow_html=True,
    )

    traffic = (
        filtered.set_index("timestamp")
        .resample("h")
        .size()
        .rename("requests")
        .reset_index()
    )

    fig = px.area(
        traffic,
        x="timestamp",
        y="requests",
        color_discrete_sequence=[BROWN],
    )
    fig.update_traces(
        fillcolor="rgba(114,81,61,0.12)",
        line=dict(width=2.2, color=BROWN),
    )
    st.plotly_chart(make_chart(fig), use_container_width=True)

with right:
    st.subheader("Response distribution")
    st.markdown(
        '<div class="section-note">Share of requests by HTTP status class</div>',
        unsafe_allow_html=True,
    )

    status_counts = (
        filtered.groupby("status_class")
        .size()
        .reset_index(name="requests")
    )

    status_colors = {
        "2xx": SAGE,
        "3xx": GOLD,
        "4xx": TERRACOTTA,
        "5xx": "#8C514A",
    }

    fig = px.pie(
        status_counts,
        names="status_class",
        values="requests",
        hole=0.68,
        color="status_class",
        color_discrete_map=status_colors,
    )
    fig.update_traces(
        textposition="inside",
        textinfo="percent",
        marker=dict(line=dict(color=PANEL, width=3)),
    )
    st.plotly_chart(make_chart(fig), use_container_width=True)

# Endpoint analytics
st.write("")
st.subheader("Endpoint performance")
st.markdown(
    '<div class="section-note">Ranked by 95th-percentile response time</div>',
    unsafe_allow_html=True,
)

endpoint_stats = (
    filtered.groupby("path", as_index=False)
    .agg(
        requests=("path", "size"),
        avg_latency_ms=("response_time_ms", "mean"),
        p95_latency_ms=(
            "response_time_ms",
            lambda s: s.quantile(0.95),
        ),
        errors=("status_code", lambda s: int((s >= 400).sum())),
    )
    .sort_values("p95_latency_ms", ascending=False)
    .head(10)
)

endpoint_stats["avg_latency_ms"] = endpoint_stats["avg_latency_ms"].round(1)
endpoint_stats["p95_latency_ms"] = endpoint_stats["p95_latency_ms"].round(1)
endpoint_stats["error_rate_pct"] = (
    endpoint_stats["errors"] / endpoint_stats["requests"] * 100
).round(1)

st.dataframe(
    endpoint_stats,
    use_container_width=True,
    hide_index=True,
    column_config={
        "path": st.column_config.TextColumn("Endpoint"),
        "requests": st.column_config.NumberColumn("Requests", format="%d"),
        "avg_latency_ms": st.column_config.NumberColumn(
            "Avg latency", format="%.1f ms"
        ),
        "p95_latency_ms": st.column_config.NumberColumn(
            "P95 latency", format="%.1f ms"
        ),
        "errors": st.column_config.NumberColumn("Errors", format="%d"),
        "error_rate_pct": st.column_config.NumberColumn(
            "Error rate", format="%.1f%%"
        ),
    },
)

# Server health
st.write("")
st.subheader("Server health")

server_stats = (
    filtered.groupby("server_id", as_index=False)
    .agg(
        requests=("status_code", "size"),
        errors=("status_code", lambda s: int((s >= 400).sum())),
        avg_latency_ms=("response_time_ms", "mean"),
    )
)
server_stats["error_rate_pct"] = (
    server_stats["errors"] / server_stats["requests"] * 100
).round(2)
server_stats["avg_latency_ms"] = server_stats["avg_latency_ms"].round(1)

st.dataframe(
    server_stats,
    use_container_width=True,
    hide_index=True,
    column_config={
        "server_id": "Server ID",
        "requests": st.column_config.NumberColumn("Requests", format="%d"),
        "errors": st.column_config.NumberColumn("Errors", format="%d"),
        "avg_latency_ms": st.column_config.NumberColumn(
            "Average latency", format="%.1f ms"
        ),
        "error_rate_pct": st.column_config.NumberColumn(
            "Error rate", format="%.2f%%"
        ),
    },
)

# Export and footer
st.write("")
download_col, info_col = st.columns([1, 2])

with download_col:
    st.download_button(
        "↓  Export filtered data",
        data=filtered.to_csv(index=False).encode("utf-8"),
        file_name="cloudpulse_filtered_logs.csv",
        mime="text/csv",
        use_container_width=True,
    )

with info_col:
    st.caption(
        "All metrics reflect the included sample logs and current filters. "
        "This is not a live production monitoring system."
    )

st.divider()
st.caption("CLOUDPULSE  /  DATA ENGINEERING & ANALYTICS")
