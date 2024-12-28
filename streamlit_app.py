import streamlit as st

st.set_page_config(page_title="ETERNALS", layout="wide")
st.title("Welcome to ETERNALS")

st.sidebar.title("Navigation")
st.sidebar.radio("Select a page:", [
    "Master Data",
    "Order Creation",
    "Order Creation with Excel",
    "Order Comparison",
    "Fee Checking"
])

st.markdown("""
## Home Page
Welcome to **ETERNALS**!
Use the sidebar to navigate to different sections.
""")
