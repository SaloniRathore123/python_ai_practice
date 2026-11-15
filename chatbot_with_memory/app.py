from pathlib import Path

import streamlit as st
from dotenv import load_dotenv
from google import genai

MODEL = "gemini-3.6-flash"

# The .env file lives in the project root, one level above this folder
load_dotenv(Path(__file__).resolve().parent.parent / ".env")
load_dotenv()  # also pick up a .env in the current directory, if any


@st.cache_resource
def get_client():
    return genai.Client()


client = get_client()

st.set_page_config(page_title="Chatbot with Memory", page_icon="💬")
st.title("💬 Chatbot with Memory")

# Chatbot memory: st.session_state survives Streamlit's reruns,
# so the conversation list keeps growing across messages.
if "conversation" not in st.session_state:
    st.session_state.conversation = []

with st.sidebar:
    st.caption(f"Model: `{MODEL}`")
    st.caption(f"Messages in memory: {len(st.session_state.conversation)}")
    if st.button("Clear memory"):
        st.session_state.conversation = []
        st.rerun()


def chat(user_message):
    conversation = st.session_state.conversation

    # 1. Add what the user said to memory
    conversation.append({"role": "user", "parts": [{"text": user_message}]})

    # 2. Send the entire conversation so far
    try:
        response = client.models.generate_content(
            model=MODEL,
            contents=conversation,
        )
        reply = response.text
    except Exception as e:
        conversation.pop()  # forget the failed turn so history stays valid
        return f"Sorry, something went wrong: ({e})."

    # 3. Add the AI's reply to memory so it remembers next time.
    #    Gemini expects the assistant's role to be "model".
    conversation.append({"role": "model", "parts": [{"text": reply}]})
    return reply


# Show the conversation so far
for message in st.session_state.conversation:
    role = "user" if message["role"] == "user" else "assistant"
    with st.chat_message(role):
        st.markdown(message["parts"][0]["text"])

# Handle new input
if prompt := st.chat_input("Say something..."):
    with st.chat_message("user"):
        st.markdown(prompt)
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            reply = chat(prompt)
        st.markdown(reply)
