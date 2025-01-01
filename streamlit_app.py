import streamlit as st
import pandas as pd
from PyPDF2 import PdfReader

def parse_admissions_data_from_pdf(file):
    # Read the uploaded PDF file
    reader = PdfReader(file)
    lines = []
    for page in reader.pages:
        lines.extend(page.extract_text().splitlines())

    # Initialize variables
    structured_data = []
    current_college_code = ""
    current_college_name = ""
    current_course_code = ""
    current_course_name = ""
    processing_rows = False

    for line in lines:
        line = line.strip()
        
        # Skip empty or dashed lines
        if not line or "-----" in line:
            continue

        # Identify COLL sections
        if line.startswith("COLL ::"):
            parts = line.split(" - ")
            current_college_code = parts[0].replace("COLL ::", "").strip()
            current_college_name = parts[1].strip() if len(parts) > 1 else ""
            processing_rows = False  # Reset for new COLL section

        # Identify CRS sections
        elif line.startswith("CRS ::"):
            parts = line.split(" - ")
            current_course_code = parts[0].replace("CRS ::", "").strip()
            current_course_name = parts[1].strip() if len(parts) > 1 else ""
            processing_rows = True  # Start processing rows for this CRS

        # Process student rows
        elif processing_rows:
            parts = line.split()
            if len(parts) >= 10:  # Ensure minimum columns for valid data
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
                    rank, roll_no, percentile, candidate_name, loc, cat, sx, 
                    min_status, ph, adm_details
                ])

    # Define DataFrame columns
    columns = [
        "College Code", "College Name", "Course Code", "Course Name", "Rank",
        "Roll Number", "Percentile", "Candidate Name", "Location", "Category",
        "Sex", "MIN", "PH", "Admission Details"
    ]

    # Create DataFrame
    df = pd.DataFrame(structured_data, columns=columns)

    return df

# Streamlit interface
st.title("Admissions Data Parser (PDF Support)")

uploaded_file = st.file_uploader("Upload your admissions PDF file", type=["pdf"])

if uploaded_file is not None:
    # Parse the uploaded PDF file
    df = parse_admissions_data_from_pdf(uploaded_file)

    # Display the DataFrame
    st.write("### Parsed Admissions Data")
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
