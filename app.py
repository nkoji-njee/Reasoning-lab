import streamlit as st
from shared import init_state, render_teacher_sidebar

init_state()
st.title("🧠 Reasoning Lab: Pixitex Prototype")
render_teacher_sidebar()

st.write(
    "Use the page navigation in the sidebar to open **Session 1**, **Session 2**, or **Session 3**. "
    "Each page runs that session's rules on its own — your progress (chat history, maturity score, "
    "flagged messages) carries over between them automatically within this browser session."
)
