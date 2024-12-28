import streamlit as st
import pandas as pd
import os

# Define each page as a function
def home():
    """Home Page Content"""
    st.title("Welcome to ETERNALS")
    st.markdown("""
    ## Home Page
    Welcome to **ETERNALS**! 🎉

    This application provides a suite of tools for managing data, creating orders, and performing comparisons.

    ### Features:
    - **📊 Master Data**: View and manage your master dataset.
    - **⚙️ Order Creation**: Create orders manually or using uploaded Excel files.
    - **🔍 Comparison Tools**: Compare data using advanced features.
    - **💸 Fee Checking**: Analyze and validate fee structures.

    ### How to Navigate:
    Use the **Sidebar** on the left to:
    - Select different sections of the application.
    - Group related functionalities under expandable menus for clarity.

    ---
    **Start Exploring Now!**
    """)

def master_data():
    """Master Data Page"""
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

def order_creation():
    """Order Creation Page"""
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

def excel_ranking():
    """Order Creation with Excel Page"""
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

def order_comparison():
    """Order Comparison Page"""
    st.title("Order Comparison")
    st.write("Comparison functionality coming soon.")

def fee_checking():
    """Fee Checking Page"""
    st.title("Fee Checking")
    st.write("Fee checking functionality coming soon.")

# Sidebar Navigation with Expanders
def main():
    with st.sidebar:
        st.title("Navigation")
        with st.expander("🏠 Home", expanded=True):
            if st.button("Go to Home"):
                st.session_state.page = "home"

        with st.expander("📊 Data Management", expanded=False):
            if st.button("Master Data"):
                st.session_state.page = "master_data"
            if st.button("Order Creation"):
                st.session_state.page = "order_creation"

        with st.expander("⚙️ Rankings and Comparison", expanded=False):
            if st.button("Order Creation with Excel"):
                st.session_state.page = "excel_ranking"
            if st.button("Order Comparison"):
                st.session_state.page = "order_comparison"

        with st.expander("💸 Fee Management", expanded=False):
            if st.button("Fee Checking"):
                st.session_state.page = "fee_checking"

    # Page Routing
    if 'page' not in st.session_state:
        st.session_state.page = "home"

    if st.session_state.page == "home":
        home()
    elif st.session_state.page == "master_data":
        master_data()
    elif st.session_state.page == "order_creation":
        order_creation()
    elif st.session_state.page == "excel_ranking":
        excel_ranking()
    elif st.session_state.page == "order_comparison":
        order_comparison()
    elif st.session_state.page == "fee_checking":
        fee_checking()

# Run the app
if __name__ == "__main__":
    main()
