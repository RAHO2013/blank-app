import streamlit as st
import pandas as pd

st.title("Order Creation with Excel")

uploaded_file = st.file_uploader("Upload Excel File", type=["xlsx"])
if uploaded_file:
    try:
        state_data = pd.read_excel(uploaded_file, sheet_name='StateRanks')
        program_data = pd.read_excel(uploaded_file, sheet_name='ProgramRanks')

        # Normalize uploaded data
        state_data['State'] = state_data['State'].str.strip().str.upper()
        program_data['Program'] = program_data['Program'].str.strip().str.upper()
        program_data['Program Type'] = program_data['Program Type'].str.strip().str.upper()

        st.write("### State Rankings")
        st.dataframe(state_data)
        st.write("### Program Rankings")
        st.dataframe(program_data)
    except Exception as e:
        st.error(f"Error processing file: {e}")
else:
    st.info("Please upload a valid Excel file.")
