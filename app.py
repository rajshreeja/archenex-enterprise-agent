
import streamlit as st
import pandas as pd

# Import directly from the root folder
import agent as ag
import auth
import charts
import insights as ins
import mapping as mp
import pipeline
import detectors

st.set_page_config(
    page_title="ArcheNex Enterprise Agent",
    page_icon="🛡️",
    layout="wide"
)

def main():
    st.title("ArcheNex Enterprise Agent")
    st.success("App loaded successfully from root files!")

if __name__ == "__main__":
    main()
