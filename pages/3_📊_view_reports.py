import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json 

st.set_page_config(layout="wide", page_title="View Reports", page_icon="💬")

# Set up credentials to access the Google Sheet
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
cred = json.loads(st.secrets['sheets_cred'], strict=False)
credentials = ServiceAccountCredentials.from_json_keyfile_dict(cred, scope)
gc = gspread.authorize(credentials)
spreadsheet = gc.open_by_key(st.secrets['rockwood_sheet'])

def get_reports_as_dataframe():
    global spreadsheet
    worksheet = spreadsheet.worksheet('reports')
    records = worksheet.get_all_records()
    df = pd.DataFrame(records)
    
    # Split the columns with '|||' delimiter
    df['questions'] = df['questions'].apply(lambda x: x.split('|||'))
    df['answers'] = df['answers'].apply(lambda x: x.split('|||'))
    df['blocked_questions'] = df['blocked_questions'].apply(lambda x: x.split('|||'))
    
    return df

def display_report(df_filtered):
    for idx, row in df_filtered.iterrows():
        st.subheader(f"Student ID: {row['student_id']}")
        st.write(f"Assignment: {row['assignment_name']}")
        st.write(f"Questions: {row['questions']}")
        st.write(f"Answers: {row['answers']}")
        st.write(f"Blocked Questions: {row['blocked_questions']}")
        st.write("-----")

def main():
    st.header("View Reports")

    df_reports = get_reports_as_dataframe()
    student_ids = df_reports['student_id'].unique().tolist()

    filter_by = st.selectbox("Filter by", ["Student ID", "All"])
    if filter_by == "Student ID":
        selected_student_id = st.selectbox("Select Student ID", student_ids)
        df_filtered = df_reports[df_reports['student_id'] == selected_student_id]
    else:
        df_filtered = df_reports

    display_report(df_filtered)

main()
