import os
import json
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

load_dotenv()

DATA_DIR = os.getenv("DATA_DIR", "data")
VECTOR_DIR = os.getenv("VECTOR_DIR", "vectorstore")
URL_MAPPING_FILE = os.path.join(DATA_DIR, "url_mapping.json")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")


def load_url_mapping():
    """Load URL to filename mapping"""
    if os.path.exists(URL_MAPPING_FILE):
        with open(URL_MAPPING_FILE, 'r') as f:
            return json.load(f)
    return {}


def load_pdfs():
    docs = []
    url_mapping = load_url_mapping()

    for file in os.listdir(DATA_DIR):
        if file.endswith(".pdf"):
            path = os.path.join(DATA_DIR, file)
            loader = PyPDFLoader(path)
            pdf_docs = loader.load()

            # ✅ Add source metadata with URL
            for d in pdf_docs:
                # Use URL from mapping if available, else use filename
                d.metadata["source"] = url_mapping.get(file, f"https://www.sbimf.com/{file}")
                d.metadata["filename"] = file

            docs.extend(pdf_docs)

    return docs


def split_docs(documents):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        separators=["\n\n", "\n", ". ", " ", ""]
    )
    return splitter.split_documents(documents)


def create_vectorstore():
    print("📥 Loading PDFs...")
    documents = load_pdfs()

    print(f"✅ Loaded {len(documents)} pages")

    print("✂️ Splitting documents...")
    chunks = split_docs(documents)

    print(f"✅ Created {len(chunks)} chunks")

    print("🧠 Creating embeddings...")
    embeddings = HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL
    )

    db = FAISS.from_documents(chunks, embeddings)

    if not os.path.exists(VECTOR_DIR):
        os.makedirs(VECTOR_DIR)

    db.save_local(VECTOR_DIR)

    print("✅ Vectorstore created successfully!")


if __name__ == "__main__":
    create_vectorstore()