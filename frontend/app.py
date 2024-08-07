import streamlit as st
import requests
from utils import clean_response

st.title("Doc Bot")

query_url = "http://backend:8000/query"
upload_url = "http://backend:8000/upload"

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
    response = requests.post(query_url, json=data)

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

# Multiple File Upload
uploaded_files = st.file_uploader("Choose files to upload", accept_multiple_files=True)

if uploaded_files:
    for uploaded_file in uploaded_files:
        # Display file name
        st.write(f"File selected: {uploaded_file.name}")

        # Send file to upload URL
        files = {"file": uploaded_file.getvalue()}
        response = requests.post(upload_url, files=files)

        if response.status_code == 200:
            st.success(f"File {uploaded_file.name} uploaded successfully")
            st.json(response.json())
        else:
            st.error(
                f"Failed to upload file {uploaded_file.name}: {response.status_code}, {response.json()}"
            )
