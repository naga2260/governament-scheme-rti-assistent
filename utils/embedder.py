# utils/embedder.py
import os
import streamlit as st
from langchain_google_genai import GoogleGenerativeAIEmbeddings

def get_embedding_model():
    # Fetch API Key from Vercel Environment Variables or local Streamlit secrets
    api_key = os.environ.get("GOOGLE_API_KEY") or st.secrets.get("GOOGLE_API_KEY")
    
    if not api_key:
        raise ValueError("GOOGLE_API_KEY is missing! Add it to Vercel Environment Variables.")
        
    return GoogleGenerativeAIEmbeddings(
        model="models/embedding-001",
        google_api_key=api_key
    )