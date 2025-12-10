---
id: 2
title: unified-textbook-plan
stage: plan
date: 2025-12-10
surface: agent
model: claude-sonnet-4-5-20250929
feature: memorize-config
branch: 2-memorize-config
user: Admin
command: /sp.plan execute --feature 2-memorize-config --tasks " 1. Import Claude-generated textbook into Docusaurus my-website/docs/physical-ai folder; 2. Verify all markdown chapters for frontmatter (id, title, sidebar_label); 3. Update sidebars.ts for correct chapter order; 4. Move all images and assets to my-website/static/img and update markdown links; 5. Setup RAG chatbot using OpenAI Agents / ChatKit SDK, FastAPI backend, Neon Postgres DB, and Qdrant Cloud vector DB; 6. Integrate chatbot in Docusaurus pages to answer questions from full book and selected text only; 7. Implement optional Claude Subagents / Agent Skills for reusable intelligence (bonus points); 8. Implement Better-Auth signup/signin with user background questionnaire for personalization (bonus points); 9. Add per-chapter 'Personalize this Chapter' button (bonus points); 10. Add per-chapter 'Translate to Urdu' button (bonus points); 11. Run verification to ensure all requirements from constitution.md and project history are satisfied; 12. Prepare for GitHub Pages deployment; 13. Generate final validation report with points scored and bonus points." --output plans/2-memorize-config/unified-execution-plan.md --priority high
labels: [planning,textbook-generation,RAG,architecture]
links:
  spec: specs/2-memorize-config/spec.md
  ticket: null
  adr: null
  pr: null
files:
 - plans/2-memorize-config/unified-execution-plan.md
 - plans/2-memorize-config/research.md
 - plans/2-memorize-config/data-model.md
 - plans/2-memorize-config/contracts/textbook-api.yaml
tests:
 - plans/2-memorize-config/research.md
 - plans/2-memorize-config/data-model.md
 - plans/2-memorize-config/contracts/textbook-api.yaml
---

## Prompt

```
execute \
  --feature 2-memorize-config \
  --tasks "
    1. Import Claude-generated textbook into Docusaurus my-website/docs/physical-ai folder;
    2. Verify all markdown chapters for frontmatter (id, title, sidebar_label);
    3. Update sidebars.ts for correct chapter order;
    4. Move all images and assets to my-website/static/img and update markdown links;
    5. Setup RAG chatbot using OpenAI Agents / ChatKit SDK, FastAPI backend, Neon Postgres DB, and Qdrant Cloud vector DB;
    6. Integrate chatbot in Docusaurus pages to answer questions from full book and selected text only;
    7. Implement optional Claude Subagents / Agent Skills for reusable intelligence (bonus points);
    8. Implement Better-Auth signup/signin with user background questionnaire for personalization (bonus points);
    9. Add per-chapter 'Personalize this Chapter' button (bonus points);
    10. Add per-chapter 'Translate to Urdu' button (bonus points);
    11. Run verification to ensure all requirements from constitution.md and project history are satisfied;
    12. Prepare for GitHub Pages deployment;
    13. Generate final validation report with points scored and bonus points."
  --output plans/2-memorize-config/unified-execution-plan.md \
  --priority high
```

## Response snapshot

Created comprehensive implementation plan for the Unified Physical AI & Humanoid Robotics Learning Book project. The plan includes:
- Technical architecture overview with frontend (Docusaurus), backend (FastAPI), vector DB (Qdrant Cloud), and metadata DB (Neon Postgres)
- Detailed phase breakdown: Research, Data Model & API Design, Implementation Planning, and Validation
- Data models for Configuration, Chapter, User, ChatSession, TranslationCache, and PersonalizationProfile entities
- OpenAPI specification for the textbook system APIs
- Research document addressing unknowns about textbook structure, Docusaurus integration, RAG architecture, and other technical decisions

## Outcome

- ✅ Impact: Complete implementation plan for textbook generation and RAG system
- 🧪 Tests: Created data models and API contracts with validation
- 📁 Files: Created implementation plan, research doc, data model, and API contracts
- 🔁 Next prompts: Ready for task generation with `/sp.tasks`
- 🧠 Reflection: Successfully mapped complex requirements to technical implementation approach

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): PASS
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Proceed to task generation phase