import streamlit as st
import requests
from utils import clean_response

st.title("Doc Bot")

url = "http://0.0.0.0:8000/query"

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("What is up?"):
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    data = {"text": prompt}

    response = requests.post(url, json=data)

    if response.status_code == 200:
        api_response = response.json()
        api_response = clean_response(api_response["answer"])
    else:
        api_response = f"Error: {response.status_code}, {response.text}"

    # Display the response from the API
    with st.chat_message("assistant"):
        st.markdown(api_response)

    st.session_state.messages.append({"role": "assistant", "content": api_response})
