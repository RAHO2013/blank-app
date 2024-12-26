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

    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Select a page:", ["Order Comparison", "Order Creation", "Fee Checking"])

    # Order Creation Page
    if page == "Order Creation":
        st.title("Order Creation Dashboard")

        # Ensure necessary columns exist
        if {'State', 'Program', 'College Name', 'TYPE'}.issubset(master_sheet.columns):

            # Dropdown to select column to rank
            st.subheader("Select Column to Rank")
            column_options = ["State", "Program", "TYPE"]
            selected_column = st.selectbox("Choose a column to rank:", column_options)

            # Filter unique values based on the selected column
            unique_items = sorted(master_sheet[selected_column].unique())

            # Display ranking widgets in a compact view
            st.subheader(f"Rank {selected_column}s")
            item_ranking = {}
            cols_per_row = 4  # Number of items to display per row
            rows = len(unique_items) // cols_per_row + (len(unique_items) % cols_per_row > 0)

            for i in range(rows):
                cols = st.columns(cols_per_row)
                for j, item in enumerate(unique_items[i * cols_per_row:(i + 1) * cols_per_row]):
                    with cols[j]:
                        rank = st.number_input(
                            f"{item} +",
                            min_value=1,
                            step=1,
                            key=f"{selected_column}_{item}",
                            help="Assign a unique rank"
                        )
                        item_ranking[item] = rank

            # Generate Ranked Data
            st.subheader("Generate Ranked Data")
            if st.button("Generate Ranked Table"):
                # Map rankings to the selected column
                master_sheet[f"{selected_column} Rank"] = master_sheet[selected_column].map(item_ranking).fillna(0)

                # Filter out zero-ranked items
                ranked_data = master_sheet[master_sheet[f"{selected_column} Rank"] > 0]

                # Sort by the selected column's rank
                ranked_data = ranked_data.sort_values(by=f"{selected_column} Rank").reset_index(drop=True)

                # Create Order Number
                ranked_data['Order Number'] = range(1, len(ranked_data) + 1)

                # Display Ranked Table
                st.write(f"### Ranked Table for {selected_column}s")
                st.write(ranked_data[[selected_column, f"{selected_column} Rank", 'Order Number']])

                # Save to file
                if st.button("Save Ranked Table"):
                    filename = f"Ranked_{selected_column}.xlsx"
                    ranked_data.to_excel(filename, index=False)
                    st.success(f"Ranked table saved as '{filename}'.")
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
