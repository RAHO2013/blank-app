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

                # Rank Programs by TYPE in Expanders
                program_ranking = {}
                for type_value in unique_types:
                    with st.expander(f"Rank Programs for TYPE: {type_value}"):
                        st.write(f"### Programs in TYPE: {type_value}")
                        filtered_programs = master_sheet[master_sheet['TYPE'] == type_value]['Program'].unique()

                        used_program_ranks = set()  # Track used ranks for programs

                        # Create a compact table for programs
                        rows = []
                        for program in filtered_programs:
                            rank = st.selectbox(
                                f"Rank for {program}",
                                options=[0] + [i for i in range(1, len(filtered_programs) + 1) if i not in used_program_ranks],
                                key=f"program_{program}_{type_value}",
                            )
                            if rank > 0:
                                used_program_ranks.add(rank)
                            rows.append({"Program": program, "Rank": rank})

                        # Convert to DataFrame and display
                        program_df = pd.DataFrame(rows)
                        display_programs = program_df[program_df["Rank"] > 0].sort_values("Rank")
                        st.write(display_programs)

                        program_ranking.update(dict(zip(program_df['Program'], program_df['Rank'])))

            # Generate Ordered Table by Rankings
            with tab2:
                st.subheader("Generate Order by Rankings")

                if st.button("Generate Order Table"):
                    # Map rankings to master sheet
                    master_sheet['Program Rank'] = master_sheet['Program'].map(program_ranking).fillna(0)

                    # Filter out zero-ranked programs
                    filtered_data = master_sheet[master_sheet['Program Rank'] > 0]

                    # Sort by Program Rank
                    ordered_data = filtered_data.sort_values(by=['Program Rank']).reset_index(drop=True)

                    # Create Order Number
                    ordered_data['Order Number'] = range(1, len(ordered_data) + 1)

                    # Display Ordered Table with College Name
                    st.write("### Ordered Table")
                    st.write(ordered_data[['Program', 'State', 'College Name', 'TYPE', 'Program Rank', 'Order Number']])

                    # Save to file
                    if st.button("Save Ordered Table"):
                        ordered_data.to_excel("Ordered_Program_State.xlsx", index=False)
                        st.success("Ordered table saved as 'Ordered_Program_State.xlsx'.")
        else:
            st.error("Required columns 'State', 'Program', 'College Name', and 'TYPE' are missing in the master sheet!")
