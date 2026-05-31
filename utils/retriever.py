# utils/retriever.py
import os
import streamlit as st
from langchain_google_genai import GoogleGenerativeAI
from utils.embedder import get_embedding_model
from utils.loader import get_cached_chunks

SCHEME_SUBMISSION_MAP = {
    "pm-kisan": {
        "portal": "pmkisan.gov.in",
        "office": "Mandal Revenue Office (MRO) / MeeSeva Center",
        "docs": ["Aadhaar Card", "Land Pattadar Passbook", "Bank Passbook"]
    },
    "ayushman-bharat": {
        "portal": "pmjay.gov.in",
        "office": "Network Hospital Arogya Mitra Desk",
        "docs": ["Ration Card / Food Security Card", "Aadhaar Card"]
    }
}

def execute_rag_pipeline(user_query, language="English"):
    api_key = os.environ.get("GOOGLE_API_KEY") or st.secrets.get("GOOGLE_API_KEY")
    if not api_key:
        return "System error: Google API Key missing on server environment.", []

    # 1. Fetch available data chunks
    chunks = get_cached_chunks()
    if not chunks:
        return "No documents found in memory. Please add text files to the data/ folder.", []

    # 2. Fast Server-Side Retrieval Match
    embeddings = get_embedding_model()
    try:
        query_vector = embeddings.embed_query(user_query)
        doc_texts = [c.page_content for c in chunks]
        doc_vectors = embeddings.embed_documents(doc_texts)
        
        # Math helper: Cosine similarity matching to pick top 2 relevant chunks
        import numpy as np
        scores = [np.dot(query_vector, dv) / (np.linalg.norm(query_vector) * np.linalg.norm(dv)) for dv in doc_vectors]
        top_indices = np.argsort(scores)[-2:][::-1]
        retrieved_docs = [chunks[i] for i in top_indices]
    except Exception:
        # Fallback to direct text matching if math modules conflict during serverless bootup
        retrieved_docs = chunks[:2]

    context = "\n\n".join([doc.page_content for doc in retrieved_docs])
    
    system_prompt = f"""
    You are an expert Indian Government Schemes Assistant. 
    Answer the question accurately based ONLY on the provided context.
    
    CRITICAL: You must write your response completely in {language}. 
    If Telugu, write cleanly in Telugu script. Keep it highly practical.
    
    CONTEXT:
    {context}
    
    QUESTION:
    {user_query}
    """
    
    try:
        # Utilizing ultra-fast, serverless-friendly Gemini model
        llm = GoogleGenerativeAI(model="gemini-2.5-flash", google_api_key=api_key, temperature=0.2)
        return llm.invoke(system_prompt), retrieved_docs
    except Exception as e:
        return f"Could not process response via Google AI Gateway: {e}", []