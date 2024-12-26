import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

# File Upload or Static File Handling
st.sidebar.title("Upload or Use Default File")
uploaded_file = st.sidebar.file_uploader("Upload MASTER EXCEL file", type=["xlsx"])

if uploaded_file is not None:
    MASTER_FILE = uploaded_file
else:
    MASTER_FILE = "MASTER EXCEL.xlsx"

# Check if the master file is available
try:
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

        # Tabs for Ranking
        rank_tab, order_tab = st.tabs(["Rank States and Programs", "Order by Ranking"])

        with rank_tab:
            # Sub-tabs for Ranking States and Programs
            state_tab, program_tab = st.tabs(["Rank States", "Rank Programs by TYPE"])

            # Rank States Tab
            with state_tab:
                st.subheader("Rank States")

                # Create an editable table for states
                state_table = pd.DataFrame({'State': unique_states, 'Rank': [0] * len(unique_states)})

                # Set up AgGrid
                gb = GridOptionsBuilder.from_dataframe(state_table)
                gb.configure_default_column(editable=True)
                gb.configure_column("Rank", editable=True)
                grid_options = gb.build()

                st.write("### Edit State Rankings")
                grid_response = AgGrid(
                    state_table,
                    gridOptions=grid_options,
                    update_mode=GridUpdateMode.MANUAL,
                    fit_columns_on_grid_load=True,
                )

                # Updated table from the grid
                updated_state_data = pd.DataFrame(grid_response["data"])

                st.write("Updated State Rankings:")
                st.write(updated_state_data)

            # Rank Programs by TYPE Tab
            with program_tab:
                st.subheader("Rank Programs by TYPE")

                # Dropdown to Select Program Type
                selected_type = st.selectbox("Select Program TYPE to Rank:", options=unique_types)

                if selected_type:
                    # Filter Programs by Selected Type
                    filtered_programs = sorted(master_sheet[master_sheet['TYPE'] == selected_type]['Program'].unique())
                    program_table = pd.DataFrame({'Program': filtered_programs, 'Rank': [0] * len(filtered_programs)})

                    # Set up AgGrid
                    gb = GridOptionsBuilder.from_dataframe(program_table)
                    gb.configure_default_column(editable=True)
                    gb.configure_column("Rank", editable=True)
                    grid_options = gb.build()

                    st.write(f"### Edit Program Rankings for TYPE: {selected_type}")
                    grid_response = AgGrid(
                        program_table,
                        gridOptions=grid_options,
                        update_mode=GridUpdateMode.MANUAL,
                        fit_columns_on_grid_load=True,
                    )

                    # Updated table from the grid
                    updated_program_data = pd.DataFrame(grid_response["data"])

                    st.write(f"Updated Program Rankings for TYPE: {selected_type}")
                    st.write(updated_program_data)

        # Generate Ordered Table by Rankings
        with order_tab:
            st.subheader("Generate Order by Rankings")

            if st.button("Generate Order Table"):
                # Map rankings to master sheet
                state_ranking = dict(zip(updated_state_data["State"], updated_state_data["Rank"]))
                program_ranking = dict(zip(updated_program_data["Program"], updated_program_data["Rank"]))

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
except Exception as e:
    st.error(f"Error loading the master file: {e}")
