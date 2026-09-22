# Enterprise Financial Data & AI Architecture
### Portfolio for PwC Financial Services Data & AI Practice

This repository contains an end-to-end financial data engineering, quantitative risk analytics, and autonomous AI assistant ecosystem designed to reflect the modernization challenges of Tier-1 banking clients.

---

## 🏛️ Architecture Overview
├── project1_pii_pipeline/ # S/4HANA-inspired Data Governance & PII Masking
│ ├── generate_mock_data.py # Synthetic data generation with injected data flaws
│ └── pipeline.py # Data profiling, deduplication, imputation & PII masking
│
├── project2_risk_analytics/ # CECL / CCAR Credit Risk Modeling & Aggregation
│ ├── generate_transactions.py # Star-schema transactional fact table generation
│ ├── risk_analysis.py # Advanced SQL (CTEs, Window Functions) & Visualization
│ └── credit_risk_dashboard.png # Executive credit risk reporting dashboard
│
└── project3_ai_agent/ # Autonomous Agentic Financial Assistant (Amazon Bedrock inspired)
└── agent.py # Text-to-SQL LLM Agent with enterprise guardrails & Code Interpreter
code
Code
---

## 📁 Project 1: Financial Data Quality & PII Masking Pipeline
* **Business Objective:** Secure data migration and compliance (GDPR, GLBA, CCPA) for financial platforms.
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
  - Multi-tier risk categorization (Low, Medium, High Risk) correlated with historical default probabilities and visualized via Seaborn/Matplotlib.

---

## 📁 Project 3: "Agentic" Financial Data Assistant
* **Business Objective:** Autonomous natural-language database querying inspired by **Amazon Bedrock AgentCore**.
* **Key Capabilities:**
  - **Text-to-SQL Tooling:** Translates complex natural language prompts into optimized SQLite queries.
  - **Enterprise Security Guardrail:** Programmatically intercepts and blocks destructive commands (`DROP`, `DELETE`, `UPDATE`).
  - **Code Interpreter & Synthesis:** Synthesizes SQL result sets into executive-level financial commentary.

---

## 🚀 Setup & Execution

1. **Clone the repository:**
   ```bash
   git clone https://github.com/<YOUR_USERNAME>/financial-data-ai-portfolio.git
   cd financial-data-ai-portfolio
2. Install dependencies:
   pip3 install pandas faker matplotlib seaborn groq
3. Run the AI Agent:
   cd project3_ai_agent
   python3 agent.py