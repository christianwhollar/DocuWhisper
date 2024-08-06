import requests
from utils import clean_response
import streamlit as st

sample_api_response = {"answer": "This is a test response"}


def test_echo_bot(requests_mock):
    url = "http://0.0.0.0:8000/query"
    requests_mock.post(url, json=sample_api_response)

    if "messages" not in st.session_state:
        st.session_state.messages = []

    prompt = "Hello, bot!"
    st.session_state.messages.append({"role": "user", "content": prompt})

    data = {"text": prompt}

    response = requests.post(url, json=data)

    assert response.status_code == 200

    api_response = clean_response(response.json()["answer"])

    assert api_response == "This is a test response"

    with st.chat_message("assistant"):
        st.markdown(api_response)

    st.session_state.messages.append({"role": "assistant", "content": api_response})

    assert st.session_state.messages[-1] == {
        "role": "assistant",
        "content": "This is a test response",
    }
