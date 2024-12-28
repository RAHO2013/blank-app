import streamlit as st

# Define each page as a function
def home():
    st.title("Welcome to ETERNALS")
    st.markdown("""
    ## Home Page
    Welcome to **ETERNALS**! Use the sidebar to navigate to different sections.
    """)

def master_data():
    st.title("Master Data Overview")
    # Load and display master data
    MASTER_FILE = "data/MASTER EXCEL.xlsx"
    if st.file_exists(MASTER_FILE):
        master_sheet = pd.read_excel(MASTER_FILE, sheet_name='Sheet1')
        st.dataframe(master_sheet)
    else:
        st.error("Master file not found.")

def order_creation():
    st.title("Order Creation (Manual)")
    st.write("Manual ranking functionality coming soon.")

def excel_ranking():
    st.title("Order Creation with Excel")
    st.write("Upload Excel-based rankings functionality coming soon.")

def order_comparison():
    st.title("Order Comparison")
    st.write("Comparison functionality coming soon.")

def fee_checking():
    st.title("Fee Checking")
    st.write("Fee checking functionality coming soon.")

# Sidebar Navigation with Expanders
def main():
    with st.sidebar:
        st.title("Navigation")
        with st.expander("📊 Data Management", expanded=True):
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
