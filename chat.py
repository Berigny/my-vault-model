import streamlit as st
import requests
import os

st.set_page_config(page_title="Sovereign Vault Chat", layout="centered")
st.title("💬 Sovereign Vault Chat")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# React to user input
prompt = st.chat_input("Ask the vault…")
if prompt:
    # 1. Display user message immediately
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # 2. Retrieve Credential
    # Checks Streamlit secrets first, then Environment variable, then falls back to default
    if "VAULT_KEY" in st.secrets:
        VAULT_KEY = st.secrets["VAULT_KEY"]
    else:
        VAULT_KEY = os.getenv("VAULT_KEY", "sovereign-123456")

    # 3. Define API Endpoint
    # CRITICAL FIX: Changed http:// to https://
    # This prevents the 301 Redirect which was converting your POST request into a GET request
    url = "https://my-vault-model.fly.dev/v1/chat/completions"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {VAULT_KEY}"
    }

    payload = {
        "messages": st.session_state.messages,
        "temperature": 0.7,
        "max_tokens": 500
    }

    # 4. Get response
    with st.chat_message("assistant"):
        placeholder = st.empty()
        resp = None  # ensure defined for exception handlers
        try:
            with st.spinner("The Vault is thinking..."):
                # Increased timeout to 60s in case the Fly machine is "waking up"
                resp = requests.post(url, headers=headers, json=payload, timeout=60)
            
            # This will trigger an error if the status code is 4xx or 5xx
            resp.raise_for_status()
            
            data = resp.json()
            reply = data["choices"][0]["message"]["content"]
            
            placeholder.markdown(reply)
            st.session_state.messages.append({"role": "assistant", "content": reply})
            
        except requests.exceptions.HTTPError as http_err:
            # If auth fails (401) or URL is wrong (404), this will catch it
            body = resp.text if resp is not None else "No response body"
            placeholder.error(f"HTTP Error: {http_err} - Response: {body}")
        except Exception as e:
            # Error handling
            placeholder.error(f"Vault error: {e}")
            
            # CRITICAL FIX: Remove the user's last message if the request failed
            # This prevents the "User -> User" history corruption
            if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
                st.session_state.messages.pop()
