import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json 
import matplotlib.pyplot as plt

st.set_page_config(layout="wide", page_title="View Reports", page_icon="💬")

# Set up credentials to access the Google Sheet
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
cred = json.loads(st.secrets['sheets_cred'], strict=False)
credentials = ServiceAccountCredentials.from_json_keyfile_dict(cred, scope)
gc = gspread.authorize(credentials)
spreadsheet = gc.open_by_key(st.secrets['rockwood_sheet'])

def get_reports_as_dataframe():
    global spreadsheet
    worksheet = spreadsheet.worksheet('responses')
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



def plot_help_percentage(df_reports):
    # Count the number of students who needed help for each question
    help_counts = df_reports[df_reports['needed_help'] == True].groupby('questions')['needed_help'].count()
    
    # Count the total number of students for each question
    total_counts = df_reports.groupby('questions')['needed_help'].count()
    
    # Calculate the percentage of students needing help for each question
    help_percentage = (help_counts / total_counts) * 100
    
    # Plot the bar graph
    help_percentage.plot(kind='bar', figsize=(15, 6), color='#1F77B4')
    plt.xlabel('Questions')
    plt.ylabel('Percentage of Students Needing Help')
    plt.title('Percentage of Students Needing Help per Question')
    plt.xticks(rotation=45, ha='right')
    plt.show()


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
    plot_help_percentage(df_reports)


main()
