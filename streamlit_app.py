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

    # Initialize variables
    structured_data = []
    current_college_code = ""
    current_college_name = ""
    current_course_code = ""
    current_course_name = ""
    processing_rows = False  # Ensure rows are processed only after the first COLL section
    buffer = ""

    for line in lines:
        line = line.strip()
        
        # Skip empty or dashed lines
        if not line or "-----" in line:
            continue

        # Combine buffer with the current line if necessary
        if not line.startswith("COLL ::") and not line.startswith("CRS ::") and processing_rows:
            buffer += f" {line}"
            line = buffer.strip()

        # Ensure data processing starts only after the first COLL section
        if line.startswith("COLL ::"):
            parts = line.split(" - ")
            current_college_code = parts[0].replace("COLL ::", "").strip()
            current_college_name = parts[1].strip() if len(parts) > 1 else ""
            processing_rows = True  # Start processing rows after COLL is found
            buffer = ""  # Reset buffer

        # Identify CRS sections
        elif line.startswith("CRS ::"):
            if processing_rows:  # Only process CRS if a COLL has been encountered
                parts = line.split(" - ")
                current_course_code = parts[0].replace("CRS ::", "").strip()
                current_course_name = parts[1].strip() if len(parts) > 1 else ""
                buffer = ""  # Reset buffer

        # Skip repeated headers
        elif line.lower().startswith("rank roll_no percentile candidate_name loc cat sx min ph adm details"):
            continue

        # Process student rows only if processing_rows is True
        elif processing_rows:
            parts = line.split()
            if len(parts) >= 10:  # Ensure minimum columns for valid data
                try:
                    # Extract and validate Rank
                    rank = parts[0]
                    if not rank.isdigit() or int(rank) > 300000:
                        buffer = line  # Store the line in buffer for multi-line handling
                        continue

                    # Extract and validate Roll Number
                    roll_no = parts[1]
                    if not (roll_no.isdigit() and len(roll_no) == 11 and roll_no.startswith("24")):
                        buffer = line
                        continue

                    # Extract Percentile
                    percentile = parts[2]
                    if not percentile.replace(".", "").isdigit():
                        buffer = line
                        continue

                    # Extract Candidate Name
                    candidate_name_end_index = next((i for i, part in enumerate(parts[3:], start=3) if part in ["OU", "BCB", "BCA", "BCD", "BCC", "BCE", "ST", "SC", "OC"]), None)
                    candidate_name = " ".join(parts[3:candidate_name_end_index]) if candidate_name_end_index else ""

                    # Extract Location
                    loc = parts[candidate_name_end_index]

                    # Extract Category
                    cat = parts[candidate_name_end_index + 1]
                    if cat not in ["BCA", "BCB", "BCD", "BCC", "BCE", "ST", "SC", "OC"]:
                        buffer = line
                        continue

                    # Extract Sex
                    sx = parts[candidate_name_end_index + 2]
                    if sx not in ["F", "M"]:
                        buffer = line
                        continue

                    # Extract MIN
                    min_status = parts[candidate_name_end_index + 3]
                    if min_status not in ["MSM", ""]:
                        buffer = line
                        continue

                    # Extract PH
                    ph = parts[candidate_name_end_index + 4]
                    if ph not in ["PHO", ""]:
                        buffer = line
                        continue

                    # Extract Admission Details
                    adm_details = parts[candidate_name_end_index + 5]
                    if not (adm_details.startswith("N") or adm_details.startswith("S")) or not adm_details.endswith("1"):
                        buffer = line
                        continue

                    # Append structured row
                    structured_data.append([
                        current_college_code, current_college_name, 
                        current_course_code, current_course_name, 
                        rank, roll_no, percentile, candidate_name, loc, cat, sx, 
                        min_status, ph, adm_details
                    ])
                    buffer = ""  # Reset buffer
                except Exception as e:
                    buffer = line
                    continue

    # Define DataFrame columns
    columns = [
        "College Code", "College Name", "Course Code", "Course Name", "Rank",
        "Roll Number", "Percentile", "Candidate Name", "Location", "Category",
        "Sex", "MIN", "PH", "Admission Details"
    ]

    # Create DataFrame
    df = pd.DataFrame(structured_data, columns=columns)

    # Remove rows that have "RANK" as the value in the "Rank" column
    df = df[df["Rank"].str.upper() != "RANK"]

    return df

# Streamlit interface
st.title("Admissions Data Parser (PDF Support)")

uploaded_file = st.file_uploader("Upload your admissions PDF file", type=["pdf"])

if uploaded_file is not None:
    # Parse the uploaded PDF file
    df = parse_admissions_data_from_pdf(uploaded_file)

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
