#"https://igetitv2-learner-api-dev.myigetit.com/chatbot/chatbot/get_llm_answer"

import streamlit as st
import requests
import json
import re

# === Streamlit App Config ===
st.set_page_config(page_title="LLM Chat (Non-Streaming)", layout="wide")
st.title("💬 IGETIT AI Chat Assistant")

# === Session State Initialization ===
if "messages" not in st.session_state:
    st.session_state.messages = []

if "jwt_token" not in st.session_state:
    st.session_state.jwt_token = ""

# === Sidebar for JWT Token Input ===
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
        # Add user message to session
        st.session_state.messages.append({"role": "user", "content": user_input})

        # Display user's message
        with st.chat_message("user"):
            st.markdown(user_input)

        # === API Call ===
        payload = {"question": user_input}
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
                        sources = result.get("sources", [])

                        # === Timestamp Link Logic ===
                        timestamp_pattern = r"\[?🕒\s*([0-9]+:[0-9]{2}:[0-9]{2}(?:\.[0-9]+)?)\]?"
                        matches = re.findall(timestamp_pattern, answer)
                        ts_to_url = {}

                        def normalize(ts):
                            return ts.strip().lstrip("0") if ts.startswith("0") else ts

                        # Build timestamp-to-URL mapping
                        for ts in set(matches):
                            for source in sources:
                                if ts in source.get("content", ""):
                                    ts_to_url[ts] = source["doc_url"]
                                    break

                        def linkify(match):
                            ts = match.group(1)
                            url = ts_to_url.get(ts)
                            if url:
                                return f"[🕒 {ts}]({url})"
                            return f"🕒 {ts}"

                        # Final answer with hyperlinks
                        answer_with_links = re.sub(timestamp_pattern, linkify, answer)

                        # === Display Answer ===
                        st.markdown("### 🤖 Answer")
                        st.markdown(answer_with_links, unsafe_allow_html=True)
                        st.session_state.messages.append({"role": "assistant", "content": answer_with_links})

                        # === Source Docs
                        answer_lower = answer.lower()
                        if sources and "couldn’t find anything related to" not in answer_lower:
                            st.markdown("### 📎 Source Documents")
                            for i, src in enumerate(sources, start=1):
                                st.markdown(f"{i}. [Document Source {i}]({src['doc_url']})", unsafe_allow_html=True)
                        else:
                            st.info("No source documents found.")



                except requests.exceptions.RequestException as e:
                    st.error(f"Connection Error: {e}")

