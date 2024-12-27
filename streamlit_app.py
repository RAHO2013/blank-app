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
    master_sheet = pd.read_excel(MASTER_FILE, sheet_name='Sheet1')

    # Normalize `State`, `Program`, and `TYPE` columns
    master_sheet['State'] = master_sheet['State'].str.strip().str.upper()
    master_sheet['Program'] = master_sheet['Program'].str.strip().str.upper()
    master_sheet['TYPE'] = master_sheet['TYPE'].astype(str).str.strip().str.upper()

    # Create MAIN CODE column
    if {'MCC College Code', 'COURSE CODE'}.issubset(master_sheet.columns):
        master_sheet['MAIN CODE'] = master_sheet['MCC College Code'].astype(str) + "_" + master_sheet['COURSE CODE'].astype(str)

    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Select a page:", ["Order Creation", "Order Comparison", "Fee Checking"])

    # Order Creation Page
    if page == "Order Creation":
        st.title("Order Creation Dashboard")

        # Ensure necessary columns exist
        if {'State', 'Program', 'College Name', 'TYPE'}.issubset(master_sheet.columns):
            unique_states = master_sheet['State'].unique()

            # Tabs for Ranking and Orders
            tab1, tab2, tab3 = st.tabs([
                "Ranking States",
                "Ranking Programs by Type",
                "Order by Ranking of Programs and States"
            ])

            # Ranking States
            with tab1:
                st.subheader("Rank States")
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

                # Check if ranked_data is populated
                if ranked_data:
                    # Convert to DataFrame and display the entered rankings
                    state_df = pd.DataFrame(ranked_data).sort_values("Rank")
                    st.write("### Entered State Rankings")
                    st.dataframe(state_df)
                else:
                    st.write("No states ranked yet. Please assign ranks to display the table.")

            # Ranking Programs by TYPE
            with tab2:
                st.subheader("Rank Programs by Type")
                all_programs = master_sheet[['TYPE', 'Program']].drop_duplicates()

                program_ranking = {}
                ranked_data = []

                # Ranking all programs without filtering by TYPE
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

                # Check if ranked_data is populated
                if ranked_data:
                    # Convert to DataFrame and display the entered rankings
                    program_df = pd.DataFrame(ranked_data).sort_values("Rank")
                    st.write("### Entered Program Rankings")
                    st.dataframe(program_df)
                else:
                    st.write("No programs ranked yet. Please assign ranks to display the table.")

            # Generate Ordered Table by Rankings
            with tab3:
                st.subheader("Generate Order by Rankings")
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

                    st.write("### Ordered Table")
                    st.dataframe(ordered_data[['MAIN CODE', 'Program', 'TYPE', 'State', 'College Name', 'Program Rank', 'State Rank', 'Order Number']])

                    # Save and download
                    if st.button("Save and Download Ordered Table"):
                        file_path = "Ordered_Program_State.xlsx"
                        ordered_data.to_excel(file_path, index=False)
                        st.success(f"Ordered table saved as '{file_path}'.")
                        with open(file_path, "rb") as file:
                            st.download_button("Download Ordered Table", file, file_name=file_path)

        else:
            st.error("Required columns 'State', 'Program', 'College Name', and 'TYPE' are missing in the master sheet!")

    # Order Comparison Page
    elif page == "Order Comparison":
        st.title("Order Comparison Dashboard")
        uploaded_file = st.file_uploader("Upload Comparison File (Excel)", type=["xlsx"])
        if uploaded_file:
            comparison_sheet = pd.read_excel(uploaded_file, sheet_name='Sheet1')
            if 'Institute Name' in comparison_sheet.columns and 'Program Name' in comparison_sheet.columns:
                comparison_sheet['MAIN CODE'] = comparison_sheet['Institute Name'].astype(str) + "_" + comparison_sheet['Program Name'].astype(str)
                st.success("MAIN CODE created for Comparison file.")
                master_sheet['MAIN CODE'] = master_sheet['MCC College Code'].astype(str) + "_" + master_sheet['COURSE CODE'].astype(str)
                missing_in_comparison = set(master_sheet['MAIN CODE']) - set(comparison_sheet['MAIN CODE'])
                missing_in_master = set(comparison_sheet['MAIN CODE']) - set(master_sheet['MAIN CODE'])

                st.write("### MAIN CODE Missing in Comparison File")
                st.dataframe(pd.DataFrame(list(missing_in_comparison), columns=["MAIN CODE"]))
                st.write("### MAIN CODE Missing in Master File")
                st.dataframe(pd.DataFrame(list(missing_in_master), columns=["MAIN CODE"]))

    # Fee Checking Page
    elif page == "Fee Checking":
        st.title("Fee Checking Dashboard")
        if 'Fees' in master_sheet.columns:
            st.bar_chart(master_sheet.groupby('Program')['Fees'].mean())
        else:
            st.warning("The column 'Fees' is missing in the master sheet.")
