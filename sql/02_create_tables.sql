-- ============================================================
-- ADVENTUREWORKS SALES & CUSTOMER CHURN PROJECT
-- STAR SCHEMA + ANALYTICAL TABLES
-- ============================================================

USE b2b_sales_churn;


-- ============================================================
-- DROP TABLES IF THEY ALREADY EXIST
-- Order matters because of foreign keys
-- ============================================================

DROP TABLE IF EXISTS customer_churn_risk;
DROP TABLE IF EXISTS customer_rfm;
DROP TABLE IF EXISTS fact_sales;
DROP TABLE IF EXISTS dim_territory;
DROP TABLE IF EXISTS dim_product;
DROP TABLE IF EXISTS dim_customer;
DROP TABLE IF EXISTS dim_date;


-- ============================================================
-- DIMENSION: DATE
-- CSV:
-- DateKey,Date,Year,Quarter,Month,MonthName,Day
-- ============================================================

CREATE TABLE dim_date (
    DateKey INT PRIMARY KEY,
    FullDate DATE NOT NULL,
    Year INT,
    Quarter VARCHAR(5),
    Month INT,
    MonthName VARCHAR(20),
    Day INT
);


-- ============================================================
-- DIMENSION: CUSTOMER
-- ============================================================

CREATE TABLE dim_customer (
    CustomerKey INT PRIMARY KEY,
    Prefix VARCHAR(20),
    FirstName VARCHAR(100),
    LastName VARCHAR(100),
    BirthDate DATE,
    MaritalStatus VARCHAR(10),
    Gender VARCHAR(10),
    EmailAddress VARCHAR(255),
    AnnualIncome DECIMAL(15,2),
    TotalChildren INT,
    EducationLevel VARCHAR(100),
    Occupation VARCHAR(100),
    HomeOwner VARCHAR(10)
);


-- ============================================================
-- DIMENSION: PRODUCT
-- Exact CSV structure
-- ============================================================

CREATE TABLE dim_product (
    ProductKey INT PRIMARY KEY,
    ProductSubcategoryKey INT,
    ProductSKU VARCHAR(100),
    ProductName VARCHAR(255),
    ModelName VARCHAR(255),
    ProductDescription TEXT,
    ProductColor VARCHAR(50),
    ProductSize VARCHAR(50),
    ProductStyle VARCHAR(50),
    ProductCost DECIMAL(15,4),
    ProductPrice DECIMAL(15,4),
    ProductSubcategory VARCHAR(150),
    ProductCategoryKey INT,
    ProductCategory VARCHAR(150)
);


-- ============================================================
-- DIMENSION: TERRITORY
-- ============================================================

CREATE TABLE dim_territory (
    TerritoryKey INT PRIMARY KEY,
    Region VARCHAR(100),
    Country VARCHAR(100),
    Continent VARCHAR(100)
);


-- ============================================================
-- FACT TABLE: SALES
-- ============================================================

CREATE TABLE fact_sales (
    OrderNumber VARCHAR(50),
    OrderLineItem INT,

    DateKey INT,
    OrderDate DATE,
    StockDate DATE,

    ProductKey INT,
    CustomerKey INT,
    TerritoryKey INT,

    OrderQuantity INT,

    ProductPrice DECIMAL(15,4),
    ProductCost DECIMAL(15,4),

    Revenue DECIMAL(15,4),
    TotalCost DECIMAL(15,4),
    Profit DECIMAL(15,4),

    PRIMARY KEY (OrderNumber, OrderLineItem),

    CONSTRAINT fk_sales_date
        FOREIGN KEY (DateKey)
        REFERENCES dim_date(DateKey),

    CONSTRAINT fk_sales_product
        FOREIGN KEY (ProductKey)
        REFERENCES dim_product(ProductKey),

    CONSTRAINT fk_sales_customer
        FOREIGN KEY (CustomerKey)
        REFERENCES dim_customer(CustomerKey),

    CONSTRAINT fk_sales_territory
        FOREIGN KEY (TerritoryKey)
        REFERENCES dim_territory(TerritoryKey)
);


-- ============================================================
-- CUSTOMER RFM
-- ============================================================

CREATE TABLE customer_rfm (
    CustomerKey INT PRIMARY KEY,
    LastPurchaseDate DATE,

    Recency INT,
    Frequency INT,
    Monetary DECIMAL(15,4),

    R_Score INT,
    F_Score INT,
    M_Score INT,

    RFM_Score VARCHAR(10),
    RFM_Total INT,

    CustomerSegment VARCHAR(100),

    FirstName VARCHAR(100),
    LastName VARCHAR(100),
    Gender VARCHAR(10),

    AnnualIncome DECIMAL(15,2),

    Occupation VARCHAR(100),

    CONSTRAINT fk_rfm_customer
        FOREIGN KEY (CustomerKey)
        REFERENCES dim_customer(CustomerKey)
);


-- ============================================================
-- CUSTOMER CHURN RISK
-- ============================================================

CREATE TABLE customer_churn_risk (
    CustomerKey INT PRIMARY KEY,

    LastPurchaseDate DATE,

    Recency INT,
    Frequency INT,
    Monetary DECIMAL(15,4),

    R_Score INT,
    F_Score INT,
    M_Score INT,

    RFM_Score VARCHAR(10),
    RFM_Total INT,

    CustomerSegment VARCHAR(100),

    FirstName VARCHAR(100),
    LastName VARCHAR(100),
    Gender VARCHAR(10),

    AnnualIncome DECIMAL(15,2),

    Occupation VARCHAR(100),

    RecentOrders INT,
    RecentRevenue DECIMAL(15,4),

    PreviousOrders INT,
    PreviousRevenue DECIMAL(15,4),

    OrderFrequencyChange DECIMAL(12,4),
    RevenueChange DECIMAL(12,4),

    RecencyRisk INT,
    FrequencyRisk INT,
    RevenueRisk INT,
    HighValueRisk INT,

    ChurnRiskScore INT,
    ChurnRiskLevel VARCHAR(30),

    RevenueDeclineValue DECIMAL(15,4),
    RevenueAtRisk DECIMAL(15,4),

    PriorityScore DECIMAL(20,4),

    CONSTRAINT fk_churn_customer
        FOREIGN KEY (CustomerKey)
        REFERENCES dim_customer(CustomerKey)
);