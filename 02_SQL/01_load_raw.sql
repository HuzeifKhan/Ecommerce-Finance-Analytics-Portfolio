-- 01_load_raw.sql
-- E-commerce Finance Analytics Portfolio
-- Author: Huzeif Khan
-- Description: Import raw data into MySQL and basic setup

CREATE DATABASE IF NOT EXISTS ecommerce_portfolio;
USE ecommerce_portfolio;

-- Start fresh
DROP TABLE IF EXISTS raw_transactions;

-- Table structure matching the CSV columns
CREATE TABLE raw_transactions (
    InvoiceNo       VARCHAR(10),
    StockCode       VARCHAR(20),
    Description     TEXT,
    Quantity        INT,
    InvoiceDate_str VARCHAR(25),
    UnitPrice       DECIMAL(10,2),
    CustomerID      VARCHAR(10),
    Country         VARCHAR(50)
);

-- Import from MySQL's secure folder (shown by SHOW VARIABLES LIKE 'secure_file_priv';)
-- If line ending error occurs, change LINES TERMINATED to '\n'
LOAD DATA INFILE 'C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/ecommerce_data.csv'
INTO TABLE raw_transactions
CHARACTER SET latin1
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\r\n'
IGNORE 1 ROWS
(InvoiceNo, StockCode, Description, Quantity, @InvoiceDate, UnitPrice, CustomerID, Country)
SET InvoiceDate_str = @InvoiceDate;

-- Quick verification
SELECT COUNT(*) AS total_rows FROM raw_transactions;
