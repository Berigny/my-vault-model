import streamlit as st
from openai import OpenAI
import os

# --- CONFIGURATION ---
# We are testing the "Instant" 8B model. 
# If you want to test the 70B model, change this to: "groq/llama-3.1-70b-versatile"
MODEL_ID = "groq/llama-3.1-8b-instant"

st.set_page_config(page_title="Vault Verification (Groq)", layout="centered")
st.title(f"⚡ Verification: {MODEL_ID}")

# 1. Fetch API Key (Prioritize Secrets)
if "OPENROUTER_API_KEY" in st.secrets:
    api_key = st.secrets["OPENROUTER_API_KEY"]
else:
    api_key = os.getenv("OPENROUTER_API_KEY")

if not api_key:
    st.error("❌ Missing OpenRouter API Key in Secrets!")
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
prompt = st.chat_input("Test the model latency...")
if prompt:
    # User Message
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Assistant Response
    with st.chat_message("assistant"):
        placeholder = st.empty()
        full_response = ""
        
        try:
            stream = client.chat.completions.create(
                model=MODEL_ID,
                messages=st.session_state.messages,
                stream=True,
                extra_headers={
                    "HTTP-Referer": "https://my-vault-model.fly.dev", # Optional: Your site
                    "X-Title": "Vault Verification",
                }
            )
            
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    full_response += content
                    placeholder.markdown(full_response + "▌")
            
            placeholder.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            
        except Exception as e:
            st.error(f"API Error: {e}")