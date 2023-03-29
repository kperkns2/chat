import streamlit as st
st.set_page_config(layout="wide")
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json
from functools import partial

# Set up credentials to access the Google Sheet
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
cred = json.loads(st.secrets['sheets_cred'], strict=False)
credentials = ServiceAccountCredentials.from_json_keyfile_dict(cred, scope)

# Authorize and open the Google Sheet
gc = gspread.authorize(credentials)
spreadsheet = gc.open_by_key(st.secrets['rockwood_sheet'])

def fetch_scenarios():
    worksheet = spreadsheet.worksheet('mls')
    data = worksheet.get_all_values()
    df = pd.DataFrame(data[1:])
    df.columns = data[0]
    return df

# Fetch saved scenarios from the Google Sheet
if 'scenarios_df' not in st.session_state:
  st.session_state['scenarios_df'] = fetch_scenarios()

# Initialize assignment_df as an empty DataFrame with the same columns as scenarios_df
if 'assignment_df' not in st.session_state:
  st.session_state['assignment_df'] = pd.DataFrame(columns=st.session_state['scenarios_df'].columns)



st.title("Create a new scenario")
st.write("Here is where you add questions to a new chat scenario.")



search_string = st.text_input("Search for questions:")

def make_grid(cols, rows):
    grid = [0] * cols
    for i in range(cols):
        with st.container():
            grid[i] = st.columns(rows)
    return grid

def edit_callback(row_index):
    st.write(f"Editing row {row_index}")

def duplicate_callback(row_index):
    row_data = st.session_state['scenarios_df'].loc[row_index].copy()
    st.session_state['scenarios_df'] = st.session_state['scenarios_df'].append(row_data, ignore_index=True)
    st.session_state['scenarios_df'] = st.session_state['scenarios_df'].reset_index(drop=True)
    st.experimental_rerun()

def delete_callback(row_index):
    st.session_state['assignment_df'] = st.session_state['assignment_df'].drop(row_index).reset_index(drop=True)
    st.experimental_rerun()

def add_to_assignment_callback(row_index):
    row_data = st.session_state['scenarios_df'].loc[row_index]
    st.session_state['assignment_df'] = st.session_state['assignment_df'].append(row_data, ignore_index=True)
    st.write(f"Added row {row_index} to assignment")


if len(search_string) > 0:
  filtered_scenarios_df = st.session_state['scenarios_df'][st.session_state['scenarios_df']['Question'].str.contains(search_string)]
else:
  filtered_scenarios_df = st.session_state['scenarios_df']



assignment_grid = make_grid(len(filtered_scenarios_df), 4)
for index, row in filtered_scenarios_df.iterrows():
    question_input = assignment_grid[index][0].text_area(f"Question {index}", row['Question'], label_visibility='hidden')
    hint_input = assignment_grid[index][1].text_area(f"Hint {index}", row['Hint'], label_visibility='hidden')
    answer_input = assignment_grid[index][2].text_area(f"Answer {index}", row['Answer'], label_visibility='hidden')

    #edit_button = assignment_grid[index][3].button("Edit", on_click=partial(edit_callback, index))
    #duplicate_button = assignment_grid[index][4].button("Duplicate", on_click=partial(duplicate_callback, index))
    delete_button = assignment_grid[index][3].button("Delete", on_click=partial(delete_callback, index), key=f'delete_{index}')
    #add_to_assignment_button = assignment_grid[index][3].button("Add", on_click=partial(add_to_assignment_callback, index), key=f'add_{index}')


if st.button('Add Question'):
  st.session_state['assignment_df'] = st.session_state['assignment_df'].append(['']*len(st.session_state['assignment_df'].columns()), ignore_index=True)


st.header('Available Questions')

mygrid = make_grid(len(filtered_scenarios_df), 4)
for index, row in filtered_scenarios_df.iterrows():
    question_input = mygrid[index][0].text_area(f"Question {index}", row['Question'], label_visibility='hidden')
    hint_input = mygrid[index][1].text_area(f"Hint {index}", row['Hint'], label_visibility='hidden')
    answer_input = mygrid[index][2].text_area(f"Answer {index}", row['Answer'], label_visibility='hidden')

    #edit_button = mygrid[index][3].button("Edit", on_click=partial(edit_callback, index))
    #duplicate_button = mygrid[index][4].button("Duplicate", on_click=partial(duplicate_callback, index))
    #delete_button = mygrid[index][5].button("Delete", on_click=partial(delete_callback, index))
    add_to_assignment_button = mygrid[index][3].button("Add", on_click=partial(add_to_assignment_callback, index), key=f'add_{index}')
