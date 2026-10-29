import pytest
import os
import duckdb
from src.pipeline.etl_duckdb import DataPipeline
from src.analytics.metrics_engine import MetricsEngine
from src.qa_agent.integrity_auditor import DataIntegrityAuditor

@pytest.fixture(scope="session")
def setup_pipeline():
    pipeline = DataPipeline(data_dir="/tmp/test_data_engine")
    raw_file = pipeline.generate_synthetic_operational_data(n_rows=500, seed=123)
    lakehouse_file = pipeline.process_and_partition(raw_file)
    return pipeline

def test_lakehouse_creation(setup_pipeline):
    pipeline = setup_pipeline
    res = pipeline.con.execute("SELECT COUNT(*) FROM operational_lakehouse").fetchone()[0]
    assert res == 500

def test_metrics_summary(setup_pipeline):
    pipeline = setup_pipeline
    metrics = MetricsEngine(pipeline.con)
    summary = metrics.get_executive_summary()
    assert summary["total_tickets"] == 500
    assert 0 <= summary["sla_compliance_pct"] <= 100

def test_integrity_auditor(setup_pipeline):
    pipeline = setup_pipeline
    auditor = DataIntegrityAuditor(pipeline.con)
    audit = auditor.run_full_audit()
    assert audit["checks_passed"] is True
    assert audit["anomalies_detected"] == 0
