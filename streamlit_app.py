import streamlit as st
import pandas as pd
import os

st.title("ETERNALS")
# Constants
MASTER_FILE = "MASTER EXCEL.xlsx"

# Load MASTER EXCEL file
if not os.path.exists(MASTER_FILE):
    st.error(f"Master file '{MASTER_FILE}' is missing in the project folder!")
else:
    # Load the master sheet
    master_sheet = pd.read_excel(MASTER_FILE, sheet_name='Sheet1')

    # Normalize `State`, `Program`, and `TYPE` columns
    master_sheet['State'] = master_sheet['State'].str.strip().str.upper()
    master_sheet['Program'] = master_sheet['Program'].str.strip().str.upper()
    master_sheet['TYPE'] = master_sheet['TYPE'].astype(str).str.strip().str.upper()

    # Create MAIN CODE column
    if {'MCC College Code', 'COURSE CODE'}.issubset(master_sheet.columns):
        master_sheet['MAIN CODE'] = master_sheet['MCC College Code'].astype(str) + "_" + master_sheet['COURSE CODE'].astype(str)

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
                master_sheet['State Rank'] = master_sheet['State'].map(state_data.set_index('State')['State Rank']).fillna(0)
                master_sheet['Program Rank'] = master_sheet.apply(
                    lambda x: program_data.loc[
                        (program_data['Program'].str.upper() == x['Program'].upper()) &
                        (program_data['Program Type'].str.upper() == x['TYPE'].upper()),
                        'Program Rank'
                    ].values[0] if ((program_data['Program'].str.upper() == x['Program'].upper()) &
                                    (program_data['Program Type'].str.upper() == x['TYPE'].upper())).any() else 0,
                    axis=1
                )

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

    # Order Creation (Manual)
    elif page == "Order Creation":
        st.title("Order Creation Dashboard")

        # Ensure necessary columns exist
        if {'State', 'Program', 'College Name', 'TYPE'}.issubset(master_sheet.columns):
            unique_states = master_sheet['State'].unique()

            # Tabs for Ranking and Orders
            tab1, tab2, tab3 = st.tabs([
                "Ranking States",
                "Ranking Programs by Type",
                "Generate Order Table"
            ])

            # Ranking States
            with tab1:
                st.subheader("Rank States")
                rank_tab1, rank_tab2 = st.tabs(["Assign Rankings", "View Entered Rankings"])

                with rank_tab1:
                    state_ranking = {}
                    ranked_data = []

                    for state in unique_states:
                        col1, col2 = st.columns([4, 1])  # Adjusted column widths for better layout
                        with col1:
                            rank = st.selectbox(
                                state,  # Directly display the state name
                                options=[0] + [i for i in range(1, len(unique_states) + 1) if i not in state_ranking.values()],
                                key=f"state_{state}",
                            )
                        if rank > 0:
                            state_ranking[state] = rank
                            ranked_data.append({"State": state, "Rank": rank})

                with rank_tab2:
                    if ranked_data:
                        # Convert to DataFrame and reset the index to start from 1
                        state_df = pd.DataFrame(ranked_data).sort_values("Rank")
                        state_df.index = range(1, len(state_df) + 1)  # Reset index to start from 1
                        st.write("### Entered State Rankings")
                        st.dataframe(state_df)
                    else:
                        st.write("No states ranked yet. Please assign ranks to display the table.")

            # Ranking Programs by TYPE
            with tab2:
                st.subheader("Rank Programs by Type")
                rank_tab1, rank_tab2 = st.tabs(["Assign Rankings", "View Entered Rankings"])

                with rank_tab1:
                    all_programs = master_sheet[['TYPE', 'Program']].drop_duplicates()
                    program_ranking = {}
                    ranked_data = []

                    for _, row in all_programs.iterrows():
                        program = row['Program']
                        program_type = row['TYPE']
                        col1, col2 = st.columns([4, 1])  # Adjusted column widths for better layout
                        with col1:
                            rank = st.selectbox(
                                f"{program} ({program_type})",  # Concise label with program and type
                                options=[0] + [i for i in range(1, len(all_programs) + 1) if i not in program_ranking.values()],
                                key=f"program_{program}_{program_type}",
                            )
                        if rank > 0:
                            program_ranking[(program, program_type)] = rank
                            ranked_data.append({"Program": program, "TYPE": program_type, "Rank": rank})

                with rank_tab2:
                    if ranked_data:
                        # Convert to DataFrame and reset the index to start from 1
                        program_df = pd.DataFrame(ranked_data).sort_values("Rank")
                        program_df.index = range(1, len(program_df) + 1)  # Reset index to start from 1
                        st.write("### Entered Program Rankings")
                        st.dataframe(program_df)
                    else:
                        st.write("No programs ranked yet. Please assign ranks to display the table.")

            # Generate Ordered Table
            with tab3:
                st.subheader("Generate Order by Rankings")

                # Collapsible section to select columns to display
                with st.expander("Select Columns to Display", expanded=True):
                    st.write("### Choose the columns you want to include in the ordered table:")
                    default_columns = ['MAIN CODE', 'Program', 'TYPE', 'State', 'College Name', 'Program Rank', 'State Rank', 'Order Number']
                    selected_columns = st.multiselect(
                        "Select columns:",
                        list(master_sheet.columns) + ['State Rank', 'Program Rank', 'Order Number'],  # Include derived columns
                        default=default_columns
                    )

                # Generate Order Table button
                if st.button("Generate Order Table"):
                    # Apply rankings to the master sheet
                    master_sheet['State Rank'] = master_sheet['State'].map(state_ranking).fillna(0)
                    master_sheet['Program Rank'] = master_sheet.apply(
                        lambda x: program_ranking.get((x['Program'], x['TYPE']), 0), axis=1
                    )

                    # Filter and sort data
                    ordered_data = master_sheet.query("`State Rank` > 0 and `Program Rank` > 0").sort_values(
                        by=['Program Rank', 'State Rank']
                    ).reset_index(drop=True)
                    ordered_data['Order Number'] = range(1, len(ordered_data) + 1)

                    # Display the selected columns
                    if selected_columns:
                        st.write("### Ordered Table")
                        # Format numeric columns in the ordered table
                        st.dataframe(ordered_data[selected_columns].style.format({col: "{:.0f}" for col in numeric_columns}))
                    else:
                        st.warning("Please select at least one column to display the table.")
