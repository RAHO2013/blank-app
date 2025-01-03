import streamlit as st
import pandas as pd
import numpy as np
from scipy.stats import ttest_ind
import matplotlib.pyplot as plt
import seaborn as sns

# Upload data
st.title("Streamlit Data Analysis App")
uploaded_file = st.file_uploader("Upload your Excel file", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)

    # Tab structure
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["Distribution Tables", "Pivot Tables", "Statistical Analysis", "Correlations", "Graph Builder"])

    # Tab 1: Distribution Tables
    with tab1:
        st.header("Automated Distribution Tables")
        for column in df.columns:
            if df[column].dtype in [np.int64, np.float64, object]:
                st.subheader(f"Distribution for {column}")
                distribution = df[column].value_counts().reset_index()
                distribution.columns = [column, "Count"]
                distribution["Percentage"] = (distribution["Count"] / distribution["Count"].sum() * 100).round(2).astype(str) + '%'
                distribution.reset_index(drop=True, inplace=True)
                distribution.index = distribution.index + 1  # Start index from 1
                st.dataframe(distribution)

                # Plot chart with customization options
                chart_type = st.selectbox(f"Select Chart Type for {column}", ["Bar", "Pie"], key=f"{column}_chart_type")
                chart_title = st.text_input(f"Chart Title for {column}", value=f"{column} Distribution", key=f"{column}_title")
                x_label = st.text_input(f"X-Axis Label for {column}", value=column, key=f"{column}_xlabel")
                y_label = st.text_input(f"Y-Axis Label for {column}", value="Count", key=f"{column}_ylabel")
                legend_label = st.text_input(f"Legend Label for {column}", value="Values", key=f"{column}_legend")

                fig, ax = plt.subplots()
                if chart_type == "Bar":
                    ax.bar(distribution[column], distribution["Count"], label=legend_label)
                    ax.set_xlabel(x_label)
                    ax.set_ylabel(y_label)
                elif chart_type == "Pie":
                    ax.pie(distribution["Count"], labels=distribution[column], autopct='%1.1f%%')
                ax.set_title(chart_title)
                ax.legend()
                st.pyplot(fig)

    # Tab 2: Pivot Tables
    with tab2:
        st.header("Pivot Tables")
        st.write("Select columns to create pivot tables.")

        rows = st.multiselect("Rows", df.columns)
        cols = st.multiselect("Columns", df.columns)
        values = st.selectbox("Values", df.columns)
        filters = st.multiselect("Filters", df.columns)
        agg_func = st.selectbox("Aggregation Function", ["mean", "sum", "count", "max", "min"])

        if st.button("Generate Pivot Table"):
            try:
                pivot_table = pd.pivot_table(
                    df,
                    index=rows,
                    columns=cols,
                    values=values,
                    aggfunc=agg_func,
                )
                pivot_table.reset_index(drop=True, inplace=True)
                pivot_table.index = pivot_table.index + 1  # Start index from 1
                st.dataframe(pivot_table)
            except Exception as e:
                st.error(f"Error generating pivot table: {e}")

    # Tab 3: Statistical Analysis
    with tab3:
        st.header("Statistical Analysis")
        st.write("Select columns for statistical calculations.")
        selected_columns = st.multiselect("Select Columns", df.select_dtypes(include=[np.number]).columns)
        if len(selected_columns) >= 2:
            col1, col2 = selected_columns[:2]
            st.write(f"Calculating statistics between {col1} and {col2}")

            # Calculate statistics
            mean1, mean2 = df[col1].mean(), df[col2].mean()
            median1, median2 = df[col1].median(), df[col2].median()
            std1, std2 = df[col1].std(), df[col2].std()
            t_stat, p_value = ttest_ind(df[col1].dropna(), df[col2].dropna())

            st.write(f"Mean: {mean1:.2f}, {mean2:.2f}")
            st.write(f"Median: {median1:.2f}, {median2:.2f}")
            st.write(f"Standard Deviation: {std1:.2f}, {std2:.2f}")
            st.write(f"T-Statistic: {t_stat:.2f}")
            st.write(f"P-Value: {p_value:.4f}")

    # Tab 4: Correlations
    with tab4:
        st.header("Correlations")
        st.write("Correlation matrix of numeric columns.")
        correlation_matrix = df.corr()
        correlation_matrix.reset_index(drop=True, inplace=True)
        correlation_matrix.index = correlation_matrix.index + 1  # Start index from 1
        st.dataframe(correlation_matrix)

        # Heatmap
        fig, ax = plt.subplots()
        sns.heatmap(correlation_matrix, annot=True, cmap="coolwarm", ax=ax)
        st.pyplot(fig)

    # Tab 5: Graph Builder
    with tab5:
        st.header("Graph Builder")
        st.write("Select columns to build graphs.")
        x_col = st.selectbox("X-Axis", df.columns)
        y_col = st.selectbox("Y-Axis", df.columns)
        graph_type = st.selectbox("Graph Type", ["Scatter", "Line", "Bar", "Histogram", "Boxplot"])

        # Customization options for the graph
        graph_title = st.text_input("Graph Title", value=f"{x_col} vs {y_col}")
        x_label = st.text_input("X-Axis Label", value=x_col)
        y_label = st.text_input("Y-Axis Label", value=y_col)

        if st.button("Generate Graph"):
            fig, ax = plt.subplots()
            if graph_type == "Scatter":
                sns.scatterplot(x=df[x_col], y=df[y_col], ax=ax)
            elif graph_type == "Line":
                sns.lineplot(x=df[x_col], y=df[y_col], ax=ax)
            elif graph_type == "Bar":
                sns.barplot(x=df[x_col], y=df[y_col], ax=ax)
            elif graph_type == "Histogram":
                sns.histplot(df[x_col], bins=30, kde=True, ax=ax)
            elif graph_type == "Boxplot":
                sns.boxplot(x=df[x_col], y=df[y_col], ax=ax)
            ax.set_title(graph_title)
            ax.set_xlabel(x_label)
            ax.set_ylabel(y_label)
            st.pyplot(fig)
