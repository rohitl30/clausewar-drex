# generate_docs.py
from fpdf import FPDF
import os

os.makedirs("sample_docs", exist_ok=True)

DOCS = {
    "RFP_Requirements.pdf": (
        "REQUEST FOR PROPOSAL: CLOUD GPU CLUSTER (RFP-2026-88)\n\n"
        "1. Scope: 64x H200 GPU nodes for 12-month reserved compute.\n"
        "2. Target Budget Ceiling: $480,000 USD total ($40,000/month max).\n"
        "3. Required Uptime SLA: Minimum 99.9% uptime with financial penalty credits.\n"
        "4. Payment Terms: Preferred Net-60; Net-30 acceptable only if total price <= $455,000.\n"
        "5. Delivery Deadline: Full cluster live within 14 calendar days of signing."
    ),
    "VendorA_ApexCompute.pdf": (
        "PROPOSAL: APEX COMPUTE SYSTEMS\n\n"
        "Total Quote: $510,000 USD ($42,500/month).\n"
        "SLA Guarantee: 99.95% uptime with 15% monthly credit penalty.\n"
        "Payment Terms: Net-30 strictly.\n"
        "Deployment Timeline: 7 calendar days (hardware already racked in US-West).\n"
        "Walk-Away Floor: Cannot drop below $468,000 unless payment is Net-15."
    ),
    "VendorB_NebulaScale.pdf": (
        "PROPOSAL: NEBULA SCALE INFRASTRUCTURE\n\n"
        "Total Quote: $492,000 USD ($41,000/month).\n"
        "SLA Guarantee: 99.9% uptime with 10% credit penalty.\n"
        "Payment Terms: Net-60 standard.\n"
        "Deployment Timeline: 12 calendar days.\n"
        "Flexibility Note: Willing to discount up to 6% to secure an enterprise logo."
    ),
    "VendorC_BudgetNode.pdf": (
        "PROPOSAL: BUDGETNODE AI HOSTING\n\n"
        "Total Quote: $445,000 USD ($37,083/month).\n"
        "SLA Guarantee: 99.5% uptime (no financial penalty credits).\n"
        "Payment Terms: 50% upfront, 50% Net-30.\n"
        "Deployment Timeline: 21 calendar days."
    ),
}

for filename, body in DOCS.items():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", size=11)
    pdf.multi_cell(0, 8, body)
    pdf.output(os.path.join("sample_docs", filename))

print("Generated 4 sample contract PDFs in ./sample_docs/")