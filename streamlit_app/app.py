import streamlit as st

# Define navigation logic
def navigate():
    st.sidebar.title("Navigation")
    page = st.sidebar.radio(
        "Select a page:",
        ["Home", "Master Data", "Order Creation", "Order Creation with Excel", "Order Comparison", "Fee Checking"]
    )
    return page

# Run the selected page
def run_page(page):
    if page == "Home":
        from pages.home import display_home
        display_home()
    elif page == "Master Data":
        from pages.master_data import display_master_data
        display_master_data()
    elif page == "Order Creation":
        from pages.order_creation import display_order_creation
        display_order_creation()
    elif page == "Order Creation with Excel":
        from pages.excel_ranking import display_excel_ranking
        display_excel_ranking()
    elif page == "Order Comparison":
        from pages.comparison import display_comparison
        display_comparison()
    elif page == "Fee Checking":
        from pages.fee_checking import display_fee_checking
        display_fee_checking()

# Main app logic
def main():
    st.set_page_config(page_title="ETERNALS", layout="wide")
    page = navigate()
    run_page(page)

if __name__ == "__main__":
    main()
