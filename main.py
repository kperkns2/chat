import streamlit as st

# Set the page title and layout
st.set_page_config(page_title='AI Education Samples', layout='wide')

# Set a custom theme
st.set_page_config(
    page_title="AI Education Samples",
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="📚"
)


#theme={
#        "primaryColor": "#0D8BF0",
#        "backgroundColor": "#F0F0F0",
#        "secondaryBackgroundColor": "#F0F0F0",
#        "textColor": "#333333",
#        "font": "sans-serif"
#    }


st.title('Artificial Intelligence - Education Samples')

st.header('Test out some assignments 👍')
st.subheader('Prebuilt activities')

# Create columns for links
col1, col2 = st.columns(2)

with col1:
    st.markdown("[Beginner Spanish Conversation](https://chatbox.streamlit.app/test_assignment?assignment_id=0)", unsafe_allow_html=True)
    st.markdown("[Intermediate Spanish Conversation](https://chatbox.streamlit.app/test_assignment?assignment_id=1)", unsafe_allow_html=True)
    st.markdown("[Algebra I](https://chatbox.streamlit.app/test_assignment?assignment_id=2)", unsafe_allow_html=True)

with col2:
    st.markdown("[Physics (Mechanics)](https://chatbox.streamlit.app/test_assignment?assignment_id=3)", unsafe_allow_html=True)
    st.markdown("[Debate](https://chatbox.streamlit.app/test_assignment?assignment_id=4)", unsafe_allow_html=True)

st.subheader('Prebuilt quizzes')

with col1:
    st.markdown("[Physics (force)](https://chatbox.streamlit.app/test_assignment?assignment_id=4764886)", unsafe_allow_html=True)

with col2:
    st.markdown("[Revolutionary War](https://chatbox.streamlit.app/test_assignment?assignment_id=5598895)", unsafe_allow_html=True)

st.header('Build your own quiz')
st.markdown("Create a [new quiz](https://chatbox.streamlit.app/create_assignment)", unsafe_allow_html=True)

st.markdown("""
Pick a topic and chat with the AI to refine the questions. 
 - You can say things like 'make them all multiple choice'
 - Write 5 more questions
 - Only keep questions 1, 2, and 4
 - You can pass in class notes, a video transcript, or any raw text as a guide for creating questions""")
