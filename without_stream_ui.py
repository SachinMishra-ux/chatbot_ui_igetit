import streamlit as st
import requests
import json

# === Backend Configuration ===
API_BASE = "https://igetitv2-learner-api-dev.myigetit.com/chatbot"  # Change this to your actual deployment endpoint

# === Initialize Streamlit session state ===
st.set_page_config(page_title="IGETIT Chatbot", layout="wide")

if "jwt_token" not in st.session_state:
    st.session_state.jwt_token = ""

if "messages" not in st.session_state:
    st.session_state.messages = []

if "session_stored" not in st.session_state:
    st.session_state.session_stored = False

# === Sidebar ===
st.sidebar.title("🔐 JWT & Session Setup")

# === Input JWT Token ===
jwt_input = st.sidebar.text_area("Paste your JWT token", height=150)
if st.sidebar.button("Use This Token"):
    st.session_state.jwt_token = jwt_input
    st.sidebar.success("JWT Token set successfully!")

# === Call /store_user_context ===
if st.sidebar.button("Call /store_user_context"):
    if not st.session_state.jwt_token:
        st.sidebar.error("Set JWT token first.")
    else:
        headers = {"Authorization": f"Bearer {st.session_state.jwt_token}"}
        payload = {"SubscriptionIDs": []}  # Set valid SubscriptionIDs
        response = requests.post(f"{API_BASE}/store_user_context", json=payload, headers=headers)
        if response.status_code == 200:
            st.session_state.session_stored = True
            st.sidebar.success("Session stored successfully!")
        else:
            st.sidebar.error(f"Error: {response.json().get('detail')}")

# === Main Chat Interface ===
st.title("💬 IGETIT Coach Chat")

user_input = st.text_input("Ask a question...", key="input", placeholder="Type your query here...")

if st.button("Send"):
    if not user_input.strip():
        st.warning("Please enter a message.")
    elif not st.session_state.jwt_token:
        st.warning("Please set JWT token.")
    elif not st.session_state.session_stored:
        st.warning("Please store session context.")
    else:
        headers = {"Authorization": f"Bearer {st.session_state.jwt_token}"}
        payload = {"question": user_input}

        try:
            response = requests.post(f"{API_BASE}/get_llm_answer", json=payload, headers=headers)
            if response.status_code == 200:
                data = response.json()
                st.session_state.messages.append(("user", user_input))
                st.session_state.messages.append(("bot", data["answer"]))
            else:
                st.error(f"Bot Error: {response.json().get('detail')}")
        except Exception as e:
            st.error(f"Request failed: {e}")

# === Display chat history ===
for role, msg in st.session_state.messages:
    if role == "user":
        st.markdown(f"🧑‍💻 **You:** {msg}")
    else:
        st.markdown(f"🤖 **Bot:** {msg}")
