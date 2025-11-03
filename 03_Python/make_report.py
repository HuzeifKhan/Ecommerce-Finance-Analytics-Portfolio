# -*- coding: utf-8 -*-
"""
Ecommerce & Finance – Insights Report (Cyberpunk theme)

Pages
1) Title + KPIs + Live Tableau link
2) Monthly Revenue + Top Products (Tableau exports)
3) Customer Segmentation (RFM) title + chart

Inputs:
- 01_Data/processed/monthly_revenue.xlsx
- 01_Data/processed/top_products.xlsx
- 01_Data/processed/customer_rfm_segments.xlsx
- 05_Tableau/exports/{dashboard_overview,monthly_revenue,top_products,customer_segments}.png

Output:
- 06_Reports/Ecommerce_Finance_Insights_Report.pdf
"""

import os
from pathlib import Path

import pandas as pd
from reportlab.lib.pagesizes import A4, landscape, portrait
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

# -------------------------
# Paths
# -------------------------
BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "01_Data" / "processed"
REPORT_DIR = BASE_DIR / "06_Reports"
REPORT_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_PATH = REPORT_DIR / "Ecommerce_Finance_Insights_Report.pdf"

IMG_DIR = BASE_DIR / "05_Tableau" / "exports"
IMG_DASH = IMG_DIR / "dashboard_overview.png"
IMG_REV = IMG_DIR / "monthly_revenue.png"
IMG_TOP = IMG_DIR / "top_products.png"
IMG_RFM = IMG_DIR / "customer_segments.png"

# -------------------------
# Theme (cyberpunk cyan)
# -------------------------
CYAN = colors.Color(0.0, 0.87, 0.85)   # bright cyan accent
INK  = colors.whitesmoke               # body on dark
DARK = colors.Color(0.08, 0.08, 0.10)  # near-black bg

styles = getSampleStyleSheet()
styles.add(ParagraphStyle(
    name="CyanTitle",
    parent=styles["Title"],
    textColor=CYAN,
    fontName="Helvetica-Bold",
    fontSize=28,
    leading=32,
    spaceAfter=12,
))
styles.add(ParagraphStyle(
    name="Heading2Cyan",
    parent=styles["Heading2"],
    textColor=CYAN,
    fontName="Helvetica-Bold",
    spaceBefore=6,
    spaceAfter=6,
))
styles.add(ParagraphStyle(
    name="Heading3Cyan",
    parent=styles["Heading3"],
    textColor=CYAN,
    fontName="Helvetica-Bold",
    spaceBefore=4,
    spaceAfter=4,
))
styles.add(ParagraphStyle(
    name="Body",
    parent=styles["BodyText"],
    fontName="Helvetica",
    fontSize=10.5,
    leading=14,
    textColor=INK,
))

# -------------------------
# Helpers
# -------------------------
def load_excel_or_zero(path: Path, sheet: str | int | None = None) -> pd.DataFrame:
    try:
        return pd.read_excel(path, sheet_name=sheet)
    except Exception:
        return pd.DataFrame()

def fit_image_keep_ratio(img_path: Path, max_w: float, max_h: float) -> Image:
    """Return a reportlab Image scaled to fit within max_w x max_h preserving aspect."""
    img = Image(str(img_path))
    # reportlab reads actual sizes after draw; we can pre-scale using PIL size if needed,
    # but Image() can determine on build; here we pass width/height bounding box:
    img._restrictSize(max_w, max_h)  # preserves aspect
    return img

def strong(txt: str) -> str:
    """Wrap a keyword in cyan for emphasis."""
    return f'<font color="#00ddd8"><b>{txt}</b></font>'

# -------------------------
# Load data (KPIs)
# -------------------------
monthly_df = load_excel_or_zero(DATA_DIR / "monthly_revenue.xlsx")
top_df     = load_excel_or_zero(DATA_DIR / "top_products.xlsx")
rfm_df     = load_excel_or_zero(DATA_DIR / "customer_rfm_segments.xlsx")

try:
    total_revenue = float(monthly_df["Line Amount"].sum())
except Exception:
    total_revenue = 0.0

try:
    # distinct customers from RFM or customer column if present
    if "Customer ID" in rfm_df.columns:
        total_customers = int(rfm_df["Customer ID"].nunique())
    elif "Customers" in rfm_df.columns:
        total_customers = int(rfm_df["Customers"].sum())
    else:
        total_customers = 0
except Exception:
    total_customers = 0

try:
    # crude AOV = sum(LineAmount)/unique customers
    uniq_cust = total_customers if total_customers else 1
    avg_order_value = total_revenue / uniq_cust
except Exception:
    avg_order_value = 0.0

# -------------------------
# Build document
# -------------------------
doc = SimpleDocTemplate(
    str(OUTPUT_PATH),
    pagesize=portrait(A4),
    leftMargin=2*cm, rightMargin=2*cm, topMargin=1.8*cm, bottomMargin=1.6*cm,
)

Story: list = []

# === Page 1: Title + KPIs + Live link ===
Story.append(Paragraph("E-Commerce & Finance Insights Report", styles["CyanTitle"]))
Story.append(Paragraph(
    f"Generated via {strong('Python ReportLab')} • Author: Huzeif Khan",
    styles["Body"])
)
Story.append(Spacer(1, 10))

# Live link to Tableau
tableau_url = "https://public.tableau.com/app/profile/huzeif.khan/viz/Book1_17618490659490/E-commerceFinanceAnalyticsDashboard"
Story.append(Paragraph(
    f'Live Dashboard: <a href="{tableau_url}" color="#00ddd8">{strong("Open in Tableau Public")}</a>',
    styles["Body"])
)
Story.append(Spacer(1, 16))

# KPI block with cyan highlighted labels
Story.append(Paragraph(strong("Key Performance Indicators (KPIs)"), styles["Heading2Cyan"]))
kpi_lines = [
    f"{strong('Total Revenue')}: {total_revenue:,.2f}",
    f"{strong('Total Customers')}: {total_customers:,}",
    f"{strong('Average Order Value')}: {avg_order_value:,.2f}",
]
for line in kpi_lines:
    Story.append(Paragraph("• " + line, styles["Body"]))
Story.append(Spacer(1, 12))

# Optional small dashboard thumbnail (comment out if not wanted on page 1)
if IMG_DASH.exists():
    Story.append(Paragraph(strong("Dashboard Preview"), styles["Heading3Cyan"]))
    Story.append(fit_image_keep_ratio(IMG_DASH, max_w=16.5*cm, max_h=8.5*cm))
    Story.append(Spacer(1, 6))

Story.append(PageBreak())

# === Page 2: Monthly Revenue + Top Products ===
Story.append(Paragraph(strong("Visual Summary (Tableau Exports)"), styles["Heading2Cyan"]))
Story.append(Spacer(1, 6))

if IMG_REV.exists():
    Story.append(Paragraph(strong("Monthly Revenue Trend"), styles["Heading3Cyan"]))
    Story.append(fit_image_keep_ratio(IMG_REV, max_w=16.5*cm, max_h=8.8*cm))
    Story.append(Spacer(1, 10))

if IMG_TOP.exists():
    Story.append(Paragraph(strong("Top 10 Products by Revenue"), styles["Heading3Cyan"]))
    Story.append(fit_image_keep_ratio(IMG_TOP, max_w=16.5*cm, max_h=8.8*cm))
    Story.append(Spacer(1, 6))

Story.append(PageBreak())

# === Page 3: RFM title + chart (together on the same page) ===
Story.append(Paragraph(strong("Customer Segmentation (RFM Model)"), styles["Heading2Cyan"]))
Story.append(Spacer(1, 6))

if IMG_RFM.exists():
    Story.append(fit_image_keep_ratio(IMG_RFM, max_w=16.5*cm, max_h=17*cm))
else:
    Story.append(Paragraph("RFM chart not found in 05_Tableau/exports/", styles["Body"]))

# -------------------------
# Build & Save
# -------------------------
doc.build(Story)
print(f"\n✅ Report saved to {OUTPUT_PATH}\n")




