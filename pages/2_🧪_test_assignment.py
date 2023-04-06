import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json 
from chatbot import chatbot, chatbot_select
st.set_page_config(layout="wide",page_title="Test assignment",page_icon="💬")


# Set up credentials to access the Google Sheet
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
cred = json.loads(st.secrets['sheets_cred'], strict=False)
credentials = ServiceAccountCredentials.from_json_keyfile_dict(cred, scope)
gc = gspread.authorize(credentials)
spreadsheet = gc.open_by_key(st.secrets['rockwood_sheet'])


# Load all assignements
def get_assignments_as_dataframe(key='assignments'):
    global spreadsheet
    worksheet = spreadsheet.worksheet(key)
    # Get all records from the worksheet
    records = worksheet.get_all_records()
    # Convert the records to a pandas DataFrame
    df = pd.DataFrame(records)
    return df


def main():
  st.header('Education AI')

  ### Check if the assignment is one of the preset activities
  qp = st.experimental_get_query_params()
  if 'assignment_id' in qp:
    assignment_id = str(qp['assignment_id'][0]).zfill(3)
    if len(assignment_id) == 3:
      df_activities = get_assignments_as_dataframe(key='activities')
      df_activities['assignment_id'] = df_activities['assignment_id'].apply(lambda i: str(i).zfill(3))
      df_activities = df_activities[df_activities['assignment_id'] == assignment_id].iloc[0]
      course,topic,subtopic,focus,hard_guardrail,prompt,first_message,assignment_id = df_activities
      chatbot(focus, hard_guardrail, first_message, prompt, prefix='activity_' )
      return 


  # Load the prompts
  prompt_assignment = spreadsheet.worksheet('take_assignment_prompt')
  str_prompt = prompt_assignment.cell(1, 2).value
  first_assistant_message = prompt_assignment.cell(2, 2).value
  bool_focus = prompt_assignment.cell(3, 2).value
  hard_focus = prompt_assignment.cell(4, 2).value


  df_assignments = get_assignments_as_dataframe()
  assignment_names = df_assignments['assignment_name'].unique().tolist()

  # Select the assignment
  #placeholder = st.empty()
  #with placeholder.container():
  #  chatbot_select(items=assignment_names, answer_name='assignment_name', prefix='ca_')
  #   #placeholder.empty() make sure to add this once the assignment name is set

  qp = st.experimental_get_query_params()
  if 'assignment_id' in qp:
    assignment_id = str(qp['assignment_id'][0]).zfill(7)
    df_assignments['assignment_id'] = df_assignments['assignment_id'].apply(lambda i: str(i).zfill(7))
    tmp = df_assignments[df_assignments['assignment_id'] == assignment_id]
    st.session_state['assignment_name'] = tmp['assignment_name'].unique()[0]
    st.session_state['assignment_id'] = assignment_id
  else:
    st.session_state['assignment_name'] = 'Civil War Quiz'
    st.session_state['assignment_id'] = '-1'


  # Run the assignment
  if 'assignment_name' in st.session_state:

    df_current_assignment = df_assignments[df_assignments['assignment_name'] == st.session_state['assignment_name']]
    assignment_questions = df_current_assignment['question_text'].tolist()
    str_prompt = str_prompt.format(assignment_questions)
    
    chatbot(bool_focus, 
      hard_focus, 
      first_assistant_message, 
      str_prompt, 
      prefix='student_', 
      spreadsheet=spreadsheet, 
      assignment_id=assignment_id, 
      assignment_name=assignment_name)

main()
