import streamlit as st
import pandas as pd
import pdfplumber
import re

def extract_college_course_and_student_details(file):
    # Read the uploaded PDF file
    lines = []
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            extracted_text = page.extract_text()
            if extracted_text:
                lines.extend(extracted_text.splitlines())

    # Initialize variables
    structured_data = []
    current_college_code = ""
    current_college_name = ""
    current_course_code = ""
    current_course_name = ""

    for line in lines:
        line = line.strip()

        # Skip empty or dashed lines
        if not line or "-----" in line:
            continue

        # Capture college details from COLL ::
        if line.startswith("COLL ::"):
            parts = line.split(" - ")
            current_college_code = parts[0].replace("COLL ::", "").strip()
            current_college_name = parts[1].strip() if len(parts) > 1 else ""

        # Capture course details from CRS ::
        elif line.startswith("CRS ::"):
            parts = line.split(" - ")
            current_course_code = parts[0].replace("CRS ::", "").strip()
            current_course_name = parts[1].strip() if len(parts) > 1 else ""

        # Process student rows
        else:
            parts = line.split()
            if len(parts) >= 10:  # Ensure minimum columns for valid data
                try:
                    rank = parts[0]
                    roll_no = parts[1]
                    percentile = parts[2]
                    candidate_name = " ".join(parts[3:-7])
                    loc = parts[-7]
                    cat = parts[-6]
                    sx = parts[-5]
                    min_status = parts[-4]
                    ph = parts[-3]
                    adm_details = " ".join(parts[-2:])

                    # Append structured row
                    structured_data.append([
                        current_college_code, current_college_name,
                        current_course_code, current_course_name,
                        rank, roll_no, percentile, candidate_name,
                        loc, cat, sx, min_status, ph, adm_details
                    ])
                except Exception as e:
                    continue

    # Define DataFrame columns
    columns = [
        "College Code", "College Name", "Course Code", "Course Name",
        "Rank", "Roll Number", "Percentile", "Candidate Name",
        "Location", "Category", "Sex", "MIN", "PH", "Admission Details"
    ]

    # Create DataFrame
    df = pd.DataFrame(structured_data, columns=columns)
    return df

# Streamlit interface
st.title("College, Course, and Student Details Extractor")

uploaded_file = st.file_uploader("Upload your admissions PDF file", type=["pdf"])

if uploaded_file is not None:
    # Extract college, course, and student details
    df = extract_college_course_and_student_details(uploaded_file)

    if not df.empty:
        # Display the DataFrame
        st.write("### Extracted College, Course, and Student Details")
        st.dataframe(df)

        # Allow user to download the Excel file
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
        st.error("No data extracted. Check the PDF format and content.")
