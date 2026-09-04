import pandas as pd
from pathlib import Path


# ============================================================
# PATHS
# ============================================================

RAW_PATH = Path("data/raw")
PROCESSED_PATH = Path("data/processed")

# Create processed folder if it doesn't exist
PROCESSED_PATH.mkdir(parents=True, exist_ok=True)


# ============================================================
# HELPER FUNCTION
# ============================================================

def read_csv_safely(file_path):
    """
    Try different encodings to read CSV files.
    """

    encodings = ["utf-8", "latin1", "cp1252"]

    for encoding in encodings:
        try:
            df = pd.read_csv(file_path, encoding=encoding)
            print(f"Successfully read {file_path.name} using {encoding}")
            return df

        except UnicodeDecodeError:
            continue

    raise ValueError(f"Could not read {file_path.name}")


# ============================================================
# PROJECT HEADER
# ============================================================

print("=" * 70)
print("ADVENTUREWORKS DATA CLEANING")
print("=" * 70)


# ============================================================
# 1. CLEAN CALENDAR
# ============================================================

print("\n[1/9] Cleaning Calendar...")

calendar = read_csv_safely(
    RAW_PATH / "AdventureWorks_Calendar.csv"
)

calendar["Date"] = pd.to_datetime(
    calendar["Date"],
    format="%m/%d/%Y"
)

# Add useful date columns
calendar["Year"] = calendar["Date"].dt.year
calendar["Month"] = calendar["Date"].dt.month
calendar["MonthName"] = calendar["Date"].dt.month_name()
calendar["Quarter"] = "Q" + calendar["Date"].dt.quarter.astype(str)
calendar["Day"] = calendar["Date"].dt.day

print(f"Calendar rows: {len(calendar)}")


# ============================================================
# 2. CLEAN CUSTOMERS
# ============================================================

print("\n[2/9] Cleaning Customers...")

customers = read_csv_safely(
    RAW_PATH / "AdventureWorks_Customers.csv"
)

print(f"Customer rows before cleaning: {len(customers)}")

# Remove completely duplicated rows
customers = customers.drop_duplicates()

print(f"Customer rows after cleaning: {len(customers)}")


# ============================================================
# 3. CLEAN PRODUCT CATEGORIES
# ============================================================

print("\n[3/9] Cleaning Product Categories...")

categories = read_csv_safely(
    RAW_PATH / "AdventureWorks_Product_Categories.csv"
)

categories = categories.drop_duplicates()


# ============================================================
# 4. CLEAN PRODUCT SUBCATEGORIES
# ============================================================

print("\n[4/9] Cleaning Product Subcategories...")

subcategories = read_csv_safely(
    RAW_PATH / "AdventureWorks_Product_Subcategories.csv"
)

subcategories = subcategories.drop_duplicates()


# ============================================================
# 5. CLEAN PRODUCTS
# ============================================================

print("\n[5/9] Cleaning Products...")

products = read_csv_safely(
    RAW_PATH / "AdventureWorks_Products.csv"
)

products = products.drop_duplicates()

# Replace missing product colors
products["ProductColor"] = products["ProductColor"].fillna("Unknown")

print(f"Products: {len(products)}")
print(f"Missing ProductColor: {products['ProductColor'].isnull().sum()}")


# ============================================================
# 6. COMBINE SALES FILES
# ============================================================

print("\n[6/9] Combining Sales Files...")

sales_2015 = read_csv_safely(
    RAW_PATH / "AdventureWorks_Sales_2015.csv"
)

sales_2016 = read_csv_safely(
    RAW_PATH / "AdventureWorks_Sales_2016.csv"
)

sales_2017 = read_csv_safely(
    RAW_PATH / "AdventureWorks_Sales_2017.csv"
)

# Combine all years
sales = pd.concat(
    [sales_2015, sales_2016, sales_2017],
    ignore_index=True
)

print(f"Total sales rows before cleaning: {len(sales)}")

# Convert date columns
sales["OrderDate"] = pd.to_datetime(
    sales["OrderDate"],
    format="%m/%d/%Y"
)

sales["StockDate"] = pd.to_datetime(
    sales["StockDate"],
    format="%m/%d/%Y"
)

# Remove duplicates
sales = sales.drop_duplicates()

# Remove invalid quantities
sales = sales[sales["OrderQuantity"] > 0]

print(f"Total sales rows after cleaning: {len(sales)}")

print(f"Date range: {sales['OrderDate'].min()} to {sales['OrderDate'].max()}")


# ============================================================
# 7. CLEAN RETURNS
# ============================================================

print("\n[7/9] Cleaning Returns...")

returns = read_csv_safely(
    RAW_PATH / "AdventureWorks_Returns.csv"
)

returns["ReturnDate"] = pd.to_datetime(
    returns["ReturnDate"],
    format="%m/%d/%Y"
)

returns = returns.drop_duplicates()

# Keep only valid return quantities
returns = returns[returns["ReturnQuantity"] > 0]

print(f"Returns rows: {len(returns)}")


# ============================================================
# 8. CLEAN TERRITORIES
# ============================================================

print("\n[8/9] Cleaning Territories...")

territories = read_csv_safely(
    RAW_PATH / "AdventureWorks_Territories.csv"
)

territories = territories.drop_duplicates()

print(f"Territories: {len(territories)}")


# ============================================================
# 9. SAVE CLEANED FILES
# ============================================================

print("\n[9/9] Saving Cleaned Files...")

calendar.to_csv(
    PROCESSED_PATH / "calendar_clean.csv",
    index=False
)

customers.to_csv(
    PROCESSED_PATH / "customers_clean.csv",
    index=False
)

categories.to_csv(
    PROCESSED_PATH / "product_categories_clean.csv",
    index=False
)

subcategories.to_csv(
    PROCESSED_PATH / "product_subcategories_clean.csv",
    index=False
)

products.to_csv(
    PROCESSED_PATH / "products_clean.csv",
    index=False
)

sales.to_csv(
    PROCESSED_PATH / "sales_clean.csv",
    index=False
)

returns.to_csv(
    PROCESSED_PATH / "returns_clean.csv",
    index=False
)

territories.to_csv(
    PROCESSED_PATH / "territories_clean.csv",
    index=False
)


# ============================================================
# SUMMARY
# ============================================================

print("\n" + "=" * 70)
print("DATA CLEANING COMPLETE")
print("=" * 70)

print("\nCLEANED DATA SUMMARY")

print(f"Calendar      : {len(calendar):,} rows")
print(f"Customers     : {len(customers):,} rows")
print(f"Categories    : {len(categories):,} rows")
print(f"Subcategories : {len(subcategories):,} rows")
print(f"Products      : {len(products):,} rows")
print(f"Sales         : {len(sales):,} rows")
print(f"Returns       : {len(returns):,} rows")
print(f"Territories   : {len(territories):,} rows")

print("\nCleaned files saved successfully to:")
print(PROCESSED_PATH.resolve())

print("\n" + "=" * 70)