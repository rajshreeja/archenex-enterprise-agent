import streamlit as st
import pandas as pd
import numpy as np

# 1. Page Configuration
st.set_page_config(
    page_title="ArcheNex Enterprise | Strategic Audit Report",
    page_icon="⚡",
    layout="wide"
)

# 2. MBB-Style Blue & White Professional CSS
st.markdown("""
    <style>
    /* Clean Crisp White & Corporate Blue MBB Theme */
    .stApp { background-color: #f8fafc; color: #0f172a; font-family: 'Inter', -apple-system, sans-serif; }
    
    header { visibility: hidden; }
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    
    /* Elegant White Cards with Subtle Borders */
    .mbb-card {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-top: 4px solid #1e3a8a;
        border-radius: 6px;
        padding: 24px;
        margin-bottom: 20px;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.05);
    }
    
    .mbb-callout {
        background-color: #eff6ff;
        border-left: 4px solid #2563eb;
        padding: 20px;
        border-radius: 0 6px 6px 0;
        margin: 20px 0;
        color: #1e3a8a;
        font-size: 15px;
        line-height: 1.6;
    }
    
    .mbb-action {
        background-color: #f0fdf4;
        border-left: 4px solid #16a34a;
        padding: 20px;
        border-radius: 0 6px 6px 0;
        margin: 20px 0;
        color: #14532d;
        font-size: 15px;
    }

    /* Sidebar Styling */
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

# 3. Dynamic Prospect Onboarding (Built specifically for Mid-Market Sales)
st.sidebar.markdown("### 🎯 Live Prospect Configurator")
st.sidebar.caption("Type any mid-market target company to generate a tailored audit.")

prospect_name = st.sidebar.text_input("Target Company Name", "Apex Autotech Ltd. (Pune)")
prospect_revenue = st.sidebar.selectbox("Annual Revenue Scale", ["₹100Cr - ₹250Cr", "₹250Cr - ₹500Cr", "₹500Cr+"])

st.sidebar.markdown("---")
st.sidebar.markdown("### 📊 Report Modules")
report_module = st.sidebar.radio(
    "Select Deliverable",
    ["Executive Summary & Charts", "Blue-Collar (Plant Floor) Deep Dive", "White-Collar (Corporate ERP) Deep Dive"]
)

# Scale leakage dynamically based on prospect input
scale_factor = 1.2 if "₹250Cr" in prospect_revenue else (1.8 if "₹500Cr" in prospect_revenue else 0.8)

# Main Title Header (MBB Slide Style)
st.markdown(f"### STRATEGIC AUDIT & FINANCIAL RECOVERY REPORT")
st.markdown(f"**Prepared For:** {prospect_name} | **Framework:** Agentic Cross-Silo Governance")
st.markdown("---")

if report_module == "Executive Summary & Charts":
    st.subheader("1. Executive Summary: Cross-Silo Value Leakage")
    
    c1, c2, c3 = st.columns(3)
    c1.markdown(f'<div class="mbb-card"><p style="color: #64748b; font-size: 13px; font-weight: 600;">TOTAL LEAKAGE IDENTIFIED</p><p style="font-size: 28px; color: #1e3a8a; font-weight: bold; margin: 0;">₹{int(72 * scale_factor)} Lakhs</p><p style="color: #16a34a; font-size: 12px; margin-top: 6px;">↑ 95% Confidence Interval</p></div>', unsafe_allow_html=True)
    c2.markdown(f'<div class="mbb-card"><p style="color: #64748b; font-size: 13px; font-weight: 600;">BLUE-COLLAR VARIANCE</p><p style="font-size: 28px; color: #2563eb; font-weight: bold; margin: 0;">₹{int(42 * scale_factor)} Lakhs</p><p style="color: #64748b; font-size: 12px; margin-top: 6px;">Plant MES vs Attendance</p></div>', unsafe_allow_html=True)
    c3.markdown(f'<div class="mbb-card"><p style="color: #64748b; font-size: 13px; font-weight: 600;">WHITE-COLLAR GAP</p><p style="font-size: 28px; color: #2563eb; font-weight: bold; margin: 0;">₹{int(30 * scale_factor)} Lakhs</p><p style="color: #64748b; font-size: 12px; margin-top: 6px;">ERP Invoicing Lags</p></div>', unsafe_allow_html=True)
    
    st.markdown(
        f'<div class="mbb-callout"><b>MBB Diagnostic Takeaway:</b> Our autonomous cross-silo analysis for <b>{prospect_name}</b> indicates that 3.4% of operating margin is lost due to communication friction between factory-floor shift logs and corporate billing software. Implementing automated agentic synchronization captures immediate bottom-line recovery.</div>',
        unsafe_allow_html=True
    )
    
    st.markdown("### 📈 Financial Leakage Distribution by Department")
    chart_data = pd.DataFrame({
        'Department': ['Assembly Line #1', 'Machining Bay #2', 'Sales & Consulting', 'Corporate Administration'],
        'Leakage (₹ Lakhs)': [int(22 * scale_factor), int(20 * scale_factor), int(18 * scale_factor), int(12 * scale_factor)]
    }).set_index('Department')
    
    st.bar_chart(chart_data, color="#1e3a8a")

elif report_module == "Blue-Collar (Plant Floor) Deep Dive":
    st.subheader("2. Blue-Collar Operations: Plant Floor & Shift Audit")
    
    c1, c2 = st.columns(2)
    c1.markdown(f'<div class="mbb-card"><p style="color: #64748b; font-size: 13px;">PLANT IDLE TIMELINE</p><p style="font-size: 24px; color: #1e3a8a; font-weight: bold;">{int(180 * scale_factor)} Hours / Mo</p></div>', unsafe_allow_html=True)
    c2.markdown(f'<div class="mbb-card"><p style="color: #64748b; font-size: 13px;">GHOST ATTENDANCE COST</p><p style="font-size: 24px; color: #dc2626; font-weight: bold;">₹{int(42 * scale_factor)} Lakhs</p></div>', unsafe_allow_html=True)
    
    st.markdown("### 🔍 Root-Cause Analysis")
    st.markdown(f'<div class="mbb-callout"><b>Operational Breakdown:</b> Material staging bottlenecks forced primary production lines to halt while shift rosters in HR systems recorded labor crews as fully utilized, resulting in unverified wage payouts.</div>', unsafe_allow_html=True)
    
    st.markdown("### 💡 Recommended Strategic Intervention")
    st.markdown(f'<div class="mbb-action"><b>Action Plan:</b> Deploy real-time PLC-to-HRIS auto-sync to pause shift billing dynamically during machinery downtime.</div>', unsafe_allow_html=True)

elif report_module == "White-Collar (Corporate ERP) Deep Dive":
    st.subheader("3. White-Collar Operations: Corporate ERP & Billing Audit")
    
    c1, c2 = st.columns(2)
    c1.markdown(f'<div class="mbb-card"><p style="color: #64748b; font-size: 13px;">AVERAGE INVOICING LAG</p><p style="font-size: 24px; color: #1e3a8a; font-weight: bold;">16 Days</p></div>', unsafe_allow_html=True)
    c2.markdown(f'<div class="mbb-card"><p style="color: #64748b; font-size: 13px;">ORPHANED SOFTWARE LICENSES</p><p style="font-size: 24px; color: #dc2626; font-weight: bold;">₹{int(15 * scale_factor)} Lakhs</p></div>', unsafe_allow_html=True)
    
    st.markdown("### 🔍 Root-Cause Analysis")
    st.markdown(f'<div class="mbb-callout"><b>Administrative Breakdown:</b> Project delivery milestones achieved in CRM modules experienced systematic delays before triggering financial invoicing in enterprise ERP systems.</div>', unsafe_allow_html=True)
    
    st.markdown("### 💡 Recommended Strategic Intervention")
    st.markdown(f'<div class="mbb-action"><b>Action Plan:</b> Automate invoice creation workflows upon CRM milestone approval to accelerate cash flow cycles.</div>', unsafe_allow_html=True)
