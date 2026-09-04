# B2B Sales & Customer Churn Intelligence Dashboard
An end-to-end business analytics project built using the AdventureWorks dataset to analyze sales performance, customer value, customer segmentation, churn-risk signals, product performance, and territory performance.

The project combines **Python, MySQL, SQL, and Power BI** into a complete analytics workflow.
---

## Project Overview

The objective of this project is to transform raw sales and customer data into actionable business intelligence.

The solution focuses on four key business questions:
1. How is the business performing overall?
2. Which customers are most valuable?
3. Which customers require retention attention?
4. Which territories, products, and categories are driving revenue and profit?

The final solution consists of:
- Python-based data cleaning and transformation
- Star schema data modeling
- RFM customer segmentation
- Customer churn-risk analysis
- MySQL data warehouse
- SQL business analysis
- Four-page Power BI dashboard
---

##  Tools & Technologies

| Technology | Purpose                                                          |
| Python     | Data cleaning, transformation, RFM analysis, churn-risk analysis |
| Pandas     | Data manipulation and analysis                                   |
| NumPy      | Numerical calculations                                           |
| MySQL      | Data storage and SQL analysis                                    |
| SQL        | Business analysis and KPI queries                                |
| Power BI   | Interactive dashboard and visualization                          |
| DAX        | Power BI measures and calculations                               |
| VS Code    | Development environment                                          |
---

##  Dataset

The project uses the **AdventureWorks** sample dataset.

The raw data includes:
- Calendar
- Customers
- Products
- Product Categories
- Product Subcategories
- Returns
- Sales
- Territories

The sales data covers the 2015–2017 period used in the analysis.
---

#  Project Workflow

```text
Raw AdventureWorks CSV Files
            │
            ▼
      Python Data Cleaning
            │
            ▼
       Star Schema Model
            │
      ┌─────┴─────┐
      ▼           ▼
 RFM Analysis   Churn Risk Analysis
      │           │
      └─────┬─────┘
            ▼
          MySQL
            │
            ▼
      SQL Business Analysis
            │
            ▼
         Power BI
            │
      ┌─────┼─────────────┐
      ▼     ▼             ▼
 Overview  Customer     Churn
           Segmentation  Risk
            │
            ▼
      Territory & Product
         Performance
