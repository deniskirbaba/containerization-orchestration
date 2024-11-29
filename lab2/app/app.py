import streamlit as st
from database.connection import init_db
from database_bridge import DatabaseBridge
from model_bridge import ModelBridge


def init_page() -> None:
    st.set_page_config(page_title="Storyteller")
    st.header("Storyteller")
    st.sidebar.title("Options")


@st.cache_resource
def load_model_bridge() -> ModelBridge:
    return ModelBridge()


def reset_conversation() -> None:
    """
    Reset the conversation history in the session state and the database.
    """
    st.session_state.messages = []
    DatabaseBridge.reset()


def get_options() -> dict:
    """
    Return dict with generation options from sidebar.
    """
    n_predict = st.sidebar.slider(
        "Max Tokens to Predict",
        min_value=16,
        max_value=4096,
        value=64,
        step=16,
        help="The maximum number of tokens the model will generate in response.",
    )

    temperature = st.sidebar.slider(
        "Temperature",
        min_value=0.1,
        max_value=2.0,
        value=0.8,
        step=0.1,
        help="Controls the randomness of the response. Lower values make the output more deterministic.",
    )

    top_k = st.sidebar.slider(
        "Top-k Sampling",
        min_value=1,
        max_value=100,
        value=40,
        step=1,
        help="Limits the next token selection to the top-k most probable tokens.",
    )

    top_p = st.sidebar.slider(
        "Top-p (Nucleus) Sampling",
        min_value=0.1,
        max_value=1.0,
        value=0.95,
        step=0.05,
        help="Top-p sampling selects tokens with a cumulative probability above a threshold, controlling diversity.",
    )

    min_p = st.sidebar.slider(
        "Minimum Probability (Min-P)",
        min_value=0.0,
        max_value=1.0,
        value=0.05,
        step=0.01,
        help="Ensures tokens with at least this probability are considered during sampling.",
    )

    st.sidebar.button("Clear history", on_click=reset_conversation, use_container_width=True)

    return {
        "n_predict": n_predict,
        "temperature": temperature,
        "top_k": top_k,
        "top_p": top_p,
        "min_p": min_p,
    }


def main() -> None:
    init_db()
    init_page()
    model_bridge = load_model_bridge()
    options = get_options()

    if "messages" not in st.session_state:
        st.session_state.messages = DatabaseBridge.get_history()

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # React to user input
    if prompt := st.chat_input("Enter the beginning of the story"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        DatabaseBridge.add_message(prompt, "user")
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            response = st.write_stream(model_bridge.response_generator(prompt, **options))
        st.session_state.messages.append({"role": "assistant", "content": response})
        DatabaseBridge.add_message(response, "assistant")


if __name__ == "__main__":
    main()
