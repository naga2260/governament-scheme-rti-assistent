# RAG Pipeline Implementation Plan

## Overview

Build the Retrieval-Augmented Generation (RAG) pipeline that retrieves scheme documents and generates intelligent responses using Google Generative AI.

## Implementation Strategy

### Phase 1: Setup Core Components
**Goal:** Initialize embedder, vector store, and LLM client

**Files to Create:**
- `utils/embedder.py` - GoogleGenerativeAIEmbeddings wrapper
- `utils/retriever.py` - RAG pipeline and LangChain setup

**Files to Modify:**
- `app.py` - Import RAG components

### Phase 2: Document Integration
**Goal:** Integrate document loading with RAG pipeline

**Files to Modify:**
- `utils/loader.py` - Integrate with vector store
- `utils/retriever.py` - Add document processing

### Phase 3: UI & Testing
**Goal:** Create Streamlit UI and validate end-to-end

**Files to Modify:**
- `app.py` - Add query interface
- `tests/test_repository_smoke.py` - Add RAG tests

## Key Implementation Details

- Use LangChain's RetrievalQA chain
- Google Generative AI for embeddings and LLM
- Chroma vector store with persistent storage
- Streamlit caching for performance

## References

See `spec.md` for full feature specification
