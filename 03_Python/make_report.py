# -*- coding: utf-8 -*-
"""
Ecommerce & Finance – Insights Report (Cyan headings, dark-grey text, soft light-grey background)

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

from pathlib import Path
import os
import pandas as pd

from reportlab.lib.pagesizes import A4
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
DATA_DIR = Path(__file__).resolve().parents[1] / "01_Data" / "processed"
REPORT_DIR = BASE_DIR / "06_Reports"
REPORT_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_PATH = REPORT_DIR / "Ecommerce_Finance_Insights_Report.pdf"

IMG_DIR = BASE_DIR / "05_Tableau" / "exports"
IMG_DASH = IMG_DIR / "dashboard_overview.png"
IMG_REV  = IMG_DIR / "monthly_revenue.png"
IMG_TOP  = IMG_DIR / "top_products.png"
IMG_RFM  = IMG_DIR / "customer_segments.png"

# -------------------------
# Theme
# -------------------------
CYAN      = colors.HexColor("#00DDD8")  # headings only
DARKGREY  = colors.HexColor("#333333")  # body text
LIGHT_BG  = colors.HexColor("#F4F6FA")  # page background (soft light grey)

styles = getSampleStyleSheet()

# Cyan headings
styles.add(ParagraphStyle(
    name="CyanTitle",
    parent=styles["Title"],
    textColor=CYAN,
    fontName="Helvetica-Bold",
    fontSize=28,
    leading=32,
    spaceAfter=10,
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

# Dark grey body
styles.add(ParagraphStyle(
    name="BodyGrey",
    parent=styles["BodyText"],
    textColor=DARKGREY,
    fontName="Helvetica",
    fontSize=10.5,
    leading=14,
))
styles.add(ParagraphStyle(
    name="SmallGrey",
    parent=styles["BodyText"],
    textColor=DARKGREY,
    fontName="Helvetica",
    fontSize=9.5,
    leading=13,
))

def strong_cyan(txt: str) -> str:
    return f'<font color="#00DDD8"><b>{txt}</b></font>'

# -------------------------
# Background painter (soft light-grey)
# -------------------------
def paint_background(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(LIGHT_BG)
    w, h = A4  # portrait A4
    canvas.rect(0, 0, w, h, fill=1, stroke=0)
    canvas.restoreState()

# -------------------------
# Helpers
# -------------------------
def load_excel_or_zero(path: Path, sheet=None) -> pd.DataFrame:
    try:
        return pd.read_excel(path, sheet_name=sheet)
    except Exception:
        return pd.DataFrame()

def fit_image_keep_ratio(img_path: Path, max_w: float, max_h: float) -> Image:
    img = Image(str(img_path))
    # Let reportlab keep aspect while limiting box:
    img._restrictSize(max_w, max_h)
    return img

# -------------------------
# Load data for KPIs (CSV/XLSX tolerant)
# -------------------------
def load_table(name: str) -> pd.DataFrame:
    """
    Try CSV first, then XLSX, inside 01_Data/processed.
    """
    csv_path = DATA_DIR / f"{name}.csv"
    xlsx_path = DATA_DIR / f"{name}.xlsx"
    if csv_path.exists():
        return pd.read_csv(csv_path)
    if xlsx_path.exists():
        return pd.read_excel(xlsx_path)
    return pd.DataFrame()

monthly = load_table("monthly_revenue")
top     = load_table("top_products")
rfm     = load_table("customer_rfm_segments")

# Normalize column names to handle spacing/case differences
def norm_cols(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty: 
        return df
    df = df.copy()
    df.columns = [c.strip().replace(" ", "").lower() for c in df.columns]
    return df

monthly_n = norm_cols(monthly)
rfm_n     = norm_cols(rfm)

# KPI calculations with robust fallbacks
# total_revenue: prefer 'lineamount' then 'lineamount' with space removed, else 0
if not monthly_n.empty and "lineamount" in monthly_n.columns:
    total_revenue = float(monthly_n["lineamount"].sum())
else:
    # try original names if normalization failed
    if "LineAmount" in monthly.columns:
        total_revenue = float(monthly["LineAmount"].sum())
    elif "Line Amount" in monthly.columns:
        total_revenue = float(monthly["Line Amount"].sum())
    else:
        total_revenue = 0.0

# total_customers: from customer id distinct if present, else 'customers' aggregate
if not rfm_n.empty:
    if "customerid" in rfm_n.columns:
        total_customers = int(rfm_n["customerid"].nunique())
    elif "customers" in rfm_n.columns:
        total_customers = int(rfm_n["customers"].sum())
    else:
        total_customers = 0
else:
    # try original headers
    if "CustomerID" in rfm.columns:
        total_customers = int(rfm["CustomerID"].nunique())
    elif "Customer ID" in rfm.columns:
        total_customers = int(rfm["Customer ID"].nunique())
    elif "Customers" in rfm.columns:
        total_customers = int(rfm["Customers"].sum())
    else:
        total_customers = 0

avg_order_value = (total_revenue / total_customers) if total_customers else 0.0

# -------------------------
# Save KPIs to Excel
# -------------------------
from openpyxl import Workbook, load_workbook
from datetime import datetime

excel_path = BASE_DIR / "04_Excel" / "KPI_Snapshot.xlsx"

try:
    if excel_path.exists():
        wb = load_workbook(excel_path)
        ws = wb.active
    else:
        wb = Workbook()
        ws = wb.active
        ws.append(["Metric", "Value", "Last Updated"])

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    data = [
        ["Total Revenue", total_revenue, now],
        ["Total Customers", total_customers, now],
        ["Average Order Value", avg_order_value, now]
    ]

    for row in data:
        ws.append(row)

    wb.save(excel_path)
    print(f"💾 Excel KPI snapshot updated at {excel_path}")
except Exception as e:
    print(f"⚠️ Excel update skipped due to: {e}")

# -------------------------
# Build document
# -------------------------
doc = SimpleDocTemplate(
    str(OUTPUT_PATH),
    pagesize=A4,
    leftMargin=2*cm, rightMargin=2*cm, topMargin=1.8*cm, bottomMargin=1.6*cm,
)

Story = []

# === Page 1 ===
Story.append(Paragraph("E-Commerce & Finance Insights Report", styles["CyanTitle"]))
Story.append(Paragraph(
    "Generated via Python ReportLab • Author: Huzeif Khan",
    styles["BodyGrey"]
))
Story.append(Spacer(1, 8))

tableau_url = "https://public.tableau.com/app/profile/huzeif.khan/viz/Book1_17618490659490/E-commerceFinanceAnalyticsDashboard"
Story.append(Paragraph(
    f'Live Dashboard: <a href="{tableau_url}" color="#00DDD8">{strong_cyan("Open in Tableau Public")}</a>',
    styles["BodyGrey"]
))
Story.append(Spacer(1, 14))

Story.append(Paragraph("Key Performance Indicators (KPIs)", styles["Heading2Cyan"]))
kpi_lines = [
    f'{strong_cyan("Total Revenue")}: {total_revenue:,.2f}',
    f'{strong_cyan("Total Customers")}: {total_customers:,}',
    f'{strong_cyan("Average Order Value")}: {avg_order_value:,.2f}',
]
for line in kpi_lines:
    Story.append(Paragraph("• " + line, styles["BodyGrey"]))
Story.append(Spacer(1, 10))

if IMG_DASH.exists():
    Story.append(Paragraph("Dashboard Preview", styles["Heading3Cyan"]))
    Story.append(fit_image_keep_ratio(IMG_DASH, max_w=16.5*cm, max_h=8.5*cm))
    Story.append(Spacer(1, 8))

Story.append(PageBreak())

# === Page 2 ===
Story.append(Paragraph("Visual Summary (Tableau Exports)", styles["Heading2Cyan"]))
Story.append(Spacer(1, 6))

if IMG_REV.exists():
    Story.append(Paragraph("Monthly Revenue Trend", styles["Heading3Cyan"]))
    Story.append(fit_image_keep_ratio(IMG_REV, max_w=16.5*cm, max_h=8.8*cm))
    Story.append(Spacer(1, 10))

if IMG_TOP.exists():
    Story.append(Paragraph("Top 10 Products by Revenue", styles["Heading3Cyan"]))
    Story.append(fit_image_keep_ratio(IMG_TOP, max_w=16.5*cm, max_h=8.8*cm))
    Story.append(Spacer(1, 6))

Story.append(PageBreak())

# === Page 3 ===
Story.append(Paragraph("Customer Segmentation (RFM Model)", styles["Heading2Cyan"]))
Story.append(Spacer(1, 6))
if IMG_RFM.exists():
    Story.append(fit_image_keep_ratio(IMG_RFM, max_w=16.5*cm, max_h=17*cm))
else:
    Story.append(Paragraph("RFM chart not found in 05_Tableau/exports/", styles["SmallGrey"]))

# Build with soft background on every page
doc.build(Story, onFirstPage=paint_background, onLaterPages=paint_background)

print(f"\n✅ Report saved to {OUTPUT_PATH}\n")




