import streamlit as st
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
scenarios_df = fetch_scenarios()

st.title("Chat Scenarios")
st.write("Here's a list of your saved chat scenarios:")

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
    global scenarios_df
    row_data = scenarios_df.loc[row_index].copy()
    scenarios_df = scenarios_df.append(row_data, ignore_index=True)
    scenarios_df = scenarios_df.reset_index(drop=True)
    st.experimental_rerun()

def delete_callback(row_index):
    global scenarios_df
    scenarios_df = scenarios_df.drop(row_index).reset_index(drop=True)
    st.experimental_rerun()

def add_to_assignment_callback(row_index):
    global assignment_df
    row_data = scenarios_df.loc[row_index]
    assignment_df = assignment_df.append(row_data, ignore_index=True)
    st.write(f"Added row {row_index} to assignment")

# Initialize assignment_df as an empty DataFrame with the same columns as scenarios_df
assignment_df = pd.DataFrame(columns=scenarios_df.columns)

if len(search_string) > 0:
  filtered_scenarios_df = scenarios_df[scenarios_df['Question'].str.contains(search_string)]
else:
  filtered_scenarios_df = scenarios_df
mygrid = make_grid(len(filtered_scenarios_df), 7)

for index, row in filtered_scenarios_df.iterrows():
    question_input = mygrid[index][0].text_input(f"Question {index}", row['Question'])
    hint_input = mygrid[index][1].text_input(f"Hint {index}", row['Hint'])
    answer_input = mygrid[index][2].text_input(f"Answer {index}", row['Answer'])

    edit_button = mygrid[index][3].button("Edit", on_click=partial(edit_callback, index))
    duplicate_button = mygrid[index][4].button("Duplicate", on_click=partial(duplicate_callback, index))
    delete_button = mygrid[index][5].button("Delete", on_click=partial(delete_callback, index))
    add_to_assignment_button = mygrid[index][6].button("Add To Assignment", on_click=partial(add_to_assignment_callback, index))
