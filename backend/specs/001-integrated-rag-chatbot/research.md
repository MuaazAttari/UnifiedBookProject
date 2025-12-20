# Research Notes: Integrated RAG Chatbot for Published Book

## Decision Log

### 1. Project Structure Decision
**Decision**: Web application structure with backend API and integration points
**Rationale**: The feature requires a backend service (FastAPI) to handle RAG operations, with integration into a book reading experience
**Alternatives considered**: Single monolithic project vs. separate backend + frontend; chose backend focus with integration points

### 2. Technology Stack Selection
**Decision**: Use the mandated technology stack as specified in requirements
**Rationale**: Requirements mandate specific technologies that must be used
**Alternatives considered**: Other LLM providers (OpenAI, Anthropic) but requirements mandate Cohere only

### 3. Retrieval Strategy
**Decision**: Use Qdrant Cloud with specific metadata schema
**Rationale**: Requirements mandate Qdrant Cloud; metadata schema required for deterministic retrieval
**Alternatives considered**: Other vector databases but requirements mandate Qdrant

### 4. Authentication & Security
**Decision**: Environment-based credential management with no hardcoded secrets
**Rationale**: Security requirements mandate credential isolation
**Alternatives considered**: Various secret management approaches; selected environment variable approach as required

### 5. Selected Text Mode Implementation
**Decision**: Separate endpoint pathway with bypass for vector retrieval
**Rationale**: Requirements specify strict isolation between selected text and full book modes
**Alternatives considered**: Parameter-based switching vs. separate pathways; chose separate pathways for cleaner isolation