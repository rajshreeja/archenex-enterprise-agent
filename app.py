import streamlit as st

# 1. Page Configuration
st.set_page_config(
    page_title="ArcheNex Enterprise | Autonomous Audit Suite",
    page_icon="⚡",
    layout="wide"
)

# 2. Professional Enterprise CSS (Fixing contrast, native headers, and radio buttons)
st.markdown("""
    <style>
    /* Global Theme - Deep Corporate Slate */
    .stApp { background-color: #0f172a; color: #f8fafc; font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif; }
    
    /* Hide Streamlit Default Header and Footer for Clean SaaS Look */
    header { visibility: hidden; }
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    
    /* Sleek Card Containers */
    .metric-card {
        background-color: #1e293b;
        border: 1px solid #334155;
        border-radius: 8px;
        padding: 20px;
        margin-bottom: 15px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2);
    }
    
    /* Explanation & Action Boxes */
    .executive-summary-box {
        background-color: #1e293b;
        border-left: 4px solid #3b82f6;
        padding: 18px;
        border-radius: 0 8px 8px 0;
        margin: 20px 0;
        color: #e2e8f0;
        font-size: 15px;
        line-height: 1.6;
        border-top: 1px solid #334155;
        border-right: 1px solid #334155;
        border-bottom: 1px solid #334155;
    }
    
    .remediation-box {
        background-color: #064e3b;
        border-left: 4px solid #10b981;
        padding: 18px;
        border-radius: 0 8px 8px 0;
        margin: 20px 0;
        color: #d1fae5;
        font-size: 15px;
        border-top: 1px solid #065f46;
        border-right: 1px solid #065f46;
        border-bottom: 1px solid #065f46;
    }

    /* Sidebar Styling */
    [data-testid="stSidebar"] { 
        background-color: #090d16; 
        border-right: 1px solid #1e293b; 
    }
    
    /* Custom Styling for Radio Options */
    .stRadio label {
        color: #cbd5e1 !important;
        font-weight: 500;
    }
    
    /* Professional Primary Button */
    .stButton>button {
        background-color: #2563eb;
        color: white;
        border: none;
        border-radius: 6px;
        padding: 10px 20px;
        font-weight: 600;
        width: 100%;
        transition: background-color 0.2s;
    }
    .stButton>button:hover { background-color: #1d4ed8; }
    </style>
""", unsafe_allow_html=True)

# 3. Enterprise Client Data Repository
CLIENT_DATABASE = {
    "Tata Motors (Pune Plant)": {
        "industry": "Automotive & Heavy Manufacturing",
        "total_leakage": "₹1.76 Cr",
        "blue_collar": {
            "title": "Factory Floor & Shift Operations",
            "metric_1": "310 Idle Hours",
            "metric_2": "₹42.5 Lakhs Leakage",
            "layman_summary": "Factory assembly line #4 experienced unexpected downtime due to material staging delays. Meanwhile, the HR attendance system logged teams as fully active, paying for idle labor.",
            "action": "Automated Remediation: Integrate PLC power-state logs directly with Darwinbox attendance to suspend shift billing during verified line stoppages."
        },
        "white_collar": {
            "title": "Corporate Office & Software Systems",
            "metric_1": "₹68.0 Lakhs Unbilled",
            "metric_2": "₹14.2 Lakhs License Waste",
            "layman_summary": "Corporate project milestones were completed in SAP CRM, but disconnects with downstream billing modules delayed invoice generation by an average of 14 days.",
            "action": "Automated Remediation: Establish event-driven triggers in SAP to auto-generate client invoices immediately upon CRM milestone approval."
        }
    },
    "Bosch India (Bangalore Hub)": {
        "industry": "Industrial Technology & Engineering",
        "total_leakage": "₹2.10 Cr",
        "blue_collar": {
            "title": "Factory Floor & Shift Operations",
            "metric_1": "185 Idle Hours",
            "metric_2": "₹28.0 Lakhs Leakage",
            "layman_summary": "SMT manufacturing lines encountered micro-stoppages. Contract shift rosters showed full capacity, while real-time throughput counters confirmed waiting periods.",
            "action": "Automated Remediation: Implement real-time component barcode scanning at station entry to synchronize shift allocations."
        },
        "white_collar": {
            "title": "Corporate Office & Software Systems",
            "metric_1": "₹92.4 Lakhs Unbilled",
            "metric_2": "₹21.5 Lakhs License Waste",
            "layman_summary": "High-tier engineering and analytics software licenses continued renewing automatically for personnel inactive for over 45 days.",
            "action": "Automated Remediation: Deploy automated license de-provisioning rules across active directory after 30 days of non-usage."
        }
    }
}

# Sidebar Control Console
st.sidebar.markdown("### 🏢 Enterprise Console")
selected_client = st.sidebar.selectbox("Target Enterprise", list(CLIENT_DATABASE.keys()))

st.sidebar.markdown("---")
st.sidebar.markdown("### 📑 Report Modules")
report_view = st.sidebar.radio(
    "Select View",
    ["Executive Master Report", "Blue-Collar Operations", "White-Collar Corporate"]
)

client_data = CLIENT_DATABASE[selected_client]

st.sidebar.markdown("---")
run_audit = st.sidebar.button("Execute Agentic Audit")

# Main Header Section
st.markdown(f"## ⚡ ArcheNex Intelligence Suite")
st.markdown(f"**Target Enterprise:** {selected_client} | **Sector:** {client_data['industry']}")
st.markdown("---")

# Default or Executed View Logic
if run_audit or report_view:
        
    if report_view == "Executive Master Report":
        st.subheader("Executive Financial Recovery Briefing")
        
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(f'<div class="metric-card"><p style="color: #94a3b8; font-size: 14px; margin-bottom: 4px;">TOTAL IDENTIFIED LEAKAGE</p><p style="font-size: 26px; color: #38bdf8; font-weight: bold; margin: 0;">{client_data["total_leakage"]}</p><p style="color: #64748b; font-size: 12px; margin-top: 6px;">Confidence Level: 95% ($N \\geq 50$)</p></div>', unsafe_allow_html=True)
        with c2:
            st.markdown(f'<div class="metric-card"><p style="color: #94a3b8; font-size: 14px; margin-bottom: 4px;">BLUE-COLLAR VARIANCE</p><p style="font-size: 26px; color: #34d399; font-weight: bold; margin: 0;">{client_data["blue_collar"]["metric_2"]}</p><p style="color: #64748b; font-size: 12px; margin-top: 6px;">Plant Floor & MES</p></div>', unsafe_allow_html=True)
        with c3:
            st.markdown(f'<div class="metric-card"><p style="color: #94a3b8; font-size: 14px; margin-bottom: 4px;">WHITE-COLLAR GAP</p><p style="font-size: 26px; color: #fbbf24; font-weight: bold; margin: 0;">{client_data["white_collar"]["metric_1"]}</p><p style="color: #64748b; font-size: 12px; margin-top: 6px;">Corporate ERP & HRIS</p></div>', unsafe_allow_html=True)
        
        st.markdown("### 📋 Executive Summary")
        st.markdown(
            f'<div class="executive-summary-box"><b>Strategic Overview:</b> Cross-silo orchestration between factory MES and corporate ERP environments for <b>{selected_client}</b> reveals systemic leakage split evenly between plant floor waiting inefficiencies and delayed corporate billing cycles. Adopting autonomous agentic oversight enables full financial recovery without staffing cutbacks.</div>',
            unsafe_allow_html=True
        )

    elif report_view == "Blue-Collar Operations":
        st.subheader(f"🏭 Blue-Collar Audit: {client_data['blue_collar']['title']}")
        
        c1, c2 = st.columns(2)
        c1.markdown(f'<div class="metric-card"><p style="color: #94a3b8; font-size: 14px; margin-bottom: 4px;">MACHINERY INEFFICIENCY</p><p style="font-size: 24px; color: #38bdf8; font-weight: bold; margin: 0;">{client_data["blue_collar"]["metric_1"]}</p></div>', unsafe_allow_html=True)
        c2.markdown(f'<div class="metric-card"><p style="color: #94a3b8; font-size: 14px; margin-bottom: 4px;">FINANCIAL LEAKAGE</p><p style="font-size: 24px; color: #f87171; font-weight: bold; margin: 0;">{client_data["blue_collar"]["metric_2"]}</p></div>', unsafe_allow_html=True)
        
        st.markdown("### 🔍 Root-Cause Analysis (Plain English)")
        st.markdown(f'<div class="executive-summary-box">{client_data["blue_collar"]["layman_summary"]}</div>', unsafe_allow_html=True)
        
        st.markdown("### 🛠️ Recommended Action Plan")
        st.markdown(f'<div class="remediation-box">{client_data["blue_collar"]["action"]}</div>', unsafe_allow_html=True)

    elif report_view == "White-Collar Corporate":
        st.subheader(f"💻 White-Collar Audit: {client_data['white_collar']['title']}")
        
        c1, c2 = st.columns(2)
        c1.markdown(f'<div class="metric-card"><p style="color: #94a3b8; font-size: 14px; margin-bottom: 4px;">UNBILLED REVENUE</p><p style="font-size: 24px; color: #fbbf24; font-weight: bold; margin: 0;">{client_data["white_collar"]["metric_1"]}</p></div>', unsafe_allow_html=True)
        c2.markdown(f'<div class="metric-card"><p style="color: #94a3b8; font-size: 14px; margin-bottom: 4px;">LICENSE WASTE</p><p style="font-size: 24px; color: #f87171; font-weight: bold; margin: 0;">{client_data["white_collar"]["metric_2"]}</p></div>', unsafe_allow_html=True)
        
        st.markdown("### 🔍 Root-Cause Analysis (Plain English)")
        st.markdown(f'<div class="executive-summary-box">{client_data["white_collar"]["layman_summary"]}</div>', unsafe_allow_html=True)
        
        st.markdown("### 🛠️ Recommended Action Plan")
        st.markdown(f'<div class="remediation-box">{client_data["white_collar"]["action"]}</div>', unsafe_allow_html=True)
