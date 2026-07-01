import os
import base64
import streamlit as st
from dotenv import load_dotenv
from datetime import datetime
from src.retriever import get_retriever
from src.prompt import PromptTemplates
from src.guardrails import Guardrails
from langchain_groq import ChatGroq

# ---------- Environment Configuration ----------
load_dotenv()

# ---------- Initialize RAG Components ----------
@st.cache_resource
def initialize_rag_components():
    """Initialize retriever and LLM with caching for performance"""
    retriever = get_retriever(k=6)
    llm = ChatGroq(
        model=os.getenv("LLM_MODEL", "llama-3.3-70b-versatile"),
        temperature=float(os.getenv("LLM_TEMPERATURE", "0")),
        groq_api_key=os.getenv("GROQ_API_KEY")
    )
    return retriever, llm

retriever, llm = initialize_rag_components()

# ---------- QA Logic ----------
def answer_query(question: str):
    """Answer a factual question using RAG with source citation"""
    # Guardrails check
    if Guardrails.is_advice_question(question):
        return {
            "answer": "I can only provide factual information about mutual funds. I do not provide investment advice, recommendations, or return predictions.",
            "source": ""
        }

    # Retrieve documents
    docs = retriever.invoke(question)
    
    if not docs:
        return {
            "answer": "I couldn't find this information in the selected official documents.",
            "source": ""
        }

    # Build context
    context = "\n\n".join([f"[Source: {d.metadata.get('source', 'Unknown')}]\n{d.page_content}" for d in docs])
    
    # Deduplicate document names
    unique_documents = list(set([d.metadata.get("title", "Unknown") for d in docs]))
    unique_documents = [doc for doc in unique_documents if doc != "Unknown" and doc != ""]
    document_names = ", ".join(unique_documents) if unique_documents else "official documents"

    # Generate prompt and get response
    prompt = PromptTemplates.get_rag_prompt(context, question, document_names)
    response = llm.invoke(prompt)
    answer = response.content.strip()
    
    # Post-processing
    answer = Guardrails.filter_generic_advice(answer)
    
    # Check if answer indicates information not found
    not_found_indicators = [
        "couldn't find this information",
        "information not found",
        "not available in the provided",
        "does not contain information"
    ]
    
    is_not_found = any(indicator in answer.lower() for indicator in not_found_indicators)
    
    if is_not_found:
        answer = "I couldn't find this information in the selected official documents."
        source = ""
    else:
        # Prioritize web sources for source citation
        web_docs = [doc for doc in docs if doc.metadata.get("source", "").startswith("http")]
        selected_doc = web_docs[0] if web_docs else docs[0]
        source = selected_doc.metadata.get("source", "")
        
        # Add "Last updated from sources"
        current_date = datetime.now().strftime("%B %d, %Y")
        answer = f"{answer} Last updated from sources: {current_date}"

    return {
        "answer": answer,
        "source": source
    }

# ---------- Logo Processing ----------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
logo_path = os.path.join(BASE_DIR, "data/groww_logo.webp")

def get_logo_base64(path):
    if os.path.exists(path):
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return None

logo_base64 = get_logo_base64(logo_path)

# ---------- Streamlit Window Configuration ----------
st.set_page_config(
    page_title="Groww Mutual Fund FAQ Assistant",
    page_icon="📊",
    layout="wide"
)

# ---------- Theme Variables ----------
GROWW_GREEN = "#00D09C"
GROWW_DARK_GREEN = "#00B386"
BORDER_COLOR = "#E2E8F0"

# ---------- Comprehensive Responsive CSS ----------
st.markdown(f"""
<style>
/* Global Layout Adaptations */
.block-container {{
    padding-top: 1.5rem;
    padding-bottom: 5rem; 
    max-width: 1100px;
}}

/* Header Typography */
h1 {{
    font-weight: 700 !important;
    color: #1E293B !important;
    letter-spacing: -0.02em;
    font-size: calc(1.5rem + 1vw) !important;
    margin-bottom: 4px !important;
}}

/* Sticky Top Section */
.top-fixed {{
    position: sticky;
    top: 0;
    background: rgba(255, 255, 255, 0.95);
    backdrop-filter: blur(8px);
    z-index: 99;
    padding: 8px 0 16px 0;
    border-bottom: 1px solid {BORDER_COLOR};
    margin-bottom: 24px;
}}

.top-caption {{
    font-size: 13px;
    font-weight: 500;
    color: #64748B;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}}

.suggested-title {{
    font-size: 14px;
    font-weight: 600;
    color: #475569;
    margin-bottom: 10px;
}}

/* Streamlit Native Chat Overrides */
div[data-testid="stChatMessage"] {{
    padding: 1rem;
    border-radius: 12px;
    margin-bottom: 1rem;
    box-shadow: 0 1px 3px rgba(0,0,0,0.02);
    border: 1px solid {BORDER_COLOR};
}}

div[data-testid="stChatMessage"]:has([data-testid*="user" i]) {{
    background-color: #FFFFFF;
    border-color: #000000;
}}

div[data-testid="stChatMessage"]:has([data-testid*="assistant" i]) {{
    background-color: #F0FDF4;
    border-color: #000000;
}}

/* Source Verification Boxes */
.source-box {{
    background: #FFFFFF;
    padding: 12px 16px;
    border-radius: 8px;
    margin-top: 14px;
    border: 1px solid #DFE7E2;
    border-left: 4px solid {GROWW_GREEN};
}}

.source-box b {{
    color: #334155;
    font-size: 13px;
    text-transform: uppercase;
}}

.source-box a {{
    color: {GROWW_DARK_GREEN} !important;
    text-decoration: none !important;
    font-weight: 500;
    font-size: 14px;
    word-break: break-all;
}}

/* Modern Interactive Suggestion Buttons */
.stButton button {{
    border-radius: 8px !important;
    border: 1px solid {BORDER_COLOR} !important;
    background-color: #FFFFFF !important;
    color: #334155 !important;
    font-weight: 500 !important;
    padding: 10px 14px !important;
    font-size: 13px !important;
    text-align: left !important;
    box-shadow: 0 1px 2px rgba(0,0,0,0.05) !important;
    white-space: normal !important;
    height: auto !important;
    min-height: 52px;
}}

.stButton button:hover {{
    border-color: {GROWW_GREEN} !important;
    color: {GROWW_DARK_GREEN} !important;
    background-color: #F0FDF4 !important;
}}

/* Sidebar Safe Disclaimer Box */
.sidebar-disclaimer {{
    background-color: #F8FAFC;
    padding: 14px;
    border-radius: 8px;
    border: 1px solid {BORDER_COLOR};
    border-left: 4px solid #64748B;
    font-size: 12px;
    color: #475569;
    line-height: 1.5;
    margin-top: 20px;
}}
/* --- Enhanced User Chat Input Styling --- */
/* Outer Container targeting the stickied bottom container */
div[data-testid="stChatInput"] {{
    border-radius: 12px !important;
    padding: 4px !important;
    background-color: #FFFFFF !important;
    border: 1px solid {BORDER_COLOR} !important;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.03) !important;
    transition: all 0.2s ease-in-out;
}}

/* Container focus state change */
div[data-testid="stChatInput"]:focus-within {{
    border-color: {GROWW_GREEN} !important;
    box-shadow: 0 4px 16px rgba(0, 208, 156, 0.08) !important;
}}

/* Internal text field overrides */
div[data-testid="stChatInput"] textarea {{
    color: #1E293B !important;
    font-size: 14px !important;
    line-height: 1.5 !important;
    
}}

/* Chat Input Send Button Customizations */
div[data-testid="stChatInput"] button {{
    background-color: #F8FAFC !important;
    border-radius: 8px !important;
    color: #64748B !important;
    transition: all 0.2s ease;
}}

/* Active/Hover states for the chat action button */
div[data-testid="stChatInput"] button:hover {{
    background-color: {GROWW_GREEN} !important;
    color: #FFFFFF !important;
}}
</style>
""", unsafe_allow_html=True)

logo_img = (
    f'<img src="data:image/webp;base64,{logo_base64}" width="32" style="vertical-align: middle; margin-right: 6px;"/>'
    if logo_base64 else "📊 "
)

# ---------- Sidebar Surface Layer ----------
with st.sidebar:
    st.markdown(f"### {logo_img}Groww", unsafe_allow_html=True)
    st.title("Mutual Fund FAQ")
    
    st.markdown("""
Facts-only assistant built using **RAG** architecture.

### Data Scope
- SBI Mutual Fund
- AMC Portal Data
- AMFI Regulations
- SEBI Guidelines

---

### Topics Indexed
- Expense Ratio 
- ELSS lock-in period
- SIP Minimum Thresholds
- Exit Load
- Riskometer/benchmark
""")
    
    st.markdown("---")
    if st.button("🗑 Clear Chat History", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    # Fixed placement avoiding chat_input window layout collisons entirely
    st.markdown("""
    <div class="sidebar-disclaimer">
        <b>Regulatory Disclaimer:</b><br>
        This assistant answers **only factual questions** using official public documents from official sources.

It **does not provide investment advice, recommendations, or return predictions.
    </div>
    """, unsafe_allow_html=True)

# ---------- Main Workspace Header ----------
st.markdown("<h1>Groww — RAG-Based Mutual Fund FAQ Assistant</h1>", unsafe_allow_html=True)

st.markdown("""
<div class="top-fixed">
    <div class="top-caption">
        🛡️ Facts-only • Official Sources • No Investment Advice
    </div>
</div>
""", unsafe_allow_html=True)

# ---------- Suggested Enquiries Block ----------
examples = [
    "What is the expense ratio of SBI Small Cap Fund?",
    "What is the exit load of SBI Gold Direct Plan Growth?",
    "What is the minimum SIP amount for SBI Equity Hybrid Fund?"
]

if "messages" not in st.session_state:
    st.session_state.messages = []

st.markdown('<div class="suggested-title">💡 Suggested Enquiries</div>', unsafe_allow_html=True)
col1, col2, col3 = st.columns(3)

clicked_prompt = None
with col1:
    if st.button(examples[0], key="s1", use_container_width=True):
        clicked_prompt = examples[0]
with col2:
    if st.button(examples[1], key="s2", use_container_width=True):
        clicked_prompt = examples[1]
with col3:
    if st.button(examples[2], key="s3", use_container_width=True):
        clicked_prompt = examples[2]

# ---------- Chat Execution & Processing ----------
prompt = st.chat_input("Ask a factual rule or compliance question...")

if clicked_prompt:
    prompt = clicked_prompt

# Core messaging stack rendering
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg["role"] == "assistant" and msg.get("source"):
            st.markdown(f"""
            <div class="source-box">
                <b>Source Document:</b><br>
                <a href="{msg['source']}" target="_blank">{msg['source']}</a>
            </div>
            """, unsafe_allow_html=True)

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Querying knowledge base..."):
            try:
                result = answer_query(prompt)
                answer = result.get("answer", "No descriptive answer variants located inside current document indexes.")
                source = result.get("source", "")
                
                st.markdown(answer)
                if source:
                    st.markdown(f"""
                    <div class="source-box">
                        <b>Source Document:</b><br>
                        <a href="{source}" target="_blank">{source}</a>
                    </div>
                    """, unsafe_allow_html=True)
                
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer,
                    "source": source
                })
            except Exception as e:
                st.error(f"Error processing question: {e}")
                
    if clicked_prompt:
        st.rerun()