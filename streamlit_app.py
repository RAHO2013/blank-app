import streamlit as st
import pandas as pd
from PyPDF2 import PdfReader

def parse_admissions_data_from_pdf(file):
    # Read the uploaded PDF file
    reader = PdfReader(file)
    lines = []
    for page in reader.pages:
        extracted_text = page.extract_text()
        if extracted_text:  # Ensure text was extracted
            lines.extend(extracted_text.splitlines())

    # Log extracted lines for debugging
    if not lines:
        return pd.DataFrame(), ["No text extracted from PDF. Check the PDF formatting."]

    # Initialize variables
    structured_data = []
    debug_log = []
    current_college_code = ""
    current_college_name = ""
    current_course_code = ""
    current_course_name = ""
    processing_rows = False

    for line in lines:
        debug_log.append(f"Processing line: {line}")
        line = line.strip()
        
        # Skip empty or dashed lines
        if not line or "-----" in line:
            debug_log.append("Skipped line: Empty or dashed.")
            continue

        # Identify COLL sections
        if line.startswith("COLL ::"):
            parts = line.split(" - ")
            current_college_code = parts[0].replace("COLL ::", "").strip()
            current_college_name = parts[1].strip() if len(parts) > 1 else ""
            processing_rows = False  # Reset for new COLL section
            debug_log.append(f"Captured COLL: {current_college_code}, {current_college_name}")

        # Identify CRS sections
        elif line.startswith("CRS ::"):
            parts = line.split(" - ")
            current_course_code = parts[0].replace("CRS ::", "").strip()
            current_course_name = parts[1].strip() if len(parts) > 1 else ""
            processing_rows = True  # Start processing rows for this CRS
            debug_log.append(f"Captured CRS: {current_course_code}, {current_course_name}")

        # Skip headings like RANK, ROLL_NO
        elif line.lower().startswith("rank roll_no"):
            debug_log.append("Skipped line: Repeated headings.")
            continue

        # Process student rows
        elif processing_rows:
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
                        rank, roll_no, percentile, candidate_name, loc, cat, sx, 
                        min_status, ph, adm_details
                    ])
                    debug_log.append(f"Captured row: {structured_data[-1]}")
                except Exception as e:
                    debug_log.append(f"Error processing row: {line}, Error: {e}")

    # Define DataFrame columns
    columns = [
        "College Code", "College Name", "Course Code", "Course Name", "Rank",
        "Roll Number", "Percentile", "Candidate Name", "Location", "Category",
        "Sex", "MIN", "PH", "Admission Details"
    ]

    # Create DataFrame
    df = pd.DataFrame(structured_data, columns=columns)

    return df, debug_log

# Streamlit interface
st.title("Admissions Data Parser (PDF Support)")

uploaded_file = st.file_uploader("Upload your admissions PDF file", type=["pdf"])

if uploaded_file is not None:
    # Parse the uploaded PDF file
    df, debug_log = parse_admissions_data_from_pdf(uploaded_file)

    # Display debug logs
    st.write("### Debug Logs")
    st.text("\n".join(debug_log[:50]))  # Show first 50 log entries for brevity

    if not df.empty:
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
    else:
        st.error("No data extracted. Check the PDF format and content.")
