# RAG-based Mutual Fund FAQ Chatbot

## Overview
A RAG-based FAQ assistant for SBI Mutual Fund schemes that provides factual answers with source citations. This assistant is designed for **Groww** users to quickly get factual information about SBI Mutual Fund schemes.

**Product Context:** Built for Groww platform users comparing SBI Mutual Fund schemes.

**AMC:** SBI Mutual Fund

## Features
- ✅ Facts-only answers from official public pages
- ✅ Source citation in every answer (prioritizes Groww URLs)
- ✅ No investment advice (refuses opinionated questions)
- ✅ Simple, user-friendly interface with Groww branding
- ✅ Example questions for quick start
- ✅ Web scraping from Groww mutual fund pages
- ✅ PDF ingestion from SBI MF factsheets

## Scope
**AMC**: SBI Mutual Fund

**Schemes Covered** (15+ schemes):
1. SBI Gold Fund Direct Plan Growth
2. SBI Small Midcap Fund Direct Plan Growth
3. SBI Contra Fund Direct Plan Growth
4. SBI Magnum Multiplier Fund Direct Plan Growth
5. SBI ELSS Tax Saver Fund Direct Plan Growth
6. SBI Large Cap Fund Direct Plan Growth
7. SBI Mid Cap Fund Direct Plan Growth
8. SBI Premier Liquid Fund Direct Plan Growth
9. SBI Magnum Balanced Fund Direct Plan Growth
10. SBI Multicap Fund Direct Plan Growth
11. SBI Nifty Smallcap 250 Index Fund Direct Plan Growth
12. SBI Flexicap Fund Direct Plan Growth
13. SBI Quality Fund Direct Plan Growth
14. SBI Retirement Benefit Fund Direct Plan Growth
15. SBI Equity Savings Fund Direct Plan Growth

Supported query types:
- Expense ratio
- Exit load
- Minimum SIP/Lumpsum investment
- Lock-in period (ELSS)
- Riskometer/benchmark
- Fund size (AUM)
- NAV information
- Fund details and objectives

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

5. Update the `data/sources.csv` file with your source URLs and metadata (scheme, title, publisher, document_type).

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
ragchatbot/
├── app.py                 # Streamlit frontend UI
├── main.py                # FastAPI backend API
├── requirements.txt       # Python dependencies
├── architecture.md        # System architecture documentation
├── sample_qa.md          # Sample Q&A examples
├── inspect_vectorstore.py # Vector store inspection utility
├── data/
│   ├── sources.csv        # Source URLs and metadata configuration
│   ├── groww_logo.webp    # Groww logo for UI
│   └── *.pdf             # Source documents (factsheets, regulations)
├── src/
│   ├── ingest.py         # Document ingestion pipeline
│   ├── retriever.py      # RAG retrieval logic
│   ├── qa.py            # Question answering with guardrails
│   ├── vectorstore.py   # FAISS vector store management
│   ├── web_loader.py   # Web scraping from Groww
│   ├── guardrails.py   # Investment advice detection
│   ├── prompt.py       # LLM prompt templates
│   ├── metadata.py     # Metadata management
│   ├── pdf_loader.py   # PDF loading utilities
│   └── scraper.py      # Web scraping utilities
└── vectorstore/          # FAISS vector database (generated)
```

## Disclaimer
This assistant provides factual information only based on official public documents. It does not provide investment advice. Please consult a SEBI-registered investment advisor for investment decisions.
