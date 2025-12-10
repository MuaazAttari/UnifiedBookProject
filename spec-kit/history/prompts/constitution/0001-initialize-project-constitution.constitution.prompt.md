---
id: 0001
title: Initialize project constitution
stage: constitution
date: 2025-12-08
surface: agent
model: claude-sonnet-4-5-20250929
feature: none
branch: master
user: Admin
command: /sp.constitution
labels: ["governance", "initialization"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
- .specify/memory/constitution.md
tests:
null
---

## Prompt

# Unified AI & Physical Robotics Book Project — Constitution

## 1. Preamble
This Constitution defines the rules, structure, and expectations for completing the
Unified Book Project based on Spec-Driven Development.
All participants must follow these guidelines to ensure a consistent, fair, and
high-quality submission.

This project integrates AI-driven book writing, RAG-powered learning tools,
and Physical AI concepts related to Humanoid Robotics.

---

## 2. Project Title
**Unified Physical AI & Humanoid Robotics Learning Book**

---

## 3. Core Deliverables (Mandatory Requirements)

### 3.1 AI/Spec-Driven Book Creation
Participants must create a complete educational book using:

- **Docusaurus**
- **Spec-Kit Plus**
- **Claude Code** (Subagents allowed)
- Deployment on **GitHub Pages**

The book content must cover:
- Physical AI
- Humanoid Robotics
- ROS 2
- Gazebo / Unity
- NVIDIA Isaac
- Vision-Language-Action (VLA)
- Conversational Robotics
- Weekly Breakdown of Course

---

### 3.2 Integrated RAG Chatbot (Mandatory)
The published book must include an active RAG-based chatbot using:

- OpenAI Agents / ChatKit SDK
- FastAPI backend
- Qdrant Cloud (Vector DB)
- Neon Serverless Postgres (Metadata storage)

The chatbot must support:
1. Answering questions **from the entire book**
2. Answering questions based on **selected text only**
3. Working inside the Docusaurus frontend

---

### 3.3 Base Points
You will receive **100 Points** for completing all mandatory requirements above.

---

## 4. Bonus Deliverables (Optional for Extra Points)

### 4.1 Reusable Intelligence (Up to 50 Points)
Projects may include:

- Claude Code Subagents
- Agent Skills
- Modular Intelligence Flows integrated into book content
- Spec-Driven pipelines used multiple times

---

### 4.2 Signup & Signin with Personalization (Up to 50 Points)

Use **Better-Auth** for:
- Sign-up
- Sign-in
- User background questionnaire:
  - Software experience
  - Hardware/GPU availability
  - Robotics familiarity

This user data must enable **automatic content personalization** based on user profiles (e.g., beginner, expert, hardware owner).

---

### 4.3 Urdu Translation System (Up to 50 Points)

- Implement a real-time content translation system for Urdu.
- Use advanced AI translation APIs (e.g., Google Translate API, DeepL).

---

### 4.4 Advanced Search & Discovery (Up to 50 Points)
- Implement a sophisticated search engine for the book content beyond Docusaurus's built-in capabilities.
- Features: semantic search, keyword highlighting, filtering by section.

---

### 4.5 Interactive Simulations/Demos (Up to 50 Points)
- Embed interactive simulations (e.g., web-based Gazebo/Unity viewer, ROS 2 topics visualization) directly into book pages.
- Provide simple code demos for key concepts.

---

## 5. Development Principles & Quality Standards

### 5.1 Code Quality
- All code must be well-documented, readable, and follow best practices for the respective language/framework.
- Use static analysis tools (e.g., linters, formatters) in CI/CD.

### 5.2 Testing
- Comprehensive unit, integration, and end-to-end tests are required for all core functionalities.
- Minimum 80% code coverage for backend services and critical frontend components.

### 5.3 Performance
- Frontend load times (LCP, FID) under 2.5 seconds.
- Backend API response times (p95) under 500ms.
- Efficient resource utilization for AI models and databases.

### 5.4 Security
- Implement OWASP Top 10 mitigations for web applications.
- All secrets and API keys must be stored securely (e.g., environment variables, secret management services).
- Regular security audits and vulnerability scanning.

### 5.5 Architecture
- Modular, scalable, and maintainable architecture.
- Clear separation of concerns between frontend, backend, and AI services.
- Leverage cloud-native patterns where applicable.

---

## 6. Project Management & Workflow

### 6.1 Spec-Driven Development (Mandatory)
- Follow the Spec-Driven Development (SDD) workflow using Spec-Kit Plus.
- Each feature must have a `spec.md`, `plan.md`, and `tasks.md`.

### 6.2 Content Implementation Rules
- All chapters in Markdown
- All AI-generated content must be **manually reviewed**
- Clear headings, diagrams, and examples required

### 6.3 Git Rules
- Push regularly
- Use branches:
  - feature/*
  - fix/*
- Submit final project through GitHub Repo

---

## 7. Allowed Tools & Technologies

### Required:
- **Docusaurus**
- **Spec-Kit Plus**
- **Claude Code**
- **FastAPI**
- **Qdrant Cloud**
- **Neon DB**
- **OpenAI Agents or ChatKit SDK**

### Optional but Recommended:
- NVIDIA Isaac Sim
- Unity / Gazebo
- ROS 2 (Humble or Iron)
- Whisper
- VLM/VLA tools

---

## 8. Content Requirements (The Book Must Include)

### 8.1 Physical AI & Embodied Intelligence
- What is Physical AI?
- Why humanoid robots need embodied intelligence
- Transition from digital AI to real-world agents

### 8.2 ROS 2 Fundamentals
- Nodes, Topics, Services, Actions
- rclpy usage
- URDF

### 8.3 Gazebo / Unity Simulation
- Physics simulation
- Sensors (LiDAR, Depth Cam, IMU)
- Digital Twin concepts

### 8.4 NVIDIA Isaac Platform
- Isaac Sim
- Perception pipelines
- VSLAM & Navigation

### 8.5 Vision-Language-Action (VLA)
- LLM → Action planning
- Voice commands → Robot control
- Multimodal robotics

### 8.6 Capstone Project Outline
- Voice-to-Action system
- Navigation & SLAM
- Object identification
- Manipulation with humanoid hands

---

## 9. User Data & Privacy

### 9.1 Collected Data (Signup)
- Name
- Email
- Background info
- Device/GPU info
- Experience level

### 9.2 Privacy Rules
- Never expose user data publicly
- Use DB read-only for personalization
- JWT tokens must be used for auth

---

## 10. Evaluation Structure

### Mandatory (100 Points)
- Book created using Spec-Driven pipeline
- RAG Chatbot that understands book content
- Deployment to GitHub Pages

### Bonus (Up to 150 Points Total)
- Subagents (50)
- Auth + Personalization (50)
- Urdu translation system (50)

**Max Achievable Score: 250 Points**

---

## 11. Amendments
Any updates or improvements to this Constitution must be documented and
approved by the Project Owner or Course Instructor.

---

## 12. Closing Statement
This Constitution is the official governing document for your Unified Book Project.
Following it ensures fairness, quality, and alignment with course goals in
Physical AI and Humanoid Robotics.

---

**Version**: 1.0.0 | **Ratified**: 2025-12-08 | **Last Amended**: 2025-12-08

## Response snapshot

The project constitution has been updated to version 1.0.0. This is an initial version bump as the constitution was created based on your input.

The following template files require manual review to ensure alignment with the new constitution's principles:
- `.specify/templates/plan-template.md`
- `.specify/templates/spec-template.md`
- `.specify/templates/tasks-template.md`
- `.specify/templates/commands/sp.clarify.md`
- `.specify/templates/commands/sp.checklist.md`
- `.specify/templates/commands/sp.analyze.md`
- `.specify/templates/commands/sp.adr.md`
- `.specify/templates/commands/sp.phr.md`
- `.specify/templates/commands/sp.implement.md`
- `.specify/templates/commands/sp.git.commit_pr.md`
- `.specify/templates/commands/sp.constitution.md`
- `.specify/templates/commands/sp.specify.md`
- `.specify/templates/commands/sp.plan.md`
- `.specify/templates/commands/sp.tasks.md`

Suggested commit message: `docs: initialize constitution to v1.0.0 (initial project governance)`

I will now create a Prompt History Record for this update.

## Outcome

- ✅ Impact: Project governance document initialized with user-provided content.
- 🧪 Tests: No tests were run for this task.
- 📁 Files: One file was modified: .specify/memory/constitution.md. One file was created: history/prompts/constitution/0001-initialize-project-constitution.constitution.prompt.md.
- 🔁 Next prompts: Manual review of template files is recommended.
- 🧠 Reflection: The bash script for PHR creation was not found, requiring a fallback to agent-native tools. This highlights the importance of robust error handling and fallback mechanisms.

## Evaluation notes (flywheel)

- Failure modes observed: Bash script for PHR creation not found.
- Graders run and results (PASS/FAIL): Not applicable.
- Prompt variant (if applicable): Not applicable.
- Next experiment (smallest change to try): Investigate the bash script path or ensure it's properly handled in the environment.
