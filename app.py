import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import io
from datetime import datetime, timedelta
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

# 1. Page Configuration
st.set_page_config(
    page_title="ArcheNex Enterprise Intelligence | Autonomous Governance",
    page_icon="⚡",
    layout="wide"
)

# 2. Ultra-Sleek MBB & Palantir Enterprise CSS
st.markdown("""
    <style>
    .stApp { background-color: #f8fafc; color: #0f172a; font-family: 'Inter', -apple-system, sans-serif; }
    header { visibility: hidden; }
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    
    .enterprise-card {
        background-color: #ffffff;
        border: 1px solid #cbd5e1;
        border-top: 4px solid #1e3a8a;
        border-radius: 6px;
        padding: 20px;
        margin-bottom: 16px;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.05);
    }
    
    .layman-box {
        background-color: #eff6ff;
        border-left: 4px solid #2563eb;
        padding: 18px;
        border-radius: 0 6px 6px 0;
        margin: 16px 0;
        color: #1e3a8a;
        font-size: 14px;
        line-height: 1.6;
    }
    
    .action-box {
        background-color: #f0fdf4;
        border-left: 4px solid #16a34a;
        padding: 18px;
        border-radius: 0 6px 6px 0;
        margin: 16px 0;
        color: #14532d;
        font-size: 14px;
        line-height: 1.6;
    }

    [data-testid="stSidebar"] { 
        background-color: #ffffff; 
        border-right: 1px solid #e2e8f0; 
    }
    
    .stButton>button {
        background-color: #1e3a8a;
        color: white;
        border: none;
        border-radius: 4px;
        padding: 10px 20px;
        font-weight: 600;
        width: 100%;
    }
    .stButton>button:hover { background-color: #1d4ed8; }
    </style>
""", unsafe_allow_html=True)

# 3. Enterprise Control Console (Sidebar)
st.sidebar.markdown("### 🏢 Enterprise Target Setup")
client_name = st.sidebar.text_input("Target Organization", "Kalyani Precision Engineering Ltd.")
industry_sector = st.sidebar.selectbox("Industry Vertical", ["Auto-Component Manufacturing", "Industrial Tooling & Machinery", "Precision Casting & Foundry", "Contract Logistics & SC"])

st.sidebar.markdown("---")
st.sidebar.markdown("### 🔌 Client Tech Stack Connectors")
hris_system = st.sidebar.selectbox("Target HRIS / Attendance System", ["Darwinbox", "Workday HCM", "SAP SuccessFactors", "Keka HR", "greytHR"])
erp_system = st.sidebar.selectbox("Target ERP / CRM System", ["SAP S/4HANA", "Microsoft Dynamics 365", "Oracle NetSuite", "Infor CloudSuite"])

st.sidebar.markdown("---")
st.sidebar.markdown("### 🎛️ Parametric Scaling Engine")
headcount_blue = st.sidebar.slider("Blue-Collar Headcount (Plant Floor)", 300, 5000, 1450)
headcount_white = st.sidebar.slider("White-Collar Headcount (Corporate ERP)", 80, 1200, 380)
friction_index = st.sidebar.slider("Cross-Silo Friction Coefficient (%)", 2.0, 15.0, 6.2)

# Dynamic Calculations for Enterprise Scale
total_leakage_cr = round((headcount_blue * 0.22 + headcount_white * 0.31) * (friction_index / 5.0) / 100, 2)
blue_drain_lakhs = round(total_leakage_cr * 68, 1)
white_drain_lakhs = round(total_leakage_cr * 32, 1)

st.sidebar.markdown("---")
st.sidebar.markdown("### 📑 Navigation Cockpit")
module_selection = st.sidebar.radio(
    "Select Enterprise Module",
    [
        "1. Executive Master Cockpit", 
        "2. Granular Transactional Audit Log", 
        "3. Plant MES & HRIS Deep-Dive", 
        "4. ERP & Billing Reconciliation", 
        "5. Boardroom Dossier & Export"
    ]
)

# Main Title Header
st.markdown("### ARCHENEX ENTERPRISE GOVERNANCE & AUTONOMOUS AUDIT SUITE")
st.markdown(f"**Client Profile:** {client_name} | **Active Connectors:** {hris_system} + {erp_system} | **Status:** <span style='color:#16a34a; font-weight:bold;'>CONTINUOUS GOVERNANCE ACTIVE</span>", unsafe_allow_html=True)
st.markdown("---")

# Ledger DataFrame definition for reuse
ledger_df = pd.DataFrame({
    'Audit Vector': ['Plant Floor Shift Roster Mismatch', 'Unbilled CRM Milestone Lag', 'Orphaned SaaS Subscriptions', 'Material Staging Downtime Drain', 'Contractor Attendance Discrepancy'],
    'Source Silos': [f'MES & {hris_system}', f'CRM & {erp_system}', 'Corporate IT & HRIS', 'Plant MES & SC', f'MES & {hris_system}'],
    'Financial Leakage (₹ Lakhs)': [round(blue_drain_lakhs * 0.35, 1), round(white_drain_lakhs * 0.50, 1), round(white_drain_lakhs * 0.50, 1), round(blue_drain_lakhs * 0.35, 1), round(blue_drain_lakhs * 0.30, 1)],
    'Remediation Status': ['Automated API Sync Ready', 'Webhook Trigger Ready', 'Auto-Reclaim Active', 'PLC Power-State Lock Ready', 'Biometric Gate Sync Ready']
})

if module_selection == "1. Executive Master Cockpit":
    st.subheader("Executive Master Cockpit: Financial Leakage & Cross-Silo Health")
    
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f'<div class="enterprise-card"><p style="color: #64748b; font-size: 11px; font-weight: 700;">TOTAL LEAKAGE IDENTIFIED</p><p style="font-size: 24px; color: #1e3a8a; font-weight: bold; margin: 0;">₹{total_leakage_cr} Cr</p><p style="color: #16a34a; font-size: 11px; margin-top: 4px;">95% Confidence (N >= 50)</p></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="enterprise-card"><p style="color: #64748b; font-size: 11px; font-weight: 700;">BLUE-COLLAR FLOOR DRAIN</p><p style="font-size: 24px; color: #2563eb; font-weight: bold; margin: 0;">₹{blue_drain_lakhs} Lakhs</p><p style="color: #64748b; font-size: 11px; margin-top: 4px;">Plant MES vs {hris_system}</p></div>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="enterprise-card"><p style="color: #64748b; font-size: 11px; font-weight: 700;">WHITE-COLLAR ERP GAP</p><p style="font-size: 24px; color: #2563eb; font-weight: bold; margin: 0;">₹{white_drain_lakhs} Lakhs</p><p style="color: #64748b; font-size: 11px; margin-top: 4px;">{erp_system} Invoicing Lag</p></div>', unsafe_allow_html=True)
    with c4:
        st.markdown(f'<div class="enterprise-card"><p style="color: #64748b; font-size: 11px; font-weight: 700;">SYSTEMIC FRICTION INDEX</p><p style="font-size: 24px; color: #dc2626; font-weight: bold; margin: 0;">{friction_index}%</p><p style="color: #64748b; font-size: 11px; margin-top: 4px;">Variance Threshold</p></div>', unsafe_allow_html=True)

    st.markdown(
        f'<div class="layman-box"><b>In Plain English (The Big Picture):</b> Imagine your factory floor as an engine and your corporate office as the steering wheel. Right now, they aren\'t communicating. When parts are delayed on the factory floor, workers wait around—yet your {hris_system} attendance system keeps paying them as if everything is running smoothly. At the same time, your office completes projects but takes weeks to send invoices because {erp_system} isn\'t linked to project delivery logs. ArcheNex acts as the digital bridge, recovering <b>₹{total_leakage_cr} Cr</b> annually without laying off a single person.</div>',
        unsafe_allow_html=True
    )

    col_a, col_b = st.columns(2
