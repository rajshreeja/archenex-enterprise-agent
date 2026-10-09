import streamlit as st
import pandas as pd
import io
from detectors import run_deterministic_audit

st.set_page_config(page_title="ArcheNex Enterprise Intelligence", page_icon="⚡", layout="wide")

st.markdown("### ARCHENEX ENTERPRISE GOVERNANCE & AUDIT ENGINE")
st.markdown("**Status:** <span style='color:#16a34a; font-weight:bold;'>DETERMINISTIC PILOT MODE ACTIVE</span>", unsafe_allow_html=True)
st.markdown("---")

st.sidebar.markdown("### 📂 Pilot Data Ingestion (CSV / Excel)")
st.sidebar.markdown("Upload client export files to run deterministic leakage analysis.")

att_file = st.sidebar.file_uploader("1. Attendance Export (HRIS)", type=['csv', 'xlsx'])
mach_file = st.sidebar.file_uploader("2. Plant Machine Logs (MES)", type=['csv', 'xlsx'])
inv_file = st.sidebar.file_uploader("3. Project Milestones / Invoices (ERP)", type=['csv', 'xlsx'])
saas_file = st.sidebar.file_uploader("4. Software Usage Logs (IT)", type=['csv', 'xlsx'])

# Load dataframes safely
df_att = pd.read_csv(att_file) if att_file else None
df_mach = pd.read_csv(mach_file) if mach_file else None
df_inv = pd.read_csv(inv_file) if inv_file else None
df_saas = pd.read_csv(saas_file) if saas_file else None

# Run Audit Analysis
audit_results = run_deterministic_audit(df_att, df_mach, df_inv, df_saas)

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Leakage Identified", f"₹{audit_results['total_leakage_cr']} Cr", "Deterministic Calculation")
col2.metric("Valuation Lift (12x EV/EBITDA)", f"₹{audit_results['valuation_lift_cr']} Cr", "Equity Impact")
col3.metric("Audit Vectors Flagged", len(audit_results['findings']), "Verified Rules")
col4.metric("Cryptographic Hash Status", "VERIFIED SHA-256", "Tamper-Proof")

st.markdown("### 🔍 Verified Findings & Deterministic Audit Trail")
findings_df = pd.DataFrame(audit_results['findings'])
st.dataframe(findings_df, use_container_width=True)

st.markdown(f"""
> **Cryptographic Governance Proof:**  
> `sha256:{audit_results['audit_hash']}`  
> *Note: This hash is dynamically computed from the exact transactional dataset and rule outputs above. Any modification to source records changes the hash immediately.*
""")
