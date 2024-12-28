import streamlit as st

st.set_page_config(page_title="ETERNALS", layout="wide")
st.title("Welcome to ETERNALS")

# Remove sidebar navigation
st.sidebar.title("ETERNALS Navigation")
st.sidebar.info("Use the links on the home page to navigate.")

st.markdown("""
## Home Page
Welcome to **ETERNALS**! Please use the navigation menu below to select a section.

### Sections:
- [Master Data](Master%20Data)
- [Order Creation](Order%20Creation)
- [Order Creation with Excel](Order%20Creation%20with%20Excel)
- [Order Comparison](Order%20Comparison)
- [Fee Checking](Fee%20Checking)
""")
