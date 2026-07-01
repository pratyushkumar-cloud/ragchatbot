# System Architecture

## Overview
This RAG-based Mutual Fund FAQ Chatbot uses a Retrieval-Augmented Generation architecture to provide factual answers about SBI Mutual Fund schemes with source citations. The system is designed for Groww platform users and refuses investment advice questions.

**Architecture Type:** Single-file Streamlit application with integrated RAG pipeline for simplified deployment on Streamlit Cloud.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    Streamlit Application (app.py)                │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │         User Interface Layer                              │  │
│  │  - Chat interface with Groww branding                   │  │
│  │  - Suggested questions                                   │  │
│  │  - Source citation display                               │  │
│  │  - Chat history management                               │  │
│  └────────────────────┬─────────────────────────────────────┘  │
│                       │                                          │
│  ┌────────────────────┴─────────────────────────────────────┐  │
│  │         Question Answering Layer (Integrated)             │  │
│  │  - Guardrails (advice detection)                         │  │
│  │  - Retrieval from vector store                          │  │
│  │  - LLM generation with context                          │  │
│  │  - Source citation (web sources prioritized)            │  │
│  └────────────────────┬─────────────────────────────────────┘  │
│                       │                                          │
└───────────────────────┼─────────────────────────────────────────┘
                        │
        ┌───────────────┼───────────────┐
        │               │               │
        ▼               ▼               ▼
┌───────────────┐ ┌───────────────┐ ┌───────────────┐
│  Retrieval    │ │   LLM         │ │  Guardrails   │
│  Layer        │ │   Layer       │ │  Layer        │
├───────────────┤ ├───────────────┤ ├───────────────┤
│ retriever.py  │ │ Groq API      │ │ guardrails.py │
│ - FAISS       │ │ - llama-3.3   │ │ - Advice      │
│   search      │ │   -70b        │ │   detection   │
│ - k=6         │ │ - temp=0      │ │ - Generic     │
│   retrieval   │ │               │ │   advice      │
└───────────────┘ └───────────────┘ └───────────────┘
        │
        ▼
┌──────────────────────────────────────────────────────────┐
│              Vector Store Layer                           │
│  ┌────────────────────────────────────────────────────┐  │
│  │         vectorstore.py - FAISS Management         │  │
│  │  - Load/save vector store                         │  │
│  │  - Embedding model: all-MiniLM-L6-v2             │  │
│  │  - Dimension: 384                                 │  │
│  └────────────────────┬───────────────────────────────┘  │
└───────────────────────┼──────────────────────────────────┘
                        │
        ┌───────────────┼───────────────┐
        │               │               │
        ▼               ▼               ▼
┌───────────────┐ ┌───────────────┐ ┌───────────────┐
│  Document     │ │   Web         │ │  Metadata     │
│  Ingestion    │ │   Scraping    │ │  Management   │
├───────────────┤ ├───────────────┤ ├───────────────┤
│ ingest.py     │ │ web_loader.py │ │ metadata.py   │
│ - PDF loading │ │ - BeautifulSoup│ │ - Source      │
│ - Web loading │ │ - requests    │ │   mapping     │
│ - Chunking    │ │ - Groww       │ │ - Document    │
│ - Embedding   │ │   scraping    │ │   types      │
└───────────────┘ └───────────────┘ └───────────────┘
        │
        ▼
┌──────────────────────────────────────────────────────────┐
│              Data Sources Layer                           │
│  ┌────────────────────────────────────────────────────┐  │
│  │         sources.csv - Source Configuration        │  │
│  │  - URL, type, scheme, title, publisher, type      │  │
│  │  - Web sources: Groww mutual fund pages          │  │
│  │  - PDF sources: SBI MF factsheets, AMFI, SEBI    │  │
│  └────────────────────┬───────────────────────────────┘  │
│                       │                                      │
│  ┌────────────────────┴───────────────────────────────┐  │
│  │  data/ Directory                                      │  │
│  │  - PDF factsheets (SBI MF schemes)                 │  │
│  │  - AMFI investor education PDFs                     │  │
│  │  - SEBI regulatory PDFs                             │  │
│  │  - Groww logo                                      │  │
│  └────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────┘
```

## Component Details

### 1. Streamlit Application (app.py)
- **Framework**: Streamlit
- **Architecture**: Single-file application with integrated RAG pipeline
- **Features**:
  - Chat interface with Groww branding
  - Suggested questions for quick start
  - Source citation display with clickable links
  - Chat history management
  - Responsive CSS styling
  - Clear chat history functionality
  - Integrated QA logic (no separate backend required)
- **Caching**: Uses `@st.cache_resource` for retriever and LLM initialization

### 2. Question Answering Layer (Integrated in app.py)
- **Components**:
  - **Guardrails**: Detects and refuses investment advice questions
  - **Retrieval**: Fetches relevant documents from vector store
  - **Generation**: Uses LLM to generate answers with context
  - **Citation**: Prioritizes web sources for source URLs
- **LLM**: Groq - llama-3.3-70b-versatile (temperature=0)

### 3. Retrieval Layer
- **File**: `retriever.py`
- **Technology**: FAISS vector store
- **Embedding Model**: sentence-transformers/all-MiniLM-L6-v2
- **Configuration**: k=6, score_threshold=0.2
- **Function**: Semantic search over document chunks

### 4. Vector Store Layer
- **File**: `vectorstore.py`
- **Technology**: FAISS (Facebook AI Similarity Search)
- **Storage**: Local disk (`vectorstore/` directory)
- **Dimensions**: 384 (from embedding model)
- **Features**: Load/save functionality, embedding generation

### 5. Document Ingestion Layer
- **File**: `ingest.py`
- **Components**:
  - **PDF Loading**: PyPDFLoader, UnstructuredPDFLoader (fallback)
  - **Web Scraping**: WebLoader with BeautifulSoup + requests
  - **Chunking**: RecursiveCharacterTextSplitter (chunk_size=700, overlap=150)
  - **Metadata Assignment**: Maps documents to sources.csv entries
- **Process**:
  1. Load sources from sources.csv
  2. Load PDFs from data/ directory
  3. Scrape web pages from Groww
  4. Split documents into chunks
  5. Generate embeddings
  6. Create FAISS vector store

### 6. Guardrails Layer
- **File**: `guardrails.py`
- **Features**:
  - Investment advice detection
  - Generic advice filtering
  - Not-found response handling
- **Purpose**: Ensures system only provides factual information

### 7. Data Sources
- **Configuration**: `data/sources.csv`
- **Web Sources**: Groww mutual fund pages (15 schemes)
- **PDF Sources**: 
  - SBI MF factsheets (monthly)
  - SBI MF passives factsheets
  - AMFI investor education
  - SEBI regulatory documents
  - SID/KIM documents

## Data Flow

### Ingestion Flow
1. **Source Configuration**: Load `sources.csv`
2. **Document Loading**:
   - PDFs: Load from `data/` directory
   - Web: Scrape from Groww URLs
3. **Metadata Assignment**: Match documents to sources.csv entries
4. **Chunking**: Split documents into 700-character chunks with 150-character overlap
5. **Embedding**: Generate embeddings using all-MiniLM-L6-v2
6. **Vector Store**: Create and save FAISS index

### Query Flow
1. **User Input**: User submits question via Streamlit UI
2. **Guardrails Check**: Detect investment advice questions
3. **Retrieval**: Fetch top 6 relevant chunks from FAISS
4. **Context Building**: Combine retrieved chunks with source metadata
5. **LLM Generation**: Generate answer using Groq API
6. **Source Citation**: Prioritize web sources for citation
7. **Response**: Display answer with source URL in UI

## Key Design Decisions

### Web Source Prioritization
- **Rationale**: Web-scraped content from Groww is the primary data source
- **Implementation**: Filter retrieved documents for HTTP sources before citation
- **Benefit**: Ensures accurate source attribution to Groww URLs

### Guardrails
- **Rationale**: Regulatory compliance - no investment advice
- **Implementation**: Pattern matching for advice keywords
- **Benefit**: Prevents liability and maintains factual-only scope

### FAISS Vector Store
- **Rationale**: Fast similarity search for large document collections
- **Implementation**: Local disk storage with AVX2 optimization
- **Benefit**: Efficient retrieval without external dependencies

### Chunking Strategy
- **Rationale**: Balance between context preservation and retrieval precision
- **Implementation**: 700-character chunks with 150-character overlap
- **Benefit**: Maintains context while enabling granular retrieval

### Single-File Architecture
- **Rationale**: Simplified deployment for Streamlit Cloud
- **Implementation**: Integrated QA logic directly into Streamlit app
- **Benefit**: No separate backend required, easier deployment and maintenance
- **Caching**: Uses Streamlit's `@st.cache_resource` for efficient resource management

## Technology Stack

### Frontend & Application
- Streamlit (UI framework + application logic)
- Custom CSS (styling)
- LangChain (orchestration)

### RAG Pipeline
- LangChain (orchestration)
- FAISS (vector similarity)
- sentence-transformers (embeddings)
- Groq (LLM inference)

### Data Processing
- PyPDF (PDF parsing)
- Unstructured (PDF fallback)
- BeautifulSoup (web scraping)
- Requests (HTTP client)

## Environment Variables

```env
GROQ_API_KEY=your_groq_api_key_here
BACKEND_URL=http://localhost:8000
DATA_DIR=data
VECTOR_DIR=vectorstore
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
LLM_MODEL=llama-3.3-70b-versatile
LLM_TEMPERATURE=0
```

## Performance Characteristics

- **Vector Store Size**: ~6,529 chunks (current)
- **Embedding Dimension**: 384
- **Retrieval Time**: <100ms (FAISS)
- **LLM Generation Time**: 1-3 seconds (Groq)
- **Total Response Time**: 2-5 seconds

## Scalability Considerations

- **Vector Store**: Can handle millions of vectors with FAISS
- **Document Ingestion**: Batch processing for large document sets
- **API**: FastAPI supports async operations for concurrent requests
- **Frontend**: Streamlit is stateless, can be deployed with load balancers
