import streamlit as st
from agent_model import archenex_master_agent

st.set_page_config(page_title="ArcheNex Enterprise | Agentic Intelligence Suite", layout="wide")

st.title("⚡ ArcheNex Enterprise AI")
st.subheader("Autonomous Cross-Silo White-Space & Financial Leakage Engine")
st.write("Bridging HRIS (Darwinbox/Keka), SAP ERP, and Plant MES with zero-hallucination agentic governance.")

st.sidebar.header("Target Enterprise Client")
client_choice = st.sidebar.selectbox(
    "Select Target Enterprise", 
    [
        "Tata Motors (Pune Plant - Commercial Vehicles)", 
        "Bharat Forge (Chakan Manufacturing)", 
        "Schneider Electric (Grenoble / Global Operations - EU)", 
        "Bosch India (Bangalore & Nashik Powertrain)"
    ]
)

silo_choice = st.sidebar.selectbox(
    "Select Cross-Departmental Silo", 
    [
        "Plant Floor Operations (MES Roster vs. HRIS Onboarding)", 
        "Corporate Strategy & Workforce Analytics (Low Sample Test)"
    ]
)

if st.sidebar.button("Execute Autonomous Agentic Audit"):
    with st.spinner("Agent planning strategy, executing secure tool calls, and running reflective compliance guardrails..."):
        initial_state = {
            "client_name": client_choice,
            "target_sector": "Automotive & Industrial Manufacturing",
            "active_silo": silo_choice,
            "agent_memory": [],
            "tool_execution_log": [],
            "raw_enterprise_data": {},
            "reasoning_verdict": "",
            "calculated_leakage": 0.0,
            "tailored_playbook": []
        }
        result = archenex_master_agent.invoke(initial_state)

    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="Audit Status", value=result["reasoning_verdict"].replace("_", " ").upper())
    with col2:
        st.metric(label="Calculated Financial Leakage", value=f"₹{result['calculated_leakage']:,.2f}")
    with col3:
        st.metric(label="Tools Executed", value=str(len(result["tool_execution_log"])))

    st.markdown("### 🧠 Autonomous Agent Execution & Reasoning Trace")
    for memory in result["agent_memory"]:
        if "🛡️" in memory:
            st.warning(memory)
        elif "✔" in memory:
            st.success(memory)
        else:
            st.info(memory)

    if result["reasoning_verdict"] == "approved_for_recovery":
        st.markdown("### 📈 Agent-Generated 6-Week Trial Playbook")
        for action in result["tailored_playbook"]:
            st.write(f"- {action}")
    else:
        st.error("🛡️️ Compliance Guardrail Enforced: Agent blocked automated leakage reporting due to insufficient sample confidence.")
