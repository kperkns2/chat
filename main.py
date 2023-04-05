import streamlit as st

st.title('Artificial intelligence - education samples')

st.header('Test out some assignments 👍')
st.subtopic('Prebuilt activities')
st.markdown("[Beginner Spanish Conversation](https://chatbox.streamlit.app/test_assignment?assignment_id=0)")
st.markdown("[Intermediate Spanish Conversation](https://chatbox.streamlit.app/test_assignment?assignment_id=1)")
st.markdown("[Algebra I](https://chatbox.streamlit.app/test_assignment?assignment_id=2)")
st.markdown("[Physics (Mechanics)](https://chatbox.streamlit.app/test_assignment?assignment_id=3)")
st.markdown("[Debate](https://chatbox.streamlit.app/test_assignment?assignment_id=4)")

st.subtopic('Prebuilt quizes')
st.markdown("[Physics (force)](https://chatbox.streamlit.app/test_assignment?assignment_id=4764886)")
st.markdown("[Revolutionary War](https://chatbox.streamlit.app/test_assignment?assignment_id=5598895)")



st.header('Build your own quiz')
st.markdown("Create a [new quiz](https://chatbox.streamlit.app/create_assignment)")

st.markdown("""
Pick a topic and chat with the AI to refine the questions. 
 - You can say things like 'make them all multiple choice'
 - Write 5 more questions
 - Only keep questions 1,2 and 4
 - You can pass in class notes, a video transcript or any raw text as a guide for creating questions""")
