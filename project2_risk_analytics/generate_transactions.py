import sqlite3
import random
from datetime import datetime, timedelta
import pandas as pd

# Path to the database you created in Project 1
DB_PATH = "../project1_pii_pipeline/finance_vault.db"

print("🔗 Connecting to existing finance database to fetch customer IDs...")
conn = sqlite3.connect(DB_PATH)

# Fetch customer IDs and starting balances from dim_customers
customers_df = pd.read_sql_query(
    "SELECT customer_id, account_balance, credit_score, has_defaulted FROM dim_customers;",
    conn
)

print(f"Loaded {len(customers_df):,} customers. Generating 12 months of transaction history...")

# Possible transaction types
TXN_TYPES = [
    "PAYMENT_RECEIVED",  # Loan / Credit Card payment (Positive cash flow)
    "PURCHASE",          # Debit / Credit purchase (Negative cash flow)
    "MISSED_PAYMENT",    # Flag for Credit Risk / CECL modeling ($0 amount, penalty flag)
    "OVERDRAFT_FEE",     # Penalty fee
]

transactions = []
txn_id = 1
start_date = datetime.now() - timedelta(days=365)

# Generate 5 to 15 transactions per customer across the year (~80,000+ total rows)
for _, cust in customers_df.iterrows():
    c_id = cust["customer_id"]
    is_defaulter = cust["has_defaulted"] == 1
    low_credit = cust["credit_score"] < 580

    # Defaulters / low-credit customers have higher probability of missed payments
    missed_prob = 0.25 if (is_defaulter or low_credit) else 0.02

    num_txns = random.randint(6, 14)
    running_balance = cust["account_balance"]

    for _ in range(num_txns):
        # Generate random date in past 365 days
        random_days = random.randint(0, 365)
        txn_date = (start_date + timedelta(days=random_days)).strftime("%Y-%m-%d")

        # Determine transaction type
        if random.random() < missed_prob:
            txn_type = "MISSED_PAYMENT"
            amount = 0.0
        elif random.random() < 0.25:
            txn_type = "PAYMENT_RECEIVED"
            amount = round(random.uniform(100.0, 2500.0), 2)
            running_balance += amount
        elif running_balance < 0 and random.random() < 0.40:
            txn_type = "OVERDRAFT_FEE"
            amount = -35.00
            running_balance += amount
        else:
            txn_type = "PURCHASE"
            amount = -round(random.uniform(10.0, 500.0), 2)
            running_balance += amount

        transactions.append({
            "transaction_id": f"TXN_{txn_id:08d}",
            "customer_id": c_id,
            "transaction_date": txn_date,
            "transaction_type": txn_type,
            "amount": amount,
            "balance_after_txn": round(running_balance, 2)
        })
        txn_id += 1

txn_df = pd.DataFrame(transactions)

# Sort chronologically by customer and date
txn_df = txn_df.sort_values(by=["customer_id", "transaction_date"]).reset_index(drop=True)

print(f"Generated {len(txn_df):,} transactions. Creating SQL table 'fact_transactions'...")

# DDL: Create the fact table schema
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS fact_transactions (
    transaction_id TEXT PRIMARY KEY,
    customer_id TEXT NOT NULL,
    transaction_date TEXT NOT NULL,
    transaction_type TEXT NOT NULL,
    amount REAL NOT NULL,
    balance_after_txn REAL NOT NULL,
    FOREIGN KEY (customer_id) REFERENCES dim_customers(customer_id)
);
""")
conn.commit()

# Insert data into SQLite
txn_df.to_sql("fact_transactions", conn, if_exists="replace", index=False)
conn.commit()

# Verify
cursor.execute("SELECT COUNT(*) FROM fact_transactions;")
total_count = cursor.fetchone()[0]

cursor.execute("SELECT * FROM fact_transactions LIMIT 3;")
samples = cursor.fetchall()
conn.close()

print(f"🎉 Successfully loaded {total_count:,} records into 'fact_transactions'!")
print("Sample rows:")
for s in samples:
    print(f"  {s}")