# Document Ingestion Implementation Plan

## Overview

Build the document ingestion pipeline that loads scheme documents and converts them to vector embeddings for RAG queries.

## Implementation Strategy

### Phase 1: Document Loading
**Goal:** Load and parse documents from data sources

**Files to Create:**
- `utils/loader.py` - File I/O and document parsing

**Key Implementation:**
- Load .txt files from `data/` directory
- Parse PDFs from `data_pdfs/` directory
- Extract text content and metadata

### Phase 2: Text Processing
**Goal:** Prepare documents for embedding

**Key Implementation:**
- Clean and normalize text
- Chunk documents into semantic pieces (500 tokens)
- Preserve context and boundaries
- Handle encoding issues

### Phase 3: Vectorization
**Goal:** Generate embeddings and store in vector database

**Files to Modify:**
- `utils/embedder.py` - Embeddings integration
- Create Chroma vector store

### Phase 4: Caching & Optimization
**Goal:** Optimize performance with caching

**Key Implementation:**
- Cache processed documents with `@st.cache_resource`
- Persist vector store to disk
- Re-use cached embeddings across sessions

## References

See `spec.md` for full feature specification
