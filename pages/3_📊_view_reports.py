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

@st.cache_data()
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
    
    df['question_number'] = df['questions'].apply(lambda i: list(range(len(i))))
    df = df.explode('question_number')
    df['questions'] =  df[['questions','question_number']].apply(lambda i: i[0][i[1]],axis=1)
    df['answers'] =  df[['answers','question_number']].apply(lambda i: i[0][i[1]],axis=1)
    df['bool_hint'] =  df[['bool_hint','question_number']].apply(lambda i: i[0][i[1]],axis=1)
    df = df.drop('question_number', axis=1)
    #df = df.explode('questions')
    #df = df.explode('answers')
    #df = df.explode('bool_hint')
    #df = df.reset_index().drop_duplicates(subset=['index','questions'])
    
    return df

def display_report(df_filtered):
    df_tmp = df_filtered.copy()
    st.write(df_tmp.columns)
    df_tmp.columns = ['Questions','Answers','Hint Needed','assignment_id','assignment_name','student_id','Blocked Messages']
    df_tmp = df_tmp.reset_index(drop=True)
    st.dataframe(df_tmp)



def plot_help_percentage(df_reports):
    # Count the number of students who needed help for each question
    help_counts = df_reports[df_reports['bool_hint'].apply(lambda i: str(i).upper()) == 'TRUE'].groupby('questions')['bool_hint'].count()
    
    # Count the total number of students for each question
    total_counts = df_reports.groupby('questions')['bool_hint'].count()
    
    # Calculate the percentage of students needing help for each question
    help_percentage = ((help_counts / total_counts) * 100).round()
    
    # Create the bar graph using Plotly
    fig = go.Figure(data=[go.Bar(x=help_percentage.index, y=help_percentage.values, text=help_percentage.values, textposition='auto')])
    
    # Customize the appearance
    fig.update_layout(title='Percentage of Students Needing Help per Question',
                      xaxis_title='Questions',
                      yaxis_title='Percentage of Students Needing Help',
                      width=600,
                      height=1200,
                      xaxis_tickangle=-45)
    
    # Show the graph in Streamlit
    st.plotly_chart(fig)



def main():
    st.header("View Reports")

    df_reports = get_reports_as_dataframe()
    student_ids = df_reports['student_id'].unique().tolist()
    assignment_names = df_reports['assignment_name'].unique().tolist()
    selected_assignment = st.selectbox("Choose an assignemnt", assignment_names)

    df_filtered = df_reports[df_reports['assignment_name'] == selected_assignment]
    plot_help_percentage(df_filtered)


    filter_by = st.selectbox("Filter by", ["Student ID", "All"])
    if filter_by == "Student ID":
        selected_student_id = st.selectbox("Select Student ID", student_ids)
        df_filtered = df_filtered[df_filtered['student_id'] == selected_student_id]
    else:
        df_filtered = df_filtered

    
    display_report(df_filtered)
    


main()
