import streamlit as st
from agent_model import archenex_master_agent

st.set_page_config(
    page_title="ArcheNex Enterprise AI",
    page_icon="⚡",
    layout="wide"
)

st.title("⚡ ArcheNex Enterprise AI")
st.subheader("Autonomous Cross-Silo White-Space & Financial Leakage Engine")

# Sidebar for client selection
client_name = st.sidebar.selectbox(
    "Select Target Enterprise",
    ["Tata Motors (Pune Plant - Commercial Vehicles)", "Bosch India (Bangalore Hub)", "Mahindra & Mahindra"]
)

if st.sidebar.button("Execute Autonomous Agentic Audit"):
    with st.spinner("Executing multi-agent cross-silo analysis..."):
        result = archenex_master_agent(client_name)
        
        st.write("### Audit Status:", result.get("status"))
        st.write("### Calculated Financial Leakage: ₹{:,.2f}".format(result.get("financial_leakage", 0.0)))
        st.write("### Sample Size Verified:", result.get("sample_size", 0))
        st.success(result.get("connector_source", "Analysis complete."))
