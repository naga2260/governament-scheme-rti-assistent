# # utils/loader.py
import os
import streamlit as st
from langchain_text_splitters import RecursiveCharacterTextSplitter

@st.cache_resource
def get_cached_chunks():
    """Reads raw data files once and holds chunks in web server memory."""
    data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
    documents = []
    
    # Create the folder if missing
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
        
    # Default initial fallback text if files aren't uploaded yet
    default_files = {
        "pm_kisan.txt": "PM-Kisan scheme provides ₹6,000 per year in three equal installments to eligible landholding farmers.",
        "ayushman_bharat.txt": "Ayushman Bharat PM-JAY offers health cover up to ₹5 Lakhs per family per year for secondary care hospitalization."
    }
    
    for filename, text in default_files.items():
        filepath = os.path.join(data_dir, filename)
        if not os.path.exists(filepath):
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(text)

    # Read files
    for file in os.listdir(data_dir):
        if file.endswith(".txt"):
            with open(os.path.join(data_dir, file), "r", encoding="utf-8") as f:
                documents.append(f.read())

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    return text_splitter.create_documents(documents)

def ingest_documents():
    # Force a refresh of the cached data chunks
    get_cached_chunks.clear()
    chunks = get_cached_chunks()
    return f"Successfully indexed {len(chunks)} text chunks into Cloud memory!"      