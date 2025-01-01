import streamlit as st
import pandas as pd
import re
from PyPDF2 import PdfReader

# Function to parse the PDF and extract data
def parse_pdf(file):
    data = []
    college_code, college_name, course_code, course_name = None, None, None, None

    # Read the PDF pages
    for page in PdfReader(file).pages:
        text = page.extract_text()

        lines = text.splitlines()

        for line in lines:
            # Identify college details
            if line.startswith("COLL ::"):
                match = re.match(r"COLL :: (\S+) - (.+)", line)
                if match:
                    college_code = match.group(1)
                    college_name = match.group(2)

            # Identify course details
            elif line.startswith("CRS ::"):
                match = re.match(r"CRS :: (\S+) - (.+)", line)
                if match:
                    course_code = match.group(1)
                    course_name = match.group(2)

            # Identify student details
            elif re.match(r"^\d{3,}\s+\d{11}\s+", line):
                fields = re.split(r"\s{3,}", line)

                if len(fields) >= 8:
                    rank = fields[0]
                    roll_number = fields[1]
                    percentile = fields[2]
                    candidate_name = fields[3]
                    location = fields[4]
                    category = fields[5]
                    sex = fields[6]
                    minority = fields[7] if fields[7] not in ["", "PHO"] else ""
                    ph = "PHO" if "PHO" in fields else ""
                    admission_details = fields[-1]

                    data.append([
                        college_code,
                        college_name,
                        course_code,
                        course_name,
                        rank,
                        roll_number,
                        percentile,
                        candidate_name,
                        location,
                        category,
                        sex,
                        minority,
                        ph,
                        admission_details,
                    ])

    return pd.DataFrame(
        data,
        columns=[
            "College Code",
            "College Name",
            "Course Code",
            "Course Name",
            "Rank",
            "Roll Number",
            "Percentile",
            "Candidate Name",
            "Location",
            "Category",
            "Sex",
            "Minority",
            "PH",
            "Admission Details",
        ],
    )

# Streamlit App
st.title("PDF Data Extractor")

uploaded_file = st.file_uploader("Upload PDF File", type="pdf")

if uploaded_file:
    st.write("Processing the file...")
    extracted_data = parse_pdf(uploaded_file)

    if not extracted_data.empty:
        st.write("### Extracted Data")
        st.dataframe(extracted_data)

        # Option to download the data
        csv = extracted_data.to_csv(index=False)
        st.download_button(
            label="Download Data as CSV",
            data=csv,
            file_name="extracted_data.csv",
            mime="text/csv",
        )
    else:
        st.write("No valid data found in the PDF.")
