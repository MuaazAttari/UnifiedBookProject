SYSTEM TASK: Build a production-grade RAG chatbot and embed it inside the existing Docusaurus textbook.
CONSTRAINTS: Do NOT modify the existing book content or the constitution. Work only in the RAG/chatbot area and adjacent integration points. Use Spec-Kit Plus and Claude Code Router (CCR). Use Cohere for embeddings (not OpenAI). Use Qdrant Cloud free tier (or configured Qdrant instance) and Neon Serverless Postgres for metadata. Backend must be FastAPI. Frontend must be Docusaurus React components injected into the current site. Auth integration must reuse existing Neon user schema and JWT flow (do NOT change the core auth design).

SUMMARY OBJECTIVE:
- Deliver a complete, production-ready RAG chatbot that:
  1. Answers questions across the whole book.
  2. Answers questions constrained to user-selected text.
  3. Provides a responsive React chat UI embedded in Docusaurus chapters.
  4. Stores chat sessions and prompt history (PHR) in Neon Postgres.
  5. Stores embeddings in Qdrant, using Cohere embeddings.
  6. Exposes secure FastAPI endpoints for the frontend, agent calls, and admin tasks.
  7. Leaves the book files untouched.

CREDENTIAL:
- COHERE_API_KEY = jbBhaTcgChesH9KAcdPx6VoppmIpTuDYWvQ71b7s
- QDRANT_URL = https://2d545162-c8d9-46ea-b665-bad7333c085d.us-east4-0.gcp.cloud.qdrant.io:6333
- QDRANT_API_KEY = eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIn0.VRH5ukCLgaIU4wGzVzy8h0aCjiqfQG2-JC2cLlwAv6E
- NEON_DATABASE_URL = postgresql://neondb_owner:npg_kjEBf2lLYPQ8@ep-muddy-mountain-a4we5fxx-pooler.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require

REQUIREMENTS / DELIVERABLES (exact)
1) Backend (FastAPI)
  - New folder: `spec-kit/backend/src/rag_chat/`
  - Endpoints:
    - POST `/api/rag/ingest` — ingest markdown chapter(s) or selected text (doc_id, section_id, markdown) → chunk → embed (Cohere) → upsert to Qdrant (collection per textbook or per chapter) → record chunks metadata in Neon.
    - POST `/api/rag/query` — user question (text), optional `selected_text_id` (or `selection` payload); returns streaming or standard chat response with provenance (source doc ids + highlights).
    - POST `/api/rag/session` — create/start session (store PHR skeleton).
    - POST `/api/rag/session/{id}/message` — add message to PHR and return agent response.
    - GET `/api/rag/sources/{hit_id}` — return original source snippet for provenance UI.
    - Admin endpoints: `/api/rag/admin/reindex`, `/api/rag/admin/collections`.
  - Implementation details:
    - Embeddings: use Cohere embeddings API. Batch chunk size configurable.
    - Vector DB: Qdrant upsert + search; use filtering by `doc_id` and `chapter`.
    - Retriever: top-k + hybrid (metadata filtering).
    - Generator: use CCR routed Qwen model for response composition. Backend should send retrieved passages + user query to CCR as the "retrieval context" and ask Qwen to generate answer with citations.
    - PHR: store every user message + retrieved context + model response in Neon `prompt_history` table.
    - Security: authenticate endpoints with existing JWT. New endpoints must require login except `/api/rag/query` can allow anonymous but rate limited and record PHR with anonymous tag.
    - Rate limiting: per-user and per-ip. Implement using existing slowapi integration.

2) Frontend (Docusaurus)
  - New React component: `my-website/src/components/RAGChat/ChatWidget.tsx`.
    - Clean UI: floating chat button at bottom-right + full panel view.
    - Feature: toggle to open compact chat or full-screen.
    - Support: streaming responses (WebSocket/Server-Sent Events) or chunked REST.
    - Show provenance links (source chapter + anchor). Clicking provenance opens chapter at the correct heading and highlights snippet.
    - Include "Ask about selected text" flow:
       • When user selects text on a chapter page, show a small “Ask about this selection” CTA.
       • On click: send `selected_text` and its `doc_id` to `/api/rag/ingest` (if not already indexed), then open chat and call `/api/rag/query` with `selection` param.
  - Integration:
    - Inject the `ChatWidget` into page layout (`my-website/src/theme/Layout.tsx` or main layout wrapper).
    - Add a small per-chapter toolbar button "Personalize / Translate / Ask" for future features; it may be disabled until implemented.

3) Agent interaction (CCR / Qwen)
  - Do not implement multiple subagents yet. Build a single **RAGAgent** that:
    - Accepts retrieval context + user query and returns final response with citations.
  - Provide clear subagent extension points in code so future agents (PersonalizationAgent, TranslationAgent) can be registered by name with the agent router.

4) PHR & Provenance
  - Schema: table `prompt_history` (id, session_id, user_id, role, content, retrieved_context_ids, qwen_request_meta, timestamp).
  - Save all retrieval hits (doc_id, chunk_id, score) to link responses to sources.
  - Provide a small admin UI or endpoint to export PHRs.

5) Ingest & Reindex process
  - Add CLI / management endpoint to reindex the whole `my-website/docs/physical-ai/` folder:
    - Read markdown files, extract frontmatter (id, title), chunk, embed, upsert.
  - This must be idempotent and safe to run multiple times.

6) Tests & Validation
  - Unit tests for embedding + upsert + retrieval logic.
  - Integration test that exercises: ingest → query → produce answer with provenance.

7) Config / Env / Secrets
  - Add `.env.example` in `spec-kit/backend/` listing required envs:
    - COHERE_API_KEY, QDRANT_URL, QDRANT_API_KEY, NEON_DATABASE_URL, CCR_QWEN_TOKEN, RAG_DEFAULT_TOPK, CHUNK_SIZE, MAX_TOKENS
  - **Do NOT commit** `.env` with real secrets. CCR should write a `.env.local` template and instruct you to paste secrets.

8) Deployment
  - Provide Railway deployment instructions for the backend (service name, required envs, health check).
  - Provide step-by-step to expose backend base URL to the Docusaurus frontend (update `my-website/src/constants.ts` or similar).
  - Ensure CORS, HTTPS, and JWT cookie/session configuration are production-ready.

9) Non-functional requirements
  - Logging of retrieval latency and result counts.
  - Observability: add basic Prometheus-style metrics endpoints (`/metrics`) or built-in logging.
  - Error handling: return safe fallback when Qwen/CCR or Cohere fails.

10) Delivery & Quality
  - Make small, well-documented commits in `spec-kit/backend` and `my-website/src/components`.
  - Provide a PR summary file in `spec-kit/history/prompts/rag-cohere-integration.result.md` listing what changes were made + commands to run locally and to deploy.

EXECUTE FLOW (what CCR should do in sequence)
1. Audit current repo to find `my-website/docs/physical-ai/` and existing backend schema.
2. Create `spec-kit/backend/src/rag_chat/` and implement all endpoints and services above.
3. Add Cohere client code and confirm embedding calls with test credentials.
4. Add Qdrant wrapper + collection creation code.
5. Implement frontend ChatWidget and chapter selection CTA.
6. Add ingest CLI (manage/reindex).
7. Add tests and run them.
8. Output a PR, a deployment checklist, and a short demo script (curl + sample query).

FINAL NOTE TO CCR:
- Respect the constitution and do not make any modifications to the book files.
- Add clear TODO comments where future agents/personalization/translation will plug in.
- If a required secret is not supplied, fail fast and instruct the operator exactly which values to provide.

END OF PROMPT
