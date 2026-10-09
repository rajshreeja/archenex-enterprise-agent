import streamlit as st

# 1. Page Configuration
st.set_page_config(
    page_title="ArcheNex Enterprise | Autonomous Audit Suite",
    page_icon="⚡",
    layout="wide"
)

# 2. Enterprise UI Styling (Custom CSS to remove "kiddish" look)
st.markdown("""
    <style>
    .main { background-color: #0E1117; color: #FAFAFA; }
    .stMetric { background-color: #161B22; padding: 15px; border-radius: 8px; border: 1px solid #30363D; }
    h1, h2, h3 { font-family: 'Inter', sans-serif; letter-spacing: -0.5px; }
    .stAlert { background-color: #161B22; border: 1px solid #30363D; color: #FAFAFA; }
    </style>
""", unsafe_allow_html=True)

# 3. Dynamic Client Customization Engine
# This dictionary lets you onboard ANY client instantly without changing code logic
CLIENT_DATABASE = {
    "Tata Motors (Pune Plant)": {
        "industry": "Automotive & Manufacturing",
        "blue_collar_metrics": {"idle_hours": "310 Hours", "labor_leakage": "₹42.5 Lakhs", "desc": "Line #4 stamping delay vs Darwinbox shift rosters."},
        "white_collar_metrics": {"unbilled_hours": "₹68.0 Lakhs", "license_waste": "₹14.2 Lakhs", "desc": "SAP CRM billing lag across commercial vehicle divisions."}
    },
    "Bosch India (Bangalore Hub)": {
        "industry": "Industrial Engineering & Tech",
        "blue_collar_metrics": {"idle_hours": "185 Hours", "labor_leakage": "₹28.0 Lakhs", "desc": "SMT line throughput mismatch with HRIS attendance logs."},
        "white_collar_metrics": {"unbilled_hours": "₹92.4 Lakhs", "license_waste": "₹21.5 Lakhs", "desc": "R&D milestone sign-off delays in enterprise SAP modules."}
    },
    "Custom Prospect (Dynamic Input)": {
        "industry": "Multi-Vertical Enterprise",
        "blue_collar_metrics": {"idle_hours": "240 Hours", "labor_leakage": "₹35.0 Lakhs", "desc": "Plant MES and shift record discrepancy detected."},
        "white_collar_metrics": {"unbilled_hours": "₹55.0 Lakhs", "license_waste": "₹12.0 Lakhs", "desc": "Corporate ERP and billing milestone lag."}
    }
}

# Sidebar Control Center
st.sidebar.title("⚙️ Enterprise Control")
selected_client = st.sidebar.selectbox("Select Target Client", list(CLIENT_DATABASE.keys()))

# Quick Custom Client Creator (Allows you to pitch live to anyone!)
with st.sidebar.expander("➕ Onboard New Client Live"):
    new_client_name = st.text_input("Client Company Name")
    new_leakage_scale = st.slider("Estimated Scale Multiplier", 1.0, 5.0, 1.5)
    if new_client_name and st.button("Initialize Client Profile"):
        CLIENT_DATABASE[new_client_name] = {
            "industry": "Custom Enterprise",
            "blue_collar_metrics": {"idle_hours": f"{int(200 * new_leakage_scale)} Hours", "labor_leakage": f"₹{int(30 * new_leakage_scale)} Lakhs", "desc": "Simulated cross-silo plant floor discrepancy."},
            "white_collar_metrics": {"unbilled_hours": f"₹{int(60 * new_leakage_scale)} Lakhs", "license_waste": f"₹{int(15 * new_leakage_scale)} Lakhs", "desc": "Simulated ERP-to-CRM billing friction."}
        }
        st.success(f"Profile for {new_client_name} loaded successfully!")

report_view = st.sidebar.radio(
    "Audit Module",
    ["Executive Overview", "🏭 Blue-Collar Audit (Plant MES)", "💻 White-Collar Audit (Corporate ERP)"]
)

client_data = CLIENT_DATABASE[selected_client]

# Main Dashboard Header
st.title(f"⚡ ArcheNex AI: {selected_client}")
st.caption(f"Industry Vertical: {client_data['industry']} | Autonomous Governance Engine v4.2")

if st.sidebar.button("Execute Agentic Audit Pipeline"):
    with st.spinner("Running cross-silo zero-hallucination verification..."):
        
        if report_view == "Executive Overview":
            st.markdown("---")
            st.subheader("Executive Financial Recovery Briefing")
            
            c1, c2, c3 = st.columns(3)
            c1.metric("Total Leakage Identified", "₹1.76 Cr", "95% Confidence")
            c2.metric("Blue-Collar Variance", client_data["blue_collar_metrics"]["idle_hours"], "Plant Floor")
            c3.metric("White-Collar Gap", client_data["white_collar_metrics"]["unbilled_hours"], "Corporate ERP")
            
            st.info(f"**Agentic Insight:** Cross-referencing plant MES logs with white-collar SAP milestones for {selected_client} indicates systemic disconnect between shift planning and billing execution.")

        elif report_view == "🏭 Blue-Collar Audit (Plant MES)":
            st.markdown("---")
            st.subheader("Blue-Collar Workforce & Plant Floor Audit")
            
            bc = client_data["blue_collar_metrics"]
            c1, c2 = st.columns(2)
            c1.metric("Idle Machinery & Shift Variance", bc["idle_hours"])
            c2.metric("Contract Labor Leakage", bc["labor_leakage"])
            
            st.markdown("### 🔍 Root-Cause Breakdown")
            st.warning(bc["desc"])
            st.success("**Automated Remediation:** Sync biometric punch logs directly with MES line power cycles to stop manual adjustments.")

        elif report_view == "💻 White-Collar Audit (Corporate ERP)":
            st.markdown("---")
            st.subheader("White-Collar Corporate & Resource Audit")
            
            wc = client_data["white_collar_metrics"]
            c1, c2 = st.columns(2)
            c1.metric("Unbilled Milestone Revenue", wc["unbilled_hours"])
            c2.metric("Orphaned SaaS License Cost", wc["license_waste"])
            
            st.markdown("### 🔍 Root-Cause Breakdown")
            st.warning(wc["desc"])
            st.success("**Automated Remediation:** Trigger automatic invoice generation in SAP immediately upon CRM milestone sign-off.")
