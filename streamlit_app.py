import streamlit as st

st.set_page_config(page_title="ETERNALS", layout="wide")
st.title("Welcome to ETERNALS")

st.sidebar.title("Navigation")
st.sidebar.markdown("""
- [Master Data](Master%20Data)
- [Order Creation](Order%20Creation)
- [Order Creation with Excel](Order%20Creation%20with%20Excel)
- [Order Comparison](Order%20Comparison)
- [Fee Checking](Fee%20Checking)
""")

st.markdown("""
## Home Page
Welcome to **ETERNALS**! Please use the navigation menu to select a section.
""")
