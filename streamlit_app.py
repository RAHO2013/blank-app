import streamlit as st
import pandas as pd
from PyPDF2 import PdfReader

def extract_college_course_details(file):
    # Read the uploaded PDF file
    reader = PdfReader(file)
    lines = []
    for page in reader.pages:
        extracted_text = page.extract_text()
        if extracted_text:
            lines.extend(extracted_text.splitlines())

    # Debugging: Print extracted lines
    print("Extracted Lines:")
    for line in lines:
        print(line)

    # Initialize variables
    college_course_data = []
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

            # Append the current college and course details
            college_course_data.append([
                current_college_code, current_college_name,
                current_course_code, current_course_name
            ])

    # Define DataFrame columns
    columns = ["College Code", "College Name", "Course Code", "Course Name"]

    # Create DataFrame
    df = pd.DataFrame(college_course_data, columns=columns)
    return df

# Streamlit interface
st.title("College and Course Details Extractor")

uploaded_file = st.file_uploader("Upload your admissions PDF file", type=["pdf"])

if uploaded_file is not None:
    # Extract college and course details
    df = extract_college_course_details(uploaded_file)

    if not df.empty:
        # Display the DataFrame
        st.write("### Extracted College and Course Details")
        st.dataframe(df)

        # Allow user to download the Excel file
        excel_file = "college_course_details.xlsx"
        df.to_excel(excel_file, index=False)
        with open(excel_file, "rb") as file:
            st.download_button(
                label="Download Excel File",
                data=file,
                file_name="college_course_details.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
    else:
        st.error("No data extracted. Check the PDF format and content.")
