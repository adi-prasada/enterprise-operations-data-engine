import time
from src.pipeline.etl_duckdb import DataPipeline
from src.analytics.metrics_engine import MetricsEngine
from src.qa_agent.integrity_auditor import DataIntegrityAuditor

def main():
    print("=" * 60)
    print("🚀 ENTERPRISE OPERATIONS & SLA DATA ENGINE")
    print("=" * 60)
    
    start_time = time.time()
    pipeline = DataPipeline()
    
    # 1. Ingestion / Batch Generation
    print("\n[1/4] Ingesting raw operational ticket logs...")
    raw_file = pipeline.generate_synthetic_operational_data(n_rows=25000)
    print(f"      ✓ Generated 25,000 raw tickets -> {raw_file}")
    
    # 2. DuckDB Columnar Transformation & Parquet Lakehouse
    print("\n[2/4] Executing DuckDB ETL & Parquet partitioning...")
    lakehouse_file = pipeline.process_and_partition(raw_file)
    print(f"      ✓ Enriched & persisted lakehouse -> {lakehouse_file}")
    
    # 3. Data Integrity & Automated QA Audit
    print("\n[3/4] Running automated QA data integrity audit...")
    auditor = DataIntegrityAuditor(pipeline.con)
    audit_results = auditor.run_full_audit()
    for log_entry in audit_results["audit_log"]:
        print(f"      {log_entry}")
        
    # 4. Analytics & SLA Metrics Computation
    print("\n[4/4] Computing executive operational metrics...")
    metrics = MetricsEngine(pipeline.con)
    summary = metrics.get_executive_summary()
    
    print("\n" + "-" * 40)
    print("📊 EXECUTIVE OPERATIONS SUMMARY")
    print("-" * 40)
    print(f" Total Tickets Volume    : {summary['total_tickets']:,}")
    print(f" Resolution Rate         : {summary['resolution_rate_pct']}%")
    print(f" SLA Compliance Rate     : {summary['sla_compliance_pct']}%")
    print(f" Avg Resolution Duration : {summary['avg_resolution_time_hrs']} hrs")
    print(f" Customer Satisfaction   : {summary['avg_csat']} / 5.0")
    print("-" * 40)
    
    elapsed = time.time() - start_time
    print(f"\n✨ Pipeline executed successfully in {elapsed:.2f}s!")
    print("💡 Launch interactive dashboard with: streamlit run src/dashboard/app.py\n")

if __name__ == "__main__":
    main()
