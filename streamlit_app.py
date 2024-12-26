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

                    # Initialize State Ranking Dictionary
                    state_ranking = {}
                    used_state_ranks = set()  # Track used ranks across states

                    # Table Header
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.markdown("**State**")
                    with col2:
                        st.markdown("**Rank**")

                    # Display States in a Table
                    for state in unique_states:
                        col1, col2 = st.columns([3, 1])
                        with col1:
                            st.write(state)
                        with col2:
                            rank = st.number_input(
                                f"Rank for {state}",
                                min_value=0,
                                step=1,
                                key=f"state_{state}",
                                help="Assign a unique rank for the state.",
                            )
                            if rank > 0:
                                if rank in used_state_ranks:
                                    st.warning(f"Duplicate rank detected for States: {rank}")
                                else:
                                    state_ranking[state] = rank
                                    used_state_ranks.add(rank)

                # Rank Programs by TYPE Tab
                with program_tab:
                    st.subheader("Rank Programs by TYPE")

                    # Dropdown to Select Program Type
                    selected_type = st.selectbox("Select Program TYPE to Rank:", options=unique_types)

                    if selected_type:
                        st.write(f"### Programs for {selected_type}")

                        # Filter Programs by Selected Type
                        filtered_programs = sorted(master_sheet[master_sheet['TYPE'] == selected_type]['Program'].unique())

                        # Initialize Program Ranking Dictionary
                        program_ranking = {}
                        used_program_ranks = set()  # Track used ranks locally for this TYPE

                        # Table Header
                        col1, col2 = st.columns([3, 1])
                        with col1:
                            st.markdown("**Program**")
                        with col2:
                            st.markdown("**Rank**")

                        # Display Programs in a Table
                        for program in filtered_programs:
                            col1, col2 = st.columns([3, 1])
                            with col1:
                                st.write(program)
                            with col2:
                                rank = st.number_input(
                                    f"Rank for {program}",
                                    min_value=0,
                                    step=1,
                                    key=f"program_{program}_{selected_type}",
                                    help="Assign a unique rank for the program.",
                                )
                                if rank > 0:
                                    if rank in used_program_ranks:
                                        st.warning(f"Duplicate rank detected for Programs ({selected_type}): {rank}")
                                    else:
                                        program_ranking[program] = rank
                                        used_program_ranks.add(rank)

            # Generate Ordered Table by Rankings
            with order_tab:
                st.subheader("Generate Order by Rankings")

                if st.button("Generate Order Table"):
                    # Map rankings to master sheet
                    master_sheet['State Rank'] = master_sheet['State'].map(state_ranking).fillna(0)
                    master_sheet['Program Rank'] = master_sheet['Program'].map(program_ranking).fillna(0)

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
