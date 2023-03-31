import streamlit as st
import pandas as pd
import openai
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json 
st.set_page_config(layout="wide",page_title="Test assignment",page_icon="💬")
from chatbot import chatbot, chatbot_answer

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


def create_question_name_column(df_assignments):
    grouped = df_assignments.groupby('assignment_name')
    def generate_question_name(group):
        group['question_name'] = group['assignment_name'] + ' - Question ' + (group.reset_index().index + 1).astype(str)
        return group
    df_assignments = grouped.apply(generate_question_name)
    return df_assignments


df_assignments = get_assignments_as_dataframe()
assignment_names = df_assignments['assignment_name'].unique().tolist()
assignment_string = '\n\n'.join([(f"{i} {n}") for i,n in enumerate(df_assignments['assignment_name'].unique().tolist())])
df_assignments = create_question_name_column(df_assignments)
assignment_name_to_count = str(df_assignments.groupby('assignment_name')['question_text'].count())
question_name_to_question = dict(df_assignments[['question_name','question_text']].values)

import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json
from functools import partial
from gspread_dataframe import set_with_dataframe


bool_focus = 'FALSE'
first_assistant_message = """Hi are you ready to talk about the assignment? To begin, can you please pick one from the list?


""" + assignment_string

str_prompt = f"""You are a chatbot that helps students with assignment questions. First you copy and paste the question from the pandas dataframe that was provide to you. 
If they do not answer correctly, first give them a small hint. Do not answer right away.
After they guess you may give them the correct answer.

Step 0
  - Store this dataframe in memory: df_assignments = {df_assignments}

Step 1
  - Briefly greet the student
  - Ask the student to pick a quiz
  - Wait for a response

Step 2
  - In df_assignments find the question named "ASSIGNMENT_NAME - Question 1" replacing ASSIGNMENT_NAME with the name of the assignment
  - Extract the question text from df_assignments by filtering on 'question_name' and selecting the 'question_text' column 
  - Ask the question to the user exactly as it appears in the DataFrame
  - Wait for a response

Step 3
  - If the student correctly answers go on to the next question in quiz_dataframe "ASSIGNMENT_NAME - Question 2" etc...
  - If the student does not answer correctly 
    - Think of a hint that gives a bit more information, but does not answer the original question.
    - Give them a hint
  - If the student makes multiple failed attempts, give them the answer 
  - Wait for a response - iterate on the questions

Definition of hint - A small amount of information, but not enough to be considered a complete answer. 


"""


# chatbot(spreadsheet, bool_focus, first_assistant_message, str_prompt, prefix='student_', replace=question_name_to_question)

str_prompt = "You give the user a list of options. They pick one, although they don't have to type it exactly. You repeat their choice exactly as it appears in the list. Return the answer inside 3 backticks such as ```answer``` If they don't pick then politely encourage them to pick one"
first_assistant_message = "Please select one of these ['0 Red Apple','1 Banana','2 Orange']"
chatbot_answer(bool_focus, first_assistant_message, str_prompt, answer_name='fruit', prefix='ca_')

if 'fruit' in st.session_state:
  st.write(st.session_state['fruit'])
