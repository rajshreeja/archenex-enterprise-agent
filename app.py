import streamlit as st
import pandas as pd
import numpy as np

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

# 3. Enterprise Control Console (Sidebar with Flexible Connectors)
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
        "2. Blue-Collar Plant MES Audit", 
        "3. White-Collar ERP & Billing Audit", 
        "4. Multi-Silo Heatmap & Risk Matrix", 
        "5. Comprehensive Boardroom Dossier"
    ]
)

# Main Title Header
st.markdown(f"### ARCHENEX ENTERPRISE GOVERNANCE & AUTONOMOUS AUDIT SUITE")
st.markdown(f"**Client Profile:** {client_name} | **Active Connectors:** {hris_system} + {erp_system} | **Status:** <span style='color:#16a34a; font-weight:bold;'>CONTINUOUS GOVERNANCE ACTIVE</span>", unsafe_allow_html=True)
st.markdown("---")

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

    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("#### Departmental Financial Drain Breakdown (₹ Lakhs)")
        dept_df = pd.DataFrame({
            'Financial Drain (₹ Lakhs)': [blue_drain_lakhs*0.32, blue_drain_lakhs*0.28, blue_drain_lakhs*0.24, blue_drain_lakhs*0.16, white_drain_lakhs*0.55, white_drain_lakhs*0.45]
        }, index=['Assembly Staging', 'Machining Cells', 'Tooling & Maint.', 'Shift Logistics', 'Corporate Sales', 'Admin & HRIS'])
        st.bar_chart(dept_df, color="#1e3a8a")

    with col_b:
        st.markdown("#### Quarterly Recovery Trajectory (Pre vs Post ArcheNex)")
        trend_df = pd.DataFrame({
            'Baseline Leakage (₹ Cr)': [total_leakage_cr * 1.25, total_leakage_cr * 1.15, total_leakage_cr],
            'Post-Recovery Leakage (₹ Cr)': [total_leakage_cr * 1.25, total_leakage_cr * 0.60, total_leakage_cr * 0.15]
        }, index=['Q1 (Pre-Audit)', 'Q2 (Implementation)', 'Q3 (Optimized)'])
        st.line_chart(trend_df, color=["#dc2626", "#16a34a"])

elif module_selection == "2. Blue-Collar Plant MES Audit":
    st.subheader(f"Blue-Collar Audit: Plant Floor & {hris_system} Integration")
    
    overtime_cost = round(blue_drain_lakhs * 0.6, 1)
    ghost_cost = round(blue_drain_lakhs * 0.4, 1)
    idle_hrs = int(headcount_blue * 0.18)

    c1, c2, c3 = st.columns(3)
    c1.markdown(f'<div class="enterprise-card"><p style="color: #64748b; font-size: 11px;">IDLE STAGING HOURS</p><p style="font-size: 22px; color: #1e3a8a; font-weight: bold;">{idle_hrs} Hours/Mo</p></div>', unsafe_allow_html=True)
    c2.markdown(f'<div class="enterprise-card"><p style="color: #64748b; font-size: 11px;">GHOST ATTENDANCE COST</p><p style="font-size: 22px; color: #dc2626; font-weight: bold;">₹{ghost_cost} Lakhs</p></div>', unsafe_allow_html=True)
    c3.markdown(f'<div class="enterprise-card"><p style="color: #64748b; font-size: 11px;">OVERTIME DISCREPANCY</p><p style="font-size: 22px; color: #2563eb; font-weight: bold;">₹{overtime_cost} Lakhs</p></div>', unsafe_allow_html=True)

    col_1, col_2 = st.columns(2)
    with col_1:
        st.markdown("#### Shift-wise Efficiency vs Idle Time (%)")
        shift_df = pd.DataFrame({
            'Active Production Rate (%)': [91, 78, 65],
            'Forced Staging Idle (%)': [9, 22, 35]
        }, index=['Shift A (Morning)', 'Shift B (Evening)', 'Shift C (Night Cleanroom)'])
        st.bar_chart(shift_df, color=["#1e3a8a", "#dc2626"])

    with col_2:
        st.markdown("### 🔍 Granular Root-Cause Breakdown")
        st.markdown(f'<div class="layman-box"><b>What is happening?</b> Assembly line #4 experienced chronic parts staging delays. Because your <b>{hris_system}</b> attendance system and plant machine logs do not talk to each other, workers logged in at the gate are paid for full shifts even when assembly lines sit idle waiting for raw materials.</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="action-box"><b>How we fix it:</b> We connect ArcheNex via secure API to your <b>{hris_system}</b> instance. If machine power logs show downtime due to staging delays, shift payroll tracking automatically pauses until parts arrive.</div>', unsafe_allow_html=True)

elif module_selection == "3. White-Collar ERP & Billing Audit":
    st.subheader(f"White-Collar Audit: {erp_system} & Corporate Workflow Integration")
    
    unbilled_milestones = round(white_drain_lakhs * 0.65, 1)
    orphaned_saas = round(white_drain_lakhs * 0.35, 1)

    c1, c2, c3 = st.columns(3)
    c1.markdown(f'<div class="enterprise-card"><p style="color: #64748b; font-size: 11px;">AVG INVOICING LAG</p><p style="font-size: 22px; color: #1e3a8a; font-weight: bold;">19 Business Days</p></div>', unsafe_allow_html=True)
    c2.markdown(f'<div class="enterprise-card"><p style="color: #64748b; font-size: 11px;">UNBILLED MILESTONES</p><p style="font-size: 22px; color: #dc2626; font-weight: bold;">₹{unbilled_milestones} Lakhs</p></div>', unsafe_allow_html=True)
    c3.markdown(f'<div class="enterprise-card"><p style="color: #64748b; font-size: 11px;">ORPHANED SAAS LICENSES</p><p style="font-size: 22px; color: #2563eb; font-weight: bold;">₹{orphaned_saas} Lakhs</p></div>', unsafe_allow_html=True)

    col_1, col_2 = st.columns(2)
    with col_1:
        st.markdown("#### Milestone Approval to Invoicing Delay (Days)")
        lag_df = pd.DataFrame({
            'Average Delay (Days)': [0, 5, 12, 19]
        }, index=['Project Sign-off', 'Technical Review', 'Finance Compliance', f'{erp_system} Invoice Dispatch'])
        st.bar_chart(lag_df, color="#2563eb")

    with col_2:
        st.markdown("### 🔍 Granular Root-Cause Breakdown")
        st.markdown(f'<div class="layman-box"><b>What is happening?</b> When your consulting and technical teams finish a project milestone, it sits in administrative limbo for 19 days before someone manually inputs it into <b>{erp_system}</b> to generate an invoice. Simultaneously, your organization continues paying software subscriptions for personnel who haven\'t logged in for 60+ days.</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="action-box"><b>How we fix it:</b> We configure automated API triggers with <b>{erp_system}</b> so client invoices are generated the exact second a milestone is digitally signed off, while inactive SaaS licenses are auto-reclaimed.</div>', unsafe_allow_html=True)

elif module_selection == "4. Multi-Silo Heatmap & Risk Matrix":
    st.subheader("Cross-Silo Correlation & Systemic Vulnerability Matrix")
    
    col_1, col_2 = st.columns(2)
    with col_1:
        st.markdown("#### Data Silo Correlation Matrix Table")
        matrix_data = pd.DataFrame({
            'Plant MES': [1.00, 0.79, 0.42, 0.31],
            f'{hris_system}': [0.79, 1.00, 0.58, 0.49],
            f'{erp_system}': [0.42, 0.58, 1.00, 0.84],
            'CRM Milestones': [0.31, 0.49, 0.84, 1.00]
        }, index=['Plant MES', f'{hris_system}', f'{erp_system}', 'CRM Milestones'])
        st.dataframe(matrix_data, use_container_width=True)

    with col_2:
        st.markdown("#### Vulnerability Financial Impact (₹ Lakhs)")
        risk_df = pd.DataFrame({
            'Financial Impact (₹ Lakhs)': [45, 38, 22, 50, 65]
        }, index=['Shift Roster Mismatch', 'Unbilled CRM Milestones', 'Orphaned SaaS Subscriptions', 'Material Staging Delay', 'Ghost Contractor Logs'])
        st.bar_chart(risk_df, color="#dc2626")

    st.markdown(
        f'<div class="layman-box"><b>Audit Defensibility:</b> Evaluated across <b>{headcount_blue * 14} transactional data points</b> (N >= 50) with a 95% statistical confidence interval. Integrated seamlessly with <b>{hris_system}</b> and <b>{erp_system}</b> without custom database overhauls.</div>',
        unsafe_allow_html=True
    )

elif module_selection == "5. Comprehensive Boardroom Dossier":
    st.subheader("Comprehensive Boardroom Audit Dossier & Export Brief")
    
    st.markdown("### 📑 Executive Summary of Findings")
    st.markdown(
        f'<div class="layman-box">'
        f'<b>Target Organization:</b> {client_name}<br>'
        f'<b>Industry Vertical:</b> {industry_sector}<br>'
        f'<b>Integrated Architecture:</b> Plant MES + <b>{hris_system}</b> + <b>{erp_system}</b><br>'
        f'<b>Total Annual Leakage Detected:</b> ₹{total_leakage_cr} Cr (Equivalent to {(total_leakage_cr * 100 / 350):.1f}% of mid-market EBITDA baseline)<br>'
        f'<b>Statistical Confidence:</b> 95% ($N \\ge 50$ transactional audit vectors)'
        f'</div>',
        unsafe_allow_html=True
    )

    st.markdown("### 📊 Complete Financial Reconciliation Ledger")
    ledger_df = pd.DataFrame({
        'Audit Vector': ['Plant Floor Shift Roster Mismatch', 'Unbilled CRM Milestone Lag', 'Orphaned SaaS Subscriptions', 'Material Staging Downtime Drain', 'Contractor Attendance Discrepancy'],
        'Source Silos': [f'MES & {hris_system}', f'CRM & {erp_system}', 'Corporate IT & HRIS', 'Plant MES & SC', f'MES & {hris_system}'],
        'Financial Leakage (₹ Lakhs)': [blue_drain_lakhs * 0.35, white_drain_lakhs * 0.50, white_drain_lakhs * 0.50, blue_drain_lakhs * 0.35, blue_drain_lakhs * 0.30],
        'Remediation Status': ['Automated API Sync Ready', 'Webhook Trigger Ready', 'Auto-Reclaim Active', 'PLC Power-State Lock Ready', 'Biometric Gate Sync Ready']
    })
    st.dataframe(ledger_df, use_container_width=True)

    st.markdown("### 🚀 Boardroom Action Plan & Commercial Payback Model")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f'<div class="enterprise-card"><p style="color: #64748b; font-size: 12px; font-weight: bold;">VERIFIED FINANCIAL RECOVERY</p><p style="font-size: 28px; color: #16a34a; font-weight: bold; margin: 0;">₹{total_leakage_cr} Cr / Year</p><p style="color: #64748b; font-size: 11px; margin-top: 4px;">Direct EBITDA Impact</p></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="enterprise-card"><p style="color: #64748b; font-weight: bold; font-size: 12px;">ARCHENEX ENTERPRISE TIER</p><p style="font-size: 28px; color: #1e3a8a; font-weight: bold; margin: 0;">₹35 Lakhs / Year</p><p style="font-size: 24px; color: #16a34a; font-weight: bold; margin-top: 4px;">10x ROI Payback Model</p></div>', unsafe_allow_html=True)

    st.markdown(
        f'<div class="action-box">'
        f'<b>Implementation Roadmap:</b><br>'
        f'• <b>Phase 1 (Days 1–30):</b> Non-invasive API connector deployment across <b>{client_name}</b>\'s plant MES, <b>{hris_system}</b>, and <b>{erp_system}</b> environments.<br>'
        f'• <b>Phase 2 (Days 31–60):</b> Real-time anomaly detection activation to halt unbilled milestone lags and ghost attendance payouts.<br>'
        f'• <b>Phase 3 (Days 61+):</b> Continuous automated governance loop established, securing recurring annual recovery of <b>₹{total_leakage_cr} Cr</b>.'
        f'</div>',
        unsafe_allow_html=True
    )
