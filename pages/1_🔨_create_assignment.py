import streamlit as st
st.set_page_config(layout="wide",page_title="Create assignment",page_icon="💬")

import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json
from chatbot import chatbot
import random

scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
cred = json.loads(st.secrets['sheets_cred'], strict=False)
credentials = ServiceAccountCredentials.from_json_keyfile_dict(cred, scope)
gc = gspread.authorize(credentials)
spreadsheet = gc.open_by_key(st.secrets['rockwood_sheet'])

@st.cache_data
def load_prompt():
  # Prompts are stored in Google Sheet
  prompt_worksheet = spreadsheet.worksheet('create_assignment_prompt')
  str_prompt = prompt_worksheet.cell(1, 2).value
  first_assistant_message = prompt_worksheet.cell(2, 2).value
  bool_focus = prompt_worksheet.cell(3, 2).value
  hard_focus = prompt_worksheet.cell(4, 2).value
  return str_prompt, first_assistant_message, bool_focus, hard_focus
str_prompt, first_assistant_message, bool_focus, hard_focus = load_prompt()

if 'assignment_id' in st.session_state:
  st.header('Assignment Saved')
  st.write("Link to assignment: https://chatbox.streamlit.app/test_assignment/?assignment_id="+st.session_state['assignment_id'])
else:
  st.header('Create an Assignment')
  chatbot(bool_focus, 
    hard_focus,
    first_assistant_message, 
    str_prompt, 
    prefix='teacher_', 
    assistant_role='AI', 
    user_role='Teacher',
    spreadsheet=spreadsheet)
