# utils/embedder.py
from langchain_community.embeddings import HuggingFaceEmbeddings

def get_embedding_model():
    # BGE-M3 or MiniLM handle multilingual data beautifully
    model_name = "BAAI/bge-small-en-v1.5" 
    encode_kwargs = {'normalize_embeddings': True}
    return HuggingFaceEmbeddings(
        model_name=model_name,
        encode_kwargs=encode_kwargs
    )