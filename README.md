# RAG-based Mutual Fund FAQ Chatbot

## Overview
A RAG-based FAQ assistant for SBI Mutual Fund schemes that provides factual answers with source citations. This assistant is designed for **Groww** users to quickly get factual information about SBI Mutual Fund schemes.

**Product Context:** Built for Groww platform users comparing SBI Mutual Fund schemes.

**AMC:** SBI Mutual Fund

## Features
- ✅ Facts-only answers from official public pages
- ✅ Source citation in every answer
- ✅ No investment advice (refuses opinionated questions)
- ✅ Simple, user-friendly interface
- ✅ Example questions for quick start

## Scope
**AMC**: SBI Mutual Fund

**Schemes Covered** (4 schemes):
1. SBI Blue Chip Fund (Large Cap)
2. SBI Small Cap Fund (Small Cap)
3. SBI Equity Hybrid Fund (Hybrid)
4. SBI ELSS Fund (ELSS - Tax Saving)

Supported query types:
- Expense ratio
- Exit load
- Minimum SIP amount
- Lock-in period (ELSS)
- Riskometer/benchmark
- How to download statements

## Setup Instructions

### Prerequisites
- Python 3.8+
- Groq API key (free at https://console.groq.com/)

### Installation
1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Create a `.env` file in the project root with the following configuration:
```bash
# Copy the .env file and update with your API key
cp .env.example .env
```

3. Update `.env` file with your Groq API key:
```env
GROQ_API_KEY=your_groq_api_key_here
BACKEND_URL=http://localhost:8000
DATA_DIR=data
VECTOR_DIR=vectorstore
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
LLM_MODEL=llama-3.3-70b-versatile
LLM_TEMPERATURE=0
```

**Note:** This project uses free APIs:
- **Groq API** (LLM) - Free tier available at https://console.groq.com/
- **Hugging Face sentence-transformers** (Embeddings) - Completely free, runs locally

4. Download official PDF documents from SBI Mutual Fund, AMFI, and SEBI and place them in the `data/` directory.

5. Update the `data/url_mapping.json` file with your PDF filenames and their corresponding source URLs.

6. Run the ingestion script to create the vector store:
```bash
python src/ingest.py
```

### Running the Application

1. Start the FastAPI backend:
```bash
uvicorn main:app --reload
```

2. In a new terminal, start the Streamlit frontend:
```bash
streamlit run app.py
```

3. Open your browser to `http://localhost:8501`

## Known Limitations
- Only answers questions based on ingested documents
- Limited to SBI Mutual Fund schemes
- Does not handle real-time NAV or market data
- Refuses all investment advice questions
- Requires manual document updates for new information
- Accuracy depends on the quality and recency of source documents

## Project Structure
```
mf-rag-chatbot/
├── app.py                 # Streamlit UI
├── main.py                # FastAPI backend
├── requirements.txt       # Python dependencies
├── sources.md             # List of 25 source URLs
├── sample_qa.md          # Sample Q&A examples
├── data/
│   ├── url_mapping.json  # PDF to URL mapping
│   └── *.pdf             # Source documents
├── src/
│   ├── ingest.py         # Document ingestion
│   ├── retriever.py      # RAG retrieval
│   └── qa.py            # Question answering logic
└── vectorstore/          # FAISS vector database
```

## Disclaimer
This assistant provides factual information only based on official public documents. It does not provide investment advice. Please consult a SEBI-registered investment advisor for investment decisions.
