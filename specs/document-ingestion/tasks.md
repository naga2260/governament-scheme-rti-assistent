# Document Ingestion Tasks

## Phase 1: File Loading

- [ ] Implement file discovery for `data/` directory
- [ ] Read .txt files and extract content
- [ ] Implement PDF parsing from `data_pdfs/`
- [ ] Handle file encoding (UTF-8, Unicode)

## Phase 2: Text Processing

- [ ] Clean whitespace and normalize text
- [ ] Implement text chunking (500-token chunks)
- [ ] Add context preservation between chunks
- [ ] Handle boundary conditions

## Phase 3: Metadata Management

- [ ] Extract filename and source metadata
- [ ] Add document type (scheme name, category)
- [ ] Store ingestion date and version
- [ ] Create metadata index

## Phase 4: Embedding Generation

- [ ] Initialize GoogleGenerativeAIEmbeddings
- [ ] Batch process documents for efficiency
- [ ] Handle API rate limiting
- [ ] Store embeddings in Chroma vector database

## Phase 5: Persistence & Caching

- [ ] Implement `@st.cache_resource` for caching
- [ ] Persist vector store to `chroma_db/`
- [ ] Add cache invalidation logic
- [ ] Handle cache rebuilds

## Phase 6: Validation & Testing

- [ ] Verify all documents loaded (50+)
- [ ] Test chunking logic
- [ ] Validate embedding quality
- [ ] Test cache functionality

## Status: ✅ Complete
