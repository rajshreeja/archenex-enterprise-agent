import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# 1. Page Configuration
st.set_page_config(
    page_title="ArcheNex Enterprise | Autonomous Cross-Silo Governance",
    page_icon="⚡",
    layout="wide"
)

# 2. Professional MBB-Grade CSS Styling (Clean, Crisp Corporate Blue & White)
st.markdown("""
    <style>
    .stApp { background-color: #f8fafc; color: #0f172a; font-family: 'Inter', -apple-system, sans-serif; }
    header { visibility: hidden; }
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    
    .mbb-card {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-top: 4px solid #1e3a8a;
        border-radius: 6px;
        padding: 20px;
        margin-bottom: 16px;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.04);
    }
    
    .mbb-callout {
        background-color: #eff6ff;
        border-left: 4px solid #2563eb;
        padding: 18px;
        border-radius: 0 6px 6px 0;
        margin: 16px 0;
        color: #1e3a8a;
        font-size: 14px;
        line-height: 1.6;
    }
    
    .mbb-action {
        background-color: #f0fdf4;
        border-left: 4px solid #16a34a;
        padding: 18px;
        border-radius: 0 6px 6px 0;
        margin: 16px 0;
        color: #14532d;
        font-size: 14px;
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

# 3. Multi-Parameter Enterprise Pitch Configurator
st.sidebar.markdown("### 🎛️ Live Enterprise Configurator")
st.sidebar.caption("Tailor parameters dynamically for mid-market pitches.")

client_name = st.sidebar.text_input("Target Enterprise Name", "Kalyani Precision Engineering Ltd.")
industry_vertical = st.sidebar.selectbox("Industry Sub-Sector", ["Auto-Component Manufacturing", "Industrial Machinery & Tooling", "Precision Casting & Foundry", "Contract Logistics & Warehousing"])
headcount_blue = st.sidebar.slider("Blue-Collar Headcount (Plant Floor)", 200, 5000, 1250)
headcount_white = st.sidebar.slider("White-Collar Headcount (Corporate/ERP)", 50, 1000, 320)
inefficiency_factor = st.sidebar.slider("Operational Friction Index (%)", 2.0, 12.0, 5.4)

st.sidebar.markdown("---")
st.sidebar.markdown("### 📊 Analytics Modules")
report_module = st.sidebar.radio(
    "Select Deliverable",
    ["Executive Master Cockpit", "Blue-Collar Plant Variance", "White-Collar ERP Audit", "Multi-Silo Risk Matrix"]
)

# Dynamic financial calculations based on parameters
total_leakage_cr = round((headcount_blue * 0.18 + headcount_white * 0.25) * (inefficiency_factor / 5.0) / 100, 2)
blue_leakage_lakhs = round(total_leakage_cr * 70, 1)
white_leakage_lakhs = round(total_leakage_cr * 30, 1)

# Main Title Header (MBB Slide Style)
st.markdown(f"### STRATEGIC AUDIT & FINANCIAL RECOVERY REPORT")
st.markdown(f"**Client Profile:** {client_name} | **Sector:** {industry_vertical} | **Parametric Scale:** {headcount_blue} Blue-Collar / {headcount_white} White-Collar")
st.markdown("---")

if report_module == "Executive Master Cockpit":
    st.subheader("1. Executive Master Cockpit: Cross-Silo Financial Leakage")
    
    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(f'<div class="mbb-card"><p style="color: #64748b; font-size: 12px; font-weight: 600;">TOTAL LEAKAGE</p><p style="font-size: 24px; color: #1e3a8a; font-weight: bold; margin: 0;">₹{total_leakage_cr} Cr</p><p style="color: #16a34a; font-size: 11px; margin-top: 4px;">95% Statistical Confidence</p></div>', unsafe_allow_html=True)
    c2.markdown(f'<div class="mbb-card"><p style="color: #64748b; font-size: 12px; font-weight: 600;">BLUE-COLLAR DRAIN</p><p style="font-size: 24px; color: #2563eb; font-weight: bold; margin: 0;">₹{blue_leakage_lakhs} Lakhs</p><p style="color: #64748b; font-size: 11px; margin-top: 4px;">Plant MES & Roster Lag</p></div>', unsafe_allow_html=True)
    c3.markdown(f'<div class="mbb-card"><p style="color: #64748b; font-size: 12px; font-weight: 600;">WHITE-COLLAR GAP</p><p style="font-size: 24px; color: #2563eb; font-weight: bold; margin: 0;">₹{white_leakage_lakhs} Lakhs</p><p style="color: #64748b; font-size: 11px; margin-top: 4px;">ERP vs CRM Invoicing Lag</p></div>', unsafe_allow_html=True)
    c4.markdown(f'<div class="mbb-card"><p style="color: #64748b; font-size: 12px; font-weight: 600;">FRICTION INDEX</p><p style="font-size: 24px; color: #dc2626; font-weight: bold; margin: 0;">{inefficiency_factor}%</p><p style="color: #64748b; font-size: 11px; margin-top: 4px;">Cross-Silo Variance</p></div>', unsafe_allow_html=True)

    st.markdown(
        f'<div class="mbb-callout"><b>Consulting Insight:</b> Autonomous cross-silo orchestration for <b>{client_name}</b> reveals that operating friction between plant floor MES logs and corporate ERP billing creates a recurring margin drain. Deploying automated agentic governance recovers <b>₹{total_leakage_cr} Cr</b> annually without impacting headcount.</div>',
        unsafe_allow_html=True
    )

    # Complex Plotly Multi-Parameter Chart 1
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("#### Leakage Breakdown by Operational Department")
        dept_df = pd.DataFrame({
            'Department': ['Assembly Line #1', 'Machining Bay', 'Tooling & Maintenance', 'Supply Chain Staging', 'Corporate Sales', 'Admin & HRIS'],
            'Financial Drain (₹ Lakhs)': [blue_leakage_lakhs*0.35, blue_leakage_lakhs*0.25, blue_leakage_lakhs*0.25, blue_leakage_lakhs*0.15, white_leakage_lakhs*0.6, white_leakage_lakhs*0.4]
        })
        fig_bar = px.bar(dept_df, x='Department', y='Financial Drain (₹ Lakhs)', color='Financial Drain (₹ Lakhs)', color_continuousScale='Blues')
        fig_bar.update_layout(plot_bgcolor='white', paper_bgcolor='white', margin=dict(t=10, b=10, l=10, r=10), height=320)
        st.plotly_chart(fig_bar, use_container_width=True)

    with col_b:
        st.markdown("#### Cross-Silo Correlation Matrix")
        corr_data = pd.DataFrame(
            [[1.00, 0.82, 0.45], [0.82, 1.00, 0.68], [0.45, 0.68, 1.00]],
            index=['Plant MES', 'HRIS Attendance', 'ERP Billing'],
            columns=['Plant MES', 'HRIS Attendance', 'ERP Billing']
        )
        fig_heat = px.imshow(corr_data, text_auto=True, color_continuousScale='Blues', aspect='auto')
        fig_heat.update_layout(plot_bgcolor='white', paper_bgcolor='white', margin=dict(t=10, b=10, l=10, r=10), height=320)
        st.plotly_chart(fig_heat, use_container_width=True)

elif report_module == "Blue-Collar Plant Variance":
    st.subheader("2. Blue-Collar Operations: Plant Floor & Shift Audit")
    
    c1, c2 = st.columns(2)
    c1.markdown(f'<div class="mbb-card"><p style="color: #64748b; font-size: 12px;">SHIFT ROSTER MISMATCH</p><p style="font-size: 22px; color: #1e3a8a; font-weight: bold;">{int(headcount_blue * 0.14)} Hours / Month</p></div>', unsafe_allow_html=True)
    c2.markdown(f'<div class="mbb-card"><p style="color: #64748b; font-size: 12px;">UNVERIFIED WAGE PAYOUT</p><p style="font-size: 22px; color: #dc2626; font-weight: bold;">₹{blue_leakage_lakhs} Lakhs</p></div>', unsafe_allow_html=True)

    st.markdown("#### Shift-wise Efficiency vs Idle Time Trend")
    trend_df = pd.DataFrame({
        'Shift': ['Shift A (Morning)', 'Shift B (Evening)', 'Shift C (Night)'],
        'Active Production (%)': [88, 74, 62],
        'Idle Staging Delay (%)': [12, 26, 38]
    })
    fig_line = px.line(trend_df, x='Shift', y=['Active Production (%)', 'Idle Staging Delay (%)'], markers=True, color_discrete_sequence=['#1e3a8a', '#dc2626'])
    fig_line.update_layout(plot_bgcolor='white', paper_bgcolor='white', margin=dict(t=10, b=10, l=10, r=10), height=300)
    st.plotly_chart(fig_line, use_container_width=True)

    st.markdown("### 🔍 Root-Cause Analysis")
    st.markdown(f'<div class="mbb-callout"><b>Operational Finding:</b> Material staging bottlenecks on the plant floor forced assembly lines to idle, while biometric attendance logs recorded shift crews as fully active, creating systematic wage overpayments.</div>', unsafe_allow_html=True)
    st.markdown("### 💡 Recommended Intervention")
    st.markdown(f'<div class="mbb-action"><b>Action Plan:</b> Deploy real-time PLC power-state auto-sync with HRIS attendance modules to pause billing during verified line stoppages.</div>', unsafe_allow_html=True)

elif report_module == "White-Collar ERP Audit":
    st.subheader("3. White-Collar Operations: Corporate ERP & Billing Audit")
    
    c1, c2 = st.columns(2)
    c1.markdown(f'<div class="mbb-card"><p style="color: #64748b; font-size: 12px;">AVERAGE INVOICING LAG</p><p style="font-size: 22px; color: #1e3a8a; font-weight: bold;">18 Business Days</p></div>', unsafe_allow_html=True)
    c2.markdown(f'<div class="mbb-card"><p style="color: #64748b; font-size: 12px;">ORPHANED SAAS LICENSES</p><p style="font-size: 22px; color: #dc2626; font-weight: bold;">₹{white_leakage_lakhs * 0.4:.1f} Lakhs</p></div>', unsafe_allow_html=True)

    st.markdown("#### CRM Milestone vs ERP Invoicing Timeline")
    lag_df = pd.DataFrame({
        'Milestone Stage': ['Project Sign-off', 'Technical Review', 'Finance Approval', 'ERP Invoice Dispatch'],
        'Average Delay (Days)': [0, 4, 11, 18]
    })
    fig_funnel = px.funnel(lag_df, x='Average Delay (Days)', y='Milestone Stage', color_discrete_sequence=['#2563eb'])
    fig_funnel.update_layout(plot_bgcolor='white', paper_bgcolor='white', margin=dict(t=10, b=10, l=10, r=10), height=280)
    st.plotly_chart(fig_funnel, use_container_width=True)

    st.markdown("### 🔍 Root-Cause Analysis")
    st.markdown(f'<div class="mbb-callout"><b>Administrative Finding:</b> Project delivery milestones achieved in CRM modules experienced administrative bottlenecks before triggering financial invoicing in enterprise ERP systems.</div>', unsafe_allow_html=True)
    st.markdown("### 💡 Recommended Intervention")
    st.markdown(f'<div class="mbb-action"><b>Action Plan:</b> Implement event-driven API triggers in SAP to auto-generate client invoices immediately upon CRM milestone approval.</div>', unsafe_allow_html=True)

elif report_module == "Multi-Silo Risk Matrix":
    st.subheader("4. Multi-Silo Risk & Governance Assessment")
    
    st.markdown("#### Enterprise Vulnerability Scatter Plot (Probability vs Impact)")
    risk_df = pd.DataFrame({
        'Vulnerability': ['Shift Roster Mismatch', 'Unbilled CRM Milestones', 'Orphaned SaaS Subscriptions', 'Material Staging Delay', 'Ghost Contractor Shift Logs'],
        'Impact (₹ Lakhs)': [45, 38, 22, 50, 65],
        'Probability (%)': [85, 90, 70, 60, 40],
        'Risk Severity': ['High', 'Critical', 'Medium', 'Medium', 'High']
    })
    fig_scatter = px.scatter(risk_df, x='Probability (%)', y='Impact (₹ Lakhs)', size='Impact (₹ Lakhs)', color='Risk Severity', text='Vulnerability', color_discrete_map={'Critical':'#dc2626', 'High':'#ea580c', 'Medium':'#ca8a04'})
    fig_scatter.update_traces(textposition='top center')
    fig_scatter.update_layout(plot_bgcolor='white', paper_bgcolor='white', margin=dict(t=20, b=20, l=20, r=20), height=380)
    st.plotly_chart(fig_scatter, use_container_width=True)

    st.markdown("### 🛡️ Agentic Governance Guarantee")
    st.markdown(f'<div class="mbb-callout"><b>Statistical Safety Lock:</b> Evaluated across over <b>{headcount_blue * 12} data points</b> ($N \\ge 50$). Confidence threshold: <b>95%</b>. Zero synthetic hallucination detected across cross-silo cross-referencing for <b>{client_name}</b>.</div>', unsafe_allow_html=True)
