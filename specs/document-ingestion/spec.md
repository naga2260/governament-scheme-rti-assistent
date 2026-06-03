# Document Ingestion Feature Specification

## Metadata

- **Title:** Document Ingestion & Vectorization
- **Status:** Complete
- **Owner:** Development Team
- **Created:** 2024-06-03
- **Target Release:** v0.1.0

## Overview

The Document Ingestion feature loads government welfare scheme documents from multiple sources (text files, PDFs) and converts them into vector embeddings stored in the Chroma vector database. This indexing process powers the RAG pipeline by making documents searchable by semantic similarity. The system handles:
- Loading and parsing scheme documents from `data/` and `data_pdfs/` directories
- Text chunking and preprocessing
- Vector embedding generation
- Persistent storage in Chroma vector store
- Caching to avoid re-processing

## Acceptance Criteria

- [x] Load scheme documents from data/ directory (50+ .txt files)
- [x] Parse and chunk documents for RAG compatibility
- [x] Generate embeddings via Google Generative AI
- [x] Store embeddings in Chroma vector database
- [x] Cache ingested data to avoid re-processing
- [x] Support both text and PDF formats
- [x] Validate document quality and completeness

## Scope

### In Scope
- Load .txt files from data/ directory
- Load .pdf files from data_pdfs/ directory
- Parse and extract text content
- Intelligent text chunking (preserve context, handle boundaries)
- Embed documents with GoogleGenerativeAIEmbeddings
- Persist embeddings to Chroma
- Caching for performance (avoid re-processing)
- Error handling for malformed documents

### Out of Scope
- OCR for scanned PDFs (assumed clean PDFs)
- Document validation against government sources
- Real-time document updates (batch process only)
- Metadata extraction (title, author, date handled manually)

## Design & Architecture

### High-Level Design

```
Scheme Documents
  (data/ .txt files, data_pdfs/ PDFs)
    ↓
Document Loading
  - Read files from filesystem
  - Parse content (text extraction for PDFs)
    ↓
Text Preprocessing
  - Clean whitespace, encoding issues
  - Extract relevant sections
    ↓
Text Chunking
  - Split into semantic chunks (300-500 tokens)
  - Preserve context boundaries
    ↓
Embedding Generation
  - GoogleGenerativeAIEmbeddings wrapper
  - Batch process for efficiency
    ↓
Vector Store Ingestion
  - Store in Chroma (chroma_db/)
  - Associate metadata (filename, source, date)
    ↓
Caching
  - Cache processed embeddings in Streamlit
  - Re-use across sessions
    ↓
Ready for RAG Pipeline Queries
```

### Key Components

- **Document Loader (`utils/loader.py`):** File I/O, PDF parsing, text extraction
- **Embedder (`utils/embedder.py`):** GoogleGenerativeAIEmbeddings wrapper
- **Vector Store:** Chroma persistent database in `chroma_db/`
- **Cache:** Streamlit `@st.cache_resource` for expensive operations
- **Metadata:** Track source, document type, ingestion date

### API & Integration Points

```python
# Document loader interface
def ingest_documents(
    data_dir: str = "data",
    pdf_dir: str = "data_pdfs"
) -> List[Document]:
    """Load and ingest scheme documents from data sources."""

def create_vector_store(
    documents: List[Document],
    embedder: Embeddings
) -> VectorStore:
    """Create Chroma vector store from documents."""

def chunk_documents(
    raw_documents: List[Document],
    chunk_size: int = 500,
    overlap: int = 50
) -> List[Document]:
    """Chunk documents for RAG compatibility."""
```

## Implementation Details

### Technology Choices

1. **Chroma Vector Database:**
   - Chosen for: Lightweight, local storage, Langchain integration
   - Benefits: No external service, persistent storage, semantic search

2. **GoogleGenerativeAIEmbeddings:**
   - Chosen for: Multilingual support, cost-effective free tier
   - Model: `models/embedding-001` (Google's default)

3. **Text Chunking Strategy:**
   - Chosen for: Langchain's RecursiveCharacterTextSplitter
   - Chunk size: 500 tokens (balance context vs. specificity)
   - Overlap: 50 tokens (preserve context across chunks)

4. **PDF Processing:**
   - Chosen for: PyPDF2 or pdfplumber (simple, no ML needed)
   - Approach: Extract text, treat same as .txt files

### Document Processing Pipeline

```python
# Pseudo-code pipeline
documents = load_files("data/", "data_pdfs/")
documents = chunk_documents(documents, size=500, overlap=50)
embedder = GoogleGenerativeAIEmbeddings()
vector_store = Chroma.from_documents(documents, embedder)
vector_store.persist()
```

### Caching Strategy

- **Streamlit Cache:** `@st.cache_resource` for document loading and embedding
- **Persistent Storage:** Chroma DB saved to disk (`chroma_db/`)
- **Invalidation:** Manual invalidation or time-based TTL if document updates needed
- **Memory:** Cache embeddings in memory for fast retrieval within session

### Error Handling

- **Missing files:** Log and skip, continue with available documents
- **Parse errors:** Log PDF/text parsing failures, include in error report
- **Encoding issues:** Detect and handle UTF-8, Unicode, mixed encoding
- **Empty documents:** Skip documents with no meaningful content

### Testing Strategy

- **Unit Tests:** Test file loading, text chunking, metadata extraction
- **Integration Tests:** End-to-end ingestion → vector store creation
- **Data Validation Tests:** Verify 50+ documents loaded, embeddings generated
- **Performance Tests:** Measure ingestion time for 10K+ documents

## Multilingual Support
- [x] Support both English and Telugu scheme documents
- [x] Handle multilingual text in embeddings
- [x] Preserve language metadata

## Dependencies & Risks

### External Dependencies
- langchain-text-splitters (text chunking)
- chromadb >= 0.3.21 (vector store)
- pdfplumber or PyPDF2 (PDF parsing)
- google-generativeai (embeddings)

### Risks

| Risk | Impact | Mitigation |
|------|--------|-----------|
| Large PDF files (1000+ pages) | Medium | Stream processing, batch ingestion |
| Memory overflow from 10K+ docs | Medium | Batch processing, clear cache between batches |
| Encoding issues in scheme documents | Low | Auto-detect encoding, log problematic files |
| Chroma DB corruption | Medium | Regular backups, validation on startup |
| API quota exceeded during ingestion | Low | Batch API calls, implement rate limiting |

### Performance Impact

- **Ingestion Time:** ~30 seconds for 50 scheme documents (with caching: 1st load only)
- **Memory:** ~1-2GB for loaded embeddings
- **Storage:** ~100MB for Chroma DB with 50 documents

## Acceptance & Validation

### Definition of Done
- [x] All 50+ scheme documents successfully loaded
- [x] Documents properly chunked (500-token chunks)
- [x] Embeddings generated for all chunks
- [x] Chroma vector store created and persisted
- [x] Caching working (no re-ingestion on app restart)
- [x] Error handling tested with malformed files
- [x] Unit and integration tests pass
- [x] Code review approved

### Validation Steps
1. Count documents loaded: `len(documents)` >= 50
2. Verify chunking: Sample chunk length 300-700 tokens (500 avg)
3. Test vector store: Query "MGNERGA" returns MGNERGA document in top 5
4. Check storage: `chroma_db/` directory contains persisted vectors
5. Verify cache: App restart loads documents from cache (< 1s)

## Timeline & Effort

- **Estimated Effort:** 15 hours
- **Implementation Plan:** See `plan.md`
- **Task Breakdown:** See `tasks.md`
- **Status:** ✅ Complete

## Known Issues & Limitations

- **Limitation 1:** Only supports scheme documents; not generic government documents
- **Limitation 2:** Requires documents in `data/` or `data_pdfs/`; dynamic document upload not yet supported
- **Limitation 3:** Chunking strategy optimized for scheme documents; may need tuning for other document types
- **Limitation 4:** No duplicate detection across multiple PDF/text sources

## References

- [Plan](plan.md) - Implementation strategy
- [Tasks](tasks.md) - Task breakdown
- [Constitution](../../.specify/memory/constitution.md) - Project standards
- LangChain Text Splitters: https://python.langchain.com/docs/modules/data_connection/document_loaders/

---

**Status:** ✅ Feature Complete
**Last Updated:** 2024-06-03
