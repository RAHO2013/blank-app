import streamlit as st
import pandas as pd

st.title("Order Creation (Manual)")

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
    unique_states = master_sheet['State'].unique()

    st.subheader("Rank States")
    state_ranking = {}
    for state in unique_states:
        rank = st.selectbox(
            f"Select rank for {state}",
            options=[0] + [i for i in range(1, len(unique_states) + 1)],
            key=f"state_{state}",
        )
        if rank > 0:
            state_ranking[state] = int(rank)
    st.write("### State Rankings")
    st.write(state_ranking)
