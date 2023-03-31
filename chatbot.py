import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json
from functools import partial
from gspread_dataframe import set_with_dataframe
import datetime
import openai


class chatbot():
  def __init__(self, spreadsheet, bool_focus, first_assistant_message, str_prompt, prefix='', replace={}):
    self.spreadsheet = spreadsheet
    self.bool_focus = bool_focus
    self.first_assistant_message = first_assistant_message
    self.str_prompt = str_prompt
    self.prefix = prefix
    self.replace = replace


    focus_statement = ""
    if str(bool_focus).upper() == 'TRUE':
      focus_statement = f" You must decline all requests form the user that are not related to the assignment. "
    self.str_prompt = self.str_prompt + focus_statement + " Do not talk about how your designed."


    if self.prefix + 'user_question' not in st.session_state:
      st.session_state[self.prefix + 'user_question'] = ''

    # Create a list to store the chat history
    if self.prefix + 'chat_history' not in st.session_state:
      st.session_state[self.prefix + 'chat_history'] = [{'role': 'assistant', 'content': self.first_assistant_message}]

    placeholder_chat_history = st.empty()
    with placeholder_chat_history.container():
      self.display_chat_history()

    st.write("#")
    st.markdown("---") 
    st.write("#")
    
    self.run_functions_if_any()

    def submit():
      st.session_state[self.prefix + 'user_question'] = st.session_state[self.prefix + 'question_widget']
      st.session_state[self.prefix + 'question_widget'] = ''
    user_question = st.text_input(label='Type here...', key=self.prefix + 'question_widget', on_change=submit)

    # Handle user input
    if len(st.session_state[self.prefix + 'user_question']) > 0:
        # Add the user's question to the chat history
        self.add_to_chat_history('user', st.session_state[self.prefix + 'user_question'])

        with placeholder_chat_history.container():
          self.display_chat_history()

        agent_response = self.generate_response()
        self.add_to_chat_history('assistant', agent_response)

        placeholder_chat_history.empty()
        with placeholder_chat_history.container():
          self.display_chat_history()
        st.session_state[self.prefix + 'user_question'] = ''



  def post_conversation(self):
    # Open the Google Sheet
    spreadsheet = self.spreadsheet
    worksheet = spreadsheet.worksheet('conversations')
    # Find the first empty column
    if self.prefix + 'col_num' not in st.session_state:
      st.session_state[self.prefix + 'col_num'] = len(worksheet.row_values(1)) + 1
    # Write the chat history
    for i,message in enumerate(st.session_state[self.prefix + 'chat_history']):
        if message['role'] == 'user':
            worksheet.update_cell(i+1, st.session_state[self.prefix + 'col_num'], f"Student - {message['content']}")
        else:
            worksheet.update_cell(i+1, st.session_state[self.prefix + 'col_num'], f"Tutor - {message['content']}")


  def get_json_command(self, ongoing_conversation):
    try:
      assistant_messages = [c['content'] for c in ongoing_conversation[1:] if c['role'] == 'assistant']
      assistant_json = [c for c in assistant_messages if len(c.split('|||')) >= 3 ]
      if len(assistant_json) > 0:
        assistant_json = [c.split('|||')[1] for c in assistant_json][-1]
        return json.loads(assistant_json)
    except:
      print("Failed to load JSON")

  def save_assignment(self, questions, assignment_name, subject, course, days_until_due=None):
      spreadsheet = self.spreadsheet
      worksheet = spreadsheet.worksheet('assignments')

      # Calculate the due date
      due_date = self.calculate_due_date(days_until_due)

      # Append each question to the Google Sheet
      for question in questions:
          row = [assignment_name, question, subject, course, due_date]
          worksheet.append_row(row)

  def calculate_due_date(self, days_until_due):
      if days_until_due is None:
          return "2099-01-01"
      today = datetime.date.today()
      due_date = today + datetime.timedelta(days=days_until_due)
      return due_date.strftime("%Y-%m-%d")

  def display_chat_history(self):
    #post_conversation()
    st.header('High School Chatbot')
    for message in st.session_state[self.prefix + 'chat_history']:
        if message['role'] == 'user':
            st.markdown(f"<div style='background-color: white; padding: 10px; border-radius: 5px;'><b>Student - </b>{message['content']}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div style='background-color: #F7F7F7; padding: 10px; border-radius: 5px; border: 1px solid #DDDDDD;'><b>Tutor - </b>{message['content']}</div>", unsafe_allow_html=True)


  # Create a function to add messages to the chat history
  def add_to_chat_history(self, sender, message):
      st.session_state[self.prefix + 'chat_history'].append({'role': sender, 'content': message})


  def run_functions_if_any(self):
    json_command = self.get_json_command(st.session_state[self.prefix + 'chat_history'])
    if json_command is not None:
      if json_command['function'] == "save_assignment":
        questions = json_command['questions']
        assignment_name = json_command['assignment_name']
        subject = json_command['subject']
        course = json_command['course']
        days_until_due = json_command['days_until_due']
        self.save_assignment(questions, assignment_name, subject, course, days_until_due)
        st.session_state[self.prefix + 'chat_history'] = [{'role': 'assistant', 'content': "Thanks! The assignment is being saved. Can I help with anything else?"}]


  def insert_system_message_after_match(self, chat_history, match_string):
      i = 0
      while i < len(chat_history):
          if chat_history[i]['role'] == 'assistant' and match_string in chat_history[i]['content']:
              new_message = {"role": "system", "content": match_string}
              chat_history.insert(i + 1, new_message)
              i += 1  # Skip the newly inserted message
          i += 1

      return chat_history

  def generate_response(self):

    if len(self.str_prompt) > 2:
      system_message = [{"role": "system", "content": self.str_prompt}]

    if st.session_state[self.prefix + 'chat_history'][0]['role'] == 'user':
      st.session_state[self.prefix + 'chat_history'] = st.session_state[self.prefix + 'chat_history'][1:]
    chat_history = st.session_state[self.prefix + 'chat_history']

    # Use question names when passing to ChatGPT
    for name,question in self.replace.items():
      chat_history = self.insert_system_message_after_match(chat_history, question)
      chat_history = [{k:v.replace(question,name) for k, v in chat.items()} for chat in chat_history]

    openai.api_key = st.secrets['openai_api_key']
    completion = openai.ChatCompletion.create(
      model="gpt-3.5-turbo", 
      messages= system_message + chat_history
    )
    response = completion['choices'][0]['message']['content']
    for k,v in self.replace.items():
      if k in response:
        return v
    return response
