# utils/loader.py
import os
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from utils.embedder import get_embedding_model

def ingest_documents():
    data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
    db_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "chroma_db")
    
    documents = []
    if not os.path.exists(data_dir):
        return "Data folder missing!"

    # Read all text files in the data directory
    for file in os.listdir(data_dir):
        if file.endswith(".txt"):
            with open(os.path.join(data_dir, file), "r", encoding="utf-8") as f:
                documents.append(f.read())

    if not documents:
        return "No documents found to index."

    # Chunking Math
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=700, chunk_overlap=100)
    split_docs = text_splitter.create_documents(documents)

    # Initialize and save to ChromaDB
    embeddings = get_embedding_model()
    Chroma.from_documents(split_docs, embeddings, persist_directory=db_dir)
    return f"Successfully indexed {len(split_docs)} text chunks!"