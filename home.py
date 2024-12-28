import streamlit as st

def display_home():
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
