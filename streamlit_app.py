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
    debug_logs = []  # Collect debug logs

    for line_number, line in enumerate(lines):
        line = line.strip()

        # Skip empty or dashed lines
        if not line or "-----" in line:
            debug_logs.append(f"Line {line_number}: Skipped empty or dashed line.")
            continue

        # Ensure data processing starts only after the first COLL section
        if line.startswith("COLL ::"):
            parts = line.split(" - ")
            current_college_code = parts[0].replace("COLL ::", "").strip()
            current_college_name = parts[1].strip() if len(parts) > 1 else ""
            processing_rows = True  # Start processing rows after COLL is found
            debug_logs.append(f"Line {line_number}: Identified COLL section: {current_college_code}, {current_college_name}")

        # Identify CRS sections
        elif line.startswith("CRS ::"):
            if processing_rows:  # Only process CRS if a COLL has been encountered
                parts = line.split(" - ")
                current_course_code = parts[0].replace("CRS ::", "").strip()
                current_course_name = parts[1].strip() if len(parts) > 1 else ""
                debug_logs.append(f"Line {line_number}: Identified CRS section: {current_course_code}, {current_course_name}")

        # Skip repeated headers
        elif line.lower().startswith("rank roll_no percentile candidate_name loc cat sx min ph adm details"):
            debug_logs.append(f"Line {line_number}: Skipped repeated header.")
            continue

        # Process student rows only if processing_rows is True
        elif processing_rows:
            parts = re.split(r'\s+', line)
            try:
                # Extract Rank (must be a number less than 300000)
                rank = parts[0]
                if not rank.isdigit() or int(rank) > 300000:
                    debug_logs.append(f"Line {line_number}: Invalid rank: {rank}")
                    continue

                # Extract Roll Number (11 digits starting with 24)
                roll_no = parts[1]
                if not re.match(r'^24\d{9}$', roll_no):
                    debug_logs.append(f"Line {line_number}: Invalid roll number: {roll_no}")
                    continue

                # Extract Percentile (a floating-point number)
                percentile = parts[2]
                if not re.match(r'^\d+\.\d+$', percentile):
                    debug_logs.append(f"Line {line_number}: Invalid percentile: {percentile}")
                    continue

                # Extract Candidate Name (letters only)
                candidate_name_parts = []
                for part in parts[3:]:
                    if part.upper() in ["OU", "BCA", "BCB", "BCD", "BCC", "BCE", "ST", "SC", "OC", "F", "M", "MSM", "PHO"]:
                        break
                    candidate_name_parts.append(part)
                candidate_name = " ".join(candidate_name_parts)

                # Extract Location (OU)
                loc = parts[3 + len(candidate_name_parts)]
                if loc != "OU":
                    debug_logs.append(f"Line {line_number}: Invalid location: {loc}")
                    continue

                # Extract Category (BCA, BCB, BCD, etc.)
                cat = parts[4 + len(candidate_name_parts)]
                if cat not in ["BCA", "BCB", "BCD", "BCC", "BCE", "ST", "SC", "OC"]:
                    debug_logs.append(f"Line {line_number}: Invalid category: {cat}")
                    continue

                # Extract Sex (F, M)
                sx = parts[5 + len(candidate_name_parts)]
                if sx not in ["F", "M"]:
                    debug_logs.append(f"Line {line_number}: Invalid sex: {sx}")
                    continue

                # Extract MIN (MSM or blank)
                min_status = parts[6 + len(candidate_name_parts)]
                if min_status not in ["MSM", ""]:
                    debug_logs.append(f"Line {line_number}: Invalid MIN: {min_status}")
                    continue

                # Extract PH (PHO or blank)
                ph = parts[7 + len(candidate_name_parts)]
                if ph not in ["PHO", ""]:
                    debug_logs.append(f"Line {line_number}: Invalid PH: {ph}")
                    continue

                # Extract Admission Details (remaining parts)
                adm_details = " ".join(parts[8 + len(candidate_name_parts):])

                # Append structured row
                structured_data.append([
                    current_college_code, current_college_name, 
                    current_course_code, current_course_name, 
                    rank, roll_no, percentile, candidate_name, loc, cat, sx, 
                    min_status, ph, adm_details
                ])
                debug_logs.append(f"Line {line_number}: Successfully parsed student data.")

            except Exception as e:
                debug_logs.append(f"Line {line_number}: Error processing row: {e}")
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

    return df, debug_logs

# Streamlit interface
st.title("Admissions Data Parser (PDF Support)")

uploaded_file = st.file_uploader("Upload your admissions PDF file", type=["pdf"])

if uploaded_file is not None:
    # Parse the uploaded PDF file
    df, debug_logs = parse_admissions_data_from_pdf(uploaded_file)

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

        # Display debug logs
        st.write("### Debug Logs")
        st.text("\n".join(debug_logs[:100]))  # Show first 100 debug logs for brevity
    else:
        st.error("No data extracted. Check the PDF format and content.")

        # Display debug logs
        st.write("### Debug Logs")
        st.text("\n".join(debug_logs[:100]))  # Show first 100 debug logs for brevity
