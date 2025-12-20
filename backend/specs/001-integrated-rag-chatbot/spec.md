# Feature Specification: Integrated RAG Chatbot for Published Book

**Feature Branch**: `001-integrated-rag-chatbot`
**Created**: 2025-01-01
**Status**: Draft
**Input**: User description: "Integrated RAG Chatbot for a Published Book Target audience: Readers of the published book who want contextual, accurate answers directly grounded in the book's content via an embedded chatbot. Primary objective: Specify and implement a production-grade RAG chatbot that: - Answers questions strictly from book content - Supports selected text only question answering - Is embedded inside the published book experience - Uses Cohere for all LLM inference (no OpenAI models) Functional scope: - Chunk and embed book content into a vector database - Retrieve relevant content for each query - Generate grounded answers using retrieved context only - Support a special mode where answers are based ONLY on user-selected text - Expose chatbot APIs via FastAPI Technology stack (MANDATORY): - Backend: FastAPI - LLM Provider: Cohere API (generation + embeddings) - Vector Database: Qdrant Cloud (Free Tier) - Relational Database: Neon Serverless Postgres - Orchestration: Agent-style patterns inspired by OpenAI Agents / ChatKit (patterns only, not OpenAI models) Required environment variables: - COHERE_API_KEY - QDRANT_API_KEY - QDRANT_CLUSTER_URL - NEON_DATABASE_URL Credential handling rules: - All credentials MUST be provided via environment variables - No secrets may be hardcoded in source code or prompts - Local development must use a `.env` file (excluded from version control) - Production must use platform-native secrets management Retrieval behavior: - All user queries must trigger retrieval before generation - Retrieved chunks must be passed verbatim to the LLM - If retrieval returns no relevant content: Respond with: This information is not available in the book. Selected text mode: - When user provides selected text: - Disable vector search - Use ONLY the provided text as context - Do not add, infer, or expand beyond selected content - Explicitly state that the answer is based on selected text Success criteria: - Every response is grounded in retrieved or selected text - Zero hallucination from general model knowledge - Cohere is used exclusively for inference - API responses are deterministic and repeatable - System cleanly refuses unsupported questions Non-goals (Not building): - General-purpose chatbot - Internet search or external knowledge augmentation - Model fine-tuning - Recommendation or personalization engine - Analytics dashboards beyond basic query logging Quality bar: - Clear, concise, educational responses - No system prompt leakage - No mention of training data or internal reasoning - Consistent behavior across identical inputs"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Ask Book Questions (Priority: P1)

As a reader of the published book, I want to ask questions about the book content and receive accurate answers based only on what's in the book, so I can better understand the material without being distracted by external sources.

**Why this priority**: This is the core functionality - the chatbot must be able to answer questions from the book content to provide value to readers.

**Independent Test**: Can be fully tested by asking multiple questions about book content and verifying that responses are grounded in book text and that the system refuses to answer when information is not available in the book.

**Acceptance Scenarios**:

1. **Given** I am viewing a published book with the RAG chatbot, **When** I ask a question about the book content, **Then** I receive an answer that is grounded in and cites specific parts of the book
2. **Given** I am viewing a published book with the RAG chatbot, **When** I ask a question not covered by the book content, **Then** I receive the response "This information is not available in the book."
3. **Given** I am viewing a published book with the RAG chatbot, **When** I ask the same question multiple times, **Then** I receive consistent answers each time

---

### User Story 2 - Ask About Selected Text Only (Priority: P2)

As a focused reader, I want to select specific text in the book and ask questions about only that text, so I can get detailed explanations of particular passages without the chatbot referencing other parts of the book.

**Why this priority**: This provides an advanced feature for users who want to deeply understand specific sections of the book.

**Independent Test**: Can be fully tested by selecting text and asking follow-up questions, verifying that the chatbot only references the selected text and not other parts of the book.

**Acceptance Scenarios**:

1. **Given** I have selected specific text in the book, **When** I ask a question with the selected text mode active, **Then** the chatbot uses only that text as context and explicitly states that the answer is based on selected text only
2. **Given** I have selected text in the book, **When** I ask a question that requires broader context than what's selected, **Then** the chatbot responds based only on the selected text, without augmenting with other book content

---

### User Story 3 - Embed Chatbot in Book Experience (Priority: P3)

As a book reader, I want the chatbot to be seamlessly integrated into the book reading experience, so I can interact with it naturally without leaving the book interface.

**Why this priority**: This enhances user experience by making the chatbot feel like a natural part of the book rather than a separate tool.

**Independent Test**: Can be tested by evaluating how naturally the chatbot interface integrates with the book interface and how intuitive it is to switch between reading and chatting.

**Acceptance Scenarios**:

1. **Given** I am reading the book, **When** I want to ask a question, **Then** I can easily access the chatbot interface without leaving the book context
2. **Given** I am interacting with the chatbot, **When** I want to reference specific parts of the book, **Then** I can easily select text and use it in my questions

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST chunk and embed book content into a vector database for retrieval
- **FR-002**: System MUST retrieve relevant content chunks before generating any response to a user query
- **FR-003**: System MUST generate answers that are grounded only in retrieved or selected text context
- **FR-004**: Users MUST be able to activate a special "selected text only" mode where responses are based solely on user-selected text
- **FR-005**: System MUST use Cohere API exclusively for all LLM inference (no OpenAI models)
- **FR-006**: System MUST respond with "This information is not available in the book." when retrieval returns no relevant content
- **FR-007**: System MUST explicitly state that answers in selected text mode are based only on the provided text
- **FR-008**: System MUST expose chatbot functionality via FastAPI endpoints
- **FR-009**: System MUST handle credential management through environment variables only
- **FR-010**: System MUST log all user queries for feedback and improvement purposes

### Key Entities

- **Book Content**: The published book text that serves as the authoritative knowledge base, including: book_id, chapter, section, paragraph_index, page_number, content_type, and associated metadata
- **Retrieved Chunks**: Segments of book content retrieved from the vector database that are used as context for LLM responses
- **User Query**: Input from the reader that represents a question or request for information about the book content
- **Chat Response**: System-generated answers that are grounded in book content or selected text only, with citations where appropriate

## Clarifications

### Session 2025-01-01

- Q: What specific attributes should the Book Content entity include for proper retrieval? → A: book_id, chapter, section, paragraph_index, page_number, content_type

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Every response is grounded in retrieved or selected text with zero hallucination from general model knowledge
- **SC-002**: 100% of LLM inferences use Cohere API exclusively, with no OpenAI model usage
- **SC-003**: System responds with "This information is not available in the book." when content is not found, with 95% accuracy
- **SC-004**: Responses in selected text mode are based solely on provided text, with no reference to other book content
- **SC-005**: System provides consistent responses across identical inputs, with 99% repeatability
- **SC-006**: User satisfaction rating of 4.0 or higher for accuracy and relevance of responses