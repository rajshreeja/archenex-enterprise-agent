import os
import sys

# Ensure the root directory is on Python's path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

import streamlit as st
import pandas as pd

# Import all modules from the archenex package structure
from archenex import agent as ag
from archenex import auth
from archenex import charts
from archenex import insights as ins
from archenex import mapping as mp
from archenex import pipeline
from archenex import detectors

# --- Streamlit Application Entrypoint ---
st.set_page_config(
    page_title="ArcheNex Enterprise Agent",
    page_icon="🛡️",
    layout="wide"
)

# Main app invocation
def main():
    st.title("ArcheNex Enterprise Agent (v3)")
    st.sidebar.title("Navigation & Controls")
    
    # Basic health check / test render to verify imports
    if hasattr(ag, "run_pipeline") or hasattr(pipeline, "run"):
        st.success("ArcheNex core package loaded successfully!")
    else:
        st.info("ArcheNex modules loaded. Ready for execution.")

if __name__ == "__main__":
    main()
