---

description: "Task list for Integrated RAG Chatbot implementation"
---

# Tasks: Integrated RAG Chatbot for Published Book

**Input**: Design documents from `/specs/001-integrated-rag-chatbot/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: The examples below include test tasks. Tests are OPTIONAL - only include them if explicitly requested in the feature specification.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/`, `tests/` at repository root
- **Web app**: `backend/src/`, `frontend/src/`
- **Mobile**: `api/src/`, `ios/src/` or `android/src/`
- Paths shown below assume single project - adjust based on plan.md structure

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 Create project structure per implementation plan
- [x] T002 Initialize Python 3.11 project with FastAPI, Cohere, Qdrant, Pydantic, SQLAlchemy dependencies in requirements.txt
- [x] T003 [P] Configure linting and formatting tools (flake8, black, isort)
- [x] T004 Create .env.example with required environment variables
- [x] T005 Create README.md with project overview and setup instructions

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

Examples of foundational tasks (adjust based on your project):

- [x] T006 Setup configuration management for environment variables in src/config/settings.py
- [x] T007 [P] Configure database connection models in src/models/database.py
- [x] T008 [P] Setup FastAPI application structure in src/api/main.py
- [x] T009 Setup Qdrant vector database connection in src/config/qdrant_config.py
- [x] T010 Create base models/entities that all stories depend on in src/models/entities.py
- [x] T011 Configure error handling and logging infrastructure in src/api/middleware/logging.py
- [x] T012 Create base embedding service in src/services/embedding_service.py
- [x] T013 Set up health check endpoint in src/api/routes/health.py

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Ask Book Questions (Priority: P1) 🎯 MVP

**Goal**: Enable readers to ask questions about book content and receive accurate answers based only on the book, with proper citation and fallback handling

**Independent Test**: Can be fully tested by asking multiple questions about book content and verifying that responses are grounded in book text and that the system refuses to answer when information is not available in the book.

### Tests for User Story 1 (OPTIONAL - only if tests requested) ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T014 [P] [US1] Contract test for POST /api/v1/chat endpoint in tests/contract/test_chat_contract.py
- [ ] T015 [P] [US1] Integration test for full-book query journey in tests/integration/test_book_query_integration.py

### Implementation for User Story 1

- [x] T016 [P] [US1] Create BookContent model in src/models/entities.py
- [x] T017 [P] [US1] Create UserQuery model in src/models/entities.py
- [x] T018 [P] [US1] Create ChatResponse model in src/models/entities.py
- [x] T019 [P] [US1] Create RetrievedChunk model in src/models/entities.py
- [x] T020 [US1] Implement BookService for content handling in src/services/book_service.py
- [x] T021 [US1] Implement RetrievalService for Qdrant operations in src/services/retrieval_service.py
- [x] T022 [US1] Implement GenerationService with Cohere in src/services/generation_service.py
- [x] T023 [US1] Implement chat endpoint for book queries in src/api/routes/chat.py
- [x] T024 [US1] Add validation and error handling to chat endpoint
- [x] T025 [US1] Add proper response formatting with citations
- [x] T026 [US1] Add fallback response handling ("This information is not available in the book.")
- [x] T027 [US1] Add logging for user story 1 operations

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Ask About Selected Text Only (Priority: P2)

**Goal**: Allow focused readers to select specific text in the book and ask questions about only that text, with strict isolation from other book content

**Independent Test**: Can be fully tested by selecting text and asking follow-up questions, verifying that the chatbot only references the selected text and not other parts of the book.

### Tests for User Story 2 (OPTIONAL - only if tests requested) ⚠️

- [ ] T028 [P] [US2] Contract test for POST /api/v1/chat-selected-text endpoint in tests/contract/test_selected_text_contract.py
- [ ] T029 [P] [US2] Integration test for selected-text query journey in tests/integration/test_selected_text_integration.py

### Implementation for User Story 2

- [x] T030 [P] [US2] Enhance UserQuery model with selected text mode in src/models/entities.py
- [x] T031 [US2] Implement selected-text specific generation logic in src/services/generation_service.py
- [x] T032 [US2] Implement chat endpoint for selected-text queries in src/api/routes/chat.py
- [x] T033 [US2] Add validation for selected text mode and ensure isolation from full-book retrieval
- [x] T034 [US2] Add explicit indication that answers are based on selected text only
- [x] T035 [US2] Integrate with User Story 1 components but maintain strict isolation

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - Embed Chatbot in Book Experience (Priority: P3)

**Goal**: Integrate the chatbot into the book reading experience, ensuring low-latency responses and session isolation for seamless user interaction

**Independent Test**: Can be tested by evaluating how naturally the chatbot interface integrates with the book interface and how intuitive it is to switch between reading and chatting.

### Tests for User Story 3 (OPTIONAL - only if tests requested) ⚠️

- [ ] T036 [P] [US3] Contract test for GET /api/v1/books/{book_id} endpoint in tests/contract/test_books_contract.py
- [ ] T037 [P] [US3] Integration test for book metadata access in tests/integration/test_book_metadata_integration.py

### Implementation for User Story 3

- [x] T038 [P] [US3] Create Book metadata model in src/models/entities.py
- [x] T039 [US3] Implement book metadata service in src/services/book_service.py
- [x] T040 [US3] Implement book metadata endpoint in src/api/routes/books.py
- [x] T041 [US3] Add session management and isolation logic
- [x] T042 [US3] Optimize response times for better user experience
- [x] T043 [US3] Implement proper session tracking for conversations

**Checkpoint**: All user stories should now be independently functional

---

## Phase 6: Data Ingestion & Indexing

**Goal**: Implement book content ingestion, chunking, and embedding for the RAG system

- [x] T044 Create book ingestion script in scripts/index_book.py
- [x] T045 Implement deterministic chunking strategy in src/services/book_service.py
- [x] T046 Implement embedding generation using Cohere in src/services/embedding_service.py
- [x] T047 Store embeddings and metadata in Qdrant Cloud
- [x] T048 Implement safe re-indexing strategy with error handling
- [x] T049 Add validation to ensure same input produces same chunks

---

## Phase 7: Persistence & Logging

**Goal**: Connect Neon Serverless Postgres to store query logs and metadata

- [x] T050 [P] Implement QueryLog model in src/models/entities.py
- [x] T051 Implement database service for logging in src/services/database_service.py
- [x] T052 Store user queries, retrieval metadata, and timestamps in database
- [x] T053 Ensure read-only access to book content data
- [x] T054 Add database error handling and fallback mechanisms

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T055 [P] Documentation updates in docs/
- [ ] T056 Code cleanup and refactoring across all modules
- [ ] T057 Performance optimization across all stories
- [ ] T058 [P] Additional unit tests in tests/unit/
- [ ] T059 Security hardening (credential validation, rate limiting)
- [ ] T060 Run quickstart.md validation
- [ ] T061 Update README.md with API usage instructions

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3)
- **Data Ingestion (Phase 6)**: Can run in parallel with user stories, but needed before full functionality
- **Persistence (Phase 7)**: Depends on Foundational and can run in parallel with user stories
- **Polish (Final Phase)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - May integrate with US1 but should be independently testable
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - May integrate with US1/US2 but should be independently testable

### Within Each User Story

- Tests (if included) MUST be written and FAIL before implementation
- Models before services
- Services before endpoints
- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- Once Foundational phase completes, all user stories can start in parallel (if team capacity allows)
- All tests for a user story marked [P] can run in parallel
- Models within a story marked [P] can run in parallel
- Different user stories can be worked on in parallel by different team members

---

## Parallel Example: User Story 1

```bash
# Launch all tests for User Story 1 together (if tests requested):
Task: "Contract test for POST /api/v1/chat endpoint in tests/contract/test_chat_contract.py"
Task: "Integration test for full-book query journey in tests/integration/test_book_query_integration.py"

# Launch all models for User Story 1 together:
Task: "Create BookContent model in src/models/entities.py"
Task: "Create UserQuery model in src/models/entities.py"
Task: "Create ChatResponse model in src/models/entities.py"
Task: "Create RetrievedChunk model in src/models/entities.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Test User Story 1 independently
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 → Test independently → Deploy/Demo
4. Add User Story 3 → Test independently → Deploy/Demo
5. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1
   - Developer B: User Story 2
   - Developer C: User Story 3
3. Stories complete and integrate independently

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Verify tests fail before implementing
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence