import streamlit as st
import pandas as pd
import os

st.title("Master Data Overview")

MASTER_FILE = "data/MASTER EXCEL.xlsx"

@st.cache_data
def load_master_file():
    if os.path.exists(MASTER_FILE):
        data = pd.read_excel(MASTER_FILE, sheet_name='Sheet1')
        return data
    else:
        st.error("Master file not found.")
        return None

master_sheet = load_master_file()

if master_sheet is not None:
    numeric_columns = master_sheet.select_dtypes(include=['int64', 'float64']).columns
    st.write("### Master Sheet (Formatted)")
    st.dataframe(master_sheet.style.format({col: "{:.0f}" for col in numeric_columns}))
