import os
import streamlit as st
import requests
from dotenv import load_dotenv

load_dotenv()

# Page configuration
st.set_page_config(
    page_title="RAG Based Mutual Fund FAQ Chatbot Assistant",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Header
st.title("📊 RAG Based Mutual Fund FAQ Chatbot Assistant")
st.markdown("Welcome! Ask factual questions about SBI Mutual Fund schemes on Groww.")
st.info("💡 Facts-only. No investment advice.")

# Example questions
with st.expander("💡 Example Questions"):
    example_questions = [
        "What is the expense ratio of SBI Small Cap Fund?",
        "What is the exit load for SBI Blue Chip Fund?",
        "What is the minimum SIP amount for SBI Equity Hybrid Fund?",
        "What is the NAV of SBI Small Cap Fund?"
    ]
    
    for q in example_questions:
        if st.button(q, key=q, use_container_width=True):
            st.session_state.user_question = q

# Chat interface
if "user_question" not in st.session_state:
    st.session_state.user_question = ""

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "source" in message and message["source"] not in ["N/A", "AMFI"]:
            st.caption(f"📎 Source: {message['source']}")

# User input
user_input = st.chat_input("Ask your question about SBI Mutual Funds...")

if user_input:
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(user_input)
    
    # Get response from backend
    with st.chat_message("assistant"):
        with st.spinner("Searching..."):
            try:
                res = requests.post(
                    f"{BACKEND_URL}/ask", 
                    json={"question": user_input}, 
                    timeout=30
                )
                
                if res.status_code == 200:
                    data = res.json()
                    
                    # Display answer
                    st.markdown(data["answer"])
                    
                    # Display source only if available and not N/A
                    if data.get("source") and data["source"] not in ["N/A", "AMFI"]:
                        st.caption(f"📎 Source: {data['source']}")
                    
                    # Add assistant message to chat history
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": data["answer"],
                        "source": data.get("source", "N/A")
                    })
                else:
                    st.error(f"Backend error: {res.status_code}")
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": f"Error: Backend returned status code {res.status_code}"
                    })
                    
            except requests.exceptions.Timeout:
                st.error("Request timed out. Please try again.")
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": "Error: Request timed out. Please try again."
                })
            except requests.exceptions.ConnectionError:
                st.error("Could not connect to backend. Make sure the backend is running.")
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": "Error: Could not connect to backend. Please ensure the backend server is running."
                })
            except Exception as e:
                st.error(f"Error: {str(e)}")
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": f"Error: {str(e)}"
                })

# Disclaimer
st.markdown("---")
st.markdown("""
### ⚠️ Disclaimer
This assistant provides factual information only based on official public documents from SBI Mutual Fund, AMFI, and SEBI. 
It does not provide investment advice or recommendations. Please consult a SEBI-registered investment advisor 
for investment decisions.
""")

# Clear chat button
if st.button("🗑️ Clear Chat", use_container_width=True):
    st.session_state.messages = []
    st.rerun()
