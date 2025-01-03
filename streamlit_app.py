import streamlit as st
import pandas as pd
import numpy as np
from scipy.stats import ttest_ind, f_oneway
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO
from docx import Document

# Function to create a Word document
def create_word_doc(content):
    doc = Document()
    for section in content:
        doc.add_heading(section['title'], level=1)
        for table in section.get('tables', []):
            doc.add_paragraph(f"Table: {table['title']}")
            df = table['dataframe']
            table_doc = doc.add_table(rows=1, cols=len(df.columns))
            table_doc.style = 'Table Grid'
            # Add headers
            hdr_cells = table_doc.rows[0].cells
            for i, col in enumerate(df.columns):
                hdr_cells[i].text = str(col)
            # Add rows
            for _, row in df.iterrows():
                row_cells = table_doc.add_row().cells
                for i, value in enumerate(row):
                    row_cells[i].text = str(value)
        for chart in section.get('charts', []):
            doc.add_paragraph(f"Chart: {chart['title']}")
            image_stream = chart["image_buffer"]
            doc.add_picture(image_stream)
    return doc

# Helper function to apply manual ranges
def apply_manual_ranges(value, ranges):
    for r in ranges:
        if r.startswith("<"):
            threshold = float(r[1:])
            if value < threshold:
                return r
        elif r.startswith(">"):
            threshold = float(r[1:])
            if value > threshold:
                return r
        elif "-" in r:
            low, high = map(float, r.split("-"))
            if low <= value < high:
                return r
    return "Other"  # Catch-all for values outside specified ranges

# Upload data
st.title("Streamlit Data Analysis App")
uploaded_file = st.file_uploader("Upload your Excel file", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    export_content = []

    # Tab structure
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["Distribution Tables", "Pivot Tables", "Statistical Analysis", "Correlations", "Graph Builder"])

    # Tab 1: Distribution Tables
    with tab1:
        st.header("Automated Distribution Tables")
        tab1_content = {"title": "Distribution Tables", "tables": [], "charts": []}

        for column in df.columns:
            if df[column].dtype in [np.int64, np.float64, object]:
                st.subheader(f"Distribution for {column}")

                # Option to use manual ranges or automatic binning
                use_manual_ranges = st.checkbox(f"Use Manual Ranges for {column}?", key=f"{column}_manual_ranges")
                manual_ranges = []
                if use_manual_ranges and df[column].dtype in [np.int64, np.float64]:
                    st.write("Specify manual ranges (e.g., '<5', '5-10', '>90')")
                    manual_ranges = st.text_area(
                        f"Enter ranges for {column} (one range per line)", 
                        value="<5\n5-10\n10-20\n>90",
                        key=f"{column}_manual_range_input"
                    ).splitlines()

                # Use automatic binning if manual ranges are not specified
                if not use_manual_ranges or not manual_ranges:
                    use_ranges = st.checkbox(f"Use Dynamic Ranges for {column}?", key=f"{column}_ranges")
                    if use_ranges and df[column].dtype in [np.int64, np.float64]:
                        range_step = st.number_input(
                            f"Step size for {column} ranges",
                            min_value=0.01 if df[column].dtype == np.float64 else 1,
                            value=10 if df[column].dtype == np.int64 else 0.1,
                            key=f"{column}_range_step",
                        )
                        bins = np.arange(df[column].min(), df[column].max() + range_step, range_step)
                        labels = [f"{round(bins[i], 2)}-{round(bins[i + 1], 2)}" for i in range(len(bins) - 1)]
                        df[column] = pd.cut(df[column], bins=bins, labels=labels, right=False)
                elif use_manual_ranges:
                    df[column] = df[column].apply(lambda x: apply_manual_ranges(x, manual_ranges))

                # Create distribution table
                distribution = df[column].value_counts().reset_index()
                distribution.columns = [column, "Count"]
                distribution["Percentage"] = (distribution["Count"] / distribution["Count"].sum() * 100).round(2).astype(str) + '%'
                distribution.reset_index(drop=True, inplace=True)
                distribution.index = distribution.index + 1  # Start index from 1

                if not distribution.empty:
                    total_row = pd.DataFrame({column: ["Total"], "Count": [distribution["Count"].sum()], "Percentage": ["100%"]})
                    distribution = pd.concat([distribution, total_row], ignore_index=True)

                    st.dataframe(distribution)
                    tab1_content["tables"].append({"title": f"Distribution for {column}", "dataframe": distribution})

                    # Graph Customization Options
                    graph_title = st.text_input(f"Graph Title for {column}", value=f"{column} Distribution", key=f"{column}_title")
                    x_label = st.text_input(f"X-Axis Label for {column}", value=column, key=f"{column}_x_label")
                    y_label = st.text_input(f"Y-Axis Label for {column}", value="Count", key=f"{column}_y_label")
                    legend_label = st.text_input(f"Legend Label for {column}", value="Values", key=f"{column}_legend")

                    # Plot chart
                    fig, ax = plt.subplots()
                    distribution.iloc[:-1].plot(kind="bar", x=column, y="Count", ax=ax, legend=False)
                    ax.set_title(graph_title)
                    ax.set_xlabel(x_label)
                    ax.set_ylabel(y_label)
                    ax.legend([legend_label])
                    ax.tick_params(axis="x", rotation=0)  # Set x-axis labels to horizontal
                    st.pyplot(fig)

                    # Save chart for Word export
                    buffer = BytesIO()
                    fig.savefig(buffer, format="png")
                    buffer.seek(0)
                    tab1_content["charts"].append({"title": f"{column} Distribution", "image_buffer": buffer})
                else:
                    st.info(f"No data available for column {column}.")

        export_content.append(tab1_content)

    # Tab 3: Statistical Analysis
    with tab3:
        st.header("Statistical Analysis")
        st.write("Select columns for statistical calculations.")
        selected_columns = st.multiselect("Select Columns", df.select_dtypes(include=[np.number]).columns)
        
        # T-Test
        if len(selected_columns) == 2:
            col1, col2 = selected_columns[:2]
            st.write(f"Calculating statistics between {col1} and {col2}")

            stats = {
                "Metric": ["Mean", "Median", "Std Dev", "T-Statistic", "P-Value"],
                col1: [
                    df[col1].mean(),
                    df[col1].median(),
                    df[col1].std(),
                    None,  # Placeholder for T-Statistic
                    None,  # Placeholder for P-Value,
                ],
                col2: [
                    df[col2].mean(),
                    df[col2].median(),
                    df[col2].std(),
                    None,
                    None,
                ],
            }
            t_stat, p_value = ttest_ind(df[col1].dropna(), df[col2].dropna())
            stats[col1][3] = t_stat
            stats[col1][4] = p_value
            stats[col2][3] = t_stat
            stats[col2][4] = p_value

            stats_df = pd.DataFrame(stats)
            stats_df.index = stats_df.index + 1  # Start index from 1
            st.dataframe(stats_df)

        # ANOVA
        if len(selected_columns) > 2:
            st.write("Performing ANOVA test for selected columns.")
            groups = [df[col].dropna() for col in selected_columns]
            f_stat, p_value = f_oneway(*groups)
            st.write(f"ANOVA F-Statistic: {f_stat:.4f}")
            st.write(f"ANOVA P-Value: {p_value:.4f}")
