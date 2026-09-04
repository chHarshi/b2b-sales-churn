import pandas as pd
from pathlib import Path


# ============================================================
# PATHS
# ============================================================

MODEL_PATH = Path("data/model")

OUTPUT_PATH = Path("data/processed")

OUTPUT_PATH.mkdir(parents=True, exist_ok=True)


# ============================================================
# LOAD DATA
# ============================================================

print("=" * 70)
print("CUSTOMER RFM ANALYSIS")
print("=" * 70)

fact_sales = pd.read_csv(
    MODEL_PATH / "fact_sales.csv",
    parse_dates=["OrderDate"]
)

customers = pd.read_csv(
    MODEL_PATH / "dim_customer.csv"
)


# ============================================================
# ANALYSIS DATE
# ============================================================

analysis_date = fact_sales["OrderDate"].max()

print(f"\nLatest transaction date: {analysis_date}")


# ============================================================
# CALCULATE RFM
# ============================================================

print("\nCalculating RFM metrics...")


rfm = fact_sales.groupby("CustomerKey").agg(

    LastPurchaseDate=("OrderDate", "max"),

    Frequency=("OrderNumber", "nunique"),

    Monetary=("Revenue", "sum")

).reset_index()


# ============================================================
# RECENCY
# ============================================================

rfm["Recency"] = (
    analysis_date - rfm["LastPurchaseDate"]
).dt.days


# ============================================================
# SELECT RFM COLUMNS
# ============================================================

rfm = rfm[
    [
        "CustomerKey",
        "LastPurchaseDate",
        "Recency",
        "Frequency",
        "Monetary"
    ]
]


# ============================================================
# RFM SCORES
# ============================================================

print("\nCreating RFM scores...")


# Recency:
# Lower number of days = better
rfm["R_Score"] = pd.qcut(
    rfm["Recency"].rank(method="first"),
    5,
    labels=[5, 4, 3, 2, 1]
).astype(int)


# Frequency:
# Higher number = better
rfm["F_Score"] = pd.qcut(
    rfm["Frequency"].rank(method="first"),
    5,
    labels=[1, 2, 3, 4, 5]
).astype(int)


# Monetary:
# Higher revenue = better
rfm["M_Score"] = pd.qcut(
    rfm["Monetary"].rank(method="first"),
    5,
    labels=[1, 2, 3, 4, 5]
).astype(int)


# Combined score
rfm["RFM_Score"] = (
    rfm["R_Score"].astype(str)
    + rfm["F_Score"].astype(str)
    + rfm["M_Score"].astype(str)
)


# Numeric overall score
rfm["RFM_Total"] = (
    rfm["R_Score"]
    + rfm["F_Score"]
    + rfm["M_Score"]
)


# ============================================================
# CUSTOMER SEGMENTS
# ============================================================

def assign_segment(row):

    r = row["R_Score"]
    f = row["F_Score"]
    m = row["M_Score"]

    if r >= 4 and f >= 4 and m >= 4:
        return "Champions"

    elif r >= 4 and f >= 3:
        return "Loyal Customers"

    elif r >= 4 and f <= 2:
        return "Potential Loyalists"

    elif r <= 2 and f >= 4:
        return "At Risk"

    elif r <= 2 and f <= 2:
        return "Lost Customers"

    else:
        return "Needs Attention"


rfm["CustomerSegment"] = rfm.apply(
    assign_segment,
    axis=1
)


# ============================================================
# ADD CUSTOMER INFORMATION
# ============================================================

print("\nAdding customer information...")

customer_columns = [
    "CustomerKey",
    "FirstName",
    "LastName",
    "Gender",
    "AnnualIncome",
    "Occupation"
]

rfm = rfm.merge(
    customers[customer_columns],
    on="CustomerKey",
    how="left"
)


# ============================================================
# SUMMARY
# ============================================================

print("\n" + "=" * 70)
print("RFM SUMMARY")
print("=" * 70)

print("\nCustomer segments:")

segment_summary = (
    rfm["CustomerSegment"]
    .value_counts()
)

print(segment_summary)


print("\nTotal customers analyzed:")
print(f"{len(rfm):,}")


print("\nTotal customer revenue:")
print(f"${rfm['Monetary'].sum():,.2f}")


# ============================================================
# TOP CUSTOMERS
# ============================================================

print("\nTop 10 customers by revenue:")

top_customers = rfm.sort_values(
    "Monetary",
    ascending=False
).head(10)

print(
    top_customers[
        [
            "CustomerKey",
            "FirstName",
            "LastName",
            "Frequency",
            "Monetary",
            "CustomerSegment"
        ]
    ].to_string(index=False)
)


# ============================================================
# SAVE
# ============================================================

output_file = OUTPUT_PATH / "customer_rfm.csv"

rfm.to_csv(
    output_file,
    index=False
)


print("\n" + "=" * 70)
print("RFM ANALYSIS COMPLETE")
print("=" * 70)

print(f"\nSaved to:")
print(output_file.resolve())