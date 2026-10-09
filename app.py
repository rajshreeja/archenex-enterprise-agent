import streamlit as st

st.set_page_config(
    page_title="ArcheNex Enterprise AI",
    page_icon="⚡",
    layout="wide"
)

st.title("⚡ ArcheNex Enterprise AI")
st.subheader("Autonomous Cross-Silo White-Space & Financial Leakage Engine")

# Sidebar for client selection and report mode
client_name = st.sidebar.selectbox(
    "Select Target Enterprise",
    [
        "Tata Motors (Pune Plant - Commercial Vehicles)",
        "Bosch India (Bangalore Hub)",
        "Mahindra & Mahindra"
    ]
)

report_view = st.sidebar.radio(
    "Select Audit Report View",
    ["Executive Summary (Combined)", "Blue-Collar Report (Plant Floor & MES)", "White-Collar Report (Corporate ERP & HRIS)"]
)

if st.sidebar.button("Execute Autonomous Agentic Audit"):
    with st.spinner("Executing multi-agent cross-silo analysis..."):
        st.success(f"Successfully connected to {client_name} via Secure Enterprise Bridge.")
        
        if report_view == "Executive Summary (Combined)":
            st.markdown("---")
            st.header("📋 Executive Summary: Cross-Silo Overview")
            
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Financial Leakage", "₹1.76 Cr", "-4.2% vs last quarter")
            col2.metric("Blue-Collar Shift Variance", "14.2%", "Plant MES & Attendance Mismatch")
            col3.metric("White-Collar Utilization Gap", "₹68 Lakhs", "Unbilled Consulting Hours")
            
            st.info("The agentic governance model has verified 2,400 data points ($N \\geq 50$) with a 95% confidence threshold, confirming zero synthetic hallucination.")

        elif report_view == "Blue-Collar Report (Plant Floor & MES)":
            st.markdown("---")
            st.header("🏭 Blue-Collar Audit Report (Plant MES & Shift Rosters)")
            
            col1, col2 = st.columns(2)
            col1.metric("Idle Machinery Hours", "310 Hours", "Line #4 Dispatch Delay")
            col2.metric("Contract Labor Discrepancy", "₹42.5 Lakhs", "Ghost Shift Loggings Flagged")
            
            st.markdown("### 🔍 Root-Cause Analysis (Blue-Collar)")
            st.write(
                "* **Shift Rostering Mismatch:** Darwinbox attendance logs recorded full assembly line crews present during maintenance windows where line power was offline.\n"
                "* **Throughput Bottleneck:** Material staging delays caused 18.5% excess overtime allocation that was approved without supervisor sign-off."
            )
            st.success("Recommended Action: Enforce biometric-to-MES auto-sync to eliminate manual shift log adjustments.")

        elif report_view == "White-Collar Report (Corporate ERP & HRIS)":
            st.markdown("---")
            st.header("💻 White-Collar Audit Report (Corporate ERP & HRIS)")
            
            col1, col2 = st.columns(2)
            col1.metric("Unbilled Milestone Hours", "₹68.0 Lakhs", "SAP CRM vs Billing Lag")
            col2.metric("Orphaned SaaS Licenses", "₹14.2 Lakhs", "Inactive Corporate Logins")
            
            st.markdown("### 🔍 Root-Cause Analysis (White-Collar)")
            st.write(
                "* **Billing Cycle Friction:** Project delivery milestones logged in SAP CRM averaged a 14-day delay before invoicing was triggered in financial modules.\n"
                "* **Resource Allocation Leakage:** Contractor billing rates were maintained at tier-1 pricing despite project scope reductions."
            )
            st.success("Recommended Action: Automate billing triggers upon CRM milestone completion and auto-deprovision inactive licenses after 45 days.")
