# -*- coding: utf-8 -*-
"""
Ecommerce & Finance – Insights Report (Cyan headings, dark-grey text, soft light-grey background)

Adds:
- "Last Refreshed (UTC)" timestamp in A1 for all Excel outputs
- Same timestamp in the footer of every PDF page
- Removes duplicate/overlapping Excel blocks for a clean single source of truth
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
CYAN      = colors.HexColor("#00DDD8")  # headings
DARKGREY  = colors.HexColor("#333333")  # body text
LIGHT_BG  = colors.HexColor("#F4F6FA")  # page background

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
# Background + footer
# -------------------------
def paint_background(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(LIGHT_BG)
    w, h = A4
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

def norm_cols(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df
    df = df.copy()
    df.columns = [c.strip().replace(" ", "").lower() for c in df.columns]
    return df

# -------------------------
# Load data for KPIs
# -------------------------
monthly = load_table("monthly_revenue")
top     = load_table("top_products")
rfm     = load_table("customer_rfm_segments")

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

# single UTC stamp for Excel + PDF footer
ts_utc = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

# -------------------------
# Excel outputs (with A1 timestamp)
# -------------------------
from openpyxl import Workbook, load_workbook
from openpyxl.utils.dataframe import dataframe_to_rows

def write_timestamp(ws):
    ws["A1"] = f"Last Refreshed (UTC): {ts_utc}"
    # mild styling
    ws["A1"].font = ws["A1"].font.copy(bold=True)
    ws["A1"].alignment = ws["A1"].alignment.copy(wrap_text=True)

# --- KPI_Snapshot.xlsx ---
excel_dir = BASE_DIR / "04_Excel"
excel_dir.mkdir(parents=True, exist_ok=True)

kpi_path = excel_dir / "KPI_Snapshot.xlsx"
try:
    if kpi_path.exists():
        wb = load_workbook(kpi_path)
        ws = wb.active
        ws.delete_rows(1, ws.max_row)
    else:
        wb = Workbook()
        ws = wb.active

    write_timestamp(ws)
    ws.append(["Metric", "Value", "Last Updated (UTC)"])
    data = [
        ["Total Revenue", total_revenue, ts_utc],
        ["Total Customers", total_customers, ts_utc],
        ["Average Order Value", avg_order_value, ts_utc],
    ]
    for row in data:
        ws.append(row)

    wb.save(kpi_path)
    print(f"💾 Excel KPI snapshot updated at {kpi_path}")
except Exception as e:
    print(f"⚠️ Excel update skipped due to: {e}")

# --- 01_Data_Overview.xlsx ---
overview_path = excel_dir / "01_Data_Overview.xlsx"
try:
    if overview_path.exists():
        wb_over = load_workbook(overview_path)
        for s in list(wb_over.sheetnames):
            del wb_over[s]
    else:
        wb_over = Workbook()
        for s in wb_over.sheetnames:
            del wb_over[s]

    ws_sum = wb_over.create_sheet("Overview")
    ws_cols = wb_over.create_sheet("Columns")
    ws_dq   = wb_over.create_sheet("Data_Quality")
    ws_log  = wb_over.create_sheet("Refresh_Log")
    ws_mo   = wb_over.create_sheet("Monthly_Revenue")
    ws_top  = wb_over.create_sheet("Top_Products")

    # Overview
    write_timestamp(ws_sum)
    ws_sum.append(["Metric", "Value"])
    ws_sum.append(["Total Revenue", total_revenue])
    ws_sum.append(["Total Customers", total_customers])
    ws_sum.append(["Average Order Value", avg_order_value])

    # Columns
    ws_cols.append(["Table", "Column"])
    for name, df in [("monthly_revenue", monthly),
                     ("top_products", top),
                     ("customer_rfm_segments", rfm)]:
        if not df.empty:
            for c in df.columns:
                ws_cols.append([name, str(c)])
        else:
            ws_cols.append([name, "(no columns)"])

    # Data_Quality
    ws_dq.append(["Table", "Column", "Null_Count"])
    for name, df in [("monthly_revenue", monthly),
                     ("top_products", top),
                     ("customer_rfm_segments", rfm)]:
        if not df.empty:
            s = df.isna().sum()
            for col, nulls in s.items():
                ws_dq.append([name, str(col), int(nulls)])
        else:
            ws_dq.append([name, "(no columns)", 0])

    # Refresh_Log
    ws_log.append(["Refreshed_At_UTC"])
    ws_log.append([ts_utc])

    # Monthly_Revenue table
    if not monthly.empty:
        for r in dataframe_to_rows(monthly, index=False, header=True):
            ws_mo.append(r)
    else:
        ws_mo.append(["No monthly_revenue data found"])

    # Top_Products table
    if not top.empty:
        for r in dataframe_to_rows(top, index=False, header=True):
            ws_top.append(r)
    else:
        ws_top.append(["No top_products data found"])

    wb_over.save(overview_path)
    print(f"💾 Data Overview updated at {overview_path}")
except Exception as e:
    print(f"⚠️ Data Overview update skipped: {e}")

# --- Dashboard_Notes.xlsx ---
notes_path = excel_dir / "Dashboard_Notes.xlsx"
tableau_url = "https://public.tableau.com/app/profile/huzeif.khan/viz/Book1_17618490659490/E-commerceFinanceAnalyticsDashboard"
pdf_repo_path = "06_Reports/Ecommerce_Finance_Insights_Report.pdf"

try:
    if notes_path.exists():
        wb_notes = load_workbook(notes_path)
        for s in list(wb_notes.sheetnames):
            del wb_notes[s]
    else:
        wb_notes = Workbook()
        for s in wb_notes.sheetnames:
            del wb_notes[s]

    ws_notes = wb_notes.create_sheet("Dashboard_Notes")
    ws_defs  = wb_notes.create_sheet("KPI_Definitions")
    ws_links = wb_notes.create_sheet("Links")

    write_timestamp(ws_notes)
    ws_notes.append(["View","What it shows","How to read","Filters / Drilldowns"])
    ws_notes.append(["Dashboard Overview",
                     "Executive overview combining KPIs and key charts.",
                     "Scan KPIs (top) → trend (left) → product mix (right).",
                     "Date range, region (if available)."])
    ws_notes.append(["Monthly Revenue",
                     "Revenue trend by month.",
                     "Look for seasonality, spikes, and sustained trends.",
                     "Month picker or date range."])
    ws_notes.append(["Top Products",
                     "Top 10 products by total revenue.",
                     "Compare bars by length; hover for totals.",
                     "Category / product filter."])
    ws_notes.append(["Customer Segments (RFM)",
                     "Customers grouped by Recency, Frequency, Monetary.",
                     "Focus on ‘Champions’ and ‘Loyal’ for upsell.",
                     "RFM score sliders / segment filter."])

    ws_defs.append(["KPI","Definition","Current Value"])
    ws_defs.append(["Total Revenue","Σ(LineAmount) over period", f"{total_revenue:,.2f}"])
    ws_defs.append(["Total Customers","Distinct count of CustomerID", f"{total_customers:,}"])
    ws_defs.append(["Average Order Value","Revenue / Customers", f"{avg_order_value:,.2f}"])

    ws_links.append(["Asset","URL / Path"])
    ws_links.append(["Live Tableau Dashboard", tableau_url])
    ws_links.append(["Latest PDF Report (repo path)", pdf_repo_path])
    ws_links.append(["Last Refreshed (UTC)", ts_utc])

    wb_notes.save(notes_path)
    print(f"📝 Dashboard Notes updated at {notes_path}")
except Exception as e:
    print(f"⚠️ Dashboard Notes update skipped: {e}")

# -------------------------
# PDF document
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

Story.append(Paragraph(
    f'Live Dashboard: <a href="{tableau_url}" color="#00DDD8">{strong_cyan("Open in Tableau Public")}</a>',
    styles["BodyGrey"]
))
Story.append(Spacer(1, 14))

Story.append(Paragraph("Key Performance Indicators (KPIs)", styles["Heading2Cyan"]))
for line in [
    f'{strong_cyan("Total Revenue")}: {total_revenue:,.2f}',
    f'{strong_cyan("Total Customers")}: {total_customers:,}',
    f'{strong_cyan("Average Order Value")}: {avg_order_value:,.2f}',
]:
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

def _on_page(canvas, doc):
    paint_background(canvas, doc)
    draw_footer(canvas, f"Last refreshed: {ts_utc}")

doc.build(Story, onFirstPage=_on_page, onLaterPages=_on_page)

print(f"\n✅ Report saved to {OUTPUT_PATH}\n")
