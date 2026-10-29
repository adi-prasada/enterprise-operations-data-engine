import duckdb
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

class DataPipeline:
    """
    High-performance ETL pipeline using DuckDB and Parquet storage.
    Optimized for batch operational logs, omnichannel ticketing, and SLA audits.
    """
    def __init__(self, db_path=":memory:", data_dir="data"):
        self.con = duckdb.connect(db_path)
        self.data_dir = data_dir
        self.raw_dir = os.path.join(data_dir, "raw")
        self.processed_dir = os.path.join(data_dir, "processed")
        os.makedirs(self.raw_dir, exist_ok=True)
        os.makedirs(self.processed_dir, exist_ok=True)

    def generate_synthetic_operational_data(self, n_rows=25000, seed=42):
        """
        Generates realistic enterprise operational ticket data for benchmarking.
        """
        np.random.seed(seed)
        channels = ["Call Center", "Live Chat", "Social Media", "TnC / Claims", "SSD Priority"]
        statuses = ["CLOSED", "RESOLVED", "IN_PROGRESS", "PENDING_CLAIM", "ESCALATED"]
        partners = ["Shopee", "TikTok Shop", "Tokopedia", "Lazada", "Corporate Direct"]
        
        start_date = datetime.now() - timedelta(days=30)
        dates = [start_date + timedelta(minutes=int(x)) for x in np.random.randint(0, 30*24*60, n_rows)]
        
        created_at = sorted(dates)
        resolution_hours = np.random.exponential(scale=18.0, size=n_rows)
        
        closed_at = []
        for c_time, r_hr in zip(created_at, resolution_hours):
            if np.random.rand() > 0.12:  # 88% resolved/closed
                closed_at.append(c_time + timedelta(hours=float(r_hr)))
            else:
                closed_at.append(None)
                
        df = pd.DataFrame({
            "ticket_id": [f"TCK-{20260000 + i}" for i in range(n_rows)],
            "created_at": created_at,
            "closed_at": closed_at,
            "channel": np.random.choice(channels, n_rows, p=[0.25, 0.35, 0.15, 0.15, 0.10]),
            "partner": np.random.choice(partners, n_rows, p=[0.35, 0.30, 0.15, 0.10, 0.10]),
            "status": [
                "CLOSED" if closed else np.random.choice(["IN_PROGRESS", "PENDING_CLAIM", "ESCALATED"])
                for closed in closed_at
            ],
            "agent_id": [f"AGT-{np.random.randint(101, 150)}" for _ in range(n_rows)],
            "csat_score": [
                int(np.random.choice([1, 2, 3, 4, 5], p=[0.05, 0.05, 0.15, 0.40, 0.35]))
                if closed and np.random.rand() > 0.4 else None
                for closed in closed_at
            ]
        })
        
        # Save raw snapshot
        raw_path = os.path.join(self.raw_dir, "raw_operational_batch.parquet")
        df.to_parquet(raw_path, index=False, engine="pyarrow", compression="snappy")
        return raw_path

    def process_and_partition(self, raw_parquet_path):
        """
        Executes columnar ingestion, partitions by channel, and registers in DuckDB.
        """
        # Register raw parquet in DuckDB directly without memory overhead
        self.con.execute(f"CREATE OR REPLACE VIEW v_raw_tickets AS SELECT * FROM read_parquet('{raw_parquet_path}')")
        
        processed_path = os.path.join(self.processed_dir, "operational_lakehouse.parquet")
        
        # Add enriched columns: duration_hours, is_over_sla_24h, resolution_status
        query = f"""
            COPY (
                SELECT 
                    ticket_id,
                    created_at,
                    closed_at,
                    channel,
                    partner,
                    status,
                    agent_id,
                    csat_score,
                    CAST(date_diff('minute', created_at, COALESCE(closed_at, CURRENT_TIMESTAMP)) AS DOUBLE) / 60.0 AS duration_hours,
                    CASE 
                        WHEN closed_at IS NOT NULL AND date_diff('hour', created_at, closed_at) <= 24.0 THEN 1
                        WHEN closed_at IS NULL AND date_diff('hour', created_at, CURRENT_TIMESTAMP) > 24.0 THEN 0
                        WHEN closed_at IS NOT NULL AND date_diff('hour', created_at, closed_at) > 24.0 THEN 0
                        ELSE 1
                    END AS is_within_sla_24h,
                    CASE 
                        WHEN closed_at IS NULL AND date_diff('day', created_at, CURRENT_TIMESTAMP) > 7 THEN 'AGING_HIGH'
                        WHEN closed_at IS NULL AND date_diff('day', created_at, CURRENT_TIMESTAMP) > 3 THEN 'AGING_MEDIUM'
                        WHEN closed_at IS NULL THEN 'AGING_LOW'
                        ELSE 'RESOLVED'
                    END AS aging_tier
                FROM v_raw_tickets
            ) TO '{processed_path}' (FORMAT PARQUET, COMPRESSION SNAPPY);
        """
        self.con.execute(query)
        self.con.execute(f"CREATE OR REPLACE TABLE operational_lakehouse AS SELECT * FROM read_parquet('{processed_path}')")
        return processed_path
