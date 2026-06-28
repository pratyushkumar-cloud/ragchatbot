import os
import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

st.set_page_config(
    page_title="Mutual Fund FAQ Assistant",
    page_icon="📊",
    layout="wide"
)

# ---------- Custom CSS ----------
st.markdown("""
<style>

.block-container{
    padding-top:2rem;
    padding-bottom:2rem;
}

.stChatMessage{
    border-radius:12px;
}

.source-box{
    background:#F4F6F9;
    padding:10px;
    border-radius:8px;
    margin-top:10px;
}

.example-btn button{
    width:100%;
}

</style>
""", unsafe_allow_html=True)

# ---------- Sidebar ----------
with st.sidebar:

    st.title("📊 Mutual Fund FAQ")

    st.markdown("""
Facts-only assistant built using **RAG**.

### Scope

- SBI Mutual Fund
- Official AMC Pages
- AMFI
- SEBI

---

### Example Topics

- Expense Ratio
- Exit Load
- Minimum SIP
- Lock-in
- Riskometer
- Benchmark
- Statement Download

---

❌ No Investment Advice
""")

    if st.button("🗑 Clear Chat"):
        st.session_state.messages = []
        st.rerun()

# ---------- Header ----------

st.title("📊 RAG-Based Mutual Fund FAQ Assistant")

st.caption("Facts-only • Official Sources • No Investment Advice")

# ---------- Chat History ----------

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:

    with st.chat_message(msg["role"]):

        st.markdown(msg["content"])

        if msg["role"] == "assistant" and msg.get("source"):

            source_info = f"<b>Source:</b><br><a href='{msg['source']}' target='_blank'>{msg['source']}</a>"
            if msg.get("document"):
                source_info += f"<br><b>Document:</b> {msg['document']}"
            if msg.get("page"):
                source_info += f"<br><b>Page:</b> {msg['page']}"
            if msg.get("publisher"):
                source_info += f"<br><b>Publisher:</b> {msg['publisher']}"
            if msg.get("last_updated"):
                source_info += f"<br><b>Last Updated:</b> {msg['last_updated']}"

            st.markdown(
                f"""
<div class="source-box">
{source_info}
</div>
""",
                unsafe_allow_html=True,
            )

# ---------- Suggested Questions ----------

st.markdown("### 💡 Suggested Questions")

col1, col2, col3 = st.columns(3)

examples = [
    "What is the expense ratio of SBI Small Cap Fund?",
    "What is the exit load for SBI Bluechip Fund?",
    "What is the minimum SIP amount for SBI Equity Hybrid Fund?"
]

selected = None

with col1:
    if st.button(examples[0], use_container_width=True):
        selected = examples[0]

with col2:
    if st.button(examples[1], use_container_width=True):
        selected = examples[1]

with col3:
    if st.button(examples[2], use_container_width=True):
        selected = examples[2]

# ---------- Chat Input ----------

prompt = st.chat_input("Ask a factual question about SBI Mutual Fund...")

if selected:
    prompt = selected

if prompt:

    st.session_state.messages.append(
        {
            "role": "user",
            "content": prompt
        }
    )

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):

        with st.spinner("Searching official sources..."):

            try:

                response = requests.post(
                    f"{BACKEND_URL}/ask",
                    json={"question": prompt},
                    timeout=30,
                )

                data = response.json()

                answer = data.get(
                    "answer",
                    "No answer found."
                )

                source = data.get("source", "")
                document = data.get("document", "")
                page = data.get("page", "")
                publisher = data.get("publisher", "")
                last_updated = data.get("last_updated", "")

                st.markdown(answer)

                if source:
                    source_info = f"<b>Source:</b><br><a href='{source}' target='_blank'>{source}</a>"
                    if document:
                        source_info += f"<br><b>Document:</b> {document}"
                    if page:
                        source_info += f"<br><b>Page:</b> {page}"
                    if publisher:
                        source_info += f"<br><b>Publisher:</b> {publisher}"
                    if last_updated:
                        source_info += f"<br><b>Last Updated:</b> {last_updated}"
                    
                    st.markdown(
                        f"""
<div class="source-box">
{source_info}
</div>
""",
                        unsafe_allow_html=True,
                    )

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": answer,
                        "source": source,
                        "document": document,
                        "page": page,
                        "publisher": publisher,
                        "last_updated": last_updated,
                    }
                )

            except Exception as e:

                error_msg = f"Unable to connect to backend.\n\n{e}"

                st.error(error_msg)

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": error_msg,
                        "source": "",
                        "document": "",
                        "last_updated": "",
                    }
                )

# ---------- Footer ----------

st.markdown("---")

st.info(
    """
**Disclaimer**

This assistant answers **only factual questions** using official public documents from SBI Mutual Fund, AMFI and SEBI.

It **does not provide investment advice, recommendations, or return predictions.**
"""
)