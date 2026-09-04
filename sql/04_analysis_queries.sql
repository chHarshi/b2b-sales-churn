-- ============================================================
-- ADVENTUREWORKS B2B SALES & CUSTOMER CHURN INTELLIGENCE
-- BUSINESS ANALYSIS QUERIES
-- ============================================================

USE b2b_sales_churn;


-- ============================================================
-- 1. OVERALL BUSINESS PERFORMANCE
-- ============================================================

SELECT
    COUNT(DISTINCT OrderNumber) AS TotalOrders,
    COUNT(DISTINCT CustomerKey) AS TotalCustomers,
    SUM(OrderQuantity) AS UnitsSold,
    ROUND(SUM(Revenue), 2) AS TotalRevenue,
    ROUND(SUM(TotalCost), 2) AS TotalCost,
    ROUND(SUM(Profit), 2) AS TotalProfit,
    ROUND(
        SUM(Profit) / NULLIF(SUM(Revenue), 0) * 100,
        2
    ) AS ProfitMarginPct
FROM fact_sales;


-- ============================================================
-- 2. YEARLY SALES PERFORMANCE
-- ============================================================

SELECT
    d.Year,
    COUNT(DISTINCT f.OrderNumber) AS TotalOrders,
    COUNT(DISTINCT f.CustomerKey) AS Customers,
    ROUND(SUM(f.Revenue), 2) AS Revenue,
    ROUND(SUM(f.Profit), 2) AS Profit,
    ROUND(
        SUM(f.Profit) / NULLIF(SUM(f.Revenue), 0) * 100,
        2
    ) AS ProfitMarginPct
FROM fact_sales f
JOIN dim_date d
    ON f.DateKey = d.DateKey
GROUP BY d.Year
ORDER BY d.Year;


-- ============================================================
-- 3. MONTHLY REVENUE TREND
-- ============================================================

SELECT
    d.Year,
    d.Month,
    d.MonthName,
    ROUND(SUM(f.Revenue), 2) AS Revenue,
    ROUND(SUM(f.Profit), 2) AS Profit
FROM fact_sales f
JOIN dim_date d
    ON f.DateKey = d.DateKey
GROUP BY
    d.Year,
    d.Month,
    d.MonthName
ORDER BY
    d.Year,
    d.Month;


-- ============================================================
-- 4. TERRITORY PERFORMANCE
-- ============================================================

SELECT
    t.Region,
    t.Country,
    t.Continent,

    COUNT(DISTINCT f.CustomerKey) AS Customers,

    COUNT(DISTINCT f.OrderNumber) AS Orders,

    ROUND(SUM(f.Revenue), 2) AS Revenue,

    ROUND(SUM(f.Profit), 2) AS Profit,

    ROUND(
        SUM(f.Profit) /
        NULLIF(SUM(f.Revenue), 0) * 100,
        2
    ) AS ProfitMarginPct

FROM fact_sales f

JOIN dim_territory t
    ON f.TerritoryKey = t.TerritoryKey

GROUP BY
    t.Region,
    t.Country,
    t.Continent

ORDER BY Revenue DESC;


-- ============================================================
-- 5. PRODUCT PERFORMANCE
-- ============================================================

SELECT
    p.ProductKey,
    p.ProductName,
    p.ProductSubcategory,
    p.ProductCategory,

    SUM(f.OrderQuantity) AS UnitsSold,

    COUNT(DISTINCT f.OrderNumber) AS Orders,

    ROUND(SUM(f.Revenue), 2) AS Revenue,

    ROUND(SUM(f.Profit), 2) AS Profit,

    ROUND(
        SUM(f.Profit) /
        NULLIF(SUM(f.Revenue), 0) * 100,
        2
    ) AS ProfitMarginPct

FROM fact_sales f

JOIN dim_product p
    ON f.ProductKey = p.ProductKey

GROUP BY
    p.ProductKey,
    p.ProductName,
    p.ProductSubcategory,
    p.ProductCategory

ORDER BY Revenue DESC;


-- ============================================================
-- 6. PRODUCT CATEGORY PERFORMANCE
-- ============================================================

SELECT
    p.ProductCategory,

    SUM(f.OrderQuantity) AS UnitsSold,

    COUNT(DISTINCT f.OrderNumber) AS Orders,

    ROUND(SUM(f.Revenue), 2) AS Revenue,

    ROUND(SUM(f.Profit), 2) AS Profit,

    ROUND(
        SUM(f.Profit) /
        NULLIF(SUM(f.Revenue), 0) * 100,
        2
    ) AS ProfitMarginPct

FROM fact_sales f

JOIN dim_product p
    ON f.ProductKey = p.ProductKey

GROUP BY p.ProductCategory

ORDER BY Revenue DESC;


-- ============================================================
-- 7. TOP 20 CUSTOMERS BY REVENUE
-- ============================================================

SELECT
    c.CustomerKey,

    CONCAT(
        c.FirstName,
        ' ',
        c.LastName
    ) AS CustomerName,

    c.Occupation,

    COUNT(DISTINCT f.OrderNumber) AS Orders,

    ROUND(SUM(f.Revenue), 2) AS Revenue,

    ROUND(SUM(f.Profit), 2) AS Profit

FROM fact_sales f

JOIN dim_customer c
    ON f.CustomerKey = c.CustomerKey

GROUP BY
    c.CustomerKey,
    c.FirstName,
    c.LastName,
    c.Occupation

ORDER BY Revenue DESC

LIMIT 20;


-- ============================================================
-- 8. RFM CUSTOMER SEGMENTATION
-- ============================================================

SELECT
    CustomerSegment,

    COUNT(*) AS Customers,

    ROUND(
        COUNT(*) /
        (SELECT COUNT(*) FROM customer_rfm) * 100,
        2
    ) AS CustomerPct,

    ROUND(SUM(Monetary), 2) AS Revenue

FROM customer_rfm

GROUP BY CustomerSegment

ORDER BY Revenue DESC;


-- ============================================================
-- 9. CHURN RISK DISTRIBUTION
-- ============================================================

SELECT
    ChurnRiskLevel,

    COUNT(*) AS Customers,

    ROUND(
        COUNT(*) /
        (SELECT COUNT(*) FROM customer_churn_risk) * 100,
        2
    ) AS CustomerPct,

    ROUND(SUM(RevenueAtRisk), 2) AS RevenueAtRisk

FROM customer_churn_risk

GROUP BY ChurnRiskLevel

ORDER BY
    CASE ChurnRiskLevel
        WHEN 'Critical' THEN 1
        WHEN 'At Risk' THEN 2
        WHEN 'Monitor' THEN 3
        WHEN 'Healthy' THEN 4
    END;


-- ============================================================
-- 10. TOP CUSTOMERS BY REVENUE AT RISK
-- ============================================================

SELECT
    CustomerKey,

    CONCAT(
        FirstName,
        ' ',
        LastName
    ) AS CustomerName,

    CustomerSegment,

    Recency,

    Frequency,

    ROUND(Monetary, 2) AS LifetimeRevenue,

    RecentOrders,

    PreviousOrders,

    ROUND(
        RevenueChange * 100,
        2
    ) AS RevenueChangePct,

    ChurnRiskScore,

    ChurnRiskLevel,

    ROUND(RevenueAtRisk, 2) AS RevenueAtRisk,

    ROUND(PriorityScore, 2) AS PriorityScore

FROM customer_churn_risk

WHERE ChurnRiskLevel IN ('At Risk', 'Critical')

ORDER BY RevenueAtRisk DESC

LIMIT 20;


-- ============================================================
-- 11. HIGH-PRIORITY CUSTOMERS
-- ============================================================

SELECT
    CustomerKey,

    CONCAT(
        FirstName,
        ' ',
        LastName
    ) AS CustomerName,

    CustomerSegment,

    Recency,

    Frequency,

    ROUND(Monetary, 2) AS LifetimeRevenue,

    ChurnRiskScore,

    ChurnRiskLevel,

    ROUND(RevenueAtRisk, 2) AS RevenueAtRisk,

    ROUND(PriorityScore, 2) AS PriorityScore

FROM customer_churn_risk

WHERE ChurnRiskLevel IN ('At Risk', 'Critical')

ORDER BY PriorityScore DESC

LIMIT 20;


-- ============================================================
-- 12. CUSTOMER SEGMENT + CHURN RISK
-- ============================================================

SELECT
    CustomerSegment,

    ChurnRiskLevel,

    COUNT(*) AS Customers,

    ROUND(
        SUM(Monetary),
        2
    ) AS CustomerRevenue,

    ROUND(
        SUM(RevenueAtRisk),
        2
    ) AS RevenueAtRisk

FROM customer_churn_risk

GROUP BY
    CustomerSegment,
    ChurnRiskLevel

ORDER BY
    CustomerSegment,
    RevenueAtRisk DESC;


-- ============================================================
-- 13. TERRITORY + CHURN RISK
-- ============================================================

SELECT
    t.Region,

    r.ChurnRiskLevel,

    COUNT(DISTINCT r.CustomerKey) AS Customers,

    ROUND(
        SUM(r.Monetary),
        2
    ) AS CustomerRevenue,

    ROUND(
        SUM(r.RevenueAtRisk),
        2
    ) AS RevenueAtRisk

FROM customer_churn_risk r

JOIN fact_sales f
    ON r.CustomerKey = f.CustomerKey

JOIN dim_territory t
    ON f.TerritoryKey = t.TerritoryKey

GROUP BY
    t.Region,
    r.ChurnRiskLevel

ORDER BY
    t.Region,
    RevenueAtRisk DESC;


-- ============================================================
-- 14. CUSTOMERS WHO STOPPED PURCHASING
-- ============================================================

SELECT

    CustomerKey,

    CONCAT(
        FirstName,
        ' ',
        LastName
    ) AS CustomerName,

    Frequency,

    ROUND(Monetary, 2) AS LifetimeRevenue,

    RecentOrders,

    PreviousOrders,

    Recency,

    ChurnRiskLevel,

    ROUND(RevenueAtRisk, 2) AS RevenueAtRisk

FROM customer_churn_risk

WHERE
    RecentOrders = 0
    AND PreviousOrders > 0

ORDER BY RevenueAtRisk DESC

LIMIT 20;


-- ============================================================
-- 15. REVENUE DECLINE BY CUSTOMER SEGMENT
-- ============================================================

SELECT

    CustomerSegment,

    COUNT(*) AS Customers,

    ROUND(
        SUM(RevenueDeclineValue),
        2
    ) AS RevenueDecline,

    ROUND(
        SUM(RevenueAtRisk),
        2
    ) AS RevenueAtRisk

FROM customer_churn_risk

GROUP BY CustomerSegment

ORDER BY RevenueAtRisk DESC;


-- ============================================================
-- 16. HIGH-VALUE CUSTOMERS AT RISK
-- ============================================================

SELECT

    CustomerKey,

    CONCAT(
        FirstName,
        ' ',
        LastName
    ) AS CustomerName,

    CustomerSegment,

    ROUND(Monetary, 2) AS LifetimeRevenue,

    Recency,

    ChurnRiskScore,

    ChurnRiskLevel,

    ROUND(RevenueAtRisk, 2) AS RevenueAtRisk

FROM customer_churn_risk

WHERE
    HighValueRisk = 5
    AND ChurnRiskLevel IN ('At Risk', 'Critical')

ORDER BY RevenueAtRisk DESC;


-- ============================================================
-- 17. BASIC CUSTOMER RETENTION
-- ============================================================

SELECT

    COUNT(DISTINCT CustomerKey) AS TotalCustomers,

    COUNT(
        DISTINCT CASE
            WHEN RecentOrders > 0
            THEN CustomerKey
        END
    ) AS ActiveRecentCustomers,

    ROUND(
        COUNT(
            DISTINCT CASE
                WHEN RecentOrders > 0
                THEN CustomerKey
            END
        )
        /
        COUNT(DISTINCT CustomerKey)
        * 100,
        2
    ) AS RecentCustomerActivityPct

FROM customer_churn_risk;


-- ============================================================
-- 18. SALES BY PRODUCT CATEGORY AND YEAR
-- ============================================================

SELECT

    d.Year,

    p.ProductCategory,

    ROUND(
        SUM(f.Revenue),
        2
    ) AS Revenue,

    ROUND(
        SUM(f.Profit),
        2
    ) AS Profit

FROM fact_sales f

JOIN dim_date d
    ON f.DateKey = d.DateKey

JOIN dim_product p
    ON f.ProductKey = p.ProductKey

GROUP BY

    d.Year,
    p.ProductCategory

ORDER BY

    d.Year,
    Revenue DESC;