import duckdb
import pandas as pd

class MetricsEngine:
    """
    Computes SLA compliance, agent productivity distribution, and aging ticket risk.
    """
    def __init__(self, con: duckdb.DuckDBPyConnection):
        self.con = con

    def get_executive_summary(self) -> dict:
        query = """
            SELECT 
                COUNT(*) AS total_tickets,
                COUNT(closed_at) AS resolved_tickets,
                ROUND(COUNT(closed_at) * 100.0 / COUNT(*), 2) AS resolution_rate_pct,
                ROUND(AVG(duration_hours), 2) AS avg_resolution_time_hrs,
                ROUND(SUM(CASE WHEN is_within_sla_24h = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS sla_compliance_pct,
                ROUND(AVG(csat_score), 2) AS avg_csat
            FROM operational_lakehouse;
        """
        res = self.con.execute(query).fetchdf().to_dict(orient="records")[0]
        return res

    def get_channel_performance(self) -> pd.DataFrame:
        query = """
            SELECT 
                channel,
                COUNT(*) AS ticket_volume,
                ROUND(AVG(duration_hours), 2) AS avg_handling_hours,
                ROUND(SUM(CASE WHEN is_within_sla_24h = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS sla_pct,
                ROUND(AVG(csat_score), 2) AS csat_avg
            FROM operational_lakehouse
            GROUP BY channel
            ORDER BY ticket_volume DESC;
        """
        return self.con.execute(query).fetchdf()

    def get_aging_risk_backlog(self) -> pd.DataFrame:
        query = """
            SELECT 
                partner,
                COUNT(*) AS open_backlog_count,
                SUM(CASE WHEN aging_tier = 'AGING_HIGH' THEN 1 ELSE 0 END) AS critical_over_7d,
                SUM(CASE WHEN aging_tier = 'AGING_MEDIUM' THEN 1 ELSE 0 END) AS warning_3_7d,
                ROUND(AVG(duration_hours), 1) AS avg_open_hours
            FROM operational_lakehouse
            WHERE status != 'CLOSED' AND status != 'RESOLVED'
            GROUP BY partner
            ORDER BY critical_over_7d DESC;
        """
        return self.con.execute(query).fetchdf()

    def get_agent_productivity_matrix(self, top_n=10) -> pd.DataFrame:
        query = f"""
            SELECT 
                agent_id,
                COUNT(*) AS handled_count,
                ROUND(AVG(duration_hours), 1) AS avg_resolve_hours,
                ROUND(SUM(CASE WHEN is_within_sla_24h = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS sla_pct,
                ROUND(AVG(csat_score), 2) AS csat_score
            FROM operational_lakehouse
            GROUP BY agent_id
            ORDER BY handled_count DESC
            LIMIT {top_n};
        """
        return self.con.execute(query).fetchdf()
