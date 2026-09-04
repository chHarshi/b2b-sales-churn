import pandas as pd
from pathlib import Path


# ============================================================
# PATHS
# ============================================================

MODEL_PATH = Path("data/model")
PROCESSED_PATH = Path("data/processed")

PROCESSED_PATH.mkdir(parents=True, exist_ok=True)


# ============================================================
# HEADER
# ============================================================

print("=" * 70)
print("CUSTOMER CHURN RISK ANALYSIS")
print("=" * 70)


# ============================================================
# LOAD DATA
# ============================================================

print("\nLoading data...")

fact_sales = pd.read_csv(
    MODEL_PATH / "fact_sales.csv",
    parse_dates=["OrderDate"]
)

rfm = pd.read_csv(
    PROCESSED_PATH / "customer_rfm.csv",
    parse_dates=["LastPurchaseDate"]
)

print(f"Sales records loaded : {len(fact_sales):,}")
print(f"Customers loaded     : {len(rfm):,}")


# ============================================================
# ANALYSIS DATE
# ============================================================

analysis_date = fact_sales["OrderDate"].max()

print(f"\nAnalysis date: {analysis_date.date()}")


# ============================================================
# DEFINE TWO 90-DAY PERIODS
# ============================================================

recent_start = analysis_date - pd.Timedelta(days=90)

previous_start = analysis_date - pd.Timedelta(days=180)

print(
    f"Recent period     : "
    f"{recent_start.date()} to {analysis_date.date()}"
)

print(
    f"Previous period   : "
    f"{previous_start.date()} to {recent_start.date()}"
)


# ============================================================
# RECENT 90 DAYS
# ============================================================

recent_sales = fact_sales[
    fact_sales["OrderDate"] > recent_start
].copy()

recent_metrics = recent_sales.groupby(
    "CustomerKey"
).agg(
    RecentOrders=("OrderNumber", "nunique"),
    RecentRevenue=("Revenue", "sum")
).reset_index()


# ============================================================
# PREVIOUS 90 DAYS
# ============================================================

previous_sales = fact_sales[
    (fact_sales["OrderDate"] > previous_start)
    & (fact_sales["OrderDate"] <= recent_start)
].copy()

previous_metrics = previous_sales.groupby(
    "CustomerKey"
).agg(
    PreviousOrders=("OrderNumber", "nunique"),
    PreviousRevenue=("Revenue", "sum")
).reset_index()


# ============================================================
# MERGE CUSTOMER METRICS
# ============================================================

churn = rfm.merge(
    recent_metrics,
    on="CustomerKey",
    how="left"
)

churn = churn.merge(
    previous_metrics,
    on="CustomerKey",
    how="left"
)


# ============================================================
# FILL MISSING ACTIVITY WITH ZERO
# ============================================================

activity_columns = [
    "RecentOrders",
    "RecentRevenue",
    "PreviousOrders",
    "PreviousRevenue"
]

churn[activity_columns] = (
    churn[activity_columns].fillna(0)
)


# ============================================================
# CALCULATE ORDER CHANGE
# ============================================================

def calculate_change(recent, previous):

    if previous == 0:
        return 0.0

    return (recent - previous) / previous


churn["OrderFrequencyChange"] = churn.apply(
    lambda row: calculate_change(
        row["RecentOrders"],
        row["PreviousOrders"]
    ),
    axis=1
)


# ============================================================
# CALCULATE REVENUE CHANGE
# ============================================================

churn["RevenueChange"] = churn.apply(
    lambda row: calculate_change(
        row["RecentRevenue"],
        row["PreviousRevenue"]
    ),
    axis=1
)


# ============================================================
# HIGH-VALUE CUSTOMER THRESHOLD
# ============================================================

high_value_threshold = (
    churn["Monetary"].quantile(0.75)
)

print(
    f"\nHigh-value customer threshold: "
    f"${high_value_threshold:,.2f}"
)


# ============================================================
# RECENCY SCORE
# ============================================================

def recency_score(days):

    if days <= 60:
        return 0

    elif days <= 90:
        return 10

    elif days <= 120:
        return 20

    elif days <= 180:
        return 30

    else:
        return 40


churn["RecencyRisk"] = (
    churn["Recency"]
    .apply(recency_score)
)


# ============================================================
# FREQUENCY DECLINE SCORE
# ============================================================

def frequency_risk(row):

    recent = row["RecentOrders"]
    previous = row["PreviousOrders"]

    # No comparison history
    if previous == 0:
        return 0

    decline = row["OrderFrequencyChange"]

    if decline <= -0.75:
        return 25

    elif decline <= -0.50:
        return 20

    elif decline <= -0.25:
        return 10

    elif decline < 0:
        return 5

    return 0


churn["FrequencyRisk"] = churn.apply(
    frequency_risk,
    axis=1
)


# ============================================================
# REVENUE DECLINE SCORE
# ============================================================

def revenue_risk(row):

    previous_revenue = row["PreviousRevenue"]

    if previous_revenue == 0:
        return 0

    decline = row["RevenueChange"]

    if decline <= -0.75:
        return 20

    elif decline <= -0.50:
        return 15

    elif decline <= -0.25:
        return 10

    elif decline < 0:
        return 5

    return 0


churn["RevenueRisk"] = churn.apply(
    revenue_risk,
    axis=1
)


# ============================================================
# HIGH VALUE RISK
# ============================================================

churn["HighValueRisk"] = (
    churn["Monetary"] >= high_value_threshold
).astype(int) * 5


# ============================================================
# TOTAL CHURN SCORE
# ============================================================

churn["ChurnRiskScore"] = (
    churn["RecencyRisk"]
    + churn["FrequencyRisk"]
    + churn["RevenueRisk"]
    + churn["HighValueRisk"]
)


# ============================================================
# RISK LEVEL
# ============================================================

def assign_risk(score):

    if score < 20:
        return "Healthy"

    elif score < 40:
        return "Monitor"

    elif score < 60:
        return "At Risk"

    else:
        return "Critical"


churn["ChurnRiskLevel"] = (
    churn["ChurnRiskScore"]
    .apply(assign_risk)
)


# ============================================================
# REVENUE DECLINE VALUE
# ============================================================

churn["RevenueDeclineValue"] = 0.0

valid_previous = (
    churn["PreviousRevenue"] > 0
)

churn.loc[
    valid_previous,
    "RevenueDeclineValue"
] = (
    churn.loc[
        valid_previous,
        "PreviousRevenue"
    ]
    - churn.loc[
        valid_previous,
        "RecentRevenue"
    ]
).clip(lower=0)


# ============================================================
# REVENUE AT RISK
# ============================================================
#
# Only customers classified as At Risk or Critical
# contribute to the estimated revenue exposure.
#
# We use the positive decline between the previous
# 90-day period and recent 90-day period.
#

churn["RevenueAtRisk"] = 0.0

risk_customers = churn[
    "ChurnRiskLevel"
].isin(["At Risk", "Critical"])

churn.loc[
    risk_customers,
    "RevenueAtRisk"
] = churn.loc[
    risk_customers,
    "RevenueDeclineValue"
]


# ============================================================
# PRIORITY SCORE
# ============================================================
#
# Higher risk + higher revenue exposure = higher priority.
#

churn["PriorityScore"] = (
    churn["ChurnRiskScore"]
    * churn["RevenueAtRisk"]
)


# ============================================================
# SUMMARY
# ============================================================

print("\n" + "=" * 70)
print("CHURN RISK SUMMARY")
print("=" * 70)


# ------------------------------------------------------------
# Customer count
# ------------------------------------------------------------

print("\nCustomers by risk level:")

risk_summary = (
    churn["ChurnRiskLevel"]
    .value_counts()
)

print(risk_summary)


# ------------------------------------------------------------
# Percentage
# ------------------------------------------------------------

print("\nRisk level percentages:")

risk_percentage = (
    churn["ChurnRiskLevel"]
    .value_counts(normalize=True)
    .mul(100)
    .round(2)
)

print(risk_percentage)


# ------------------------------------------------------------
# Revenue exposure
# ------------------------------------------------------------

print("\nEstimated revenue at risk:")

print(
    f"${churn['RevenueAtRisk'].sum():,.2f}"
)


# ------------------------------------------------------------
# Customers requiring attention
# ------------------------------------------------------------

customers_requiring_attention = churn[
    churn["ChurnRiskLevel"].isin(
        ["At Risk", "Critical"]
    )
]

print("\nCustomers requiring attention:")

print(
    f"{len(customers_requiring_attention):,}"
)


# ============================================================
# TOP PRIORITY CUSTOMERS
# ============================================================

print("\n" + "=" * 70)
print("TOP 10 HIGHEST-PRIORITY CUSTOMERS")
print("=" * 70)

top_priority = (
    churn[
        churn["RevenueAtRisk"] > 0
    ]
    .sort_values(
        "PriorityScore",
        ascending=False
    )
    .head(10)
)


print(
    top_priority[
        [
            "CustomerKey",
            "FirstName",
            "LastName",
            "Recency",
            "Frequency",
            "Monetary",
            "RecentOrders",
            "PreviousOrders",
            "OrderFrequencyChange",
            "RevenueChange",
            "ChurnRiskScore",
            "ChurnRiskLevel",
            "RevenueAtRisk"
        ]
    ].to_string(index=False)
)


# ============================================================
# TOP REVENUE AT RISK
# ============================================================

print("\n" + "=" * 70)
print("TOP 10 CUSTOMERS BY REVENUE AT RISK")
print("=" * 70)

top_revenue_risk = (
    churn[
        churn["RevenueAtRisk"] > 0
    ]
    .sort_values(
        "RevenueAtRisk",
        ascending=False
    )
    .head(10)
)


print(
    top_revenue_risk[
        [
            "CustomerKey",
            "FirstName",
            "LastName",
            "Recency",
            "Frequency",
            "Monetary",
            "RevenueChange",
            "ChurnRiskScore",
            "ChurnRiskLevel",
            "RevenueAtRisk"
        ]
    ].to_string(index=False)
)


# ============================================================
# SAVE FILE
# ============================================================

output_file = (
    PROCESSED_PATH
    / "customer_churn_risk.csv"
)

churn.to_csv(
    output_file,
    index=False
)


# ============================================================
# FINAL MESSAGE
# ============================================================

print("\n" + "=" * 70)
print("CHURN ANALYSIS COMPLETE")
print("=" * 70)

print("\nSaved to:")
print(output_file.resolve())

print("\nOutput columns:")
print(list(churn.columns))

print("\n" + "=" * 70)