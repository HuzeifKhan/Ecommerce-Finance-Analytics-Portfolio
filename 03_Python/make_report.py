# -*- coding: utf-8 -*-
"""
Generate a 2-page PDF report with KPIs + charts for the Ecommerce Finance Analytics project.
Output: 06_Reports/Ecommerce_Finance_Insights_Report.pdf

Priority for charts (page 2):
1) Use existing PNGs if found in 05_Tableau/ (or common alternates)
2) Otherwise, auto-generate charts with matplotlib as a fallback
"""

import os
from pathlib import Path
import pandas as pd

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.utils import ImageReader

# -----------------------
# Paths & folders
# -----------------------
BASE_DIR   = Path(__file__).resolve().parents[1]
DATA_DIR   = BASE_DIR / "01_Data" / "processed"
OUT_DIR    = BASE_DIR / "06_Reports"
OUT_FILE   = OUT_DIR / "Ecommerce_Finance_Insights_Report.pdf"
PNG_DIR    = BASE_DIR / "05_Tableau"        # where you might export tableau PNGs
ALT_PNGDIR = BASE_DIR / "03_Analysis" / "figures"  # optional alternates
TMP_DIR    = BASE_DIR / "03_Python" / "_tmp_charts"

OUT_DIR.mkdir(parents=True, exist_ok=True)
TMP_DIR.mkdir(parents=True, exist_ok=True)

# -----------------------
# Helpers
# -----------------------
def load_table(base_dir: Path, stem: str) -> pd.DataFrame:
    """Load CSV or XLSX (auto-detect)."""
    p_csv  = base_dir / f"{stem}.csv"
    p_xlsx = base_dir / f"{stem}.xlsx"
    if p_csv.exists():
        print(f"✓ Loading {p_csv.name}")
        return pd.read_csv(p_csv)
    if p_xlsx.exists():
        print(f"✓ Loading {p_xlsx.name}")
        return pd.read_excel(p_xlsx)
    existing = [f.name for f in base_dir.glob(f"{stem}.*")]
    raise FileNotFoundError(f"❌ Could not find {stem}.csv or {stem}.xlsx in {base_dir}\nFound: {existing}")

def find_chart_png(basenames: list[str]) -> Path | None:
    """Try to find a PNG by any of the basenames in PNG_DIR or ALT_PNGDIR."""
    search_dirs = [PNG_DIR, ALT_PNGDIR]
    for d in search_dirs:
        for name in basenames:
            p = d / f"{name}.png"
            if p.exists():
                return p
    return None

def draw_img_or_placeholder(c: canvas.Canvas, img_path: Path | None,
                            x: float, y: float, w: float, h: float, title: str):
    """Draw an image if available, else a labelled placeholder box."""
    c.setFillColor(colors.white)
    c.setStrokeColor(colors.HexColor("#7A7A7A"))
    c.rect(x, y, w, h, fill=1, stroke=1)

    c.setFillColor(colors.black)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(x + 0.3*cm, y + h + 0.3*cm, title)

    if img_path and img_path.exists():
        try:
            img = ImageReader(str(img_path))
            c.drawImage(img, x+0.25*cm, y+0.25*cm, width=w-0.5*cm, height=h-0.5*cm,
                        preserveAspectRatio=True, anchor='sw')
            return
        except Exception as e:
            print(f"⚠️ Could not draw image {img_path.name}: {e}")

    # Placeholder text if missing/failed
    c.setFont("Helvetica-Oblique", 10)
    c.setFillColor(colors.HexColor("#5f5f5f"))
    c.drawString(x + 0.3*cm, y + h/2, "Chart image not found. Fallback will be attempted.")

def ensure_fallback_pngs(monthly: pd.DataFrame, products: pd.DataFrame, rfm: pd.DataFrame) -> dict[str, Path | None]:
    """
    Ensure we have PNGs for: monthly_revenue, top_products, customer_segments.
    If not found, try to generate simple charts with matplotlib (if installed).
    Returns dict with keys: 'monthly', 'products', 'segments'
    """
    # 1) Try to find user-exported images first
    found = {
        "monthly":  find_chart_png(["monthly_revenue", "1_Monthly_Revenue", "MonthlyRevenue"]),
        "products": find_chart_png(["top_products", "2_Top_Products_by_Revenue", "TopProducts"]),
        "segments": find_chart_png(["customer_segments", "3_Customer_Segments_RFM", "CustomerSegments"])
    }
    if all(found.values()):
        return found

    # 2) Fallback: try to auto-generate missing images with matplotlib
    try:
        import matplotlib.pyplot as plt
    except Exception as e:
        print("⚠️ matplotlib not available; cannot generate fallback PNGs.\n"
              "   Install with: py -3.13 -m pip install matplotlib")
        return found

    TMP_DIR.mkdir(parents=True, exist_ok=True)

    # Monthly revenue line (fallback)
    if found["monthly"] is None:
        try:
            fig = plt.figure(figsize=(8, 3))
            plt.plot(monthly.iloc[:, 0], monthly.iloc[:, 1], marker='o')
            plt.title("Monthly Revenue")
            plt.xlabel(str(monthly.columns[0]))
            plt.ylabel(str(monthly.columns[1]))
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
            out = TMP_DIR / "monthly_revenue_fallback.png"
            fig.savefig(out, dpi=150)
            plt.close(fig)
            found["monthly"] = out
        except Exception as e:
            print(f"⚠️ Fallback monthly chart failed: {e}")

    # Top products bar (fallback) – use Top 10 if more
    if found["products"] is None:
        try:
            dfp = products.copy()
            # assume last column is the metric if ambiguous
            if dfp.shape[1] >= 2:
                metric_col = dfp.columns[-1]
                label_col  = dfp.columns[0]
                dfp = dfp.nlargest(10, metric_col)
                fig = plt.figure(figsize=(8, 3))
                plt.barh(dfp[label_col], dfp[metric_col])
                plt.title("Top Products by Revenue (Top 10)")
                plt.xlabel(metric_col)
                plt.tight_layout()
                out = TMP_DIR / "top_products_fallback.png"
                fig.savefig(out, dpi=150)
                plt.close(fig)
                found["products"] = out
        except Exception as e:
            print(f"⚠️ Fallback top-products chart failed: {e}")

    # Customer segments pie (fallback)
    if found["segments"] is None:
        try:
            seg_col = None
            for col in rfm.columns:
                if str(col).lower() in ("segment", "seg", "rfm_segment", "rfm segments", "rfm_segments"):
                    seg_col = col
                    break
            if seg_col is None:
                # fallback to first column if nothing explicit
                seg_col = rfm.columns[0]
            counts = rfm[seg_col].value_counts().sort_values(ascending=False)
            fig = plt.figure(figsize=(4, 4))
            plt.pie(counts.values, labels=counts.index, autopct='%1.1f%%', startangle=90)
            plt.title("Customer Segmentation (RFM)")
            plt.tight_layout()
            out = TMP_DIR / "customer_segments_fallback.png"
            fig.savefig(out, dpi=150)
            plt.close(fig)
            found["segments"] = out
        except Exception as e:
            print(f"⚠️ Fallback segments chart failed: {e}")

    return found

# -----------------------
# Load data
# -----------------------
print("\n📂 Files in processed:")
for f in sorted(DATA_DIR.glob("*")):
    print(" -", f.name)

monthly      = load_table(DATA_DIR, "monthly_revenue")
top_products = load_table(DATA_DIR, "top_products")
rfm          = load_table(DATA_DIR, "customer_rfm_segments")

# -----------------------
# KPIs (adjust column names if needed)
# -----------------------
# assume first col is period, second col is revenue
total_revenue   = monthly.iloc[:, 1].sum() if monthly.shape[1] > 1 else 0.0
total_customers = int(rfm.shape[0])
avg_order_value = (total_revenue / total_customers) if total_customers else 0.0

print(f"\nKPIs → Revenue: {total_revenue:,.2f} | Customers: {total_customers:,} | AOV: {avg_order_value:,.2f}")

# -----------------------
# PDF assembly
# -----------------------
c = canvas.Canvas(str(OUT_FILE), pagesize=A4)
W, H = A4
margin = 2*cm
gap = 0.6*cm

# Page 1 — Title + KPIs
c.setFont("Helvetica-Bold", 18)
c.drawString(margin, H - margin, "E-Commerce & Finance Insights Report")

c.setFont("Helvetica", 12)
c.drawString(margin, H - margin - 0.7*cm, "Generated via Python ReportLab | Author: Huzeif Khan")

c.setFont("Helvetica-Bold", 14)
c.drawString(margin, H - margin - 2.5*cm, "Key Performance Indicators (KPIs)")

c.setFont("Helvetica", 12)
y0 = H - margin - 3.5*cm
c.drawString(margin + 0.4*cm, y0,     f"• Total Revenue: {total_revenue:,.2f}")
c.drawString(margin + 0.4*cm, y0-0.8*cm, f"• Total Customers: {total_customers:,}")
c.drawString(margin + 0.4*cm, y0-1.6*cm, f"• Average Order Value: {avg_order_value:,.2f}")

c.showPage()

# Page 2 — Charts
c.setFont("Helvetica-Bold", 16)
c.drawString(margin, H - margin, "Visual Summary")

# chart boxes layout
top_h = 7.2*cm
top_w = W - 2*margin
top_x = margin
top_y = H - margin - top_h - 0.6*cm

bot_h = 7.2*cm
bot_w = (W - 2*margin - gap)/2
bot_y = margin

left_x  = margin
right_x = margin + bot_w + gap

# Ensure PNGs (prefer user-exported -> fallback)
pngs = ensure_fallback_pngs(monthly, top_products, rfm)

# Draw them
draw_img_or_placeholder(c, pngs["monthly"], top_x, top_y, top_w, top_h, "Monthly Revenue")
draw_img_or_placeholder(c, pngs["products"], left_x, bot_y, bot_w, bot_h, "Top Products by Revenue")
draw_img_or_placeholder(c, pngs["segments"], right_x, bot_y, bot_w, bot_h, "Customer Segmentation (RFM)")

# Footer
c.setFont("Helvetica", 9)
c.setFillColor(colors.HexColor("#777777"))
c.drawRightString(W - margin, margin/2,
                  "Generated via Python • GitHub: Ecommerce-Finance-Analytics-Portfolio")

c.save()

print(f"\n✅ Report saved to: {OUT_FILE}")
