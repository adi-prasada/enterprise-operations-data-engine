import duckdb
from typing import List, Dict, Any

class DataIntegrityAuditor:
    """
    Automated data quality & anomaly detection engine.
    Mimics autonomous evaluation protocols for enterprise operations.
    """
    def __init__(self, con: duckdb.DuckDBPyConnection):
        self.con = con

    def run_full_audit(self) -> Dict[str, Any]:
        results = {
            "checks_passed": True,
            "anomalies_detected": 0,
            "audit_log": []
        }

        # Check 1: Null or Duplicate Primary Keys
        pk_check = self.con.execute("""
            SELECT 
                COUNT(*) - COUNT(DISTINCT ticket_id) AS duplicate_pks,
                SUM(CASE WHEN ticket_id IS NULL THEN 1 ELSE 0 END) AS null_pks
            FROM operational_lakehouse;
        """).fetchone()
        
        dup_pks, null_pks = pk_check[0], pk_check[1]
        if dup_pks > 0 or null_pks > 0:
            results["checks_passed"] = False
            results["anomalies_detected"] += (dup_pks + null_pks)
            results["audit_log"].append(f"[FAIL] Primary Key Violation: {dup_pks} duplicates, {null_pks} nulls.")
        else:
            results["audit_log"].append("[PASS] Primary Key Integrity: Unique and Non-Null.")

        # Check 2: Logical Timestamp Ordering (closed_at < created_at)
        ts_check = self.con.execute("""
            SELECT COUNT(*) 
            FROM operational_lakehouse 
            WHERE closed_at IS NOT NULL AND closed_at < created_at;
        """).fetchone()[0]

        if ts_check > 0:
            results["checks_passed"] = False
            results["anomalies_detected"] += ts_check
            results["audit_log"].append(f"[FAIL] Temporal Inversion: {ts_check} records have closed_at earlier than created_at.")
        else:
            results["audit_log"].append("[PASS] Temporal Ordering: All timestamps follow chronologically valid sequence.")

        # Check 3: Status Consistency vs Closed Timestamp
        status_inconsistency = self.con.execute("""
            SELECT COUNT(*) 
            FROM operational_lakehouse
            WHERE (status = 'CLOSED' AND closed_at IS NULL)
               OR (status IN ('IN_PROGRESS', 'PENDING_CLAIM') AND closed_at IS NOT NULL);
        """).fetchone()[0]

        if status_inconsistency > 0:
            results["checks_passed"] = False
            results["anomalies_detected"] += status_inconsistency
            results["audit_log"].append(f"[FAIL] State Machine Mismatch: {status_inconsistency} tickets have inconsistent status vs closed_at.")
        else:
            results["audit_log"].append("[PASS] State Machine Consistency: All status labels match completion timestamps.")

        # Check 4: SLA Outliers (> 500 hours anomaly check)
        outliers = self.con.execute("""
            SELECT COUNT(*) 
            FROM operational_lakehouse 
            WHERE duration_hours > 500.0;
        """).fetchone()[0]

        if outliers > 0:
            results["audit_log"].append(f"[WARN] Extreme Outliers: {outliers} tickets exceeded 500 hours duration (Flagged for operational review).")
        else:
            results["audit_log"].append("[PASS] Duration Distribution: No severe multi-month runaway anomalies detected.")

        return results
