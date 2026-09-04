-- ============================================================
-- ADVENTUREWORKS
-- LOAD CSV DATA INTO MYSQL
-- ============================================================

USE b2b_sales_churn;


-- ============================================================
-- 1. DIM_DATE
-- ============================================================

LOAD DATA LOCAL INFILE
'C:/Users/HARSHITHA/b2b-sales-churn/data/model/dim_date.csv'

INTO TABLE dim_date

FIELDS TERMINATED BY ','
OPTIONALLY ENCLOSED BY '"'

LINES TERMINATED BY '\n'

IGNORE 1 ROWS

(
    DateKey,
    @FullDate,
    Year,
    Quarter,
    Month,
    MonthName,
    Day
)

SET FullDate = STR_TO_DATE(
    TRIM(@FullDate),
    '%Y-%m-%d'
);


-- ============================================================
-- 2. DIM_CUSTOMER
-- ============================================================

LOAD DATA LOCAL INFILE
'C:/Users/HARSHITHA/b2b-sales-churn/data/model/dim_customer.csv'

INTO TABLE dim_customer

FIELDS TERMINATED BY ','
OPTIONALLY ENCLOSED BY '"'

LINES TERMINATED BY '\n'

IGNORE 1 ROWS

(
    CustomerKey,
    Prefix,
    FirstName,
    LastName,
    @BirthDate,
    MaritalStatus,
    Gender,
    EmailAddress,
    @AnnualIncome,
    TotalChildren,
    EducationLevel,
    Occupation,
    HomeOwner
)

SET

BirthDate =
    STR_TO_DATE(
        TRIM(@BirthDate),
        '%m/%d/%Y'
    ),

AnnualIncome =
    CAST(
        REPLACE(
            REPLACE(
                REPLACE(
                    TRIM(@AnnualIncome),
                    '$',
                    ''
                ),
                ',',
                ''
            ),
            ' ',
            ''
        )
        AS DECIMAL(15,2)
    );


-- ============================================================
-- 3. DIM_PRODUCT
-- ============================================================

LOAD DATA LOCAL INFILE
'C:/Users/HARSHITHA/b2b-sales-churn/data/model/dim_product.csv'

INTO TABLE dim_product

FIELDS TERMINATED BY ','
OPTIONALLY ENCLOSED BY '"'

LINES TERMINATED BY '\n'

IGNORE 1 ROWS

(
    ProductKey,
    ProductSubcategoryKey,
    ProductSKU,
    ProductName,
    ModelName,
    ProductDescription,
    ProductColor,
    ProductSize,
    ProductStyle,
    ProductCost,
    ProductPrice,
    ProductSubcategory,
    ProductCategoryKey,
    ProductCategory
);


-- ============================================================
-- 4. DIM_TERRITORY
-- ============================================================

LOAD DATA LOCAL INFILE
'C:/Users/HARSHITHA/b2b-sales-churn/data/model/dim_territory.csv'

INTO TABLE dim_territory

FIELDS TERMINATED BY ','
OPTIONALLY ENCLOSED BY '"'

LINES TERMINATED BY '\n'

IGNORE 1 ROWS

(
    TerritoryKey,
    Region,
    Country,
    Continent
);


-- ============================================================
-- 5. FACT_SALES
-- ============================================================

LOAD DATA LOCAL INFILE
'C:/Users/HARSHITHA/b2b-sales-churn/data/model/fact_sales.csv'

INTO TABLE fact_sales

FIELDS TERMINATED BY ','
OPTIONALLY ENCLOSED BY '"'

LINES TERMINATED BY '\n'

IGNORE 1 ROWS

(
    OrderNumber,
    OrderLineItem,
    DateKey,
    @OrderDate,
    @StockDate,
    ProductKey,
    CustomerKey,
    TerritoryKey,
    OrderQuantity,
    ProductPrice,
    ProductCost,
    Revenue,
    TotalCost,
    Profit
)

SET

OrderDate =
    STR_TO_DATE(
        TRIM(@OrderDate),
        '%Y-%m-%d'
    ),

StockDate =
    STR_TO_DATE(
        TRIM(@StockDate),
        '%Y-%m-%d'
    );


-- ============================================================
-- 6. CUSTOMER_RFM
-- ============================================================

LOAD DATA LOCAL INFILE
'C:/Users/HARSHITHA/b2b-sales-churn/data/processed/customer_rfm.csv'

INTO TABLE customer_rfm

FIELDS TERMINATED BY ','
OPTIONALLY ENCLOSED BY '"'

LINES TERMINATED BY '\n'

IGNORE 1 ROWS

(
    CustomerKey,
    @LastPurchaseDate,
    Recency,
    Frequency,
    Monetary,

    R_Score,
    F_Score,
    M_Score,

    RFM_Score,
    RFM_Total,

    CustomerSegment,

    FirstName,
    LastName,
    Gender,

    @AnnualIncome,

    Occupation
)

SET

LastPurchaseDate =
    STR_TO_DATE(
        TRIM(@LastPurchaseDate),
        '%Y-%m-%d'
    ),

AnnualIncome =
    CAST(
        REPLACE(
            REPLACE(
                REPLACE(
                    TRIM(@AnnualIncome),
                    '$',
                    ''
                ),
                ',',
                ''
            ),
            ' ',
            ''
        )
        AS DECIMAL(15,2)
    );


-- ============================================================
-- 7. CUSTOMER_CHURN_RISK
-- ============================================================

LOAD DATA LOCAL INFILE
'C:/Users/HARSHITHA/b2b-sales-churn/data/processed/customer_churn_risk.csv'

INTO TABLE customer_churn_risk

FIELDS TERMINATED BY ','
OPTIONALLY ENCLOSED BY '"'

LINES TERMINATED BY '\n'

IGNORE 1 ROWS

(
    CustomerKey,
    @LastPurchaseDate,

    Recency,
    Frequency,
    Monetary,

    R_Score,
    F_Score,
    M_Score,

    RFM_Score,
    RFM_Total,

    CustomerSegment,

    FirstName,
    LastName,
    Gender,

    @AnnualIncome,

    Occupation,

    @RecentOrders,
    RecentRevenue,

    @PreviousOrders,
    PreviousRevenue,

    OrderFrequencyChange,
    RevenueChange,

    RecencyRisk,
    FrequencyRisk,
    RevenueRisk,
    HighValueRisk,

    ChurnRiskScore,
    ChurnRiskLevel,

    RevenueDeclineValue,
    RevenueAtRisk,
    PriorityScore
)

SET

LastPurchaseDate =
    STR_TO_DATE(
        TRIM(@LastPurchaseDate),
        '%Y-%m-%d'
    ),

AnnualIncome =
    CAST(
        REPLACE(
            REPLACE(
                REPLACE(
                    TRIM(@AnnualIncome),
                    '$',
                    ''
                ),
                ',',
                ''
            ),
            ' ',
            ''
        )
        AS DECIMAL(15,2)
    ),

RecentOrders =
    CAST(@RecentOrders AS UNSIGNED),

PreviousOrders =
    CAST(@PreviousOrders AS UNSIGNED);


-- ============================================================
-- LOAD COMPLETE
-- ============================================================

SELECT 'DATA LOAD COMPLETED' AS Status;