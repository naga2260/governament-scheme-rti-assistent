# Telangana Welfare Navigator - Project Constitution

## Project Vision

A bilingual (English/Telugu) AI-powered assistant that helps citizens discover government welfare schemes they're eligible for using Retrieval-Augmented Generation (RAG) and intelligent query routing. The application streamlines access to India's complex welfare landscape while supporting RTI (Right to Information) requests.

## Technology Stack

### Core Framework
- **Runtime:** Python 3.11+
- **Web Framework:** Streamlit (for rapid UI development and interactive data apps)
- **LLM & Embeddings:** Google Generative AI (Gemini)
- **Vector Database:** Chroma (for RAG vector storage)

### Libraries & Packages
- **LLM Integration:** LangChain ecosystem (langchain-core, langchain-community, langchain-google-genai, langchain-text-splitters)
- **Data Processing:** NumPy, pandas
- **Document Processing:** PyPDF2 (implied via data_pdfs)
- **Testing:** pytest with coverage reporting
- **Code Quality:** ruff (linting & formatting), mypy (type checking), bandit (security), vulture (dead code)
- **Secret Management:** detect-secrets, gitleaks

## Code Standards

### Language & Python Version
- **Target Version:** Python 3.11 (enforced via pyproject.toml and CI)
- **Style Guide:** PEP 8 with line length of 100 characters
- **Type Hints:** Required for function signatures; `allow_untyped_defs = true` for internal implementation to allow flexibility

### Naming Conventions
- **Modules/Files:** snake_case (e.g., `loader.py`, `rti_generator.py`)
- **Classes:** PascalCase (e.g., `GoogleGenerativeAIEmbeddings`)
- **Functions & Variables:** snake_case (e.g., `generate_rti_draft()`, `ingest_documents()`)
- **Constants:** UPPER_SNAKE_CASE (e.g., `UI_TELUGU`, `SCHEME_NAME_TELUGU`)

### Import Organization
```python
# 1. Standard library imports
import os
import json

# 2. Third-party imports
import streamlit as st
from langchain_core.documents import Document

# 3. Local application imports
from utils.loader import ingest_documents
from utils.retriever import get_retriever
```

### Code Patterns

#### Streamlit Caching
Use `@st.cache_resource` for expensive operations (model loading, document ingestion):
```python
@st.cache_resource
def load_model():
    return your_model()
```

#### State Management
Use `st.session_state` for persistent data within a session:
```python
if 'user_profile' not in st.session_state:
    st.session_state.user_profile = {}
```

#### Error Handling
- Handle API failures gracefully with user-friendly error messages
- Log errors for debugging; use try-except for recoverable errors
- Surface critical errors to the user via st.error()

#### Multilingual Support
- All UI text MUST have English and Telugu translations
- Store translations in dictionaries: `UI_TELUGU`, `SCHEME_NAME_TELUGU`, `QUESTION_TELUGU`
- Use getter functions or context to select language based on `st.session_state.get('lang', 'en')`

## Project Structure

```
.
├── app.py                    # Main Streamlit application entry point
├── utils/                    # Core utilities
│   ├── __init__.py
│   ├── loader.py            # Document ingestion with caching
│   ├── retriever.py         # RAG pipeline & UI translations
│   ├── embedder.py          # Embedding wrapper
│   └── rti_generator.py     # RTI form generation
├── tests/                    # Test directory
│   └── test_repository_smoke.py
├── data/                     # Scheme text files (.txt)
├── data_pdfs/               # PDF source data
├── .specify/                # Spec-Kit infrastructure
│   ├── memory/
│   │   └── constitution.md  # This file
│   └── templates/           # Spec templates
├── specs/                    # Feature specifications
├── .env.example             # Environment variables template
├── pyproject.toml           # Python project config
├── .gitlab-ci.yml           # CI/CD pipeline
└── .pre-commit-config.yaml  # Pre-commit hooks
```

## Testing Strategy

### Test Types
1. **Smoke Tests:** Verify core files exist and data is available (tests/test_repository_smoke.py)
2. **Unit Tests:** Test individual functions and utilities (future expansion)
3. **Integration Tests:** Test RAG pipeline end-to-end (future expansion)

### Coverage Requirements
- **Minimum:** 1% (very permissive for early-stage project)
- **Future Target:** Increase as test coverage matures
- **Reports:** Generate HTML and XML coverage reports via pytest-cov

### Test Configuration (pyproject.toml)
```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "--cov=. --cov-report=term-missing --cov-report=xml --cov-fail-under=1"
```

## Code Quality Tools

### Linting & Formatting
- **Tool:** Ruff (v0.6.9+)
- **Rules:** E9, F63, F7, F82 (focused rules to catch critical issues)
- **Line Length:** 100 characters
- **Run:** `ruff check .` (lint), `ruff format .` (format)

### Type Checking
- **Tool:** MyPy (v1.11.2+)
- **Python Version:** 3.11
- **Config:** `ignore_missing_imports = true`, `allow_untyped_defs = true`
- **Run:** `mypy app.py utils`

### Security Scanning
- **Static Analysis:** Bandit (detects common security issues)
- **Secret Detection:** detect-secrets + gitleaks (prevents accidental secret commits)
- **Dependency Audit:** pip-audit (identifies vulnerable dependencies)
- **Dead Code:** Vulture (removes unused code)

### Pre-commit Hooks (Enforced)
All developers MUST run pre-commit hooks before committing:
```bash
pre-commit install
pre-commit run --all-files  # Test locally before pushing
```

Hooks include: trailing-whitespace, end-of-file-fixer, yaml validation, ruff, mypy, secret detection, bandit, pip-audit.

## CI/CD Pipeline

### Stages (in .gitlab-ci.yml)
1. **lint** → `ruff check .`
2. **format** → Format verification
3. **type_check** → `mypy app.py utils`
4. **security** → Secret scanning, dependency audit, static analysis
5. **test** → `pytest --cov` with XML report
6. **coverage** → Coverage reporting to GitLab
7. **changelog** → Automatic changelog generation via git-cliff

### Pipeline Requirements
- ALL stages must pass before merging to main
- Coverage reports uploaded to GitLab automatically
- Changelog automatically updated on release

## Documentation Standards

### Required Files
- **README.md** → Project overview, setup instructions, quick start
- **CONTRIBUTING.md** → How to contribute, branch strategy, PR process
- **USER_MANUAL.md** → End-user guide with screenshots/examples
- **SECURITY.md** → Security policy, vulnerability reporting
- **CODE_OF_CONDUCT.md** → Community guidelines
- **CHANGELOG.md** → Auto-generated release notes

### Documentation Format
- Markdown (.md) files
- Clear headings (H1, H2, H3)
- Code examples in fenced blocks with language tags
- Links should be relative where possible
- Keep README concise; detailed docs in separate files

### Spec Documentation
- Feature specs in `specs/<feature-name>/spec.md`
- Implementation plans in `specs/<feature-name>/plan.md`
- Task breakdowns in `specs/<feature-name>/tasks.md`
- Follow templates in `.specify/templates/`

## Deployment

### Containerization
- **Docker:** Dockerfile present for containerized deployment
- **Image Base:** python:3.11-slim (for CI)
- **Deployment:** Vercel (via vercel.json for Streamlit apps)

### Environment Variables
- **Storage:** `.env` file locally, Streamlit secrets in production
- **Template:** `.env.example` documents all required variables
- **API Keys:** Google Generative AI key (GOOGLE_API_KEY)

### Versioning
- **Semantic Versioning:** vMAJOR.MINOR.PATCH (e.g., v0.1.0, v1.2.3)
- **Git Tags:** Tag releases with version numbers
- **Changelog:** Maintained via git-cliff (cliff.toml config)

## Version Control

### Branching Strategy
- **main** → Production-ready code; protected branch
- **naga** → Development branch for feature work
- **Feature Branches:** `feature/<name>` from naga, merge via PR

### Commit Messages
- Clear, descriptive commit messages
- Reference issue numbers when applicable
- Use imperative mood: "Add feature" not "Added feature"

### PR Process
1. Create PR from feature branch → naga
2. All CI checks must pass
3. Code review required
4. Merge to naga; squash commits if needed
5. Release PRs: merge to main, tag with version

## Security Practices

### Secret Management
- **Never commit:** `.env` file, API keys, credentials
- **Always use:** `.env.example` for templates
- **Detection:** gitleaks + detect-secrets in CI/pre-commit
- **Rotation:** Regularly rotate API keys in production

### Dependency Security
- **Audit:** `pip-audit` checks for known vulnerabilities
- **Updates:** Keep dependencies up-to-date
- **Lock File:** Use requirements.txt with pinned versions for reproducibility

### Code Security
- **Bandit:** Scans for common security issues (hardcoded secrets, unsafe functions)
- **Input Validation:** Validate user input at Streamlit layer
- **API Keys:** Use environment variables, never hardcode
- **Sensitive Data:** Don't log or expose user personal information

## Multilingual Support

### Current Languages
1. **English** (Primary)
2. **Telugu** (Indian regional language)

### Translation Management
- Store translations in dictionaries in `utils/retriever.py`
- Keys: `UI_TELUGU`, `SCHEME_NAME_TELUGU`, `QUESTION_TELUGU`
- Selection: Use `st.session_state.get('lang', 'en')`
- Adding new languages: Create new dictionary and add language selector to app

## Performance Considerations

### Caching Strategy
- Use Streamlit's `@st.cache_resource` for models, embeddings, vector stores
- Cache invalidation: Set TTL or manual invalidation as needed
- Document cache behavior in function docstrings

### RAG Pipeline Optimization
- Use efficient embeddings (Google Generative AI)
- Batch document ingestion for large datasets
- Limit search results to top K most relevant (tune K based on use case)

## Future Roadmap

- Expand language support (Hindi, Kannada, Tamil, etc.)
- Add more agent types for specialized queries
- Implement user feedback loop for continuous improvement
- Add analytics to track scheme discovery patterns
- Mobile-friendly UI enhancements

## Questions & Escalations

- **Technical Decisions:** Discuss in PR comments or project issues
- **Major Architecture Changes:** Create a spec first (specs/<feature-name>/spec.md)
- **Security Issues:** See SECURITY.md for reporting procedures
- **Questions on Standards:** Reference this constitution and pre-commit hooks
