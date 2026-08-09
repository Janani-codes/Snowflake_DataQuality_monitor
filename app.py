import streamlit as st
import pandas as pd
import snowflake.connector
import plotly.express as px
from datetime import datetime
from config import SNOWFLAKE_CONFIG


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
# PROFESSIONAL UI STYLING
# ============================================================

st.markdown("""
<style>

.main {
    padding-top: 1.5rem;
}

/* Main title */
h1 {
    font-size: 2.4rem !important;
    font-weight: 700 !important;
    letter-spacing: -1px;
}

/* Section headings */
h2, h3 {
    font-weight: 650 !important;
}

/* KPI cards */
div[data-testid="metric-container"] {
    background-color: white;
    border: 1px solid #e5e7eb;
    border-radius: 14px;
    padding: 18px;
    box-shadow: 0 2px 8px rgba(15, 23, 42, 0.05);
}

/* Sidebar */
[data-testid="stSidebar"] {
    background-color: #f8fafc;
    border-right: 1px solid #e5e7eb;
}

/* Data table */
[data-testid="stDataFrame"] {
    border: 1px solid #e5e7eb;
    border-radius: 12px;
}

/* Footer */
.footer {
    text-align: center;
    color: #94a3b8;
    font-size: 0.8rem;
    padding: 30px 0 10px 0;
}

</style>
""", unsafe_allow_html=True)


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
    """
    Reads Data Quality results from the DQ_RESULTS table.
    Results are cached for 60 seconds.
    """

    conn = get_connection()

    query = """
        SELECT *
        FROM DQ_RESULTS
        ORDER BY RUN_TIMESTAMP DESC
    """

    df = pd.read_sql(query, conn)

    conn.close()

    return df


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

    st.error("Unable to connect to Snowflake.")

    st.code(str(e))

    st.stop()


# ============================================================
# EMPTY DATA CHECK
# ============================================================

if df.empty:

    st.title("❄️ Snowflake Data Quality Monitor")

    st.info(
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

    st.warning(
        "No records match the selected filters."
    )

    st.stop()


# ============================================================
# HEADER
# ============================================================

st.title("❄️ Snowflake Data Quality Monitor")

st.caption(
    "Real-time monitoring of data quality checks "
    "executed against Snowflake."
)


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


st.info(
    f"🟢 Monitoring Active  •  Last DQ result: {latest_time}"
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


# ============================================================
# KPI CARDS
# ============================================================

k1, k2, k3, k4 = st.columns(4)

with k1:

    st.metric(
        "📋 Total Checks",
        total_checks
    )

with k2:

    st.metric(
        "✅ Passed",
        passed_checks
    )

with k3:

    st.metric(
        "❌ Failed",
        failed_checks
    )

with k4:

    st.metric(
        "💯 Health Score",
        f"{health_score}%"
    )


# ============================================================
# HEALTH STATUS
# ============================================================

st.markdown("---")

st.subheader("Overall Data Health")

if health_score >= 90:

    st.success(
        "🟢 Excellent — data quality is healthy."
    )

elif health_score >= 70:

    st.warning(
        "🟡 Attention Required — some checks are failing."
    )

else:

    st.error(
        "🔴 Critical — significant data quality issues detected."
    )


st.progress(
    health_score / 100
)


# ============================================================
# ANALYTICS
# ============================================================

st.markdown("---")

st.subheader("📊 Data Quality Overview")

left, right = st.columns(2)


# ============================================================
# FAILED RECORDS BY CHECK
# ============================================================

with left:

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
        marker_color="#dc2626",
        textposition="outside"
    )

    fig_bar.update_layout(
        height=370,
        margin=dict(
            l=10,
            r=30,
            t=20,
            b=20
        ),
        xaxis_title="Failed Records",
        yaxis_title="",
        showlegend=False,
        plot_bgcolor="white",
        paper_bgcolor="white"
    )

    st.plotly_chart(
        fig_bar,
        use_container_width=True
    )


# ============================================================
# PASS VS FAIL
# ============================================================

with right:

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

    fig_status = px.bar(
        status_chart,
        x="COUNT",
        y="STATUS",
        orientation="h",
        text="COUNT",
        color="STATUS",
        color_discrete_map={
            "PASS": "#16a34a",
            "FAIL": "#dc2626"
        }
    )

    fig_status.update_traces(
        textposition="outside"
    )

    fig_status.update_layout(
        height=370,
        margin=dict(
            l=10,
            r=30,
            t=20,
            b=20
        ),
        xaxis_title="Number of Checks",
        yaxis_title="",
        showlegend=False,
        plot_bgcolor="white",
        paper_bgcolor="white"
    )

    st.plotly_chart(
        fig_status,
        use_container_width=True
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

    st.success(
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
        hide_index=True
    )


# ============================================================
# DATA QUALITY SUMMARY
# ============================================================

st.markdown("---")

st.subheader("📌 Data Quality Summary")


if failed_checks == 0:

    st.success(
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

    st.warning(
        f"Highest-priority issue: "
        f"**{worst_check}** "
        f"with **{worst_count} failed records**."
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

        st.write(
            f"• {recommendation}"
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

st.dataframe(
    display_df,
    use_container_width=True,
    hide_index=True
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