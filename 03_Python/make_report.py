# -*- coding: utf-8 -*-
"""
Ecommerce & Finance – Insights Report (Cyan headings, dark-grey text, soft light-grey background)

Changes in this version:
- Replaced Page 2–3 charts with the same logic/visuals used in ecommerce_analysis.ipynb:
    * Monthly Revenue Trend  (returns excluded, same YearMonth build, neon style)
    * Top 10 Products        (returns excluded, Description-based, neon style)
    * Customer Segmentation  (RFM rebuilt from raw if needed, same emoji segments, NEON STYLE)
- RFM chart is now a **pie chart** (to match ecommerce_analysis.ipynb).
- No other sections changed.

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

# Python-generated chart targets
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
# PY CHARTS — Generate from processed data (MATCHING NOTEBOOK)
# -------------------------
def _ensure_numeric(series):
    return pd.to_numeric(series, errors="coerce")

# — Neon style (as used in the notebook) —
_BG      = "#E8E8E8"
_GRID    = "#494949"
_AX      = "#383B3E"
_TITLE   = "#1B1B1B"
_CYAN    = "#10DCC4"
_PINK    = "#0087A2"
_ORANGE  = "#FF7F0E"
_PURPLE  = "#5302A9"
_NEON_PALETTE = [_PURPLE, _PINK, _ORANGE, _CYAN]

def _style_axes(ax):
    ax.set_facecolor(_BG)
    for spine in ax.spines.values():
        spine.set_color(_GRID)
        spine.set_linewidth(1.2)
    ax.tick_params(colors=_AX, labelsize=10)
    ax.grid(True, color=_GRID, linewidth=0.8, alpha=0.6)

def _maybe_parse_dates(s):
    try:
        return pd.to_datetime(s, errors="coerce")
    except Exception:
        return s

def make_monthly_revenue_chart(df: pd.DataFrame, out_path: Path):
    """
    Match ecommerce_analysis.ipynb:
    - If raw columns exist: exclude returns (IsReturn==0), group by InvoiceYear/InvoiceMonth -> YearMonth.
    - Otherwise, honor pre-aggregated monthly_revenue file (YearMonth + LineAmount).
    - Neon styling + emoji title.
    """
    if df.empty:
        return

    work = df.copy()

    # Prefer raw → rebuild like in notebook
    raw_cols = set(work.columns)
    has_raw = {"InvoiceYear", "InvoiceMonth", "LineAmount"}.issubset(raw_cols)
    if has_raw:
        # Exclude returns if present
        if "IsReturn" in raw_cols:
            work = work[work["IsReturn"] == 0].copy()
        grouped = (
            work.groupby(["InvoiceYear", "InvoiceMonth"], as_index=False)["LineAmount"]
                .sum()
        )
        grouped["YearMonth"] = (
            grouped["InvoiceYear"].astype(str) + "-" + grouped["InvoiceMonth"].astype(str).str.zfill(2)
        )
        x = pd.to_datetime(grouped["YearMonth"], errors="coerce").dt.to_period("M").dt.to_timestamp()
        y = _ensure_numeric(grouped["LineAmount"])
    else:
        # Use provided processed table
        ym_col = next((c for c in ["YearMonth", "Year_Month", "Month", "yearmonth", "year_month"] if c in work.columns), None)
        amt_col = next((c for c in ["LineAmount", "Line Amount", "Revenue", "Amount", "lineamount"] if c in work.columns), None)
        if ym_col is None or amt_col is None:
            return
        x = pd.to_datetime(work[ym_col], errors="coerce").dt.to_period("M").dt.to_timestamp()
        y = _ensure_numeric(work[amt_col])

        # If the processed file still has raw row-level data, aggregate
        tmp = pd.DataFrame({"YearMonth": x, "Revenue": y}).dropna().groupby("YearMonth", as_index=False)["Revenue"].sum()
        x, y = tmp["YearMonth"], tmp["Revenue"]

    order = np.argsort(pd.to_datetime(x))
    x, y = x.iloc[order], y.iloc[order]

    fig, ax = plt.subplots(figsize=(10, 5), facecolor=_BG)
    _style_axes(ax)

    ax.plot(x, y,
            linewidth=2.4,
            color=_PINK,
            marker="o",
            markersize=5,
            markerfacecolor=_PINK,
            markeredgecolor=_BG)

    ax.set_title("📈 Monthly Revenue Trend", color=_TITLE, fontsize=14, fontweight="bold", pad=14)
    ax.set_xlabel("Month",  color=_AX, fontsize=11)
    ax.set_ylabel("Revenue (€)", color=_AX, fontsize=11)
    plt.xticks(rotation=45, ha="right")

    plt.tight_layout()
    plt.savefig(out_path, dpi=200, bbox_inches="tight")
    plt.close()

def make_top_products_chart(df: pd.DataFrame, out_path: Path):
    """
    Match ecommerce_analysis.ipynb:
    - Exclude returns (IsReturn==0) when raw columns present
    - Group by Description (fallbacks to other name fields)
    - Top 10 by LineAmount
    - Neon styling + emoji title
    """
    if df.empty:
        return

    work = df.copy()
    raw_cols = set(work.columns)
    amt_col = next((c for c in ["LineAmount", "TotalRevenue", "Revenue", "Line Amount", "Amount", "lineamount"] if c in raw_cols), None)

    # Try notebook's 'Description' first
    prod_col = next((c for c in ["Description", "Product", "ProductName", "Item", "SKU", "Product Name", "Name", "Title", "product"] if c in raw_cols), None)
    if prod_col is None or amt_col is None:
        return

    # Exclude returns if present (notebook behavior)
    if "IsReturn" in raw_cols:
        work = work[work["IsReturn"] == 0].copy()

    tmp = (
        work.groupby(prod_col, as_index=False)[amt_col]
            .sum()
            .rename(columns={amt_col: "Revenue"})
            .sort_values("Revenue", ascending=False)
            .head(10)
    )

    fig, ax = plt.subplots(figsize=(10, 5.2), facecolor=_BG)
    _style_axes(ax)

    y_labels = tmp[prod_col][::-1]
    vals     = tmp["Revenue"][::-1]
    bars = ax.barh(y_labels, vals, height=0.7, color=_CYAN)

    # Optional value labels at bar ends
    for b in bars:
        ax.text(b.get_width(), b.get_y() + b.get_height()/2,
                f" {b.get_width():,.0f}", va="center", ha="left", color=_AX, fontsize=9)

    ax.set_title("🏆 Top 10 Products by Revenue", color=_TITLE, fontsize=14, fontweight="bold", pad=14)
    ax.set_xlabel("Revenue (€)", color=_AX, fontsize=11)
    ax.set_ylabel("Product",     color=_AX, fontsize=11)

    plt.tight_layout()
    plt.savefig(out_path, dpi=200, bbox_inches="tight")
    plt.close()

def make_rfm_chart(df: pd.DataFrame, out_path: Path):
    """
    Match ecommerce_analysis.ipynb (PIE CHART):
    - If segment column exists, plot it.
    - Else, rebuild RFM from raw:
        Recency = (max InvoiceDate - last purchase) in days
        Frequency = number of invoices
        Monetary = sum(LineAmount) with returns excluded
      Score each on 1..5 (quantiles) and sum → RFM_Score.
      Segment with same thresholds/labels (with emojis) as notebook.
    - Neon styling.
    - Render as a PIE chart (not bar).
    """
    if df.empty:
        return

    work = df.copy()
    cols = set(work.columns)

    # If already segmented
    seg_col = next((c for c in ["Segment", "RFM_Segment", "rfm_segment", "segment", "RFMGroup", "rfmgroup"] if c in cols), None)
    if seg_col is None:
        # Need raw columns to build RFM
        cust_col = next((c for c in ["CustomerID", "Customer Id", "customerid"] if c in cols), None)
        date_col = next((c for c in ["InvoiceDate", "invoice_date", "Date", "date"] if c in cols), None)
        amt_col  = next((c for c in ["LineAmount", "Line Amount", "Amount", "Revenue", "lineamount"] if c in cols), None)
        inv_col  = next((c for c in ["InvoiceNo", "Invoice", "Invoice_Number", "invoiceno", "InvoiceID"] if c in cols), None)

        if not (cust_col and date_col and amt_col):
            # Fallback: dummy single slice
            seg_plot = pd.DataFrame({"Segment": ["No RFM Segments Found"], "Count": [len(work)]})
            seg_name = "Segment"
        else:
            # Filter for monetary = exclude returns
            if "IsReturn" in cols:
                work = work[work["IsReturn"] == 0].copy()

            work[date_col] = _maybe_parse_dates(work[date_col])
            latest_date = work[date_col].max()

            freq_series = work.groupby(cust_col)[inv_col].nunique() if inv_col else work.groupby(cust_col)[date_col].count()
            mon_series  = work.groupby(cust_col)[amt_col].sum()
            rec_series  = (latest_date - work.groupby(cust_col)[date_col].max()).dt.days

            rfm_built = pd.DataFrame({
                "CustomerID": freq_series.index,
                "Recency":    rec_series.values,
                "Frequency":  freq_series.values,
                "Monetary":   mon_series.loc[freq_series.index].values
            })

            # Score 1..5 via quantiles (1=best for Recency; 5=best for F/M)
            r_rank = pd.qcut(rfm_built["Recency"].rank(method="first", ascending=True), 5, labels=[5,4,3,2,1]).astype(int)
            f_rank = pd.qcut(rfm_built["Frequency"].rank(method="first", ascending=False), 5, labels=[1,2,3,4,5]).astype(int)
            m_rank = pd.qcut(rfm_built["Monetary"].rank(method="first", ascending=False), 5, labels=[1,2,3,4,5]).astype(int)
            rfm_built["RFM_Score"] = r_rank + f_rank + m_rank

            # Same labels & thresholds as notebook
            def segment_customer(score: int) -> str:
                if score >= 12:
                    return "💎 Champions"
                elif score >= 9:
                    return "💼 Loyal Customers"
                elif score >= 6:
                    return "🌱 Regular Buyers"
                else:
                    return "⚠️ At Risk / Lost"

            rfm_built["Segment"] = rfm_built["RFM_Score"].apply(segment_customer)
            seg_plot = rfm_built.groupby("Segment").size().reset_index(name="Count").sort_values("Count", ascending=False)
            seg_name = "Segment"
    else:
        seg_plot = work.groupby(seg_col).size().reset_index(name="Count").sort_values("Count", ascending=False)
        seg_name = seg_col

    # ---- PIE CHART (matches notebook) ----
    fig, ax = plt.subplots(figsize=(9.5, 6.5), facecolor=_BG)
    ax.set_facecolor(_BG)

    sizes  = seg_plot["Count"].values
    labels = seg_plot[seg_name].astype(str).values

    # Consistent neon palette
    colors = (_NEON_PALETTE * (len(sizes)//len(_NEON_PALETTE) + 1))[:len(sizes)]

    # Slightly explode "Champions" slice for emphasis (if present)
    explode = [0.08 if ("Champions" in str(lbl)) else 0.02 for lbl in labels]

    wedges, texts, autotexts = ax.pie(
        sizes,
        labels=None,               # labels in legend to keep plot clean
        autopct="%1.1f%%",
        startangle=140,
        explode=explode,
        colors=colors,
        wedgeprops={"linewidth": 1.0, "edgecolor": _BG},
        pctdistance=0.75
    )

    # Donut hole (common in notebook visual styles)
    centre_circle = plt.Circle((0, 0), 0.48, fc=_BG)
    fig.gca().add_artist(centre_circle)

    # Legend with names + counts
    legend_labels = [f"{lbl} — {cnt:,}" for lbl, cnt in zip(labels, sizes)]
    ax.legend(wedges, legend_labels, title="Segments", loc="center left", bbox_to_anchor=(1.0, 0.5), fontsize=9)

    ax.set_title("👥 Customer Segmentation (RFM)", color=_TITLE, fontsize=14, fontweight="bold", pad=14)
    ax.axis("equal")  # Equal aspect ratio ensures the pie is circular.

    plt.tight_layout()
    plt.savefig(out_path, dpi=200, bbox_inches="tight")
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

    Story.append(Spacer(1, 30))

Story.append(Paragraph("Visual Summary", styles["Heading2Cyan"]))
Story.append(Spacer(1, 10))

if IMG_REV_PY.exists():
    Story.append(Paragraph("Monthly Revenue Trend", styles["Heading3Cyan"]))
    Story.append(fit_image_keep_ratio(IMG_REV_PY, max_w=16.5*cm, max_h=8.8*cm))
    Story.append(Spacer(1, 10))
else:
    Story.append(Paragraph("Monthly revenue chart not found (expected 03_Analysis/figures/monthly_revenue_py.png).", styles["SmallGrey"]))

Story.append(PageBreak())

# === Page 2 === (PY charts)
Story.append(Paragraph("Top 10 Products by Revenue", styles["Heading2Cyan"]))
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
