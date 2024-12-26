import streamlit as st
import pandas as pd
import os

# Constants
MASTER_FILE = "MASTER EXCEL.xlsx"

# Load MASTER EXCEL file
if not os.path.exists(MASTER_FILE):
    st.error(f"Master file '{MASTER_FILE}' is missing in the project folder!")
else:
    # Load the data and normalize the "State" and "TYPE" columns
    master_sheet = pd.read_excel(MASTER_FILE, sheet_name='Sheet1')
    master_sheet['State'] = master_sheet['State'].str.strip().str.upper()  # Normalize state names to uppercase
    master_sheet['TYPE'] = master_sheet['TYPE'].astype(str).str.strip().str.upper()  # Normalize TYPE to uppercase strings

    # Get unique values for TYPE and States
    unique_types = sorted(master_sheet['TYPE'].unique())
    unique_states = sorted(master_sheet['State'].unique())

    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Select a page:", ["Order Comparison", "Order Creation", "Fee Checking"])

    # Order Creation Page
    if page == "Order Creation":
        st.title("Order Creation Dashboard")

        # Ensure necessary columns exist
        if {'State', 'Program', 'College Name', 'TYPE'}.issubset(master_sheet.columns):

            # Tabs for Ranking
            rank_tab, order_tab = st.tabs(["Rank States and Programs", "Order by Ranking"])

            with rank_tab:
                # Sub-tabs for Ranking States and Programs
                state_tab, program_tab = st.tabs(["Rank States", "Rank Programs by TYPE"])

                # Rank States Tab
                with state_tab:
                    st.subheader("Rank States")
                    state_ranking = {}
                    used_ranks = set()  # Track used ranks across all states

                    for state in unique_states:
                        cols = st.columns([3, 1])  # Adjusted for name and dropdown
                        with cols[0]:
                            st.text(state)
                        with cols[1]:
                            rank = st.selectbox(
                                f"Rank for {state}",
                                options=[0] + [i for i in range(1, len(unique_states) + 1) if i not in used_ranks],
                                key=f"state_{state}",
                            )
                            if rank > 0:
                                if rank in used_ranks:
                                    st.error(f"Duplicate rank detected for States: {rank}")
                                else:
                                    state_ranking[state] = rank
                                    used_ranks.add(rank)

                # Rank Programs by TYPE Tab
                with program_tab:
                    st.subheader("Rank Programs by TYPE")

                    # Type Selection Dropdown
                    selected_type = st.selectbox("Select Program TYPE to Rank:", options=unique_types)

                    if selected_type:
                        st.write(f"### Programs for {selected_type}")
                        filtered_programs = sorted(master_sheet[master_sheet['TYPE'] == selected_type]['Program'].unique())
                        type_program_ranking = {}
                        for program in filtered_programs:
                            cols = st.columns([3, 1])  # Adjusted for name and dropdown
                            with cols[0]:
                                st.text(program)
                            with cols[1]:
                                rank = st.selectbox(
                                    f"Rank for {program}",
                                    options=[0] + [i for i in range(1, len(master_sheet['Program'].unique()) + 1) if i not in used_ranks],
                                    key=f"program_{program}_{selected_type}",
                                )
                                if rank > 0:
                                    if rank in used_ranks:
                                        st.error(f"Duplicate rank detected globally: {rank}")
                                    else:
                                        type_program_ranking[program] = rank
                                        used_ranks.add(rank)

            # Generate Ordered Table by Rankings
            with order_tab:
                st.subheader("Generate Order by Rankings")

                if st.button("Generate Order Table"):
                    # Map rankings to master sheet
                    master_sheet['State Rank'] = master_sheet['State'].map(state_ranking).fillna(0)
                    master_sheet['Program Rank'] = master_sheet['Program'].map(type_program_ranking).fillna(0)

                    # Filter out zero-ranked states and programs
                    filtered_data = master_sheet[
                        (master_sheet['State Rank'] > 0) & 
                        (master_sheet['Program Rank'] > 0)
                    ]

                    # Sort by Program Rank and then State Rank
                    ordered_data = filtered_data.sort_values(
                        by=['Program Rank', 'State Rank']
                    ).reset_index(drop=True)

                    # Create Order Number
                    ordered_data['Order Number'] = range(1, len(ordered_data) + 1)

                    # Display Ordered Table with College Name
                    st.write("### Ordered Table")
                    st.write(ordered_data[['Program', 'State', 'College Name', 'TYPE', 'Program Rank', 'State Rank', 'Order Number']])

                    # Save to file
                    if st.button("Save Ordered Table"):
                        ordered_data.to_excel("Ordered_Program_State.xlsx", index=False)
                        st.success("Ordered table saved as 'Ordered_Program_State.xlsx'.")
        else:
            st.error("Required columns 'State', 'Program', 'College Name', and 'TYPE' are missing in the master sheet!")

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
