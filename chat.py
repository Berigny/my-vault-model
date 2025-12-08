import os
import streamlit as st
import requests

st.set_page_config(page_title="Sovereign Vault Chat", layout="centered")
st.title("💬 Sovereign Vault Chat")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Display existing chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Handle user input
prompt = st.chat_input("Ask the vault…")
if prompt:
    # 1. Display user message immediately
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. Prepare the API request
    # NOTE: Ensure this matches the key shown in your logs (****3456)
    VAULT_KEY = os.getenv("VAULT_KEY", "sovereign-123456") 
    
    # CRITICAL FIX: Changed http -> https to prevent 301 Redirect -> GET conversion
    url = "https://my-vault-model.fly.dev/v1/chat/completions"
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {VAULT_KEY}"
    }
    
    payload = {
        "messages": st.session_state.messages,
        "temperature": 0.7,
        "max_tokens": 500  # Increased slightly for better answers
    }

    # 3. Get response from the Vault
    with st.chat_message("assistant"):
        placeholder = st.empty()
        response = None  # ensure defined for error handling
        try:
            with st.spinner("Thinking..."):
                response = requests.post(url, headers=headers, json=payload, timeout=60)
            
            # Raise error for 4xx/5xx status codes
            response.raise_for_status()
            
            # Parse JSON
            data = response.json()
            reply = data["choices"][0]["message"]["content"]
            
            # Display and save
            placeholder.markdown(reply)
            st.session_state.messages.append({"role": "assistant", "content": reply})
            
        except requests.exceptions.HTTPError as err:
            # This will help you debug if you get a 401 (Auth) or 500 (Server) error
            error_text = response.text if response is not None else "No response body"
            placeholder.error(f"HTTP Error: {err} - {error_text}")
        except Exception as e:
            placeholder.error(f"Vault error: {e}")
