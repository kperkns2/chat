import streamlit as st
st.set_page_config(layout="wide",page_title="Create assignment",page_icon="💬")

import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json
from functools import partial
from gspread_dataframe import set_with_dataframe
import datetime
import openai
from chatbot import chatbot



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
  - Think about how the JSON object will be structured and go through this checklist
    - Does the question list have one element for every question? If not, fix it.
    - Has the teacher confirmed the subject, course and assignment name? If not, ask. 
    - Has the teacher provided a number of days until due (Or did they say 'no due date')? If not, ask. 

Step 5
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



chatbot(spreadsheet, bool_focus, first_assistant_message, str_prompt, prefix='teacher_')
