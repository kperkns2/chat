import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json 
import plotly.graph_objects as go
import plotly.express as px

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
    df['assignment_id'] = df['assignment_id'].astype('str')
    
    # Split the columns with '|||' delimiter
    df['questions'] = df['questions'].apply(lambda x: x.split('|||'))
    df['answers'] = df['answers'].apply(lambda x: x.split('|||'))
    df['bool_hint'] = df['bool_hint'].apply(lambda x: x.split('|||'))
    df['blocked_questions'] = df['blocked_questions'].apply(lambda x: x.split('|||'))

    df = df.explode('questions')
    df = df.explode('answers')
    df = df.explode('bool_hint')

    df = df.reset_index().drop_duplicates(subset=['index','questions'])
    
    return df

def display_report(df_filtered):
    st.write(df_filtered)



def plot_help_percentage(df_reports):
    # Count the number of students who needed help for each question
    help_counts = df_reports[df_reports['bool_hint'] == True].groupby('questions')['bool_hint'].count()
    
    # Count the total number of students for each question
    total_counts = df_reports.groupby('questions')['bool_hint'].count()
    
    # Calculate the percentage of students needing help for each question
    help_percentage = (help_counts / total_counts) * 100

    print(help_percentage)
    
    # Create the bar graph using Plotly
    fig = go.Figure(data=[go.Bar(x=help_percentage.index, y=help_percentage.values, text=help_percentage.values, textposition='auto')])
    
    # Customize the appearance
    fig.update_layout(title='Percentage of Students Needing Help per Question',
                      xaxis_title='Questions',
                      yaxis_title='Percentage of Students Needing Help',
                      xaxis_tickangle=-45)
    
    # Show the graph in Streamlit
    st.plotly_chart(fig)



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
