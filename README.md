# Enterprise Operations Data Engine ⚡

[![DuckDB](https://img.shields.io/badge/DuckDB-0.9+-FFF100.svg?logo=duckdb&logoColor=black)](https://duckdb.org/)
[![Apache Parquet](https://img.shields.io/badge/Storage-Apache_Parquet-blue.svg)](https://parquet.apache.org/)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg?logo=python&logoColor=white)](https://python.org/)
[![Streamlit](https://img.shields.io/badge/Dashboard-Streamlit-FF4B4B.svg?logo=streamlit&logoColor=white)](https://streamlit.io/)

A production-grade, local columnar lakehouse and operational analytics engine designed to handle high-throughput omnichannel ticketing data, SLA tracking, aging claim resolution, and automated data quality audits.

---

## 🎯 Architecture & Capabilities

```
┌────────────────────────┐      ┌───────────────────────────┐      ┌─────────────────────────┐
│   Raw Operational      │      │     DuckDB Ingestion      │      │    Parquet Lakehouse    │
│   Ingestion (Batch)    │ ───► │  - Columnar ETL Engine    │ ───► │  - High compression     │
│   (25,000+ Records)    │      │  - Temporal Enrichment    │      │  - Fast columnar scans  │
└────────────────────────┘      └───────────────────────────┘      └─────────────────────────┘
                                              │
                                              ▼
                                ┌───────────────────────────┐
                                │ Automated QA Auditor      │
                                │  - Temporal anomaly check │
                                │  - State machine validity │
                                │  - Null/PK integrity      │
                                └───────────────────────────┘
                                              │
                                              ▼
                                ┌───────────────────────────┐
                                │ Analytics & Dashboard     │
                                │  - SLA compliance (<24h)  │
                                │  - Partner aging risk     │
                                │  - Agent productivity     │
                                └───────────────────────────┘
```

1. **High-Performance ETL (DuckDB & Parquet):**
   * Ingests, joins, and normalizes batch operational records into Snappy-compressed Parquet lakehouse without memory bloat.
   * Performs sub-second aggregations across 25,000+ multi-channel records.

2. **Automated QA & Data Quality Audits:**
   * Automated verification rules checking for state machine mismatches, temporal inversions (e.g., ticket closed before created), and primary key integrity.

3. **SLA & Aging Exposure Intelligence:**
   * Dynamic calculation of 24-hour SLA compliance, tiered backlog aging (`AGING_HIGH > 7d`, `AGING_MEDIUM 3-7d`), and partner risk distribution.

4. **Interactive BI Dashboard:**
   * Native Streamlit dashboard visualizing omnichannel throughput, agent productivity leaderboard, and critical escalation backlogs.

---

## 🚀 Quick Start

### 1. Installation
Clone the repository and install dependencies:
```bash
git clone https://github.com/adi-prasada/enterprise-operations-data-engine.git
cd enterprise-operations-data-engine
pip install -r requirements.txt
```

### 2. Run Pipeline & Audits
Run the core ETL, automated QA checks, and summary metric generation:
```bash
python main.py
```

### 3. Launch Analytics Dashboard
Start the local BI interface:
```bash
streamlit run src/dashboard/app.py
```

---

## 📁 Repository Structure
```
enterprise-operations-data-engine/
├── data/
│   ├── raw/               # Raw batch snapshots
│   └── processed/         # Optimized Parquet lakehouse
├── src/
│   ├── pipeline/          # DuckDB ingestion & ETL logic
│   ├── analytics/         # SLA & KPI metric calculation engine
│   ├── qa_agent/          # Automated data integrity & audit rules
│   └── dashboard/         # Streamlit visual dashboard
├── tests/                 # Unit & regression tests
├── main.py                # Pipeline entrypoint
└── requirements.txt       # Dependencies
```

---

## 👤 Author
**Firdian Adi Prasada**  
*Data Analyst & AI Automation Specialist*  
[LinkedIn](https://linkedin.com) • [GitHub](https://github.com/adi-prasada)
