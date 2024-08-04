import streamlit as st
from streamlit_lottie import st_lottie
import requests
import random

# Function to load Lottie animations
def load_lottieurl(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

# Set page config
st.set_page_config(page_title="EchoBot - Your AI Assistant", page_icon="🤖", layout="wide")

# Custom CSS
st.markdown("""
<style>
    .stApp {
        background-color: #f0f4f8;
    }
    .stTextInput > div > div > input {
        background-color: #ffffff;
    }
    .stMarkdown {
        font-family: 'Arial', sans-serif;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar
st.sidebar.title("EchoBot Settings")
bot_persona = st.sidebar.selectbox("Choose Bot Persona", ["Friendly", "Professional", "Sarcastic"])
language = st.sidebar.selectbox("Language", ["English", "Spanish", "French"])

# Main content
col1, col2 = st.columns([2, 1])

with col1:
    st.title("🤖 EchoBot - Your AI Assistant")
    st.markdown("Welcome to EchoBot! I'm here to echo your thoughts and keep you company.")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("What's on your mind?"):
        st.chat_message("user").markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Persona-based responses
        friendly_responses = [
            f"That's interesting! Here's what I heard: {prompt}",
            f"I like how you think! You said: {prompt}",
            f"Thanks for sharing! I'm echoing: {prompt}"
        ]
        professional_responses = [
            f"Understood. To confirm, you stated: {prompt}",
            f"Noted. Your input was: {prompt}",
            f"Acknowledged. I've recorded: {prompt}"
        ]
        sarcastic_responses = [
            f"Oh, how original. You said: {prompt}",
            f"Wow, never heard that before. Echoing: {prompt}",
            f"Brilliant insight, truly. You mentioned: {prompt}"
        ]

        if bot_persona == "Friendly":
            response = random.choice(friendly_responses)
        elif bot_persona == "Professional":
            response = random.choice(professional_responses)
        else:
            response = random.choice(sarcastic_responses)

        with st.chat_message("assistant"):
            st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})

with col2:
    lottie_url = "https://assets5.lottiefiles.com/packages/lf20_M9p23l.json"
    lottie_animation = load_lottieurl(lottie_url)
    st_lottie(lottie_animation, key="lottie", height=300)

    st.markdown("### How to use EchoBot")
    st.markdown("""
    1. Type your message in the chat input
    2. EchoBot will respond based on the selected persona
    3. Explore different personas and languages in the sidebar
    4. Enjoy your conversation with EchoBot!
    """)

# Footer
st.markdown("---")
st.markdown("Created with ❤️ by Your Name | [GitHub](https://github.com/yourusername)")