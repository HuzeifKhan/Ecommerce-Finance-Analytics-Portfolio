<p align="center">
  <img src="github_banner.png" alt="E-commerce & Finance Analytics Portfolio Banner" width="100%">
</p>

<h1 align="center">🧾 E-commerce & Finance Analytics Portfolio</h1>

<p align="center">
  <em>SQL-driven data cleaning and analysis uncovering revenue trends, product performance, and seasonal insights from 500K+ e-commerce transactions.</em>
</p>

---

# 🧾 Ecommerce & Finance Analytics Portfolio

> **End-to-end Data Analytics Project** — from raw retail data to actionable business intelligence using **SQL, Python, and Tableau**.
> Cleaned, analyzed, and visualized **500K+ transactions** to uncover key insights into revenue, products, and customer behavior.

---

<!-- Badges -->
[![Refresh PDF report](https://github.com/HuzeifKhan/Ecommerce-Finance-Analytics-Portfolio/actions/workflows/refresh-report.yml/badge.svg?branch=main)](https://github.com/HuzeifKhan/Ecommerce-Finance-Analytics-Portfolio/actions/workflows/refresh-report.yml)
![Last updated](https://img.shields.io/github/last-commit/HuzeifKhan/Ecommerce-Finance-Analytics-Portfolio?label=Last%20updated)
![Python](https://img.shields.io/badge/Python-3.13%20%7C%203.12-blue?logo=python)
![License](https://img.shields.io/github/license/HuzeifKhan/Ecommerce-Finance-Analytics-Portfolio)
![Repo size](https://img.shields.io/github/repo-size/HuzeifKhan/Ecommerce-Finance-Analytics-Portfolio)
![Open issues](https://img.shields.io/github/issues/HuzeifKhan/Ecommerce-Finance-Analytics-Portfolio)

---

## 📖 Project Overview

This project demonstrates a complete **data cleaning, analytics, and visualization workflow** using
**SQL (MySQL)**, **Python (Pandas, Matplotlib)**, and **Tableau** on a real-world **E-Commerce Finance dataset**.

It transforms raw transactional data into **interactive dashboards** and **automated PDF reports** revealing trends, customer segments, and business KPIs — designed with a clean cyberpunk aesthetic for visual impact.

---

## ⚙️ Tech Stack

* 🧮 **SQL (MySQL)** — Data cleaning, transformation, KPI computation
* 🐍 **Python (Pandas, ReportLab)** — Data analysis, RFM modeling, PDF report automation
* 📊 **Tableau Public** — Visual analytics dashboard and KPI storytelling
* 💾 **GitHub** — Version control, documentation, and portfolio publishing

---

## 🧹 Data Cleaning Workflow

**Source:** [Kaggle – E-Commerce Data (Carrie1)](https://www.kaggle.com/datasets/carrie1/ecommerce-data)

### Key Steps

1. **Imported raw data** (541,909 rows) via SQL `LOAD DATA INFILE`.
2. **Converted and cleaned timestamps** using `STR_TO_DATE`.
3. **Filtered anomalies** — removed zero-price and negative-price rows.
4. **Removed duplicates** using `ROW_NUMBER()` window functions.
5. **Added analytical fields:**

   * `LineAmount = Quantity × UnitPrice`
   * `IsReturn` flag for negative quantities
   * `InvoiceYear`, `InvoiceMonth`, `InvoiceHour`
6. **Indexed columns** for faster aggregation and joins.
7. **Final dataset:** 534,123 valid transactions ready for analytics.

---

## 💰 Key Insights

* **Total Revenue:** €10,641,558.95
* **Total Valid Transactions:** 534K
* **Peak Sales Month:** November 2011 (holiday season surge)
* **Top Products:** Gift & household decor — “DOTCOM POSTAGE”, “REGENCY CAKESTAND 3 TIER”
* **Customer Segmentation:** RFM model grouped users into 4 categories based on behavior

---

## 🎨 Visual Analytics (Tableau Dashboard)

### 🔗 **[→ Open Live Dashboard on Tableau Public](https://public.tableau.com/app/profile/huzeif.khan/viz/Book1_17618490659490/E-commerceFinanceAnalyticsDashboard)**

|                                                                                  **Full Dashboard**                                                                                 |                     **Monthly Revenue**                    |                  **Top 10 Products**                 |                 **Customer Segmentation**                 |
| :---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------: | :--------------------------------------------------------: | :--------------------------------------------------: | :-------------------------------------------------------: |
| [![Dashboard Overview](05_Tableau/exports/dashboard_overview.png)](https://public.tableau.com/app/profile/huzeif.khan/viz/Book1_17618490659490/E-commerceFinanceAnalyticsDashboard) | ![Monthly Revenue](05_Tableau/exports/monthly_revenue.png) | ![Top Products](05_Tableau/exports/top_products.png) | ![RFM Segments](05_Tableau/exports/customer_segments.png) |

> *Built with a cyberpunk-inspired dark theme — neon cyan highlights, clean typography, and dynamic interactivity.*

---

## 📦 Automated Report (Python)

A fully-automated, professional PDF report generated using **ReportLab**:

📄 `06_Reports/Ecommerce_Finance_Insights_Report.pdf`

**Features:**

* Page 1: Title + KPIs + Live Tableau Link
* Page 2: Monthly Revenue & Top Products
* Page 3: Customer Segmentation (RFM)

> Styled with cyan headings, dark text, and a subtle light-grey illuminated background for a premium look.

---

## 📁 Project Structure

```
Ecommerce-Finance-Analytics-Portfolio/
│
├── 01_Data/
│   ├── raw/              # Original CSV from Kaggle
│   └── processed/        # Cleaned + RFM datasets (.csv / .xlsx)
│
├── 02_SQL/
│   ├── 01_load_raw.sql   # Import and setup
│   └── 02_cleaning.sql   # Data cleaning & transformations
│
├── 03_Python/
│   ├── ecommerce_analysis.ipynb  # EDA + RFM + visual analysis
│   └── make_report.py            # Automated PDF generator
│
├── 05_Tableau/
│   ├── exports/          # Exported Tableau charts (.png)
│   └── 05_Tableau.twbx   # Interactive dashboard file
│
├── 06_Reports/           # Auto-generated PDF report
│   └── Ecommerce_Finance_Insights_Report.pdf
│
├── README.md             # Project documentation
└── .gitignore
```

---

## ✨ Highlights

✅ End-to-end pipeline (SQL → Python → Tableau → PDF)
✅ Cyberpunk-themed visuals for a modern portfolio look
✅ Automated PDF report generation
✅ Hosted interactive dashboard on Tableau Public
✅ Modular project structure ready for CI/CD or cloud automation

---

## 🚀 Next Steps

1. **Add GitHub Actions workflow** to auto-generate report weekly.
2. **Integrate CLV & Churn Prediction** models in Python.
3. **Embed dashboard preview GIF** for live visual transitions.
4. **Deploy Power BI version** for professional benchmarking.

---

## 👨‍💻 Author

**Huzeif Khan**
📍 Berlin, Germany | 💼 Data Analyst / BI Analyst
🔗 [LinkedIn](https://www.linkedin.com/in/huzeif-khan-651042274/) • [GitHub](https://github.com/HuzeifKhan)


