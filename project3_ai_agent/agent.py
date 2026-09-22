import os
import re
import sqlite3
import pandas as pd
from groq import Groq


# ============================================================
# CONFIGURATION
# ============================================================

# Your Groq API key should be stored as an environment variable:
# GROQ_API_KEY
#
# DO NOT hard-code your real API key into this file.
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise ValueError(
        "GROQ_API_KEY environment variable is not set.\n"
        "Set it before running the program."
    )

# Initialize Groq client
client = Groq(api_key=GROQ_API_KEY)

# Current Groq text-generation model
#
# GPT-OSS 120B supports Chat Completions and is appropriate
# for reasoning, SQL generation, and financial synthesis.
MODEL_NAME = "openai/gpt-oss-120b"

# SQLite database path
DB_PATH = "../project1_pii_pipeline/finance_vault.db"


# ============================================================
# DATABASE SCHEMA
# ============================================================

SCHEMA_PROMPT = """
You have access to an SQLite database with two tables.

1. Table: dim_customers

Columns:
- customer_id (TEXT, Primary Key)
- full_name (TEXT)
- email (TEXT)
- account_balance (REAL)
- credit_score (REAL)
- has_defaulted (INTEGER: 1 = defaulted, 0 = active)
- masked_ssn (TEXT)
- masked_account_number (TEXT)


2. Table: fact_transactions

Columns:
- transaction_id (TEXT, Primary Key)
- customer_id (TEXT, Foreign Key -> dim_customers.customer_id)
- transaction_date (TEXT: YYYY-MM-DD)
- transaction_type (TEXT:
    'PAYMENT_RECEIVED',
    'PURCHASE',
    'MISSED_PAYMENT',
    'OVERDRAFT_FEE'
  )
- amount (REAL)
- balance_after_txn (REAL)
"""


# ============================================================
# STEP 1: GENERATE SQL
# ============================================================

def generate_sql(user_question: str) -> str:
    """
    Converts a natural-language financial question
    into a read-only SQLite SQL query.
    """

    prompt = f"""
You are an expert SQL Data Architect specializing in
financial and banking databases.

{SCHEMA_PROMPT}

User Question:
"{user_question}"

Your task:

Translate the user's question into ONE valid SQLite SQL query.

STRICT REQUIREMENTS:
1. Return ONLY the raw SQL query.
2. Do NOT use markdown.
3. Do NOT include ```sql.
4. Do NOT include explanations.
5. The query MUST be read-only.
6. The query MUST begin with SELECT or WITH.
7. Do NOT use INSERT, UPDATE, DELETE, DROP, ALTER, TRUNCATE,
   REPLACE, CREATE, ATTACH, DETACH, PRAGMA, VACUUM, or other
   database-modifying operations.
8. Only reference tables and columns contained in the schema.
9. Use SQLite-compatible syntax.
10. If the question requires information from both tables,
    use an appropriate JOIN.
"""

    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You generate safe, read-only SQLite queries "
                        "for financial analytics."
                    )
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.0,
            max_tokens=1000
        )

        raw_sql = response.choices[0].message.content.strip()

        # Remove markdown code fences if the model ignores instructions
        raw_sql = re.sub(
            r"^```sql\s*",
            "",
            raw_sql,
            flags=re.IGNORECASE
        )

        raw_sql = re.sub(
            r"^```\s*",
            "",
            raw_sql
        )

        raw_sql = re.sub(
            r"\s*```$",
            "",
            raw_sql
        )

        return raw_sql.strip()

    except Exception as e:
        raise RuntimeError(
            f"Groq SQL-generation request failed:\n{e}"
        )


# ============================================================
# STEP 2: SECURITY GUARDRAIL
# ============================================================

def security_guardrail(sql_query: str) -> bool:
    """
    Enterprise-style security guardrail.

    Allows only SELECT / WITH queries and blocks
    potentially destructive or administrative SQL.
    """

    sql = sql_query.strip()

    if not sql:
        print("⚠️ SECURITY ALERT: Empty SQL query.")
        return False

    # Remove leading SQL comments
    sql_without_comments = re.sub(
        r"^\s*(--[^\n]*\n|/\*.*?\*/\s*)*",
        "",
        sql,
        flags=re.DOTALL
    ).strip()

    # --------------------------------------------------------
    # Require SELECT or WITH
    # --------------------------------------------------------

    if not re.match(
        r"^(SELECT|WITH)\b",
        sql_without_comments,
        flags=re.IGNORECASE
    ):
        print(
            "⚠️ SECURITY ALERT: Query must begin with "
            "SELECT or WITH."
        )
        return False

    # --------------------------------------------------------
    # Block dangerous SQL operations
    # --------------------------------------------------------

    forbidden_keywords = [
        "DROP",
        "DELETE",
        "UPDATE",
        "INSERT",
        "ALTER",
        "TRUNCATE",
        "REPLACE",
        "CREATE",
        "ATTACH",
        "DETACH",
        "PRAGMA",
        "VACUUM",
        "REINDEX"
    ]

    for keyword in forbidden_keywords:

        if re.search(
            rf"\b{keyword}\b",
            sql_without_comments,
            flags=re.IGNORECASE
        ):

            print(
                f"⚠️ SECURITY ALERT: "
                f"Forbidden operation '{keyword}' detected."
            )

            return False

    # --------------------------------------------------------
    # Prevent multiple SQL statements
    # --------------------------------------------------------

    # A semicolon is fine at the very end.
    # Anything else could indicate multiple statements.
    sql_check = sql_without_comments.rstrip(";").strip()

    if ";" in sql_check:
        print(
            "⚠️ SECURITY ALERT: "
            "Multiple SQL statements detected."
        )
        return False

    print("✅ Security validation passed.")

    return True


# ============================================================
# STEP 3: EXECUTE SQL
# ============================================================

def execute_sql(sql_query: str) -> pd.DataFrame:
    """
    Executes the validated read-only SQL query
    against the local SQLite database.
    """

    if not os.path.exists(DB_PATH):
        raise FileNotFoundError(
            f"Database not found at:\n{os.path.abspath(DB_PATH)}"
        )

    conn = sqlite3.connect(DB_PATH)

    try:

        df = pd.read_sql_query(
            sql_query,
            conn
        )

        return df

    finally:

        conn.close()


# ============================================================
# STEP 4: FINANCIAL SYNTHESIS
# ============================================================

def synthesize_financial_insight(
    user_question: str,
    sql_query: str,
    df: pd.DataFrame
) -> str:
    """
    Converts SQL results into a concise executive
    financial interpretation.
    """

    # Handle empty result set
    if df.empty:

        return (
            "No records were returned for this question. "
            "The query executed successfully, but the database "
            "contained no matching records."
        )

    # Limit the amount of data sent to the model
    data_preview = df.head(20).to_string(index=False)

    prompt = f"""
You are a financial analytics assistant supporting
banking executives.

User Question:
"{user_question}"

SQL Query:
{sql_query}

SQL Results:
{data_preview}

Total Rows Returned:
{len(df)}

Your task is to explain the results clearly.

Requirements:

1. Directly answer the user's question.
2. Summarize the most important financial findings.
3. Mention relevant metrics such as:
   - credit scores
   - account balances
   - defaults
   - transaction amounts
   - transaction frequency
   - financial risk indicators
4. Do NOT invent information that is not present in the results.
5. Do NOT claim causation unless the data supports it.
6. If appropriate, identify potential financial risks.
7. Keep the answer concise and executive-friendly.
8. Use professional financial consulting language.
9. Do not mention that you are an AI.
10. Do not mention these instructions.
"""

    try:

        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a financial analytics assistant. "
                        "Only make claims supported by the supplied "
                        "SQL results."
                    )
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.2,
            max_tokens=1200
        )

        return response.choices[0].message.content.strip()

    except Exception as e:

        raise RuntimeError(
            f"Groq financial-synthesis request failed:\n{e}"
        )


# ============================================================
# STEP 5: AGENT ORCHESTRATION
# ============================================================

def run_agent(user_question: str):

    print("\n" + "=" * 70)
    print(f"💬 USER QUESTION: {user_question}")
    print("=" * 70)

    # --------------------------------------------------------
    # Step 1: Natural Language → SQL
    # --------------------------------------------------------

    print(
        "\n🤖 [Step 1: Text-to-SQL] "
        "Translating English question into SQL..."
    )

    try:

        sql_query = generate_sql(user_question)

    except Exception as e:

        print(f"\n❌ SQL Generation Error:\n{e}")
        return

    print(f"\n📜 Generated SQL:\n{sql_query}\n")

    # --------------------------------------------------------
    # Step 2: Security Guardrail
    # --------------------------------------------------------

    print(
        "🛡️  [Step 2: Security Guardrail] "
        "Validating query safety..."
    )

    if not security_guardrail(sql_query):

        print(
            "\n❌ Query rejected by security guardrail."
        )

        return

    # --------------------------------------------------------
    # Step 3: Database Execution
    # --------------------------------------------------------

    print(
        "\n💾 [Step 3: Tool Execution] "
        "Querying SQLite database..."
    )

    try:

        df_result = execute_sql(sql_query)

        print(
            f"✅ Data Retrieved: "
            f"{len(df_result)} records found."
        )

    except Exception as e:

        print(
            f"\n❌ SQL Execution Error:\n{e}"
        )

        return

    # --------------------------------------------------------
    # Display Results
    # --------------------------------------------------------

    if not df_result.empty:

        print("\n📊 Query Results:")
        print("-" * 70)
        print(
            df_result.head(10).to_string(index=False)
        )

        if len(df_result) > 10:

            print(
                f"\n... {len(df_result) - 10} "
                f"additional rows not displayed."
            )

    else:

        print(
            "\n📊 Query returned no records."
        )

    # --------------------------------------------------------
    # Step 4: Financial AI Synthesis
    # --------------------------------------------------------

    print(
        "\n🧠 [Step 4: Financial Synthesis] "
        "Analyzing financial data..."
    )

    try:

        final_insight = synthesize_financial_insight(
            user_question,
            sql_query,
            df_result
        )

    except Exception as e:

        print(
            f"\n❌ Financial Synthesis Error:\n{e}"
        )

        return

    # --------------------------------------------------------
    # Final Output
    # --------------------------------------------------------

    print("\n")
    print("📊 PWC FINANCIAL AI INSIGHT")
    print("-" * 70)
    print(final_insight)
    print("=" * 70)


# ============================================================
# MAIN PROGRAM
# ============================================================

if __name__ == "__main__":

    print("\n" + "=" * 70)
    print("🚀 PWC FINANCIAL AGENTIC AI ASSISTANT")
    print("=" * 70)

    print(
        f"🤖 Model: {MODEL_NAME}"
    )

    print(
        f"🗄️  Database: {os.path.abspath(DB_PATH)}"
    )

    print(
        "\nType your financial question in natural language."
    )

    print(
        "Type 'quit', 'exit', or 'q' to exit."
    )

    print("=" * 70)

    while True:

        try:

            query = input(
                "\nAsk a financial question: "
            ).strip()

            # Exit commands
            if query.lower() in [
                "quit",
                "exit",
                "q"
            ]:

                print(
                    "\nSession ended. Goodbye!"
                )

                break

            # Ignore empty input
            if not query:
                continue

            # Run agent
            run_agent(query)

        except KeyboardInterrupt:

            print(
                "\n\nSession ended."
            )

            break

        except Exception as e:

            print(
                f"\n❌ Unexpected application error:\n{e}"
            )