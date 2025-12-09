import streamlit as st
import time
from openai import OpenAI
import os

# --- CONFIGURATION ---
# This matches the model you set in your backend
MODEL_ID = "groq/llama-3.1-8b-instant"

st.set_page_config(page_title="Vault Latency Test", layout="centered")
st.title("⚡ Groq Speed Verification")

# 1. Fetch API Key (Prioritize Secrets)
if "OPENROUTER_API_KEY" in st.secrets:
    api_key = st.secrets["OPENROUTER_API_KEY"]
else:
    api_key = os.getenv("OPENROUTER_API_KEY")

if not api_key:
    st.error("❌ Critical Error: `OPENROUTER_API_KEY` not found in Streamlit Secrets.")
    st.stop()

# 2. Initialize Client (Direct to OpenRouter)
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=api_key,
)

# 3. Chat State
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display History
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 4. Input & Response
prompt = st.chat_input("Test the model latency (e.g. 'Explain quantum entropy')")
if prompt:
    # User Message
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Assistant Response
    with st.chat_message("assistant"):
        placeholder = st.empty()
        full_response = ""
        start_time = time.time()
        
        try:
            # We use stream=True to visually see the speed
            stream = client.chat.completions.create(
                model=MODEL_ID,
                messages=st.session_state.messages,
                stream=True,
                extra_headers={
                    "HTTP-Referer": "https://my-vault-model.fly.dev",
                    "X-Title": "Vault Verification",
                }
            )
            
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    full_response += content
                    placeholder.markdown(full_response + "▌")
            
            # Calculate final stats
            end_time = time.time()
            latency = end_time - start_time
            chars = len(full_response)
            
            # Display result with stats
            placeholder.markdown(full_response)
            st.caption(f"⏱️ **Latency:** {latency:.2f}s | **Speed:** {int(chars/latency) if latency > 0 else 0} chars/sec")
            
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            
        except Exception as e:
            st.error(f"API Error: {e}")