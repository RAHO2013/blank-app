import streamlit as st
import pandas as pd
import pdfplumber
import re

# Function to dynamically apply rules
def apply_dynamic_rules(line, rules):
    try:
        # Extract rank
        rank_match = re.search(rules["rank"], line)
        rank = rank_match.group(1) if rank_match else ""

        # Extract roll number
        roll_no_match = re.search(rules["roll_no"], line)
        roll_no = roll_no_match.group(1) if roll_no_match else ""

        # Extract percentile
        percentile_match = re.search(rules["percentile"], line)
        percentile = percentile_match.group(1) if percentile_match else ""

        # Extract candidate name
        name_start = line.find(percentile) + len(percentile)
        name_end = line.find("OU", name_start)
        candidate_name = line[name_start:name_end].strip() if name_end != -1 else ""

        # Extract location, category, sex, MIN, PH, and Admission Details
        loc = "OU" if "OU" in line else ""
        cat_match = re.search(rules["category"], line)
        cat = cat_match.group(1) if cat_match else ""
        sx_match = re.search(rules["sex"], line)
        sx = sx_match.group(1) if sx_match else ""
        min_match = re.search(rules["min"], line)
        min_status = min_match.group(1) if min_match else ""
        ph_match = re.search(rules["ph"], line)
        ph = ph_match.group(1) if ph_match else ""
        adm_details_match = re.search(rules["admission_details"], line)
        adm_details = adm_details_match.group(0) if adm_details_match else ""

        return [rank, roll_no, percentile, candidate_name, loc, cat, sx, min_status, ph, adm_details]
    except Exception as e:
        print(f"Error applying rules: {line}, Error: {e}")
        return []

# Function to parse PDF
def extract_college_course_and_student_details(file, rules):
    # Read PDF file
    lines = []
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            extracted_text = page.extract_text()
            if extracted_text:
                lines.extend(extracted_text.splitlines())

    # Process lines
    structured_data = []
    for line in lines:
        line = line.strip()
        if not line or "-----" in line:
            continue
        structured_data.append(apply_dynamic_rules(line, rules))

    # Create DataFrame
    columns = [
        "Rank", "Roll Number", "Percentile", "Candidate Name",
        "Location", "Category", "Sex", "MIN", "PH", "Admission Details"
    ]
    df = pd.DataFrame(structured_data, columns=columns)
    return df

# Streamlit app interface
st.title("Dynamic Rules Admissions Data Parser")

# Define default rules
default_rules = {
    "rank": r"^(\d{1,6})\s",
    "roll_no": r"(24\d{9})",
    "percentile": r"(\d+\.\d+)",
    "category": r"(BCA|BCB|BCD|BCC|BCE|ST|SC|OC)",
    "sex": r"(F|M)",
    "min": r"(MSM)?",
    "ph": r"(PHO)?",
    "admission_details": r"(NS-|S-).*(-P1|-P2|-P3|-P4)$"
}

# User interface for rule modification
st.sidebar.title("Edit Parsing Rules")
rules = {}
for key, regex in default_rules.items():
    rules[key] = st.sidebar.text_input(f"Rule for {key.replace('_', ' ').capitalize()}", regex)

# File upload
uploaded_file = st.file_uploader("Upload your admissions PDF file", type=["pdf"])

if uploaded_file is not None:
    # Extract and display data
    df = extract_college_course_and_student_details(uploaded_file, rules)
    if not df.empty:
        st.write("### Extracted Data")
        st.dataframe(df)
        # Download button for Excel
        excel_file = "structured_admissions_data.xlsx"
        df.to_excel(excel_file, index=False)
        with open(excel_file, "rb") as file:
            st.download_button(
                label="Download Excel File",
                data=file,
                file_name="structured_admissions_data.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
    else:
        st.error("No data extracted. Check the PDF format or rules.")
