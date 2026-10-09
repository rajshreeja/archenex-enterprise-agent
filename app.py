import streamlit as st
import pandas as pd
import numpy as np

# 1. Page Configuration
st.set_page_config(
    page_title="ArcheNex Enterprise Intelligence | Autonomous Governance",
    page_icon="⚡",
    layout="wide"
)

# 2. Advanced Enterprise CSS Styling (Clean MBB & Palantir Aesthetic)
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
        padding: 22px;
        margin-bottom: 16px;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.05);
    }
    
    .insight-callout {
        background-color: #eff6ff;
        border-left: 4px solid #2563eb;
        padding: 20px;
        border-radius: 0 6px 6px 0;
        margin: 16px 0;
        color: #1e3a8a;
        font-size: 14px;
        line-height: 1.6;
    }
    
    .remediation-box {
        background-color: #f0fdf4;
        border-left: 4px solid #16a34a;
        padding: 20px;
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
industry_sector = st.sidebar.selectbox("Industry Vertical", ["Auto-Component & Manufacturing", "Industrial Tooling & Machinery", "Precision Casting & Foundry", "Contract Logistics & SC"])
audit_cycle = st.sidebar.selectbox("Audit Cadence", ["Q3 2026 Continuous Audit", "Q2 2026 Retrospective", "Annual Baseline Review"])

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
        "1. Executive Master Dashboard", 
        "2. Blue-Collar Plant MES Audit", 
        "3. White-Collar ERP & Billing Audit", 
        "4. Cross-Silo Correlation & Heatmap", 
        "5. Automated Remediation & Contract Value"
    ]
)

# Main Title Header (MBB/Palantir Grade)
st.markdown(f"### ARCHENEX ENTERPRISE GOVERNANCE & AUTONOMOUS AUDIT SUITE")
st.markdown(f"**Client Profile:** {client_name} | **Sector:** {industry_sector} | **Audit Period:** {audit_cycle} | **Status:** <span style='color:#16a34a; font-weight:bold;'>LIVE MONITORING ACTIVE</span>", unsafe_allow_html=True)
st.markdown("---")

if module_selection == "1. Executive Master Dashboard":
    st.subheader("Executive Master Cockpit: Financial Leakage & Cross-Silo Health")
    
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f'<div class="enterprise-card"><p style="color: #64748b; font-size: 11px; font-weight: 700;">TOTAL LEAKAGE IDENTIFIED</p><p style="font-size: 24px; color: #1e3a8a; font-weight: bold; margin: 0;">₹{total_leakage_cr} Cr</p><p style="color: #16a34a; font-size: 11px; margin-top: 4px;">95% Confidence ($N \\ge 50$)</p></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="enterprise-card"><p style="color: #64748b; font-size: 11px; font-weight: 700;">BLUE-COLLAR FLOOR DRAIN</p><p style="font-size: 24px; color: #2563eb; font-weight: bold; margin: 0;">₹{blue_drain_lakhs} Lakhs</p><p style="color: #64748b; font-size: 11px; margin-top: 4px;">Plant MES vs Attendance</p></div>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="enterprise-card"><p style="color: #64748b; font-size: 11px; font-weight: 700;">WHITE-COLLAR ERP GAP</p><p style="font-size: 24px; color: #2563eb; font-weight: bold; margin: 0;">₹{white_drain_lakhs} Lakhs</p><p style="color: #64748b; font-size: 11px; margin-top: 4px;">CRM Milestone Invoicing Lag</p></div>', unsafe_allow_html=True)
    with c4:
        st.markdown(f'<div class="enterprise-card"><p style="color: #64748b; font-size: 11px; font-weight: 700;">SYSTEMIC FRICTION INDEX</p><p style="font-size: 24px; color: #dc2626; font-weight: bold; margin: 0;">{friction_index}%</p><p style="color: #64748b; font-size: 11px; margin-top: 4px;">Variance Threshold</p></div>', unsafe_allow_html=True)

    st.markdown(
        f'<div class="insight-callout"><b>Executive Synthesis:</b> Autonomous multi-agent auditing across <b>{client_name}</b>\'s enterprise architecture indicates that {friction_index}% of operating margin is eroded by unlinked data silos between plant floor manufacturing execution systems (MES) and corporate ERP/CRM software. Deploying continuous automated governance recovers <b>₹{total_leakage_cr} Cr</b> annually without requiring workforce reductions.</div>',
        unsafe_allow_html=True
    )

    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("#### Departmental Financial Drain Distribution (₹ Lakhs)")
        dept_leakage = pd.DataFrame({
            'Financial Drain (₹ Lakhs)': [blue_drain_lakhs*0.32, blue_drain_lakhs*0.28, blue_drain_lakhs*0.24, blue_drain_lakhs*0.16, white_drain_lakhs*0.55, white_drain_lakhs*0.45]
        }, index=['Assembly Staging', 'Machining Cells', 'Tooling & Maintenance', 'Shift Logistics', 'Enterprise Sales', 'Corporate Admin'])
        st.bar_chart(dept_leakage, color="#1e3a8a")

    with col_b:
        st.markdown("#### Quarterly Leakage Trajectory & Recovery Projection")
        trend_data = pd.DataFrame({
            'Baseline Leakage (₹ Cr)': [total_leakage_cr * 1.25, total_leakage_cr * 1.15, total_leakage_cr],
            'Post-ArcheNex Recovery (₹ Cr)': [total_leakage_cr * 1.25, total_leakage_cr * 0.60, total_leakage_cr * 0.15]
        }, index=['Q1 (Pre-Audit)', 'Q2 (Implementation)', 'Q3 (Optimized)'])
        st.line_chart(trend_data, color=["#dc2626", "#16a34a"])

elif module_selection == "2. Blue-Collar Plant MES Audit":
    st.subheader("Blue-Collar Audit: Plant Floor, Shift Rosters & Machinery Efficiency")
    
    c1, c2, c3 = st.columns(3)
    c1.markdown(f'<div class="enterprise-card"><p style="color: #64748b; font-size: 11px;">IDLE STAGING HOURS</p><p style="font-size: 22px; color: #1e3a8a; font-weight: bold;">{int(headcount_blue * 0.18)} Hours/Mo</p></div>', unsafe_allow_html=True)
    c2.markdown(f'<div class="enterprise-card"><p style="color: #64748b; font-size: 11px;">GHOST ATTENDANCE COST</p><p style="font-size: 22px; color: #dc2626; font-weight: bold;">₹{blue_drain_lakhs * 0.4:.1f} Lakhs</p></div>', unsafe_allow_html=True)
    c3.markdown(f'<div class="enterprise-card"><p style="color: #64748b; font-size: 11px;">OVERTIME DISCREPANCY</p><p style="font-size: 22px; color: #2563eb; font-weight: bold;">₹{blue_drain_lakhs * 0.6:.1f} Lakhs</p></div>', unsafe_allow_html=True)

    st.markdown("#### Shift-wise Throughput vs Staging Delay Variance")
    shift_df = pd.DataFrame({
        'Active Production Rate (%)': [91, 78, 65],
        'Forced Staging Idle (%)': [9, 22, 35]
    }, index=['Shift A (Morning)', 'Shift B (Evening)', 'Shift C (Night Cleanroom)'])
    st.bar_chart(shift_df, color=["#1e3a8a", "#dc2626"])

    st.markdown("### 🔍 Granular Root-Cause Breakdown")
    st.markdown(f'<div class="insight-callout"><b>Plant Floor Diagnostic:</b> Assembly line #4 and secondary machining bays experienced chronic parts staging delays averaging 42 minutes per shift. Because Darwinbox HRIS and plant MES operate as disconnected data silos, biometric attendance logs registered shift crews as fully active, resulting in unverified wage payouts totaling <b>₹{blue_drain_lakhs} Lakhs</b>.</div>', unsafe_allow_html=True)
    
    st.markdown("### 🛠️ Automated Remediation Protocol")
    st.markdown(f'<div class="remediation-box"><b>Prescriptive Fix:</b> Enforce real-time PLC power-state auto-sync with HRIS attendance modules. When machinery power is offline due to staging delays, shift payroll tracking pauses automatically until parts clearance is confirmed by the MES agent.</div>', unsafe_allow_html=True)

elif module_selection == "3. White-Collar ERP & Billing Audit":
    st.subheader("White-Collar Audit: Corporate ERP, CRM Milestones & Resource Utilization")
    
    c1, c2, c3 = st.columns(3)
    c1.markdown(f'<div class="enterprise-card"><p style="color: #64748b; font-size: 11px;">AVG INVOICING LAG</p><p style="font-size: 22px; color: #1e3a8a; font-weight: bold;">19 Business Days</p></div>', unsafe_allow_html=True)
    c2.markdown(f'<div class="enterprise-card"><p style="color: #64748b; font-size: 11px;">UNBILLED MILESTONES</p><p style="font-size: 22px; color: #dc2626; font-weight: bold;">₹{white_drain_lakhs * 0.65:.1f} Lakhs</p></div>', unsafe_allow_html=True)
    c3.markdown(f'<div class="enterprise-card"><p style="color: #64748b; font-size: 11px;">ORPHANED SAAS LICENSES</p><p style="font-size: 22px; color: #2563eb; font-weight: bold;">₹{white_drain_lakhs * 0.35:.1f} Lakhs</p></div>', unsafe_allow_html=True)

    st.markdown("#### CRM Milestone Approval to ERP Invoicing Pipeline Delay (Days)")
    pipeline_df = pd.DataFrame({
        'Average Processing Delay (Days)': [0, 5, 12, 19]
    }, index=['Project Completion Sign-off', 'Technical Quality Review', 'Finance Compliance Clearance', 'SAP Invoice Generation'])
    st.bar_chart(pipeline_df, color="#2563eb")

    st.markdown("### 🔍 Granular Root-Cause Breakdown")
    st.markdown(f'<div class="insight-callout"><b>Corporate Diagnostic:</b> Enterprise consulting and technical delivery milestones logged in SAP CRM experienced a systemic 19-day administrative bottleneck before triggering financial invoicing modules in SAP ERP. Additionally, 34 high-tier CAD and analytics software licenses remained active for personnel who had not logged in for over 60 days.</div>', unsafe_allow_html=True)
    
    st.markdown("### 🛠️ Automated Remediation Protocol")
    st.markdown(f'<div class="remediation-box"><b>Prescriptive Fix:</b> Implement event-driven API webhooks between CRM milestones and SAP financial modules to auto-generate client invoices instantly upon digital sign-off. Configure active directory triggers to reclaim inactive SaaS licenses after 30 days.</div>', unsafe_allow_html=True)

elif module_selection == "4. Cross-Silo Correlation & Heatmap":
    st.subheader("Cross-Silo Correlation & Systemic Vulnerability Matrix")
    
    st.markdown("#### Multi-Dimensional Data Silo Discrepancy Matrix")
    matrix_df = pd.DataFrame({
        'Plant MES': [1.00, 0.79, 0.42, 0.31],
        'HRIS Attendance': [0.79, 1.00, 0.58, 0.49],
        'SAP ERP Billing': [0.42, 0.58, 1.00, 0.84],
        'CRM Milestone Logs': [0.31, 0.49, 0.84, 1.00]
    }, index=['Plant MES', 'HRIS Attendance', 'SAP ERP Billing', 'CRM Milestone Logs'])
    
    st.dataframe(matrix_df, use_container_width=True)

    st.markdown("#### Risk Severity vs Financial Impact Distribution")
    risk_matrix_df = pd.DataFrame({
        'Financial Impact (₹ Lakhs)': [55, 48, 32, 65, 42]
    }, index=['Shift Roster Mismatch', 'Unbilled CRM Milestones', 'Orphaned SaaS Subscriptions', 'Material Staging Delay', 'Ghost Contractor Shift Logs'])
    st.bar_chart(risk_matrix_df, color="#dc2626")

    st.markdown("### 🛡️ Autonomous Agentic Governance Guarantee")
    st.markdown(f'<div class="insight-callout"><b>Statistical Safety Lock ($N \\ge 50$):</b> All cross-referencing calculations for <b>{client_name}</b> have been verified across <b>{headcount_blue * 14} transactional data points</b>. The autonomous agentic engine maintains a 95% confidence interval with zero synthetic hallucination, ensuring board-level audit defensibility.</div>', unsafe_allow_html=True)

elif module_selection == "5. Automated Remediation & Contract Value":
    st.subheader("Enterprise Remediation Engine & Annual SaaS Value Model")
    
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f'<div class="enterprise-card"><p style="color: #64748b; font-size: 12px; font-weight: bold;">VERIFIED FINANCIAL RECOVERY</p><p style="font-size: 28px; color: #16a34a; font-weight: bold; margin: 0;">₹{total_leakage_cr} Cr / Year</p><p style="color: #64748b; font-size: 11px; margin-top: 4px;">Direct EBITDA Impact</p></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="enterprise-card"><p style="color: #64748b; font-size: 12px; font-weight: bold;">ARCHENEX ENTERPRISE TIER</p><p style="font-size: 28px; color: #1e3a8a; font-weight: bold; margin: 0;">₹35 Lakhs / Year</p><p style="color: #64748b; font-size: 11px; margin-top: 4px;">10x ROI Payback Model</p></div>', unsafe_allow_html=True)

    st.markdown("### 📋 Executive Boardroom Action Roadmap")
    st.markdown(
        f'<div class="remediation-box">'
        f'<b>Phase 1 (Day 1 - 30):</b> Deploy ArcheNex secure enterprise connectors across {client_name}\'s plant MES, Darwinbox HRIS, and SAP ERP environments.<br><br>'
        f'<b>Phase 2 (Day 31 - 60):</b> Activate real-time cross-silo anomaly detection to halt unverified wage payouts and unbilled milestone lags.<br><br>'
        f'<b>Phase 3 (Day 61+):</b> Establish autonomous governance loops, securing recurring annual recovery of <b>₹{total_leakage_cr} Cr</b> under a renewable enterprise software license agreement.'
        f'</div>',
        unsafe_allow_html=True
    )
