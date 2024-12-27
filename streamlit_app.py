import streamlit as st
import pandas as pd
import os

# Constants
MASTER_FILE = "MASTER EXCEL.xlsx"

# Load MASTER EXCEL file
if not os.path.exists(MASTER_FILE):
    st.error(f"Master file '{MASTER_FILE}' is missing in the project folder!")
else:
    master_sheet = pd.read_excel(MASTER_FILE, sheet_name='Sheet1')

    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Select a page:", ["Order Comparison", "Order Creation", "Fee Checking"])

    # Order Creation Page
    if page == "Order Creation":
        st.title("Order Creation Dashboard")

        # Ensure the necessary columns exist
        if 'State' in master_sheet.columns and 'Program' in master_sheet.columns:
            unique_states = master_sheet['State'].unique()
            unique_programs = master_sheet['Program'].unique()

            # Tabs for State-wise Order and Program-wise Order
            tab1, tab2 = st.tabs(["State-wise Order", "Program-wise Order"])

            # State-wise Order
            with tab1:
                st.subheader("Rank States")
                state_ranking = {}
                for state in unique_states:
                    rank = st.number_input(f"Rank for {state}", min_value=0, step=1, key=f"state_{state}")
                    state_ranking[state] = rank

                if st.button("Generate State-wise Order", key="state_order"):
                    # Map rankings and filter out zero-ranked states
                    master_sheet['State Rank'] = master_sheet['State'].map(state_ranking).fillna(0)
                    filtered_data = master_sheet[master_sheet['State Rank'] > 0]

                    # Sort by State Rank
                    ordered_state_data = filtered_data.sort_values(by=['State Rank', 'Program']).reset_index(drop=True)

                    st.subheader("State-wise Ordered Data")
                    st.write(ordered_state_data[['State', 'Program', 'State Rank']])

                    # Save to file
                    if st.button("Save State-wise Order"):
                        ordered_state_data.to_excel("State_Wise_Order.xlsx", index=False)
                        st.success("State-wise order saved as 'State_Wise_Order.xlsx'.")

            # Program-wise Order
            with tab2:
                st.subheader("Rank Programs")
                program_ranking = {}
                for program in unique_programs:
                    rank = st.number_input(f"Rank for {program}", min_value=0, step=1, key=f"program_{program}")
                    program_ranking[program] = rank

                if st.button("Generate Program-wise Order", key="program_order"):
                    # Map rankings and filter out zero-ranked programs
                    master_sheet['Program Rank'] = master_sheet['Program'].map(program_ranking).fillna(0)
                    filtered_data = master_sheet[master_sheet['Program Rank'] > 0]

                    # Sort by Program Rank
                    ordered_program_data = filtered_data.sort_values(by=['Program Rank', 'State']).reset_index(drop=True)

                    st.subheader("Program-wise Ordered Data")
                    st.write(ordered_program_data[['State', 'Program', 'Program Rank']])

                    # Save to file
                    if st.button("Save Program-wise Order"):
                        ordered_program_data.to_excel("Program_Wise_Order.xlsx", index=False)
                        st.success("Program-wise order saved as 'Program_Wise_Order.xlsx'.")

        else:
            st.error("Required columns 'State' and 'Program' are missing in the master sheet!")

    # Order Comparison Page
    elif page == "Order Comparison":
        st.title("Order Comparison Dashboard")

        # Upload Comparison File
        uploaded_file = st.file_uploader("Upload Comparison File (Excel)", type=["xlsx"])
        if uploaded_file is not None:
            comparison_sheet = pd.read_excel(uploaded_file, sheet_name='Sheet1')

            # Create MAIN CODE for Comparison
            if 'Institute Name' in comparison_sheet.columns and 'Program Name' in comparison_sheet.columns:
                comparison_sheet['MAIN CODE'] = comparison_sheet['Institute Name'].astype(str) + "_" + comparison_sheet['Program Name'].astype(str)
                st.success("MAIN CODE created for Comparison file.")

            # Compare MAIN CODEs between Master and Comparison Sheets
            st.header("MAIN CODE-Based Comparison")
            master_sheet['MAIN CODE'] = master_sheet['MCC College Code'].astype(str) + "_" + master_sheet['COURSE CODE'].astype(str)

            master_codes = set(master_sheet['MAIN CODE'])
            comparison_codes = set(comparison_sheet['MAIN CODE'])

            missing_in_comparison = master_codes - comparison_codes
            missing_in_master = comparison_codes - master_codes

            # Display Results
            st.subheader("MAIN CODE Missing in Comparison File")
            if missing_in_comparison:
                st.write(pd.DataFrame(list(missing_in_comparison), columns=['MAIN CODE']))
            else:
                st.write("No MAIN CODEs missing in Comparison File.")

            st.subheader("MAIN CODE Missing in Master File")
            if missing_in_master:
                st.write(pd.DataFrame(list(missing_in_master), columns=['MAIN CODE']))
            else:
                st.write("No MAIN CODEs missing in Master File.")
        else:
            st.info("Please upload a comparison file to proceed.")

    # Fee Checking Page
    elif page == "Fee Checking":
        st.title("Fee Checking Dashboard")

        st.header("Fee Comparison")
        fee_column = "Fees"  # Assuming 'Fees' is the column for fee data
        if fee_column in master_sheet.columns:
            fee_comparison = master_sheet.groupby("Program")[fee_column].mean()
            st.bar_chart(fee_comparison)
        else:
            st.warning(f"Fee column '{fee_column}' not found in the master sheet!")
