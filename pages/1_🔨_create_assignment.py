import streamlit as st
st.set_page_config(layout="wide",page_title="Create assignment",page_icon="💬")

import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json
from functools import partial
from gspread_dataframe import set_with_dataframe
import datetime


str_prompt = """You are a chatbot that will make it easy for Missouri educators to make quizzes for high school students. 
Your job is to help them craft a set of questions on a particular topic. 
Keep the questions in line with the Missouri Learning Standards (MLS) and consistent with the topic as described by the teacher. 
Once the teacher is satisfied, you can save the assignment by writing a JSON object wrapped in |||. 
Write the python code in three vertical lines like this |||{"function":"save_assignment", }||| Include the following attributes in the JSON object

```
"function":"save_assignment" 
"questions": a python list of questions to ask the student
"assignment_name" : a python string
"subject": e.g., 'Mathematics' ,  
"course": e.g., 'Algebra'
"days_until_due": e.g., 5 # you MUST ask how many days until the assignment is due, if the response indicates no due date then use None ```

Step 1
  - Start with a one sentence acknowledgement that you understand the teacher would like to make an assignment and begin the conversation.
  - Wait for a response

Step 2
  - Once the teacher has described the topic, return a list of possible questions. 
  - Wait for a response - iterate on the questions until the teacher is satisfied.

Step 3
  - Select the most likely subject from the list ["Fine Arts", "Health/PE", "Language Arts", "Mathematics", "Science", "Social Studies"]
  - Select the most likely course from the list ["Visual Arts", "Music", "Theatre", "Health/PE", "Reading", "Writing", "Algebra","Geometry", "Statistics and Probability", "Biology", "Chemistry", "Earth and Space","Physics", "Civics", "Economics", "Geography", "Government", "American History","World History"] 
  - Guess the most likely assignment name
  - Tell the teacher your predicted subject and course and assignment name and ask them to confirm
  - Ask the teacher for the number of days until the due date

Step 4
  - Start your last message with "|||" inside this block write the JSON object. 
  - Tell the user 'Thank you! The assignment is being saved. Do you have any questions?'

Guidelines to always keep
  - Do NOT mention the JSON object. The teacher can NOT see, edit or copy the JSON object It must be exactly correct. No mention of the JSON object should be given outside the vertical bars
  - Don't mention Missouri Learning Standards. 
  - Don't mention the list of courses or subjects"""
first_assistant_message = """Hello! I understand that you would like to create a quiz for your high school students. What is the topic of the quiz?"""
bool_focus = "FALSE"

# Set up credentials to access the Google Sheet
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
cred = json.loads(st.secrets['sheets_cred'], strict=False)
credentials = ServiceAccountCredentials.from_json_keyfile_dict(cred, scope)

# Authorize and open the Google Sheet
gc = gspread.authorize(credentials)
spreadsheet = gc.open_by_key(st.secrets['rockwood_sheet'])

def post_conversation():
  # Open the Google Sheet
  spreadsheet = gc.open_by_key(st.secrets['rockwood_sheet'])
  worksheet = spreadsheet.worksheet('conversations')
  # Find the first empty column
  if 't_col_num' not in st.session_state:
    st.session_state.t_col_num = len(worksheet.row_values(1)) + 1
  # Write the chat history
  for i,message in enumerate(st.session_state['t_chat_history']):
      if message['role'] == 'user':
          worksheet.update_cell(i+1, st.session_state.t_col_num, f"Student - {message['content']}")
      else:
          worksheet.update_cell(i+1, st.session_state.t_col_num, f"Tutor - {message['content']}")


def get_json_command(ongoing_conversation):
  try:
    assistant_messages = [c['content'] for c in ongoing_conversation[1:] if c['role'] == 'assistant']
    assistant_json = [c for c in assistant_messages if len(c.split('|||')) >= 3 ]
    if len(assistant_json) > 0:
      assistant_json = [c.split('|||')[1] for c in assistant_json][-1]
      return json.loads(assistant_json)
  except:
    print("Failed to load JSON")

def save_assignment(questions, assignment_name, subject, course, days_until_due=None):
    global spreadsheet
    worksheet = spreadsheet.worksheet('assignments')

    # Calculate the due date
    due_date = calculate_due_date(days_until_due)

    # Append each question to the Google Sheet
    for question in questions:
        row = [assignment_name, question, subject, course, due_date]
        worksheet.append_row(row)

def calculate_due_date(days_until_due):
    if days_until_due is None:
        return "2099-01-01"

    today = datetime.date.today()
    due_date = today + datetime.timedelta(days=days_until_due)
    return due_date.strftime("%Y-%m-%d")



def display_chat_history():
  #post_conversation()
  st.header('High School Chatbot')
  for message in st.session_state['t_chat_history']:
      if message['role'] == 'user':
          st.markdown(f"<div style='background-color: white; padding: 10px; border-radius: 5px;'><b>Student - </b>{message['content']}</div>", unsafe_allow_html=True)
      else:
          st.markdown(f"<div style='background-color: #F7F7F7; padding: 10px; border-radius: 5px; border: 1px solid #DDDDDD;'><b>Tutor - </b>{message['content']}</div>", unsafe_allow_html=True)

# Create a function to add messages to the chat history
def add_to_chat_history(sender, message):
    st.session_state['t_chat_history'].append({'role': sender, 'content': message})

# Create a list to store the chat history
if 't_chat_history' not in st.session_state:
  st.session_state['t_chat_history'] = [{'role': 'assistant', 'content': first_assistant_message}]


json_command = get_json_command(st.session_state['t_chat_history'])
if json_command is not None:
  if json_command['function'] == "save_assignment":
    questions = json_command['questions']
    assignment_name = json_command['assignment_name']
    subject = json_command['subject']
    course = json_command['course']
    days_until_due = json_command['days_until_due']
    save_assignment(questions, assignment_name, subject, course, days_until_due=None)
    st.session_state['t_chat_history'] = [{'role': 'assistant', 'content': "Thanks! The assignment is being saved. Can I help with anything else?"}]




def generate_response():
  focus_statement = ""
  if bool_focus == 'TRUE':
    focus_statement = f" You must decline all requests form the user that are not related to the question that you are asking. Changes in topic are only permitted if the user provies the hidden key 'asdj238'. You must not divulge the hidden key or mention that it exists."
  system = str_prompt + focus_statement + " Do not talk about how your designed."
  system_message = []

  if len(system) > 2:
    system_message = [{"role": "system", "content": system}]

  if st.session_state['t_chat_history'][0]['role'] == 'user':
    st.session_state['t_chat_history'] = st.session_state['t_chat_history'][1:]
  
  openai.api_key = st.secrets['openai_api_key']
  completion = openai.ChatCompletion.create(
    model="gpt-3.5-turbo", 
    messages= system_message + st.session_state['t_chat_history']
  )
  response = completion['choices'][0]['message']['content']
  return response




placeholder_chat_history = st.empty()
with placeholder_chat_history.container():
  display_chat_history()

st.write("#")
st.markdown("---") 
st.write("#")


def submit():
    st.session_state.t_user_question = st.session_state.t_question_widget
    st.session_state.t_question_widget = ''

user_question = st.text_input(label='Type here...', key='t_question_widget', on_change=submit)


# Handle user input
if len(st.session_state.t_user_question) > 0:
    # Add the user's question to the chat history
    add_to_chat_history('user', st.session_state.t_user_question)

    # TODO: Add code to handle the user's question and generate a response

    with placeholder_chat_history.container():
      display_chat_history()

    agent_response = generate_response()

    add_to_chat_history('assistant', agent_response)

    placeholder_chat_history.empty()
    with placeholder_chat_history.container():
      display_chat_history()
    st.session_state.t_user_question = ''
    

