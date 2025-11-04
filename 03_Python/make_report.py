# -*- coding: utf-8 -*-
"""
Ecommerce & Finance – Insights Report (Cyan headings, dark-grey text, soft light-grey background)

Adds:
- "Last Updated (UTC)" timestamp in the Excel KPI snapshot
- Same timestamp rendered in the footer of every PDF page
"""

from pathlib import Path
from datetime import datetime, timezone
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
DATA_DIR = BASE_DIR / "01_Data" / "processed"
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
# Background + footer (soft light-grey + UTC timestamp)
# -------------------------
def paint_background(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(LIGHT_BG)
    w, h = A4  # portrait A4
    canvas.rect(0, 0, w, h, fill=1, stroke=0)
    canvas.restoreState()

def draw_footer(canvas, stamp_text: str):
    canvas.saveState()
    canvas.setFillColor(DARKGREY)
    canvas.setFont("Helvetica", 8)
    footer = f"{stamp_text}  •  Page {canvas.getPageNumber()}"
    canvas.drawRightString(A4[0] - 2*cm, 1.0*cm, footer)
    canvas.restoreState()

# -------------------------
# Helpers
# -------------------------
def load_table(name: str) -> pd.DataFrame:
    """Try CSV first, then XLSX, inside 01_Data/processed."""
    csv_path = DATA_DIR / f"{name}.csv"
    xlsx_path = DATA_DIR / f"{name}.xlsx"
    if csv_path.exists():
        return pd.read_csv(csv_path)
    if xlsx_path.exists():
        return pd.read_excel(xlsx_path)
    return pd.DataFrame()

def fit_image_keep_ratio(img_path: Path, max_w: float, max_h: float) -> Image:
    img = Image(str(img_path))
    img._restrictSize(max_w, max_h)  # keep aspect ratio within box
    return img

# -------------------------
# Load data for KPIs (CSV/XLSX tolerant)
# -------------------------
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
if not monthly_n.empty and "lineamount" in monthly_n.columns:
    total_revenue = float(monthly_n["lineamount"].sum())
else:
    if "LineAmount" in monthly.columns:
        total_revenue = float(monthly["LineAmount"].sum())
    elif "Line Amount" in monthly.columns:
        total_revenue = float(monthly["Line Amount"].sum())
    else:
        total_revenue = 0.0

if not rfm_n.empty:
    if "customerid" in rfm_n.columns:
        total_customers = int(rfm_n["customerid"].nunique())
    elif "customers" in rfm_n.columns:
        total_customers = int(rfm_n["customers"].sum())
    else:
        total_customers = 0
else:
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
# Save KPIs to Excel (UTC)
# -------------------------
from openpyxl import Workbook, load_workbook

excel_path = BASE_DIR / "04_Excel" / "KPI_Snapshot.xlsx"
ts_utc = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

try:
    if excel_path.exists():
        wb = load_workbook(excel_path)
        ws = wb.active
    else:
        wb = Workbook()
        ws = wb.active
        ws.append(["Metric", "Value", "Last Updated (UTC)"])

    data = [
        ["Total Revenue", total_revenue, ts_utc],
        ["Total Customers", total_customers, ts_utc],
        ["Average Order Value", avg_order_value, ts_utc],
    ]
    for row in data:
        ws.append(row)

    wb.save(excel_path)
    print(f"💾 Excel KPI snapshot updated at {excel_path}")
except Exception as e:
    print(f"⚠️ Excel update skipped due to: {e}")

    # -------------------------
# Excel: Data Overview + Dashboard Notes
# -------------------------
from openpyxl import Workbook, load_workbook
from datetime import datetime
import numpy as np

utc_now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

excel_dir = BASE_DIR / "04_Excel"
excel_dir.mkdir(parents=True, exist_ok=True)

# ---------- helpers ----------
def safe_cols(df):
    try:
        return [str(c) for c in df.columns]
    except Exception:
        return []

def null_summary(df, label):
    if df.empty:
        return [[label, "N/A", "N/A"]]
    s = df.isna().sum()
    rows = [[label, str(idx), int(val)] for idx, val in s.items()]
    return rows

def try_date_range(df):
    """Try to find a date-like column and return min/max as strings."""
    if df.empty:
        return "N/A", "N/A"
    for cand in ["InvoiceDate","Date","Month","OrderDate","Invoice_Timestamp"]:
        for col in df.columns:
            if cand.lower() == str(col).lower():
                series = pd.to_datetime(df[col], errors="coerce")
                if series.notna().any():
                    return (
                        str(series.min().date()),
                        str(series.max().date())
                    )
    # fallback for monthly table having month-period text
    for col in df.columns:
        if "month" in str(col).lower():
            vals = df[col].dropna().astype(str)
            if len(vals) > 0:
                return vals.min(), vals.max()
    return "N/A", "N/A"

# ======================================
# 01) 04_Excel/01_Data_Overview.xlsx
# ======================================
overview_path = excel_dir / "01_Data_Overview.xlsx"

# create or open
if overview_path.exists():
    wb = load_workbook(overview_path)
else:
    wb = Workbook()

# Summary
if "Summary" in wb.sheetnames:
    ws = wb["Summary"]
    ws.delete_rows(1, ws.max_rows)
else:
    ws = wb.create_sheet("Summary")

min_date, max_date = try_date_range(monthly)
rows = [
    ["Metric", "Value"],
    ["Total Revenue", f"{total_revenue:,.2f}"],
    ["Total Customers", f"{total_customers:,}"],
    ["Average Order Value", f"{avg_order_value:,.2f}"],
    ["Monthly Period (min)", min_date],
    ["Monthly Period (max)", max_date],
    ["Tables Present", ", ".join([n for n,df in [("monthly_revenue",monthly),
                                                 ("top_products",top),
                                                 ("customer_rfm_segments",rfm)] if not df.empty]) or "N/A"],
]
for r in rows: ws.append(r)

# Columns
if "Columns" in wb.sheetnames:
    ws_cols = wb["Columns"]
    ws_cols.delete_rows(1, ws_cols.max_rows)
else:
    ws_cols = wb.create_sheet("Columns")

ws_cols.append(["Table","Column"])
for name, df in [("monthly_revenue", monthly),
                 ("top_products", top),
                 ("customer_rfm_segments", rfm)]:
    cols = safe_cols(df)
    if cols:
        for c in cols:
            ws_cols.append([name, c])
    else:
        ws_cols.append([name, "(no columns)"])

# Data_Quality
if "Data_Quality" in wb.sheetnames:
    ws_dq = wb["Data_Quality"]
    ws_dq.delete_rows(1, ws_dq.max_rows)
else:
    ws_dq = wb.create_sheet("Data_Quality")

ws_dq.append(["Table","Column","Null_Count"])
for name, df in [("monthly_revenue", monthly),
                 ("top_products", top),
                 ("customer_rfm_segments", rfm)]:
    for row in null_summary(df, name):
        ws_dq.append(row)

# Refresh_Log
if "Refresh_Log" not in wb.sheetnames:
    wb.create_sheet("Refresh_Log")
ws_log = wb["Refresh_Log"]
if ws_log.max_row == 1 and ws_log.max_column == 1 and ws_log["A1"].value is None:
    ws_log.append(["Refreshed_At_UTC"])
ws_log.append([utc_now])

wb.save(overview_path)
print(f"💾 Data Overview updated at {overview_path}")

# ======================================
# 02) 04_Excel/Dashboard_Notes.xlsx
# ======================================
notes_path = excel_dir / "Dashboard_Notes.xlsx"

if notes_path.exists():
    nb = load_workbook(notes_path)
else:
    nb = Workbook()

# Dashboard_Notes
if "Dashboard_Notes" in nb.sheetnames:
    ws_dn = nb["Dashboard_Notes"]
    ws_dn.delete_rows(1, ws_dn.max_rows)
else:
    ws_dn = nb.create_sheet("Dashboard_Notes")

ws_dn.append(["View","What it shows","How to read","Filters / Drilldowns"])
ws_dn.append(["Dashboard Overview",
              "Executive overview combining KPIs and key charts.",
              "Scan KPIs (top) → trend (left) → product mix (right).",
              "Date range, country/region (if available)."])
ws_dn.append(["Monthly Revenue",
              "Revenue trend by month.",
              "Look for seasonality, spikes, and sustained trends.",
              "Month picker or date range."])
ws_dn.append(["Top Products",
              "Top 10 products by total revenue.",
              "Compare bars by length; hover for totals.",
              "Category / product filter."])
ws_dn.append(["Customer Segments (RFM)",
              "Customer clusters by Recency, Frequency, Monetary.",
              "Focus on ‘Champions’ and ‘Loyal’ groups for upsell.",
              "RFM score sliders / segment filter."])

# KPI_Definitions
if "KPI_Definitions" in nb.sheetnames:
    ws_kpi = nb["KPI_Definitions"]
    ws_kpi.delete_rows(1, ws_kpi.max_rows)
else:
    ws_kpi = nb.create_sheet("KPI_Definitions")

ws_kpi.append(["KPI","Definition","Current Value"])
ws_kpi.append(["Total Revenue","Σ(LineAmount) over selected period", f"{total_revenue:,.2f}"])
ws_kpi.append(["Total Customers","Distinct count of Customer ID", f"{total_customers:,}"])
ws_kpi.append(["Average Order Value","Revenue / Customers (or Orders where applicable)", f"{avg_order_value:,.2f}"])

# Links
if "Links" in nb.sheetnames:
    ws_l = nb["Links"]
    ws_l.delete_rows(1, ws_l.max_rows)
else:
    ws_l = nb.create_sheet("Links")

tableau_url = "https://public.tableau.com/app/profile/huzeif.khan/viz/Book1_17618490659490/E-commerceFinanceAnalyticsDashboard"
pdf_url = "06_Reports/Ecommerce_Finance_Insights_Report.pdf"
ws_l.append(["Asset","URL"])
ws_l.append(["Live Tableau Dashboard", tableau_url])
ws_l.append(["Latest PDF Report (repo path)", pdf_url])
ws_l.append(["Last Refreshed (UTC)", utc_now])

nb.save(notes_path)
print(f"📝 Dashboard Notes updated at {notes_path}")

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

# Build with soft background + timestamp footer on every page
def _on_page(canvas, doc):
    paint_background(canvas, doc)
    draw_footer(canvas, f"Last refreshed: {ts_utc}")

doc.build(Story, onFirstPage=_on_page, onLaterPages=_on_page)

print(f"\n✅ Report saved to {OUTPUT_PATH}\n")
