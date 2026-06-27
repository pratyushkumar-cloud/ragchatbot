import os
from dotenv import load_dotenv
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

load_dotenv()

def inspect_vectorstore():
    """Load and inspect the vector store"""
    vector_dir = os.getenv("VECTOR_DIR", "vectorstore")
    embedding_model = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
    
    print(f"Loading vector store from: {vector_dir}")
    print(f"Using embedding model: {embedding_model}")
    print("-" * 50)
    
    # Load embeddings
    embeddings = HuggingFaceEmbeddings(model_name=embedding_model)
    
    # Load vector store
    db = FAISS.load_local(vector_dir, embeddings, allow_dangerous_deserialization=True)
    
    # Get the index
    index = db.index
    
    print(f"Vector store loaded successfully!")
    print(f"Total vectors: {index.ntotal}")
    print(f"Dimension: {index.d}")
    print("-" * 50)
    
    # Get retriever
    retriever = db.as_retriever(search_kwargs={"k": 3})
    
    # Test a query
    test_query = "What is the expense ratio?"
    print(f"Testing query: '{test_query}'")
    print("-" * 50)
    
    docs = retriever.invoke(test_query)
    
    print(f"Found {len(docs)} relevant documents:")
    for i, doc in enumerate(docs, 1):
        print(f"\n--- Document {i} ---")
        print(f"Source: {doc.metadata.get('source', 'Unknown')}")
        print(f"Content preview: {doc.page_content[:200]}...")
    
    print("\n" + "=" * 50)
    print("Vector store inspection complete!")

if __name__ == "__main__":
    inspect_vectorstore()
