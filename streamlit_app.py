import streamlit as st
import pandas as pd
from PyPDF2 import PdfReader
import re

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
            processing_rows = True  # Start processing rows after COLL is found

        # Capture course details from CRS ::
        elif line.startswith("CRS ::"):
            if processing_rows:  # Only process CRS if a COLL has been encountered
                parts = line.split(" - ")
                current_course_code = parts[0].replace("CRS ::", "").strip()
                current_course_name = parts[1].strip() if len(parts) > 1 else ""

        # Skip repeated headers
        elif line.lower().startswith("rank roll_no percentile candidate_name loc cat sx min ph adm details"):
            continue

        # Process student rows only if processing_rows is True
        elif processing_rows:
            try:
                # Use regex to extract specific parts of the line
                rank_match = re.match(r"^(\d{1,6})\s", line)
                if not rank_match:
                    continue
                rank = rank_match.group(1)

                roll_no_match = re.search(r"(24\d{9})", line)
                if not roll_no_match:
                    continue
                roll_no = roll_no_match.group(1)

                percentile_match = re.search(r"(\d+\.\d+)", line[roll_no_match.end():])
                if not percentile_match:
                    continue
                percentile = percentile_match.group(1)

                candidate_name_start = roll_no_match.end() + len(percentile) + 1
                candidate_name_end = line.find("OU", candidate_name_start)
                if candidate_name_end == -1:
                    continue
                candidate_name = line[candidate_name_start:candidate_name_end].strip()

                loc = "OU"

                category_match = re.search(r"(BCA|BCB|BCD|BCC|BCE|ST|SC|OC)", line[candidate_name_end:])
                if not category_match:
                    continue
                cat = category_match.group(1)

                sex_match = re.search(r"(F|M)", line[category_match.end():])
                if not sex_match:
                    continue
                sx = sex_match.group(1)

                min_status_match = re.search(r"(MSM)?", line[sex_match.end():])
                min_status = min_status_match.group(1) if min_status_match else ""

                ph_match = re.search(r"(PHO)?", line[min_status_match.end():] if min_status_match else "")
                ph = ph_match.group(1) if ph_match else ""

                adm_details_match = re.search(r"(NS-|S-).*(-P1|-P2|-P3|-P4)$", line)
                if not adm_details_match:
                    continue
                adm_details = adm_details_match.group(0)

                # Append structured row
                structured_data.append([
                    current_college_code, current_college_name, 
                    current_course_code, current_course_name, 
                    rank, roll_no, percentile, candidate_name, loc, cat, sx, 
                    min_status, ph, adm_details
                ])
            except Exception as e:
                # Log the error and continue processing other lines
                print(f"Error processing line: {line}, Error: {e}")
                continue

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
