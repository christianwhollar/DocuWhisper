# frontend/app.py
import streamlit as st
import requests
from utils import clean_response

st.title("Doc Bot")

url = "http://0.0.0.0:8000/query"

# Create Messages List
if "messages" not in st.session_state:
    st.session_state.messages = []

# Write Message Content to Interface
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Default Chat Input
if prompt := st.chat_input(""):
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Format User Input
    data = {"text": prompt}

    # API Request
    response = requests.post(url, json=data)

    if response.status_code == 200:
        api_response = response.json()
        api_response = clean_response(api_response["answer"])
    else:
        api_response = f"Error: {response.status_code}, {response.text}"

    # Display the response from the API
    with st.chat_message("assistant"):
        st.markdown(api_response)

    # Append to Message List
    st.session_state.messages.append({"role": "assistant", "content": api_response})
