<p align="center">
  <img src="github_banner.png" alt="E-commerce & Finance Analytics Portfolio Banner" width="100%">
</p>

<h1 align="center">🧾 E-commerce & Finance Analytics Portfolio</h1>

<p align="center">
  <em>SQL-driven data cleaning and analysis uncovering revenue trends, product performance, and seasonal insights from 500K+ e-commerce transactions.</em>
</p>

---

# 🧾 Ecommerce & Finance Analytics Portfolio  

> **End-to-end Data Analytics Project** — transforming raw retail data into actionable business intelligence using **SQL, Python, and Tableau**.  
> Cleaned, analyzed, and visualized **500K+ transactions** to uncover revenue trends, top-performing products, and customer behavior patterns.

---

<!-- Badges -->
[![Refresh PDF report](https://github.com/HuzeifKhan/Ecommerce-Finance-Analytics-Portfolio/actions/workflows/refresh-report.yml/badge.svg?branch=main)](https://github.com/HuzeifKhan/Ecommerce-Finance-Analytics-Portfolio/actions/workflows/refresh-report.yml)
![Last updated](https://img.shields.io/github/last-commit/HuzeifKhan/Ecommerce-Finance-Analytics-Portfolio?label=Last%20updated)
![Python](https://img.shields.io/badge/Python-3.13%20%7C%203.12-blue?logo=python)
![License](https://img.shields.io/github/license/HuzeifKhan/Ecommerce-Finance-Analytics-Portfolio)
![Repo size](https://img.shields.io/github/repo-size/HuzeifKhan/Ecommerce-Finance-Analytics-Portfolio)
![Open issues](https://img.shields.io/github/issues/HuzeifKhan/Ecommerce-Finance-Analytics-Portfolio)

---

## 🚀 Project Overview  

I built an end-to-end BI workflow on a real **E-Commerce Finance dataset** (541K transactions → 534K valid) to deliver decision-ready insights.  
Data is cleaned in **SQL (MySQL)**, analyzed in **Python (Pandas, Matplotlib, ReportLab)**, visualized in **Tableau**, and published via **GitHub Pages**.  
A **GitHub Actions** workflow auto-generates the report and syncs dashboard images on a monthly schedule.

**Business Impact:**  
Clear visibility into **seasonal trends (Q4 surge)**, **top revenue drivers**, and **customer cohorts (RFM)** — helping improve promotions, assortment planning, and retention strategy.

---

## ⚙️ Tech Stack  

- 🧮 **SQL (MySQL)** — Data cleaning, transformation, KPI computation  
- 🐍 **Python (Pandas, ReportLab)** — Data analysis, RFM modeling, automated PDF report generation  
- 📊 **Tableau Public** — Interactive dashboard & KPI storytelling  
- ⚙️ **GitHub Actions** — Continuous integration and monthly automation  
- 💾 **GitHub Pages** — Portfolio hosting and live project preview  

---

## 🧹 Data Cleaning Workflow  

**Source:** [Kaggle – E-Commerce Data (Carrie1)](https://www.kaggle.com/datasets/carrie1/ecommerce-data)

### Key Steps  

1. Imported raw data (**541,909 rows**) using `LOAD DATA INFILE`  
2. Converted and standardized timestamps via `STR_TO_DATE`  
3. Removed invalid and duplicate transactions using `ROW_NUMBER()`  
4. Filtered anomalies (zero or negative pricing)  
5. Added new analytical fields:
   - `LineAmount = Quantity × UnitPrice`
   - `IsReturn` flag for returns
   - `InvoiceYear`, `InvoiceMonth`, `InvoiceHour`
6. Indexed key columns for faster aggregation  
7. Final dataset: **534,123 valid transactions**

---

## 💰 Key Insights  

| Metric | Insight |
|:--|:--|
| **Total Revenue** | €10,641,558.95 |
| **Valid Transactions** | 534K |
| **Peak Sales** | November 2011 (holiday season) |
| **Top Products** | Gift & décor items — “DOTCOM POSTAGE”, “REGENCY CAKESTAND 3 TIER” |
| **Customer Segments** | Derived via RFM (Recency, Frequency, Monetary) |

---

## 🎨 Visual Analytics (Tableau Dashboard)  

### 🔗 **[→ Open Live Dashboard on Tableau Public](https://public.tableau.com/app/profile/huzeif.khan/viz/Book1_17618490659490/E-commerceFinanceAnalyticsDashboard)**  

| **Full Dashboard** | **Monthly Revenue** | **Top 10 Products** | **Customer Segmentation** |
|:--:|:--:|:--:|:--:|
| [![Dashboard Overview](05_Tableau/exports/dashboard_overview.png)](https://public.tableau.com/app/profile/huzeif.khan/viz/Book1_17618490659490/E-commerceFinanceAnalyticsDashboard) | ![Monthly Revenue](05_Tableau/exports/monthly_revenue.png) | ![Top Products](05_Tableau/exports/top_products.png) | ![RFM Segments](05_Tableau/exports/customer_segments.png) |

> *Built with a cyberpunk-inspired dark theme — neon cyan highlights, clean typography, and modular interactivity.*

---

## 📦 Automated PDF Report  

A professional, auto-generated PDF created via **ReportLab**, combining text insights and Tableau exports:  
📄 `06_Reports/Ecommerce_Finance_Insights_Report.pdf`

**Sections:**  
- Page 1 → Overview + KPIs + Dashboard Link  
- Page 2 → Revenue Trend & Top Products  
- Page 3 → RFM Segmentation  

> Styled with **cyan headers**, dark grey text, and a **soft illuminated grey background** for a clean, futuristic aesthetic.  

---

## 📁 Project Structure  
```
Ecommerce-Finance-Analytics-Portfolio/
│
├── 01_Data/
│ ├── raw/ # Original CSV from Kaggle
│ └── processed/ # Cleaned + RFM datasets
│
├── 02_SQL/
│ ├── 01_load_raw.sql # Data import and setup
│ └── 02_cleaning.sql # Cleaning, transformation, indexing
│
├── 03_Python/
│ ├── ecommerce_analysis.ipynb # EDA, RFM, and analytics
│ └── make_report.py # Automated PDF generator
│
├── 05_Tableau/
│ ├── exports/ # Exported charts (.png)
│ └── 05_Tableau.twbx # Interactive dashboard
│
├── 06_Reports/ # Final PDF output
│ └── Ecommerce_Finance_Insights_Report.pdf
│
├── README.md
└── .github/workflows/refresh-report.yml
```
---

## ✨ Highlights  

✅ Full pipeline: SQL → Python → Tableau → PDF  
✅ Cyberpunk-themed visuals for a modern portfolio aesthetic  
✅ Automated monthly reporting workflow via GitHub Actions  
✅ Hosted live dashboard + PDF report via GitHub Pages  
✅ Clean modular structure, easy to extend for cloud / CI/CD  

---

## 📈 Quick Links  

- 🔗 **Tableau Dashboard:**  
  [View Live on Tableau Public](https://public.tableau.com/app/profile/huzeif.khan/viz/Book1_17618490659490/E-commerceFinanceAnalyticsDashboard)

- 📄 **Auto-generated PDF Report:**  
  [Download / View Report (GitHub)](https://github.com/HuzeifKhan/Ecommerce-Finance-Analytics-Portfolio/blob/main/06_Reports/Ecommerce_Finance_Insights_Report.pdf)

- 🌐 **Live Portfolio Website (GitHub Pages):**  
  [Visit Site](https://huzeifkhan.github.io/Ecommerce-Finance-Analytics-Portfolio/)

---

## 🧩 Next Steps  

- 🧠 Extend with CLV & Churn Prediction models (Python)  
- 🧾 Add Power BI version for professional benchmarking  
- 🔁 Optional dbt / Airflow simulation for enterprise refresh  

---

## 👨‍💻 Author  

**Huzeif Khan**  
📍 Berlin, Germany | 💼 Data Analyst / BI Analyst  
🔗 [LinkedIn](https://www.linkedin.com/in/huzeif-khan-651042274/) • [GitHub](https://github.com/HuzeifKhan)



