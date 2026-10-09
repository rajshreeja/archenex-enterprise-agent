
import streamlit as st
import pandas as pd
import pipeline
import detectors
import charts
import insights as ins
import mapping as mp

st.set_page_config(
    page_title="ArcheNex Enterprise Agent",
    page_icon="🛡️",
    layout="wide"
)

def main():
    st.sidebar.title("🛡️ ArcheNex Navigation")
    choice = st.sidebar.radio("Go to", ["Audit Dashboard", "Pipeline Inspector", "System Configuration"])

    st.title("🛡️ ArcheNex Enterprise Agent")
    st.markdown("### Autonomous AI Audit & Compliance System")

    if choice == "Audit Dashboard":
        st.info("Upload your dataset or logs to begin automated audit analysis.")
        
        uploaded_file = st.file_uploader("Upload Audit Data (CSV/Excel)", type=["csv", "xlsx"])
        
        if uploaded_file is not None:
            try:
                df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file)
                st.write("### Preview of Uploaded Data", df.head())
                
                if st.button("Run Audit Pipeline", type="primary"):
                    with st.spinner("Running AI audit detectors..."):
                        processed_df = pipeline.run_pipeline(df)
                        st.success("Audit completed successfully!")
                        st.dataframe(processed_df)
            except Exception as e:
                st.error(f"Error processing file: {e}")
        else:
            st.warning("Please upload a file via the uploader above to start auditing.")

    elif choice == "Pipeline Inspector":
        st.subheader("Pipeline Configuration & Rules")
        st.json({
            "Active Detectors": ["Anomaly Detection", "Compliance Check", "Format Validation"],
            "Status": "Operational",
            "Environment": "Streamlit Cloud"
        })

    else:
        st.subheader("System Settings")
        st.write("Manage enterprise connections and access tokens here.")

if __name__ == "__main__":
    main()
