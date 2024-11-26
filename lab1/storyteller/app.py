import json
from pathlib import Path

import streamlit as st
from model import StoryModel

CHAT_FILE = Path("/app/data/chat_history.json")
CHAT_FILE.parent.mkdir(parents=True, exist_ok=True)

st.title("Storyteller")


@st.cache_resource
def load_model():
    model = StoryModel()
    model.load(model.model_name)
    return model


model = load_model()


def load_chat_history():
    """
    Initialize or load chat history
    """
    if CHAT_FILE.exists():
        return json.loads(CHAT_FILE.read_text())
    return []


def save_chat_history(chat_history):
    CHAT_FILE.write_text(json.dumps(chat_history, indent=4))


if "messages" not in st.session_state:
    st.session_state.messages = load_chat_history()

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# React to user input
if prompt := st.chat_input("Enter the beginning of the story"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"), st.empty():
        with st.spinner("Generating..."):
            response = model.generate(prompt)
        st.markdown(response)
    st.session_state.messages.append({"role": "assistant", "content": response})

    save_chat_history(st.session_state.messages)
