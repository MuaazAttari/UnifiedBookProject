<!-- SYNC IMPACT REPORT
Version change: N/A -> 1.0.0
Modified principles: N/A (initial creation)
Added sections: All sections (initial creation)
Removed sections: None
Templates requiring updates: 
  - .specify/templates/spec-template.md: ✅ Updated
  - .specify/templates/plan-template.md: ✅ Updated
  - .specify/templates/tasks-template.md: ✅ Updated
  - .specify/commands/*.toml: ✅ Updated
Follow-up TODOs: None
-->

# Integrated RAG Chatbot Constitution

## Core Principles

### Single Source of Truth
The book content is the only authoritative knowledge base. All responses must be grounded in book content without deviation.

### Zero Hallucination
No answers outside retrieved or selected content. The system must refuse to answer if content is not available in the book's text.

### Deterministic Retrieval
All responses must be traceable to retrieved chunks. Retrieval process must be reproducible and auditable.

### AI-Native Design
Agent-based orchestration with explicit tools and memory. System architecture must leverage AI-specific patterns and capabilities.

### Provider Neutrality
Use Cohere LLM APIs exclusively (no OpenAI models). All AI services must comply with this constraint.

## Technical Constraints

### LLM & AI Requirements
- LLM Provider: Cohere API only
- OpenAI APIs must NOT be used for inference
- OpenAI Agents / ChatKit SDK patterns may be used only for orchestration logic
- All prompts must enforce grounded responses using retrieved context

### Retrieval Rules
- Vector Store: Qdrant Cloud (Free Tier)
- Embeddings stored with: book_id, chapter, section, paragraph_index
- Retrieval must always precede generation
- If no relevant context is retrieved, respond with: "This information is not available in the book."

### Selected Text Mode
- If user provides selected text:
  - Ignore full-book retrieval
  - Use ONLY the selected text as context
  - Do not enrich or expand beyond selected content
  - Clearly state that the answer is based on selected text only

## Backend & Infrastructure

### Technology Stack
- API Framework: FastAPI
- Database: Neon Serverless Postgres
- Storage: Qdrant Cloud for embeddings

### Backend Responsibilities
- User sessions
- Query logs
- Feedback storage
- Retrieval metadata tracking

## Response Standards

### Communication Protocols
- Tone: Clear, neutral, educational
- Audience: General readers of the book
- No speculation or external references
- No training data mentions
- No system or developer prompt leakage

## Security & Data Integrity

### Access Control
- API keys stored via environment variables
- No hardcoded secrets
- User queries must not modify source content
- Read-only access to book embeddings

### Data Protection
- All user data encrypted in transit and at rest
- Session data properly secured and regularly cleaned up
- No personal information stored without explicit consent

## Success Criteria

### Functional Requirements
- Every answer is fully grounded in retrieved or selected text
- No hallucinated facts detected
- Correct refusal when information is unavailable
- Cohere API successfully used for all generations
- Chatbot behaves consistently across identical queries

### Quality Metrics
- 95% accuracy in citation of source text
- Less than 1% hallucination rate
- Sub-second response times for standard queries
- 99.9% availability during business hours

## Failure Conditions

### System Failures
- Answering from general knowledge instead of book content
- Using OpenAI models for generation
- Mixing selected-text mode with full-book retrieval
- Providing uncited or unverifiable responses

### Performance Issues
- Response times exceeding 3 seconds for standard queries
- Consistent failure to retrieve relevant content
- Inconsistent behavior across identical queries

## Governance

### Amendment Procedure
This constitution may be amended only with documented justification and stakeholder approval. All changes must be backward-compatible unless explicitly stated otherwise.

### Versioning Policy
Version follows semantic versioning: MAJOR.MINOR.PATCH where:
- MAJOR: Backward incompatible changes to core principles
- MINOR: Addition of new principles or requirements
- PATCH: Clarifications, typo fixes, non-semantic refinements

### Compliance Review
All development work must verify compliance with constitutional principles. Code reviews must explicitly check for adherence to constraints specified herein.

**Version**: 1.0.0 | **Ratified**: 2025-01-01 | **Last Amended**: 2025-01-01