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

            # Tabs for Ranking and Orders
            tab1, tab2 = st.tabs(["Rank States and Programs", "Order by Ranking"])

            with tab1:
                st.subheader("Rank States and Programs")

                # Rank States in Expander
                with st.expander("Rank States"):
                    st.write("### Rank States")
                    state_ranking = {}
                    used_state_ranks = set()  # Track used state ranks

                    state_data = []
                    for state in unique_states:
                        col1, col2 = st.columns([3, 1])  # Adjust layout for compactness
                        with col1:
                            st.write(state)
                        with col2:
                            rank = st.selectbox(
                                f"Rank for {state}",
                                options=[0] + [i for i in range(1, len(unique_states) + 1) if i not in used_state_ranks],
                                key=f"state_{state}",
                            )
                            if rank > 0:
                                used_state_ranks.add(rank)
                            state_data.append({"State": state, "Rank": rank})

                    # Display only non-zero ranks for the user
                    state_df = pd.DataFrame(state_data)
                    display_states = state_df[state_df["Rank"] > 0].sort_values("Rank")
                    st.write(display_states)

                # Rank Programs by TYPE in Expanders
                program_ranking = {}
                for type_value in unique_types:
                    with st.expander(f"Rank Programs for TYPE: {type_value}"):
                        st.write(f"### Programs in TYPE: {type_value}")
                        filtered_programs = master_sheet[master_sheet['TYPE'] == type_value]['Program'].unique()

                        used_program_ranks = set()  # Track used ranks for programs

                        program_data = []
                        for program in filtered_programs:
                            col1, col2 = st.columns([3, 1])
                            with col1:
                                st.write(program)
                            with col2:
                                rank = st.selectbox(
                                    f"Rank for {program}",
                                    options=[0] + [i for i in range(1, len(filtered_programs) + 1) if i not in used_program_ranks],
                                    key=f"program_{program}_{type_value}",
                                )
                                if rank > 0:
                                    used_program_ranks.add(rank)
                                program_data.append({"Program": program, "Rank": rank})

                        # Display only non-zero ranks for the user
                        program_df = pd.DataFrame(program_data)
                        display_programs = program_df[program_df["Rank"] > 0].sort_values("Rank")
                        st.write(display_programs)

                        program_ranking.update(dict(zip(program_df["Program"], program_df["Rank"])))

            # Generate Ordered Table by Rankings
            with tab2:
                st.subheader("Generate Order by Rankings")

                if st.button("Generate Order Table"):
                    # Map rankings to master sheet
                    master_sheet['State Rank'] = master_sheet['State'].map(
                        dict(zip(state_df['State'], state_df['Rank']))
                    ).fillna(0)
                    master_sheet['Program Rank'] = master_sheet['Program'].map(
                        dict(zip(program_df['Program'], program_df['Rank']))
                    ).fillna(0)

                    # Filter out zero-ranked states and programs
                    filtered_data = master_sheet[
                        (master_sheet['State Rank'] > 0) | 
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
