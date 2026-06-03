# RAG Pipeline Feature Specification

## Metadata

- **Title:** Retrieval-Augmented Generation (RAG) Pipeline
- **Status:** Complete
- **Owner:** Development Team
- **Created:** 2024-06-03
- **Target Release:** v0.1.0

## Overview

The RAG pipeline is the core intelligence of the Telangana Welfare Navigator. It retrieves relevant government scheme documents from a vector database (Chroma) and uses Google Generative AI (Gemini) to synthesize intelligent responses about eligibility and scheme details. Users ask questions in English or Telugu, and the system returns curated, scheme-specific answers with source references.

## Acceptance Criteria

- [x] Query processing in English and Telugu
- [x] Document retrieval with relevance scoring
- [x] Response generation using Gemini LLM
- [x] Source attribution for retrieved documents
- [x] Performance: Response time < 5 seconds
- [x] Bilingual UI with language toggle

## Scope

### In Scope
- Vector store initialization (Chroma with GoogleGenerativeAIEmbeddings)
- Query routing for different schemes
- Multi-turn conversation with context preservation
- Streamlit UI with language selection
- Caching of embeddings for performance

### Out of Scope
- Fine-tuning of LLM models
- Advanced prompt engineering (handled in LangChain)
- Custom embedding models (using Google's default)

## Design & Architecture

### High-Level Design

```
User Query (EN/TE)
    ↓
Language Detection / Normalization
    ↓
Vector Embedding (Google Generative AI)
    ↓
Chroma Vector Store Query (Top K results)
    ↓
Document Ranking / Relevance Scoring
    ↓
Prompt Construction (with Retrieved Docs)
    ↓
Gemini LLM Response Generation
    ↓
Response + Source Attribution (EN/TE)
    ↓
Streamlit UI Display
```

### Key Components

- **Embedder (`utils/embedder.py`):** GoogleGenerativeAIEmbeddings wrapper for converting text to vectors
- **Retriever (`utils/retriever.py`):** Core RAG logic, Chroma integration, LangChain setup
- **LLM Client:** Google Generative AI (Gemini) via LangChain
- **Vector Store:** Chroma (persistent in `chroma_db/`)
- **UI Layer (`app.py`):** Streamlit components for query input and response display

### API & Integration Points

```python
# Core retriever interface
def get_retriever(documents: List[Document]) -> Retriever:
    """Initialize and return a RAG retriever with loaded documents."""
    
def generate_response(query: str, lang: str = 'en') -> str:
    """Generate LLM response given user query and language."""
```

## Implementation Details

### Technology Choices

1. **Google Generative AI (Gemini):**
   - Chosen for: Cost-effectiveness, multilingual capability, good quality for welfare scheme queries
   - Alternative considered: OpenAI, but Google's free tier better for project budget
   
2. **Chroma Vector Database:**
   - Chosen for: Lightweight, local storage, no server required
   - Alternative: Pinecone (requires external service), Weaviate (complex setup)
   
3. **LangChain Framework:**
   - Chosen for: Abstracts LLM & embedding complexity, built-in RAG patterns
   - Reduces code: Pre-built chains for question-answering

### Multilingual Support

- **Language Detection:** User selects via session state (`st.session_state['lang']`)
- **Query Normalization:** Normalize Telugu script if needed (currently handled manually)
- **Response Translation:** Responses generated in queried language
- **UI Text:** All UI elements in `UI_TELUGU` and `UI_ENGLISH` dictionaries

### Caching Strategy

- **Embedder:** `@st.cache_resource` prevents re-initialization of Google Generative AI embedder
- **Vector Store:** `@st.cache_resource` for Chroma instance (persistent across sessions)
- **LLM Client:** Cached to avoid reinitializing Gemini connection

### Testing Strategy

- **Unit Tests:** Test retrieval ranking, prompt construction
- **Integration Tests:** End-to-end query → response flow
- **Manual Testing:** Query sample schemes (MGNERGA, PM Kisan, etc.), verify accuracy
- **Performance Testing:** Measure query latency with 10K+ documents

## Multilingual Support
- [x] English UI text finalized
- [x] Telugu translations added (in `utils/retriever.py`)
- [x] Language selector tested

## Dependencies & Risks

### External Dependencies
- google-generativeai >= 0.3.0 (API key required)
- chromadb >= 0.3.21 (local vector store)
- langchain-core, langchain-google-genai, langchain-text-splitters (RAG framework)

### Risks

| Risk | Impact | Mitigation |
|------|--------|-----------|
| Google API quota exceeded | High | Implement rate limiting, cache results aggressively |
| Chroma vector store corruption | Medium | Backup chroma_db/, validate schema on startup |
| Irrelevant search results | Medium | Fine-tune top K retrieval results, implement reranking |
| LLM hallucination | Medium | Add confidence scoring, cite sources explicitly |

### Performance Impact

- **Latency:** First query ~3s (embedding), subsequent <1s (cached)
- **Memory:** Embedder model ~2GB, vector store grows with documents
- **Storage:** Chroma DB ~100MB per 10K documents

## Acceptance & Validation

### Definition of Done
- [x] RAG pipeline retrieves correct documents for test queries
- [x] LLM generates coherent responses
- [x] Telugu queries work end-to-end
- [x] Performance < 5 seconds per query
- [x] No API key hardcoded (uses environment variable)
- [x] Unit and integration tests pass
- [x] Code review approved

### Validation Steps
1. Query: "What is MGNERGA?" → Verify top result is MGNERGA scheme document
2. Query (Telugu): "అర్హత ఎంత?" → Verify response in Telugu
3. Query: "PM Kisan age limit?" → Verify source attributed to PM Kisan doc
4. Load test: 100 concurrent queries → Verify no crashes

## Timeline & Effort

- **Estimated Effort:** 40 hours
- **Implementation Plan:** See `plan.md`
- **Task Breakdown:** See `tasks.md`
- **Status:** ✅ Complete

## Known Issues & Limitations

- **Limitation 1:** Google API free tier rate limits (500 queries/day) — mitigated with aggressive caching
- **Limitation 2:** Telugu script normalization not fully automated — manual input expected
- **Limitation 3:** Scheme data only includes Telangana schemes — future expansion planned for India-wide

## References

- [Plan](plan.md) - Implementation strategy
- [Tasks](tasks.md) - Task breakdown
- [Constitution](../../.specify/memory/constitution.md) - Project standards
- LangChain RAG docs: https://python.langchain.com/docs/use_cases/qa_structured_data

---

**Status:** ✅ Feature Complete
**Last Updated:** 2024-06-03
