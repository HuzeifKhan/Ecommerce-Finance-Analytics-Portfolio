# -*- coding: utf-8 -*-
"""
Generate a clean PDF report with Tableau visuals for the Ecommerce & Finance Analytics Portfolio.
Output: 06_Reports/Ecommerce_Finance_Insights_Report.pdf
Requires:
    pip install reportlab pandas
"""

# --- Imports ---
import os
from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image

# --- Define paths dynamically ---
BASE_DIR = Path(__file__).resolve().parents[1]         # Repo root
DATA_DIR = BASE_DIR / "01_Data" / "processed"
IMG_DIR = BASE_DIR / "05_Tableau" / "exports"          # << your correct folder name
REPORT_DIR = BASE_DIR / "06_Reports"
REPORT_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_PATH = REPORT_DIR / "Ecommerce_Finance_Insights_Report.pdf"

print("🔍 Checking image paths:")
for fn in ["dashboard_overview.png", "monthly_revenue.png", "top_products.png", "customer_segments.png"]:
    print(f"   {fn} ->", (IMG_DIR / fn).exists())

# --- Initialize PDF ---
doc = SimpleDocTemplate(str(OUTPUT_PATH), pagesize=A4)
styles = getSampleStyleSheet()
Story = []

# --- Helper function to add an image safely ---
def add_img(title, filename, w=500, h=260):
    Story.append(Paragraph(f"<b>{title}</b>", styles["Heading3"]))
    p = IMG_DIR / filename
    if p.exists():
        try:
            img = Image(str(p), width=w, height=h)
            Story.append(img)
        except Exception as e:
            Story.append(Paragraph(f"<font color='red'>⚠️ Could not load image: {filename}</font>", styles["BodyText"]))
    else:
        Story.append(Paragraph(f"<font color='red'>⚠️ Missing image: {p}</font>", styles["BodyText"]))
    Story.append(Spacer(1, 12))

# --- Title Page ---
Story.append(Paragraph("<b>E-commerce & Finance Analytics Portfolio</b>", styles["Title"]))
Story.append(Spacer(1, 14))
Story.append(Paragraph("Generated via Python (ReportLab) | Author: Huzeif Khan", styles["Normal"]))
Story.append(Spacer(1, 30))
Story.append(Paragraph("<b>Project Summary</b>", styles["Heading2"]))
Story.append(Paragraph(
    "An end-to-end data analytics portfolio integrating SQL, Python, and Tableau to deliver "
    "business insights from e-commerce transaction data. This report highlights KPIs, key visual summaries, "
    "and Tableau dashboard exports.",
    styles["BodyText"]
))
Story.append(Spacer(1, 20))

# --- Dashboard Overview ---
Story.append(Paragraph("<b>📈 Dashboard Overview</b>", styles["Heading2"]))
add_img("Full Tableau Dashboard (Overview)", "dashboard_overview.png")

# --- Tableau Visuals ---
Story.append(Spacer(1, 20))
Story.append(Paragraph("<b>📊 Visual Summary (Tableau Exports)</b>", styles["Heading2"]))
Story.append(Spacer(1, 10))

add_img("Monthly Revenue Trend", "monthly_revenue.png")
add_img("Top 10 Products by Revenue", "top_products.png")
add_img("Customer Segmentation (RFM Model)", "customer_segments.png")

# --- Footer ---
Story.append(Spacer(1, 25))
Story.append(Paragraph("<b>📄 Generated via Python (ReportLab)</b>", styles["Italic"]))
Story.append(Paragraph("Huzeif Khan | Data Analytics & BI Portfolio | Berlin, Germany", styles["Normal"]))

# --- Build the PDF ---
doc.build(Story)
print(f"✅ Report saved to {OUTPUT_PATH}")



