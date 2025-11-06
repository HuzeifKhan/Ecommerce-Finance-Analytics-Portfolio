# -*- coding: utf-8 -*-
"""
Ecommerce & Finance – Insights Report (Cyan headings, dark-grey text, soft light-grey background)

Changes in this version:
- Removed Dashboard section from Page 1 (no preview image, no Tableau link)
- Page 2–3 charts now generated via Python from 01_Data/processed:
    * Monthly Revenue Trend  -> 03_Analysis/figures/monthly_revenue_py.png
    * Top 10 Products        -> 03_Analysis/figures/top_products_py.png
    * Customer Segmentation  -> 03_Analysis/figures/rfm_segments_py.png
- Excel notes no longer include "Dashboard Overview" row.

Pages
1) Title + KPIs (no dashboard)
2) Monthly Revenue + Top Products (PY charts)
3) Customer Segmentation (RFM) (PY chart)
4) Cohort Retention (cohort_retention.png)
5) Customer Lifetime Value (Top 20)
6) Customer Lifetime Value v1 – 12-Month Model
7) CLV by Customer Segment
8) RFM × CLV — Segment Insights (new)

Inputs (CSV/XLSX tolerant):
- 01_Data/processed/monthly_revenue.{csv|xlsx}
- 01_Data/processed/top_products.{csv|xlsx}
- 01_Data/processed/customer_rfm_segments.{csv|xlsx}
- (optional) 01_Data/processed/rfm_clv_summary.csv
- (optional) 01_Data/processed/rfm_clv_insights.csv

Images (auto-generated + existing):
- 03_Analysis/figures/monthly_revenue_py.png
- 03_Analysis/figures/top_products_py.png
- 03_Analysis/figures/rfm_segments_py.png
- 03_Analysis/figures/cohort_retention.png
- 03_Analysis/figures/clv_top20.png
- 03_Analysis/figures/clv_by_segment.png
- (optional) 03_Analysis/figures/rfm_clv_correlation.png
- (optional) 03_Analysis/figures/rfm_clv_scatter.png

Output:
- 06_Reports/Ecommerce_Finance_Insights_Report.pdf
- 04_Excel/KPI_Snapshot.xlsx
- 04_Excel/01_Data_Overview.xlsx
- 04_Excel/Dashboard_Notes.xlsx
"""

from pathlib import Path
from datetime import datetime, timezone
import pandas as pd
import numpy as np

# ReportLab
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

# Matplotlib (for Python charts)
import matplotlib
matplotlib.use("Agg")  # headless
import matplotlib.pyplot as plt

# -------------------------
# Paths
# -------------------------
BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "01_Data" / "processed"
REPORT_DIR = BASE_DIR / "06_Reports"
REPORT_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_PATH = REPORT_DIR / "Ecommerce_Finance_Insights_Report.pdf"

# (optional) RFM–CLV insights CSVs
CSV_RFM_CLV_SUMMARY  = DATA_DIR / "rfm_clv_summary.csv"
CSV_RFM_CLV_INSIGHTS = DATA_DIR / "rfm_clv_insights.csv"

# Analysis figures (existing optional)
FIG_DIR = BASE_DIR / "03_Analysis" / "figures"
FIG_DIR.mkdir(parents=True, exist_ok=True)

IMG_COHORT       = FIG_DIR / "cohort_retention.png"
IMG_CLV          = FIG_DIR / "clv_top20.png"
IMG_CLV_SEGMENT  = FIG_DIR / "clv_by_segment.png"
IMG_RFM_CLV_CORR = FIG_DIR / "rfm_clv_correlation.png"
IMG_RFM_CLV_SCAT = FIG_DIR / "rfm_clv_scatter.png"

# Python-generated chart targets (NEW)
IMG_REV_PY = FIG_DIR / "monthly_revenue_py.png"
IMG_TOP_PY = FIG_DIR / "top_products_py.png"
IMG_RFM_PY = FIG_DIR / "rfm_segments_py.png"

EXCEL_DIR = BASE_DIR / "04_Excel"
EXCEL_DIR.mkdir(parents=True, exist_ok=True)
KPI_XLSX      = EXCEL_DIR / "KPI_Snapshot.xlsx"
OVERVIEW_XLSX = EXCEL_DIR / "01_Data_Overview.xlsx"
NOTES_XLSX    = EXCEL_DIR / "Dashboard_Notes.xlsx"

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
# OPTIONAL: Load RFM–CLV CSV insights (for Page 8)
# -------------------------
rfm_clv_summary  = pd.read_csv(CSV_RFM_CLV_SUMMARY)  if CSV_RFM_CLV_SUMMARY.exists()  else pd.DataFrame()
rfm_clv_insights = pd.read_csv(CSV_RFM_CLV_INSIGHTS) if CSV_RFM_CLV_INSIGHTS.exists() else pd.DataFrame()

def bullets_from_insights(df: pd.DataFrame, max_rows: int = 4):
    out = []
    if df.empty:
        return out
    for _, r in df.head(max_rows).iterrows():
        metric  = str(r.get("Metric", "")).strip()
        insight = str(r.get("Insight", "")).strip()
        if insight:
            out.append(f"• {strong_cyan(metric)} — {insight}" if metric else f"• {insight}")
    return out

def bullets_from_summary(df: pd.DataFrame, max_rows: int = 4):
    out = []
    if df.empty:
        return out
    for _, r in df.head(max_rows).iterrows():
        seg   = str(r.get("Segment","")).strip()
        meanv = r.get("mean", None)
        cnt   = r.get("count", None)
        if seg and meanv is not None:
            out.append(f"• {strong_cyan(seg)} — avg CLV €{float(meanv):,.0f} (n={int(cnt) if pd.notna(cnt) else '—'})")
    return out

# -------------------------
# PY CHARTS — Generate from processed data
# -------------------------
def _ensure_numeric(series):
    return pd.to_numeric(series, errors="coerce")

def make_monthly_revenue_chart(df: pd.DataFrame, out_path: Path):
    if df.empty:
        return
    # Flexible column names
    df = df.copy()
    # expected: YearMonth + LineAmount (from your pipeline)
    ym_col = None
    for cand in ["YearMonth", "Year_Month", "Month", "yearmonth", "year_month"]:
        if cand in df.columns:
            ym_col = cand
            break
    amt_col = None
    for cand in ["LineAmount", "Line Amount", "Revenue", "Amount", "Line_Amount", "lineamount"]:
        if cand in df.columns:
            amt_col = cand
            break
    if ym_col is None or amt_col is None:
        return

    # Parse YearMonth
    # Accept formats like "2024-01", "Jan-2024", full dates, etc.
    try:
        ym = pd.to_datetime(df[ym_col], errors="coerce")
        # If it looks like end-of-month dates, normalize to Month Start for sorting
        ym = ym.dt.to_period("M").dt.to_timestamp()
    except Exception:
        # Fallback: leave as-is
        ym = df[ym_col]

    amt = _ensure_numeric(df[amt_col])
    tmp = pd.DataFrame({"YearMonth": ym, "Revenue": amt}).dropna().groupby("YearMonth", as_index=False)["Revenue"].sum()
    tmp = tmp.sort_values("YearMonth")

    plt.figure(figsize=(9, 4.5), dpi=200)
    plt.plot(tmp["YearMonth"], tmp["Revenue"], linewidth=2)
    plt.title("Monthly Revenue Trend")
    plt.xlabel("Month")
    plt.ylabel("Revenue")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(out_path)
    plt.close()

def make_top_products_chart(df: pd.DataFrame, out_path: Path):
    if df.empty:
        return
    df = df.copy()
    # expected: Product + LineAmount (or pre-aggregated)
    prod_col = None
    for cand in ["Product", "ProductName", "Item", "SKU", "product", "Product Name"]:
        if cand in df.columns:
            prod_col = cand
            break
    amt_col = None
    for cand in ["LineAmount", "TotalRevenue", "Revenue", "Line Amount", "Amount", "lineamount"]:
        if cand in df.columns:
            amt_col = cand
            break

    if prod_col is None:
        # maybe already in columns: 'Product' derived name like 'Description'
        for cand in ["Description", "Name", "Title"]:
            if cand in df.columns:
                prod_col = cand
                break
    if prod_col is None or amt_col is None:
        return

    amt = _ensure_numeric(df[amt_col])
    tmp = (
        pd.DataFrame({prod_col: df[prod_col], "Revenue": amt})
        .dropna(subset=[prod_col])
        .groupby(prod_col, as_index=False)["Revenue"].sum()
        .sort_values("Revenue", ascending=False)
        .head(10)
    )

    plt.figure(figsize=(9, 5), dpi=200)
    plt.barh(tmp[prod_col][::-1], tmp["Revenue"][::-1])
    plt.title("Top 10 Products by Revenue")
    plt.xlabel("Revenue")
    plt.ylabel("Product")
    plt.tight_layout()
    plt.savefig(out_path)
    plt.close()

def make_rfm_chart(df: pd.DataFrame, out_path: Path):
    """
    Simple RFM Segments bar chart.
    Accepts columns like:
      - Segment OR RFM_Segment OR rfm_segment
      - Or builds segments if Recency, Frequency, Monetary present (quantile-based)
    """
    if df.empty:
        return
    df = df.copy()

    # Try to detect segment column
    seg_col = None
    for cand in ["Segment", "RFM_Segment", "rfm_segment", "segment", "RFMGroup", "rfmgroup"]:
        if cand in df.columns:
            seg_col = cand
            break

    if seg_col is None:
        # Attempt to build segments if R/F/M present
        r_col = next((c for c in ["Recency","recency","R"] if c in df.columns), None)
        f_col = next((c for c in ["Frequency","frequency","F"] if c in df.columns), None)
        m_col = next((c for c in ["Monetary","monetary","M","MonetaryValue","monetaryvalue"] if c in df.columns), None)

        if r_col and f_col and m_col:
            # Lower recency is better; higher freq & monetary are better
            df["_R_q"] = pd.qcut(df[r_col].rank(method="first", ascending=True), 5, labels=[5,4,3,2,1]) # 1 best (recent), 5 worst
            df["_F_q"] = pd.qcut(df[f_col].rank(method="first", ascending=False), 5, labels=[1,2,3,4,5])
            df["_M_q"] = pd.qcut(df[m_col].rank(method="first", ascending=False), 5, labels=[1,2,3,4,5])
            df["RFM_Score"] = df["_R_q"].astype(int) + df["_F_q"].astype(int) + df["_M_q"].astype(int)

            # Simple mapping
            def _seg(score):
                if score <= 5:   return "Champions"
                if score <= 7:   return "Loyal"
                if score <= 9:   return "Potential Loyalists"
                if score <= 11:  return "At Risk"
                return "Hibernating"
            df["Segment"] = df["RFM_Score"].apply(_seg)
            seg_col = "Segment"

    if seg_col is None:
        # Fall back to a placeholder count if no usable info
        tmp = pd.DataFrame({"Segment": ["No RFM Segments Found"], "Count": [len(df)]})
    else:
        tmp = df.groupby(seg_col).size().reset_index(name="Count").sort_values("Count", ascending=True)

    plt.figure(figsize=(9, 5), dpi=200)
    plt.barh(tmp[seg_col] if seg_col in tmp.columns else tmp["Segment"], tmp["Count"])
    plt.title("Customer Segmentation (RFM)")
    plt.xlabel("Customers")
    plt.ylabel("Segment")
    plt.tight_layout()
    plt.savefig(out_path)
    plt.close()

# Build charts
try:
    make_monthly_revenue_chart(monthly, IMG_REV_PY)
    make_top_products_chart(top, IMG_TOP_PY)
    make_rfm_chart(rfm, IMG_RFM_PY)
    print("✅ Python charts saved in 03_Analysis/figures/")
except Exception as e:
    print(f"⚠️ Chart generation skipped: {e}")

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
    # Removed "Dashboard Overview" row (since we removed dashboard from report)
    ws_dn.append(["Monthly Revenue (PY)",
                  "Revenue trend by month.",
                  "Look for seasonality, spikes, and sustained trends.",
                  "Month picker or date range (if available)."])
    ws_dn.append(["Top Products (PY)",
                  "Top 10 products by total revenue.",
                  "Compare bars by length; hover for totals.",
                  "Category / product filter."])
    ws_dn.append(["Customer Segments (RFM) (PY)",
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

    # Links (kept minimal; no dashboard link)
    if "Links" in nwb.sheetnames:
        ws_l = nwb["Links"]
        ws_l.delete_rows(1, ws_l.max_row)
    else:
        ws_l = nwb.create_sheet("Links")
    write_timestamp(ws_l, ts_utc)
    ws_l.append([])
    pdf_url = "06_Reports/Ecommerce_Finance_Insights_Report.pdf"
    ws_l.append(["Asset","URL"])
    ws_l.append(["Latest PDF Report (repo path)", pdf_url])
    ws_l.append(["Last Refreshed (UTC)", ts_utc])

    if "Sheet" in nwb.sheetnames and len(nwb.sheetnames) > 1:
        try:
            del nwb["Sheet"]
        except Exception:
            pass

    nwb.save(NOTES_XLSX)
    print(f"📝 Notes updated at {NOTES_XLSX}")
except Exception as e:
    print(f"⚠️ Notes update skipped: {e}")

# -------------------------
# Build PDF document
# -------------------------
doc = SimpleDocTemplate(
    str(OUTPUT_PATH),
    pagesize=A4,
    leftMargin=2*cm, rightMargin=2*cm, topMargin=1.8*cm, bottomMargin=1.6*cm,
)

Story = []

# === Page 1 === (NO Dashboard)
Story.append(Paragraph("E-Commerce & Finance Insights Report", styles["CyanTitle"]))
Story.append(Paragraph(
    "Generated via Python ReportLab • Author: Huzeif Khan",
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

Story.append(PageBreak())

# === Page 2 === (PY charts)
Story.append(Paragraph("Visual Summary", styles["Heading2Cyan"]))
Story.append(Spacer(1, 6))

if IMG_REV_PY.exists():
    Story.append(Paragraph("Monthly Revenue Trend", styles["Heading3Cyan"]))
    Story.append(fit_image_keep_ratio(IMG_REV_PY, max_w=16.5*cm, max_h=8.8*cm))
    Story.append(Spacer(1, 10))
else:
    Story.append(Paragraph("Monthly revenue chart not found (expected 03_Analysis/figures/monthly_revenue_py.png).", styles["SmallGrey"]))

if IMG_TOP_PY.exists():
    Story.append(Paragraph("Top 10 Products by Revenue", styles["Heading3Cyan"]))
    Story.append(fit_image_keep_ratio(IMG_TOP_PY, max_w=16.5*cm, max_h=8.8*cm))
    Story.append(Spacer(1, 6))
else:
    Story.append(Paragraph("Top products chart not found (expected 03_Analysis/figures/top_products_py.png).", styles["SmallGrey"]))

Story.append(PageBreak())

# === Page 3 === (PY RFM)
Story.append(Paragraph("Customer Segmentation (RFM Model)", styles["Heading2Cyan"]))
Story.append(Spacer(1, 6))
if IMG_RFM_PY.exists():
    Story.append(fit_image_keep_ratio(IMG_RFM_PY, max_w=16.5*cm, max_h=17*cm))
else:
    Story.append(Paragraph("RFM chart not found (expected 03_Analysis/figures/rfm_segments_py.png).", styles["SmallGrey"]))

# === Page 4 — Cohort Retention (existing) ===
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

# === Page 6 — CLV v1 (12-Month Model) ===
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

# === Page 7 — CLV by Segment ===
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

# === Page 8 — RFM × CLV Insights (NEW) ===
Story.append(PageBreak())
Story.append(Paragraph("RFM × CLV — Segment Insights", styles["Heading2Cyan"]))
Story.append(Spacer(1, 6))
intro = ("How lifetime value varies by customer segment, and how it correlates with Recency, "
         "Frequency and Monetary (RFM).")
Story.append(Paragraph(intro, styles["SmallGrey"]))
Story.append(Spacer(1, 8))

# Bullet points from optional CSVs
def _safe_list(x): return x if x is not None else []
ins_bullets = _safe_list(bullets_from_insights(rfm_clv_insights, max_rows=4))
sum_bullets = _safe_list(bullets_from_summary(rfm_clv_summary,  max_rows=4))
for bl in (ins_bullets + sum_bullets):
    Story.append(Paragraph(bl, styles["BodyGrey"]))
if not (ins_bullets or sum_bullets):
    Story.append(Paragraph("No RFM–CLV insights CSVs found yet.", styles["SmallGrey"]))
Story.append(Spacer(1, 10))

# Correlation heatmap
Story.append(Paragraph("RFM–CLV Correlation", styles["Heading3Cyan"]))
if IMG_RFM_CLV_CORR.exists():
    Story.append(fit_image_keep_ratio(IMG_RFM_CLV_CORR, max_w=16.5*cm, max_h=8.5*cm))
else:
    Story.append(Paragraph("Correlation heatmap not found (expected 03_Analysis/figures/rfm_clv_correlation.png).",
                           styles["SmallGrey"]))
Story.append(Spacer(1, 10))

# Scatter plot
Story.append(Paragraph("CLV vs RFM (example scatter)", styles["Heading3Cyan"]))
if IMG_RFM_CLV_SCAT.exists():
    Story.append(fit_image_keep_ratio(IMG_RFM_CLV_SCAT, max_w=16.5*cm, max_h=8.5*cm))
else:
    Story.append(Paragraph("Scatter not found (expected 03_Analysis/figures/rfm_clv_scatter.png).",
                           styles["SmallGrey"]))

# background + timestamp footer on every page
def _on_page(canvas, doc):
    paint_background(canvas, doc)
    draw_footer(canvas, f"Last refreshed: {ts_utc}")

doc.build(Story, onFirstPage=_on_page, onLaterPages=_on_page)

print(f"\n✅ Report saved to {OUTPUT_PATH}\n")
