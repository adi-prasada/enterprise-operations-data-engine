import streamlit as st
import duckdb
import pandas as pd
import os

st.set_page_config(page_title="Operations & SLA Lakehouse", layout="wide", page_icon="📊")

st.title("⚡ Enterprise Operations & SLA Analytics Engine")
st.markdown("Real-time operational lakehouse powered by **DuckDB**, **Parquet**, and **Automated Data Auditing**.")

PARQUET_FILE = "data/processed/operational_lakehouse.parquet"

@st.cache_resource
def get_db_connection():
    con = duckdb.connect(":memory:")
    if os.path.exists(PARQUET_FILE):
        con.execute(f"CREATE OR REPLACE VIEW operational_lakehouse AS SELECT * FROM read_parquet('{PARQUET_FILE}')")
    return con

con = get_db_connection()

if not os.path.exists(PARQUET_FILE):
    st.warning("⚠️ Lakehouse data not found. Please run `python main.py` to generate & process the initial batch.")
    st.stop()

# --- TOP METRICS ROW ---
summary = con.execute("""
    SELECT 
        COUNT(*) AS total,
        COUNT(closed_at) AS resolved,
        ROUND(AVG(duration_hours), 1) AS avg_duration,
        ROUND(SUM(CASE WHEN is_within_sla_24h = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) AS sla_pct,
        ROUND(AVG(csat_score), 2) AS csat
    FROM operational_lakehouse;
""").fetchdf().iloc[0]

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Total Tickets", f"{summary['total']:,}")
c2.metric("Resolution Rate", f"{(summary['resolved']/summary['total'])*100:.1f}%")
c3.metric("SLA Compliance (<24h)", f"{summary['sla_pct']}%", delta="Target: 85%")
c4.metric("Avg Handling Time", f"{summary['avg_duration']} hrs")
c5.metric("Avg CSAT Score", f"{summary['csat']} / 5.0")

st.divider()

# --- CHARTS & MATRICES ---
col_left, col_right = st.columns([1, 1])

with col_left:
    st.subheader("📈 Omnichannel Volume & SLA Distribution")
    channel_df = con.execute("""
        SELECT 
            channel,
            COUNT(*) AS volume,
            ROUND(SUM(CASE WHEN is_within_sla_24h = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) AS sla_compliance
        FROM operational_lakehouse
        GROUP BY channel
        ORDER BY volume DESC;
    """).fetchdf()
    st.dataframe(channel_df, use_container_width=True)

with col_right:
    st.subheader("🚨 Partner Aging & Backlog Exposure")
    aging_df = con.execute("""
        SELECT 
            partner,
            COUNT(*) AS total_backlog,
            SUM(CASE WHEN aging_tier = 'AGING_HIGH' THEN 1 ELSE 0 END) AS high_risk_7d,
            SUM(CASE WHEN aging_tier = 'AGING_MEDIUM' THEN 1 ELSE 0 END) AS med_risk_3_7d
        FROM operational_lakehouse
        WHERE status != 'CLOSED' AND status != 'RESOLVED'
        GROUP BY partner
        ORDER BY high_risk_7d DESC;
    """).fetchdf()
    st.dataframe(aging_df, use_container_width=True)

st.divider()

st.subheader("👥 Agent Productivity & Quality Leaderboard")
agent_df = con.execute("""
    SELECT 
        agent_id,
        COUNT(*) AS tickets_handled,
        ROUND(AVG(duration_hours), 1) AS avg_resolution_hours,
        ROUND(SUM(CASE WHEN is_within_sla_24h = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) AS sla_pct,
        ROUND(AVG(csat_score), 2) AS csat_avg
    FROM operational_lakehouse
    GROUP BY agent_id
    ORDER BY tickets_handled DESC
    LIMIT 15;
""").fetchdf()
st.dataframe(agent_df, use_container_width=True)
