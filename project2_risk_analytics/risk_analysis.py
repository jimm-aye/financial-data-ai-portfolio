import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

DB_PATH = "../project1_pii_pipeline/finance_vault.db"

print("🔗 Connecting to database to execute Advanced SQL Risk Analytics...")
conn = sqlite3.connect(DB_PATH)

# ==============================================================================
# ADVANCED SQL QUERY (CTEs + WINDOW FUNCTIONS + JOINS + CONDITIONAL AGGREGATIONS)
# ==============================================================================
sql_query = """
WITH CustomerTxnMetrics AS (
    -- CTE 1: Calculate rolling metrics per customer using SQL Window Functions
    SELECT 
        transaction_id,
        customer_id,
        transaction_date,
        transaction_type,
        amount,
        balance_after_txn,
        -- WINDOW FUNCTION: 3-transaction rolling moving average balance
        AVG(balance_after_txn) OVER (
            PARTITION BY customer_id 
            ORDER BY transaction_date 
            ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
        ) AS rolling_avg_balance
    FROM fact_transactions
),

CustomerAggregates AS (
    -- CTE 2: Aggregate transaction behaviors (Missed Payments, Overdrafts, Cash Flow)
    SELECT 
        customer_id,
        COUNT(*) AS total_transactions,
        -- Conditional Aggregations for risk indicators
        SUM(CASE WHEN transaction_type = 'MISSED_PAYMENT' THEN 1 ELSE 0 END) AS missed_payments_count,
        SUM(CASE WHEN transaction_type = 'OVERDRAFT_FEE' THEN 1 ELSE 0 END) AS overdraft_count,
        ROUND(AVG(balance_after_txn), 2) AS avg_historical_balance,
        ROUND(MIN(balance_after_txn), 2) AS min_balance_recorded
    FROM fact_transactions
    GROUP BY customer_id
)

-- MAIN QUERY: Join aggregates with Customer Dimension and assign Risk Tiers
SELECT 
    c.customer_id,
    c.full_name,
    c.masked_ssn,
    c.credit_score,
    c.account_balance AS current_balance,
    c.has_defaulted,
    a.total_transactions,
    a.missed_payments_count,
    a.overdraft_count,
    a.avg_historical_balance,
    a.min_balance_recorded,
    -- Financial Risk Classification (CECL / CCAR inspired)
    CASE 
        WHEN c.credit_score < 580 OR a.missed_payments_count >= 2 OR a.min_balance_recorded < -300 
            THEN 'High Risk'
        WHEN c.credit_score BETWEEN 580 AND 669 OR a.missed_payments_count = 1 
            THEN 'Medium Risk'
        ELSE 'Low Risk'
    END AS risk_tier
FROM dim_customers c
INNER JOIN CustomerAggregates a 
    ON c.customer_id = a.customer_id;
"""

df_risk = pd.read_sql_query(sql_query, conn)
conn.close()

print(f"✅ Query executed successfully! Retrieved {len(df_risk):,} customer risk profiles.\n")

# ==============================================================================
# EXECUTIVE SUMMARY AUDIT (Printed to terminal)
# ==============================================================================
print("=" * 65)
print("🏦 EXECUTIVE CREDIT RISK SUMMARY")
print("=" * 65)
tier_summary = df_risk.groupby("risk_tier").agg(
    total_customers=("customer_id", "count"),
    avg_credit_score=("credit_score", "mean"),
    avg_missed_payments=("missed_payments_count", "mean"),
    default_rate=("has_defaulted", "mean")
).reset_index()

tier_summary["default_rate"] = (tier_summary["default_rate"] * 100).round(2).astype(str) + "%"
tier_summary["avg_credit_score"] = tier_summary["avg_credit_score"].round(1)
tier_summary["avg_missed_payments"] = tier_summary["avg_missed_payments"].round(2)
print(tier_summary.to_string(index=False))
print("=" * 65 + "\n")

# ==============================================================================
# DATA VISUALIZATION DASHBOARD (Matplotlib & Seaborn)
# ==============================================================================
print("📊 Generating Visual Credit Risk Dashboard...")

sns.set_theme(style="whitegrid")
fig, axes = plt.subplots(2, 2, figsize=(14, 10))
fig.suptitle("Financial Services: Customer Credit Risk Modeling Dashboard", fontsize=16, fontweight="bold")

palette = {"Low Risk": "#2ca02c", "Medium Risk": "#ff7f0e", "High Risk": "#d62728"}

# 1. Customer Count by Risk Tier
sns.countplot(data=df_risk, x="risk_tier", order=["Low Risk", "Medium Risk", "High Risk"], ax=axes[0, 0], palette=palette)
axes[0, 0].set_title("Customer Distribution by Risk Tier", fontweight="bold")
axes[0, 0].set_xlabel("Risk Classification")
axes[0, 0].set_ylabel("Number of Customers")

# 2. Credit Score vs. Risk Tier (Boxplot)
sns.boxplot(data=df_risk, x="risk_tier", y="credit_score", order=["Low Risk", "Medium Risk", "High Risk"], ax=axes[0, 1], palette=palette)
axes[0, 1].set_title("Credit Score Distribution by Risk Tier", fontweight="bold")
axes[0, 1].set_xlabel("Risk Classification")
axes[0, 1].set_ylabel("Credit Score")

# 3. Missed Payments by Risk Tier
sns.barplot(data=df_risk, x="risk_tier", y="missed_payments_count", order=["Low Risk", "Medium Risk", "High Risk"], ax=axes[1, 0], palette=palette, ci=None)
axes[1, 0].set_title("Average Missed Payments (Last 12 Mos)", fontweight="bold")
axes[1, 0].set_xlabel("Risk Classification")
axes[1, 0].set_ylabel("Avg Missed Payments")

# 4. Actual Default Rate by Risk Tier
default_rates = df_risk.groupby("risk_tier")["has_defaulted"].mean().reset_index()
sns.barplot(data=default_rates, x="risk_tier", y="has_defaulted", order=["Low Risk", "Medium Risk", "High Risk"], ax=axes[1, 1], palette=palette)
axes[1, 1].set_title("Observed Historical Default Rate", fontweight="bold")
axes[1, 1].set_xlabel("Risk Classification")
axes[1, 1].set_ylabel("Default Rate (0.0 - 1.0)")

plt.tight_layout()
output_image = "risk_dashboard.png"
plt.savefig(output_image, dpi=300)
print(f"🎉 Dashboard saved successfully as '{output_image}'!")