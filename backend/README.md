# Integrated RAG Chatbot for Published Book

This project implements a production-grade Retrieval-Augmented Generation (RAG) chatbot that answers questions strictly from book content, with support for selected text mode.

## Technology Stack

- **Backend**: FastAPI
- **LLM Provider**: Cohere API (generation + embeddings)
- **Vector Database**: Qdrant Cloud (Free Tier)
- **Relational Database**: Neon Serverless Postgres
- **Language**: Python 3.11

## Features

1. **Book Content Q&A**: Ask questions about the book content and receive grounded answers
2. **Selected Text Mode**: Ask questions about specific selected text only
3. **Deterministic Retrieval**: All responses traceable to retrieved chunks
4. **Zero Hallucination**: System refuses to answer when content is not available

## Setup

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Copy environment variables:
   ```bash
   cp .env.example .env
   ```
5. Add your API keys to `.env`

## Usage

Start the server:
```bash
uvicorn src.api.main:app --reload
```

The API will be available at `http://localhost:8000`

## API Endpoints

- `POST /api/v1/chat` - Chat with book content
- `POST /api/v1/chat-selected-text` - Chat with selected text only
- `GET /api/v1/health` - Health check
- `GET /api/v1/books/{book_id}` - Book metadata