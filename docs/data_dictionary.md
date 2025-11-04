# Data Dictionary

Author: Huzeif Khan  
Last Updated (UTC): _update when you commit_

## Tables

### 1) monthly_revenue
| Column          | Type     | Description                                |
|-----------------|----------|--------------------------------------------|
| InvoiceYear     | int      | Year part of invoice timestamp             |
| InvoiceMonth    | int      | Month part of invoice timestamp (1–12)     |
| Line Amount     | float    | Quantity × UnitPrice (aggregated by month) |

### 2) top_products
| Column          | Type     | Description                                |
|-----------------|----------|--------------------------------------------|
| StockCode       | string   | Product identifier                         |
| Description     | string   | Product name/short description             |
| Line Amount     | float    | Total revenue for the product              |
| Rank            | int      | Rank by revenue (1 = highest)              |

### 3) customer_rfm_segments
| Column        | Type   | Description                                   |
|---------------|--------|-----------------------------------------------|
| Customer ID   | int    | Unique customer identifier                     |
| Recency       | int    | Days since last purchase                       |
| Frequency     | int    | Number of invoices                             |
| Monetary      | float  | Total customer revenue                         |
| Segment       | string | RFM label (e.g., Champions, Loyal, At Risk)    |

> **Note:** Column names may vary slightly if the upstream cleaning script normalizes headers (e.g., `LineAmount` vs `Line Amount`). The pipeline resolves both.
