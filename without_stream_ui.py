import streamlit as st
import requests
import json


#"https://igetitv2-learner-api-dev.myigetit.com/chatbot/chatbot/get_llm_answer"

st.set_page_config(page_title="LLM Chat (Non-Streaming)", layout="wide")
st.title("💬 IGETIT AI Chat Assistant")

# Session state for chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Session state for JWT token
if "jwt_token" not in st.session_state:
    st.session_state.jwt_token = ""

# === JWT Token Input ===
with st.sidebar:
    st.header("🔐 Authentication")
    st.session_state.jwt_token = st.text_input("Enter JWT Token", type="password")

    if st.session_state.jwt_token:
        st.success("Token loaded")
    else:
        st.warning("Please provide a valid JWT token")

# === Chat Input ===
user_input = st.chat_input("Ask a question...")
if user_input:
    if not st.session_state.jwt_token:
        st.error("JWT token is required. Please enter it in the sidebar.")
    else:
        st.session_state.messages.append({"role": "user", "content": user_input})

        with st.chat_message("user"):
            st.markdown(user_input)

        # Prepare payload
        payload = {"question": user_input}

        # Prepare headers with JWT Bearer token
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {st.session_state.jwt_token}"
        }

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    response = requests.post(
                        "https://igetitv2-learner-api-dev.myigetit.com/chatbot/get_llm_answer",
                        headers=headers,
                        data=json.dumps(payload),
                        timeout=60
                    )

                    if response.status_code != 200:
                        st.error(f"API Error: {response.status_code} - {response.text}")
                    else:
                        result = response.json()
                        answer = result.get("answer", "")
                        metadata = result.get("metadata", [])

                        st.markdown(answer)

                        if metadata:
                            st.markdown("#### 📎 Source Metadata")
                            for item in metadata:
                                st.json(item)

                        st.session_state.messages.append({"role": "assistant", "content": answer})

                except requests.exceptions.RequestException as e:
                    st.error(f"Connection Error: {e}")
