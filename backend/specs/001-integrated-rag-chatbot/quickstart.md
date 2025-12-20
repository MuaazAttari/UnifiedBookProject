# Quickstart Guide: Integrated RAG Chatbot

## Prerequisites

- Python 3.9+
- pip package manager
- Git

## Setup

### 1. Clone Repository
```bash
git clone <repository-url>
cd <repository-name>
```

### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Environment Configuration
Create a `.env` file with the following variables:
```env
COHERE_API_KEY=your_cohere_api_key
QDRANT_API_KEY=your_qdrant_api_key
QDRANT_CLUSTER_URL=your_qdrant_cluster_url
NEON_DATABASE_URL=your_neon_database_url
```

## Running the Service

### Start the Application
```bash
uvicorn main:app --reload --port 8000
```

### Run Tests
```bash
pytest
```

## Initial Setup for Book Content

### 1. Index a Book
```bash
python -m scripts.index_book --book-path /path/to/book.md --book-id my-book-id
```

This will:
- Chunk the book content
- Generate embeddings using Cohere
- Store in Qdrant Cloud
- Add metadata to the database

## API Usage

### Chat with Book Content
```bash
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is the main concept in chapter 1?",
    "session_id": "optional-session-id"
  }'
```

### Chat with Selected Text
```bash
curl -X POST http://localhost:8000/api/v1/chat-selected-text \
  -H "Content-Type: application/json" \
  -d '{
    "selected_text": "The important concept is X which means...",
    "query": "Can you explain concept X in more detail?",
    "session_id": "optional-session-id"
  }'
```

### Health Check
```bash
curl http://localhost:8000/api/v1/health
```

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| COHERE_API_KEY | API key for Cohere services | Yes |
| QDRANT_API_KEY | API key for Qdrant vector database | Yes |
| QDRANT_CLUSTER_URL | URL for Qdrant Cloud cluster | Yes |
| NEON_DATABASE_URL | Connection string for Neon Postgres database | Yes |
| DEBUG | Enable debug logging (True/False) | No |
| LOG_LEVEL | Logging level (DEBUG, INFO, WARNING, ERROR) | No |

## Development

### Running in Development Mode
```bash
export DEBUG=True
uvicorn main:app --reload --port 8000
```

### Running Tests
```bash
# All tests
pytest

# Specific test file
pytest tests/test_chat.py

# With coverage
pytest --cov=src
```