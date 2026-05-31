# Telangana Welfare Navigator - Agent Architecture

### Overview

Telangana Welfare Navigator uses multiple AI agents to help citizens discover government welfare schemes, verify eligibility, understand benefits, and obtain application guidance.

---

## Agent 1: Eligibility Agent

### Purpose
Identifies schemes a citizen is eligible for based on profile information.

### Input
- Age
- Gender
- Occupation
- Annual Income
- District

### Output
- Eligible Schemes
- Eligibility Status

### Responsibilities
- Match user data against scheme criteria
- Filter ineligible schemes
- Generate eligibility results

---

## Agent 2: Recommendation Agent

### Purpose
Ranks and recommends the most relevant schemes.

### Input
- Eligible Schemes
- User Profile

### Output
- Personalized Recommendations

### Responsibilities
- Prioritize schemes
- Explain benefits
- Generate recommendation summaries

---

## Agent 3: Document Assistance Agent

### Purpose
Provides document requirements for selected schemes.

### Input
- Scheme Name

### Output
- Required Documents
- Verification Checklist

### Responsibilities
- Display mandatory documents
- Explain application prerequisites

---

## Agent 4: Query Resolution Agent

### Purpose
Answers user questions through a conversational interface.

### Input
- User Queries

### Output
- Natural Language Responses

### Responsibilities
- Answer FAQs
- Explain scheme details
- Guide users through application procedures

---

## Agent 5: Retrieval Agent (RAG)

### Purpose
Retrieves relevant scheme information from the knowledge base.

### Input
- User Query

### Output
- Relevant Scheme Data

### Responsibilities
- Vector Search
- Context Retrieval
- Knowledge Base Search

---

## Agent Workflow

User Input
↓
Eligibility Agent
↓
Recommendation Agent
↓
Retrieval Agent (RAG)
↓
Query Resolution Agent
↓
Final Response

---

## Technology Stack

### Frontend
- React.js
- Tailwind CSS

### Backend
- FastAPI
- Python

### AI/RAG
- LangChain
- FAISS
- Sentence Transformers

### Database
- SQLite / PostgreSQL

### LLM
- Hugging Face Models
- Ollama

---

## Future Enhancements

- Voice-Based Assistance
- Multi-Language Support (Telugu, Hindi, English)
- Scheme Application Tracking
- District-Specific Recommendations
- Government Portal Integration
- Mobile Application Support