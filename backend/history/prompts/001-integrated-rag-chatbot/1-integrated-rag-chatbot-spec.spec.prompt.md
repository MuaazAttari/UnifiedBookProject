---
id: 1
title: integrated-rag-chatbot-spec
stage: spec
date: 2025-01-01
surface: agent
model: gpt-4o
feature: integrated-rag-chatbot
branch: 001-integrated-rag-chatbot
user: Admin
command: /sp.specify
labels: [spec,rag,chatbot,ai]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
 - specs/001-integrated-rag-chatbot/spec.md
 - specs/001-integrated-rag-chatbot/checklists/requirements.md
tests:
 - none
---

## Prompt

```
/sp.specify Integrated RAG Chatbot for a Published Book Target audience: Readers of the published book who want contextual, accurate answers directly grounded in the book's content via an embedded chatbot. Primary objective: Specify and implement a production-grade RAG chatbot that: - Answers questions strictly from book content - Supports selected text only question answering - Is embedded inside the published book experience - Uses Cohere for all LLM inference (no OpenAI models) Functional scope: - Chunk and embed book content into a vector database - Retrieve relevant content for each query - Generate grounded answers using retrieved context only - Support a special mode where answers are based ONLY on user-selected text - Expose chatbot APIs via FastAPI Technology stack (MANDATORY): - Backend: FastAPI - LLM Provider: Cohere API (generation + embeddings) - Vector Database: Qdrant Cloud (Free Tier) - Relational Database: Neon Serverless Postgres - Orchestration: Agent-style patterns inspired by OpenAI Agents / ChatKit (patterns only, not OpenAI models) Required environment variables: - COHERE_API_KEY - QDRANT_API_KEY - QDRANT_CLUSTER_URL - NEON_DATABASE_URL Credential handling rules: - All credentials MUST be provided via environment variables - No secrets may be hardcoded in source code or prompts - Local development must use a `.env` file (excluded from version control) - Production must use platform-native secrets management Retrieval behavior: - All user queries must trigger retrieval before generation - Retrieved chunks must be passed verbatim to the LLM - If retrieval returns no relevant content: Respond with: This information is not available in the book. Selected text mode: - When user provides selected text: - Disable vector search - Use ONLY the provided text as context - Do not add, infer, or expand beyond selected content - Explicitly state that the answer is based on selected text Success criteria: - Every response is grounded in retrieved or selected text - Zero hallucination from general model knowledge - Cohere is used exclusively for inference - API responses are deterministic and repeatable - System cleanly refuses unsupported questions Non-goals (Not building): - General-purpose chatbot - Internet search or external knowledge augmentation - Model fine-tuning - Recommendation or personalization engine - Analytics dashboards beyond basic query logging Quality bar: - Clear, concise, educational responses - No system prompt leakage - No mention of training data or internal reasoning - Consistent behavior across identical inputs
```

## Response snapshot

Created complete feature specification for Integrated RAG Chatbot at specs/001-integrated-rag-chatbot/spec.md with all requirements, user scenarios, and success criteria. Also created requirements checklist at specs/001-integrated-rag-chatbot/checklists/requirements.md.

## Outcome

- ✅ Impact: Full specification created with all required sections
- 🧪 Tests: none
- 📁 Files: specs/001-integrated-rag-chatbot/spec.md, specs/001-integrated-rag-chatbot/checklists/requirements.md
- 🔁 Next prompts: /sp.plan to create architecture plan
- 🧠 Reflection: Specification captures all functional requirements and constraints from user input

## Evaluation notes (flywheel)

- Failure modes observed: none
- Graders run and results (PASS/FAIL): N/A
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): N/A