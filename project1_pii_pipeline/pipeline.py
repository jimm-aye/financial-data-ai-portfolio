# -------------------------------------------------------------------------
# IMPORT STATEMENTS: Loading external toolkits into memory
# -------------------------------------------------------------------------

import sqlite3
# What it does: Loads Python's built-in engine for SQLite, a lightweight SQL database.
# Excel Analogy: Like enabling an Add-in to read/write external database files (.db/.accdb).

import re
# What it does: Loads the 'Regular Expressions' (RegEx) engine for complex text pattern matching.
# Excel Analogy: Like advanced wildcards (*, ?), but with pattern superpowers (e.g., "find all digits").

import pandas as pd
# What it does: Loads the Pandas data analysis library and nicknames it 'pd' for shorter typing.
# Excel Analogy: Brings the entire Excel engine (grid, formulas, tables, pivots) into Python memory.


# -------------------------------------------------------------------------
# CONSTANTS / CONFIGURATION (GLOBAL VARIABLES)
# -------------------------------------------------------------------------
# Python Convention: ALL_CAPS denotes values that act as configuration settings and shouldn't change.

CSV_PATH = "raw_banking_data.csv"
# What it does: Stores the file path of our input file as a string.
# Excel Analogy: Hardcoding the source workbook name.

DB_PATH = "finance_vault.db"
# What it does: Stores the target database filename where final data will be archived.

TABLE_NAME = "dim_customers"
# What it does: Names the target table. 'dim_' stands for 'Dimension Table' in database modeling 
# (a table containing descriptive attributes about an entity, here: customers).


# =========================================================================
# FUNCTION DEFINITION: profile_data
# -------------------------------------------------------------------------
# PURPOSE: Inspects the DataFrame and prints a Data Quality audit report.
# INPUT:   df: pd.DataFrame -> A Pandas table.
#          (The ': pd.DataFrame' is a "type hint"—documentation telling developers what object to pass).
# OUTPUT:  None (It calculates metrics and prints to the screen, but returns no variable).
# =========================================================================
def profile_data(df: pd.DataFrame):
    """Generates an initial Data Quality audit report."""
    # Docstring: Triple quotes denote multi-line documentation describing the function.

    print("=" * 60)
    # Syntax: Multiplying a string by an integer repeats it.
    # Math: "=" concatenated 60 times. Creates a visual separator line: "====================".

    print("📊 DATA QUALITY AUDIT REPORT (RAW DATA)")
    # Prints the header title string literally to the console.

    print("=" * 60)
    # Repeats the 60-character line for visual symmetry.

    print(f"Total Rows:        {len(df):,}")
    # len(df): Counts the number of rows in the DataFrame (Math: Cardinality of the dataset).
    # :,     : Formats the integer with thousands commas (e.g., 10,100).
    # Excel Analogy: =COUNTA(A:A) - 1 (counting non-empty rows excluding headers).

    print(f"Duplicate Rows:    {df.duplicated().sum():,}")
    # df.duplicated(): Scans every row. Returns a Series (column) of True/False booleans.
    #                  True = this exact entire row has appeared earlier above.
    # .sum()         : Booleans act as numbers in math: True = 1, False = 0.
    #                  Summing the column calculates the total count of duplicated rows.
    # Excel Analogy: SUMPRODUCT(--(COUNTIF(...) > 1))

    print("\nMissing Values per Column:")
    # Syntax: '\n' is the escape character for a newline (blank enter space).

    null_counts = df.isnull().sum()
    # df.isnull() : Scans the entire 2D grid. Turns every cell into True (if blank/None/NaN) or False.
    # .sum()      : When applied to a 2D table, Pandas sums vertically (down each column).
    # Result      : A Series mapping each Column Name -> Total Blank Count.
    # Excel Analogy: Applying =COUNTBLANK() across every individual column.

    for col, count in null_counts.items():
        # Syntax: A 'for' loop iterating through key-value pairs.
        # .items(): Unpacks the Series into pairs: 'col' (column header) and 'count' (number of nulls).

        pct = (count / len(df)) * 100
        # Math: Simple percentage calculation: (Part / Whole) * 100.
        # Excel Analogy: =COUNTBLANK(A:A) / COUNTA(A:A) formatted as %.

        print(f"  - {col:<16}: {count:>5} missing ({pct:.2f}%)")
        # Advanced f-string layout alignment:
        # {col:<16} : Left-aligns '<' the column name within a fixed space of 16 characters.
        # {count:>5}: Right-aligns '>' the count within a fixed space of 5 characters.
        # {pct:.2f} : Limits the float to 2 decimal places (e.g., 5.00%).
        # Purpose   : Keeps all numbers and colons neatly lined up in columns in the terminal.

    print("=" * 60 + "\n")
    # Prints closing border line plus an extra blank newline at the end.


# =========================================================================
# FUNCTION DEFINITION: mask_ssn
# -------------------------------------------------------------------------
# PURPOSE: Standardizes messy Social Security Numbers and masks private digits for compliance.
# INPUT:   ssn_value: str -> A single SSN value (e.g., "123-45-6789" or "123456789").
# OUTPUT:  -> str         -> A masked string format: "XXX-XX-6789".
# =========================================================================
def mask_ssn(ssn_value: str) -> str:
    """Standardizes and masks SSN to XXX-XX-#### format."""

    if not isinstance(ssn_value, str):
        # isinstance checks the data type. If ssn_value is null/float/NaN (not a string):
        return "XXX-XX-0000"
        # Return a safe fallback dummy string immediately to prevent the code from crashing.

    digits = re.sub(r"\D", "", ssn_value)
    # Syntax Breakdown:
    # re.sub(pattern, replacement, text) -> "Regular Expression Substitute"
    # r"\D" : Pattern meaning "Any character that is NOT a digit [0-9]" (the 'r' means raw string).
    # ""    : Replaces non-digits with an empty string (deletes them).
    # Result: Strips dashes, spaces, and garbage text. "123-45-6789" becomes "123456789".
    # Excel Analogy: Like using =SUBSTITUTE(A1, "-", "") repeatedly.

    if len(digits) == 9:
        # Validates that a complete 9-digit SSN exists.
        return f"XXX-XX-{digits[-4:]}"
        # String Slicing [-4:]: Negative index counts from the end backward.
        # It takes the last 4 characters of the string.
        # Excel Analogy: ="XXX-XX-" & RIGHT(digits, 4)

    return "XXX-XX-0000"
    # If the string did not contain exactly 9 digits (it was malformed/corrupted), return fallback.


# =========================================================================
# FUNCTION DEFINITION: mask_account_number
# -------------------------------------------------------------------------
# PURPOSE: Obfuscates a bank account number, keeping only the final 4 digits visible.
# INPUT:   acc_value: str -> Raw account number.
# OUTPUT:  -> str         -> Masked account string: "*******1234".
# =========================================================================
def mask_account_number(acc_value: str) -> str:
    """Masks banking account numbers to protect customer data."""

    if not isinstance(acc_value, str):
        # Guard clause: If the cell is missing/blank/NaN, don't attempt string operations.
        return "************"

    return f"*******{acc_value[-4:]}"
    # Extracts last 4 digits using slice [-4:] and prepends asterisks.
    # Excel Analogy: ="*******" & RIGHT(acc_value, 4)


# =========================================================================
# FUNCTION DEFINITION: clean_and_mask_pipeline
# -------------------------------------------------------------------------
# PURPOSE: Core ETL (Extract, Transform, Load) cleaning orchestration.
# INPUT:   csv_path: str  -> Filepath string where raw CSV lives.
# OUTPUT:  -> pd.DataFrame-> Cleaned, deduplicated, masked table.
# =========================================================================
def clean_and_mask_pipeline(csv_path: str) -> pd.DataFrame:
    """Cleans raw data and applies PII masking."""

    print("🔄 Starting Data Cleaning and Masking Pipeline...")
    
    df = pd.read_csv(csv_path)
    # What it does: Reads the flat CSV file into memory as a 2D Pandas DataFrame.
    # Excel Analogy: File -> Open -> raw_banking_data.csv.

    # 1. Profile before changes
    profile_data(df)
    # Calls our audit function above to show the messy baseline state of the data.

    # 2. Deduplicate
    initial_count = len(df)
    # Stores row count before deduplication (e.g., 10,100).

    df = df.drop_duplicates(subset=["customer_id"])
    # What it does: Scans the 'customer_id' column for duplicate IDs. 
    #               Keeps the first occurrence, deletes any subsequent occurrences.
    # Excel Analogy: Data Tab -> Remove Duplicates -> Check ONLY 'customer_id'.

    print(f"✅ Removed {initial_count - len(df)} duplicate records.")
    # Math: (Initial rows - New row count) = Exactly how many duplicate rows got dropped.

    # 3. Handle missing values (Data Imputation / Governance)
    median_credit = df["credit_score"].median()
    # Math: Calculates the 50th percentile (Median) of all non-empty credit scores.
    # Data Science Note: We use median instead of mean (average) because median is 
    # resilient to extreme outliers (e.g., balances of -$500 or $1,000,000 don't skew it).
    # Excel Analogy: =MEDIAN(E:E)

    df["credit_score"] = df["credit_score"].fillna(median_credit)
    # .fillna(): Looks at the 'credit_score' column. Wherever there is a blank/NaN cell,
    #            it overwrites that blank with our calculated median number.
    # Excel Analogy: =IF(ISBLANK(E2), $Z$1, E2)

    df["email"] = df["email"].fillna("no_email_provided@domain.com")
    # Overwrites missing/blank email cells with a standard fallback placeholder string.
    # Excel Analogy: =IF(ISBLANK(D2), "no_email_provided@domain.com", D2)

    # 4. Apply PII Masking
    print("🔒 Masking Personally Identifiable Information (PII)...")

    df["masked_ssn"] = df["ssn"].apply(mask_ssn)
    # .apply(): A vectorized loop. It takes our custom Python function 'mask_ssn' 
    #           and passes each row's SSN value into it, one by one.
    # Result: Creates a brand-new column named 'masked_ssn'.
    # Excel Analogy: Writing a custom VBA function and dragging the formula down 10,000 rows.

    df["masked_account_number"] = df["account_number"].apply(mask_account_number)
    # Passes every row's 'account_number' to 'mask_account_number' and creates a new column.

    # Drop raw unmasked PII columns for compliance
    df = df.drop(columns=["ssn", "account_number"])
    # What it does: Permanently deletes the raw, sensitive columns from memory.
    # Excel Analogy: Right-clicking columns C & E -> Delete Column.

    print(f"✅ Pipeline completed. Clean dataset contains {len(df):,} records.\n")
    
    return df
    # Returns the fully cleaned, transformed DataFrame back to the caller.


# =========================================================================
# FUNCTION DEFINITION: load_to_sqlite
# -------------------------------------------------------------------------
# PURPOSE: Connects to a SQL database, enforces strict schema types (DDL), and saves the data.
# INPUT:   df: pd.DataFrame -> Cleaned data to persist.
#          db_path: str     -> Destination database path.
#          table_name: str  -> Name of SQL table to write to.
# OUTPUT:  None (Writes data to the physical disk).
# =========================================================================
def load_to_sqlite(df: pd.DataFrame, db_path: str, table_name: str):
    """Creates SQL DDL schema and loads masked data into SQLite database."""

    print(f"💾 Connecting to SQLite database: '{db_path}'...")

    conn = sqlite3.connect(db_path)
    # What it does: Opens a pipe/connection to the SQLite file. If the file doesn't exist, it creates it.

    cursor = conn.cursor()
    # Cursor: Think of the cursor as your "blinking text cursor" or "mouse pointer" inside the database.
    # It is the object that actually sends and executes commands against SQL.

    # DDL: Data Definition Language to define strict types
    create_table_query = f"""
    CREATE TABLE IF NOT EXISTS {table_name} (
        customer_id TEXT PRIMARY KEY,
        full_name TEXT NOT NULL,
        email TEXT,
        account_balance REAL NOT NULL,
        credit_score REAL NOT NULL,
        has_defaulted INTEGER NOT NULL,
        masked_ssn TEXT NOT NULL,
        masked_account_number TEXT NOT NULL
    );
    """
    # SQL Blueprint:
    # TEXT        = String / Text
    # REAL        = Floating-point decimal number (Math: Real number $\mathbb{R}$)
    # INTEGER     = Whole number (Math: Integer $\mathbb{Z}$)
    # PRIMARY KEY = Unique Identifier. Prevents duplicates forever at the database layer.
    # NOT NULL    = Mandatory cell (blank values will be rejected).

    cursor.execute(create_table_query)
    # Sends the CREATE TABLE instruction through the pipe to be executed.

    conn.commit()
    # Saves (commits) the structural change permanently to the database file.
    # Excel Analogy: Pressing Ctrl + S.

    print(f"✅ Schema verified for table '{table_name}'.")

    # Load cleaned DataFrame into SQL
    df.to_sql(table_name, conn, if_exists="replace", index=False)
    # What it does: High-speed bulk transfer from Pandas to SQLite.
    # if_exists="replace": Drops the table if it already had old data and replaces it fresh.
    # index=False        : Do not write the Pandas row numbers (0, 1, 2...) into the database.

    conn.commit()
    # Commits the row inserts to disk (Ctrl + S).

    # Verification Query
    cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
    # Asks SQL: "How many total rows did you actually save?"
    # Excel Analogy: =COUNTA(A:A)

    saved_count = cursor.fetchone()[0]
    # .fetchone() returns a tuple representing one database row: e.g., (10000,)
    # [0] pulls the integer out of the tuple: 10000.

    # Sample query to verify masked data
    cursor.execute(f"SELECT customer_id, full_name, masked_ssn, masked_account_number, credit_score FROM {table_name} LIMIT 3;")
    # Asks SQL to grab just the first 3 rows of specific columns to verify masking visually.

    samples = cursor.fetchall()
    # .fetchall() returns a list containing all 3 row tuples.

    conn.close()
    # What it does: Closes the database pipe cleanly so the file isn't locked by the OS.

    print(f"🎉 Successfully loaded {saved_count:,} records into SQL table '{table_name}'.\n")
    print("Sample Loaded Rows (showing masked PII):")

    for row in samples:
        print(f"  {row}")
        # Prints each of the 3 sampled rows to verify they have masked asterisks.


# -------------------------------------------------------------------------
# EXECUTION ENTRY POINT (The "Green Run Button")
# -------------------------------------------------------------------------
if __name__ == "__main__":
    # What it does: A standard Python safety check. 
    # It means: "Only execute the code below if this script is being run DIRECTLY."
    # (If someone imports this script into another file to borrow a function, 
    # it won't accidentally trigger the whole pipeline).

    clean_df = clean_and_mask_pipeline(CSV_PATH)
    # Step 1: Run the pipeline function on the CSV file, storing the clean result in 'clean_df'.

    load_to_sqlite(clean_df, DB_PATH, TABLE_NAME)
    # Step 2: Pass that clean DataFrame into our SQL loader function to write it to disk.