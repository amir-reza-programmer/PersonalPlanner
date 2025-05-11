# streamlit_app.py
import streamlit as st
from app.task_flow_graph import build_task_flow_graph
from dotenv import load_dotenv

st._is_running_with_patched_torch = True  # Prevents torch inspection bug

st.title("Personal Task Assistant")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("How can I help?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    load_dotenv()
    graph = build_task_flow_graph()

    state = {"input": prompt}
    response = graph.invoke(state)
    print('resulttt', response)
    st.session_state.messages.append(
        {"role": "assistant", "content": response['respond']})
    with st.chat_message("assistant"):
        st.markdown(response['respond'])
