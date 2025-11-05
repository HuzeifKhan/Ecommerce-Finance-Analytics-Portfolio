# -*- coding: utf-8 -*-
"""
Ecommerce & Finance – Insights Report (Cyan headings, dark-grey text, soft light-grey background)

Pages
1) Title + KPIs + Live Tableau link
2) Monthly Revenue + Top Products (Tableau exports)
3) Customer Segmentation (RFM) title + chart
4) Cohort Retention (cohort_retention.png)

Inputs (CSV/XLSX tolerant):
- 01_Data/processed/monthly_revenue.{csv|xlsx}
- 01_Data/processed/top_products.{csv|xlsx}
- 01_Data/processed/customer_rfm_segments.{csv|xlsx}

Images:
- 05_Tableau/exports/{dashboard_overview,monthly_revenue,top_products,customer_segments}.png
- 03_Analysis/figures/cohort_retention.png

Output:
- 06_Reports/Ecommerce_Finance_Insights_Report.pdf
- 04_Excel/KPI_Snapshot.xlsx
- 04_Excel/01_Data_Overview.xlsx
- 04_Excel/Dashboard_Notes.xlsx
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

# Excel helpers
from openpyxl import Workbook, load_workbook
from openpyxl.utils.dataframe import dataframe_to_rows
from openpyxl.styles import Font, Alignment, PatternFill

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
IMG_COHORT = BASE_DIR / "03_Analysis" / "figures" / "cohort_retention.png"
IMG_CLV    = BASE_DIR / "03_Analysis" / "figures" / "clv_top20.png"
IMG_COHORT = BASE_DIR / "03_Analysis" / "figures" / "cohort_retention.png"
IMG_CLV    = BASE_DIR / "03_Analysis" / "figures" / "clv_top20.png"
IMG_CLV_SEGMENT = BASE_DIR / "03_Analysis" / "figures" / "clv_by_segment.png"

# NEW: cohort heatmap from analysis
IMG_COHORT = BASE_DIR / "03_Analysis" / "figures" / "cohort_retention.png"

EXCEL_DIR = BASE_DIR / "04_Excel"
EXCEL_DIR.mkdir(parents=True, exist_ok=True)
KPI_XLSX       = EXCEL_DIR / "KPI_Snapshot.xlsx"
OVERVIEW_XLSX  = EXCEL_DIR / "01_Data_Overview.xlsx"
NOTES_XLSX     = EXCEL_DIR / "Dashboard_Notes.xlsx"

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

def norm_cols(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df
    df = df.copy()
    df.columns = [c.strip().replace(" ", "").lower() for c in df.columns]
    return df

def write_timestamp(ws, ts_utc: str):
    """A1 cyan timestamp pill."""
    ws["A1"] = f"Last Refreshed (UTC): {ts_utc}"
    ws["A1"].font = Font(bold=True, color="00DDD8")  # cyan
    ws["A1"].alignment = Alignment(wrap_text=True, vertical="center")
    ws["A1"].fill = PatternFill("solid", fgColor="F4F6FA")  # light grey bg
    try:
        ws.column_dimensions["A"].width = 40
    except Exception:
        pass

# -------------------------
# Load data for KPIs (CSV/XLSX tolerant)
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

# UTC timestamp (for Excel & PDF footer)
ts_utc = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

# -------------------------
# Excel: KPI_Snapshot.xlsx
# -------------------------
try:
    if KPI_XLSX.exists():
        wb = load_workbook(KPI_XLSX)
        ws = wb.active
    else:
        wb = Workbook()
        ws = wb.active
        # A1 reserved for timestamp; header starts at row 3 for neatness
        ws.append([])  # row 1 (timestamp)
        ws.append([])  # row 2 spacer
        ws.append(["Metric", "Value", "Last Updated (UTC)"])

    write_timestamp(ws, ts_utc)

    data = [
        ["Total Revenue", total_revenue, ts_utc],
        ["Total Customers", total_customers, ts_utc],
        ["Average Order Value", avg_order_value, ts_utc],
    ]
    for row in data:
        ws.append(row)

    wb.save(KPI_XLSX)
    print(f"💾 Excel KPI snapshot updated at {KPI_XLSX}")
except Exception as e:
    print(f"⚠️ Excel KPI snapshot skipped: {e}")

# -------------------------
# Excel: 01_Data_Overview.xlsx
# -------------------------
try:
    if OVERVIEW_XLSX.exists():
        owb = load_workbook(OVERVIEW_XLSX)
    else:
        owb = Workbook()

    # Summary sheet
    if "Summary" in owb.sheetnames:
        ws_sum = owb["Summary"]
        ws_sum.delete_rows(1, ws_sum.max_row)
    else:
        ws_sum = owb.create_sheet("Summary")

    write_timestamp(ws_sum, ts_utc)
    ws_sum.append([])  # spacer
    ws_sum.append(["Metric", "Value"])
    ws_sum.append(["Total Revenue", f"{total_revenue:,.2f}"])
    ws_sum.append(["Total Customers", f"{total_customers:,}"])
    ws_sum.append(["Average Order Value", f"{avg_order_value:,.2f}"])

    # Columns sheet
    if "Columns" in owb.sheetnames:
        ws_cols = owb["Columns"]
        ws_cols.delete_rows(1, ws_cols.max_row)
    else:
        ws_cols = owb.create_sheet("Columns")
    write_timestamp(ws_cols, ts_utc)
    ws_cols.append([])
    ws_cols.append(["Table", "Column"])
    for name, df in [("monthly_revenue", monthly),
                     ("top_products", top),
                     ("customer_rfm_segments", rfm)]:
        cols = [str(c) for c in df.columns] if not df.empty else []
        if cols:
            for c in cols:
                ws_cols.append([name, c])
        else:
            ws_cols.append([name, "(no columns)"])

    # Data_Quality sheet
    if "Data_Quality" in owb.sheetnames:
        ws_dq = owb["Data_Quality"]
        ws_dq.delete_rows(1, ws_dq.max_row)
    else:
        ws_dq = owb.create_sheet("Data_Quality")
    write_timestamp(ws_dq, ts_utc)
    ws_dq.append([])
    ws_dq.append(["Table", "Column", "Null_Count"])
    for name, df in [("monthly_revenue", monthly),
                     ("top_products", top),
                     ("customer_rfm_segments", rfm)]:
        if df.empty:
            ws_dq.append([name, "(no data)", 0])
        else:
            nulls = df.isna().sum()
            for col, val in nulls.items():
                ws_dq.append([name, str(col), int(val)])

    # Refresh_Log sheet (append-only)
    if "Refresh_Log" not in owb.sheetnames:
        owb.create_sheet("Refresh_Log")
    ws_log = owb["Refresh_Log"]
    if ws_log.max_row == 1 and ws_log.max_column == 1 and ws_log["A1"].value is None:
        ws_log.append(["Refreshed_At_UTC"])
    ws_log.append([ts_utc])

    # Monthly_Revenue & Top_Products views (optional)
    if "Monthly_Revenue" in owb.sheetnames:
        ws_mo = owb["Monthly_Revenue"]
        ws_mo.delete_rows(1, ws_mo.max_row)
    else:
        ws_mo = owb.create_sheet("Monthly_Revenue")
    write_timestamp(ws_mo, ts_utc)
    ws_mo.append([])
    if not monthly.empty:
        for r in dataframe_to_rows(monthly, index=False, header=True):
            ws_mo.append(r)
    else:
        ws_mo.append(["Note", "No monthly_revenue data found in 01_Data/processed"])

    if "Top_Products" in owb.sheetnames:
        ws_tp = owb["Top_Products"]
        ws_tp.delete_rows(1, ws_tp.max_row)
    else:
        ws_tp = owb.create_sheet("Top_Products")
    write_timestamp(ws_tp, ts_utc)
    ws_tp.append([])
    if not top.empty:
        for r in dataframe_to_rows(top, index=False, header=True):
            ws_tp.append(r)
    else:
        ws_tp.append(["Note", "No top_products data found in 01_Data/processed"])

    # Save
    if "Sheet" in owb.sheetnames and len(owb.sheetnames) > 1:
        try:
            del owb["Sheet"]
        except Exception:
            pass

    owb.save(OVERVIEW_XLSX)
    print(f"💾 Data Overview updated at {OVERVIEW_XLSX}")
except Exception as e:
    print(f"⚠️ Data Overview update skipped: {e}")

# -------------------------
# Excel: Dashboard_Notes.xlsx
# -------------------------
try:
    if NOTES_XLSX.exists():
        nwb = load_workbook(NOTES_XLSX)
    else:
        nwb = Workbook()

    # Dashboard_Notes
    if "Dashboard_Notes" in nwb.sheetnames:
        ws_dn = nwb["Dashboard_Notes"]
        ws_dn.delete_rows(1, ws_dn.max_row)
    else:
        ws_dn = nwb.create_sheet("Dashboard_Notes")

    write_timestamp(ws_dn, ts_utc)
    ws_dn.append([])
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
    if "KPI_Definitions" in nwb.sheetnames:
        ws_kpi = nwb["KPI_Definitions"]
        ws_kpi.delete_rows(1, ws_kpi.max_row)
    else:
        ws_kpi = nwb.create_sheet("KPI_Definitions")
    write_timestamp(ws_kpi, ts_utc)
    ws_kpi.append([])
    ws_kpi.append(["KPI","Definition","Current Value"])
    ws_kpi.append(["Total Revenue","Σ(LineAmount) over selected period", f"{total_revenue:,.2f}"])
    ws_kpi.append(["Total Customers","Distinct count of Customer ID", f"{total_customers:,}"])
    ws_kpi.append(["Average Order Value","Revenue / Customers (or Orders where applicable)", f"{avg_order_value:,.2f}"])

    # Links
    if "Links" in nwb.sheetnames:
        ws_l = nwb["Links"]
        ws_l.delete_rows(1, ws_l.max_row)
    else:
        ws_l = nwb.create_sheet("Links")
    write_timestamp(ws_l, ts_utc)
    ws_l.append([])
    tableau_url = "https://public.tableau.com/app/profile/huzeif.khan/viz/Book1_17618490659490/E-commerceFinanceAnalyticsDashboard"
    pdf_url = "06_Reports/Ecommerce_Finance_Insights_Report.pdf"
    ws_l.append(["Asset","URL"])
    ws_l.append(["Live Tableau Dashboard", tableau_url])
    ws_l.append(["Latest PDF Report (repo path)", pdf_url])
    ws_l.append(["Last Refreshed (UTC)", ts_utc])

    if "Sheet" in nwb.sheetnames and len(nwb.sheetnames) > 1:
        try:
            del nwb["Sheet"]
        except Exception:
            pass

    nwb.save(NOTES_XLSX)
    print(f"📝 Dashboard Notes updated at {NOTES_XLSX}")
except Exception as e:
    print(f"⚠️ Dashboard Notes update skipped: {e}")

# -------------------------
# Build PDF document
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

# === Page 4 — Cohort Retention (NEW) ===
Story.append(PageBreak())
Story.append(Paragraph("Cohort Retention", styles["Heading2Cyan"]))
Story.append(Spacer(1, 6))
caption = ("Each cell shows the % of customers who returned after N months, "
           "grouped by their first purchase month (cohort).")
Story.append(Paragraph(caption, styles["SmallGrey"]))
Story.append(Spacer(1, 8))
if IMG_COHORT.exists():
    Story.append(fit_image_keep_ratio(IMG_COHORT, max_w=16.5*cm, max_h=17*cm))
else:
    Story.append(Paragraph(
        "Cohort heatmap not found (expected 03_Analysis/figures/cohort_retention.png).",
        styles["SmallGrey"]
    ))

# === Page 5 — Customer Lifetime Value (CLV) ===
Story.append(PageBreak())
Story.append(Paragraph("Customer Lifetime Value (CLV) – 6-Month Outlook", styles["Heading2Cyan"]))
Story.append(Spacer(1, 6))
Story.append(Paragraph(
    "We estimate a simple 6-month CLV as AOV × (avg monthly repeat probability) × 6, "
    "added to the historical revenue. Top 20 customers shown.",
    styles["SmallGrey"]
))
Story.append(Spacer(1, 8))
if IMG_CLV.exists():
    Story.append(fit_image_keep_ratio(IMG_CLV, max_w=16.5*cm, max_h=17*cm))
else:
    Story.append(Paragraph(
        "CLV figure not found (expected 03_Analysis/figures/clv_top20.png).",
        styles["SmallGrey"]
    ))

    # === Page 6 ===
Story.append(PageBreak())
Story.append(Paragraph("Customer Lifetime Value (CLV v1 – 12-Month Model)", styles["Heading2Cyan"]))
Story.append(Spacer(1, 6))

caption = ("Deterministic CLV v1: AOV × Purchase Frequency per Month × 12 Months. "
           "Shows your top-value customers based on average order value and repeat purchase rate.")
Story.append(Paragraph(caption, styles["SmallGrey"]))
Story.append(Spacer(1, 8))

if IMG_CLV.exists():
    Story.append(fit_image_keep_ratio(IMG_CLV, max_w=16.5*cm, max_h=17*cm))
    Story.append(Spacer(1, 6))
    Story.append(Paragraph(f"Last updated (UTC): {ts_utc}", styles['SmallGrey']))
else:
    Story.append(Paragraph(
        "CLV chart not found (expected 03_Analysis/figures/clv_top20.png).",
        styles["SmallGrey"]
    ))

    # === Page 7 ===
Story.append(PageBreak())
Story.append(Paragraph("CLV by Customer Segment", styles["Heading2Cyan"]))
Story.append(Spacer(1, 6))
caption = "Average predicted 12-month CLV for each RFM segment."
Story.append(Paragraph(caption, styles["SmallGrey"]))
Story.append(Spacer(1, 8))

if IMG_CLV_SEGMENT.exists():
    Story.append(fit_image_keep_ratio(IMG_CLV_SEGMENT, max_w=16.5*cm, max_h=17*cm))
else:
    Story.append(Paragraph("CLV segment chart not found (expected 03_Analysis/figures/clv_by_segment.png).", styles["SmallGrey"]))

# background + timestamp footer on every page
def _on_page(canvas, doc):
    paint_background(canvas, doc)
    draw_footer(canvas, f"Last refreshed: {ts_utc}")

doc.build(Story, onFirstPage=_on_page, onLaterPages=_on_page)

print(f"\n✅ Report saved to {OUTPUT_PATH}\n")
