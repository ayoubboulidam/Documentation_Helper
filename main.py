from typing import Set
from backend.core import run_llm
import streamlit as st
from streamlit_chat import message

# App Header
st.header("LangChain - Documentation Helper Bot")

# Input field for prompt
prompt = st.text_input("Prompt", placeholder="Enter your prompt here...")

# Session state to store prompt and chat history
if "user_prompt_history" not in st.session_state:
    st.session_state["user_prompt_history"] = []

if "chat_answers_history" not in st.session_state:
    st.session_state["chat_answers_history"] = []

# Function to create sources string with clickable links
def create_sources_string(source_urls: Set[str]) -> str:
    if not source_urls:
        return ""
    sources_list = sorted(list(source_urls))
    sources_string = "### Sources:\n"
    for i, source in enumerate(sources_list):
        # Make source a clickable link if it looks like a URL
        sources_string += f"{i+1}. [{source}]({source})\n" if "http" in source else f"{i+1}. {source}\n"
    return sources_string

# Generate response when prompt is provided
if prompt:
    with st.spinner("Generating response..."):
        generated_response = run_llm(query=prompt)
        sources = set(
            [doc.metadata["source"] for doc in generated_response["source_documents"]]
        )

        formatted_response = (
            f"{generated_response['result']} \n\n {create_sources_string(sources)}"
        )

        # Append to session state for history
        st.session_state["user_prompt_history"].append(prompt)
        st.session_state["chat_answers_history"].append(formatted_response)

# Display chat history with avatars
if st.session_state["chat_answers_history"]:
    for user_query, generated_response in zip(
        st.session_state["user_prompt_history"],
        st.session_state["chat_answers_history"],
    ):
        # Display user message
        message(user_query, is_user=True, key=f"user_{user_query}")
        # Display bot response with sources
        message(generated_response, key=f"bot_{generated_response}")
