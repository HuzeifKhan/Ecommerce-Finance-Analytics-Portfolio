<p align="center">
  <img src="github_banner.png" alt="E-commerce & Finance Analytics Portfolio Banner" width="100%">
</p>

<h1 align="center">🧾 E-commerce & Finance Analytics Portfolio</h1>

<p align="center">
  <em>SQL-driven data cleaning and analysis uncovering revenue trends, product performance, and seasonal insights from 500K+ e-commerce transactions.</em>
</p>

---

# 🧾 Ecommerce & Finance Analytics Portfolio

> **End-to-end Data & BI Project** — transforming raw retail data into actionable business intelligence using **SQL, Python, and Tableau**.  
> Cleaned, analyzed, and visualized **500K+ transactions** to uncover revenue trends, top-performing products, and customer behavior patterns.

---

<!-- Badges (centered) -->
<p align="center">
  <!-- Nightly build status -->
  <a href="https://github.com/HuzeifKhan/Ecommerce-Finance-Analytics-Portfolio/actions/workflows/refresh-report.yml">
    <img src="https://img.shields.io/github/actions/workflow/status/HuzeifKhan/Ecommerce-Finance-Analytics-Portfolio/refresh-report.yml?branch=main&label=%F0%9F%95%90%20Nightly%20Build&cacheSeconds=300" alt="Nightly Build Status">
  </a>
  
  <!-- Refresh workflow badge (GitHub-hosted) -->
  <a href="https://github.com/HuzeifKhan/Ecommerce-Finance-Analytics-Portfolio/actions/workflows/refresh-report.yml">
    <img src="https://github.com/HuzeifKhan/Ecommerce-Finance-Analytics-Portfolio/actions/workflows/refresh-report.yml/badge.svg?branch=main" alt="Refresh PDF report">
  </a>
  
  <!-- PDF previews workflow badge -->
  <a href="https://github.com/HuzeifKhan/Ecommerce-Finance-Analytics-Portfolio/actions/workflows/build-report-previews.yml">
    <img src="https://github.com/HuzeifKhan/Ecommerce-Finance-Analytics-Portfolio/actions/workflows/build-report-previews.yml/badge.svg?branch=main" alt="PDF Previews workflow">
  </a>
  
  <!-- Meta badges -->
  <img src="https://img.shields.io/github/last-commit/HuzeifKhan/Ecommerce-Finance-Analytics-Portfolio?label=%F0%9F%97%93%EF%B8%8F%20Last%20updated&cacheSeconds=300" alt="Last Commit">
  <img src="https://img.shields.io/badge/Python-3.13%20%7C%203.11-3776AB?logo=python&logoColor=white&cacheSeconds=300" alt="Python Version">
  <img src="https://img.shields.io/github/repo-size/HuzeifKhan/Ecommerce-Finance-Analytics-Portfolio?label=%F0%9F%93%A6%20Repo%20Size&cacheSeconds=300" alt="Repo Size">
  
  <!-- Fixed License badge (Cyan theme, static, no API token) -->
  <a href="LICENSE">
    <img src="https://img.shields.io/badge/%F0%9F%94%92%20License-MIT-03C4A1.svg?style=flat&labelColor=1b1b1b" alt="License: MIT">
  </a>
</p>


---

<p align="center">
  <strong>📄 Live Report (HTML):</strong><br>
  <a href="https://huzeifkhan.github.io/Ecommerce-Finance-Analytics-Portfolio/">
    🌐 View Live Ecommerce & Finance Analytics Report
  </a>
</p>

<p align="center">
  <strong>📘 Downloadable Report (PDF v2):</strong><br>
  <a href="https://raw.githubusercontent.com/HuzeifKhan/Ecommerce-Finance-Analytics-Portfolio/main/docs/report/Ecommerce_Finance_Insights_Report.pdf">
    🟢 Download / View Updated PDF Report
  </a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Status-Live%20Report%20Updated-brightgreen?style=for-the-badge&logo=github" alt="Live Report Status"/>
  <img src="https://img.shields.io/badge/Version-v2.0-blue?style=for-the-badge"/>
  <img src="https://img.shields.io/badge/Last_Update-2025--11--11-cyan?style=for-the-badge"/>
</p>

---

<!-- RUN-SUMMARY:START -->
> ✅ Last successful refresh: **2025-11-17 04:13 CET**  
> ⏱️ Duration: **193 min 45 sec**  
> 🌍 UTC: **2025-11-17 03:13 UTC**
<!-- RUN-SUMMARY:END -->

---

**Last refreshed (UTC):** see the footer in the latest PDF and the “Last Updated (UTC)” column in  
📊 `04_Excel/KPI_Snapshot.xlsx` *(update to `docs/Excel/KPI_Snapshot.xlsx` if you relocate it for Pages)*

---

## 🚀 Project Overview

An end-to-end **E-Commerce Finance Analytics** pipeline converting raw transactional data into KPIs and visual insights.  
Built using **SQL + Python + Tableau**, automated via **PowerShell + GitHub Actions**, and updated **nightly** at 03:00 Berlin time.

**Business Impact:**  
- Identified **seasonal peaks (Q4 surge)** and **top-revenue SKUs**  
- Improved **customer segmentation (RFM)** for retention strategy  
- Delivered **automated reporting** for faster decision-making

---

## ⚙️ Tech Stack

| Layer | Tools | Purpose |
|:--|:--|:--|
| **Data Cleaning** | MySQL / SQL | Import, clean, aggregate, KPI computation |
| **Analytics** | Python (Pandas · Statsmodels · ReportLab) | RFM modeling, forecasting, PDF/Excel automation |
| **Visualization** | Tableau Public | Interactive KPI dashboard |
| **Automation** | PowerShell · Task Scheduler · GitHub Actions | Daily refresh, logging, CI/CD |
| **Hosting** | GitHub Pages | Live portfolio preview |

---

## 🎨 Visual Analytics (Tableau Dashboard)

🔗 **[→ Open Live Dashboard on Tableau Public](https://public.tableau.com/app/profile/huzeif.khan/viz/Book1_17618490659490/E-commerceFinanceAnalyticsDashboard)**

| Overview | Monthly Revenue | Top Products | Customer Segments |
|:--:|:--:|:--:|:--:|
| [![Dashboard](docs/assets/tableau/dashboard_overview.png)](https://public.tableau.com/app/profile/huzeif.khan/viz/Book1_17618490659490/E-commerceFinanceAnalyticsDashboard) | ![Revenue](docs/assets/tableau/monthly_revenue.png) | ![Top Products](docs/assets/tableau/top_products.png) | ![RFM](docs/assets/tableau/customer_segments.png) |

> *Neon-cyan cyberpunk theme with clean typography and modular layout.*

---

## 📦 Automated PDF + Excel Reports

Auto-generated daily using **ReportLab + PowerShell + GitHub Actions**

- 📄 `docs/report/Ecommerce_Finance_Insights_Report.pdf`  
- 📊 `04_Excel/KPI_Snapshot.xlsx` *(or `docs/Excel/KPI_Snapshot.xlsx` if you mirrored it under `docs/`)*

**Sections**
- Page 1 → Overview + KPIs + Dashboard link  
- Page 2 → Monthly Revenue & Top Products  
- Page 3 → RFM Segmentation  
- Page 4 → Cohort Retention & CLV analysis (in progress)

---

## ⚙️ Automation Workflow

### 🔁 Local Automation (PowerShell + Task Scheduler)
- Script `scripts/update_all.ps1` → builds PDF + Excel, commits & pushes  
- Wrapper `scripts/run_scheduled.ps1` → runs nightly, logs output → `/logs/run_*.log`  
- Task Scheduler → **EFA_Portfolio_Nightly_Refresh @ 03:00 Berlin**

### ☁️ Cloud Automation (GitHub Actions)
- Workflow → `.github/workflows/refresh-report.yml`  
- Runs nightly at **02:00 UTC** (≈ **03:00 CET** / **04:00 CEST**)  
- Installs dependencies, rebuilds PDF/Excel, and commits artifacts  
- Status badge above 👆 reflects last run status

---

## 📁 Project Structure

```
Ecommerce-Finance-Analytics-Portfolio/
│
├── docs/
│ ├── index.html # GitHub Pages site
│ ├── report/Ecommerce_Finance_Insights_Report.pdf
│ ├── assets/tableau/ # Static tableau PNGs used by site & README
│ │ ├── dashboard_overview.png
│ │ ├── monthly_revenue.png
│ │ ├── top_products.png
│ │ └── customer_segments.png
│ ├── previews/ # Optional: report_page-00.png, ...
│ └── assets/figures/ # Phase 8 figures (CLV, cohorts, forecast)
│
├── 04_Excel/KPI_Snapshot.xlsx
├── 05_Tableau/
│ ├── exports/ (legacy; now using docs/assets/tableau/)
│ └── EFA_Dashboard.twbx
├── 06_Reports/ (legacy; canonical PDF lives under docs/report/)
│
├── .github/workflows/refresh-report.yml
├── scripts/
│ ├── update_all.ps1
│ └── run_scheduled.ps1
└── README.md
```

---

## ✨ Highlights

✅ Full pipeline: SQL → Python → Tableau → PDF → CI/CD  
✅ Cyberpunk visuals + dark neon theme  
✅ **Daily refresh automation** (local + cloud)  
✅ Robust logging & binary-safe Git workflow  
✅ Clean, modular structure ready for enterprise pipelines

---

## 📈 Quick Links

- **Live Dashboard:**  
  [View on Tableau Public](https://public.tableau.com/app/profile/huzeif.khan/viz/Book1_17618490659490/E-commerceFinanceAnalyticsDashboard)  
- **Auto-generated PDF Report (Pages copy):**  
  [Open PDF](https://raw.githubusercontent.com/HuzeifKhan/Ecommerce-Finance-Analytics-Portfolio/main/docs/report/Ecommerce_Finance_Insights_Report.pdf)  
- **Portfolio Site (GitHub Pages):**  
  [Visit Site](https://huzeifkhan.github.io/Ecommerce-Finance-Analytics-Portfolio/)

---

## 🧩 Next Steps

- 📈 Add CLV & Churn prediction modules  
- 🧾 Integrate Power BI version for benchmarking  
- 🔁 Simulate dbt / Airflow pipelines for enterprise refresh

---

## 👨‍💻 Author

**Huzeif Khan**  
📍 Berlin, Germany  |  💼 Data Analyst / BI Analyst  
🔗 [LinkedIn](https://www.linkedin.com/in/huzeif-khan-651042274/) • [GitHub](https://github.com/HuzeifKhan)
