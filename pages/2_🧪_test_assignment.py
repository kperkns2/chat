import streamlit as st
import pandas as pd
import openai
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json 
st.set_page_config(layout="wide",page_title="Test assignment",page_icon="💬")
from chatbot import chatbot

# Set up credentials to access the Google Sheet
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
cred = json.loads(st.secrets['sheets_cred'], strict=False)
credentials = ServiceAccountCredentials.from_json_keyfile_dict(cred, scope)

# Authorize and open the Google Sheet
gc = gspread.authorize(credentials)
spreadsheet = gc.open_by_key(st.secrets['rockwood_sheet'])


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
assignment_string = '\n\n'.join([(f"{i} {n}") for i,n in enumerate(df_assignments['assignment_name'].unique().tolist())])

import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json
from functools import partial
from gspread_dataframe import set_with_dataframe


bool_focus = 'TRUE'
first_assistant_message = """Hi are you ready to talk about the assignment? To begin, can you please pick one from the list?


""" + assignment_string

str_prompt = f"""You are a chatbot that helps students by asking them a series of study questions, and you have a dialog. 
If they do not answer correctly, first give them a small hint. Do not answer right away.
After they guess you may give them the correct answer.
Step 1
  - Briefly greet the student
  - Ask the student to pick a quiz
  - Wait for a response

Step 2
  - Say "Question 1" then ask the first question in the list
  - Wait for a response

Step 3
  - If the student correctly answers go on to the next question
  - If the student does not answer correctly 
    - Think of question 2 that gives a bit more information, but does not answer the original question.
    - Give them a hint in the form of question 2
  - If the student makes multiple failed attempts, give them the answer 
  - Wait for a response - iterate on the questions

Definition of hint - A small amount of information, but not enough to be considered a complete answer. 


Here are all the assignments {df_assignments}

"""


chatbot(spreadsheet, bool_focus, first_assistant_message, str_prompt, prefix='student_')
