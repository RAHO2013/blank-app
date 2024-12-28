import streamlit as st

st.set_page_config(page_title="ETERNALS", layout="wide")
st.title("Welcome to ETERNALS")

# Initialize session state for navigation
if 'page' not in st.session_state:
    st.session_state.page = 'Home'

# Sidebar for navigation
with st.sidebar:
    st.title("Navigation")
    st.radio(
        "Select a page:",
        ['Home', 'Master Data', 'Order Creation', 'Order Creation with Excel', 'Order Comparison', 'Fee Checking'],
        key='page'
    )

# Main content based on page selection
if st.session_state.page == 'Home':
    st.markdown("""
    ## Home Page
    Welcome to **ETERNALS**! Use the sidebar to navigate to different sections.
    """)

elif st.session_state.page == 'Master Data':
    from pages.master_data import display_master_data
    display_master_data()

elif st.session_state.page == 'Order Creation':
    from pages.order_creation import display_order_creation
    display_order_creation()

elif st.session_state.page == 'Order Creation with Excel':
    from pages.excel_ranking import display_excel_ranking
    display_excel_ranking()

elif st.session_state.page == 'Order Comparison':
    from pages.comparison import display_comparison
    display_comparison()

elif st.session_state.page == 'Fee Checking':
    from pages.fee_checking import display_fee_checking
    display_fee_checking()
