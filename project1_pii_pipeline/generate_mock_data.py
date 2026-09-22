import random
from faker import Faker
import pandas as pd

# Initialize Faker with US locale for realistic US banking data
fake = Faker("en_US")
Faker.seed(42)
random.seed(42)

NUM_RECORDS = 10_000

print(f"Generating {NUM_RECORDS} raw banking customer records...")

records = []
for i in range(1, NUM_RECORDS + 1):
    account_number = fake.bban()
    name = fake.name()
    ssn = fake.ssn()
    email = fake.email()
    balance = round(random.uniform(-500.0, 75000.0), 2)
    credit_score = random.randint(300, 850)
    has_defaulted = random.choices([0, 1], weights=[0.88, 0.12])[0]

    # --- INJECT REAL-WORLD DATA QUALITY FLAWS ---
    # 1. Random missing values
    if random.random() < 0.05:
        email = None
    if random.random() < 0.03:
        credit_score = None

    # 2. Inconsistent SSN formatting
    if random.random() < 0.20:
        ssn = ssn.replace("-", "")

    # Append EVERY record (make sure this is aligned with the 'if' statements)
    records.append({
        "customer_id": f"CUST_{i:06d}",
        "full_name": name,
        "ssn": ssn,
        "email": email,
        "account_number": account_number,
        "account_balance": balance,
        "credit_score": credit_score,
        "has_defaulted": has_defaulted,
    })

df = pd.DataFrame(records)

# Inject duplicates safely (~1% duplicate rate to simulate migration errors)
num_dupes = min(100, len(df))
duplicates = df.sample(n=num_dupes, random_state=42)
df = pd.concat([df, duplicates], ignore_index=True)

# Save to CSV
output_filename = "raw_banking_data.csv"
df.to_csv(output_filename, index=False)

print(f"Done! Created '{output_filename}' with {len(df):,} total rows.")
print("Flaws included: nulls in email/credit_score, unformatted SSNs, and duplicate records.")