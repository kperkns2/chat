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

# Load the prompts
prompt_assignment = spreadsheet.worksheet('take_assignment_prompt')
str_prompt = prompt_assignment.cell(1, 2).value
first_assistant_message = prompt_assignment.cell(2, 2).value
bool_focus = prompt_assignment.cell(3, 2).value

# Load all assignements
def get_assignments_as_dataframe():
    global spreadsheet
    worksheet = spreadsheet.worksheet('assignments')
    # Get all records from the worksheet
    records = worksheet.get_all_records()
    # Convert the records to a pandas DataFrame
    df = pd.DataFrame(records)
    return df
df_assignments = get_assignments_as_dataframe()
assignment_names = df_assignments['assignment_name'].unique().tolist()

# Select the assignment
#placeholder = st.empty()
#with placeholder.container():
#  chatbot_select(items=assignment_names, answer_name='assignment_name', prefix='ca_')


st.session_state['assignment_name'] = 'Civil War Quiz'


# Run the assignment
if 'assignment_name' in st.session_state:
  placeholder.empty()
  df_current_assignment = df_assignments[df_assignments['assignment_name'] == st.session_state['assignment_name']]
  assignment_questions = df_current_assignment['question_text'].tolist()
  str_prompt = str_prompt.format(assignment_questions)
  chatbot(spreadsheet, bool_focus, first_assistant_message, str_prompt, prefix='student_')
