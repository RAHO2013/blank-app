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

    # Order Comparison Page
    if page == "Order Comparison":
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

    # Order Creation Page
    elif page == "Order Creation":
        st.title("Order Creation Dashboard")

        # Ensure the necessary columns exist
        if 'State' in master_sheet.columns and 'Program' in master_sheet.columns:
            unique_states = master_sheet['State'].unique()
            unique_programs = master_sheet['Program'].unique()

            # State Ranking
            st.subheader("Rank States")
            state_ranking = {}
            for state in unique_states:
                rank = st.number_input(f"Rank for {state}", min_value=1, step=1, key=f"state_{state}")
                state_ranking[state] = rank

            # Program Ranking
            st.subheader("Rank Programs")
            program_ranking = {}
            for program in unique_programs:
                rank = st.number_input(f"Rank for {program}", min_value=1, step=1, key=f"program_{program}")
                program_ranking[program] = rank

            # Generate Ordered Data
            if st.button("Generate Ordered Data"):
                # Sort master sheet by rankings
                master_sheet['State Rank'] = master_sheet['State'].map(state_ranking)
                master_sheet['Program Rank'] = master_sheet['Program'].map(program_ranking)

                ordered_data = master_sheet.sort_values(by=['State Rank', 'Program Rank']).reset_index(drop=True)

                st.subheader("Ordered Data")
                st.write(ordered_data[['State', 'Program', 'State Rank', 'Program Rank']])

                # Save to file
                if st.button("Save Ordered Data"):
                    ordered_data.to_excel("Ordered_Program_State.xlsx", index=False)
                    st.success("Ordered data saved as 'Ordered_Program_State.xlsx'.")
        else:
            st.error("Required columns 'State' and 'Program' are missing in the master sheet!")

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
