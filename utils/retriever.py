# utils/retriever.py
import os
from langchain_chroma import Chroma
from langchain_community.llms import Ollama
from utils.embedder import get_embedding_model

DB_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "chroma_db")

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
    if not os.path.exists(DB_DIR):
        return "Database not initialized. Please click Ingest in the sidebar.", []

    embeddings = get_embedding_model()
    db = Chroma(persist_directory=DB_DIR, embedding_function=embeddings)
    retrieved_docs = db.similarity_search(user_query, k=2)
    
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
        llm = Ollama(model="qwen2.5:7b", temperature=0.2)
        return llm.invoke(system_prompt), retrieved_docs
    except Exception as e:
        return f"Could not connect to Ollama: {e}", []