import requests
import streamlit as st
import logging
import json

logging.basicConfig(level=logging.ERROR)

dify_api_key = st.secrets["DIFY_API_KEY"]
url = 'http://api.dify.ai/v1/chat-messages'

st.title('カラスのお悩み相談室')

if "conversation_id" not in st.session_state:
    st.session_state.conversation_id = ""

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

user_input = st.chat_input("カラスに何か質問してみよう")

if user_input:
    with st.chat_message("user"):
        st.markdown(user_input)

    st.session_state.messages.append({"role": "user", "content": user_input})

with st.chat_message("assistant"):
    message_placeholder = st.empty()

    headers = {
        'Authorization': f'Bearer {dify_api_key}',
        'Content-Type': 'application/json'
    }

    payload = {
        "inputs": {"text": user_input},
        "query": user_input or "default query",
        "response_mode": "streaming",
        "conversation_id": st.session_state.conversation_id,
        "user": "alex-123",
        "files": []
    }

try:
    response = requests.post(url, headers=headers, data=json.dumps(payload))  # Ensure POST is the correct method
    response.raise_for_status()

    response_data = response.json()

    full_response = response_data.get("answer", "")
    new_conversation_id = response_data.get("conversation_id", st.session_state.conversation_id)

    st.session_state.conversation_id = new_conversation_id

except requests.exceptions.RequestException as e:
    logging.error(f"An error occurred: {e}", exc_info=True)
    st.error(f"An error occurred: {e}")
    if e.response is not None:
        st.error(f"Response status code: {e.response.status_code}")
        st.error(f"Response content: {e.response.content.decode()}")
    full_response = "An error occurred while fetching the response."

message_placeholder.markdown(full_response)

st.session_state.messages.append({"role": "assistant", "content": full_response})
