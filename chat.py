import os
import streamlit as st
import requests

st.set_page_config(page_title="Sovereign Vault Chat", layout="centered")
st.title("💬 Sovereign Vault Chat")

# persist history
if "messages" not in st.session_state:
    st.session_state.messages = []

# show history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

prompt = st.chat_input("Ask the vault…")
if prompt:
    # add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # ---- authenticated call to vault ----
    VAULT_KEY = os.getenv("VAULT_KEY", "sovereign-123456")   # same secret you set in Fly
    url = "https://my-vault-model.fly.dev/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {VAULT_KEY}"
    }
    payload = {
        "messages": st.session_state.messages,
        "temperature": 0.7,
        "max_tokens": 200
    }

    with st.chat_message("assistant"):
        placeholder = st.empty()
        try:
            resp = requests.post(url, headers=headers, json=payload, timeout=30)
            resp.raise_for_status()
            reply = resp.json()["choices"][0]["message"]["content"]
            placeholder.markdown(reply)
            st.session_state.messages.append({"role": "assistant", "content": reply})
        except Exception as e:
            placeholder.error(f"Vault error: {e}")