# Enterprise Financial Data & AI Architecture
### Portfolio for PwC Financial Services Data & AI Practice

This repository contains an end-to-end financial data engineering, quantitative risk analytics, and autonomous AI assistant ecosystem designed to reflect the modernization challenges of Tier-1 banking clients.

---

## 🏛️ Architecture Overview

```text
├── project1_pii_pipeline/
│   ├── generate_mock_data.py       # Synthetic data generation with injected data flaws
│   ├── pipeline.py                 # Data profiling, deduplication, imputation & PII masking
│   └── raw_banking_data.csv        # 10,000 raw customer records
│
├── project2_risk_analytics/
│   ├── generate_transactions.py    # Star-schema transactional fact table generation
│   ├── risk_analysis.py            # Advanced SQL (CTEs, Window Functions) & Visualization
│   └── credit_risk_dashboard.png   # Executive credit risk reporting dashboard
│
└── project3_ai_agent/
    └── agent.py                    # Autonomous Agentic Assistant (Amazon Bedrock inspired)
```

---

## 📁 Project 1: Financial Data Quality & PII Masking Pipeline
* **Business Objective:** Secure data migration and compliance (GDPR, GLBA, CCPA) for financial platforms (inspired by PwC SAP S/4HANA migrations).
* **Key Capabilities:**
  - Automated **Data Profiling Audit Report** detecting duplicate entries and null values.
  - Median-based imputation for missing credit scores and automated handling of legacy contact records.
  - Regex-driven **PII Masking Engine** standardizing and redacting SSNs (`XXX-XX-####`) and bank account numbers (`*******####`).
  - Relational persistence into SQLite using explicit SQL Data Definition Language (DDL).

---

## 📁 Project 2: Financial Risk Data Aggregation (Credit Risk)
* **Business Objective:** Credit risk stratification mirroring CECL (Current Expected Credit Losses) and CCAR stress testing.
* **Key Capabilities:**
  - Star schema design linking dimensional customer records (`dim_customers`) with 100,000+ transactional events (`fact_transactions`).
  - Advanced SQL querying using **Common Table Expressions (CTEs)** and **Window Functions** (`AVG() OVER (...)`) to calculate rolling average balances and missed payment frequencies.
  - Multi-tier risk categorization (Low, Medium, High Risk) correlated with historical default probabilities.

### 📊 Executive Credit Risk Dashboard:
![Credit Risk Dashboard](project2_risk_analytics/credit_risk_dashboard.png)

---

## 📁 Project 3: "Agentic" Financial Data Assistant
* **Business Objective:** Autonomous natural-language database querying inspired by **Amazon Bedrock AgentCore**.
* **Key Capabilities:**
  - **Text-to-SQL Tooling:** Translates complex natural language prompts into optimized SQLite queries.
  - **Enterprise Security Guardrails:** Programmatically intercepts and blocks destructive operations (`DROP`, `DELETE`, `UPDATE`).
  - **Code Interpreter & Synthesis:** Synthesizes SQL result sets into executive-level financial commentary.

---

## 🚀 Setup & Execution

1. **Clone the repository:**
   ```bash
   git clone https://github.com/jimm-aye/financial-data-ai-portfolio.git
   cd financial-data-ai-portfolio
   ```

2. **Install dependencies:**
   ```bash
   pip3 install pandas faker matplotlib seaborn groq
   ```

3. **Run the AI Agent:**
   ```bash
   cd project3_ai_agent
   python3 agent.py
   ```