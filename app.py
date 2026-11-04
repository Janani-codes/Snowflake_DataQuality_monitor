import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# Set to True to run without a Snowflake connection
DEMO_MODE = True

# Snowflake libraries and config are only needed when DEMO_MODE is False
try:
    import snowflake.connector
    from config import SNOWFLAKE_CONFIG
except ImportError:
    if not DEMO_MODE:
        raise


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Snowflake DQ Monitor v2.0",
    page_icon="❄️",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# DESIGN TOKENS
# ============================================================

INK = "#0B2239"        # deep glacier navy: sidebar, headings
ICE = "#EDF3F9"        # page background
SURFACE = "#FFFFFF"    # cards
LINE = "#DCE6F0"       # borders and gridlines
MUTED = "#5F7690"      # secondary text
ACCENT = "#1B9AD6"     # snowflake cyan
PASS_C = "#139A68"
FAIL_C = "#E0443E"
WARN_C = "#E59A12"


# ============================================================
# PROFESSIONAL UI STYLING
# ============================================================

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@500;600;700&family=Figtree:wght@400;500;600;700&display=swap');
:root {{
    --ink: {INK}; --ice: {ICE}; --surface: {SURFACE}; --line: {LINE};
    --muted: {MUTED}; --accent: {ACCENT};
    --pass: {PASS_C}; --fail: {FAIL_C}; --warn: {WARN_C};
    --bar-a: #3CC796; --bar-b: {PASS_C};
}}
html, body, [class*="css"], [data-testid="stAppViewContainer"] {{
    font-family: 'Figtree', 'Segoe UI', system-ui, sans-serif;
    color: var(--ink);
}}
[data-testid="stAppViewContainer"] {{
    background:
        radial-gradient(1100px 460px at 88% -140px, rgba(27,154,214,0.18), transparent 70%),
        radial-gradient(700px 400px at -5% 40%, rgba(27,154,214,0.07), transparent 70%),
        var(--ice);
}}
[data-testid="stHeader"] {{ background: transparent; }}
#MainMenu, footer {{ visibility: hidden; }}
.block-container {{
    padding-top: 2rem;
    padding-bottom: 3rem;
    max-width: 1280px;
}}

/* Headings */
h1, h2, h3, h4 {{
    font-family: 'Sora', 'Figtree', sans-serif !important;
    color: var(--ink);
    letter-spacing: -0.02em;
}}
h2, h3 {{ font-weight: 600 !important; }}
h3 {{ font-size: 1.35rem !important; margin-top: 0.4rem; }}
h4 {{ font-size: 1.02rem !important; font-weight: 600 !important; }}
hr {{
    border: none !important;
    height: 1px !important;
    background: linear-gradient(90deg, var(--line), transparent) !important;
    margin: 2.1rem 0 1.4rem 0 !important;
}}

/* Hero (the one entrance animation on the page) */
.hero {{
    background:
        radial-gradient(520px 260px at 100% 0%, rgba(77,196,255,0.35), transparent 70%),
        linear-gradient(120deg, #0B2239 0%, #123A5E 55%, #1B6FA8 100%);
    border-radius: 24px;
    padding: 38px 42px 34px 42px;
    margin-bottom: 1.5rem;
    position: relative;
    overflow: hidden;
    box-shadow: 0 24px 48px -26px rgba(11,34,57,0.75);
    animation: heroIn 0.7s cubic-bezier(.2,.7,.2,1) both;
}}
@keyframes heroIn {{
    from {{ opacity: 0; transform: translateY(14px); }}
    to   {{ opacity: 1; transform: translateY(0); }}
}}
.hero::after {{
    content: "❄";
    position: absolute;
    right: 30px; top: -40px;
    font-size: 14rem;
    color: rgba(255,255,255,0.07);
    line-height: 1;
}}
.hero h1 {{
    color: #fff !important;
    font-size: 2.45rem !important;
    font-weight: 700 !important;
    margin: 0 0 8px 0 !important;
    padding: 0 !important;
    position: relative;
    z-index: 1;
}}
.hero p {{
    color: #B7CCE0;
    font-size: 1.04rem;
    margin: 0 0 20px 0;
    max-width: 620px;
    position: relative;
    z-index: 1;
}}
.pill {{
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: rgba(255,255,255,0.12);
    border: 1px solid rgba(255,255,255,0.24);
    color: #fff;
    padding: 8px 18px;
    border-radius: 999px;
    font-size: 0.88rem;
    font-weight: 500;
    backdrop-filter: blur(6px);
    position: relative;
    z-index: 1;
}}

/* KPI cards */
.kpi {{
    background: var(--surface);
    border: 1px solid var(--line);
    border-radius: 20px;
    padding: 20px 22px 18px 26px;
    box-shadow: 0 14px 28px -20px rgba(11,34,57,0.5);
    position: relative;
    overflow: hidden;
    height: 100%;
}}
.kpi::before {{
    content: "";
    position: absolute;
    left: 0; top: 0; bottom: 0;
    width: 6px;
    background: var(--tone, var(--accent));
}}
.kpi::after {{
    content: "";
    position: absolute;
    right: -30px; top: -30px;
    width: 110px; height: 110px;
    border-radius: 50%;
    background: var(--tone, var(--accent));
    opacity: 0.08;
}}
.kpi-label {{
    color: var(--muted);
    font-size: 0.92rem;
    font-weight: 600;
}}
.kpi-value {{
    font-family: 'Sora', sans-serif;
    font-size: 2.45rem;
    font-weight: 700;
    line-height: 1.15;
    margin-top: 6px;
    color: var(--tone, var(--ink));
    letter-spacing: -0.03em;
}}
.kpi-sub {{
    color: var(--muted);
    font-size: 0.84rem;
    margin-top: 4px;
}}

/* Callouts */
.callout {{
    border-radius: 14px;
    padding: 15px 20px;
    font-size: 0.98rem;
    font-weight: 500;
    border: 1px solid;
    margin: 0.35rem 0 0.9rem 0;
}}
.callout.ok   {{ background: #E6F6EF; border-color: #BCE5D3; color: #0B6B47; }}
.callout.warn {{ background: #FFF4DC; border-color: #F5DDA4; color: #8A5A00; }}
.callout.bad  {{ background: #FDE9E8; border-color: #F5C2BF; color: #A32621; }}
.callout.info {{ background: #E4F3FB; border-color: #BADFF2; color: #0E5E87; }}
.action {{
    background: var(--surface);
    border: 1px solid var(--line);
    border-left: 4px solid var(--accent);
    border-radius: 10px;
    padding: 11px 16px;
    margin-bottom: 8px;
    font-size: 0.96rem;
}}
.scale {{
    display: flex;
    gap: 14px;
    flex-wrap: wrap;
    font-size: 0.82rem;
    color: var(--muted);
    margin-top: 10px;
}}
.scale span::before {{
    content: "";
    display: inline-block;
    width: 9px; height: 9px;
    border-radius: 50%;
    margin-right: 6px;
    background: var(--dot);
}}

/* Progress bar */
[data-testid="stProgress"] > div > div {{
    background-color: #D5E2EE;
    height: 14px;
    border-radius: 999px;
}}
[data-testid="stProgress"] > div > div > div > div {{
    background: linear-gradient(90deg, var(--bar-a), var(--bar-b));
    border-radius: 999px;
}}

/* Bordered containers act as cards */
[data-testid="stVerticalBlockBorderWrapper"] {{
    background: var(--surface);
    border: 1px solid var(--line) !important;
    border-radius: 20px !important;
    box-shadow: 0 14px 28px -22px rgba(11,34,57,0.55);
    padding: 8px 10px;
}}

/* Data tables */
[data-testid="stDataFrame"] {{
    border: 1px solid var(--line);
    border-radius: 12px;
    overflow: hidden;
}}

/* Download button */
[data-testid="stDownloadButton"] button {{
    background: var(--ink);
    color: #fff;
    border: none;
    border-radius: 12px;
    padding: 0.65rem 1.4rem;
    font-weight: 600;
    transition: background 0.15s ease, transform 0.15s ease;
}}
[data-testid="stDownloadButton"] button:hover {{
    background: var(--accent);
    color: #fff;
    transform: translateY(-1px);
}}
[data-testid="stDownloadButton"] button:focus-visible,
[data-testid="stSidebar"] .stButton button:focus-visible {{
    outline: 3px solid rgba(27,154,214,0.5);
    outline-offset: 2px;
}}

/* Sidebar */
[data-testid="stSidebar"] {{
    background: linear-gradient(180deg, #0B2239 0%, #0F3050 100%);
    border-right: none;
}}
[data-testid="stSidebar"] * {{ color: #D6E4F2; }}
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {{ color: #fff !important; }}
[data-testid="stSidebar"] [data-testid="stCaptionContainer"] * {{ color: #8FB0CC; }}
[data-testid="stSidebar"] hr {{ background: rgba(255,255,255,0.14) !important; }}
[data-testid="stSidebar"] label p {{
    font-weight: 600;
    color: #B7CCE0;
}}
[data-testid="stSidebar"] .stButton button {{
    background: var(--accent);
    color: #fff;
    border: none;
    border-radius: 12px;
    font-weight: 600;
    padding: 0.6rem 1rem;
    transition: filter 0.15s ease, transform 0.15s ease;
}}
[data-testid="stSidebar"] .stButton button:hover {{
    filter: brightness(1.1);
    transform: translateY(-1px);
}}
[data-testid="stSidebar"] [data-baseweb="select"] > div,
[data-testid="stSidebar"] [data-baseweb="input"] > div,
[data-testid="stSidebar"] [data-baseweb="base-input"] {{
    background: rgba(255,255,255,0.08) !important;
    border: 1px solid rgba(255,255,255,0.16) !important;
    border-radius: 10px !important;
}}
[data-testid="stSidebar"] input {{
    color: #fff !important;
    -webkit-text-fill-color: #fff !important;
}}
[data-testid="stSidebar"] input::placeholder {{ color: #7F9DB8 !important; }}
[data-testid="stSidebar"] span[data-baseweb="tag"] {{
    background: var(--accent) !important;
    border-radius: 8px !important;
}}
[data-testid="stSidebar"] span[data-baseweb="tag"] * {{ color: #fff !important; }}

/* Footer */
.footer {{
    text-align: center;
    color: #8AA0B6;
    font-size: 0.82rem;
    padding: 34px 0 10px 0;
}}

@media (max-width: 768px) {{
    .hero {{ padding: 26px 22px; }}
    .hero h1 {{ font-size: 1.7rem !important; }}
    .kpi-value {{ font-size: 1.95rem; }}
}}
@media (prefers-reduced-motion: reduce) {{
    .hero {{ animation: none; }}
}}
</style>
""", unsafe_allow_html=True)


# ============================================================
# UI HELPERS
# ============================================================

def callout(kind: str, text: str):
    """Styled message box. kind: ok | warn | bad | info"""
    st.markdown(
        f'<div class="callout {kind}">{text}</div>',
        unsafe_allow_html=True
    )


def kpi_card(label: str, value, tone: str = INK, sub: str = ""):
    sub_html = f'<div class="kpi-sub">{sub}</div>' if sub else ""
    st.markdown(
        f'<div class="kpi" style="--tone:{tone}">'
        f'<div class="kpi-label">{label}</div>'
        f'<div class="kpi-value">{value}</div>'
        f'{sub_html}'
        f'</div>',
        unsafe_allow_html=True
    )


PLOT_FONT = dict(
    family="Figtree, Segoe UI, sans-serif",
    size=13,
    color=INK
)


def style_figure(fig, height=370):
    """Shared Plotly look so every chart feels like one system."""
    fig.update_layout(
        height=height,
        margin=dict(l=10, r=40, t=10, b=20),
        showlegend=False,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=PLOT_FONT,
        bargap=0.38,
        hoverlabel=dict(
            bgcolor=INK,
            font_color="white",
            font_family="Figtree, sans-serif"
        ),
    )
    fig.update_xaxes(
        gridcolor=LINE,
        zeroline=False,
        showline=False,
        title_font=dict(color=MUTED, size=12),
        tickfont=dict(color=MUTED)
    )
    fig.update_yaxes(
        showgrid=False,
        showline=False,
        tickfont=dict(color=INK, size=13)
    )
    return fig


PLOT_CONFIG = {"displayModeBar": False}


# ============================================================
# SNOWFLAKE CONNECTION
# ============================================================

def get_connection():
    """
    Creates and returns a connection to Snowflake.
    """
    return snowflake.connector.connect(
        account=SNOWFLAKE_CONFIG["account"],
        user=SNOWFLAKE_CONFIG["user"],
        password=SNOWFLAKE_CONFIG["password"],
        warehouse=SNOWFLAKE_CONFIG["warehouse"],
        database=SNOWFLAKE_CONFIG["database"],
        schema=SNOWFLAKE_CONFIG["schema"]
    )


# ============================================================
# LOAD DATA
# ============================================================

@st.cache_data(ttl=60)
def load_data():

    if DEMO_MODE:
        return pd.DataFrame({
            "CHECK_NAME": [
                "Null Check",
                "Duplicate Check",
                "Range Check",
                "Freshness Check",
                "Null Check",
                "Duplicate Check",
                "Range Check",
                "Freshness Check"
            ],
            "TABLE_NAME": [
                "RAW_ORDERS",
                "RAW_ORDERS",
                "RAW_ORDERS",
                "RAW_ORDERS",
                "RAW_ORDERS",
                "RAW_ORDERS",
                "RAW_ORDERS",
                "RAW_ORDERS"
            ],
            "COLUMN_NAME": [
                "CUSTOMER_ID",
                "ORDER_ID",
                "AMOUNT",
                "ORDER_DATE",
                "PRODUCT_ID",
                "ORDER_ID",
                "QUANTITY",
                "ORDER_DATE"
            ],
            "STATUS": [
                "PASS",
                "FAIL",
                "PASS",
                "FAIL",
                "PASS",
                "PASS",
                "FAIL",
                "PASS"
            ],
            "FAILED_COUNT": [
                0, 12, 0, 5, 0, 0, 8, 0
            ],
            "FAILED_PERCENTAGE": [
                0, 2.4, 0, 1.0, 0, 0, 1.6, 0
            ],
            "RUN_TIMESTAMP": pd.to_datetime([
                "2026-10-17 09:00:00",
                "2026-10-17 09:00:00",
                "2026-10-17 09:00:00",
                "2026-10-17 09:00:00",
                "2026-10-16 09:00:00",
                "2026-10-16 09:00:00",
                "2026-10-16 09:00:00",
                "2026-10-16 09:00:00"
            ])
        })

    conn = get_connection()

    try:
        df = pd.read_sql(
            "SELECT * FROM DQ_RESULTS ORDER BY RUN_TIMESTAMP DESC",
            conn
        )
        return df
    finally:
        conn.close()


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title("❄️ Snowflake DQ")
st.sidebar.caption("Data Quality Monitor")

if st.sidebar.button(
    "🔄 Refresh Dashboard",
    use_container_width=True
):
    st.cache_data.clear()
    st.rerun()

st.sidebar.divider()

st.sidebar.subheader("🔎 Filters")


# ============================================================
# LOAD SNOWFLAKE DATA
# ============================================================

try:

    df = load_data()

except Exception as e:

    callout("bad", "Unable to connect to Snowflake.")

    st.code(str(e))

    st.stop()


# ============================================================
# EMPTY DATA CHECK
# ============================================================

if df.empty:

    st.markdown(
        '<div class="hero"><h1>❄️ Snowflake Data Quality Monitor</h1></div>',
        unsafe_allow_html=True
    )
    if DEMO_MODE:
        callout(
            "info",
            "DEMO MODE: Displaying sample data. "
            "Snowflake is not connected."
        )

    callout(
        "info",
        "No Data Quality results are available yet. "
        "Run dq_checks.py first."
    )

    st.stop()


# ============================================================
# FILTERS
# ============================================================

check_types = sorted(
    df["CHECK_NAME"].dropna().unique().tolist()
)

selected_checks = st.sidebar.multiselect(
    "Check Types",
    options=check_types,
    default=check_types
)


status_types = sorted(
    df["STATUS"].dropna().unique().tolist()
)

selected_status = st.sidebar.multiselect(
    "Status",
    options=status_types,
    default=status_types
)


search_text = st.sidebar.text_input(
    "Search Check",
    placeholder="Example: NULL CHECK"
)


# ============================================================
# APPLY FILTERS
# ============================================================

filtered_df = df.copy()

filtered_df = filtered_df[
    filtered_df["CHECK_NAME"].isin(selected_checks)
]

filtered_df = filtered_df[
    filtered_df["STATUS"].isin(selected_status)
]

if search_text:

    filtered_df = filtered_df[
        filtered_df["CHECK_NAME"]
        .astype(str)
        .str.contains(
            search_text,
            case=False,
            na=False
        )
    ]


# ============================================================
# NO FILTER RESULTS
# ============================================================

if filtered_df.empty:

    callout(
        "warn",
        "No records match the selected filters."
    )

    st.stop()


# ============================================================
# LAST UPDATED
# ============================================================

latest_timestamp = filtered_df["RUN_TIMESTAMP"].max()

try:

    latest_time = pd.to_datetime(
        latest_timestamp
    ).strftime(
        "%d %b %Y • %I:%M %p"
    )

except Exception:

    latest_time = datetime.now().strftime(
        "%d %b %Y • %I:%M %p"
    )


# ============================================================
# HEADER
# ============================================================

st.markdown(
    f"""
<div class="hero">
<h1>❄️ Snowflake Data Quality Monitor</h1>
<p>Real-time monitoring of data quality checks executed against Snowflake.</p>
<span class="pill">🟢 Monitoring Active &nbsp;•&nbsp; Last DQ result: {latest_time}</span>
</div>
""",
    unsafe_allow_html=True
)


# ============================================================
# KPI CALCULATIONS
# ============================================================

total_checks = len(filtered_df)

passed_checks = len(
    filtered_df[
        filtered_df["STATUS"] == "PASS"
    ]
)

failed_checks = len(
    filtered_df[
        filtered_df["STATUS"] == "FAIL"
    ]
)

health_score = (
    round(
        (passed_checks / total_checks) * 100,
        2
    )
    if total_checks > 0
    else 0
)

if health_score >= 90:
    health_tone, bar_a, bar_b = PASS_C, "#3CC796", PASS_C
elif health_score >= 70:
    health_tone, bar_a, bar_b = WARN_C, "#F4C259", WARN_C
else:
    health_tone, bar_a, bar_b = FAIL_C, "#F28782", FAIL_C

# Progress bar colour follows the health status
st.markdown(
    f"<style>:root {{ --bar-a: {bar_a}; --bar-b: {bar_b}; }}</style>",
    unsafe_allow_html=True
)

pass_share = round(passed_checks / total_checks * 100, 1)
fail_share = round(failed_checks / total_checks * 100, 1)

if "TABLE_NAME" in filtered_df.columns:
    n_tables = filtered_df["TABLE_NAME"].nunique()
    total_sub = f"across {n_tables} table{'s' if n_tables != 1 else ''}"
else:
    total_sub = ""


# ============================================================
# KPI CARDS
# ============================================================

k1, k2, k3, k4 = st.columns(4, gap="medium")

with k1:

    kpi_card("📋 Total Checks", total_checks, ACCENT, total_sub)

with k2:

    kpi_card("✅ Passed", passed_checks, PASS_C, f"{pass_share}% of checks")

with k3:

    kpi_card("❌ Failed", failed_checks, FAIL_C, f"{fail_share}% of checks")

with k4:

    kpi_card("💯 Health Score", f"{health_score}%", health_tone, "Target: 90% or higher")


# ============================================================
# HEALTH STATUS
# ============================================================

st.markdown("---")

st.subheader("Overall Data Health")

gauge_col, status_col = st.columns([1, 1.5], gap="large")

with gauge_col:

    with st.container(border=True):

        fig_gauge = go.Figure(
            go.Indicator(
                mode="gauge+number",
                value=health_score,
                number=dict(
                    suffix="%",
                    font=dict(
                        family="Sora, sans-serif",
                        size=44,
                        color=health_tone
                    )
                ),
                gauge=dict(
                    axis=dict(
                        range=[0, 100],
                        tickvals=[0, 70, 90, 100],
                        tickfont=dict(color=MUTED, size=11),
                        tickwidth=0
                    ),
                    bar=dict(color=health_tone, thickness=0.3),
                    bgcolor="rgba(0,0,0,0)",
                    borderwidth=0,
                    steps=[
                        dict(range=[0, 70], color="#FBE3E1"),
                        dict(range=[70, 90], color="#FCEFCF"),
                        dict(range=[90, 100], color="#D5F0E4"),
                    ],
                )
            )
        )

        fig_gauge.update_layout(
            height=250,
            margin=dict(l=25, r=25, t=30, b=5),
            paper_bgcolor="rgba(0,0,0,0)",
            font=PLOT_FONT
        )

        st.plotly_chart(
            fig_gauge,
            use_container_width=True,
            config=PLOT_CONFIG
        )

with status_col:

    with st.container(border=True):

        if health_score >= 90:

            callout(
                "ok",
                "🟢 Excellent — data quality is healthy."
            )

        elif health_score >= 70:

            callout(
                "warn",
                "🟡 Attention Required — some checks are failing."
            )

        else:

            callout(
                "bad",
                "🔴 Critical — significant data quality issues detected."
            )

        st.progress(
            health_score / 100
        )

        st.markdown(
            f'<div class="scale">'
            f'<span style="--dot:{FAIL_C}">Below 70%</span>'
            f'<span style="--dot:{WARN_C}">70% to 89%</span>'
            f'<span style="--dot:{PASS_C}">90% and above</span>'
            f'</div>',
            unsafe_allow_html=True
        )


# ============================================================
# ANALYTICS
# ============================================================

st.markdown("---")

st.subheader("📊 Data Quality Overview")

left, right = st.columns(2, gap="large")


# ============================================================
# FAILED RECORDS BY CHECK
# ============================================================

with left:

    with st.container(border=True):

        st.markdown("#### Failed Records by Check")

        failed_chart = (
            filtered_df
            .groupby(
                "CHECK_NAME",
                as_index=False
            )["FAILED_COUNT"]
            .sum()
            .sort_values(
                "FAILED_COUNT",
                ascending=True
            )
        )

        fig_bar = px.bar(
            failed_chart,
            x="FAILED_COUNT",
            y="CHECK_NAME",
            orientation="h",
            text="FAILED_COUNT"
        )

        fig_bar.update_traces(
            marker_color=FAIL_C,
            textposition="outside",
            textfont=dict(color=INK, size=13),
            cliponaxis=False,
            hovertemplate="<b>%{y}</b><br>%{x} failed records<extra></extra>"
        )

        fig_bar = style_figure(fig_bar, height=340)

        fig_bar.update_layout(
            xaxis_title="Failed Records",
            yaxis_title=""
        )

        st.plotly_chart(
            fig_bar,
            use_container_width=True,
            config=PLOT_CONFIG
        )


# ============================================================
# PASS VS FAIL
# ============================================================

with right:

    with st.container(border=True):

        st.markdown("#### Check Status")

        status_chart = (
            filtered_df["STATUS"]
            .value_counts()
            .reindex(
                ["PASS", "FAIL"],
                fill_value=0
            )
            .reset_index()
        )

        status_chart.columns = [
            "STATUS",
            "COUNT"
        ]

        fig_status = px.pie(
            status_chart,
            names="STATUS",
            values="COUNT",
            hole=0.68,
            color="STATUS",
            color_discrete_map={
                "PASS": PASS_C,
                "FAIL": FAIL_C
            }
        )

        fig_status.update_traces(
            textinfo="value",
            textfont=dict(color="white", size=14),
            marker=dict(line=dict(color="white", width=3)),
            sort=False,
            hovertemplate="<b>%{label}</b><br>%{value} checks (%{percent})<extra></extra>"
        )

        fig_status.update_layout(
            height=340,
            margin=dict(l=10, r=10, t=10, b=10),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=PLOT_FONT,
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.05,
                xanchor="center",
                x=0.5
            ),
            hoverlabel=dict(
                bgcolor=INK,
                font_color="white",
                font_family="Figtree, sans-serif"
            ),
            annotations=[
                dict(
                    text=f"<b>{total_checks}</b><br>Number of Checks",
                    x=0.5,
                    y=0.5,
                    showarrow=False,
                    font=dict(size=15, color=INK)
                )
            ]
        )

        st.plotly_chart(
            fig_status,
            use_container_width=True,
            config=PLOT_CONFIG
        )


# ============================================================
# FAILED RECORDS OVER TIME
# ============================================================

with st.container(border=True):

    st.markdown("#### Failed Records Over Time")

    trend = (
        filtered_df
        .assign(
            RUN_DATE=pd.to_datetime(
                filtered_df["RUN_TIMESTAMP"]
            ).dt.normalize()
        )
        .groupby("RUN_DATE", as_index=False)["FAILED_COUNT"]
        .sum()
        .sort_values("RUN_DATE")
    )

    trend["LABEL"] = trend["RUN_DATE"].dt.strftime("%d %b")

    fig_trend = go.Figure(
        go.Scatter(
            x=trend["LABEL"],
            y=trend["FAILED_COUNT"],
            mode="lines+markers+text",
            text=trend["FAILED_COUNT"],
            textposition="top center",
            line=dict(color=FAIL_C, width=3, shape="spline"),
            marker=dict(
                size=10,
                color="white",
                line=dict(color=FAIL_C, width=3)
            ),
            fill="tozeroy",
            fillcolor="rgba(224,68,62,0.10)",
            hovertemplate="<b>%{x}</b><br>%{y} failed records<extra></extra>"
        )
    )

    fig_trend = style_figure(fig_trend, height=260)

    fig_trend.update_layout(
        margin=dict(l=10, r=20, t=25, b=20),
        xaxis_title="Run Date",
        yaxis_title="Failed Records"
    )

    fig_trend.update_yaxes(
        gridcolor=LINE,
        rangemode="tozero"
    )

    fig_trend.update_xaxes(
        showgrid=False,
        type="category"
    )

    st.plotly_chart(
        fig_trend,
        use_container_width=True,
        config=PLOT_CONFIG
    )


# ============================================================
# TOP DATA QUALITY ISSUES
# ============================================================

st.markdown("---")

st.subheader("🚨 Top Data Quality Issues")

failed_data = filtered_df[
    filtered_df["STATUS"] == "FAIL"
].copy()


if failed_data.empty:

    callout(
        "ok",
        "✅ No failed checks detected. "
        "All selected checks are currently passing."
    )

else:

    issue_data = (
        failed_data
        .groupby(
            ["CHECK_NAME", "COLUMN_NAME"],
            as_index=False
        )["FAILED_COUNT"]
        .sum()
        .sort_values(
            "FAILED_COUNT",
            ascending=False
        )
    )

    # Show top 5 issues in a clean table
    top_issues = issue_data.head(5).copy()

    top_issues.columns = [
        "Check",
        "Column",
        "Failed Records"
    ]

    top_issues["Priority"] = top_issues[
        "Failed Records"
    ].apply(
        lambda x:
        "🔴 Critical"
        if x >= 20
        else "🟠 High"
        if x >= 10
        else "🟡 Medium"
    )

    with st.container(border=True):

        st.dataframe(
            top_issues[
                [
                    "Priority",
                    "Check",
                    "Column",
                    "Failed Records"
                ]
            ],
            use_container_width=True,
            hide_index=True,
            column_config={
                "Failed Records": st.column_config.ProgressColumn(
                    "Failed Records",
                    format="%d",
                    min_value=0,
                    max_value=int(top_issues["Failed Records"].max())
                ),
            }
        )


# ============================================================
# DATA QUALITY SUMMARY
# ============================================================

st.markdown("---")

st.subheader("📌 Data Quality Summary")


if failed_checks == 0:

    callout(
        "ok",
        "No immediate action is required. "
        "All selected data quality checks are passing."
    )

else:

    worst_check = (
        failed_data
        .groupby("CHECK_NAME")["FAILED_COUNT"]
        .sum()
        .idxmax()
    )

    worst_count = int(
        failed_data[
            failed_data["CHECK_NAME"] == worst_check
        ]["FAILED_COUNT"].sum()
    )

    callout(
        "warn",
        f"Highest-priority issue: "
        f"<strong>{worst_check}</strong> "
        f"with <strong>{worst_count} failed records</strong>."
    )

    st.markdown("#### Recommended Actions")

    check_names = (
        filtered_df["CHECK_NAME"]
        .astype(str)
        .str.upper()
    )

    recommendations = []

    if check_names.str.contains(
        "NULL"
    ).any():

        recommendations.append(
            "Review missing values and verify required fields."
        )

    if check_names.str.contains(
        "DUPLICATE"
    ).any():

        recommendations.append(
            "Investigate duplicate records and validate business keys."
        )

    if check_names.str.contains(
        "RANGE"
    ).any():

        recommendations.append(
            "Validate numeric fields against expected business limits."
        )

    if check_names.str.contains(
        "FRESH"
    ).any():

        recommendations.append(
            "Verify source-data freshness and pipeline execution time."
        )

    for recommendation in recommendations:

        st.markdown(
            f'<div class="action">• {recommendation}</div>',
            unsafe_allow_html=True
        )


# ============================================================
# DETAILED RESULTS
# ============================================================

st.markdown("---")

st.subheader("📄 Detailed Data Quality Results")

display_df = filtered_df.copy()

display_df["STATUS"] = display_df[
    "STATUS"
].replace(
    {
        "PASS": "🟢 PASS",
        "FAIL": "🔴 FAIL"
    }
)

with st.container(border=True):

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "FAILED_PERCENTAGE": st.column_config.ProgressColumn(
                "FAILED_PERCENTAGE",
                format="%.1f%%",
                min_value=0,
                max_value=100
            ),
            "RUN_TIMESTAMP": st.column_config.DatetimeColumn(
                "RUN_TIMESTAMP",
                format="DD MMM YYYY, hh:mm a"
            ),
        }
    )


# ============================================================
# DOWNLOAD REPORT
# ============================================================

st.download_button(
    label="📥 Download DQ Report",
    data=filtered_df.to_csv(
        index=False
    ),
    file_name="DQ_Report.csv",
    mime="text/csv"
)


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    """
    <div class="footer">
        Snowflake Data Quality Monitor v2.0
        • Snowflake
        • Python
        • Streamlit
        • Plotly
    </div>
    """,
    unsafe_allow_html=True
)