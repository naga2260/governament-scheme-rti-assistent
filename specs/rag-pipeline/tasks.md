# RAG Pipeline Tasks

## Phase 1: Core Setup

- [ ] Create `utils/embedder.py` with GoogleGenerativeAIEmbeddings wrapper
- [ ] Create `utils/retriever.py` with LangChain RAG setup
- [ ] Initialize Chroma vector store connection
- [ ] Set up Google API client with environment variable

## Phase 2: Document Integration

- [ ] Load documents from `data/` directory
- [ ] Generate embeddings for all documents
- [ ] Store embeddings in Chroma vector database
- [ ] Implement caching with `@st.cache_resource`

## Phase 3: Query & Response

- [ ] Create retrieval function for semantic search
- [ ] Set up LangChain RetrievalQA chain
- [ ] Implement query processing (English & Telugu)
- [ ] Add source attribution to responses

## Phase 4: UI Integration

- [ ] Add query input box to Streamlit app
- [ ] Display responses with formatting
- [ ] Add language selector for Telugu support
- [ ] Show retrieved document sources

## Phase 5: Testing & Validation

- [ ] Write unit tests for retriever
- [ ] Test end-to-end query flow
- [ ] Validate response accuracy
- [ ] Performance testing (<5s latency)

## Status: ✅ Complete
