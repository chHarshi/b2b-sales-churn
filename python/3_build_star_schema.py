import pandas as pd
from pathlib import Path


# ============================================================
# PATHS
# ============================================================

PROCESSED_PATH = Path("data/processed")
MODEL_PATH = Path("data/model")

# Create model folder
MODEL_PATH.mkdir(parents=True, exist_ok=True)


print("=" * 70)
print("BUILDING ADVENTUREWORKS STAR SCHEMA")
print("=" * 70)


# ============================================================
# 1. LOAD CLEANED DATA
# ============================================================

print("\nLoading cleaned datasets...")

calendar = pd.read_csv(
    PROCESSED_PATH / "calendar_clean.csv",
    parse_dates=["Date"]
)

customers = pd.read_csv(
    PROCESSED_PATH / "customers_clean.csv"
)

products = pd.read_csv(
    PROCESSED_PATH / "products_clean.csv"
)

categories = pd.read_csv(
    PROCESSED_PATH / "product_categories_clean.csv"
)

subcategories = pd.read_csv(
    PROCESSED_PATH / "product_subcategories_clean.csv"
)

sales = pd.read_csv(
    PROCESSED_PATH / "sales_clean.csv",
    parse_dates=["OrderDate", "StockDate"]
)

territories = pd.read_csv(
    PROCESSED_PATH / "territories_clean.csv"
)


# ============================================================
# 2. CREATE DIM_DATE
# ============================================================

print("\nCreating DIM_DATE...")

dim_date = calendar.copy()

dim_date["DateKey"] = dim_date["Date"].dt.strftime("%Y%m%d").astype(int)

# Reorder columns
dim_date = dim_date[
    [
        "DateKey",
        "Date",
        "Year",
        "Quarter",
        "Month",
        "MonthName",
        "Day"
    ]
]

print(f"DIM_DATE rows: {len(dim_date)}")


# ============================================================
# 3. CREATE DIM_CUSTOMER
# ============================================================

print("\nCreating DIM_CUSTOMER...")

dim_customer = customers.copy()

print(f"DIM_CUSTOMER rows: {len(dim_customer)}")
print("Customer columns:")
print(list(dim_customer.columns))


# ============================================================
# 4. CREATE DIM_PRODUCT
# ============================================================

print("\nCreating DIM_PRODUCT...")

# Join Products → Subcategories
dim_product = products.merge(
    subcategories,
    on="ProductSubcategoryKey",
    how="left"
)

# Join Subcategories → Categories
dim_product = dim_product.merge(
    categories,
    on="ProductCategoryKey",
    how="left"
)

# Rename for clarity
dim_product = dim_product.rename(
    columns={
        "CategoryName": "ProductCategory",
        "SubcategoryName": "ProductSubcategory"
    }
)

print(f"DIM_PRODUCT rows: {len(dim_product)}")


# ============================================================
# 5. CREATE DIM_TERRITORY
# ============================================================

print("\nCreating DIM_TERRITORY...")

dim_territory = territories.rename(
    columns={
        "SalesTerritoryKey": "TerritoryKey"
    }
)

print(f"DIM_TERRITORY rows: {len(dim_territory)}")


# ============================================================
# 6. CREATE FACT_SALES
# ============================================================

print("\nCreating FACT_SALES...")

fact_sales = sales.copy()

# Create DateKey
fact_sales["DateKey"] = (
    fact_sales["OrderDate"]
    .dt.strftime("%Y%m%d")
    .astype(int)
)

# Join Product Price and Cost
product_financials = dim_product[
    [
        "ProductKey",
        "ProductCost",
        "ProductPrice"
    ]
]

fact_sales = fact_sales.merge(
    product_financials,
    on="ProductKey",
    how="left"
)

# Calculate Revenue
fact_sales["Revenue"] = (
    fact_sales["OrderQuantity"]
    * fact_sales["ProductPrice"]
)

# Calculate Cost
fact_sales["TotalCost"] = (
    fact_sales["OrderQuantity"]
    * fact_sales["ProductCost"]
)

# Calculate Profit
fact_sales["Profit"] = (
    fact_sales["Revenue"]
    - fact_sales["TotalCost"]
)

# Select final columns
fact_sales = fact_sales[
    [
        "OrderNumber",
        "OrderLineItem",
        "DateKey",
        "OrderDate",
        "StockDate",
        "ProductKey",
        "CustomerKey",
        "TerritoryKey",
        "OrderQuantity",
        "ProductPrice",
        "ProductCost",
        "Revenue",
        "TotalCost",
        "Profit"
    ]
]

print(f"FACT_SALES rows: {len(fact_sales)}")


# ============================================================
# 7. DATA QUALITY CHECKS
# ============================================================

print("\n" + "=" * 70)
print("DATA QUALITY CHECKS")
print("=" * 70)

print("\nMissing values in FACT_SALES:")
print(fact_sales.isnull().sum())

print("\nNegative Revenue:")
print((fact_sales["Revenue"] < 0).sum())

print("\nNegative Profit:")
print((fact_sales["Profit"] < 0).sum())

print("\nTotal Revenue:")
print(f"${fact_sales['Revenue'].sum():,.2f}")

print("\nTotal Profit:")
print(f"${fact_sales['Profit'].sum():,.2f}")


# ============================================================
# 8. SAVE STAR SCHEMA TABLES
# ============================================================

print("\nSaving Star Schema tables...")

dim_date.to_csv(
    MODEL_PATH / "dim_date.csv",
    index=False
)

dim_customer.to_csv(
    MODEL_PATH / "dim_customer.csv",
    index=False
)

dim_product.to_csv(
    MODEL_PATH / "dim_product.csv",
    index=False
)

dim_territory.to_csv(
    MODEL_PATH / "dim_territory.csv",
    index=False
)

fact_sales.to_csv(
    MODEL_PATH / "fact_sales.csv",
    index=False
)


# ============================================================
# FINAL SUMMARY
# ============================================================

print("\n" + "=" * 70)
print("STAR SCHEMA CREATED SUCCESSFULLY")
print("=" * 70)

print(f"\nDIM_DATE       : {len(dim_date):,} rows")
print(f"DIM_CUSTOMER   : {len(dim_customer):,} rows")
print(f"DIM_PRODUCT    : {len(dim_product):,} rows")
print(f"DIM_TERRITORY  : {len(dim_territory):,} rows")
print(f"FACT_SALES     : {len(fact_sales):,} rows")

print("\nFiles saved to:")
print(MODEL_PATH.resolve())

print("\n" + "=" * 70)