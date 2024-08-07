import requests
from utils import clean_response
import streamlit as st

sample_api_response = {"answer": "This is a test response"}


def test_rag_agent_response(requests_mock):
    """
    Mock Rag Agent Response
    """
    url = "http://0.0.0.0:8000/query"
    requests_mock.post(url, json=sample_api_response)

    # Create Message List
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Test Prompt
    prompt = "Hello, bot!"
    st.session_state.messages.append({"role": "user", "content": prompt})

    data = {"text": prompt}

    # Test API Response
    response = requests.post(url, json=data)

    # Assert Valid Response
    assert response.status_code == 200

    api_response = clean_response(response.json()["answer"])

    # Assert Correct Response
    assert api_response == "This is a test response"

    with st.chat_message("assistant"):
        st.markdown(api_response)

    # Append to Message List
    st.session_state.messages.append({"role": "assistant", "content": api_response})

    # Assert Last Message Receieved
    assert st.session_state.messages[-1] == {
        "role": "assistant",
        "content": "This is a test response",
    }
