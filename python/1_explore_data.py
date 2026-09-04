import pandas as pd
from pathlib import Path

# Location of raw CSV files
DATA_PATH = Path("data/raw")

print("=" * 70)
print("ADVENTUREWORKS DATASET EXPLORATION")
print("=" * 70)

# Find all CSV files
files = list(DATA_PATH.glob("*.csv"))

print(f"\nFound {len(files)} CSV files.\n")

for file in files:
    print("\n" + "-" * 70)
    print(f"FILE: {file.name}")
    print("-" * 70)

    try:
        # Read CSV file
        df = pd.read_csv(file)

        print(f"Rows    : {df.shape[0]}")
        print(f"Columns : {df.shape[1]}")

        print("\nColumn Names:")
        print(list(df.columns))

        print("\nFirst 5 rows:")
        print(df.head())

        print("\nData Types:")
        print(df.dtypes)

        print("\nMissing Values:")
        print(df.isnull().sum())

        print(f"\nDuplicate Rows: {df.duplicated().sum()}")

    except Exception as e:
        print(f"ERROR reading {file.name}: {e}")

print("\n" + "=" * 70)
print("EXPLORATION COMPLETE")
print("=" * 70)