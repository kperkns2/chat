import streamlit as st

st.set_page_config(layout="wide",page_title="Create assignment",page_icon="💬")

import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json
from functools import partial
from gspread_dataframe import set_with_dataframe

# Set up credentials to access the Google Sheet
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
cred = json.loads(st.secrets['sheets_cred'], strict=False)
credentials = ServiceAccountCredentials.from_json_keyfile_dict(cred, scope)

# Authorize and open the Google Sheet
gc = gspread.authorize(credentials)
spreadsheet = gc.open_by_key(st.secrets['rockwood_sheet'])

def fetch_assignments():
    worksheet = spreadsheet.worksheet('mls')
    data = worksheet.get_all_values()
    df = pd.DataFrame(data[1:])
    df.columns = data[0]
    return df

# Fetch saved assignments from the Google Sheet
if 'assignments_df' not in st.session_state:
  st.session_state['assignments_df'] = fetch_assignments()

def add_blank_question():
  new_row = pd.Series(['' for _ in range(len(st.session_state['assignment_df'].columns))], index=st.session_state['assignment_df'].columns)
  st.session_state['assignment_df'] = st.session_state['assignment_df'].append(new_row, ignore_index=True)

# Initialize assignment_df as an empty DataFrame with the same columns as assignments_df
if 'assignment_df' not in st.session_state:
  st.session_state['assignment_df'] = pd.DataFrame(columns=st.session_state['assignments_df'].columns)
  add_blank_question()

st.title("New assignment")

def make_grid(cols, rows):
    grid = [0] * cols
    for i in range(cols):
        with st.container():
            grid[i] = st.columns(rows)
    return grid

def edit_callback(row_index):
    st.write(f"Editing row {row_index}")

def duplicate_callback(row_index):
    row_data = st.session_state['assignments_df'].loc[row_index].copy()
    st.session_state['assignments_df'] = st.session_state['assignments_df'].append(row_data, ignore_index=True)
    st.session_state['assignments_df'] = st.session_state['assignments_df'].reset_index(drop=True)
    st.experimental_rerun()

def delete_callback(row_index):
    st.session_state['assignment_df'] = st.session_state['assignment_df'].drop(row_index).reset_index(drop=True)
    st.experimental_rerun()

def add_to_assignment_callback(row_index):
    global filtered_assignments_df
    row_data = filtered_assignments_df.loc[row_index]
    st.session_state['assignment_df'] = st.session_state['assignment_df'].append(row_data, ignore_index=True)
    st.write(f"Added row {row_index} to assignment")

def delete_and_save_to_sheet(tab_name, dataframe):
    """
    Deletes all data in a Google Spreadsheet tab and saves a Pandas DataFrame to that same tab.

    :param credentials: Google API credentials
    :param sheet_key: Google Sheet key
    :param tab_name: Name of the tab in the Google Sheet
    :param dataframe: Pandas DataFrame to be saved to the Google Sheet
    """

    try:
        worksheet = spreadsheet.worksheet(tab_name)
    except gspread.exceptions.WorksheetNotFound:
        # Create a new worksheet with the specified name if it doesn't exist
        worksheet = spreadsheet.add_worksheet(title=tab_name, rows=dataframe.shape[0], cols=dataframe.shape[1])

    # Clear all data in the worksheet
    worksheet.clear()

    # Save the DataFrame to the cleared worksheet
    set_with_dataframe(worksheet, dataframe)

def save_assignment():
  final_assignment = st.session_state['assignment_df']
  final_assignment = final_assignment[final_assignment['Question'].str.len()!=0]
  delete_and_save_to_sheet('temp_assignment', final_assignment)


# Create the assignment grid
assignment_grid = make_grid(len(st.session_state['assignment_df']), 2)

for index, row in st.session_state['assignment_df'].iterrows():
    # Create tabs for each row
    with assignment_grid[index][0]:
        t1, t2, t3, t4 = st.tabs(['Question', 'Hint', 'Answer', 'MLS Description'])
        with t1:
            question_input = st.text_area(f"Question {index}", row['Question'], key=f'question_{index}', label_visibility='hidden')        
        with t2:
            hint_input = st.text_area(f"Hint {index}", row['Hint'], key=f'hint_{index}', label_visibility='hidden')
        with t3:
            answer_input = st.text_area(f"Answer {index}", row['Answer'], key=f'answer_{index}', label_visibility='hidden')
        with t4:
            mls_input = st.text_area(f"MLS Description {index}", row['MLS Description'], key=f'mls_{index}', label_visibility='hidden')
    with assignment_grid[index][1]:
      for i in range(8):
        st.write('')
      delete_button = st.button("Delete", on_click=partial(delete_callback, index), key=f'delete_{index}')

bt1,bt2 = st.columns(6)[:2]

with bt1:
  if st.button('Add Question'):
    add_blank_question()
with bt2:
  if st.button('Save assignment'):
    save_assignment()


#### Available Questions Grid
st.header('Available Questions')
search_string = st.text_input("Search for questions:")
if len(search_string) > 0:
  filtered_assignments_df = st.session_state['assignments_df'][st.session_state['assignments_df']['Question'].str.contains(search_string)]
else:
  filtered_assignments_df = st.session_state['assignments_df']

filtered_assignments_df = filtered_assignments_df.query("Question != 'NA'")
questions_grid = make_grid(len(filtered_assignments_df), 2)
filtered_assignments_df = filtered_assignments_df.reset_index(drop=True)

for index, row in filtered_assignments_df.iterrows():
    # Create tabs for each row
    with questions_grid[index][0]:
        t1, t2, t3, t4 = st.tabs(['Question', 'Hint', 'Answer', 'MLS Description'])
        with t1:
            question_input = st.text_area(f"Question {index}", row['Question'], key=f'base_question_{index}', label_visibility='hidden')        
        with t2:
            hint_input = st.text_area(f"Hint {index}", row['Hint'], key=f'base_hint_{index}', label_visibility='hidden')
        with t3:
            answer_input = st.text_area(f"Answer {index}", row['Answer'], key=f'base_answer_{index}', label_visibility='hidden')
        with t4:
            mls_input = st.text_area(f"MLS Description {index}", row['MLS Description'], key=f'base_mls_{index}', label_visibility='hidden')

    with questions_grid[index][1]:
      for i in range(8):
        st.write('')
      add_to_assignment_button = st.button("Add", on_click=partial(add_to_assignment_callback, index), key=f'add_{index}')


_ = """for index, row in filtered_assignments_df.iterrows():
    question_input = mygrid[index][0].text_area(f"Question {index}", row['Question'], label_visibility='hidden')
    hint_input = mygrid[index][1].text_area(f"Hint {index}", row['Hint'], label_visibility='hidden')
    answer_input = mygrid[index][2].text_area(f"Answer {index}", row['Answer'], label_visibility='hidden')

    #edit_button = mygrid[index][3].button("Edit", on_click=partial(edit_callback, index))
    #duplicate_button = mygrid[index][4].button("Duplicate", on_click=partial(duplicate_callback, index))
    #delete_button = mygrid[index][5].button("Delete", on_click=partial(delete_callback, index))
    add_to_assignment_button = mygrid[index][3].button("Add", on_click=partial(add_to_assignment_callback, index), key=f'add_{index}')"""
