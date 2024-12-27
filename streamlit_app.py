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

    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Select a page:", ["Order Creation", "Order Comparison", "Fee Checking"])

    # Helper function for ranking
    def rank_items(items, label_prefix):
        ranks = {}
        used_ranks = set()
        data = []

        for item in items:
            col1, col2 = st.columns([3, 1])  # Compact layout
            with col1:
                st.write(item)
            with col2:
                rank = st.selectbox(
                    f"Select rank for {item}",
                    options=[0] + [i for i in range(1, len(items) + 1) if i not in used_ranks],
                    key=f"{label_prefix}_{item}",
                )
                if rank > 0:
                    used_ranks.add(rank)
                ranks[item] = rank
                data.append({"Item": item, "Rank": rank})

        ranked_df = pd.DataFrame(data).query("Rank > 0").sort_values("Rank")
        return ranks, ranked_df

    # Order Creation Page
    if page == "Order Creation":
        st.title("Order Creation Dashboard")

        # Ensure necessary columns exist
        if {'State', 'Program', 'College Name', 'TYPE'}.issubset(master_sheet.columns):
            unique_states = master_sheet['State'].unique()
            unique_types = master_sheet['TYPE'].unique()

            # Tabs for Ranking and Orders
            tab1, tab2, tab3 = st.tabs([
                "Ranking States",
                "Ranking Programs by Type",
                "Order by Ranking of Programs and States"
            ])

            # Ranking States
            with tab1:
                st.subheader("Rank States")
                state_ranking, state_df = rank_items(unique_states, "state")
                st.write("### Entered State Rankings")
                st.dataframe(state_df)

            # Ranking Programs by TYPE
            with tab2:
                st.subheader("Rank Programs by Type")
                program_ranking = {}
                for type_value in unique_types:
                    st.write(f"### Ranking for TYPE: {type_value}")
                    filtered_programs = master_sheet[master_sheet['TYPE'] == type_value]['Program'].unique()
                    program_ranking[type_value], program_df = rank_items(filtered_programs, f"program_{type_value}")
                    st.write(f"### Entered Program Rankings for TYPE: {type_value}")
                    st.dataframe(program_df)

            # Generate Ordered Table by Rankings
            with tab3:
                st.subheader("Generate Order by Rankings")
                if st.button("Generate Order Table"):
                    # Apply rankings to the master sheet
                    master_sheet['State Rank'] = master_sheet['State'].map(state_ranking).fillna(0)
                    master_sheet['Program Rank'] = master_sheet['Program'].map(
                        lambda x: next((program_ranking[t].get(x, 0) for t in unique_types if x in program_ranking[t]), 0)
                    ).fillna(0)

                    # Filter and sort data
                    ordered_data = master_sheet.query("`State Rank` > 0 and `Program Rank` > 0").sort_values(
                        by=['Program Rank', 'State Rank']
                    ).reset_index(drop=True)
                    ordered_data['Order Number'] = range(1, len(ordered_data) + 1)

                    st.write("### Ordered Table")
                    st.dataframe(ordered_data[['Program', 'State', 'College Name', 'TYPE', 'Program Rank', 'State Rank', 'Order Number']])

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
