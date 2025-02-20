import streamlit as st
import requests
import uuid
import os

# Constants
WEBHOOK_URL = "https://lenhppcce180059.app.n8n.cloud/webhook/invoke_agent"

def generate_session_id():
    return str(uuid.uuid4())

def send_message_to_llm(session_id, message):
    headers = {"Content-Type": "application/json"}
    payload = {"sessionId": session_id, "chatInput": message}
    
    try:
        response = requests.post(WEBHOOK_URL, json=payload, headers=headers)
        data = response.json()
    except requests.exceptions.RequestException as e:
        return f"Error: Unable to reach API - {e}"
    except requests.exceptions.JSONDecodeError:
        return f"Error: API did not return valid JSON - {response.text}"

    if response.status_code == 404:
        return "Error 404: Webhook Not Found - Check n8n workflow!"
    elif response.status_code == 403:
        return "Error 403: Forbidden - Check n8n authentication settings!"
    elif response.status_code != 200:
        return f"Error {response.status_code}: {response.text}"

    if isinstance(data, list) and len(data) > 0:
        data = data[0]  # Lấy phần tử đầu tiên trong danh sách

    return data.get("output", "No response from LLM")

def main():
    st.title("Chat with LLM")

    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "session_id" not in st.session_state:
        st.session_state.session_id = generate_session_id()

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    user_input = st.chat_input("Type your message here...")

    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.write(user_input)

        llm_response = send_message_to_llm(st.session_state.session_id, user_input)

        st.session_state.messages.append({"role": "assistant", "content": llm_response})
        with st.chat_message("assistant"):
            st.write(llm_response)

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8501))
    st.run(port=port)
