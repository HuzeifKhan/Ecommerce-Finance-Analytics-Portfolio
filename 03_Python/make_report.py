# -*- coding: utf-8 -*-
"""
Generate a 2-page PDF with KPIs + charts for the Ecommerce Finance Analytics project.
Outputs: 06_Reports/Ecommerce_Finance_Insights_Report.pdf

Requires:
    pip install reportlab pandas
"""

import os
import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.utils import ImageReader

# --------------------------------------------------------------------
# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "01_Data", "processed")
REPORT_DIR = os.path.join(BASE_DIR, "06_Reports")
REPORT_FN = "Ecommerce_Finance_Insights_Report.pdf"
os.makedirs(REPORT_DIR, exist_ok=True)

# --------------------------------------------------------------------
# File paths
csv_revenue = os.path.join(DATA_DIR, "monthly_revenue.csv")
csv_products = os.path.join(DATA_DIR, "top_products.csv")
csv_rfm = os.path.join(DATA_DIR, "customer_rfm_segments.csv")

# Optional chart images (if exported manually)
fig_revenue = os.path.join(BASE_DIR, "05_Tableau", "monthly_revenue.png")
fig_products = os.path.join(BASE_DIR, "05_Tableau", "top_products.png")
fig_rfm = os.path.join(BASE_DIR, "05_Tableau", "customer_segments.png")

# --------------------------------------------------------------------
# Load data safely
def load_csv_safely(path):
    if os.path.exists(path):
        return pd.read_csv(path)
    else:
        print(f"⚠️  Missing file: {path}")
        return pd.DataFrame()

df_rev = load_csv_safely(csv_revenue)
df_prod = load_csv_safely(csv_products)
df_rfm = load_csv_safely(csv_rfm)

# --------------------------------------------------------------------
# Compute KPIs
try:
    total_revenue = df_rev["Line Amount"].sum()
except KeyError:
    total_revenue = 0

try:
    total_customers = df_rfm["Customer ID"].nunique()
except KeyError:
    total_customers = 0

avg_order_value = total_revenue / total_customers if total_customers else 0

# --------------------------------------------------------------------
# Draw helper for optional charts
def draw_image_if_exists(img_path, y_pos):
    if os.path.exists(img_path):
        try:
            img = ImageReader(img_path)
            c.drawImage(img, 2*cm, y_pos, width=15*cm, height=7*cm, preserveAspectRatio=True)
        except Exception as e:
            print(f"⚠️ Could not render {img_path}: {e}")

# --------------------------------------------------------------------
# Create PDF
c = canvas.Canvas(os.path.join(REPORT_DIR, REPORT_FN), pagesize=A4)
W, H = A4

# Title page
c.setFillColor(colors.darkblue)
c.setFont("Helvetica-Bold", 24)
c.drawCentredString(W/2, H - 3*cm, "E-Commerce & Finance Insights Report")

c.setFont("Helvetica", 14)
c.setFillColor(colors.black)
c.drawCentredString(W/2, H - 4*cm, "Generated via Python ReportLab | Author: Huzeif Khan")

# KPIs
c.setFont("Helvetica-Bold", 16)
c.drawString(2*cm, H - 6*cm, "Key Performance Indicators (KPIs)")
c.setFont("Helvetica", 12)
c.drawString(2*cm, H - 7*cm, f"• Total Revenue: {total_revenue:,.0f}")
c.drawString(2*cm, H - 8*cm, f"• Total Customers: {total_customers:,}")
c.drawString(2*cm, H - 9*cm, f"• Average Order Value: {avg_order_value:,.2f}")

c.setFont("Helvetica-Oblique", 10)
c.setFillColor(colors.grey)
c.drawRightString(W - 2*cm, 1.5*cm, "Generated via Python ReportLab • GitHub: Ecommerce-Finance-Analytics-Portfolio")
c.showPage()

# Page 2 – Charts
c.setFont("Helvetica-Bold", 14)
c.setFillColor(colors.black)
c.drawString(2*cm, H - 2.5*cm, "Visual Summary")

c.setFont("Helvetica-Bold", 11)
c.setFillColor(colors.whitesmoke)
c.drawString(2*cm, H - 3*cm, "Monthly Revenue Trend")
draw_image_if_exists(fig_revenue, y_pos=H - 10*cm)

c.setFont("Helvetica-Bold", 11)
c.setFillColor(colors.whitesmoke)
c.drawString(2*cm, 9*cm, "Top Products by Revenue")
draw_image_if_exists(fig_products, y_pos=2*cm)

c.setFont("Helvetica-Bold", 11)
c.setFillColor(colors.whitesmoke)
c.drawString(2*cm, 1*cm, "Customer Segmentation (RFM)")
draw_image_if_exists(fig_rfm, y_pos=-5*cm)

# Footer
c.setFont("Helvetica", 8)
c.setFillColor(colors.grey)
c.drawRightString(W - 1.5*cm, 1.3*cm, "Generated via Python ReportLab • GitHub: Ecommerce-Finance-Analytics-Portfolio")
c.save()

print(f"✅ Report saved to {os.path.join(REPORT_DIR, REPORT_FN)}")
