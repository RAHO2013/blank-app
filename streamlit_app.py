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

        # Process student rows based on specific rules
        else:
            try:
                # Treat large spaces as delimiters by splitting on multiple spaces
                fields = re.split(r"\s{2,}", line)

                if len(fields) < 10:  # Ensure there are enough fields for processing
                    continue

                # Extract fields based on expected positions
                rank = fields[0]
                roll_no = fields[1]
                percentile = fields[2]
                candidate_name = fields[3]
                loc = fields[4]
                cat = fields[5]
                sx = fields[6]
                min_status = fields[7] if fields[7] in ["MSM", ""] else ""
                ph = fields[8] if fields[8] in ["PHO", ""] else ""
                adm_details = fields[9] if re.match(r"(NS-|S-).*(-P1|-P2|-P3|-P4)$", fields[9]) else ""

                # Append structured row
                structured_data.append([
                    current_college_code, current_college_name,
                    current_course_code, current_course_name,
                    rank, roll_no, percentile, candidate_name,
                    loc, cat, sx, min_status, ph, adm_details
                ])
            except Exception as e:
                print(f"Error processing line: {line}, Error: {e}")
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
