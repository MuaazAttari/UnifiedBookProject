---
id: 1
title: rag-chatbot-constitution
stage: constitution
date: 2025-01-01
surface: agent
model: gpt-4o
feature: none
branch: main
user: Admin
command: /sp.constitution
labels: [constitution,rag,chatbot,ai]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
 - .specify/memory/constitution.md
tests:
 - none
---

## Prompt

```
/sp.constitution Project: Integrated RAG Chatbot for a Published Book (AI-Native, Spec-Driven)

Purpose:
Build a production-grade Retrieval-Augmented Generation (RAG) chatbot
embedded inside a published digital book. The chatbot must answer user
questions strictly based on the book's content, with optional support
for answering questions using only user-selected text.

Core Principles:
- Single Source of Truth: The book content is the only authoritative knowledge base
- Zero Hallucination: No answers outside retrieved or selected content
- Deterministic Retrieval: All responses must be traceable to retrieved chunks
- AI-Native Design: Agent-based orchestration with explicit tools and memory
- Provider Neutrality: Use Cohere LLM APIs exclusively (no OpenAI models)

LLM & AI Constraints:
- LLM Provider: Cohere API only
- OpenAI APIs must NOT be used for inference
- OpenAI Agents / ChatKit SDK patterns may be used only for orchestration logic
- All prompts must enforce grounded responses using retrieved context

Retrieval Rules:
- Vector Store: Qdrant Cloud (Free Tier)
- Embeddings stored with:
  - book_id
  - chapter
  - section
  - paragraph_index
- Retrieval must always precede generation
- If no relevant context is retrieved, respond with:
  "This information is not available in the book."

Selected Text Mode:
- If user provides selected text:
  - Ignore full-book retrieval
  - Use ONLY the selected text as context
  - Do not enrich or expand beyond selected content
  - Clearly state that the answer is based on selected text only

Backend & Infrastructure:
- API Framework: FastAPI
- Database: Neon Serverless Postgres
- Responsibilities:
  - User sessions
  - Query logs
  - Feedback storage
  - Retrieval metadata tracking

Response Standards:
- Tone: Clear, neutral, educational
- Audience: General readers of the book
- No speculation or external references
- No training data mentions
- No system or developer prompt leakage

Security & Data Integrity:
- API keys stored via environment variables
- No hardcoded secrets
- User queries must not modify source content
- Read-only access to book embeddings

Success Criteria:
- Every answer is fully grounded in retrieved or selected text
- No hallucinated facts detected
- Correct refusal when information is unavailable
- Cohere API successfully used for all generations
- Chatbot behaves consistently across identical queries

Failure Conditions:
- Answering from general knowledge instead of book content
- Using OpenAI models for generation
- Mixing selected-text mode with full-book retrieval
- Providing uncited or unverifiable responses
```

## Response snapshot

Constitution file created at .specify/memory/constitution.md with all specified principles and constraints.

## Outcome

- ✅ Impact: Created complete project constitution for RAG chatbot
- 🧪 Tests: none
- 📁 Files: .specify/memory/constitution.md
- 🔁 Next prompts: Implementation of spec, plan, and tasks
- 🧠 Reflection: Constitution captures all requirements specified by user

## Evaluation notes (flywheel)

- Failure modes observed: none
- Graders run and results (PASS/FAIL): N/A
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): N/A