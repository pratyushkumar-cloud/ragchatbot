import os
from dotenv import load_dotenv
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

load_dotenv()

def get_retriever():
    vector_dir = os.getenv("VECTOR_DIR", "vectorstore")
    embedding_model = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
    
    embeddings = HuggingFaceEmbeddings(
        model_name=embedding_model
    )
    db = FAISS.load_local(vector_dir, embeddings, allow_dangerous_deserialization=True)
    return db.as_retriever(
        search_type="similarity_score_threshold",
        search_kwargs={"k": 5, "score_threshold": 0.3}
    )