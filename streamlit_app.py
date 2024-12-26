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

            # Tabs for State Ranking, Program Ranking, and Final Table
            tab1, tab2, tab3 = st.tabs(["Rank States", "Rank Programs", "Final Ordered Table"])

            # State Ranking
            with tab1:
                st.subheader("Rank States")
                state_ranking = {}
                for state in unique_states:
                    rank = st.number_input(f"Rank for {state}", min_value=0, step=1, key=f"state_{state}")
                    state_ranking[state] = rank

            # Program Ranking
            with tab2:
                st.subheader("Rank Programs")
                program_ranking = {}
                for program in unique_programs:
                    rank = st.number_input(f"Rank for {program}", min_value=0, step=1, key=f"program_{program}")
                    program_ranking[program] = rank

            # Final Ordered Table
            with tab3:
                # Generate Ordered Data
                if st.button("Generate Ordered Data", key="generate_table"):
                    # Map rankings to master sheet
                    master_sheet['State Rank'] = master_sheet['State'].map(state_ranking).fillna(0)
                    master_sheet['Program Rank'] = master_sheet['Program'].map(program_ranking).fillna(0)

                    # Filter out zero-ranked states and programs
                    filtered_data = master_sheet[
                        (master_sheet['State Rank'] > 0) & (master_sheet['Program Rank'] > 0)
                    ]

                    # Sort by selected order (state or program)
                    order_option = st.radio("Select Order Type", options=["State-wise Order", "Program-wise Order"])
                    if order_option == "State-wise Order":
                        ordered_data = filtered_data.sort_values(by=['State Rank', 'Program Rank']).reset_index(drop=True)
                    else:
                        ordered_data = filtered_data.sort_values(by=['Program Rank', 'State Rank']).reset_index(drop=True)

                    # Display Ordered Table
                    st.subheader("Ordered Data")
                    st.write(ordered_data[['State', 'Program', 'State Rank', 'Program Rank']])

                    # Save to file
                    if st.button("Save Ordered Data"):
                        filename = "Ordered_State_Program.xlsx" if order_option == "State-wise Order" else "Ordered_Program_State.xlsx"
                        ordered_data.to_excel(filename, index=False)
                        st.success(f"Ordered data saved as '{filename}'.")
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
