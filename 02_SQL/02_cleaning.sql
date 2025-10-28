-- 02_cleaning.sql
-- E-commerce Finance Analytics Portfolio
-- Author: Huzeif Khan
-- Description: Cleaning and transformation queries

USE ecommerce_portfolio;

-- 1) Add proper DATETIME converted from the string
ALTER TABLE raw_transactions ADD COLUMN InvoiceDate DATETIME;

UPDATE raw_transactions
SET InvoiceDate = STR_TO_DATE(InvoiceDate_str, '%m/%d/%Y %H:%i');

-- Sanity check
SELECT COUNT(*) AS total_rows,
       SUM(InvoiceDate IS NULL) AS bad_dates
FROM raw_transactions;

-- 2) UnitPrice quality check (info only)
SELECT
  SUM(UnitPrice = 0)  AS zero_price,
  SUM(UnitPrice < 0)  AS negative_price
FROM raw_transactions;

-- 3) De-duplicate & filter into cleaned table
DROP TABLE IF EXISTS cleaned_transactions;

CREATE TABLE cleaned_transactions AS
WITH dedup AS (
  SELECT
    rt.*,
    ROW_NUMBER() OVER (
      PARTITION BY InvoiceNo, StockCode, CustomerID, UnitPrice, Quantity, InvoiceDate
      ORDER BY InvoiceNo
    ) AS rn
  FROM raw_transactions rt
)
SELECT
  InvoiceNo,
  StockCode,
  TRIM(Description) AS Description,
  Quantity,
  UnitPrice,
  CustomerID,
  Country,
  InvoiceDate,
  (Quantity * UnitPrice) AS LineAmount,
  CASE WHEN Quantity < 0 THEN 1 ELSE 0 END AS IsReturn
FROM dedup
WHERE rn = 1
  AND Quantity <> 0
  AND UnitPrice > 0;  -- drop zero/invalid prices

-- 4) Enrich with date parts
ALTER TABLE cleaned_transactions
  ADD COLUMN InvoiceDateDate DATE,
  ADD COLUMN InvoiceYear  INT,
  ADD COLUMN InvoiceMonth INT,
  ADD COLUMN InvoiceHour  INT;

UPDATE cleaned_transactions
SET
  InvoiceDateDate = DATE(InvoiceDate),
  InvoiceYear     = YEAR(InvoiceDate),
  InvoiceMonth    = MONTH(InvoiceDate),
  InvoiceHour     = HOUR(InvoiceDate);

-- 5) Indexes for performance
CREATE INDEX ix_cleaned_date     ON cleaned_transactions (InvoiceDate);
CREATE INDEX ix_cleaned_customer ON cleaned_transactions (CustomerID);
CREATE INDEX ix_cleaned_stock    ON cleaned_transactions (StockCode);

-- 6) Smoke tests (optional)
SELECT ROUND(SUM(CASE WHEN IsReturn=0 THEN LineAmount ELSE 0 END),2) AS GrossRevenue
FROM cleaned_transactions;

SELECT CONCAT(InvoiceYear, '-', LPAD(InvoiceMonth,2,'0')) AS YearMonth,
       ROUND(SUM(CASE WHEN IsReturn=0 THEN LineAmount ELSE 0 END),2) AS Revenue
FROM cleaned_transactions
GROUP BY YearMonth
ORDER BY YearMonth;
