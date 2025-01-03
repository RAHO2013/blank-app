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
            if df[column].dtype in [np.int64, np.float64, object]:  # Updated to replace np.object
                st.subheader(f"Distribution for {column}")
                distribution = df[column].value_counts(normalize=True).reset_index()
                distribution.columns = [column, "Count"]
                distribution["Percentage"] = (distribution["Count"] / distribution["Count"].sum() * 100).round(2).astype(str) + '%'
                st.dataframe(distribution)

                # Plot chart
                fig, ax = plt.subplots()
                if len(distribution) > 10:
                    distribution.plot(kind="bar", x=column, y="Count", ax=ax)
                else:
                    distribution.set_index(column)["Count"].plot(kind="pie", autopct='%1.1f%%', ax=ax)
                st.pyplot(fig)

    # Tab 2: Pivot Tables
    with tab2:
        st.header("Pivot Tables")
        st.write("Select columns to create pivot tables.")
        index_col = st.selectbox("Index", df.columns)
        columns_col = st.selectbox("Columns", df.columns)
        values_col = st.selectbox("Values", df.columns)
        agg_func = st.selectbox("Aggregation Function", ["mean", "sum", "count", "max", "min"])

        if st.button("Generate Pivot Table"):
            pivot_table = pd.pivot_table(df, index=index_col, columns=columns_col, values=values_col, aggfunc=agg_func)
            st.dataframe(pivot_table)

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
            st.pyplot(fig)
