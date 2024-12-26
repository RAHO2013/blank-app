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

            # Ranking States and Programs
            with tab1:
                st.subheader("Rank States and Programs")

                # Rank States in Expanders
                with st.expander("Rank States"):
                    st.write("### Rank States")
                    state_ranking = {}
                    used_state_ranks = set()  # Track used state ranks

                    cols_per_row = 5  # Number of widgets per row
                    rows = len(unique_states) // cols_per_row + (len(unique_states) % cols_per_row > 0)

                    for i in range(rows):
                        cols = st.columns(cols_per_row)
                        for j, state in enumerate(unique_states[i * cols_per_row:(i + 1) * cols_per_row]):
                            with cols[j]:
                                rank = st.number_input(
                                    f"Rank for {state}",
                                    min_value=1,
                                    step=1,
                                    key=f"state_{state}",
                                    help="Choose a unique rank."
                                )
                                if rank in used_state_ranks:
                                    st.error(f"Rank {rank} for state {state} is already used!")
                                else:
                                    state_ranking[state] = rank
                                    used_state_ranks.add(rank)

                # Rank Programs by TYPE in Expanders
                program_ranking = {}
                for type_value in unique_types:
                    with st.expander(f"Rank Programs for TYPE: {type_value}"):
                        st.write(f"### Programs in TYPE: {type_value}")
                        filtered_programs = sorted(master_sheet[master_sheet['TYPE'] == type_value]['Program'].unique())
                        used_program_ranks = set()  # Track used program ranks

                        rows = len(filtered_programs) // cols_per_row + (len(filtered_programs) % cols_per_row > 0)

                        for i in range(rows):
                            cols = st.columns(cols_per_row)
                            for j, program in enumerate(filtered_programs[i * cols_per_row:(i + 1) * cols_per_row]):
                                with cols[j]:
                                    rank = st.number_input(
                                        f"Rank for {program}",
                                        min_value=1,
                                        step=1,
                                        key=f"program_{program}_{type_value}",
                                        help="Choose a unique rank."
                                    )
                                    if rank in used_program_ranks:
                                        st.error(f"Rank {rank} for program {program} is already used!")
                                    else:
                                        program_ranking[program] = rank
                                        used_program_ranks.add(rank)

            # Generate Ordered Table by Rankings
            with tab2:
                st.subheader("Generate Order by Rankings")

                if st.button("Generate Order Table"):
                    # Map rankings to master sheet
                    master_sheet['State Rank'] = master_sheet['State'].map(state_ranking).fillna(0)
                    master_sheet['Program Rank'] = master_sheet['Program'].map(program_ranking).fillna(0)

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
