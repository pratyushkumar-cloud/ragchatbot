import os
import streamlit as st
import requests
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="RAG Based Mutual Fund FAQ Chatbot Assistant", page_icon="📊")

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

st.title("📊 RAG Based Mutual Fund FAQ Chatbot Assistant")
st.markdown("Welcome! Ask factual questions about SBI Mutual Fund schemes.")

st.markdown("### Example Questions:")
example_questions = [
    "What is the expense ratio of SBI Small Cap Fund?",
    "What is the exit load for SBI Blue Chip Fund?",
    "What is the minimum SIP amount for SBI Equity Hybrid Fund?"
]

for q in example_questions:
    if st.button(q, key=q):
        st.session_state.user_question = q

if "user_question" not in st.session_state:
    st.session_state.user_question = ""

user_input = st.text_input("Ask your question:", value=st.session_state.user_question, key="question_input")

st.info("💡 Facts-only. No investment advice.")

if st.button("Ask"):
    if user_input:
        with st.spinner("Searching..."):
            try:
                res = requests.post(f"{BACKEND_URL}/ask", json={"question": user_input}, timeout=30)
                data = res.json()
                
                st.success("Answer:")
                st.write(data["answer"])
                
                st.markdown(f"**Source:** [{data['source']}]({data['source']})")
            except Exception as e:
                st.error(f"Error: {str(e)}")
    else:
        st.warning("Please enter a question.")

st.markdown("---")
st.markdown("""
### Disclaimer
This assistant provides factual information only based on official public documents. 
It does not provide investment advice. Please consult a SEBI-registered investment advisor 
for investment decisions.
""")
