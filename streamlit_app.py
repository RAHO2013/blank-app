import streamlit as st
import pandas as pd
import os

st.title("ETERNALS")

# Constants
MASTER_FILE = "MASTER EXCEL.xlsx"

@st.cache_data
def load_master_file():
    """Load the master Excel file and normalize columns."""
    if os.path.exists(MASTER_FILE):
        data = pd.read_excel(MASTER_FILE, sheet_name='Sheet1')
        data['State'] = data['State'].str.strip().str.upper()
        data['Program'] = data['Program'].str.strip().str.upper()
        data['TYPE'] = data['TYPE'].astype(str).str.strip().str.upper()
        if {'MCC College Code', 'COURSE CODE'}.issubset(data.columns):
            data['MAIN CODE'] = data['MCC College Code'].astype(str) + "_" + data['COURSE CODE'].astype(str)
        return data
    else:
        return None

# Load the master file and cache the result
master_sheet = load_master_file()

if master_sheet is None:
    st.error(f"Master file '{MASTER_FILE}' is missing in the project folder!")
else:
    # Detect numeric columns
    numeric_columns = master_sheet.select_dtypes(include=['int64', 'float64']).columns

    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Select a page:", ["Master Data", "Order Creation", "Order Creation with Excel", "Order Comparison", "Fee Checking"])

    # Master Data Page
    if page == "Master Data":
        st.title("Master Data Overview")

        # Display numeric columns without commas
        st.write("### Numeric Columns Formatted Correctly")
        st.dataframe(master_sheet.style.format({col: "{:.0f}" for col in numeric_columns}))

        # Display full data
        st.write("### Full Master Sheet")
        st.dataframe(master_sheet)

    # Order Creation with Excel
    elif page == "Order Creation with Excel":
        st.title("Order Creation with Excel")

        uploaded_file = st.file_uploader("Upload Excel File (with Two Sheets)", type=["xlsx"])
        if uploaded_file:
            try:
                # Load both sheets
                state_data = pd.read_excel(uploaded_file, sheet_name='StateRanks')
                program_data = pd.read_excel(uploaded_file, sheet_name='ProgramRanks')

                # Validate State Sheet
                if not {'State', 'State Rank'}.issubset(state_data.columns):
                    st.error("State sheet must contain 'State' and 'State Rank' columns.")
                else:
                    st.success("State data loaded successfully!")

                # Validate Program Sheet
                if not {'Program', 'Program Type', 'Program Rank'}.issubset(program_data.columns):
                    st.error("Program sheet must contain 'Program', 'Program Type', and 'Program Rank' columns.")
                else:
                    st.success("Program data loaded successfully!")

                # Map state and program ranks
                if 'State Rank' not in st.session_state:
                    st.session_state['State Rank'] = master_sheet['State'].map(state_data.set_index('State')['State Rank']).fillna(0)
                master_sheet['State Rank'] = st.session_state['State Rank']

                if 'Program Rank' not in st.session_state:
                    st.session_state['Program Rank'] = master_sheet.apply(
                        lambda x: program_data.loc[
                            (program_data['Program'].str.upper() == x['Program'].upper()) &
                            (program_data['Program Type'].str.upper() == x['TYPE'].upper()),
                            'Program Rank'
                        ].values[0] if ((program_data['Program'].str.upper() == x['Program'].upper()) &
                                        (program_data['Program Type'].str.upper() == x['TYPE'].upper())).any() else 0,
                        axis=1
                    )
                master_sheet['Program Rank'] = st.session_state['Program Rank']

                # Generate ordered table
                ordered_data = master_sheet.query("`State Rank` > 0 and `Program Rank` > 0").sort_values(
                    by=['Program Rank', 'State Rank']
                ).reset_index(drop=True)
                ordered_data['Order Number'] = range(1, len(ordered_data) + 1)

                # Collapsible section to select columns to display
                with st.expander("Select Columns to Display", expanded=True):
                    st.write("### Choose the columns you want to include in the ordered table:")
                    default_columns = ['MAIN CODE', 'Program', 'TYPE', 'State', 'College Name', 'Program Rank', 'State Rank', 'Order Number']
                    selected_columns = st.multiselect(
                        "Select columns:",
                        list(master_sheet.columns) + ['State Rank', 'Program Rank', 'Order Number'],  # Include derived columns
                        default=default_columns
                    )

                # Display ordered table with selected columns
                if st.button("Generate Ordered Table"):
                    if selected_columns:
                        st.write("### Ordered Table from Uploaded Excel")
                        # Format numeric columns in the ordered table
                        st.dataframe(ordered_data[selected_columns].style.format({col: "{:.0f}" for col in numeric_columns}))
                    else:
                        st.warning("Please select at least one column to display the table.")
            except Exception as e:
                st.error(f"An error occurred while processing the uploaded file: {e}")
        else:
            st.info("Please upload an Excel file with two sheets: 'StateRanks' and 'ProgramRanks'.")

    # Other Pages
    elif page == "Order Creation":
        st.title("Order Creation Dashboard")
        st.info("Manual Order Creation functionality is currently under optimization.")

    elif page == "Order Comparison":
        st.title("Order Comparison Dashboard")
        st.info("Order Comparison functionality is currently under optimization.")

    elif page == "Fee Checking":
        st.title("Fee Checking Dashboard")
        st.info("Fee Checking functionality is currently under optimization.")
